"""Shared SVG toolkit for the profile assets: fonts → vector paths, theme tokens, primitives.

Fonts are loaded from FONT_DIR (env) or ./fonts next to this file.
Output goes to OUT_DIR (env) or ../assets unless `write()` is given an explicit dir.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get("FONT_DIR") or os.path.join(HERE, "fonts")
DEFAULT_OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "..", "assets")


class Face:
    def __init__(self, path):
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upem = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]

    def _g(self, ch):
        return self.cmap.get(ord(ch)) or self.cmap.get(ord("?"))

    def width(self, text, size, tracking=0.0):
        w = sum(self.hmtx[self._g(c)][0] for c in text) * size / self.upem
        return w + tracking * size * max(len(text) - 1, 0)

    def path(self, text, x, y, size, anchor="start", tracking=0.0):
        s = size / self.upem
        w = self.width(text, size, tracking)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        parts, cx = [], x
        for c in text:
            g = self._g(c)
            pen = SVGPathPen(self.gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
            self.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            d = pen.getCommands()
            if d:
                parts.append(d)
            cx += self.hmtx[g][0] * s + tracking * size
        return " ".join(parts)


BOLD = Face(os.path.join(FONT_DIR, "Inter-Bold.ttf"))
SEMI = Face(os.path.join(FONT_DIR, "Inter-SemiBold.ttf"))
MED = Face(os.path.join(FONT_DIR, "Inter-Medium.ttf"))
REG = Face(os.path.join(FONT_DIR, "Inter-Regular.ttf"))
MONO = Face(os.path.join(FONT_DIR, "JetBrainsMono-Medium.ttf"))
MONOB = Face(os.path.join(FONT_DIR, "JetBrainsMono-Bold.ttf"))


def T(face, text, x, y, size, fill, anchor="start", tracking=0.0, opacity=None, extra=""):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<path d="{face.path(text, x, y, size, anchor, tracking)}" fill="{fill}"{op}{extra}/>'


THEMES = {
    "dark": dict(
        bg="#0B0F19", panel="#0F1522", panel2="#141B2B",
        border="rgba(255,255,255,0.09)", border2="rgba(255,255,255,0.14)",
        ink="#F1F5F9", ink2="#A3B0C2", ink3="#6B7A90",
        grid="#1C2433", track="rgba(42,232,109,0.10)",
        accent="#2AE86D", accent2="#22D3EE", accent3="#60A5FA", accent4="#FBBF24",
        bar="#19B058", name1="#FFFFFF", name2="#A7F3C6",
        glowA="#2AE86D", glowB="#0A66C2", glowC="#22D3EE", glowOp="0.72",
        dot="rgba(255,255,255,0.10)", chipbg="rgba(255,255,255,0.04)",
        btnText="#0B0F19", iconTint="rgba(42,232,109,0.10)",
    ),
    "light": dict(
        bg="#FFFFFF", panel="#F8FAFC", panel2="#F1F5F9",
        border="rgba(15,23,42,0.10)", border2="rgba(15,23,42,0.16)",
        ink="#0F172A", ink2="#475569", ink3="#64748B",
        grid="#E2E8F0", track="rgba(22,163,74,0.12)",
        accent="#16A34A", accent2="#0891B2", accent3="#2563EB", accent4="#D97706",
        bar="#16A34A", name1="#0F172A", name2="#166534",
        glowA="#86EFAC", glowB="#93C5FD", glowC="#A5F3FC", glowOp="0.55",
        dot="rgba(15,23,42,0.10)", chipbg="rgba(15,23,42,0.03)",
        btnText="#FFFFFF", iconTint="rgba(22,163,74,0.10)",
    ),
}


def svg(w, h, body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
        f"<defs>{defs}</defs>{body}</svg>"
    )


def write(name, theme, content, out=None):
    out = out or DEFAULT_OUT
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"{name}-{theme}.svg"), "w", encoding="utf-8") as fh:
        fh.write(content)


def card(t, w, h, rx=24, fill=None, stroke=None, id_=""):
    fill = fill or t["panel"]
    stroke = stroke or t["border"]
    idd = f' id="{id_}"' if id_ else ""
    return f'<rect{idd} x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'


def dotgrid(t, id_="dg"):
    return (
        f'<pattern id="{id_}" width="26" height="26" patternUnits="userSpaceOnUse">'
        f'<circle cx="1.5" cy="1.5" r="1.2" fill="{t["dot"]}"/></pattern>'
    )


def fmt_int(n):
    return f"{n:,}"


# ──────────────────────────────────────────────────────────────────────────────
# Glass + 3D primitives (v2 design language)
# ──────────────────────────────────────────────────────────────────────────────
GLASS = {
    "dark": dict(fill="rgba(255,255,255,0.035)", tile="rgba(255,255,255,0.06)", edgeHi="rgba(255,255,255,0.42)",
                 edgeLo="rgba(255,255,255,0.07)", hi="rgba(255,255,255,0.75)", orbOp="0.58",
                 extrude="#0B3B22", extrudeEdge="#19B058", shine="rgba(255,255,255,0.55)"),
    "light": dict(fill="rgba(255,255,255,0.58)", tile="rgba(255,255,255,0.72)", edgeHi="rgba(15,23,42,0.22)",
                  edgeLo="rgba(15,23,42,0.05)", hi="rgba(255,255,255,1)", orbOp="0.62",
                  extrude="#A7F3C6", extrudeEdge="#86EFAC", shine="rgba(255,255,255,0.9)"),
}
for _k, _v in GLASS.items():
    THEMES[_k].update({f"g_{kk}": vv for kk, vv in _v.items()})


def default_orbs(t, w, h):
    r = min(w, h)
    return [
        (t["glowA"], w * 0.08, h * 0.95, r * 0.42, 60, -30, 16),
        (t["glowB"], w * 0.92, h * 0.05, r * 0.5, -70, 40, 21),
        (t["glowC"], w * 0.55, h * 1.1, r * 0.34, 40, -30, 18),
    ]


def glass_card(t, w, h, rx=24, orbs=None, uid="g", grid=True, blur=48, intensity=1.0):
    """A frosted-glass card with its own drifting aurora orbs behind the glass.

    Returns (defs, body). Put defs inside <defs>, body first in the drawing.
    """
    orbs = default_orbs(t, w, h) if orbs is None else orbs
    orb_op = f"{float(t['g_orbOp']) * intensity:.2f}"
    d = [
        f'<clipPath id="{uid}-clip"><rect x="0" y="0" width="{w}" height="{h}" rx="{rx}"/></clipPath>',
        f'<filter id="{uid}-blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{blur}"/></filter>',
        f'<linearGradient id="{uid}-bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["g_edgeHi"]}"/>'
        f'<stop offset="0.45" stop-color="{t["g_edgeLo"]}"/><stop offset="1" stop-color="{t["g_edgeHi"]}"/></linearGradient>',
        f'<linearGradient id="{uid}-hl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["g_hi"]}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{t["g_hi"]}"/><stop offset="1" stop-color="{t["g_hi"]}" stop-opacity="0"/></linearGradient>',
        dotgrid(t, f"{uid}-dg"),
    ]
    b = [f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{rx}" fill="{t["panel"]}"/>',
         f'<g clip-path="url(#{uid}-clip)">']
    for col, cx, cy, r, dx, dy, dur in orbs:
        b.append(
            f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{col}" opacity="{orb_op}" filter="url(#{uid}-blur)">'
            f'<animate attributeName="cx" values="{cx:.0f};{cx+dx:.0f};{cx:.0f}" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>'
            f'<animate attributeName="cy" values="{cy:.0f};{cy+dy:.0f};{cy:.0f}" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>'
            f'</circle>'
        )
    if grid:
        b.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}-dg)"/>')
    b.append(f'<rect width="{w}" height="{h}" fill="{t["g_fill"]}"/>')
    b.append("</g>")
    b.append(f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{rx}" fill="none" stroke="url(#{uid}-bd)"/>')
    b.append(f'<rect x="{rx}" y="1" width="{w-2*rx}" height="1" fill="url(#{uid}-hl)"/>')
    return "".join(d), "".join(b)


def glass_tile(t, x, y, w, h, rx, uid):
    """A smaller frosted tile that sits on top of a glass card (uses the card's gradients)."""
    return (f'<rect x="{x+0.5:.1f}" y="{y+0.5:.1f}" width="{w-1:.1f}" height="{h-1:.1f}" rx="{rx}" fill="{t["g_tile"]}" stroke="url(#{uid}-bd)"/>'
            f'<rect x="{x+rx:.1f}" y="{y+1:.1f}" width="{w-2*rx:.1f}" height="1" fill="url(#{uid}-hl)" opacity="0.7"/>')


ISO_C, ISO_S = 0.8660254, 0.5


def iso(x, y, z=0.0):
    return (x - y) * ISO_C, (x + y) * ISO_S - z


def iso_prism(ox, oy, x, y, w, d, h, top, left, right, opacity=1.0, stroke=None, extra=""):
    """An isometric box with its base corner at grid (x, y), footprint w×d, height h."""
    def P(px, py, pz):
        ix, iy = iso(px, py, pz)
        return f"{ox+ix:.1f},{oy+iy:.1f}"
    A, B, C, D = P(x, y, h), P(x + w, y, h), P(x + w, y + d, h), P(x, y + d, h)
    B0, C0, D0 = P(x + w, y, 0), P(x + w, y + d, 0), P(x, y + d, 0)
    st = f' stroke="{stroke}" stroke-width="0.8" stroke-linejoin="round"' if stroke else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return (f'<g{op}{extra}>'
            f'<polygon points="{D} {C} {C0} {D0}" fill="{left}"{st}/>'
            f'<polygon points="{B} {C} {C0} {B0}" fill="{right}"{st}/>'
            f'<polygon points="{A} {B} {C} {D}" fill="{top}"{st}/>'
            f'</g>')


def shade(hexcol, k):
    """Darken (k<1) or lighten (k>1) a hex colour."""
    hexcol = hexcol.lstrip("#")
    r, g, b = (int(hexcol[i:i+2], 16) for i in (0, 2, 4))
    f = lambda v: max(0, min(255, int(round(v * k if k <= 1 else v + (255 - v) * (k - 1)))))
    return f"#{f(r):02X}{f(g):02X}{f(b):02X}"
