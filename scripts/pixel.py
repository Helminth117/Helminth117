"""Piezas comunes del pixel art del perfil: paletas, fuente de 5x7 y dibujos en ASCII.

En los dibujos, "#" es un píxel lleno y "+" uno tenue (como el píxel suelto del logo).
"""

PALETAS = {
    "oscuro": {"bg": "#0D0D0D", "ink": "#F5F5F5", "soft": "#A3A3A3", "faint": "#2B2B2B"},
    "claro": {"bg": "#FFFFFF", "ink": "#0D0D0D", "soft": "#525252", "faint": "#D4D4D4"},
}
FONT_STACK = "ui-monospace,SFMono-Regular,Menlo,Consolas,'JetBrainsMono NF','DejaVu Sans Mono',monospace"
TENUE = 0.4

# Fuente de 7 filas; el ancho de cada letra es el de sus filas.
GLIFOS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    ",": ["..", "..", "..", "..", "..", ".#", "#."],
    ":": [".", "#", ".", ".", ".", "#", "."],
    "-": ["....", "....", "....", "####", "....", "....", "...."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    "%": ["##...", "##..#", "...#.", "..#..", ".#...", "#..##", "...##"],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
}
# Acentos: la letra base más píxeles en las dos filas de arriba (y = -2 y -1).
ACENTOS = {"Á": ("A", [(3, -2), (2, -1)]), "É": ("E", [(3, -2), (2, -1)]),
           "Í": ("I", [(2, -2), (1, -1)]), "Ó": ("O", [(3, -2), (2, -1)]),
           "Ú": ("U", [(3, -2), (2, -1)]), "Ñ": ("N", [(1, -2), (2, -2), (3, -2)])}


def _glifo(ch):
    if ch in ACENTOS:
        base, extra = ACENTOS[ch]
        return GLIFOS[base], extra
    return GLIFOS[ch], []


def ancho_texto(texto, p):
    """Ancho en px de un texto en la fuente pixel, con un píxel de separación entre letras."""
    celdas = sum(len(_glifo(c)[0][0]) + 1 for c in texto.upper()) - 1
    return celdas * p


def texto_pixel(texto, x, y, p):
    """Path "d" de un texto en la fuente pixel; (x, y) es la esquina de arriba de la primera letra."""
    d, cx = [], x
    for ch in texto.upper():
        filas, extra = _glifo(ch)
        for fy, fila in enumerate(filas):
            for fx, c in enumerate(fila):
                if c == "#":
                    d.append(f"M{cx + fx * p:g} {y + fy * p:g}h{p:g}v{p:g}h-{p:g}z")
        for fx, fy in extra:
            d.append(f"M{cx + fx * p:g} {y + fy * p:g}h{p:g}v{p:g}h-{p:g}z")
        cx += (len(filas[0]) + 1) * p
    return "".join(d)


def celdas(filas, x0=0, y0=0, paso=10, lado=8, solo=None, columna=None):
    """Paths "d" (lleno, tenue) de un dibujo en ASCII. `columna` limita el dibujo a una columna."""
    llenos, tenues = [], []
    for fy, fila in enumerate(filas):
        for fx, c in enumerate(fila):
            if columna is not None and fx != columna:
                continue
            if c not in "#+" or (solo and c != solo):
                continue
            (llenos if c == "#" else tenues).append(
                f"M{x0 + fx * paso:g} {y0 + fy * paso:g}h{lado}v{lado}h-{lado}z")
    return "".join(llenos), "".join(tenues)


def dibujo(filas, color, x0=0, y0=0, paso=10, lado=8, attrs=""):
    """Un dibujo en ASCII como uno o dos <path>, con el "+" en tenue."""
    lleno, tenue = celdas(filas, x0, y0, paso, lado)
    out = []
    if lleno:
        out.append(f'<path fill="{color}" d="{lleno}"{attrs}/>')
    if tenue:
        out.append(f'<path fill="{color}" fill-opacity="{TENUE}" d="{tenue}"{attrs}/>')
    return "".join(out)


def tamano(filas, paso=10, lado=8):
    return (len(max(filas, key=len)) - 1) * paso + lado, (len(filas) - 1) * paso + lado


def esc(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def texto(x, y, s, fs, color, anchor="start", peso=400):
    """Texto monoespaciado con ancho fijo por carácter, para que no dependa de la fuente instalada."""
    cw = fs * 0.6
    return (f'<text x="{x:g}" y="{y:g}" fill="{color}" font-family="{FONT_STACK}" font-size="{fs}" '
            f'font-weight="{peso}" text-anchor="{anchor}" textLength="{len(s) * cw:g}" '
            f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{esc(s)}</text>')
