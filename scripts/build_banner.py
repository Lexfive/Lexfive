"""Banner do perfil (escuro/claro) com a Samantha acenando quadro a quadro.
Roda localmente (precisa de Pillow): python scripts/build_banner.py <pasta 03_aceno do portfolio>
GitHub mostra SVG como <img>: sem JS/fonte externa, então a animação é CSS dentro do SVG
e a Samantha vai embutida como uma tira PNG (data URI)."""
import base64, io, json, sys
from pathlib import Path
from PIL import Image

src = Path(sys.argv[1])
meta = json.loads((src / "aceno_spritesheet.json").read_text())
sheet = Image.open(src / "aceno_spritesheet.webp").convert("RGBA")
H = 190
frames = []
for f in meta["frames"]:
    r = f["frame"]
    im = sheet.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))
    w = round(r["w"] * H / r["h"])
    frames.append((im.resize((w, H), Image.LANCZOS), f.get("duration", 112)))
FW = max(im.width for im, _ in frames)
strip = Image.new("RGBA", (FW * len(frames), H))
for i, (im, _) in enumerate(frames):
    strip.paste(im, (i * FW + (FW - im.width) // 2, 0))
buf = io.BytesIO()
strip.quantize(colors=96, method=Image.FASTOCTREE).save(buf, "PNG", optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()
N = len(frames)
dur = sum(d for _, d in frames) / 1000

def banner(dark: bool) -> str:
    bg, fg, dim, line = ("#19171b", "#f2f2f2", "#9a979d", "#3a383d") if dark else ("#ffffff", "#111111", "#5f5f5f", "#e6e6e6")
    acc = "#d29f22"
    W, Hh = 1200, 300
    sx, sy = 1010, Hh - H - 18
    # frame-by-frame: shift the strip left one cell per frame, each held for its own duration
    t, kts = 0.0, []
    for _, d in frames:
        kts.append(t / (dur * 1000)); t += d
    xs = ";".join(str(sx - i * FW) for i in range(N))
    kt = ";".join(f"{k:.4f}" for k in kts)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}" role="img" aria-label="LEXFIVE — Ramires Mohamed">
<defs>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{acc}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{acc}" stop-opacity="1"/>
    <stop offset="1" stop-color="{acc}" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0" dur="5s" repeatCount="indefinite"/>
  </linearGradient>
  <clipPath id="cell"><rect x="{sx}" y="{sy}" width="{FW}" height="{H}"/></clipPath>
</defs>
<style>
  .t {{ font-family: "Segoe UI Variable Display","Segoe UI",Helvetica,Arial,sans-serif; }}
  .mono {{ font-family: Consolas,"SF Mono",Menlo,monospace; }}
  .dot {{ animation: blink 1.6s ease-in-out infinite; }}
  @keyframes blink {{ 50% {{ opacity: .25; }} }}
  @media (prefers-reduced-motion: reduce) {{ .dot {{ animation: none; }} }}
</style>
<rect width="{W}" height="{Hh}" fill="{bg}"/>
<rect x="0" y="{Hh-8}" width="{W}" height="4" fill="#5d0018"/><rect x="0" y="{Hh-4}" width="{W}" height="4" fill="{acc}"/>
<text x="48" y="70" class="mono" font-size="15" letter-spacing="2.5" fill="{acc}">BELO HORIZONTE · DESENVOLVEDOR &amp; CRIADOR</text>
<text x="44" y="190" class="t" font-size="132" font-weight="800" letter-spacing="-5" fill="none" stroke="{dim}" stroke-opacity=".55" stroke-width="1.4">LEXFIVE</text>
<text x="44" y="190" class="t" font-size="132" font-weight="800" letter-spacing="-5" fill="url(#sweep)" fill-opacity=".9">LEXFIVE</text>
<text x="48" y="238" class="t" font-size="24" font-weight="600" fill="{fg}">Ramires Mohamed — <tspan fill="{acc}">sites, sistemas e automações</tspan></text>
<circle class="dot" cx="54" cy="264" r="4" fill="#3ddc84"/>
<text x="66" y="269" class="mono" font-size="13" fill="{dim}">lexfive.com · apps.lexfive.com</text>
<g clip-path="url(#cell)"><image x="{sx}" y="{sy}" width="{FW * N}" height="{H}" href="data:image/png;base64,{b64}" style="image-rendering:pixelated"><animate attributeName="x" calcMode="discrete" values="{xs}" keyTimes="{kt}" dur="{dur:.3f}s" repeatCount="indefinite"/></image></g>
</svg>'''

out = Path(__file__).resolve().parent.parent / "assets"
(out / "banner-dark.svg").write_text(banner(True), encoding="utf-8")
(out / "banner-light.svg").write_text(banner(False), encoding="utf-8")
print("ok", FW, N, round(len(b64) / 1024), "KB")
