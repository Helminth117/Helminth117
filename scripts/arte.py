"""Genera el arte del perfil a partir de dibujos en ASCII, con el mismo pixel art del logo.

- assets/proyectos/<proyecto>-{claro,oscuro}.svg: tarjetas animadas de los proyectos destacados.
- assets/separador-{claro,oscuro}.svg y assets/monstruo-{claro,oscuro}.svg: adornos del README.
- assets/social/<repo>.png: imágenes de 1280x640 para el "Social preview" de cada repo público
  (necesita rsvg-convert).

Uso: python3 scripts/arte.py <ruta del repo>
"""
import random
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pixel import PALETAS, TENUE, ancho_texto, celdas, dibujo, esc, tamano, texto, texto_pixel  # noqa: E402

repo = Path(sys.argv[1])
SIN_MOVIMIENTO = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def svg(w, h, cuerpo, etiqueta):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{esc(etiqueta)}">{cuerpo}</svg>\n')


def estilo(css):
    return f"<style>{css}{SIN_MOVIMIENTO}</style>"


def rejilla(ancho, alto):
    return [["."] * ancho for _ in range(alto)]


def pegar(g, filas, x, y, c=None):
    for fy, fila in enumerate(filas):
        for fx, ch in enumerate(fila):
            if ch in "#+":
                g[y + fy][x + fx] = c or ch


def filas_de(g):
    return ["".join(f) for f in g]


# ---------------------------------------------------------------- motivos
# Cada motivo devuelve (svg, ancho, alto) dibujado desde (0, 0). Con anim=False sale un
# fotograma fijo, para las imágenes PNG (rsvg-convert no anima).

PERSONA = [
    "......#####......",
    ".....#######.....",
    ".....#########...",
    ".....#+#######...",
    ".....#######.##..",
    "......#####...#..",
    ".......###....#..",
    ".....#######.#...",
    "....#########....",
    "...#.#######.....",
    "...#.#######.....",
    "...#.#######.....",
    "...#.#######.....",
    ".....#######.....",
    ".....##...##.....",
    ".....##...##.....",
    ".....##...##.....",
    "....###...###....",
]


def m_helcam(pal, anim):
    ink, n = pal["ink"], len(PERSONA[0])
    pad = 4
    w, h = (n + 2 * pad - 1) * 10 + 8, len(PERSONA) * 10
    lineas = [(0, 3, 9), (2, 1, 6), (n + 2 * pad - 3, 2, 8), (n + 2 * pad - 1, 6, 7), (1, 11, 5), (n + 2 * pad - 2, 12, 4)]
    out = []
    if anim:
        out.append(estilo(
            ".hc-u,.hc-d{animation:4s ease-in infinite backwards}.hc-u{animation-name:hc-u}.hc-d{animation-name:hc-d}"
            ".hc-fx{animation:hc-fx 4s infinite}.hc-gh{animation:hc-gh 4s infinite}"
            "@keyframes hc-u{0%,40%{transform:translateY(0);opacity:1}52%,86%{transform:translateY(-40px);opacity:0}96%,100%{transform:translateY(0);opacity:1}}"
            "@keyframes hc-d{0%,40%{transform:translateY(0);opacity:1}52%,86%{transform:translateY(40px);opacity:0}96%,100%{transform:translateY(0);opacity:1}}"
            "@keyframes hc-fx{0%,42%{opacity:0}47%{opacity:1}60%,100%{opacity:0}}"
            "@keyframes hc-gh{0%,44%{opacity:0}49%{opacity:.35}66%,100%{opacity:0}}"))
        fantasma, _ = celdas(PERSONA, pad * 10, 0)
        out.append(f'<path class="hc-gh" fill="{ink}" opacity="0" d="{fantasma}"/>')
        for x in range(n):
            lleno, tenue = celdas(PERSONA, pad * 10, 0, columna=x)
            if not lleno and not tenue:
                continue
            cls = "hc-u" if x % 2 else "hc-d"
            out.append(f'<g class="{cls}" style="animation-delay:{x * 0.015:.3f}s">'
                       f'<path fill="{ink}" d="{lleno}"/>'
                       + (f'<path fill="{ink}" fill-opacity="{TENUE}" d="{tenue}"/>' if tenue else "") + "</g>")
        rayos = "".join(f"M{x * 10} {y * 10}h4v{l * 10 - 2}h-4z" for x, y, l in lineas)
        out.append(f'<path class="hc-fx" fill="{ink}" opacity="0" d="{rayos}"/>')
    else:
        # Fotograma a media teletransportación: tiras desplazadas y desvaneciéndose.
        for x in range(n):
            lleno, tenue = celdas(PERSONA, pad * 10, 0, columna=x)
            if not lleno:
                continue
            dy = (-1 if x % 2 else 1) * (6 + (x * 7) % 18)
            op = 1 - abs(x - n / 2) / n
            out.append(f'<path fill="{ink}" opacity="{op:.2f}" transform="translate(0 {dy})" d="{lleno + tenue}"/>')
        rayos = "".join(f"M{x * 10} {y * 10}h4v{l * 10 - 2}h-4z" for x, y, l in lineas)
        out.append(f'<path fill="{ink}" fill-opacity="{TENUE}" d="{rayos}"/>')
    return "".join(out), w, h


CORAZON = [".#.#.", "#####", "#####", ".###.", "..#.."]


def m_overlay(pal, anim):
    ink = pal["ink"]
    marco = ["#" * 12] + ["#" + "." * 10 + "#"] * 17 + ["#" * 12]
    out = [dibujo(marco, ink)]
    chats = [(9, "+.######"), (11, "+.####"), (13, "+.#######"), (15, "+.#####")]
    corazones = [(13, 13), (15, 9), (13, 5)]
    if anim:
        out.append(estilo(
            ".ov-live{animation:ov-live 1.2s steps(1) infinite}"
            ".ov-c{animation:ov-c 4.8s infinite backwards}"
            ".ov-h{animation:ov-h 3s linear infinite backwards}"
            "@keyframes ov-live{50%{opacity:.25}}"
            "@keyframes ov-c{0%,8%{opacity:0}12%,88%{opacity:1}94%,100%{opacity:0}}"
            "@keyframes ov-h{0%{transform:translateY(0);opacity:0}15%{opacity:1}70%{opacity:1}100%{transform:translateY(-120px);opacity:0}}"))
        out.append(f'<g class="ov-live">{dibujo(["##", "##"], ink, 20, 20)}</g>')
        out.append(dibujo(["#.#.#"], ink, 50, 20, attrs=f' fill-opacity="{TENUE}"'))
        for i, (y, fila) in enumerate(chats):
            out.append(f'<g class="ov-c" style="animation-delay:{i * 0.5:.1f}s">{dibujo([fila], ink, 20, y * 10)}</g>')
        for i, (x, y) in enumerate(corazones[:3]):
            out.append(f'<g class="ov-h" style="animation-delay:{i:.0f}s">{dibujo(CORAZON, ink, x * 10, 140)}</g>')
    else:
        out.append(dibujo(["##", "##"], ink, 20, 20))
        for y, fila in chats:
            out.append(dibujo([fila], ink, 20, y * 10))
        for i, (x, y) in enumerate(corazones):
            out.append(f'<g opacity="{1 - i * 0.3:.1f}">{dibujo(CORAZON, ink, x * 10, y * 10)}</g>')
    return "".join(out), 190, 190


def m_helix(pal, anim):
    ink, bg = pal["ink"], pal["bg"]
    barras, alto = 13, 14
    rnd = random.Random(7)
    fijas = [5, 8, 11, 14, 10, 7, 12, 9, 13, 6, 9, 5, 3]
    out = [dibujo(["+" * (barras * 2 - 1)], ink, 0, alto * 10 + 10)]
    if not anim:
        g = rejilla(barras * 2 - 1, alto)
        for i, hgt in enumerate(fijas):
            for y in range(alto - hgt, alto):
                g[y][i * 2] = "#"
        out.append(dibujo(filas_de(g), ink))
        return "".join(out), (barras * 2 - 2) * 10 + 8, (alto + 1) * 10 + 8
    css = [".hx{animation:1.8s steps(1) infinite}"]
    g = rejilla(barras * 2 - 1, alto)
    for i in range(barras):
        for y in range(alto):
            g[y][i * 2] = "#"
    out.append(f'<clipPath id="hx-clip"><rect width="{barras * 20}" height="{alto * 10}"/></clipPath>')
    out.append(f'<g clip-path="url(#hx-clip)">{dibujo(filas_de(g), ink)}')
    for i in range(barras):
        pasos = [rnd.randint(2, alto) for _ in range(8)]
        kf = "".join(f"{k * 100 // 8}%{{transform:translateY(-{p * 10}px)}}" for k, p in enumerate(pasos))
        css.append(f"@keyframes hx{i}{{{kf}100%{{transform:translateY(-{pasos[0] * 10}px)}}}}")
        out.append(f'<rect class="hx" style="animation-name:hx{i};transform:translateY(-{pasos[0] * 10}px)" '
                   f'x="{i * 20 - 1}" y="0" width="10" height="{alto * 10}" fill="{bg}"/>')
    out.append("</g>")
    out.insert(0, estilo("".join(css)))
    return "".join(out), (barras * 2 - 2) * 10 + 8, (alto + 1) * 10 + 8


ARCOS = [["#.", ".#", ".#", "#."],
         ["#..", ".#.", "..#", "..#", ".#.", "#.."],
         ["#...", ".#..", "..#.", "...#", "...#", "..#.", ".#..", "#..."]]
CHIP = [".#.#.#.", "#######", "##+####", "#######", "#######", ".#.#.#."]
MONITOR = ["#" * 11] + ["#" + "." * 9 + "#"] * 5 + ["#" * 11, ".....#.....", "...#####..."]
POWER = ["..#..", "#.#.#", "#...#", "#...#", ".###."]


def m_encender(pal, anim):
    ink = pal["ink"]
    out = [dibujo(CHIP, ink, 0, 20), dibujo(MONITOR, ink, 190, 0)]
    pantalla = rejilla(9, 5)
    for y in range(5):
        for x in range(9):
            pantalla[y][x] = "+"
    pegar(pantalla, POWER, 2, 0)
    pos = [(80, 30), (100, 20), (130, 10)]
    if anim:
        out.append(estilo(
            ".ep-a{animation:ep-a 3s infinite backwards}.ep-on{animation:ep-on 3s infinite}"
            "@keyframes ep-a{0%,8%{opacity:.15}16%,60%{opacity:1}70%,100%{opacity:.15}}"
            "@keyframes ep-on{0%,40%{opacity:0}46%,88%{opacity:1}94%,100%{opacity:0}}"))
        for i, (arco, (x, y)) in enumerate(zip(ARCOS, pos)):
            out.append(f'<g class="ep-a" style="animation-delay:{i * 0.25:.2f}s">{dibujo(arco, ink, x, y)}</g>')
        out.append(f'<g class="ep-on">{dibujo(filas_de(pantalla), ink, 200, 10)}</g>')
    else:
        for arco, (x, y) in zip(ARCOS, pos):
            out.append(dibujo(arco, ink, x, y))
        out.append(dibujo(filas_de(pantalla), ink, 200, 10))
    return "".join(out), 298, 88


NUBE = ["....####.......", "..########.###.", ".##############", "###############", ".#############."]
RAYO = [".....###", "....###.", "...###..", "..######", "....###.", "...###..", "..###...", ".##.....", "#......."]


def m_herederos(pal, anim):
    ink = pal["ink"]
    out = [dibujo(NUBE, ink)]
    gotas = [(1, 6), (12, 7), (14, 6), (0, 9), (13, 10)]
    if anim:
        out.append(estilo(
            ".hd-b{animation:hd-b 3s infinite}.hd-g{animation:hd-g 1.2s linear infinite backwards}"
            "@keyframes hd-b{0%,58%{opacity:.15}61%{opacity:1}63%{opacity:.3}66%,82%{opacity:1}92%,100%{opacity:.15}}"
            "@keyframes hd-g{0%{transform:translateY(0);opacity:0}20%{opacity:1}100%{transform:translateY(50px);opacity:0}}"))
        out.append(f'<g class="hd-b">{dibujo(RAYO, ink, 40, 50)}</g>')
        for i, (x, y) in enumerate(gotas):
            out.append(f'<g class="hd-g" style="animation-delay:{i * 0.23:.2f}s">'
                       f'{dibujo(["+", "+"], ink, x * 10, y * 10)}</g>')
    else:
        out.append(dibujo(RAYO, ink, 40, 50))
        for x, y in gotas:
            out.append(dibujo(["+", "+"], ink, x * 10, y * 10))
    return "".join(out), 148, 138


HEART = [".###...###.", "#####.#####", "###########", "##+########", "###########",
         ".#########.", "..#######..", "...#####...", "....###....", ".....#....."]


def m_hardcore(pal, anim):
    ink = pal["ink"]
    rnd = random.Random(3)
    cols = [rnd.randint(1, 4) for _ in range(23)]
    out = []
    if anim:
        out.append(estilo(
            ".hh-c{transform-box:fill-box;transform-origin:center;animation:hh-b .9s ease-in-out infinite,hh-l 5s infinite}"
            ".hh-t{animation:hh-t 5s infinite backwards}"
            "@keyframes hh-b{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}"
            "@keyframes hh-l{0%,4%{opacity:1}6%{opacity:.2}8%{opacity:1}10%{opacity:.2}13%,100%{opacity:1}}"
            "@keyframes hh-t{0%,12%{opacity:0}16%,90%{opacity:1}94%,100%{opacity:0}}"))
        out.append(f'<g class="hh-c">{dibujo(HEART, ink, 60, 0)}</g>')
    else:
        out.append(dibujo(HEART, ink, 60, 0))
    for i, hgt in enumerate(cols):
        col = ["+" if y == 0 else "#" for y in range(hgt)]
        bloque = dibujo([c for c in col], ink, i * 10, 160 - hgt * 10 + 10)
        if anim:
            out.append(f'<g class="hh-t" style="animation-delay:{i * 0.05:.2f}s">{bloque}</g>')
        else:
            out.append(bloque)
    return "".join(out), 228, 168


DOC = ["#####...", "#...##..", "#...#.#.", "#...####", "#......#", "#.####.#",
       "#......#", "#.#####.", "#......#", "#.###..#", "#......#", "########"]
DOC[7] = "#.#####" + "#"
FLECHA = ["....#..", "....##.", "#######", "....##.", "....#.."]
HASH = [".#.#.", "#####", ".#.#.", "#####", ".#.#."]


def m_doc2md(pal, anim):
    ink = pal["ink"]
    hoja = ["#" * 10] + ["#" + "." * 8 + "#"] * 10 + ["#" * 10]
    out = [dibujo(DOC, ink), dibujo(hoja, ink, 190, 0)]
    partes = [dibujo(HASH, ink, 210, 20), dibujo(["######"], ink, 210, 80), dibujo(["++++"], ink, 210, 100)]
    if anim:
        out.append(estilo(
            ".dm-a{animation:dm-a 1s steps(1) infinite}.dm-l{animation:dm-l 3.6s infinite backwards}"
            "@keyframes dm-a{50%{transform:translateX(10px)}}"
            "@keyframes dm-l{0%,18%{opacity:0}22%,88%{opacity:1}94%,100%{opacity:0}}"))
        out.append(f'<g class="dm-a">{dibujo(FLECHA, ink, 100, 30)}</g>')
        for i, p in enumerate(partes):
            out.append(f'<g class="dm-l" style="animation-delay:{i * 0.45:.2f}s">{p}</g>')
    else:
        out.append(dibujo(FLECHA, ink, 100, 30))
        out.extend(partes)
    return "".join(out), 288, 118


def m_subneteo(pal, anim):
    ink = pal["ink"]
    ip = [192, 168, 100, 170]
    pref = 26
    bits = [int(b) for o in ip for b in f"{o:08b}"]
    mask = [1 if i < pref else 0 for i in range(32)]
    red = [a & b for a, b in zip(bits, mask)]
    bc = [r | (1 - m) for r, m in zip(red, mask)]

    def fila(vals):
        s = ""
        for i, v in enumerate(vals):
            if i and i % 8 == 0:
                s += "."
            s += "#" if v else "+"
        return s

    def x_de(i):
        return (i + i // 8) * 10

    out = [dibujo([fila(bits)], ink, 0, 0)]
    corte = x_de(pref) - 6
    out.append(f'<rect x="{corte}" y="-6" width="4" height="110" fill="{ink}" fill-opacity="{TENUE}"/>')
    out.append(f'<path fill="{ink}" d="{texto_pixel("/26", x_de(31) + 8 - ancho_texto("/26", 5), 130, 5)}"/>')
    if anim:
        out.append(estilo(
            ".sn-m{animation:sn-m 4s infinite backwards}.sn-r{animation:sn-r 4s infinite backwards}"
            "@keyframes sn-m{0%,4%{opacity:.4}7%,90%{opacity:1}95%,100%{opacity:.4}}"
            "@keyframes sn-r{0%,52%{opacity:0}56%,90%{opacity:1}95%,100%{opacity:0}}"))
        for i, v in enumerate(mask):
            c = "#" if v else "+"
            if v:
                out.append(f'<g class="sn-m" style="animation-delay:{i * 0.05:.2f}s">{dibujo([c], ink, x_de(i), 30)}</g>')
            else:
                out.append(dibujo([c], ink, x_de(i), 30))
        out.append(f'<g class="sn-r">{dibujo([fila(red)], ink, 0, 60)}</g>')
        out.append(f'<g class="sn-r" style="animation-delay:.3s">{dibujo([fila(bc)], ink, 0, 90)}</g>')
    else:
        for i, vals in enumerate((mask, red, bc)):
            out.append(dibujo([fila(vals)], ink, 0, 30 + i * 30))
    return "".join(out), x_de(31) + 8, 165


# Motivos fijos, solo para las imágenes de los repos públicos.
def m_hanoi(pal, anim):
    g = rejilla(29, 10)
    for c in (4, 14, 24):
        for y in range(1, 9):
            g[y][c] = "#"
    for y, w in ((6, 3), (7, 5), (8, 7)):
        for x in range(4 - w // 2, 4 + w // 2 + 1):
            g[y][x] = "#"
    for x in range(12, 17):
        g[2][x] = "+"
    for x in range(29):
        g[9][x] = "#"
    return dibujo(filas_de(g), pal["ink"]), 288, 98


def m_procesador(pal, anim):
    marco = ["#" * 14] + ["#" + "." * 12 + "#"] * 10 + ["#" * 14]
    g = [list(f) for f in marco]
    pegar(g, ["++", "++"], 9, 2)
    pegar(g, ["....#.......", "...###......", "..#####.#...", ".#######+#..", "##########+#"], 1, 6)
    hist = rejilla(15, 12)
    for i, hgt in enumerate([3, 6, 9, 7, 11, 8, 5, 4]):
        for y in range(12 - hgt, 12):
            hist[y][i * 2] = "#"
    return dibujo(filas_de(g), pal["ink"]) + dibujo(filas_de(hist), pal["ink"], 170, 0), 318, 118


def m_tienda(pal, anim):
    pocion = ["...###...", "....#....", "...###...", "..#...#..", ".#.....#.",
              "#+++++++#", "#+++++++#", ".#+++++#.", "..#####.."]
    moneda = [".####.", "#....#", "#.##.#", "#.##.#", "#....#", ".####."]
    return dibujo(pocion, pal["ink"]) + dibujo(moneda, pal["ink"], 120, 30), 178, 88


def m_hyprland(pal, anim):
    g = rejilla(19, 9)
    pegar(g, ["#" * 11, "#" * 11] + ["#" + "." * 9 + "#"] * 6 + ["#" * 11], 0, 0)
    pegar(g, ["#" * 7, "#" * 7, "#.....#", "#######"], 12, 0)
    pegar(g, ["#" * 7, "#" * 7, "#.....#", "#######"], 12, 5)
    pegar(g, ["+++", "+++", "+++"], 4, 3)
    cursor = ["#....", "##...", "#+#..", "#++#.", "#+++#", "#.#..", "...#."]
    return dibujo(filas_de(g), pal["ink"]) + dibujo(cursor, pal["ink"], 210, 50), 258, 118


def m_sensor(pal, anim):
    gota = ["....#....", "...###...", "..##.##..", ".##...##.", "##.....##",
            "#+++++++#", "#+++++++#", ".#+++++#.", "..#####.."]
    curva = rejilla(13, 9)
    for i, hgt in enumerate([2, 3, 3, 4, 6, 5, 7]):
        curva[9 - hgt][i * 2] = "#"
    return dibujo(gota, pal["ink"]) + dibujo(filas_de(curva), pal["ink"], 120, 0), 248, 88


# ---------------------------------------------------------------- tarjetas
CANDADO = [".###.", "#...#", "#####", "##.##", "#####"]
DESTACADOS = [
    ("helcam", "HelCam", "Te teletransportas de la videollamada", "Python · MediaPipe · OpenCV · Qt", False, m_helcam),
    ("overlay", "Helminths Overlay", "Overlay interactivo para directos", "Node.js · React · Flutter", True, m_overlay),
    ("helix", "Helix", "Reproductor de FLAC para Android", "Kotlin · Compose · C++", True, m_helix),
    ("encender-pc", "Encender PC", "Enciende el PC desde cualquier sitio", "ESP32 · Kotlin · Python", True, m_encender),
    ("herederos", "Los Herederos", "Poderes de dioses griegos en Minecraft", "Java · Forge 1.20.1", True, m_herederos),
    ("hardcore", "Helminths Hardcore", "Si alguien muere, el mundo se borra", "Java · Paper · Python", True, m_hardcore),
    ("doc2md", "doc2md", "Documentos a Markdown para LLMs", "Python · Flask", False, m_doc2md),
    ("subneteo", "Subneteo", "Practica subneteo IPv4 paso a paso", "HTML · JavaScript", False, m_subneteo),
]
TW, TH = 800, 440


def tarjeta(titulo, frase, tech, privado, motivo, pal):
    arte, mw, mh = motivo(pal, True)
    mx, my = round((TW - mw) / 2), round((250 - mh) / 2 + 14)
    partes = [f'<rect x="1" y="1" width="{TW - 2}" height="{TH - 2}" rx="24" fill="{pal["bg"]}" stroke="{pal["faint"]}" stroke-width="2"/>',
              f'<g transform="translate({mx} {my})" shape-rendering="crispEdges">{arte}</g>',
              f'<path fill="{pal["ink"]}" shape-rendering="crispEdges" d="{texto_pixel(titulo, 44, 284, 6)}"/>',
              texto(44, 372, frase, 30, pal["soft"]),
              f'<g opacity=".75">{texto(44, 410, tech, 22, pal["soft"])}</g>']
    if privado:
        x = TW - 44 - ancho_texto("PRIVADO", 3) - 24
        partes.append(f'<g fill="{pal["soft"]}" shape-rendering="crispEdges">'
                      f'<path d="{celdas(CANDADO, x, 38, 3, 3)[0]}"/>'
                      f'<path d="{texto_pixel("PRIVADO", x + 24, 38, 3)}"/></g>')
    return svg(TW, TH, "".join(partes), f"{titulo}: {frase}. {tech}")


# ---------------------------------------------------------------- adornos
def separador(pal):
    cola = "".join(f'<rect x="{4 - i * 12}" y="10" width="4" height="4" fill="{pal["ink"]}" opacity="{o}"/>'
                   for i, o in enumerate((1, .6, .35, .15)))
    cuerpo = (estilo(".cm{animation:cm 7s steps(84) infinite}@keyframes cm{from{transform:translateX(-12px)}to{transform:translateX(996px)}}")
              + f'<defs><pattern id="pt" width="12" height="24" patternUnits="userSpaceOnUse">'
                f'<rect x="4" y="10" width="4" height="4" fill="{pal["faint"]}"/></pattern></defs>'
              + '<rect width="960" height="24" fill="url(#pt)"/>'
              + f'<g class="cm" shape-rendering="crispEdges">{cola}</g>')
    return svg(960, 24, cuerpo, "")


MONSTRUO_A = [
    "...........####...",
    "..........######..",
    "..........#+#####.",
    ".##.......######..",
    "####.....####.....",
    "#.###...#####.....",
    "...##########.....",
    "..############....",
    ".#############....",
    "##..#########.....",
    "#....##...##......",
    ".....##...##......",
]
MONSTRUO_B = MONSTRUO_A[:10] + ["#.....##.##.......", "......##.##......."]
CAZADOR_A = [
    ".......#",
    "......#.",
    "..###.#.",
    ".#####..",
    ".#+###..",
    "..###...",
    ".######.",
    "#.####.#",
    "..####..",
    "..#..#..",
    ".##..##.",
]
CAZADOR_B = CAZADOR_A[:9] + [".#....#.", "##....##"]


def monstruo(pal):
    ink = pal["ink"]
    suelo = f'<rect x="0" y="146" width="960" height="4" fill="{pal["faint"]}"/>'
    paso_a = dibujo(MONSTRUO_A, ink, 120, 26) + dibujo(CAZADOR_A, ink, 0, 36)
    paso_b = dibujo(MONSTRUO_B, ink, 120, 26) + dibujo(CAZADOR_B, ink, 0, 36)
    cuerpo = (estilo(".mv{animation:mv 20s steps(124) infinite}"
                     ".pa{animation:pa .5s steps(1) infinite}.pb{animation:pb .5s steps(1) infinite}"
                     "@keyframes mv{from{transform:translateX(-300px)}to{transform:translateX(940px)}}"
                     "@keyframes pa{50%{opacity:0}}@keyframes pb{0%{opacity:0}50%{opacity:1}}")
              + suelo
              + f'<g class="mv" shape-rendering="crispEdges"><g class="pa">{paso_a}</g><g class="pb" opacity="0">{paso_b}</g></g>')
    return svg(960, 150, cuerpo, "Un cazador persigue a un pequeño dragón por el pie de página")


# ---------------------------------------------------------------- imágenes para compartir
SOCIAL = [
    ("helcam", "HelCam", "Teletransporte estilo anime para tu webcam", "Python · MediaPipe · OpenCV · Qt", m_helcam),
    ("doc2md_app", "doc2md", "PDF, DOCX, PPTX y XLSX a Markdown limpio", "Python · Flask", m_doc2md),
    ("subneteo-paso-a-paso", "Subneteo", "Practica subneteo IPv4 paso a paso", "HTML · JavaScript", m_subneteo),
    ("Algoritmos-Busqueda-AI", "Búsqueda IA", "BFS y DFS: Hanoi, Jarras de Agua y 8-Puzzle", "Java · Swing", m_hanoi),
    ("Procesador-Imagenes-Java", "Procesador", "Filtros de imagen e histogramas RGB", "Java · Swing", m_procesador),
    ("Python-Store-Logic", "Store Logic", "Inventario y ventas de una tienda RPG", "Python", m_tienda),
    ("Hyprland-Minecraft-Tools", "Hyprland MC", "Herramienta AFK para Minecraft en Wayland", "Python · Hyprland · ydotool", m_hyprland),
    ("Sensor-de-agua-arduino", "Nivel de agua", "Un ESP32 grafica el nivel en tiempo real", "ESP32 · Arduino · Chart.js", m_sensor),
]
ICONO = (repo / "assets/icono-blanco-transparente.svg").read_text(encoding="utf-8")


def social(titulo, frase, tech, motivo):
    pal = PALETAS["oscuro"]
    arte, mw, mh = motivo(pal, False)
    escala = min(2.0, 400 / mw, 300 / mh)
    mx, my = 1280 - 96 - mw * escala, 80 + (300 - mh * escala) / 2
    icono = ICONO.split(">", 1)[1].rsplit("</svg>", 1)[0]
    p = min(12, int((mx - 96 - 48) / ancho_texto(titulo, 1)))
    partes = [f'<rect width="1280" height="640" fill="{pal["bg"]}"/>',
              f'<g transform="translate(90 76) scale(.5)" shape-rendering="crispEdges">{icono}</g>',
              texto(158, 116, "helminth117", 30, pal["soft"]),
              f'<g transform="translate({mx:.0f} {my:.0f}) scale({escala:g})" shape-rendering="crispEdges">{arte}</g>',
              f'<path fill="{pal["ink"]}" shape-rendering="crispEdges" d="{texto_pixel(titulo, 96, 240, p)}"/>',
              texto(96, 470, frase, 42, pal["ink"]),
              texto(96, 540, tech, 30, pal["soft"]),
              f'<rect x="96" y="580" width="1088" height="4" fill="{pal["faint"]}"/>']
    return svg(1280, 640, "".join(partes), titulo)


def main():
    (repo / "assets/proyectos").mkdir(parents=True, exist_ok=True)
    for nombre, pal in PALETAS.items():
        for slug, titulo, frase, tech, privado, motivo in DESTACADOS:
            (repo / f"assets/proyectos/{slug}-{nombre}.svg").write_text(
                tarjeta(titulo, frase, tech, privado, motivo, pal), encoding="utf-8")
        (repo / f"assets/separador-{nombre}.svg").write_text(separador(pal), encoding="utf-8")
        (repo / f"assets/monstruo-{nombre}.svg").write_text(monstruo(pal), encoding="utf-8")
    destino = repo / "assets/social"
    destino.mkdir(exist_ok=True)
    rsvg = shutil.which("rsvg-convert")
    for nombre, titulo, frase, tech, motivo in SOCIAL:
        fuente = destino / f"{nombre}.svg"
        fuente.write_text(social(titulo, frase, tech, motivo), encoding="utf-8")
        if rsvg:
            subprocess.run([rsvg, "-w", "1280", "-h", "640", "-o", str(destino / f"{nombre}.png"), str(fuente)], check=True)
        fuente.unlink()
    print(f"{len(DESTACADOS)} tarjetas x2, separador, monstruo y {len(SOCIAL)} imágenes sociales"
          + ("" if rsvg else " (sin rsvg-convert: no hay PNG)"))


main()
