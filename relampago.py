"""Ofertas relámpago de Mercado Libre → sección dorada de la web.  python relampago.py [--no-push]
1) lee 5 páginas de /ofertas?promotion_type=lightning con la sesión de ml_chrome
2) elige las 16 mejores (descuento × ventas, ≥500 vendidos, ≥20 % OFF, sin productos médicos)
3) genera link + código de afiliado en el Generador del hub, baja fotos, escribe relampago.json
4) build.py + git push (GitHub Pages)"""
import json, math, re, subprocess, sys, time, urllib.request
import datetime as dt
from pathlib import Path
from playwright.sync_api import sync_playwright

D = Path(__file__).parent
PERFIL = r"D:\claude\clipping\cuentas\ml_chrome"
BAD = re.compile(r"(?i)tiras|medic|insulin|pañal|cobertizo|freestyle|gluc|nebuliz|tensi|nitrilo|sensor|anmat|preservativ|arma")
JS = r"""()=>[...document.querySelectorAll('.poly-card')].map(c=>({t:(c.querySelector('.poly-component__title')||{}).innerText,
 href:(c.querySelector('a')||{}).href, img:(c.querySelector('img')||{}).src, txt:c.innerText.replace(/\s+/g,' ')}))"""


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def parse(raw):
    now = dt.datetime.now(); seen = set(); out = []
    for x in raw:
        t = x["txt"]
        if not x.get("t") or "OFF" not in t or "click1." in (x["href"] or ""):
            continue
        k = x["href"].split("?")[0]
        if k in seen:
            continue
        seen.add(k)
        m = re.match(r"(\d) (\d) : (\d) (\d) : (\d) (\d)", t)
        fin = (now + dt.timedelta(hours=int(m[1] + m[2]), minutes=int(m[3] + m[4]), seconds=int(m[5] + m[6]))).strftime("%Y-%m-%dT%H:%M:%S") if m else ""
        v = re.search(r"\+([\d.,]+ ?(?:mil)?) vendidos", t); vn = 0
        if v:
            s = v[1].replace(" ", ""); vn = float(s.replace("mil", "").replace(".", "").replace(",", ".")) * (1000 if "mil" in s else 1)
        r = re.search(r"(\d\.\d) \|", t)
        pr = [int(a.replace(".", "")) for a in re.findall(r"\$ ([\d.]+)", t)]
        off = int(re.search(r"(\d+)% OFF", t)[1])
        if len(pr) < 2:
            continue
        out.append(dict(titulo=x["t"], url=k, img=x["img"], vendidos=vn, rating=float(r[1]) if r else None,
                        precio=pr[1], off=off, fin=fin))
    C = [x for x in out if x["vendidos"] >= 500 and x["off"] >= 20 and not BAD.search(x["titulo"])]
    C.sort(key=lambda x: -(x["off"] * math.log10(x["vendidos"] + 10)))
    return C[:16]


with sync_playwright() as p:
    c = p.chromium.launch_persistent_context(PERFIL, channel="chrome", headless=False, ignore_default_args=["--enable-automation"],
                                             args=["--disable-blink-features=AutomationControlled", "--window-position=-32000,-32000"],
                                             viewport={"width": 1400, "height": 1000})
    pg = c.pages[0]
    pg.set_default_navigation_timeout(120000)  # 25-nov: la página de ofertas puede tardar >30 s en cargar
    raw = []
    for page in range(1, 6):
        pg.goto(f"https://www.mercadolibre.com.ar/ofertas?promotion_type=lightning&page={page}", wait_until="domcontentloaded"); time.sleep(3)
        for _ in range(4):
            pg.mouse.wheel(0, 3000); time.sleep(0.7)
        raw += pg.evaluate(JS)
    sel = parse(raw)
    log("relámpago:", len(raw), "tarjetas →", len(sel), "elegidas")
    # códigos de afiliado
    resp = []
    pg.on("response", lambda r: resp.append(r) if "linkbuilder/createLink" in r.url else None)
    pg.goto("https://www.mercadolibre.com.ar/afiliados/hub", wait_until="domcontentloaded"); time.sleep(7)
    pg.get_by_text(re.compile("Generador de links|Generar link", re.I)).first.click(); time.sleep(4)
    for i in range(0, len(sel), 10):
        pg.locator("textarea:visible").first.fill("\n".join(x["url"] for x in sel[i:i + 10])); time.sleep(1)
        pg.get_by_role("button", name=re.compile("^Generar$", re.I)).last.click(); time.sleep(10)
    m = {}
    for r in resp:
        try:
            for u in r.json().get("urls", []):
                m[u["origin_url"].split("?")[0]] = u
        except Exception:
            pass
    c.close()

for i, x in enumerate(sel):
    u = m.get(x["url"])
    x["codigo"] = u["regex"] if u else ""
    x["link"] = u["short_url"] if u else ""
    fn = f"img/r{i:02d}.webp"
    for uu in (x["img"].replace("-E.webp", "-O.webp"), x["img"]):
        try:
            (D / fn).write_bytes(urllib.request.urlopen(urllib.request.Request(uu, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read()); break
        except Exception:
            pass
    x["foto"] = fn
(D / "relampago.json").write_text(json.dumps(sel, ensure_ascii=False, indent=1), encoding="utf-8")
log("con código:", sum(1 for x in sel if x["codigo"]), "/", len(sel))
subprocess.run([sys.executable, str(D / "build.py")], check=True, cwd=D)
if "--no-push" not in sys.argv:
    g = ["git", "-c", "user.name=andinoworks", "-c", "user.email=andinoworks@users.noreply.github.com"]
    subprocess.run(g + ["add", "-A"], cwd=D)
    subprocess.run(g + ["commit", "-qm", "Ofertas relámpago " + time.strftime("%d/%m %H:%M")], cwd=D)
    subprocess.run(["git", "push", "-q"], cwd=D)
    log("publicado")
