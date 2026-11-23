"""Genera index.html + go/<slug>.html (redirecciones cortas y directas al producto) desde productos.json
y relampago.json (opcional).  python build.py"""
import json, re, unicodedata
from pathlib import Path
from datetime import datetime

D = Path(__file__).parent
TAG = "matt_word=ignacioandino2005&matt_tool=22473167"
BASE = "https://andinoworks.github.io/nivel-oferta"

TIT = {
    "calor": "Sobrevivir al calor", "mosquitos": "Guerra a los mosquitos", "mate": "Mate de competición",
    "wifi": "El WiFi no llega al baño", "asado": "Asado de domingo", "gym": "En forma sin gimnasio",
    "cocina": "Cocinar sin saber", "vacaciones": "Vacaciones con poca plata", "cine": "Cine en casa",
    "vago": "Ordenar sin moverse", "relampago": "Ofertas relámpago", "bici": "Que no te roben la bici", "vecino": "El vecino y su cumbia", "gamer": "Para el que espera el GTA VI",
}
EMO = {"calor": "🥵", "mosquitos": "🦟", "mate": "🧉", "wifi": "📶", "asado": "🥩", "gym": "💪", "cocina": "🍳",
       "vacaciones": "🏖️", "cine": "🍿", "vago": "🛋️", "relampago": "⚡", "bici": "🚲", "vecino": "🔊", "gamer": "🎮"}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    w = [x for x in re.findall(r"[a-z0-9]+", s) if len(x) > 2 and x not in ("de", "con", "para", "the")]
    return "-".join(w[:3])


def directo(url):
    u = url.split("#")[0].split("?")[0]
    return f"{u}?{TAG}"


def items(lst, grupo=None):
    out, used = [], set()
    for p in lst:
        s = slug(p["titulo"])
        while s in used:
            s += "-2"
        used.add(s)
        pa = round(p["precio"] * 100 / (100 - p["off"]), -2) if p.get("off") else 0
        out.append(dict(s=s, t=p["titulo"], g=grupo or p["grupo"], p=p["precio"], pa=pa, off=p.get("off", 0),
                        v=int(p.get("vendidos") or 0), r=p.get("rating"), img=p["foto"], u=p.get("link") or directo(p["url"]),
                        c=p.get("codigo", ""), mv=bool(p.get("mas_vendido")), fin=p.get("fin", "")))
    return out


P = items(json.loads((D / "productos.json").read_text(encoding="utf-8")))
R = []
if (D / "relampago.json").exists():
    R = items(json.loads((D / "relampago.json").read_text(encoding="utf-8")), "relampago")
    for x in R:
        x["s"] = "r-" + x["s"]
ALL = R + P

# redirecciones cortas: /go/<slug>  -> producto directo con la etiqueta de afiliado
go = D / "go"
go.mkdir(exist_ok=True)
for x in ALL:
    (go / f"{x['s']}.html").write_text(
        f'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>Abriendo Mercado Libre…</title>'
        f'<meta http-equiv="refresh" content="0;url={x["u"]}"><script>location.replace({json.dumps(x["u"])})</script>'
        f'<p style="font:16px system-ui;padding:24px">Abriendo el producto en Mercado Libre… <a href="{x["u"]}">tocá acá si no abre</a>.</p>',
        encoding="utf-8")

grupos = []
for x in ALL:
    if x["g"] not in grupos:
        grupos.append(x["g"])
GR = [dict(id=g, t=TIT[g], e=EMO[g], n=sum(1 for x in ALL if x["g"] == g)) for g in grupos]
ahorro = sum(x["pa"] - x["p"] for x in ALL if x["pa"])
maxoff = max(x["off"] for x in ALL)
fecha = datetime.now().strftime("%d/%m/%Y")
marq = [x["img"] for x in sorted(P, key=lambda x: -x["v"])[:18]]

tpl = (D / "plantilla.html").read_text(encoding="utf-8")
html = (tpl.replace("__DATA__", json.dumps(ALL, ensure_ascii=False))
        .replace("__GR__", json.dumps(GR, ensure_ascii=False))
        .replace("__N__", str(len(ALL))).replace("__AHORRO__", str(int(ahorro))).replace("__MAXOFF__", str(maxoff))
        .replace("__FECHA__", fecha)
        .replace("__MARQ1__", "".join(f'<img src="{i}" alt="">' for i in marq[:9]))
        .replace("__MARQ2__", "".join(f'<img src="{i}" alt="">' for i in marq[9:])))
(D / "index.html").write_text(html, encoding="utf-8")
print("ok", len(P), "productos +", len(R), "relámpago; ahorro", ahorro)
