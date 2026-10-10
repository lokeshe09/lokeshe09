"""Isometric 3D contribution calendar, in the profile's design system.

    GITHUB_TOKEN=... python tools/contrib3d.py <out-dir> [login]

Renders contrib3d-dark.svg + contrib3d-light.svg: the last 52 weeks as an
isometric city — one block per day, height by contributions, rising in with a
left→right wave.
"""
import os
import sys
from datetime import timedelta

from svgkit import BOLD, SEMI, MED, REG, MONO, MONOB, T, THEMES, svg, write, glass_card, glass_tile, iso, iso_prism, shade, fmt_int, tip
from ghdata import calendar

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "assets")
LOGIN = sys.argv[2] if len(sys.argv) > 2 else "lokeshe09"

days, today = calendar(LOGIN)

# 52 full weeks + the current partial week, Sunday-first columns like GitHub
WEEKS = 53
end_sunday = today - timedelta(days=(today.weekday() + 1) % 7)       # most recent Sunday
start = end_sunday - timedelta(weeks=WEEKS - 1)
grid = []  # [(week_index, day_index, date, count)]
for w in range(WEEKS):
    for d in range(7):
        dt = start + timedelta(weeks=w, days=d)
        if dt > today:
            continue
        grid.append((w, d, dt, days.get(dt, 0)))

counts = [c for *_, c in grid]
total = sum(counts)
peak = max(counts) if counts else 0
active = sum(1 for c in counts if c > 0)
# quantile levels (1..4) for non-zero days, like GitHub's shading
nz = sorted(c for c in counts if c > 0)
def level(c):
    if c == 0:
        return 0
    q = [nz[int(len(nz) * p)] for p in (0.25, 0.5, 0.75)] if nz else [1, 1, 1]
    return 1 + sum(1 for qq in q if c > qq)

RAMP = {
    "dark": ["#1A2333", "#0F5A32", "#148A48", "#19B058", "#2AE86D"],
    "light": ["#E2E8F0", "#BBF7D0", "#86EFAC", "#22C55E", "#15803D"],
}


def render(theme):
    t = THEMES[theme]
    W, H = 1200, 600
    uid = "c3"
    defs, body = glass_card(t, W, H, 24, uid=uid, intensity=0.4)
    b = [body]
    # header
    b.append(f'<circle cx="46" cy="42" r="4" fill="{t["accent"]}"/>')
    b.append(T(MONO, "CONTRIBUTIONS · 3D", 60, 46.5, 12, t["ink2"], tracking=0.16))
    b.append(T(MONO, f"LAST 52 WEEKS · UPDATED {today.strftime('%Y-%m-%d')} UTC", W - 40, 46.5, 11, t["ink3"], anchor="end", tracking=0.1))
    b.append(f'<rect x="40" y="66" width="{W-80}" height="1" fill="{t["grid"]}"/>')

    # isometric scene
    cell, gap = 10.0, 1.4
    step = cell + gap
    # centre the projected footprint inside the content area
    xs = [iso(px, py)[0] for px in (0, WEEKS * step) for py in (0, 7 * step)]
    ys = [iso(px, py)[1] for px in (0, WEEKS * step) for py in (0, 7 * step)]
    ox = W / 2 - (min(xs) + max(xs)) / 2
    oy = 150                               # projection origin (grid 0,0 at z=0)
    # ground plane shadow: a soft rhombus under the whole grid
    g0x, g0y = iso(0, 0); g1x, g1y = iso(WEEKS * step, 0); g2x, g2y = iso(WEEKS * step, 7 * step); g3x, g3y = iso(0, 7 * step)
    defs += (f'<filter id="{uid}-soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="10"/></filter>')
    b.append(f'<polygon points="{ox+g0x:.1f},{oy+g0y+10:.1f} {ox+g1x:.1f},{oy+g1y+10:.1f} {ox+g2x:.1f},{oy+g2y+10:.1f} {ox+g3x:.1f},{oy+g3y+10:.1f}" fill="{t["glowB"]}" opacity="0.18" filter="url(#{uid}-soft)"/>')

    ramp = RAMP[theme]
    maxh = 54.0
    # painter's order: far (small x+y) first
    for w, d, dt, c in sorted(grid, key=lambda g: (g[0] + g[1], g[0])):
        lv = level(c)
        top = ramp[lv]
        h = 2.5 if c == 0 else 5 + maxh * (c / peak) ** 0.6
        left, right = shade(top, 0.80), shade(top, 0.64)
        if theme == "light" and lv == 0:
            left, right = shade(top, 0.93), shade(top, 0.86)
        begin = 0.1 + w * 0.028 + d * 0.01
        anim = (f'<animateTransform attributeName="transform" type="translate" from="0 18" to="0 0" dur="0.7s" begin="{begin:.2f}s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1"/>'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{begin:.2f}s" fill="freeze"/>')
        label = f"{dt.strftime('%a, %b %d, %Y').replace(' 0', ' ')} · {c} contribution{'s' if c != 1 else ''}"
        prism = iso_prism(ox, oy, w * step, d * step, cell, cell, h, top, left, right, extra=tip(label))
        b.append(f'<g opacity="0">{anim}{prism}</g>')

    # month labels along the front-left edge (where the month changes)
    seen = set()
    for w in range(WEEKS):
        dt = start + timedelta(weeks=w)
        key = (dt.year, dt.month)
        if dt.day <= 7 and key not in seen:
            seen.add(key)
            lx, ly = iso(w * step + cell / 2, 7 * step + 12)
            b.append(T(MONO, dt.strftime("%b").upper(), ox + lx, oy + ly + 4, 10.5, t["ink3"], anchor="middle", tracking=0.1))
    # weekday labels on the right edge
    for d, name in ((0, "SUN"), (3, "WED"), (6, "SAT")):
        lx, ly = iso(WEEKS * step + 10, d * step + cell / 2)
        b.append(T(MONO, name, ox + lx + 6, oy + ly + 4, 10.5, t["ink3"], tracking=0.1))

    # legend + stats tiles (bottom)
    ty = H - 92
    b.append(glass_tile(t, 40, ty, 300, 56, 14, uid))
    lx = 60
    b.append(T(MONO, "LESS", lx, ty + 34, 10.5, t["ink3"], tracking=0.12))
    lx += 44
    for i, col in enumerate(ramp):
        b.append(iso_prism(lx + i * 24, ty + 30, 0, 0, 12, 12, 4 + i * 3, col, shade(col, 0.8), shade(col, 0.64)))
    b.append(T(MONO, "MORE", lx + 5 * 24 + 8, ty + 34, 10.5, t["ink3"], tracking=0.12))

    tiles = [("TOTAL", fmt_int(total)), ("ACTIVE DAYS", fmt_int(active)), ("PEAK DAY", fmt_int(peak))]
    tx = W - 40
    for label, val in reversed(tiles):
        tw = 180
        tx -= tw
        b.append(glass_tile(t, tx, ty, tw - 12, 56, 14, uid))
        b.append(f'<rect x="{tx}" y="{ty}" width="{tw-12}" height="56" rx="14" fill="transparent"{tip(f"{label.title()}: {val} (last 52 weeks)")}/>')
        b.append(T(MONO, label, tx + 18, ty + 22, 10, t["ink3"], tracking=0.14))
        b.append(T(BOLD, val, tx + 18, ty + 46, 20, t["ink"], tracking=-0.02))
    write("contrib3d", theme, svg(W, H, "".join(b), defs), OUT)


for th in THEMES:
    render(th)
print(f"ok: total={total} active={active} peak={peak} -> {OUT}")
