"""Genera assets/banner-claro.svg y assets/banner-oscuro.svg a partir del logotipo pixel art.

Uso: python scripts/banner.py .
"""
import re
import sys
from pathlib import Path

repo = Path(sys.argv[1])
logo = (repo / "assets/logotipo-blanco-transparente.svg").read_text(encoding="utf-8")

# Icono: rectángulos 8x8 ("Mx yh8v8h-8z"); el último path es el pixel tenue.
icon_paths = re.findall(r'<path fill="#F5F5F5"( fill-opacity="0.4")? d="(M[^"]+)"/>', logo.split("</g>")[0])
pixels, dim = [], []
for faded, d in icon_paths:
    for x, y in re.findall(r"M(\d+) (\d+)h8v8h-8z", d):
        (dim if faded else pixels).append((int(x), int(y)))
# Palabra "helminth117": el path del segundo grupo, tal cual.
word = re.search(r'<g transform="translate\(0 20\)"><path fill="#F5F5F5" d="([^"]+)"/>', logo).group(1)

W, H = 960, 236
LOGO_X, LOGO_Y = (W - 620) // 2, 0
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
FS, CW = 22, 13.2                    # tamaño y avance fijo por carácter (textLength)
PROMPT = "> hago "
PHRASES = ["overlays para directos", "plugins y mods de Minecraft",
           "paneles para servidores", "aparatos con un ESP32"]
TYPE, ERASE, HOLD, GAP = 0.075, 0.03, 2.2, 0.45   # segundos
INTRO = 0.03 * len(pixels) + 0.9                  # cuándo empieza a escribir
LINE_Y = 196
longest = len(PROMPT) + max(map(len, PHRASES))
X0 = round((W - longest * CW) / 2, 1)
PX = X0 + len(PROMPT) * CW           # donde empiezan las frases

# Tiempos del ciclo de escritura.
slots, t = [], 0.0
for p in PHRASES:
    n = len(p)
    slots.append((t, n))
    t += n * TYPE + HOLD + n * ERASE + GAP
CYCLE = round(t, 3)


def steps(start, n):
    """(tiempo, caracteres visibles) de una frase: escribe, espera y borra."""
    pts = [(start + i * TYPE, i) for i in range(n + 1)]
    e0 = start + n * TYPE + HOLD
    pts += [(e0 + i * ERASE, n - i) for i in range(1, n + 1)]
    return pts


def smil(attr, pts, scale, offset):
    """animate discreto sobre todo el ciclo; fuera de su tramo vale 0."""
    pts = [(0.0, 0)] + [p for p in pts if p[0] > 0] + [(CYCLE, 0)]
    pts = sorted({round(a / CYCLE, 5): b for a, b in pts}.items())
    times = ";".join(f"{a:g}" for a, _ in pts)
    vals = ";".join(f"{offset + b * scale:g}" for _, b in pts)
    return (f'<animate attributeName="{attr}" calcMode="discrete" dur="{CYCLE}s" '
            f'begin="{INTRO:.2f}s" repeatCount="indefinite" keyTimes="{times}" values="{vals}"/>')


def build(ink, soft, faint):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'role="img" aria-label="helminth117 — hago las herramientas que yo mismo uso">',
           "<style>",
           ".px{animation:pop .35s cubic-bezier(.2,1.6,.4,1) backwards;transform-box:fill-box;transform-origin:center}",
           "@keyframes pop{from{opacity:0;transform:scale(0)}}",
           f".word{{animation:rise .7s ease-out {0.03 * len(pixels) + 0.1:.2f}s backwards}}",
           "@keyframes rise{from{opacity:0;transform:translateX(-14px)}}",
           f".eye{{animation:pop .35s ease-out {0.03 * len(pixels):.2f}s backwards,eye 6s {INTRO + 2:.2f}s infinite}}",
           "@keyframes eye{0%,88%,100%{opacity:.4}91%,95%{opacity:1}}",
           f".line{{animation:fade .5s ease-out {INTRO - 0.4:.2f}s backwards}}",
           "@keyframes fade{from{opacity:0}}",
           ".cur{animation:blink 1s steps(1) infinite}",
           "@keyframes blink{50%{opacity:0}}",
           "@media (prefers-reduced-motion:reduce){*{animation:none!important}}",
           "</style>",
           f'<g transform="translate({LOGO_X} {LOGO_Y + 20})" shape-rendering="crispEdges" fill="{ink}">']
    for i, (x, y) in enumerate(pixels):
        out.append(f'<rect class="px" style="animation-delay:{i * 0.03:.2f}s" x="{x}" y="{y}" width="8" height="8"/>')
    for x, y in dim:
        out.append(f'<rect class="px eye" x="{x}" y="{y}" width="8" height="8" opacity=".4"/>')
    out.append("</g>")
    # La animación CSS de transform pisaría el atributo transform: van en grupos distintos.
    out.append(f'<g transform="translate({LOGO_X} {LOGO_Y + 20})"><g class="word"><path fill="{ink}" d="{word}"/></g></g>')

    # Línea de terminal.
    out.append(f'<g class="line" font-family="{FONT}" font-size="{FS}">')
    out.append(f'<text x="{X0}" y="{LINE_Y}" fill="{soft}" textLength="{len(PROMPT) * CW:g}" '
               f'lengthAdjust="spacing" xml:space="preserve">{PROMPT}</text>')
    cursor_pts = []
    for k, (p, (start, n)) in enumerate(zip(PHRASES, slots)):
        pts = steps(start, n)
        cursor_pts += pts
        out.append(f'<clipPath id="c{k}"><rect x="{PX}" y="{LINE_Y - FS}" height="{FS + 8}" width="0">'
                   f'{smil("width", pts, CW, 0)}</rect></clipPath>')
        out.append(f'<text clip-path="url(#c{k})" x="{PX}" y="{LINE_Y}" fill="{ink}" '
                   f'textLength="{n * CW:g}" lengthAdjust="spacing">{p}</text>')
    out.append(f'<rect class="cur" x="{PX}" y="{LINE_Y - FS + 3}" width="{CW - 2:g}" height="{FS}" fill="{ink}">'
               f'{smil("x", cursor_pts, CW, PX)}</rect>')
    out.append("</g>")
    out.append(f'<rect x="{X0}" y="{LINE_Y + 18}" width="{longest * CW:g}" height="1" fill="{faint}"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


(repo / "assets/banner-claro.svg").write_text(build("#0D0D0D", "#6E6E6E", "#D4D4D4"), encoding="utf-8")
(repo / "assets/banner-oscuro.svg").write_text(build("#F5F5F5", "#A3A3A3", "#2B2B2B"), encoding="utf-8")
print(f"{len(pixels)} píxeles + {len(dim)} tenue, intro {INTRO:.2f}s, ciclo {CYCLE}s")
