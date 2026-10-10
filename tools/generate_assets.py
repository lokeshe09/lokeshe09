"""Generate the hand-built SVG design system for the lokeshe09 profile README (v2: glass + 3D).

    python tools/generate_assets.py [fonts-dir] [out-dir]

Every piece of text is converted to vector paths (Inter + JetBrains Mono) so the
rendering is pixel-identical on every OS. Each asset is emitted twice: dark + light.
Shared primitives / theme tokens live in svgkit.py (also used by the live cards).
"""
import os, sys

if len(sys.argv) > 1:
    os.environ["FONT_DIR"] = sys.argv[1]
if len(sys.argv) > 2:
    os.environ["OUT_DIR"] = sys.argv[2]

from svgkit import (BOLD, SEMI, MED, REG, MONO, MONOB, T, THEMES, svg, write, glass_card, glass_tile,
                    iso, iso_prism, shade, dotgrid, DEFAULT_OUT as OUT)

SPLINE = 'calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"'


def bob(dy, dur, begin=0.0):
    """Gentle floating animation for a <g>."""
    return (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {-dy};0 0" '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite" {SPLINE}/>')


def iso_stack(t, ox, oy, size, layers, gap, accent, uid, glow=True):
    """A floating stack of translucent isometric slabs with light pulses running through it."""
    b = []
    if glow:
        b.append(f'<ellipse cx="{ox}" cy="{oy + size*0.55 + 28}" rx="{size*0.95}" ry="{size*0.28}" fill="{accent}" opacity="0.22" filter="url(#{uid}-blur)"/>')
    top = accent
    for i in range(layers):
        z = i * gap
        fill_top = shade(top, 1.0 + 0.12 * i) if THEMES["dark"] is not t else shade(top, 1.0 + 0.1 * i)
        b.append(f'<g>{bob(6 + i * 2, 5.5 + i * 0.6, i * 0.35)}')
        b.append(iso_prism(ox, oy, -size / 2, -size / 2, size, size, 10 + 0 * i, fill_top, shade(fill_top, 0.72), shade(fill_top, 0.55),
                           opacity=0.42 + 0.1 * i, stroke=accent, extra=f' transform="translate(0 {-z})"'))
        b.append("</g>")
    # pulses travelling up the core
    core_top = oy - (layers - 1) * gap - 20
    for k in range(3):
        b.append(f'<circle r="3.5" fill="{t["ink"]}" opacity="0"><animateMotion dur="2.4s" begin="{k*0.8}s" repeatCount="indefinite" path="M{ox} {oy+18} L{ox} {core_top}"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="2.4s" begin="{k*0.8}s" repeatCount="indefinite"/></circle>')
    # orbiting particles with parallax (two rings, different depths)
    for r_x, r_y, dur, rad, op in ((size * 1.25, size * 0.42, 14, 4, 0.9), (size * 1.55, size * 0.55, 20, 3, 0.55)):
        path = f"M{ox - r_x} {oy - 10} a{r_x} {r_y} 0 1 0 {2*r_x} 0 a{r_x} {r_y} 0 1 0 {-2*r_x} 0"
        for k, col in enumerate((t["accent"], t["accent2"], t["accent3"])):
            b.append(f'<circle r="{rad}" fill="{col}" opacity="{op}"><animateMotion dur="{dur}s" begin="{-k*dur/3}s" repeatCount="indefinite" path="{path}"/></circle>')
        b.append(f'<path d="{path}" fill="none" stroke="{t["border2"]}" stroke-width="1" stroke-dasharray="2 6"/>')
    return "".join(b)


# ──────────────────────────────────────────────────────────────────────────────
# 1. HERO
# ──────────────────────────────────────────────────────────────────────────────
def hero(t, theme):
    W, H = 1200, 480
    uid = "hero"
    orbs = [(t["glowA"], 160, 440, 280, 90, -50, 17), (t["glowB"], 1040, 40, 320, -100, 70, 23), (t["glowC"], 620, 520, 220, 70, -60, 19)]
    defs, body = glass_card(t, W, H, 28, orbs=orbs, uid=uid, blur=70)
    name = "Lokesh E"
    name_path = BOLD.path(name, 56, 250, 116, tracking=-0.035)
    defs += (f'<linearGradient id="nameg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["name1"]}"/><stop offset="1" stop-color="{t["name2"]}"/></linearGradient>'
             f'<clipPath id="namec"><path d="{name_path}"/></clipPath>'
             f'<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["g_shine"]}" stop-opacity="0"/><stop offset="0.5" stop-color="{t["g_shine"]}"/><stop offset="1" stop-color="{t["g_shine"]}" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="lineg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/><stop offset="0.5" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}" stop-opacity="0"/>'
             f'<animate attributeName="x1" values="-1;1" dur="6s" repeatCount="indefinite"/><animate attributeName="x2" values="0;2" dur="6s" repeatCount="indefinite"/></linearGradient>')
    b = [body]

    # top bar
    b.append(f'<circle cx="44" cy="44" r="5" fill="{t["accent"]}"/>')
    b.append(T(MONO, "lokeshe09", 60, 49, 14, t["ink2"], tracking=0.02))
    b.append(T(MONO, "/", 152, 49, 14, t["ink3"]))
    b.append(T(MONO, "generative-ai-engineer", 168, 49, 14, t["ink3"], tracking=0.02))
    pill = "AVAILABLE FOR COLLABORATION"
    pw = MONO.width(pill, 12, 0.08) + 52
    px = W - 36 - pw
    b.append(glass_tile(t, px, 30, pw, 30, 15, uid))
    b.append(f'<circle cx="{px+20}" cy="45" r="4" fill="{t["accent"]}"><animate attributeName="opacity" values="1;0.25;1" dur="2s" repeatCount="indefinite"/></circle>')
    b.append(f'<circle cx="{px+20}" cy="45" r="4" fill="none" stroke="{t["accent"]}" stroke-width="1.5"><animate attributeName="r" values="4;10" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.8;0" dur="2s" repeatCount="indefinite"/></circle>')
    b.append(T(MONO, pill, px + 34, 49.5, 12, t["ink2"], tracking=0.08))

    # 3D extruded name
    b.append(T(MONO, "HELLO, I'M", 60, 148, 13, t["accent"], tracking=0.18))
    depth = 9
    for i in range(depth, 0, -1):
        k = 0.55 + 0.45 * (1 - i / depth)
        b.append(f'<path d="{name_path}" fill="{shade(t["g_extrude"], k) if theme == "dark" else t["g_extrude"]}" transform="translate({i*1.1:.1f} {i*1.1:.1f})" opacity="{0.9 if theme == "dark" else 0.85 - 0.05*i:.2f}"/>')
    b.append(f'<path d="{name_path}" fill="url(#nameg)"/>')
    b.append(f'<g clip-path="url(#namec)"><rect x="-300" y="120" width="260" height="160" fill="url(#shine)" transform="skewX(-20)">'
             f'<animate attributeName="x" values="-300;900" dur="5s" begin="1s" repeatCount="indefinite"/></rect></g>')
    b.append(T(SEMI, "Generative AI Engineer", 60, 306, 30, t["ink"], tracking=-0.015))
    b.append(T(MED, "Fine-tuning frontier LLMs & VLMs  ·  RAG systems  ·  Autonomous agents  ·  Deployment at scale", 60, 342, 17, t["ink2"]))

    # chips
    x = 60
    for c in ["LLM / VLM FINE-TUNING", "AGENTIC SYSTEMS", "COMPUTER VISION", "PRODUCTION ML"]:
        cw = MONO.width(c, 11.5, 0.08) + 30
        b.append(glass_tile(t, x, 392, cw, 32, 9, uid))
        b.append(T(MONO, c, x + 15, 412.5, 11.5, t["ink2"], tracking=0.08))
        x += cw + 10

    # 3D scene (right)
    b.append(iso_stack(t, 950, 250, 150, 5, 30, t["accent"], uid))
    b.append(f'<rect x="{W-420}" y="434" width="360" height="2" rx="1" fill="url(#lineg)"/>')
    b.append(T(MONO, "scroll ↓", W - 60, 422, 11.5, t["ink3"], anchor="end", tracking=0.06))
    write("hero", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
# 2. SECTION HEADERS
# ──────────────────────────────────────────────────────────────────────────────
SECTIONS = [
    ("about", "01", "About me", "WHO I AM"),
    ("expertise", "02", "Core expertise", "WHAT I DO"),
    ("stack", "03", "Tech stack", "WHAT I BUILD WITH"),
    ("proficiency", "04", "Skill proficiency", "HOW DEEP IT GOES"),
    ("analytics", "05", "GitHub analytics", "WHAT I SHIP"),
    ("connect", "06", "Let's build something", "SAY HELLO"),
]


def section(t, theme, key, idx, title, caption):
    W, H = 1200, 84
    defs = (f'<linearGradient id="hl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="0.6"/><stop offset="0.35" stop-color="{t["border2"]}"/><stop offset="1" stop-color="{t["border2"]}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="tg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="0.25"/><stop offset="1" stop-color="{t["accent2"]}" stop-opacity="0.08"/></linearGradient>')
    b = []
    # index tile (3D-ish: stacked offset copies)
    for i in (2, 1):
        b.append(f'<rect x="{i*2}" y="{24+i*2}" width="40" height="40" rx="11" fill="{t["accent"]}" opacity="{0.18 - 0.06*i:.2f}"/>')
    b.append(f'<rect x="0.5" y="24.5" width="39" height="39" rx="11" fill="url(#tg)" stroke="{t["border2"]}"/>')
    b.append(T(MONOB, idx, 20, 50, 14, t["accent"], anchor="middle", tracking=0.06))
    tw = SEMI.width(title, 34, -0.02)
    b.append(T(SEMI, title, 58, 57, 34, t["ink"], tracking=-0.02))
    b.append(f'<rect x="{58+tw+24:.0f}" y="46" width="{W-(58+tw+24)-230:.0f}" height="2" rx="1" fill="url(#hl)"/>')
    b.append(T(MONO, caption, W, 51, 12, t["ink3"], anchor="end", tracking=0.16))
    write(f"sh-{key}", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
# 3. PROFILE CARD
# ──────────────────────────────────────────────────────────────────────────────
def profile_card(t, theme):
    W, H = 560, 352
    uid = "pf"
    defs, body = glass_card(t, W, H, 20, uid=uid, orbs=[(t["glowA"], 520, 40, 170, -30, 30, 15), (t["glowB"], 40, 340, 160, 40, -30, 19)], intensity=0.45)
    defs += f'<linearGradient id="mg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>'
    b = [body]
    b.append(f'<circle cx="56" cy="56" r="30" fill="{t["accent"]}" opacity="0.25" filter="url(#{uid}-blur)"/>')
    b.append(f'<circle cx="56" cy="56" r="26" fill="url(#mg)"/>')
    b.append(f'<circle cx="56" cy="56" r="26" fill="none" stroke="{t["g_hi"]}" stroke-opacity="0.5"/>')
    b.append(T(BOLD, "LE", 56, 64, 20, t["btnText"], anchor="middle", tracking=-0.02))
    b.append(T(SEMI, "Lokesh E", 96, 52, 19, t["ink"], tracking=-0.01))
    b.append(T(MONO, "@lokeshe09", 96, 72, 12.5, t["ink3"]))
    cw = MONO.width("GEN-AI", 11, 0.1) + 24
    b.append(glass_tile(t, W - 30 - cw, 42, cw, 26, 7, uid))
    b.append(T(MONO, "GEN-AI", W - 30 - cw / 2, 59, 11, t["accent"], anchor="middle", tracking=0.1))
    b.append(f'<rect x="30" y="100" width="{W-60}" height="1" fill="{t["grid"]}"/>')
    rows = [("ROLE", "Generative AI Engineer"), ("FOCUS", "LLM / VLM fine-tuning · RAG · Agents"),
            ("STACK", "PyTorch · Hugging Face · LangChain · TF"), ("LEARNING", "Advanced quantization · MoE at scale"),
            ("ASK ME", "LLMs · RAG · Agents · CV · NLP")]
    y = 136
    for k, v in rows:
        b.append(T(MONO, k, 30, y, 11.5, t["ink3"], tracking=0.12))
        b.append(T(MED, v, 140, y + 1, 15.5, t["ink"]))
        y += 38
    b.append(f'<rect x="30" y="{y-14}" width="{W-60}" height="1" fill="{t["grid"]}"/>')
    b.append(f'<circle cx="38" cy="{y+16}" r="4" fill="{t["accent"]}"><animate attributeName="opacity" values="1;0.3;1" dur="2.2s" repeatCount="indefinite"/></circle>')
    b.append(T(MED, "Open to open-source collabs on fine-tuning & quantization", 52, y + 21, 13.5, t["ink2"]))
    write("profile", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
# 4. TERMINAL CARD
# ──────────────────────────────────────────────────────────────────────────────
CODE = [
    [("# about.py — who I am, as code", "c")],
    [("class ", "k"), ("LokeshE", "n"), (":", "p")],
    [("    role     ", "p"), ("= ", "o"), ('"Generative AI Engineer"', "s")],
    [("    focus    ", "p"), ("= ", "o"), ("[", "p"), ('"LLM/VLM fine-tuning"', "s"), (", ", "p"), ('"RAG"', "s"), (", ", "p"), ('"Agents"', "s"), ("]", "p")],
    [("    stack    ", "p"), ("= ", "o"), ("[", "p"), ('"PyTorch"', "s"), (", ", "p"), ('"Hugging Face"', "s"), (", ", "p"), ('"LangChain"', "s"), ("]", "p")],
    [("    learning ", "p"), ("= ", "o"), ("[", "p"), ('"Quantization"', "s"), (", ", "p"), ('"MoE at scale"', "s"), ("]", "p")],
    [],
    [("    def ", "k"), ("ship", "f"), ("(self, paper):", "p")],
    [("        return ", "k"), ("self.read(paper).prototype().deploy()", "p")],
]


def terminal(t, theme):
    W, H = 560, 352
    uid = "tm"
    defs, body = glass_card(t, W, H, 20, uid=uid, orbs=[(t["glowB"], 60, 60, 160, 40, 30, 17), (t["glowA"], 520, 340, 150, -30, -30, 14)], grid=False, intensity=0.4)
    role = {"c": t["ink3"], "k": t["accent3"], "n": t["accent4"], "s": t["accent"], "f": t["accent2"], "p": t["ink"], "o": t["ink2"]}
    b = [body]
    b.append(f'<path d="M0.5 44H{W-0.5}" stroke="{t["grid"]}"/>')
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        b.append(f'<circle cx="{26+i*18}" cy="22" r="5" fill="{c}" opacity="0.9"/>')
    b.append(T(MONO, "lokesh@ai ~ about.py", W / 2, 26.5, 12, t["ink3"], anchor="middle", tracking=0.02))
    size, lh, x0, y = 13, 22, 24, 78
    adv = MONO.width("M", size)
    for i, line in enumerate(CODE):
        b.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.25s" begin="{0.3+0.16*i:.2f}s" fill="freeze"/>')
        b.append(T(MONO, f"{i+1:>2}", x0, y, 11, t["ink3"], opacity=0.7))
        x = x0 + 30
        for text, r in line:
            b.append(T(MONO, text, x, y, size, role[r]))
            x += adv * len(text)
        if i == len(CODE) - 1:
            b.append(f'<rect x="{x+4:.1f}" y="{y-12}" width="7" height="15" rx="1" fill="{t["accent"]}"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>')
        b.append("</g>")
        y += lh
    b.append(f'<path d="M0.5 {H-34}H{W-0.5}" stroke="{t["grid"]}"/>')
    b.append(f'<circle cx="28" cy="{H-17}" r="3.5" fill="{t["accent"]}"/>')
    b.append(T(MONO, "python 3.12", 40, H - 13, 11, t["ink3"], tracking=0.04))
    b.append(T(MONO, "UTF-8  ·  LF  ·  Ln 9, Col 52", W - 24, H - 13, 11, t["ink3"], anchor="end", tracking=0.04))
    write("terminal", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
# 5. EXPERTISE CARDS
# ──────────────────────────────────────────────────────────────────────────────
def icon_chip(c):
    return (f'<g fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<rect x="-9" y="-9" width="18" height="18" rx="4"/><rect x="-4" y="-4" width="8" height="8" rx="1.5"/>'
            '<path d="M-3 -14v5M3 -14v5M-3 9v5M3 9v5M-14 -3h5M-14 3h5M9 -3h5M9 3h5"/></g>')


def icon_nodes(c):
    return (f'<g fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round"><path d="M-9 7L0 -8L9 7Z"/>'
            f'<circle cx="-9" cy="7" r="3.5" fill="{c}" stroke="none"/><circle cx="9" cy="7" r="3.5" fill="{c}" stroke="none"/><circle cx="0" cy="-8" r="3.5" fill="{c}" stroke="none"/></g>')


def icon_eye(c):
    return (f'<g fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round"><path d="M-14 0C-9 -8 -4 -11 0 -11S9 -8 14 0C9 8 4 11 0 11S-9 8 -14 0Z"/>'
            f'<circle cx="0" cy="0" r="4.5" fill="{c}" stroke="none"/></g>')


def icon_rocket(c):
    return (f'<g fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M0 -14C5 -10 7 -3 7 4L0 9L-7 4C-7 -3 -5 -10 0 -14Z"/>'
            f'<circle cx="0" cy="-2" r="2.5" fill="{c}" stroke="none"/><path d="M-7 2L-12 7L-8 8M7 2L12 7L8 8M-2 10L0 15L2 10"/></g>')


CARDS = [
    ("llm", "LLM Engineering", "accent", icon_chip,
     ["Supervised & instruction fine-tuning", "LoRA / QLoRA parameter-efficient tuning", "Retrieval-augmented generation pipelines", "Quantization for cheaper inference"],
     ["TRANSFORMERS", "PEFT", "RAG"]),
    ("agents", "Agentic Systems", "accent3", icon_nodes,
     ["Autonomous multi-step agents", "Tool-use & function orchestration", "Planning, memory & self-correction", "Papers → working prototypes, fast"],
     ["LANGCHAIN", "TOOL-USE", "EVALS"]),
    ("vision", "Computer Vision", "accent2", icon_eye,
     ["Image classification at scale", "Action & event detection", "Deep CNN / EfficientNet pipelines", "Vision-language model fine-tuning"],
     ["OPENCV", "EFFICIENTNET", "VLMs"]),
    ("mlops", "MLOps & Deployment", "accent4", icon_rocket,
     ["High-throughput model serving", "Cross-GPU validation & benchmarking", "Scalable inference infrastructure", "CI/CD for machine-learning systems"],
     ["GCP", "NGINX", "GUNICORN"]),
]


def expertise_card(t, theme, key, title, acc, icon, bullets, tags, idx):
    W, H = 580, 262
    uid = f"cd{idx}"
    c = t[acc]
    defs, body = glass_card(t, W, H, 20, uid=uid, orbs=[(c, 540, 30, 150, -30, 30, 14), (t["glowB"], 60, 260, 150, 40, -30, 18)], intensity=0.55)
    b = [body]
    b.append(f'<path d="M20 1H{W-20}" stroke="{c}" stroke-width="2" opacity="0.9"/>')
    b.append(glass_tile(t, 28, 28, 48, 48, 12, uid))
    b.append(f'<g transform="translate(52 52)">{icon(c)}</g>')
    b.append(T(SEMI, title, 92, 50, 22, t["ink"], tracking=-0.015))
    b.append(T(MONO, f"0{idx+1} / CAPABILITY", 92, 71, 11, t["ink3"], tracking=0.12))
    y = 116
    for line in bullets:
        b.append(f'<circle cx="34" cy="{y-5}" r="3" fill="{c}"/>')
        b.append(T(MED, line, 48, y, 15, t["ink2"]))
        y += 28
    x = 28
    for tag in tags:
        tw = MONO.width(tag, 10.5, 0.1) + 22
        b.append(glass_tile(t, x, H - 50, tw, 24, 6, uid))
        b.append(T(MONO, tag, x + 11, H - 34, 10.5, t["ink3"], tracking=0.1))
        x += tw + 8
    # floating 3D cube cluster (decorative) bottom-right
    ox, oy = W - 84, H - 86
    for (gx, gy, gz, k, dly) in ((0, 0, 0, 1.0, 0.0), (18, 0, 0, 0.9, 0.4), (0, 18, 0, 0.8, 0.8), (9, 9, 16, 1.15, 1.2)):
        col = shade(c, k)
        b.append(f'<g>{bob(5, 4.5, dly)}' + iso_prism(ox, oy - gz, gx, gy, 16, 16, 14, col, shade(col, 0.75), shade(col, 0.55), opacity=0.9, stroke=t["g_hi"]) + "</g>")
    write(f"card-{key}", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
# 6. PROFICIENCY CHART (dataviz: single series, sequential hue, thin marks)
# ──────────────────────────────────────────────────────────────────────────────
SKILLS = [("Python", 95), ("PyTorch / TensorFlow", 90), ("LLM fine-tuning & RAG", 90),
          ("Computer vision", 85), ("Quantization & deployment", 80), ("SQL / databases", 75)]


def chart(t, theme):
    W, H = 1200, 448
    uid = "ch"
    pad_l, pad_r, label_w = 40, 40, 300
    x0, x1 = pad_l + label_w, W - pad_r - 70
    top, row_h, bar_h = 128, 44, 14
    defs, body = glass_card(t, W, H, 20, uid=uid, intensity=0.35)
    b = [body]
    b.append(T(SEMI, "Depth across core domains", 40, 56, 22, t["ink"], tracking=-0.015))
    b.append(T(REG, "Self-assessed on a single 0–100 scale · updated 2026", 40, 80, 14, t["ink2"]))
    for pct in (0, 25, 50, 75, 100):
        x = x0 + (x1 - x0) * pct / 100
        b.append(f'<rect x="{x:.1f}" y="{top-14}" width="1" height="{row_h*len(SKILLS)+6}" fill="{t["grid"]}"/>')
        b.append(T(MONO, str(pct), x, top - 22, 11, t["ink3"], anchor="middle"))
    b.append(f'<rect x="{x0}" y="{top-14}" width="1.5" height="{row_h*len(SKILLS)+6}" fill="{t["border2"]}"/>')
    for i, (name, val) in enumerate(SKILLS):
        y = top + i * row_h
        cy = y + bar_h / 2
        w = (x1 - x0) * val / 100
        b.append(T(MED, name, x0 - 22, cy + 5.5, 15, t["ink"], anchor="end"))
        b.append(f'<rect x="{x0}" y="{y}" width="{x1-x0:.1f}" height="{bar_h}" rx="4" fill="{t["track"]}"/>')
        defs += f'<clipPath id="c{i}"><rect x="{x0}" y="{y-2}" width="0" height="{bar_h+4}"><animate attributeName="width" from="0" to="{w+4:.1f}" dur="1.1s" begin="{0.15+i*0.12:.2f}s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1"/></rect></clipPath>'
        b.append(f'<path d="M{x0} {y}H{x0+w-4:.1f}a4 4 0 0 1 4 4v{bar_h-8}a4 4 0 0 1 -4 4H{x0}Z" fill="{t["bar"]}" clip-path="url(#c{i})"/>')
        b.append(f'<path d="{SEMI.path(f"{val}%", x0 + w + 14, cy + 5.5, 14)}" fill="{t["ink"]}" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{0.9+i*0.12:.2f}s" fill="freeze"/></path>')
    b.append(f'<rect x="40" y="{H-54}" width="{W-80}" height="1" fill="{t["grid"]}"/>')
    b.append(f'<rect x="40" y="{H-34}" width="14" height="6" rx="2" fill="{t["bar"]}"/>')
    b.append(T(REG, "Depth, self-assessed", 62, H - 27, 12.5, t["ink2"]))
    b.append(f'<rect x="196" y="{H-34}" width="14" height="6" rx="2" fill="{t["track"]}" stroke="{t["border"]}"/>')
    b.append(T(REG, "Remaining headroom", 218, H - 27, 12.5, t["ink2"]))
    b.append(T(MONO, "n = 6 domains", W - 40, H - 27, 11.5, t["ink3"], anchor="end", tracking=0.04))
    write("chart-skills", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
# 7. STACK LABELS + CHIP STRIPS
# ──────────────────────────────────────────────────────────────────────────────
STACK_LABELS = [("languages", "LANGUAGES"), ("ai", "AI · ML · DL"), ("data", "DATA & NUMERICAL"), ("backend", "BACKEND · CLOUD · DEVOPS"), ("tools", "TOOLS")]


def stack_label(t, theme, key, text):
    W, H = 1200, 34
    tw = MONO.width(text, 12, 0.16)
    b = [f'<rect x="0" y="16.5" width="{(W-tw)/2-22:.0f}" height="1" fill="{t["grid"]}"/>',
         f'<rect x="{(W+tw)/2+22:.0f}" y="16.5" width="{(W-tw)/2-22:.0f}" height="1" fill="{t["grid"]}"/>',
         T(MONO, text, W / 2, 21.5, 12, t["ink3"], anchor="middle", tracking=0.16)]
    write(f"lbl-{key}", theme, svg(W, H, "".join(b)))


CHIPS = {
    "ai": [("Hugging Face", "#FFD21E"), ("Transformers", "#FF9D00"), ("PEFT / LoRA", "#2AE86D"), ("LangChain", "#1C3C3C"), ("Keras", "#D00000")],
    "data": [("NumPy", "#4DABCF"), ("Pandas", "#8A4FFF"), ("SciPy", "#0C55A5"), ("Matplotlib", "#11557C")],
    "backend": [("Gunicorn", "#499848"), ("REST APIs", "#60A5FA"), ("CI / CD", "#FBBF24")],
}


def chips(t, theme, key, items):
    W, H = 1200, 44
    size, pad, gapx = 13, 14, 10
    widths = [MED.width(n, size) + pad * 2 + 18 for n, _ in items]
    x = (W - (sum(widths) + gapx * (len(items) - 1))) / 2
    defs = (f'<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["g_edgeHi"]}"/><stop offset="0.5" stop-color="{t["g_edgeLo"]}"/><stop offset="1" stop-color="{t["g_edgeHi"]}"/></linearGradient>')
    b = []
    for (name, col), w in zip(items, widths):
        bright = col.upper() in ("#FFD21E", "#2AE86D", "#FBBF24")
        dot = col if theme == "dark" or not bright else (t["accent4"] if col.upper() != "#2AE86D" else t["accent"])
        b.append(f'<rect x="{x:.1f}" y="6" width="{w:.1f}" height="32" rx="9" fill="{t["chipbg"]}" stroke="url(#bd)"/>')
        b.append(f'<circle cx="{x+pad+4:.1f}" cy="22" r="4" fill="{dot}"/>')
        b.append(T(MED, name, x + pad + 18, 26.5, size, t["ink"]))
        x += w + gapx
    write(f"chips-{key}", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
# 8. BUTTONS + FOOTER
# ──────────────────────────────────────────────────────────────────────────────
BUTTONS = [("email", "Email me", True), ("linkedin", "LinkedIn", False), ("huggingface", "Hugging Face", False),
           ("portfolio", "Portfolio", False), ("aca", "AI Craft Alchemy", False)]


def button(t, theme, key, label, primary):
    pad, m = 22, 8                     # m = margin so the glow isn't clipped
    tw = SEMI.width(label, 15)
    bw, bh = int(tw + pad * 2 + 26), 50
    W, H = bw + 2 * m, bh + 2 * m
    defs = (f'<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["g_edgeHi"]}"/><stop offset="0.5" stop-color="{t["g_edgeLo"]}"/><stop offset="1" stop-color="{t["g_edgeHi"]}"/></linearGradient>'
            f'<linearGradient id="pg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{shade(t["accent"], 0.82)}"/></linearGradient>'
            f'<filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="6"/></filter>'
            f'<linearGradient id="hl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["g_hi"]}" stop-opacity="0"/><stop offset="0.5" stop-color="{t["g_hi"]}"/><stop offset="1" stop-color="{t["g_hi"]}" stop-opacity="0"/></linearGradient>')
    b = []
    if primary:
        b.append(f'<rect x="{m+4}" y="{m+8}" width="{bw-8}" height="{bh-8}" rx="12" fill="{t["accent"]}" opacity="0.55" filter="url(#glow)"/>')
        b.append(f'<rect x="{m+0.5}" y="{m+0.5}" width="{bw-1}" height="{bh-1}" rx="12" fill="url(#pg)"/>')
        fg = t["btnText"]
    else:
        b.append(f'<rect x="{m+0.5}" y="{m+0.5}" width="{bw-1}" height="{bh-1}" rx="12" fill="{t["chipbg"]}" stroke="url(#bd)"/>')
        fg = t["ink"]
    b.append(f'<rect x="{m+12}" y="{m+1}" width="{bw-24}" height="1" fill="url(#hl)" opacity="0.8"/>')
    b.append(T(SEMI, label, m + pad, m + 31, 15, fg, tracking=-0.005))
    b.append(f'<path d="M{m+bw-pad-12} {m+31}l12-12M{m+bw-pad-10} {m+19}h10v10" fill="none" stroke="{fg}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    write(f"btn-{key}", theme, svg(W, H, "".join(b), defs))


def footer(t, theme):
    W, H = 1200, 132
    uid = "ft"
    defs, body = glass_card(t, W, H, 24, uid=uid, orbs=[(t["glowA"], 100, 130, 180, 60, -20, 16), (t["glowB"], 1100, 0, 220, -60, 30, 20)], intensity=0.6)
    b = [body]
    b.append(T(SEMI, "Lokesh E", 40, 62, 18, t["ink"], tracking=-0.01))
    b.append(T(REG, "Generative AI Engineer · Building systems at the edge of what's possible", 40, 86, 13.5, t["ink2"]))
    b.append(T(MONO, "DESIGNED & HAND-BUILT IN SVG", W - 40, 60, 11, t["ink3"], anchor="end", tracking=0.16))
    b.append(T(MONO, "© 2026 · MADE WITH CARE AND TOO MUCH COFFEE", W - 40, 84, 11, t["ink3"], anchor="end", tracking=0.1))
    # tiny floating cubes
    for i, (gx, gz) in enumerate(((0, 0), (22, 10), (44, 0))):
        col = (t["accent"], t["accent2"], t["accent3"])[i]
        b.append(f'<g>{bob(4, 4 + i, i * 0.5)}' + iso_prism(W / 2 - 20 + gx, 70 - gz, 0, 0, 14, 14, 12, col, shade(col, 0.75), shade(col, 0.55), opacity=0.9) + "</g>")
    write("footer", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
for theme, t in THEMES.items():
    hero(t, theme)
    for key, idx, title, cap in SECTIONS:
        section(t, theme, key, idx, title, cap)
    profile_card(t, theme)
    terminal(t, theme)
    for i, (key, title, acc, icon, bullets, tags) in enumerate(CARDS):
        expertise_card(t, theme, key, title, acc, icon, bullets, tags, i)
    chart(t, theme)
    for key, text in STACK_LABELS:
        stack_label(t, theme, key, text)
    for key, items in CHIPS.items():
        chips(t, theme, key, items)
    for key, label, primary in BUTTONS:
        button(t, theme, key, label, primary)
    footer(t, theme)

print("ok:", len([f for f in os.listdir(OUT) if f.endswith(".svg")]), "files in", OUT)
