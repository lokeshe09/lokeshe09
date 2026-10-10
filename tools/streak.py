"""Build the contribution-streak card from live GitHub data.

    GITHUB_TOKEN=... python tools/streak.py <out-dir> [login]

streak-dark.svg / streak-light.svg — an "energy core" layout:
  · centre: current streak inside a glowing progress ring (vs. personal record),
    wrapped by a 52-week radial activity ring (one tick per week)
  · left : total contributions + cumulative growth curve
  · right: longest streak + a 90-day streak track
  · base : last 26 weeks as thin gradient bars, peak labelled
"""
import math
import os
import sys
from datetime import timedelta

from svgkit import BOLD, SEMI, MED, REG, MONO, MONOB, T, THEMES, svg, write, glass_card, glass_tile, shade, fmt_int, tip
from ghdata import calendar

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "assets")
LOGIN = sys.argv[2] if len(sys.argv) > 2 else "lokeshe09"

days, today = calendar(LOGIN)
dates = sorted(days)
total = sum(days.values())
active_days = sum(1 for d in dates if days[d] > 0)
first = next((d for d in dates if days[d] > 0), None)

# current streak (today may still be empty - count from yesterday then)
cur_end = today if days.get(today, 0) > 0 else today - timedelta(days=1)
cur, d = 0, cur_end
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


def weekly(n):
    out = []
    for i in range(n - 1, -1, -1):
        end = today - timedelta(days=7 * i)
        out.append((end, sum(days.get(end - timedelta(days=k), 0) for k in range(7))))
    return out


w26, w52 = weekly(26), weekly(52)
peak26 = max(w26, key=lambda w: w[1])
max52 = max((v for _, v in w52), default=1) or 1
last90 = [(today - timedelta(days=89 - i), days.get(today - timedelta(days=89 - i), 0)) for i in range(90)]

# cumulative growth curve (all time)
cum, acc = [], 0
for d in dates:
    acc += days[d]
    cum.append(acc)


def fmt_date(d, year=True):
    s = d.strftime("%b %d").replace(" 0", " ")
    return f"{s}, {d.year}" if year else s


def fmt_range(a, b):
    if not a:
        return "—"
    if a.year == b.year:
        return f"{fmt_date(a, False)} → {fmt_date(b, False)}, {b.year}"
    return f"{fmt_date(a)} → {fmt_date(b)}"


def pl(n):
    return "" if n == 1 else "s"


def fade(begin, dur=0.6):
    return f'<animate attributeName="opacity" from="0" to="1" dur="{dur}s" begin="{begin:.2f}s" fill="freeze"/>'


def render(theme):
    t = THEMES[theme]
    W, H = 1200, 540
    uid = "sk"
    defs, body = glass_card(t, W, H, 24, uid=uid, intensity=0.45,
                            orbs=[(t["glowA"], 600, 260, 210, 0, 0, 12), (t["glowB"], 120, 520, 200, 50, -30, 19), (t["glowC"], 1080, 40, 200, -50, 40, 17)])
    defs += (f'<linearGradient id="{uid}-ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>'
             f'<linearGradient id="{uid}-area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="0.35"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="{uid}-bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{t["bar"]}" stop-opacity="0.55"/><stop offset="1" stop-color="{t["accent"]}"/></linearGradient>'
             f'<filter id="{uid}-glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="8"/></filter>')
    b = [body]

    # ── header ──────────────────────────────────────────────────────────
    b.append(f'<circle cx="46" cy="42" r="4" fill="{t["accent"]}"><animate attributeName="opacity" values="1;0.3;1" dur="2.2s" repeatCount="indefinite"/></circle>')
    b.append(T(MONO, "CONTRIBUTION STREAK", 60, 46.5, 12, t["ink2"], tracking=0.16))
    b.append(T(MONO, f"UPDATED {today.strftime('%Y-%m-%d')} UTC · REFRESHES DAILY", W - 40, 46.5, 11, t["ink3"], anchor="end", tracking=0.1))
    b.append(f'<rect x="40" y="66" width="{W-80}" height="1" fill="{t["grid"]}"/>')

    # ── centre: energy core ─────────────────────────────────────────────
    cx, cy = 600, 240
    # 52-week radial activity ring (one tick per week, clockwise, newest at 12 o'clock)
    b.append(f'<g opacity="0">{fade(0.2, 0.8)}')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="126" fill="none" stroke="{t["grid"]}" stroke-width="1"/>')
    n = len(w52)
    for i, (wend, v) in enumerate(w52):
        ang = math.radians(-90 + (i + 1) * 360 / n)
        r0, ln = 130, 6 + 34 * (v / max52) ** 0.7
        x0, y0 = cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)
        x1, y1 = cx + (r0 + ln) * math.cos(ang), cy + (r0 + ln) * math.sin(ang)
        col = t["accent"] if i == n - 1 else (t["bar"] if v > 0 else t["ink3"])
        op = 1 if i == n - 1 else (0.35 + 0.65 * (v / max52) ** 0.5 if v > 0 else 0.25)
        wk = f"Week of {fmt_date(wend - timedelta(days=6), False)} – {fmt_date(wend, False)}, {wend.year} · {v} contribution{'s' if v != 1 else ''}"
        b.append(f'<path d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}" stroke="{col}" stroke-width="3.2" stroke-linecap="round" opacity="{op:.2f}"{tip(wk)}>'
                 f'<animate attributeName="opacity" from="0" to="{op:.2f}" dur="0.4s" begin="{0.3 + i*0.02:.2f}s" fill="freeze"/></path>'
                 f'<path d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}" stroke="transparent" stroke-width="10" stroke-linecap="round"{tip(wk)}/>')
    b.append("</g>")
    # orbiting particle on the activity ring
    b.append(f'<circle r="4" fill="{t["accent"]}"><animateMotion dur="12s" repeatCount="indefinite" path="M{cx} {cy-150} a150 150 0 1 1 -0.1 0"/></circle>')
    b.append(f'<circle r="9" fill="{t["accent"]}" opacity="0.35" filter="url(#{uid}-glow)"><animateMotion dur="12s" repeatCount="indefinite" path="M{cx} {cy-150} a150 150 0 1 1 -0.1 0"/></circle>')
    # progress ring: current streak vs record
    r, sw = 96, 12
    C = 2 * math.pi * r
    frac = min(cur / best, 1.0) if best else 0.0
    b.append(f'<g opacity="0">{fade(0.3)}')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#{uid}-ring)" stroke-width="{sw+10}" opacity="0.35" filter="url(#{uid}-glow)" '
             f'stroke-dasharray="{C:.2f}" stroke-dashoffset="{C:.2f}" transform="rotate(-90 {cx} {cy})"><animate attributeName="stroke-dashoffset" from="{C:.2f}" to="{C*(1-frac):.2f}" dur="1.6s" begin="0.5s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1"/></circle>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["track"]}" stroke-width="{sw}"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#{uid}-ring)" stroke-width="{sw}" stroke-linecap="round" '
             f'stroke-dasharray="{C:.2f}" stroke-dashoffset="{C:.2f}" transform="rotate(-90 {cx} {cy})"><animate attributeName="stroke-dashoffset" from="{C:.2f}" to="{C*(1-frac):.2f}" dur="1.6s" begin="0.5s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1"/></circle>')
    # inner glass disc + number
    ring_tip = tip(f"Current streak {cur} day{pl(cur)} · {int(round(frac*100))}% of your {best}-day record")
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r-14}" fill="{t["g_tile"]}" stroke="url(#{uid}-bd)"{ring_tip}/>')
    b.append(T(BOLD, fmt_int(cur), cx, cy + 16, 64, t["ink"], anchor="middle", tracking=-0.04))
    b.append(T(MONO, "DAY STREAK", cx, cy + 40, 11, t["ink3"], anchor="middle", tracking=0.2))
    b.append(T(MONO, "CURRENT", cx, cy - 46, 10.5, t["accent"], anchor="middle", tracking=0.24))
    b.append("</g>")
    # captions under the core
    b.append(f'<g opacity="0">{fade(0.9)}')
    b.append(T(MED, fmt_range(cur_start, cur_end) if cur else "No active streak — start one today", cx, 410, 14, t["ink"], anchor="middle"))
    chip = f"{int(round(frac*100))}% OF PERSONAL RECORD"
    cw = MONO.width(chip, 10.5, 0.12) + 26
    b.append(glass_tile(t, cx - cw / 2, 422, cw, 24, 7, uid))
    b.append(T(MONO, chip, cx, 438, 10.5, t["accent"], anchor="middle", tracking=0.12))
    b.append("</g>")

    # ── left: total contributions + growth curve ───────────────────────
    lx = 40
    b.append(f'<g opacity="0">{fade(0.35)}')
    b.append(T(MED, "Total contributions", lx, 112, 14, t["ink2"]))
    b.append(T(BOLD, fmt_int(total), lx, 176, 60, t["ink"], tracking=-0.035, extra=tip(f"{fmt_int(total)} contributions since {fmt_date(first) if first else '—'} · {active_days} active days")))
    b.append(T(MONO, (fmt_date(first).upper() + " → PRESENT") if first else "—", lx, 200, 11.5, t["ink3"], tracking=0.06))
    # cumulative growth curve
    gx0, gx1, gy0, gy1 = lx, 380, 236, 318
    if cum:
        pts = [(gx0 + (gx1 - gx0) * i / max(len(cum) - 1, 1), gy1 - (gy1 - gy0) * v / max(cum[-1], 1)) for i, v in enumerate(cum)]
        line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        b.append(f'<path d="{line} L{gx1} {gy1} L{gx0} {gy1} Z" fill="url(#{uid}-area)"/>')
        b.append(f'<path d="{line}" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        ex, ey = pts[-1]
        b.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="7" fill="{t["panel"]}"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="4.5" fill="{t["accent"]}"/>')
        step = max(1, len(pts) // 60)
        for i in range(0, len(pts), step):
            px, py = pts[i]
            b.append(f'<rect x="{px - (gx1-gx0)/len(pts)*step/2:.1f}" y="{gy0-6}" width="{(gx1-gx0)/len(pts)*step:.1f}" height="{gy1-gy0+12}" fill="transparent"{tip(f"{fmt_date(dates[i])} · {fmt_int(cum[i])} total contributions")}/>')
        b.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4.5" fill="none" stroke="{t["accent"]}" stroke-width="1.5"><animate attributeName="r" values="4.5;14" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.8;0" dur="2s" repeatCount="indefinite"/></circle>')
    b.append(f'<rect x="{gx0}" y="{gy1}" width="{gx1-gx0}" height="1" fill="{t["grid"]}"/>')
    b.append(T(MONO, "CUMULATIVE GROWTH · ALL TIME", lx, 338, 10, t["ink3"], tracking=0.14))
    cw = MONO.width(f"{active_days} ACTIVE DAYS", 10.5, 0.1) + 24
    b.append(glass_tile(t, lx, 352, cw, 24, 7, uid))
    b.append(T(MONO, f"{active_days} ACTIVE DAYS", lx + cw / 2, 368, 10.5, t["accent"], anchor="middle", tracking=0.1))
    avg = total / max(active_days, 1)
    b.append(T(MONO, f"~{avg:.1f} PER ACTIVE DAY", lx + cw + 14, 368, 10.5, t["ink3"], tracking=0.1))
    b.append("</g>")

    # ── right: longest streak + 90-day track ───────────────────────────
    rx = 820
    b.append(f'<g opacity="0">{fade(0.45)}')
    b.append(T(MED, "Longest streak", rx, 112, 14, t["ink2"]))
    b.append(T(BOLD, fmt_int(best), rx, 176, 60, t["ink"], tracking=-0.035, extra=tip(f"Longest streak {best} days · {fmt_range(best_start, best_end)}")))
    b.append(T(MONO, fmt_range(best_start, best_end).upper(), rx, 200, 11.5, t["ink3"], tracking=0.06))
    # 90-day track: 3 rows × 30 cells, streak runs light up
    cell, gap, cols = 9, 2.6, 30
    tx, ty = rx, 236
    in_cur = set((cur_start + timedelta(days=k)) for k in range(cur)) if cur else set()
    in_best = set((best_start + timedelta(days=k)) for k in range(best)) if best else set()
    for i, (dd, v) in enumerate(last90):
        c, r_ = i % cols, i // cols
        x, y = tx + c * (cell + gap), ty + r_ * (cell + gap)
        if dd in in_cur:
            col, op = t["accent"], 1.0
        elif dd in in_best:
            col, op = t["accent2"], 0.9
        elif v > 0:
            col, op = t["bar"], 0.75
        else:
            col, op = t["ink3"], 0.22
        extra = f'<animate attributeName="opacity" values="1;0.45;1" dur="1.6s" repeatCount="indefinite"/>' if dd == cur_end and cur else ""
        state = "current streak" if dd in in_cur else ("personal record" if dd in in_best else ("active" if v > 0 else "no activity"))
        cell_tip = tip(f"{fmt_date(dd)} · {v} contribution{pl(v)} · {state}")
        b.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.5" fill="{col}" opacity="{op}"{cell_tip}>{extra}</rect>')
    b.append(T(MONO, "LAST 90 DAYS", rx, 288, 10, t["ink3"], tracking=0.14))
    # legend
    lgx = rx
    for col, label in ((t["accent"], "CURRENT"), (t["accent2"], "RECORD"), (t["bar"], "ACTIVE")):
        b.append(f'<rect x="{lgx}" y="300" width="9" height="9" rx="2.5" fill="{col}"/>')
        b.append(T(MONO, label, lgx + 14, 308, 9.5, t["ink3"], tracking=0.12))
        lgx += 14 + MONO.width(label, 9.5, 0.12) + 16
    cw = MONO.width("PERSONAL RECORD", 10.5, 0.1) + 24
    b.append(glass_tile(t, rx, 352, cw, 24, 7, uid))
    b.append(T(MONO, "PERSONAL RECORD", rx + cw / 2, 368, 10.5, t["accent"], anchor="middle", tracking=0.1))
    b.append("</g>")

    # ── base: last 26 weeks as thin gradient bars ──────────────────────
    bx0, bx1, by0, by1 = 40, W - 40, 470, 512
    b.append(f'<rect x="40" y="452" width="{W-80}" height="1" fill="{t["grid"]}"/>')
    b.append(T(MONO, "LAST 26 WEEKS · CONTRIBUTIONS PER WEEK", bx0, 466, 10, t["ink3"], tracking=0.14))
    b.append(T(MONO, f"PEAK {peak26[1]} · WEEK OF {fmt_date(peak26[0] - timedelta(days=6), False).upper()}", bx1, 466, 10, t["ink3"], anchor="end", tracking=0.1))
    mx = max(peak26[1], 1)
    slot = (bx1 - bx0) / len(w26)
    bw = min(slot - 8, 24)
    for i, (end, v) in enumerate(w26):
        x = bx0 + i * slot + (slot - bw) / 2
        h = max(3, (by1 - by0) * v / mx)
        fill = t["accent"] if i == len(w26) - 1 else ("url(#" + uid + "-bar)" if v > 0 else t["grid"])
        wk = f"Week of {fmt_date(end - timedelta(days=6), False)} – {fmt_date(end, False)}, {end.year} · {v} contribution{'s' if v != 1 else ''}"
        b.append(f'<rect x="{x - (slot-bw)/2:.1f}" y="{by0-10}" width="{slot:.1f}" height="{by1-by0+12}" fill="transparent"{tip(wk)}/>')
        b.append(f'<rect x="{x:.1f}" y="{by1-h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="3" fill="{fill}"{tip(wk)}>'
                 f'<animate attributeName="height" from="0" to="{h:.1f}" dur="0.8s" begin="{0.6 + i*0.03:.2f}s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1"/>'
                 f'<animate attributeName="y" from="{by1}" to="{by1-h:.1f}" dur="0.8s" begin="{0.6 + i*0.03:.2f}s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1"/></rect>')
        if (end, v) == peak26:
            b.append(f'<path d="{MONOB.path(str(v), x + bw / 2, by1 - h - 6, 10.5, anchor="middle")}" fill="{t["ink"]}" opacity="0">{fade(1.6, 0.4)}</path>')
    b.append(f'<rect x="{bx0}" y="{by1}" width="{bx1-bx0}" height="1" fill="{t["border2"]}"/>')

    write("streak", theme, svg(W, H, "".join(b), defs), OUT)


for th in THEMES:
    render(th)
print(f"ok: total={total} current={cur} longest={best} active={active_days} -> {OUT}")
