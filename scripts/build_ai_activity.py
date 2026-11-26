"""Cartão "Construindo com IA": sessões por dia no Claude Code, Codex e Gemini.
Roda NO SEU PC (lê os registros locais) e grava assets/ai-*.svg. Só conta sessões
por dia — nenhum nome de projeto, caminho ou conteúdo sai do computador.
Uso: python scripts/build_ai_activity.py  (depois: git add assets && git commit && git push)"""
import json, os, re
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import base64 as _b64
from pathlib import Path as _P
# Montserrat (OFL) embutida: SVG dentro de <img> não carrega fonte externa
_FONT = _b64.b64encode((_P(__file__).resolve().parent.parent / "assets" / "fonts" / "montserrat-latin.woff2").read_bytes()).decode()
FONT_FACE = '@font-face{font-family:"Montserrat";src:url(data:font/woff2;base64,' + _FONT + ') format("woff2");font-weight:100 900}'


HOME = Path.home()
WEEKS = 52
start = date.today() - timedelta(days=date.today().weekday() + 1 + 7 * (WEEKS - 1))  # a Sunday
per = {"claude": defaultdict(set), "codex": defaultdict(set), "gemini": defaultdict(set)}

# Claude Code: each .jsonl is a session; days = local dates of its user messages
for f in (HOME / ".claude" / "projects").rglob("*.jsonl"):
    try:
        with open(f, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if '"type":"user"' not in line and '"type": "user"' not in line: continue
                m = re.search(r'"timestamp":\s*"([^"]+)"', line)
                if m:
                    d = datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).astimezone().date()
                    per["claude"][d].add(f.stem)
    except OSError: pass
# Codex: sessions/YYYY/MM/DD/rollout-*.jsonl(.zst)
for f in (HOME / ".codex" / "sessions").rglob("rollout-*"):
    m = re.search(r"rollout-(\d{4})-(\d\d)-(\d\d)", f.name)
    if m: per["codex"][date(*map(int, m.groups()))].add(f.name)
# Gemini / Antigravity: one folder per conversation; days = mtimes of its message files
for conv in (HOME / ".gemini" / "antigravity" / "brain").glob("*"):
    msgs = conv / ".system_generated" / "messages"
    for f in (msgs.glob("*") if msgs.is_dir() else []):
        per["gemini"][date.fromtimestamp(f.stat().st_mtime)].add(conv.name)

days = [start + timedelta(i) for i in range(WEEKS * 7) if start + timedelta(i) <= date.today()]
count = {d: sum(len(per[k].get(d, ())) for k in per) for d in days}
totals = {k: len({s for d in days for s in per[k].get(d, ())}) for k in per}
active = sum(1 for d in days if count[d])

def card(dark):
    bg, fg, dim, line, empty = ("#000000", "#ffffff", "#9a9a9a", "#383838", "#1a1a1a") if dark else ("#ffffff", "#111111", "#5f5f5f", "#e6e6e6", "#eeeeee")
    acc = "#d30000"
    ink = "#ff4d4d" if dark else "#d30000"
    ramp = ["#4d0000", "#850000", "#b00000", "#ff2a2a"] if dark else ["#f6b3b3", "#e86a6a", "#d30000", "#8a0000"]
    lv = lambda c: empty if c == 0 else ramp[min(3, (c - 1) // 2)]
    W, H, c = 840, 236, 11
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Sessões de desenvolvimento com IA nas últimas {WEEKS} semanas">',
         '<style>' + FONT_FACE + '.t{font-family:"Montserrat","Segoe UI",Helvetica,Arial,sans-serif}.m{font-family:Consolas,"SF Mono",Menlo,monospace}',
         '.in{opacity:0;animation:in .5s ease-out forwards}@keyframes in{to{opacity:1}}@media (prefers-reduced-motion:reduce){.in{animation:none;opacity:1}}</style>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="2" fill="{bg}" stroke="{line}"/>',
         f'<rect x="1" y="1" width="{W-2}" height="2" fill="#d30000"/><rect x="1" y="3" width="{W-2}" height="2" fill="#383838"/>',
         f'<text x="28" y="36" class="m" font-size="12" letter-spacing="2" fill="{ink}">CONSTRUINDO COM IA · NO MEU PC</text>',
         f'<text x="{W-28}" y="36" text-anchor="end" class="m" font-size="10" fill="{dim}">últimas {WEEKS} semanas · atualizado {date.today().strftime("%d/%m/%Y")}</text>']
    stats = [(totals["claude"], "sessões · Claude Code"), (totals["codex"], "sessões · Codex"), (totals["gemini"], "sessões · Gemini"), (active, "dias ativos")]
    for i, (n, l) in enumerate(stats):
        x = 28 + i * 200
        s.append(f'<text x="{x}" y="80" class="t" font-size="30" font-weight="700" fill="{fg}">{n}</text><text x="{x}" y="100" class="m" font-size="11" fill="{dim}">{l}</text>')
    gx, gy = 28, 124
    for i, d in enumerate(days):
        w, wd = divmod(i, 7)
        s.append(f'<rect class="in" style="animation-delay:{w*0.015:.2f}s" x="{gx + w*(c+3) + 4}" y="{gy + wd*(c+3) - 6}" width="{c}" height="{c}" rx="2" fill="{lv(count[d])}"><title>{d.strftime("%d/%m")}: {count[d]} sessões</title></rect>')
    return "".join(s) + "</svg>"

out = Path(__file__).resolve().parent.parent / "assets"
(out / "ai-dark.svg").write_text(card(True), encoding="utf-8")
(out / "ai-light.svg").write_text(card(False), encoding="utf-8")
print("ok", totals, "dias ativos:", active)
