"""Generate the hand-built SVG design system for the lokeshe09 profile README.

    python tools/generate_assets.py [fonts-dir] [out-dir]

Every piece of text is converted to vector paths (Inter + JetBrains Mono) so the
rendering is pixel-identical on every OS. Each asset is emitted twice: dark + light.
Shared primitives / theme tokens live in svgkit.py (also used by streak.py).
"""
import os, sys

if len(sys.argv) > 1:
    os.environ["FONT_DIR"] = sys.argv[1]
if len(sys.argv) > 2:
    os.environ["OUT_DIR"] = sys.argv[2]

from svgkit import BOLD, SEMI, MED, REG, MONO, MONOB, T, THEMES, svg, write, card, dotgrid, DEFAULT_OUT as OUT

# ──────────────────────────────────────────────────────────────────────────────
# 1. HERO
# ──────────────────────────────────────────────────────────────────────────────
def hero(t, theme):
    W, H = 1200, 420
    defs = dotgrid(t)
    defs += f'<clipPath id="clip"><rect x="0" y="0" width="{W}" height="{H}" rx="28"/></clipPath>'
    defs += '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>'
    defs += (f'<linearGradient id="nameg" x1="0" y1="0" x2="1" y2="1">'
             f'<stop offset="0" stop-color="{t["name1"]}"/><stop offset="1" stop-color="{t["name2"]}"/></linearGradient>')
    defs += (f'<linearGradient id="lineg" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/>'
             f'<stop offset="0.5" stop-color="{t["accent"]}"/>'
             f'<stop offset="1" stop-color="{t["accent2"]}" stop-opacity="0"/>'
             f'<animate attributeName="x1" values="-1;1" dur="6s" repeatCount="indefinite"/>'
             f'<animate attributeName="x2" values="0;2" dur="6s" repeatCount="indefinite"/>'
             f'</linearGradient>')
    defs += (f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{t["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{t["bg"]}" stop-opacity="0.9"/></linearGradient>')

    b = []
    b.append(f'<rect width="{W}" height="{H}" rx="28" fill="{t["bg"]}"/>')
    # glow orbs (clipped), slowly drifting
    orbs = [
        (t["glowA"], 230, 300, 180, "-40;60;-40", "0;-30;0", "18s"),
        (t["glowB"], 980, 120, 220, "40;-60;40", "0;40;0", "22s"),
        (t["glowC"], 700, 420, 160, "-30;40;-30", "0;-40;0", "16s"),
    ]
    b.append('<g clip-path="url(#clip)">')
    for col, cx, cy, r, ax, ay, dur in orbs:
        b.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}" opacity="{t["glowOp"]}" filter="url(#blur)">'
            f'<animate attributeName="cx" values="{cx+int(ax.split(";")[0])};{cx+int(ax.split(";")[1])};{cx+int(ax.split(";")[2])}" dur="{dur}" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>'
            f'<animate attributeName="cy" values="{cy+int(ay.split(";")[0])};{cy+int(ay.split(";")[1])};{cy+int(ay.split(";")[2])}" dur="{dur}" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>'
            f'</circle>'
        )
    b.append(f'<rect width="{W}" height="{H}" fill="url(#dg)"/>')
    b.append(f'<rect width="{W}" height="{H}" fill="url(#fade)" opacity="0.6"/>')
    b.append("</g>")
    b.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="28" fill="none" stroke="{t["border2"]}"/>')

    # top bar: handle + status pill
    b.append(f'<circle cx="44" cy="44" r="5" fill="{t["accent"]}"/>')
    b.append(T(MONO, "lokeshe09", 60, 49, 14, t["ink2"], tracking=0.02))
    b.append(T(MONO, "/", 152, 49, 14, t["ink3"]))
    b.append(T(MONO, "generative-ai-engineer", 168, 49, 14, t["ink3"], tracking=0.02))

    pill_txt = "AVAILABLE FOR COLLABORATION"
    pw = MONO.width(pill_txt, 12, 0.08) + 52
    px = W - 36 - pw
    b.append(f'<rect x="{px}" y="30" width="{pw:.0f}" height="30" rx="15" fill="{t["chipbg"]}" stroke="{t["border"]}"/>')
    b.append(f'<circle cx="{px+20}" cy="45" r="4" fill="{t["accent"]}"><animate attributeName="opacity" values="1;0.25;1" dur="2s" repeatCount="indefinite"/></circle>')
    b.append(f'<circle cx="{px+20}" cy="45" r="4" fill="none" stroke="{t["accent"]}" stroke-width="1.5"><animate attributeName="r" values="4;10" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.8;0" dur="2s" repeatCount="indefinite"/></circle>')
    b.append(T(MONO, pill_txt, px + 34, 49.5, 12, t["ink2"], tracking=0.08))

    # headline block
    b.append(T(MONO, "HELLO, I'M", 60, 138, 13, t["accent"], tracking=0.18))
    b.append(f'<path d="{BOLD.path("Lokesh E", 56, 228, 112, tracking=-0.035)}" fill="url(#nameg)"/>')
    b.append(T(SEMI, "Generative AI Engineer", 60, 282, 30, t["ink"], tracking=-0.015))
    b.append(T(MED, "Fine-tuning frontier LLMs & VLMs  ·  RAG systems  ·  Autonomous agents  ·  Deployment at scale", 60, 318, 17, t["ink2"]))

    # bottom chips
    chips = ["LLM / VLM FINE-TUNING", "AGENTIC SYSTEMS", "COMPUTER VISION", "PRODUCTION ML"]
    x = 60
    for c in chips:
        cw = MONO.width(c, 11.5, 0.08) + 30
        b.append(f'<rect x="{x}" y="350" width="{cw:.0f}" height="30" rx="8" fill="{t["chipbg"]}" stroke="{t["border"]}"/>')
        b.append(T(MONO, c, x + 15, 369.5, 11.5, t["ink2"], tracking=0.08))
        x += cw + 10

    # animated signal line at bottom right
    b.append(f'<rect x="{W-420}" y="364" width="360" height="2" rx="1" fill="url(#lineg)"/>')
    b.append(T(MONO, "scroll ↓", W - 60, 352, 11.5, t["ink3"], anchor="end", tracking=0.06))
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
    defs = (f'<linearGradient id="hl" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{t["border2"]}"/><stop offset="1" stop-color="{t["border2"]}" stop-opacity="0"/></linearGradient>')
    b = []
    b.append(T(MONOB, idx, 0, 54, 15, t["accent"], tracking=0.1))
    b.append(f'<rect x="34" y="47" width="22" height="2" rx="1" fill="{t["accent"]}"/>')
    tw = SEMI.width(title, 34, -0.02)
    b.append(T(SEMI, title, 70, 58, 34, t["ink"], tracking=-0.02))
    b.append(f'<rect x="{70+tw+26:.0f}" y="47" width="{W-(70+tw+26)-230:.0f}" height="1" fill="url(#hl)"/>')
    b.append(T(MONO, caption, W, 52, 12, t["ink3"], anchor="end", tracking=0.16))
    write(f"sh-{key}", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
# 3. PROFILE CARD (right side of About)
# ──────────────────────────────────────────────────────────────────────────────
def profile_card(t, theme):
    W, H = 560, 352
    defs = (f'<linearGradient id="mg" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>')
    b = [card(t, W, H, 20)]
    # monogram
    b.append('<circle cx="56" cy="56" r="26" fill="url(#mg)"/>')
    b.append(T(BOLD, "LE", 56, 64, 20, t["btnText"], anchor="middle", tracking=-0.02))
    b.append(T(SEMI, "Lokesh E", 96, 52, 19, t["ink"], tracking=-0.01))
    b.append(T(MONO, "@lokeshe09", 96, 72, 12.5, t["ink3"]))
    # verified-ish chip
    cw = MONO.width("GEN-AI", 11, 0.1) + 24
    b.append(f'<rect x="{W-30-cw:.0f}" y="42" width="{cw:.0f}" height="26" rx="7" fill="{t["iconTint"]}"/>')
    b.append(T(MONO, "GEN-AI", W - 30 - cw / 2, 59, 11, t["accent"], anchor="middle", tracking=0.1))
    b.append(f'<rect x="30" y="100" width="{W-60}" height="1" fill="{t["grid"]}"/>')

    rows = [
        ("ROLE", "Generative AI Engineer"),
        ("FOCUS", "LLM / VLM fine-tuning · RAG · Agents"),
        ("STACK", "PyTorch · Hugging Face · LangChain · TF"),
        ("LEARNING", "Advanced quantization · MoE at scale"),
        ("ASK ME", "LLMs · RAG · Agents · CV · NLP"),
    ]
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
# 4. EXPERTISE CARDS
# ──────────────────────────────────────────────────────────────────────────────
def icon_chip(c):
    return (f'<g fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<rect x="-9" y="-9" width="18" height="18" rx="4"/><rect x="-4" y="-4" width="8" height="8" rx="1.5"/>'
            '<path d="M-3 -14v5M3 -14v5M-3 9v5M3 9v5M-14 -3h5M-14 3h5M9 -3h5M9 3h5"/></g>')


def icon_nodes(c):
    return (f'<g fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round">'
            '<path d="M-9 7L0 -8L9 7Z"/><circle cx="-9" cy="7" r="3.5" fill="{c}" stroke="none"/>'
            f'<circle cx="9" cy="7" r="3.5" fill="{c}" stroke="none"/><circle cx="0" cy="-8" r="3.5" fill="{c}" stroke="none"/></g>').replace("{c}", c)


def icon_eye(c):
    return (f'<g fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round">'
            '<path d="M-14 0C-9 -8 -4 -11 0 -11S9 -8 14 0C9 8 4 11 0 11S-9 8 -14 0Z"/>'
            f'<circle cx="0" cy="0" r="4.5" fill="{c}" stroke="none"/></g>')


def icon_rocket(c):
    return (f'<g fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M0 -14C5 -10 7 -3 7 4L0 9L-7 4C-7 -3 -5 -10 0 -14Z"/>'
            f'<circle cx="0" cy="-2" r="2.5" fill="{c}" stroke="none"/>'
            '<path d="M-7 2L-12 7L-8 8M7 2L12 7L8 8M-2 10L0 15L2 10"/></g>')


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


def expertise_card(t, theme, key, title, acc, icon, bullets, tags):
    W, H = 580, 262
    c = t[acc]
    b = [card(t, W, H, 20)]
    # accent top edge
    b.append(f'<path d="M20 0.5H{W-20}" stroke="{c}" stroke-width="2" opacity="0.9"/>')
    b.append(f'<rect x="28" y="28" width="48" height="48" rx="12" fill="{c}" opacity="0.12"/>')
    b.append(f'<g transform="translate(52 52)">{icon(c)}</g>')
    b.append(T(SEMI, title, 92, 50, 22, t["ink"], tracking=-0.015))
    b.append(T(MONO, "0{} / {}".format(CARDS.index(next(x for x in CARDS if x[0] == key)) + 1, "CAPABILITY"), 92, 71, 11, t["ink3"], tracking=0.12))
    y = 116
    for line in bullets:
        b.append(f'<circle cx="34" cy="{y-5}" r="3" fill="{c}"/>')
        b.append(T(MED, line, 48, y, 15, t["ink2"]))
        y += 28
    x = 28
    for tag in tags:
        tw = MONO.width(tag, 10.5, 0.1) + 22
        b.append(f'<rect x="{x}" y="{H-50}" width="{tw:.0f}" height="24" rx="6" fill="{t["chipbg"]}" stroke="{t["border"]}"/>')
        b.append(T(MONO, tag, x + 11, H - 34, 10.5, t["ink3"], tracking=0.1))
        x += tw + 8
    write(f"card-{key}", theme, svg(W, H, "".join(b)))


# ──────────────────────────────────────────────────────────────────────────────
# 5. PROFICIENCY CHART  (dataviz: single series, sequential hue, thin marks)
# ──────────────────────────────────────────────────────────────────────────────
SKILLS = [
    ("Python", 95),
    ("PyTorch / TensorFlow", 90),
    ("LLM fine-tuning & RAG", 90),
    ("Computer vision", 85),
    ("Quantization & deployment", 80),
    ("SQL / databases", 75),
]


def chart(t, theme):
    W, H = 1200, 448
    pad_l, pad_r = 40, 40
    label_w = 300
    x0 = pad_l + label_w            # bar baseline x
    x1 = W - pad_r - 70             # bar max x (room for tip label)
    top = 128
    row_h = 44
    bar_h = 14
    defs = ""
    b = [card(t, W, H, 20)]
    b.append(T(SEMI, "Depth across core domains", 40, 56, 22, t["ink"], tracking=-0.015))
    b.append(T(REG, "Self-assessed on a single 0–100 scale · updated 2026", 40, 80, 14, t["ink2"]))
    # ticks + hairline grid (solid, recessive)
    for pct in (0, 25, 50, 75, 100):
        x = x0 + (x1 - x0) * pct / 100
        b.append(f'<rect x="{x:.1f}" y="{top-14}" width="1" height="{row_h*len(SKILLS)+6}" fill="{t["grid"]}"/>')
        b.append(T(MONO, str(pct), x, top - 22, 11, t["ink3"], anchor="middle"))
    # baseline (slightly stronger)
    b.append(f'<rect x="{x0}" y="{top-14}" width="1.5" height="{row_h*len(SKILLS)+6}" fill="{t["border2"]}"/>')
    for i, (name, val) in enumerate(SKILLS):
        y = top + i * row_h
        cy = y + bar_h / 2
        w = (x1 - x0) * val / 100
        b.append(T(MED, name, x0 - 22, cy + 5.5, 15, t["ink"], anchor="end"))
        # track: lighter step of the same ramp
        b.append(f'<rect x="{x0}" y="{y}" width="{x1-x0:.1f}" height="{bar_h}" rx="4" fill="{t["track"]}"/>')
        # bar: square at baseline, 4px rounded data-end; revealed by animated clip
        defs += f'<clipPath id="c{i}"><rect x="{x0}" y="{y-2}" width="0" height="{bar_h+4}"><animate attributeName="width" from="0" to="{w+4:.1f}" dur="1.1s" begin="{0.15+i*0.12:.2f}s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1"/></rect></clipPath>'
        b.append(f'<path d="M{x0} {y}H{x0+w-4:.1f}a4 4 0 0 1 4 4v{bar_h-8}a4 4 0 0 1 -4 4H{x0}Z" fill="{t["bar"]}" clip-path="url(#c{i})"/>')
        # value label at the tip, in ink (never the data color)
        b.append(f'<path d="{SEMI.path(f"{val}%", x0 + w + 14, cy + 5.5, 14)}" fill="{t["ink"]}" opacity="0">'
                 f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{0.9+i*0.12:.2f}s" fill="freeze"/></path>')
    # footnote
    b.append(f'<rect x="40" y="{H-54}" width="{W-80}" height="1" fill="{t["grid"]}"/>')
    b.append(f'<rect x="40" y="{H-34}" width="14" height="6" rx="2" fill="{t["bar"]}"/>')
    b.append(T(REG, "Depth, self-assessed", 62, H - 27, 12.5, t["ink2"]))
    b.append(f'<rect x="196" y="{H-34}" width="14" height="6" rx="2" fill="{t["track"]}" stroke="{t["border"]}"/>')
    b.append(T(REG, "Remaining headroom", 218, H - 27, 12.5, t["ink2"]))
    b.append(T(MONO, "n = 6 domains", W - 40, H - 27, 11.5, t["ink3"], anchor="end", tracking=0.04))
    write("chart-skills", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
# 6. STACK LABELS
# ──────────────────────────────────────────────────────────────────────────────
STACK_LABELS = [("languages", "LANGUAGES"), ("ai", "AI · ML · DL"), ("data", "DATA & NUMERICAL"), ("backend", "BACKEND · CLOUD · DEVOPS"), ("tools", "TOOLS")]


def stack_label(t, theme, key, text):
    W, H = 1200, 34
    b = []
    tw = MONO.width(text, 12, 0.16)
    b.append(f'<rect x="0" y="16.5" width="{(W-tw)/2-22:.0f}" height="1" fill="{t["grid"]}"/>')
    b.append(f'<rect x="{(W+tw)/2+22:.0f}" y="16.5" width="{(W-tw)/2-22:.0f}" height="1" fill="{t["grid"]}"/>')
    b.append(T(MONO, text, W / 2, 21.5, 12, t["ink3"], anchor="middle", tracking=0.16))
    write(f"lbl-{key}", theme, svg(W, H, "".join(b)))


# ──────────────────────────────────────────────────────────────────────────────
# 7. CONNECT BUTTONS + FOOTER
# ──────────────────────────────────────────────────────────────────────────────
BUTTONS = [
    ("email", "Email me", True),
    ("linkedin", "LinkedIn", False),
    ("huggingface", "Hugging Face", False),
    ("portfolio", "Portfolio", False),
    ("aca", "AI Craft Alchemy", False),
]


def button(t, theme, key, label, primary):
    pad = 22
    tw = SEMI.width(label, 15)
    W, H = int(tw + pad * 2 + 26), 50
    b = []
    if primary:
        b.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="{t["accent"]}"/>')
        fg = t["btnText"]
    else:
        b.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="{t["chipbg"]}" stroke="{t["border2"]}"/>')
        fg = t["ink"]
    b.append(T(SEMI, label, pad, 31, 15, fg, tracking=-0.005))
    b.append(f'<path d="M{W-pad-12} 31l12-12M{W-pad-10} 19h10v10" fill="none" stroke="{fg}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    write(f"btn-{key}", theme, svg(W, H, "".join(b)))


def footer(t, theme):
    W, H = 1200, 120
    defs = (f'<linearGradient id="fg" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/><stop offset="0.5" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}" stop-opacity="0"/></linearGradient>')
    b = [f'<rect x="0" y="0" width="{W}" height="2" fill="url(#fg)"/>']
    b.append(T(SEMI, "Lokesh E", 0, 60, 18, t["ink"], tracking=-0.01))
    b.append(T(REG, "Generative AI Engineer · Building systems at the edge of what's possible", 0, 84, 13.5, t["ink2"]))
    b.append(T(MONO, "DESIGNED & HAND-BUILT IN SVG", W, 58, 11, t["ink3"], anchor="end", tracking=0.16))
    b.append(T(MONO, "© 2026 · MADE WITH CARE AND TOO MUCH COFFEE", W, 82, 11, t["ink3"], anchor="end", tracking=0.1))
    write("footer", theme, svg(W, H, "".join(b), defs))


# ──────────────────────────────────────────────────────────────────────────────
for theme, t in THEMES.items():
    hero(t, theme)
    for key, idx, title, cap in SECTIONS:
        section(t, theme, key, idx, title, cap)
    profile_card(t, theme)
    for key, title, acc, icon, bullets, tags in CARDS:
        expertise_card(t, theme, key, title, acc, icon, bullets, tags)
    chart(t, theme)
    for key, text in STACK_LABELS:
        stack_label(t, theme, key, text)
    for key, label, primary in BUTTONS:
        button(t, theme, key, label, primary)
    footer(t, theme)

print("ok:", len(os.listdir(OUT)), "files")
