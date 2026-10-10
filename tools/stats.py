"""Build the GitHub analytics panel from live data.

    GITHUB_TOKEN=... python tools/stats.py <out-dir> [login]

Renders stats-dark.svg + stats-light.svg: a KPI row (commits, contributions,
repos, stars, PRs, followers) and a part-to-whole language bar with legend.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime

from svgkit import BOLD, SEMI, MED, REG, MONO, MONOB, T, THEMES, svg, write, glass_card, glass_tile, fmt_int

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "assets")
LOGIN = sys.argv[2] if len(sys.argv) > 2 else "lokeshe09"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
if not TOKEN:
    sys.exit("GITHUB_TOKEN is required")


def gql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


today = datetime.utcnow().date()
u = gql(f'{{ user(login:"{LOGIN}"){{ createdAt }} }}')
created = datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00")).date()

year_blocks = " ".join(
    f'y{y}: contributionsCollection(from:"{y}-01-01T00:00:00Z", to:"{y}-12-31T23:59:59Z")'
    "{ totalCommitContributions restrictedContributionsCount contributionCalendar{ totalContributions weeks{ contributionDays{ contributionCount } } } }"
    for y in range(created.year, today.year + 1)
)
u = gql(
    f'{{ user(login:"{LOGIN}") {{ '
    "followers{totalCount} pullRequests{totalCount} issues{totalCount} "
    "repositories(first:100, ownerAffiliations:OWNER, isFork:false, orderBy:{field:STARGAZERS, direction:DESC})"
    "{ totalCount nodes{ stargazerCount languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } } } "
    f"{year_blocks} }} }}"
)

commits = sum(v["totalCommitContributions"] + v["restrictedContributionsCount"] for k, v in u.items() if k.startswith("y"))
contribs = sum(v["contributionCalendar"]["totalContributions"] for k, v in u.items() if k.startswith("y"))
active_days = sum(
    1
    for k, v in u.items() if k.startswith("y")
    for wk in v["contributionCalendar"]["weeks"]
    for d in wk["contributionDays"] if d["contributionCount"] > 0
)
repos = u["repositories"]["totalCount"]
stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
prs = u["pullRequests"]["totalCount"]
issues = u["issues"]["totalCount"]
followers = u["followers"]["totalCount"]

lang_bytes = {}
for n in u["repositories"]["nodes"]:
    for e in n["languages"]["edges"]:
        lang_bytes[e["node"]["name"]] = lang_bytes.get(e["node"]["name"], 0) + e["size"]
total_bytes = sum(lang_bytes.values()) or 1
ranked = sorted(lang_bytes.items(), key=lambda kv: -kv[1])
TOP = 5
langs = [(k, v / total_bytes) for k, v in ranked[:TOP]]
other = sum(v for _, v in ranked[TOP:]) / total_bytes
if other > 0:
    langs.append(("Other", other))

# Validated categorical palette (dataviz reference instance): fixed slot order, never cycled.
SERIES = {
    "dark": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181"],
    "light": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"],
}


def render(theme):
    t = THEMES[theme]
    W, H = 1200, 420
    gdefs, gbody = glass_card(t, W, H, 24, uid="st", intensity=0.35)
    b = [gbody]
    b.append(f'<circle cx="46" cy="42" r="4" fill="{t["accent"]}"/>')
    b.append(T(MONO, "GITHUB ANALYTICS", 60, 46.5, 12, t["ink2"], tracking=0.16))
    b.append(T(MONO, f"UPDATED {today.strftime('%Y-%m-%d')} UTC · ALL-TIME · PUBLIC + PRIVATE ACTIVITY", W - 40, 46.5, 11, t["ink3"], anchor="end", tracking=0.1))
    b.append(f'<rect x="40" y="66" width="{W-80}" height="1" fill="{t["grid"]}"/>')

    # ── KPI grid (left, 3 × 2) ────────────────────────────────────────────
    kpis = [
        ("Commits", fmt_int(commits)),
        ("Contributions", fmt_int(contribs)),
        ("Active days", fmt_int(active_days)),
        ("Public repos", fmt_int(repos)),
        ("Pull requests", fmt_int(prs)),
        ("Languages", fmt_int(len(lang_bytes))),
    ]
    gx, gy, cw, ch = 40, 92, 210, 140
    for i, (label, val) in enumerate(kpis):
        col, row = i % 3, i // 3
        x, y = gx + col * cw, gy + row * ch
        b.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{0.15+0.08*i:.2f}s" fill="freeze"/>')
        b.append(T(MED, label, x, y + 28, 13, t["ink2"]))
        b.append(T(BOLD, val, x, y + 82, 44, t["ink"], tracking=-0.03))
        b.append("</g>")
        if row == 0:
            b.append(f'<rect x="{x}" y="{gy+ch-10}" width="{cw-26}" height="1" fill="{t["grid"]}"/>')
    # vertical divider between KPIs and languages
    b.append(f'<rect x="690" y="92" width="1" height="280" fill="{t["grid"]}"/>')

    # ── Languages (right): part-to-whole bar + legend ────────────────────
    lx, ly, lw = 730, 92, W - 40 - 730
    b.append(T(MED, "Languages", lx, ly + 28, 13, t["ink2"]))
    b.append(T(MONO, "BY BYTES · OWN PUBLIC REPOS", W - 40, ly + 27, 10.5, t["ink3"], anchor="end", tracking=0.1))
    by = ly + 54
    bh = 14
    x = lx
    gap = 2
    cols = SERIES[theme]
    for i, (name, frac) in enumerate(langs):
        w = max(lw * frac - gap, 0)
        col = cols[i] if name != "Other" else t["ink3"]
        rx = 4 if i == 0 or i == len(langs) - 1 else 0
        # segment with 2px surface gap; rounded only at the ends
        if i == 0:
            d = f"M{x+4} {by}H{x+w}V{by+bh}H{x+4}a4 4 0 0 1 -4 -4V{by+4}a4 4 0 0 1 4 -4Z"
        elif i == len(langs) - 1:
            d = f"M{x} {by}H{x+w-4}a4 4 0 0 1 4 4V{by+bh-4}a4 4 0 0 1 -4 4H{x}Z"
        else:
            d = f"M{x} {by}H{x+w}V{by+bh}H{x}Z"
        b.append(f'<path d="{d}" fill="{col}"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{0.3+0.1*i:.2f}s" fill="freeze"/></path>')
        x += w + gap
    # legend rows (2 columns)
    ry = by + 48
    for i, (name, frac) in enumerate(langs):
        col = cols[i] if name != "Other" else t["ink3"]
        cx = lx + (i % 2) * (lw / 2)
        cy = ry + (i // 2) * 34
        b.append(f'<rect x="{cx:.0f}" y="{cy-9}" width="12" height="12" rx="3" fill="{col}"/>')
        b.append(T(MED, name, cx + 22, cy + 1, 14, t["ink"]))
        b.append(T(MONO, f"{frac*100:.1f}%", cx + lw / 2 - 28, cy + 1, 12, t["ink3"], anchor="end"))
    # footer line
    b.append(f'<rect x="40" y="{H-54}" width="{W-80}" height="1" fill="{t["grid"]}"/>')
    b.append(T(REG, "Commits and contributions include private activity. Repos and languages count own, non-fork public repositories.", 40, H - 27, 12.5, t["ink2"]))
    b.append(T(MONO, f"{fmt_int(repos)} REPOS SCANNED", W - 40, H - 27, 11.5, t["ink3"], anchor="end", tracking=0.06))
    write("stats", theme, svg(W, H, "".join(b), gdefs), OUT)


for th in THEMES:
    render(th)
print(f"ok: commits={commits} contribs={contribs} repos={repos} stars={stars} prs={prs} followers={followers} langs={len(langs)} -> {OUT}")
