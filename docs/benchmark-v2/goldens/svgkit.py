"""Small SVG kit for hand-placed technical figures: Helvetica / Menlo text measured with PIL,
house-palette shapes, orthogonal arrows with rounded bends, and PNG + PDF output via rsvg-convert."""

import subprocess
from html import escape

from PIL import ImageFont

INK, MUTED, FAINT, GRID = "#1f2328", "#57606a", "#8c959f", "#d0d7de"

FONTS = {
    "r": ("/System/Library/Fonts/Helvetica.ttc", 0, "Helvetica", "normal"),
    "b": ("/System/Library/Fonts/Helvetica.ttc", 1, "Helvetica", "bold"),
    "m": ("/System/Library/Fonts/Menlo.ttc", 0, "Menlo", "normal"),
}
_loaded = {}


def width(s, kind="r", size=15):
    if (kind, size) not in _loaded:
        path, index, *_ = FONTS[kind]
        _loaded[kind, size] = ImageFont.truetype(path, size, index=index)
    return _loaded[kind, size].getlength(s)


def block_height(rows):
    return sum(size * 1.43 for _, _, size, _ in rows)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h, self.items, self.heads = w, h, [], set()

    def text(self, x, y, s, size=15, kind="r", color=INK, anchor="start"):
        _, _, family, weight = FONTS[kind]
        self.items.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" '
                          f'font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')

    def lines(self, x, top, rows, anchor="start"):
        """rows: (text, kind, size, color). Returns the y just below the block."""
        y = top
        for s, kind, size, color in rows:
            y += size * 1.05
            self.text(x, y, s, size, kind, color, anchor)
            y += size * 0.38
        return y

    def rect(self, x, y, w, h, fill, stroke, r=10, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def panel(self, x, y, w, h, band_fill, stroke, body_fill, band_h=48, r=12, sw=1.8):
        """A container whose title band is filled; returns the band's bottom y."""
        self.rect(x, y, w, h, body_fill, stroke, r, sw)
        self.items.append(f'<path d="M{x},{y + band_h} L{x},{y + r} A{r},{r} 0 0 1 {x + r},{y} L{x + w - r},{y} '
                          f'A{r},{r} 0 0 1 {x + w},{y + r} L{x + w},{y + band_h} Z" fill="{band_fill}" '
                          f'stroke="{stroke}" stroke-width="{sw}"/>')
        return y + band_h

    def pill(self, x_right, cy, s, fill, color, size=12):
        w = width(s, "b", size) + 18
        self.rect(x_right - w, cy - 11, w, 22, fill, color, r=11, sw=1.2)
        self.text(x_right - w / 2, cy + 4, s, size, "b", color, "middle")

    def cylinder(self, x, y, w, h, fill, stroke, dash=None, ry=8, sw=1.5):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        body = (f"M{x},{y + ry} L{x},{y + h - ry} A{w / 2},{ry} 0 0 0 {x + w},{y + h - ry} "
                f"L{x + w},{y + ry} A{w / 2},{ry} 0 0 0 {x},{y + ry} Z")
        self.items.append(f'<path d="{body}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
        self.items.append(f'<ellipse cx="{x + w / 2}" cy="{y + ry}" rx="{w / 2}" ry="{ry}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def hexagon(self, x, y, w, h, fill, stroke, k=22, sw=1.6):
        pts = [(x + k, y), (x + w - k, y), (x + w, y + h / 2), (x + w - k, y + h), (x + k, y + h), (x, y + h / 2)]
        self.items.append(f'<polygon points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{sw}"/>')

    def badge(self, cx, cy, s, fill, r=12, size=13):
        self.items.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>')
        self.text(cx, cy + size * 0.36, s, size, "b", "white", "middle")

    def arrow(self, pts, color, sw=2.0, dash=None, head=True, tail=False, bend=10):
        """Polyline through pts with rounded bends; arrowhead at the end (and optionally the start)."""
        path = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for (x0, y0), (x1, y1), (x2, y2) in zip(pts, pts[1:], pts[2:]):
            r1 = min(bend, abs(x1 - x0) + abs(y1 - y0)) / max(abs(x1 - x0) + abs(y1 - y0), 1e-9)
            r2 = min(bend, abs(x2 - x1) + abs(y2 - y1)) / max(abs(x2 - x1) + abs(y2 - y1), 1e-9)
            a = (x1 - (x1 - x0) * r1, y1 - (y1 - y0) * r1)
            b = (x1 + (x2 - x1) * r2, y1 + (y2 - y1) * r2)
            path += f" L{a[0]:.1f},{a[1]:.1f} Q{x1:.1f},{y1:.1f} {b[0]:.1f},{b[1]:.1f}"
        path += f" L{pts[-1][0]:.1f},{pts[-1][1]:.1f}"
        self.heads.add(color)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = (f' marker-end="url(#h{color[1:]})"' if head else "") + (f' marker-start="url(#h{color[1:]})"' if tail else "")
        self.items.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}" '
                          f'stroke-linejoin="round"{d}{m}/>')

    def hop(self, x, y, color, sw=2.0, r=6, bg="white"):
        """A horizontal line jumping over a vertical one at (x, y): erase a short gap, draw a bump."""
        self.items.append(f'<path d="M{x - r - 1},{y} L{x + r + 1},{y}" stroke="{bg}" stroke-width="{sw + 2}"/>')
        self.items.append(f'<path d="M{x - r},{y} A{r},{r} 0 0 1 {x + r},{y}" fill="none" stroke="{color}" stroke-width="{sw}"/>')

    def tag(self, x, y, s, color, size=13, kind="r", anchor="middle", bg="white"):
        """A label sitting on a line, with a backing so the line does not cut through the text."""
        w = width(s, kind, size) + 10
        x0 = {"middle": x - w / 2, "start": x - 5, "end": x - w + 5}[anchor]
        self.items.append(f'<rect x="{x0:.1f}" y="{y - size + 1:.1f}" width="{w:.1f}" height="{size + 6}" fill="{bg}"/>')
        self.text(x, y + 2, s, size, kind, color, anchor)

    def save(self, stem, zoom=2):
        heads = "".join(
            f'<marker id="h{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" '
            f'markerUnits="strokeWidth" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
            for c in sorted(self.heads))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}"><defs>{heads}</defs>'
               f'<rect width="{self.w}" height="{self.h}" fill="white"/>\n' + "\n".join(self.items) + "\n</svg>")
        # the SVG is only an intermediate: keep the final PNG and PDF
        subprocess.run(["rsvg-convert", "-z", str(zoom), "-o", f"{stem}.png"], input=svg.encode(), check=True)
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", f"{stem}.pdf"], input=svg.encode(), check=True)
        return f"{stem}.png", (self.w * zoom, self.h * zoom)
