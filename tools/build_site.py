"""Assemble the interactive profile site (docs/index.html) from the generated SVGs.

GitHub renders README images through <img>, which is non-interactive by design -
no hover, no tooltips, no :hover styles. This page inlines the same SVGs so every
element carrying data-tip (bars, ticks, day cells, prisms, keycaps, KPIs) gets a
real hover tooltip, plus hover lift / glow on cards and buttons.

    python tools/build_site.py [assets-dir] [docs-dir]
"""
import os
import re
import sys

ASSETS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "assets")
DOCS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "docs")
os.makedirs(DOCS, exist_ok=True)

LINKS = {
    "email": "mailto:lokeshe0912@gmail.com",
    "linkedin": "https://www.linkedin.com/in/lokesh-e-60a583201",
    "huggingface": "https://huggingface.co/lokeshe09",
    "portfolio": "https://lokeshe-09.github.io/",
    "aca": "https://aicraftalchemy.github.io/",
}

_n = [0]


def inline(name, theme, cls="", wrap=True):
    """Inline an SVG with all ids namespaced so dark + light sets can coexist."""
    path = os.path.join(ASSETS, f"{name}-{theme}.svg")
    s = open(path, encoding="utf-8").read()
    _n[0] += 1
    p = f"{theme[0]}{_n[0]}-"
    s = re.sub(r'id="([^"]+)"', lambda m: f'id="{p}{m.group(1)}"', s)
    s = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{p}{m.group(1)})', s)
    s = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{p}{m.group(1)}"', s)
    s = s.replace('<svg ', '<svg class="asset" ', 1)
    if not wrap:
        return s
    return f'<div class="card {cls} only-{theme}">{s}</div>'


def both(name, cls=""):
    return inline(name, "dark", cls) + inline(name, "light", cls)


def button(key):
    return (f'<a class="btn" href="{LINKS[key]}" target="_blank" rel="noopener">'
            f'<span class="only-dark">{inline("btn-" + key, "dark", wrap=False)}</span>'
            f'<span class="only-light">{inline("btn-" + key, "light", wrap=False)}</span></a>')


def section(key):
    return both("sh-" + key, "header")


def buttons():
    return "".join(button(k) for k in ("email", "linkedin", "huggingface", "portfolio", "aca"))

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lokesh E — interactive profile</title>
<meta name="description" content="Generative AI Engineer · live GitHub analytics with hover details. Interactive version of github.com/lokeshe09.">
<style>
:root {{ color-scheme: light dark; --bg:#ffffff; --ink:#0f172a; --ink2:#475569; --panel:#f8fafc; --border:rgba(15,23,42,.12); --accent:#16a34a; }}
:root[data-theme="dark"] {{ --bg:#0d1117; --ink:#f1f5f9; --ink2:#a3b0c2; --panel:#0f1522; --border:rgba(255,255,255,.12); --accent:#2ae86d; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0d1117; --ink:#f1f5f9; --ink2:#a3b0c2; --panel:#0f1522; --border:rgba(255,255,255,.12); --accent:#2ae86d; }} }}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; background:var(--bg); color:var(--ink); font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }}
.wrap {{ max-width: 1012px; margin: 0 auto; padding: 24px 16px 64px; }}
.only-dark, .only-light {{ display:none; }}
:root[data-theme="dark"] .only-dark {{ display:block; }}
:root[data-theme="light"] .only-light {{ display:block; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) .only-dark {{ display:block; }} }}
@media (prefers-color-scheme: light) {{ :root:not([data-theme="dark"]) .only-light {{ display:block; }} }}
.btn .only-dark, .btn .only-light {{ display:none; }}
:root[data-theme="dark"] .btn .only-dark {{ display:inline; }}
:root[data-theme="light"] .btn .only-light {{ display:inline; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) .btn .only-dark {{ display:inline; }} }}
@media (prefers-color-scheme: light) {{ :root:not([data-theme="dark"]) .btn .only-light {{ display:inline; }} }}
svg.asset {{ width:100%; height:auto; display:block; }}
.card {{ margin: 12px 0; transition: transform .25s ease, filter .25s ease; }}
.card:not(.header):hover {{ transform: translateY(-3px); filter: drop-shadow(0 18px 30px rgba(0,0,0,.25)); }}
.row {{ display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.row .card {{ margin: 0; }}
@media (max-width: 720px) {{ .row {{ grid-template-columns: 1fr; }} }}
.buttons {{ display:flex; flex-wrap:wrap; justify-content:center; gap: 2px; margin: 4px 0 12px; }}
.btn {{ display:inline-block; line-height:0; transition: transform .18s ease, filter .18s ease; }}
.btn svg {{ height: 62px; width:auto; }}
.btn:hover {{ transform: translateY(-3px); filter: drop-shadow(0 10px 18px rgba(42,232,109,.35)); }}
.btn:active {{ transform: translateY(1px); }}
.hit {{ cursor: pointer; transition: filter .15s ease; }}
.hit:hover {{ filter: brightness(1.35) saturate(1.25) drop-shadow(0 0 6px currentColor); }}
.key:hover {{ filter: brightness(1.15); }}
#tip {{ position: fixed; z-index: 50; pointer-events:none; opacity:0; transform: translate(-50%, calc(-100% - 14px)) scale(.96);
        transition: opacity .12s ease, transform .12s ease; background: var(--panel); color: var(--ink); border: 1px solid var(--border);
        border-radius: 10px; padding: 8px 12px; font: 500 13px/1.35 system-ui, -apple-system, "Segoe UI", sans-serif; white-space: nowrap;
        box-shadow: 0 12px 32px rgba(0,0,0,.28); backdrop-filter: blur(10px); }}
#tip.show {{ opacity:1; transform: translate(-50%, calc(-100% - 14px)) scale(1); }}
#tip::after {{ content:""; position:absolute; left:50%; bottom:-6px; width:10px; height:10px; transform: translateX(-50%) rotate(45deg);
               background: var(--panel); border-right:1px solid var(--border); border-bottom:1px solid var(--border); }}
.topbar {{ display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom: 12px; font-size: 13px; color: var(--ink2); }}
.topbar a {{ color: var(--accent); text-decoration: none; }}
.toggle {{ border:1px solid var(--border); background: var(--panel); color: var(--ink); border-radius: 999px; padding: 6px 14px; cursor:pointer; font: 500 13px system-ui; }}
.hint {{ text-align:center; font-size: 12.5px; color: var(--ink2); margin: 4px 0 14px; }}
.hint b {{ color: var(--accent); font-weight: 600; }}
.foot {{ text-align:center; font-size: 12px; color: var(--ink2); margin-top: 24px; }}
.foot a {{ color: var(--accent); text-decoration:none; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="topbar">
    <span>Interactive version of <a href="https://github.com/lokeshe09" target="_blank" rel="noopener">github.com/lokeshe09</a> · hover anything with data</span>
    <button class="toggle" id="toggle" type="button">Toggle theme</button>
  </div>
  {both("hero", "hero")}
  <div class="buttons">{buttons()}</div>
  {section("about")}
  <div class="row">{both("terminal")}{both("profile")}</div>
  {section("expertise")}
  <div class="row">{both("card-llm")}{both("card-agents")}{both("card-vision")}{both("card-mlops")}</div>
  {section("stack")}
  {both("stack-languages")}{both("stack-ai")}{both("stack-data")}{both("stack-backend")}{both("stack-tools")}
  {section("proficiency")}
  {both("chart-skills")}
  {section("analytics")}
  <p class="hint"><b>Live data</b> — hover any bar, tick, day cell or block for the exact value.</p>
  <div id="contrib3d">{both("contrib3d")}</div>
  <div id="stats">{both("stats")}</div>
  <div id="streak">{both("streak")}</div>
  {section("connect")}
  <div class="buttons">{buttons()}</div>
  {both("footer")}
  <p class="foot">Hand-built in SVG · <a href="https://github.com/lokeshe09/lokeshe09" target="_blank" rel="noopener">source</a></p>
</div>
<div id="tip" role="tooltip"></div>
<script>
(function () {{
  var tip = document.getElementById('tip');
  var cur = null;
  function show(el, x, y) {{
    tip.textContent = el.getAttribute('data-tip');
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
    tip.classList.add('show');
  }}
  document.addEventListener('mousemove', function (e) {{
    var el = e.target.closest ? e.target.closest('[data-tip]') : null;
    if (el) {{ cur = el; show(el, e.clientX, e.clientY); }}
    else if (cur) {{ cur = null; tip.classList.remove('show'); }}
  }});
  document.addEventListener('touchstart', function (e) {{
    var el = e.target.closest ? e.target.closest('[data-tip]') : null;
    if (el) {{ var t = e.touches[0]; show(el, t.clientX, t.clientY); setTimeout(function () {{ tip.classList.remove('show'); }}, 1800); }}
  }}, {{ passive: true }});
  var root = document.documentElement, btn = document.getElementById('toggle');
  try {{ var saved = localStorage.getItem('theme'); if (saved) root.setAttribute('data-theme', saved); }} catch (_) {{}}
  btn.addEventListener('click', function () {{
    var dark = root.getAttribute('data-theme') === 'dark' || (!root.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    var next = dark ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try {{ localStorage.setItem('theme', next); }} catch (_) {{}}
  }});
}})();
</script>
</body>
</html>
'''
with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as fh:
    fh.write(html)
with open(os.path.join(DOCS, ".nojekyll"), "w") as fh:
    fh.write("")
print(f"ok: docs/index.html ({len(html)//1024} KB) · {html.count('data-tip=')} hover targets")
