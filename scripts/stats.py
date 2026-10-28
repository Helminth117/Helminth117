"""Genera la tarjeta de estadísticas del perfil (stats-claro.svg y stats-oscuro.svg).

Lee de la API GraphQL de GitHub con el token de GH_TOKEN. Con un token que vea los repos privados,
los lenguajes y los commits los incluyen; los nombres de repos privados solo se muestran si están
en NOMBRES (los proyectos que ya salen en el perfil).

Uso: GH_TOKEN=... python3 scripts/stats.py <ruta del repo> <carpeta de salida>
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pixel import PALETAS, ancho_texto, texto, texto_pixel  # noqa: E402

USUARIO = os.environ.get("GH_USER", "Helminth117")
NOMBRES = {
    "helcam": "HelCam", "HelminthsOverlayReact": "HelminthsOverlay", "Helix": "Helix",
    "encender-pc": "Encender PC", "herederos-dioses": "Los Herederos", "helminths-hardcore": "Helminths Hardcore",
    "serverhardcore-panel": "ServerHardcore Panel", "doc2md_app": "doc2md", "subneteo-paso-a-paso": "Subneteo",
}
MESES = "ene feb mar abr may jun jul ago sep oct nov dic".split()

CONSULTA = """
query($login: String!, $desde: DateTime!, $mes: DateTime!) {
  user(login: $login) {
    anio: contributionsCollection(from: $desde) {
      totalCommitContributions
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
    mes: contributionsCollection(from: $mes) {
      commitContributionsByRepository(maxRepositories: 25) {
        repository { name isPrivate } contributions { totalCount }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name isPrivate
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
        defaultBranchRef { target { ... on Commit { messageHeadline committedDate } } }
      }
    }
  }
}"""


def consultar():
    hoy = dt.datetime.now(dt.timezone.utc)
    variables = {"login": USUARIO,
                 "desde": dt.datetime(hoy.year, 1, 1, tzinfo=dt.timezone.utc).isoformat(),
                 "mes": (hoy - dt.timedelta(days=30)).isoformat()}
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": CONSULTA, "variables": variables}).encode(),
                                 headers={"Authorization": f"bearer {os.environ['GH_TOKEN']}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        datos = json.load(r)
    if "errors" in datos:
        sys.exit(f"GraphQL: {datos['errors']}")
    return hoy, datos["data"]["user"]


def rachas(dias):
    """(racha actual, mejor racha) en días; hoy sin contribuciones todavía no rompe la racha."""
    mejor = actual = 0
    for d in dias:
        actual = actual + 1 if d["contributionCount"] else 0
        mejor = max(mejor, actual)
    actual = 0
    for i, d in enumerate(reversed(dias)):
        if d["contributionCount"]:
            actual += 1
        elif i:
            break
    return actual, mejor


def resumen(hoy, u):
    dias = [d for s in u["anio"]["contributionCalendar"]["weeks"] for d in s["contributionDays"]
            if d["date"] <= hoy.date().isoformat()]
    actual, mejor = rachas(dias)
    bytes_por = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            bytes_por[e["node"]["name"]] = bytes_por.get(e["node"]["name"], 0) + e["size"]
    total = sum(bytes_por.values()) or 1
    lenguajes = sorted(bytes_por.items(), key=lambda kv: -kv[1])[:5]
    lenguajes = [(n, b / total) for n, b in lenguajes]
    activo = None
    for c in sorted(u["mes"]["commitContributionsByRepository"], key=lambda c: -c["contributions"]["totalCount"]):
        repo = c["repository"]
        if repo["name"] != USUARIO and (not repo["isPrivate"] or repo["name"] in NOMBRES):
            activo = (NOMBRES.get(repo["name"], repo["name"]), c["contributions"]["totalCount"])
            break
    ultimo = None
    for repo in u["repositories"]["nodes"]:
        commit = (repo.get("defaultBranchRef") or {}).get("target")
        if not repo["isPrivate"] and commit and repo["name"] != USUARIO:
            fecha = dt.date.fromisoformat(commit["committedDate"][:10])
            ultimo = (NOMBRES.get(repo["name"], repo["name"]), commit["messageHeadline"],
                      f"{fecha.day} {MESES[fecha.month - 1]}")
            break
    return {"anio": hoy.year, "commits": u["anio"]["totalCommitContributions"],
            "contribuciones": u["anio"]["contributionCalendar"]["totalContributions"],
            "repos": u["repositories"]["totalCount"], "racha": actual, "mejor": mejor,
            "lenguajes": lenguajes, "n_lenguajes": len(bytes_por), "activo": activo, "ultimo": ultimo}


def recortar(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


def tarjeta(r, pal):
    W, H = 960, 330
    ink, soft, faint = pal["ink"], pal["soft"], pal["faint"]
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="{pal["bg"]}" stroke="{faint}" stroke-width="2"/>',
         f'<g shape-rendering="crispEdges">']

    def etiqueta(s, x, y, paso=2):
        p.append(f'<path fill="{soft}" d="{texto_pixel(s, x, y, paso)}"/>')

    # Columna izquierda: números grandes.
    etiqueta(f"COMMITS {r['anio']}", 44, 44, 3)
    p.append(f'<path fill="{ink}" d="{texto_pixel(str(r["commits"]), 44, 76, 8)}"/>')
    datos = [("CONTRIBUCIONES", r["contribuciones"]), ("RACHA", f"{r['racha']} DÍA" + ("" if r["racha"] == 1 else "S")), ("LENGUAJES", r["n_lenguajes"]),
             ("REPOS", r["repos"])]
    for i, (k, v) in enumerate(datos):
        x, y = 44 + (i % 2) * 200, 158 + (i // 2) * 64
        etiqueta(k, x, y)
        p.append(f'<path fill="{ink}" d="{texto_pixel(str(v), x, y + 22, 4)}"/>')
    p.append(f'<rect x="440" y="44" width="2" height="226" fill="{faint}"/>')

    # Columna derecha: lenguajes con barras de píxeles.
    etiqueta("MÁS USADOS", 480, 44, 3)
    celdas = 26
    for i, (nombre, frac) in enumerate(r["lenguajes"]):
        y = 78 + i * 38
        p.append("</g>" + texto(480, y + 15, recortar(nombre, 12), 20, ink) + '<g shape-rendering="crispEdges">')
        llenas = max(1, round(frac * celdas))
        for c in range(celdas):
            color, op = (ink, 1) if c < llenas else (faint, 1)
            p.append(f'<rect x="{640 + c * 9}" y="{y + 2}" width="7" height="14" fill="{color}" opacity="{op}"/>')
        pct = f"{frac * 100:.0f}%"
        p.append(f'<path fill="{soft}" d="{texto_pixel(pct, 916 - ancho_texto(pct, 2), y + 2, 2)}"/>')
    p.append("</g>")

    # Pie: proyecto del mes y último commit público.
    p.append(f'<rect x="44" y="282" width="{W - 88}" height="2" fill="{faint}"/>')
    pie = []
    if r["activo"]:
        pie.append(f"proyecto del mes: {r['activo'][0]}")
    if r["ultimo"]:
        pie.append(f"último commit: {r['ultimo'][0]} — {r['ultimo'][1]} · {r['ultimo'][2]}")
    if pie:
        p.append(texto(44, 312, recortar("   ".join(pie), 86), 17, soft))
    etiqueta_aria = (f"{r['commits']} commits en {r['anio']}, {r['contribuciones']} contribuciones, racha de "
                     f"{r['racha']} días. Lenguajes: " + ", ".join(f"{n} {f * 100:.0f}%" for n, f in r["lenguajes"]))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{etiqueta_aria}">{"".join(p)}</svg>\n')


def main():
    salida = Path(sys.argv[2])
    salida.mkdir(parents=True, exist_ok=True)
    r = resumen(*consultar())
    for nombre, pal in PALETAS.items():
        (salida / f"stats-{nombre}.svg").write_text(tarjeta(r, pal), encoding="utf-8")
    print(json.dumps({k: v for k, v in r.items() if k != "ultimo"}, ensure_ascii=False))


main()
