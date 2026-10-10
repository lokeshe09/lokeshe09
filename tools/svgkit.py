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
