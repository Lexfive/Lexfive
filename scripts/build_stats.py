"""Cartão de estatísticas (escuro/claro) gerado a partir da API GraphQL do GitHub.
Sem dependências. Roda na Action diária (GITHUB_TOKEN) ou local: GITHUB_TOKEN=$(gh auth token) python scripts/build_stats.py"""
import json, os, urllib.request
from datetime import date, timedelta
from pathlib import Path

USER = "Lexfive"
Q = """query($u:String!){ user(login:$u){
  contributionsCollection{ contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } }
  repositories(ownerAffiliations:OWNER, isFork:false, first:100, privacy:PUBLIC){ totalCount nodes{ stargazerCount languages(first:6, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{ name color } } } } }
}}"""

def gql():
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": Q, "variables": {"u": USER}}).encode(),
                                 {"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["data"]["user"]

u = gql()
cal = u["contributionsCollection"]["contributionCalendar"]
days = [d for w in cal["weeks"] for d in w["contributionDays"]]
total = cal["totalContributions"]
best = cur = run = 0
for d in days:
    run = run + 1 if d["contributionCount"] else 0
    best = max(best, run)
today = date.today().isoformat()
for d in reversed(days):
    if d["date"] > today: continue
    if d["contributionCount"]: cur += 1
    elif d["date"] == today: continue  # today still open
    else: break
repos = u["repositories"]
stars = sum(r["stargazerCount"] for r in repos["nodes"])
langs = {}
for r in repos["nodes"]:
    for e in r["languages"]["edges"]:
        n = e["node"]["name"]; langs.setdefault(n, [0, e["node"]["color"] or "#888"]); langs[n][0] += e["size"]
top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:5]
tsum = sum(v[0] for _, v in top) or 1
# last 20 weeks as a mini graph
weeks = cal["weeks"][-16:]
active = sum(1 for d in days if d["contributionCount"])

def card(dark):
    bg, fg, dim, line, empty = ("#19171b", "#f2f2f2", "#9a979d", "#3a383d", "#252628") if dark else ("#ffffff", "#111111", "#5f5f5f", "#e6e6e6", "#eeeeee")
    acc = "#d29f22"
    lv = lambda c: empty if c == 0 else [None, "#4a3a10", "#7a5f16", "#a87f1b", acc][min(4, 1 + c // 3)]
    W, H = 840, 222
    stats = [(f"{total}", "contribuições no ano"), (f"{active}", "dias ativos no ano"), (f"{best}", "maior sequência"), (f"{date.today().year - 2020}", "anos no GitHub")]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Estatísticas de {USER}">',
         '<style>.t{font-family:"Segoe UI",Helvetica,Arial,sans-serif}.m{font-family:Consolas,"SF Mono",Menlo,monospace}',
         '.in{opacity:0;animation:in .6s ease-out forwards}@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}',
         '@media (prefers-reduced-motion:reduce){.in{animation:none;opacity:1}}</style>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="2" fill="{bg}" stroke="{line}"/>',
         f'<rect x="1" y="1" width="{W-2}" height="2" fill="#5d0018"/><rect x="1" y="3" width="{W-2}" height="2" fill="{acc}"/>',
         f'<text x="28" y="36" class="m" font-size="12" letter-spacing="2" fill="{acc}">GITHUB · {USER.upper()}</text>']
    for i, (n, l) in enumerate(stats):
        x = 28 + i * 140
        s.append(f'<g class="in" style="animation-delay:{i*0.12:.2f}s"><text x="{x}" y="88" class="t" font-size="34" font-weight="700" fill="{fg}">{n}</text>'
                 f'<text x="{x}" y="110" class="m" font-size="11" fill="{dim}">{l}</text></g>')
    # mini contribution graph
    gx, gy, c = W - 28 - 16 * 12 + 2, 46, 10
    for wi, w in enumerate(weeks):
        for di, d in enumerate(w["contributionDays"]):
            s.append(f'<rect class="in" style="animation-delay:{0.3+wi*0.025:.3f}s" x="{gx+wi*(c+2)}" y="{gy+di*(c+2)}" width="{c}" height="{c}" rx="2" fill="{lv(d["contributionCount"])}"/>')
    s.append(f'<text x="{W-28}" y="36" text-anchor="end" class="m" font-size="10" fill="{dim}">últimas 16 semanas</text>')
    # languages bar
    y, x = 166, 28
    s.append(f'<line x1="28" y1="148" x2="{W-28}" y2="148" stroke="{line}"/>')
    bw = W - 56
    for n, (sz, col) in top:
        w = bw * sz / tsum
        s.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w-2,1):.1f}" height="6" rx="1" fill="{col}"/>'); x += w
    x = 28
    for n, (sz, col) in top:
        lab = f"{n} {round(100*sz/tsum)}%"
        s.append(f'<circle cx="{x+4}" cy="{y+28}" r="4" fill="{col}"/><text x="{x+13}" y="{y+32}" class="m" font-size="11" fill="{dim}">{lab}</text>')
        x += 24 + len(lab) * 7
    s.append("</svg>")
    return "".join(s)

out = Path(__file__).resolve().parent.parent / "assets"
out.mkdir(exist_ok=True)
(out / "stats-dark.svg").write_text(card(True), encoding="utf-8")
(out / "stats-light.svg").write_text(card(False), encoding="utf-8")
print("ok", total, cur, best, repos["totalCount"], [n for n, _ in top])
