"""Genera index.html desde productos.json (python build.py)."""
import json, html
from pathlib import Path

D = Path(__file__).parent
P = json.loads((D / "productos.json").read_text(encoding="utf-8"))

NIVEL = {  # remate de cada gancho
    "calor": "Pelopincho en el patio", "mosquitos": "tul de princesa", "mate": "luz para cebar de noche",
    "wifi": "repetidor en el pasillo", "asado": "chulengo propio", "gym": "mancuernas de 25 kg",
    "cocina": "freidora de aire", "vacaciones": "reposera gravedad cero", "cine": "proyector en la pared",
    "vago": "robot que barre solo",
}
TIT = {
    "calor": "Sobrevivir al calor", "mosquitos": "Guerra a los mosquitos", "mate": "Mate de competición",
    "wifi": "El WiFi no llega al baño", "asado": "Asado de domingo", "gym": "En forma sin gimnasio",
    "cocina": "Cocinar sin saber", "vacaciones": "Vacaciones con poca plata", "cine": "Cine en casa",
    "vago": "Ordenar sin moverse",
}


def ars(n):
    return "$ " + f"{int(n):,}".replace(",", ".")


def vend(v):
    v = int(v or 0)
    return f"+{v // 1000} mil vendidos" if v >= 1000 else f"+{v} vendidos"


grupos = []
for p in P:
    if p["grupo"] not in grupos:
        grupos.append(p["grupo"])

secs = []
for gi, g in enumerate(grupos):
    cards = []
    for p in [x for x in P if x["grupo"] == g]:
        antes = ""
        if p.get("off"):
            pa = round(p["precio"] * 100 / (100 - p["off"]), -2)
            antes = f'<s>{ars(pa)}</s><b class="off">{p["off"]}% OFF</b>'
        t = html.escape(p["titulo"])
        cards.append(f'''<article class="card">
  <a class="ph" href="{p["link"]}" target="_blank" rel="sponsored noopener"><img src="{p["foto"]}" alt="{t}" loading="lazy" width="500" height="500"></a>
  <div class="bd">
    <p class="meta">{vend(p["vendidos"])}{f' · ★ {p["rating"]}' if p.get("rating") else ""}</p>
    <h3>{t}</h3>
    <p class="pr"><strong>{ars(p["precio"])}</strong>{antes}</p>
    <div class="act">
      <a class="btn" href="{p["link"]}" target="_blank" rel="sponsored noopener">Ver precio de hoy</a>
      <button class="code" data-code="{p["codigo"]}" aria-label="Copiar código {p["codigo"]}"><span>Código</span>{p["codigo"]}</button>
    </div>
  </div>
</article>''')
    secs.append(f'''<section class="grp" id="{g}">
  <div class="wrap">
    <header class="gh"><p class="num">{gi + 1:02d}</p><h2>{TIT[g]} <em>(nivel: {NIVEL[g]})</em></h2></header>
    <div class="grid">{"".join(cards)}</div>
  </div>
</section>''')

chips = "".join(f'<a href="#{g}">{TIT[g]}</a>' for g in grupos)
hero_imgs = "".join(f'<img src="{p["foto"]}" alt="" style="--i:{i}">' for i, p in enumerate(
    [P[i] for i in (2, 0, 15, 30, 8, 21)]))
total = len(P)

page = f'''<!doctype html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nivel Oferta</title>
<meta name="description" content="Los productos que aparecen en nuestros videos, con link directo y código para buscarlos en Mercado Libre.">
<meta property="og:title" content="Nivel Oferta">
<meta property="og:description" content="Lo que mostramos en los videos, con link directo.">
<meta name="theme-color" content="#f5efe4">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23e0482a'/%3E%3Cpath d='M9 22V10l14 12V10' stroke='%23fff' stroke-width='3.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Instrument+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--bg:#f5efe4;--surface:#fffdf8;--ink:#17140f;--muted:#6d655a;--line:#e3d9c8;--accent:#e0482a;--accent-ink:#fff;--soft:#fbe3d6;--ok:#1f7a55;
--r:14px;--ease:cubic-bezier(.23,1,.32,1);--gut:clamp(16px,4vw,48px)}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#14120f;--surface:#1d1a16;--ink:#f3ede2;--muted:#a59c8e;--line:#2f2a23;--soft:#3a2219}}}}
:root[data-theme="dark"]{{--bg:#14120f;--surface:#1d1a16;--ink:#f3ede2;--muted:#a59c8e;--line:#2f2a23;--soft:#3a2219}}
*{{box-sizing:border-box;margin:0}}
html{{scroll-behavior:smooth;scroll-padding-top:72px}}
body{{background:var(--bg);color:var(--ink);font:400 16px/1.5 "Instrument Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}}
a{{color:inherit}}
.wrap{{max-width:1240px;margin:0 auto;padding:0 var(--gut)}}
.skip{{position:absolute;left:-999px}}.skip:focus{{left:16px;top:16px;background:var(--ink);color:var(--bg);padding:8px 12px;z-index:9}}
nav{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
nav .wrap{{display:flex;align-items:center;gap:20px;height:60px}}
.mark{{font:800 20px/1 "Bricolage Grotesque";letter-spacing:-.02em;text-decoration:none;white-space:nowrap}}
.mark i{{font-style:normal;color:var(--accent)}}
.chips{{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;mask-image:linear-gradient(90deg,#000 90%,transparent)}}
.chips a{{flex:none;text-decoration:none;font-size:14px;padding:6px 12px;border-radius:99px;border:1px solid var(--line);color:var(--muted);transition:background .2s,color .2s,border-color .2s}}
.chips a:hover{{color:var(--ink);border-color:var(--ink)}}
.hero{{min-height:calc(100svh - 60px);display:grid;align-items:center;padding:48px 0}}
.hero .wrap{{display:grid;grid-template-columns:1.05fr 1fr;gap:clamp(24px,5vw,72px);align-items:center}}
.hero h1{{font:800 clamp(40px,6.4vw,84px)/.98 "Bricolage Grotesque";letter-spacing:-.035em;text-wrap:balance}}
.hero h1 em{{font-style:normal;color:var(--accent)}}
.hero .lead{{margin-top:22px;font-size:clamp(17px,1.5vw,20px);color:var(--muted);max-width:34ch}}
.facts{{display:flex;gap:28px;margin-top:32px;flex-wrap:wrap}}
.facts b{{display:block;font:800 30px/1 "Bricolage Grotesque";letter-spacing:-.02em}}
.facts span{{font-size:14px;color:var(--muted)}}
.cta{{display:inline-flex;margin-top:34px}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--accent);color:var(--accent-ink);text-decoration:none;font-weight:600;font-size:15px;padding:11px 18px;border-radius:10px;border:0;cursor:pointer;transition:transform .16s var(--ease),filter .2s}}
.btn:hover{{filter:brightness(1.07)}} .btn:active{{transform:scale(.97)}}
.collage{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.collage img{{width:100%;aspect-ratio:1;object-fit:contain;background:#fff;border-radius:var(--r);padding:10%;border:1px solid var(--line)}}
.collage img:nth-child(2),.collage img:nth-child(5){{transform:translateY(28px)}}
.grp{{padding:clamp(64px,9vw,112px) 0;border-top:1px solid var(--line)}}
.gh{{display:flex;gap:18px;align-items:baseline;margin-bottom:36px}}
.num{{font:700 14px/1 "Bricolage Grotesque";color:var(--accent)}}
.gh h2{{font:800 clamp(28px,3.6vw,46px)/1.05 "Bricolage Grotesque";letter-spacing:-.03em;text-wrap:balance}}
.gh h2 em{{font-style:normal;font-weight:500;color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:18px}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;display:flex;flex-direction:column;transition:transform .25s var(--ease),box-shadow .25s var(--ease)}}
@media (hover:hover){{.card:hover{{transform:translateY(-2px);box-shadow:0 14px 30px -18px rgba(40,25,10,.35)}}.card:hover .ph img{{transform:scale(1.03)}}}}
.ph{{display:block;background:#fff;aspect-ratio:1;overflow:hidden}}
.ph img{{width:100%;height:100%;object-fit:contain;padding:9%;transition:transform .45s var(--ease)}}
.bd{{padding:16px;display:flex;flex-direction:column;gap:6px;flex:1}}
.meta{{font-size:13px;color:var(--muted)}}
.card h3{{font-size:15px;font-weight:500;line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.pr{{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-top:2px}}
.pr strong{{font:700 22px/1.1 "Bricolage Grotesque";letter-spacing:-.02em}}
.pr s{{font-size:13px;color:var(--muted)}}
.off{{font-size:12px;color:var(--ok);font-weight:600}}
.act{{display:flex;gap:8px;margin-top:auto;padding-top:10px;flex-wrap:wrap}}
.act .btn{{flex:1;font-size:14px;padding:10px 12px;white-space:nowrap}}
.code{{font:600 12px/1.1 ui-monospace,monospace;background:var(--soft);color:var(--ink);border:0;border-radius:10px;padding:7px 10px;cursor:pointer;text-align:left;transition:transform .16s var(--ease)}}
.code span{{display:block;font:500 10px/1.2 "Instrument Sans";color:var(--muted);text-transform:uppercase;letter-spacing:.06em}}
.code:active{{transform:scale(.96)}}
.how{{padding:clamp(64px,9vw,112px) 0;border-top:1px solid var(--line)}}
.how h2{{font:800 clamp(28px,3.6vw,46px)/1.05 "Bricolage Grotesque";letter-spacing:-.03em;max-width:18ch}}
.steps{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:36px;counter-reset:s}}
.steps p{{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:22px;color:var(--muted)}}
.steps p::before{{counter-increment:s;content:counter(s);display:block;font:800 34px/1 "Bricolage Grotesque";color:var(--accent);margin-bottom:12px}}
.steps b{{color:var(--ink)}}
footer{{border-top:1px solid var(--line);padding:36px 0 48px;font-size:14px;color:var(--muted)}}
footer .wrap{{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}}
.toast{{position:fixed;left:50%;bottom:24px;translate:-50% 0;background:var(--ink);color:var(--bg);padding:10px 16px;border-radius:10px;font-size:14px;opacity:0;transform:translateY(8px);transition:opacity .2s,transform .2s var(--ease);pointer-events:none;z-index:9}}
.toast.on{{opacity:1;transform:none}}
[data-enter]>*{{animation:up .7s var(--ease) both;animation-delay:calc(var(--d,0)*70ms)}}
.collage img{{animation:pop .7s var(--ease) both;animation-delay:calc(200ms + var(--i)*60ms)}}
@keyframes up{{from{{opacity:0;transform:translateY(14px)}}}}
@keyframes pop{{from{{opacity:0;scale:.94}}}}
@media (prefers-reduced-motion:reduce){{*,*::before{{animation:none!important;transition:none!important}}}}
@media (max-width:860px){{.hero .wrap{{grid-template-columns:1fr}}.hero{{min-height:auto}}.collage{{order:-1}}.collage img:nth-child(n){{transform:none}}.steps{{grid-template-columns:1fr}}}}
@media (max-width:480px){{.chips{{display:none}}.grid{{grid-template-columns:1fr 1fr;gap:10px}}.bd{{padding:12px}}.pr strong{{font-size:18px}}.act{{flex-direction:column}}.facts{{gap:18px}}}}
</style>
</head>
<body>
<a class="skip" href="#main">Saltar al contenido</a>
<nav><div class="wrap"><a class="mark" href="#top">nivel<i>:</i> oferta</a><div class="chips">{chips}</div></div></nav>
<main id="main">
<section class="hero" id="top"><div class="wrap">
  <div data-enter>
    <h1 style="--d:0">Lo que sale en los videos, <em>con link directo.</em></h1>
    <p class="lead" style="--d:1">Cada producto de nuestros memes, elegido entre los más vendidos de Mercado Libre. Tocá el botón o copiá el código y pegalo en el buscador.</p>
    <div class="facts" style="--d:2"><div><b>{total}</b><span>productos</span></div><div><b>10</b><span>temas</span></div><div><b>+10 mil</b><span>ventas cada uno, casi todos</span></div></div>
    <a class="btn cta" href="#{grupos[0]}" style="--d:3">Ver los productos</a>
  </div>
  <div class="collage" aria-hidden="true">{hero_imgs}</div>
</div></section>
{"".join(secs)}
<section class="how"><div class="wrap">
  <h2>¿Viste el video y no podés tocar el link?</h2>
  <div class="steps">
    <p><b>Copiá el código</b> que aparece al final del video o en la tarjeta del producto.</p>
    <p><b>Abrí Mercado Libre</b> y pegalo en el buscador, como si buscaras cualquier cosa.</p>
    <p><b>Te lleva directo</b> al producto. Comprás igual que siempre, al mismo precio.</p>
  </div>
</div></section>
</main>
<footer><div class="wrap"><p>Links de afiliado: si comprás, recibimos una comisión sin costo extra para vos.</p><p>Precios del 22/11/2026, pueden cambiar. No somos Mercado Libre.</p></div></footer>
<div class="toast" role="status" aria-live="polite"></div>
<script>
const t=document.querySelector('.toast');let h;
document.querySelectorAll('.code').forEach(b=>b.addEventListener('click',async()=>{{
  try{{await navigator.clipboard.writeText(b.dataset.code)}}catch(e){{}}
  t.textContent='Código '+b.dataset.code+' copiado. Pegalo en el buscador de Mercado Libre.';
  t.classList.add('on');clearTimeout(h);h=setTimeout(()=>t.classList.remove('on'),2600);
}}));
</script>
</body>
</html>'''
(D / "index.html").write_text(page, encoding="utf-8")
print("ok", total, "productos")
