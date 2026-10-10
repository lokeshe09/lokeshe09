"""Build the contribution-streak card from live GitHub data.

    GITHUB_TOKEN=... python tools/streak.py <out-dir> [login]

Pulls the full contribution calendar via GraphQL, computes total / current streak /
longest streak / weekly history, and renders streak-dark.svg + streak-light.svg
in the profile's design system (stat-tile row + ring + sparkline).
"""
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta

from svgkit import BOLD, SEMI, MED, REG, MONO, MONOB, T, THEMES, svg, write, glass_card, glass_tile, fmt_int

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "assets")
LOGIN = sys.argv[2] if len(sys.argv) > 2 else "lokeshe09"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
if not TOKEN:
    sys.exit("GITHUB_TOKEN is required")


# ──────────────────────────────────────────────────────────────────────────────
# Data
# ──────────────────────────────────────────────────────────────────────────────
def gql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "profile-streak"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit(f"GraphQL error: {payload['errors']}")
    return payload["data"]


created = datetime.fromisoformat(gql(f'{{ user(login:"{LOGIN}"){{ createdAt }} }}')["user"]["createdAt"].replace("Z", "+00:00")).date()
today = datetime.utcnow().date()

parts = []
for y in range(created.year, today.year + 1):
    start = f"{y}-01-01T00:00:00Z"
    end = f"{y}-12-31T23:59:59Z"
    parts.append(
        f'y{y}: contributionsCollection(from:"{start}", to:"{end}") '
        "{ contributionCalendar { weeks { contributionDays { date contributionCount } } } }"
    )
data = gql(f'{{ user(login:"{LOGIN}") {{ {" ".join(parts)} }} }}')["user"]

days = {}
for block in data.values():
    for wk in block["contributionCalendar"]["weeks"]:
        for d in wk["contributionDays"]:
            dd = date.fromisoformat(d["date"])
            if dd <= today:
                days[dd] = d["contributionCount"]

dates = sorted(days)
total = sum(days.values())
active_days = sum(1 for d in dates if days[d] > 0)
first = next((d for d in dates if days[d] > 0), None)

# current streak (today may still be empty — count from yesterday then)
cur_end = today if days.get(today, 0) > 0 else today - timedelta(days=1)
cur = 0
d = cur_end
while days.get(d, 0) > 0:
    cur += 1
    d -= timedelta(days=1)
cur_start = cur_end - timedelta(days=cur - 1) if cur else None

# longest streak
best, best_end, run = 0, None, 0
for d in dates:
    run = run + 1 if days[d] > 0 else 0
    if run > best:
        best, best_end = run, d
best_start = best_end - timedelta(days=best - 1) if best else None

# weekly history (last 26 full 7-day windows ending today)
WEEKS = 26
weekly = []
for i in range(WEEKS - 1, -1, -1):
    end = today - timedelta(days=7 * i)
    weekly.append((end, sum(days.get(end - timedelta(days=k), 0) for k in range(7))))
peak_week = max(weekly, key=lambda w: w[1])


def fmt_date(d, year=True):
    s = d.strftime("%b %d").replace(" 0", " ")
    return f"{s}, {d.year}" if year else s


def fmt_range(a, b):
    if not a:
        return "—"
    if a.year == b.year:
        return f"{fmt_date(a, False)} → {fmt_date(b, False)}, {b.year}"
    return f"{fmt_date(a)} → {fmt_date(b)}"


# ──────────────────────────────────────────────────────────────────────────────
# Render
# ──────────────────────────────────────────────────────────────────────────────
def render(theme):
    t = THEMES[theme]
    W, H = 1200, 400
    defs = (f'<linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity="0.18"/>'
            f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="rg" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>')
    gdefs, gbody = glass_card(t, W, H, 24, uid="sk", intensity=0.35)
    b = [gbody]

    # header
    b.append(f'<circle cx="46" cy="42" r="4" fill="{t["accent"]}"><animate attributeName="opacity" values="1;0.3;1" dur="2.2s" repeatCount="indefinite"/></circle>')
    b.append(T(MONO, "CONTRIBUTION STREAK", 60, 46.5, 12, t["ink2"], tracking=0.16))
    b.append(T(MONO, f"UPDATED {today.strftime('%Y-%m-%d')} UTC · REFRESHES DAILY", W - 40, 46.5, 11, t["ink3"], anchor="end", tracking=0.1))
    b.append(f'<rect x="40" y="66" width="{W-80}" height="1" fill="{t["grid"]}"/>')

    # tile dividers
    for x in (400, 800):
        b.append(f'<rect x="{x}" y="96" width="1" height="190" fill="{t["grid"]}"/>')

    def fade(i):
        return f'<animate attributeName="opacity" from="0" to="1" dur="0.6s" begin="{0.2+0.15*i:.2f}s" fill="freeze"/>'

    def tile(cx, label, number, sub, chip, i):
        g = [f'<g opacity="0">{fade(i)}']
        g.append(T(MED, label, cx, 128, 14, t["ink2"], anchor="middle"))
        g.append(T(BOLD, number, cx, 206, 64, t["ink"], anchor="middle", tracking=-0.03))
        g.append(T(MONO, sub, cx, 240, 12, t["ink3"], anchor="middle", tracking=0.04))
        cw = MONO.width(chip, 10.5, 0.1) + 24
        g.append(f'<rect x="{cx-cw/2:.1f}" y="256" width="{cw:.0f}" height="24" rx="7" fill="{t["iconTint"]}"/>')
        g.append(T(MONO, chip, cx, 272, 10.5, t["accent"], anchor="middle", tracking=0.1))
        g.append("</g>")
        return "".join(g)

    b.append(tile(220, "Total contributions", fmt_int(total),
                  (fmt_date(first).upper() + " → PRESENT") if first else "—",
                  f"{active_days} ACTIVE DAYS", 0))
    b.append(tile(980, "Longest streak", fmt_int(best),
                  fmt_range(best_start, best_end).upper(), "PERSONAL RECORD", 2))

    # centre: ring
    cx, cy, r, sw = 600, 172, 58, 9
    C = 2 * 3.141592653589793 * r
    frac = min(cur / best, 1.0) if best else 0.0
    b.append(f'<g opacity="0">{fade(1)}')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["track"]}" stroke-width="{sw}"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#rg)" stroke-width="{sw}" stroke-linecap="round" '
             f'stroke-dasharray="{C:.2f}" stroke-dashoffset="{C:.2f}" transform="rotate(-90 {cx} {cy})">'
             f'<animate attributeName="stroke-dashoffset" from="{C:.2f}" to="{C*(1-frac):.2f}" dur="1.4s" begin="0.4s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1"/></circle>')
    b.append(T(BOLD, fmt_int(cur), cx, cy + 12, 40, t["ink"], anchor="middle", tracking=-0.03))
    b.append(T(MONO, "DAYS", cx, cy + 32, 10.5, t["ink3"], anchor="middle", tracking=0.18))
    b.append(T(MED, "Current streak", cx, 258, 14, t["ink"], anchor="middle"))
    b.append(T(MONO, fmt_range(cur_start, cur_end).upper() if cur else "NO ACTIVE STREAK", cx, 280, 12, t["ink3"], anchor="middle", tracking=0.04))
    pct = int(round(frac * 100))
    b.append(T(MONO, f"{pct}% OF RECORD", cx + r + 24, cy + 4, 10.5, t["ink3"], tracking=0.1))
    b.append("</g>")

    # sparkline: last 26 weeks
    x0, x1, y0, y1 = 40, W - 40, 318, 372
    b.append(f'<rect x="40" y="300" width="{W-80}" height="1" fill="{t["grid"]}"/>')
    b.append(T(MONO, f"LAST {WEEKS} WEEKS · CONTRIBUTIONS PER WEEK", x0, 314, 10.5, t["ink3"], tracking=0.12))
    b.append(T(MONO, f"PEAK {peak_week[1]} · WEEK OF {fmt_date(peak_week[0] - timedelta(days=6), False).upper()}", x1, 314, 10.5, t["ink3"], anchor="end", tracking=0.1))
    mx = max(peak_week[1], 1)
    pts = []
    for i, (_, v) in enumerate(weekly):
        px = x0 + (x1 - x0) * i / (WEEKS - 1)
        py = y1 - (y1 - y0 - 6) * v / mx
        pts.append((px, py))
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = line + f" L{x1} {y1} L{x0} {y1} Z"
    length = sum(((pts[i][0]-pts[i-1][0])**2 + (pts[i][1]-pts[i-1][1])**2) ** 0.5 for i in range(1, len(pts)))
    b.append(f'<rect x="{x0}" y="{y1}" width="{x1-x0}" height="1" fill="{t["grid"]}"/>')
    b.append(f'<path d="{area}" fill="url(#ag)" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.8s" begin="1.2s" fill="freeze"/></path>')
    # history in the de-emphasis hue, drawn in
    b.append(f'<path d="{line}" fill="none" stroke="{t["ink3"]}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" '
             f'stroke-dasharray="{length:.1f}" stroke-dashoffset="{length:.1f}">'
             f'<animate attributeName="stroke-dashoffset" from="{length:.1f}" to="0" dur="1.4s" begin="0.6s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1"/></path>')
    # current period in the accent + end marker with surface ring
    (ax, ay), (bx, by) = pts[-2], pts[-1]
    b.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.9s" fill="freeze"/>'
             f'<path d="M{ax:.1f} {ay:.1f} L{bx:.1f} {by:.1f}" fill="none" stroke="{t["accent"]}" stroke-width="2.5" stroke-linecap="round"/>'
             f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="6.5" fill="{t["panel"]}"/><circle cx="{bx:.1f}" cy="{by:.1f}" r="4.5" fill="{t["accent"]}"/></g>')
    # selective direct label: the peak only
    pi = weekly.index(peak_week)
    px, py = pts[pi]
    anchor = "end" if px > x1 - 40 else ("start" if px < x0 + 40 else "middle")
    b.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2s" fill="freeze"/>'
             f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{t["ink3"]}"/>'
             + T(MONOB, str(peak_week[1]), px, py - 9, 11, t["ink"], anchor=anchor) + "</g>")

    write("streak", theme, svg(W, H, "".join(b), gdefs + defs), OUT)


for th in THEMES:
    render(th)
print(f"ok: total={total} current={cur} longest={best} active={active_days} -> {OUT}")
