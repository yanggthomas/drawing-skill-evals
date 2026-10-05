"""Swimlane renderer: rows = numbered steps, columns = owner lanes, plus an optional ledger lane.

Generalized from the no-skill G2 figure (b22ede75). A figure is a SPEC dict (see g2_ppo_step.py);
render(SPEC, out_png) lays it out deterministically: a row is as tall as its tallest wrapped cell,
cells in a row are top-aligned, text is left-aligned, and cross-lane arrows are horizontal.
"""

import math
import subprocess

from PIL import Image, ImageDraw, ImageFont

INK, MUTED, GRID = "#1f2328", "#57606a", "#d0d7de"
BADGE = "#3b6fb6"
COND = "#9a6700"
EMPH_FILL, EMPH_BORDER = "#fff7d6", "#b08800"
ARROWS = {  # kind: color, width, dashed, head, y offset from the top of the cell row
    "call": (INK, 2, False, 11, 20),
    "ret": (MUTED, 2, True, 11, 44),
    "stream": ("#c77700", 2, True, 11, 40),
    "weights": ("#d9480f", 8, False, 20, 34),
}
LANE_GAP, MARGIN, TOP, ROWPAD, BADGE_W = 60, 30, 300, 18, 46


def font_path(pattern):
    path = subprocess.run(["fc-match", "-f", "%{file}", pattern], capture_output=True, text=True).stdout
    return path or f"/usr/share/fonts/truetype/dejavu/{pattern.replace(' ', '').replace(':bold', '-Bold')}.ttf"


def fonts():
    sans, bold, mono = font_path("DejaVu Sans"), font_path("DejaVu Sans:bold"), font_path("DejaVu Sans Mono")
    f = ImageFont.truetype
    return {
        "n": f(sans, 15), "b": f(bold, 15), "m": f(mono, 13), "h": f(bold, 17),
        "t": f(bold, 28), "s": f(sans, 15), "step": f(bold, 16),
    }


def wrap(d, text, font, width):
    out = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            trial = f"{cur} {word}".strip() if cur else word
            if d.textlength(trial, font=font) <= width:
                cur = trial
            else:
                if cur:
                    out.append(cur)
                cur = word
        out.append(cur)
    return out


def layout(d, F, lines, width):
    style = {"b": (F["b"], INK, 21), "n": (F["n"], INK, 20), "m": (F["m"], MUTED, 18), "i": (F["n"], MUTED, 20)}
    res = []
    for kind, text in lines:
        font, color, lh = style[kind]
        res += [(font, color, lh, s) for s in wrap(d, text, font, width)]
    return res


def box_height(d, F, lines, width):
    return sum(lh for *_, lh, _ in layout(d, F, lines, width - 24)) + 20


def draw_box(d, F, x0, y0, x1, lines, fill, border, bw=2):
    lay = layout(d, F, lines, x1 - x0 - 24)
    h = sum(l[2] for l in lay) + 20
    d.rounded_rectangle([x0, y0, x1, y0 + h], radius=10, fill=fill, outline=border, width=bw)
    y = y0 + 10
    for font, color, lh, s in lay:
        d.text((x0 + 12, y), s, font=font, fill=color)
        y += lh
    return h


def arrow(d, x0, y0, x1, y1, color=INK, width=2, dashed=False, head=11):
    if dashed:
        n = int(math.hypot(x1 - x0, y1 - y0) // 10)
        for i in range(0, n, 2):
            a, b = i / n, min((i + 1) / n, 1)
            d.line([x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b], fill=color, width=width)
    else:
        d.line([x0, y0, x1, y1], fill=color, width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    p1 = (x1 - head * math.cos(ang - 0.4), y1 - head * math.sin(ang - 0.4))
    p2 = (x1 - head * math.cos(ang + 0.4), y1 - head * math.sin(ang + 0.4))
    d.polygon([(x1, y1), p1, p2], fill=color)


def render(spec, out_png):
    F = fonts()
    scratch = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lanes, x = {}, MARGIN
    for lane in spec["lanes"]:
        lanes[lane["key"]] = dict(lane, x0=x, x1=x + lane["width"])
        x += lane["width"] + LANE_GAP
    W = x - LANE_GAP + MARGIN
    ctl = spec["lanes"][0]["key"]          # the controller lane carries the step badges
    ledger = next((l["key"] for l in spec["lanes"] if l.get("ledger")), None)
    owners = [l["key"] for l in spec["lanes"] if l["key"] not in (ctl, ledger)]

    rows, y = [], TOP
    for s in spec["steps"]:
        hdr = 30 + (22 if s.get("cond") else 0)
        c = lanes[ctl]
        hs = [hdr + box_height(scratch, F, s[ctl], c["x1"] - c["x0"] - 60)]
        hs += [hdr + box_height(scratch, F, s[k], lanes[k]["x1"] - lanes[k]["x0"]) for k in owners if k in s]
        if ledger:
            hs.append(hdr + 30 * max(1, len(s.get(ledger, []))) + 10)
        h = max(hs) + ROWPAD
        rows.append((y, h))
        y += h
    H = y + 220

    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((MARGIN, 22), spec["title"], font=F["t"], fill=INK)
    for i, line in enumerate(spec.get("subtitle", [])):
        d.text((MARGIN, 64 + 24 * i), line, font=F["s"], fill=MUTED)

    lx, ly = MARGIN, 124
    d.rounded_rectangle([lx, ly, W - MARGIN, ly + 60], radius=8, outline=GRID, width=1, fill="#fbfcfd")
    cx = lx + 20
    for kind, label, bold in spec["legend"]:
        color, width, dashed, head, _ = ARROWS[kind]
        if kind == "ret":
            arrow(d, cx + 70, ly + 20, cx, ly + 20, color=color, width=width, dashed=dashed, head=head)
        else:
            arrow(d, cx, ly + 20, cx + 70, ly + 20, color=color, width=min(width, 6), dashed=dashed, head=min(head, 16))
        font = F["b"] if bold else F["n"]
        d.text((cx + 85, ly + 11), label, font=font, fill=color if bold else INK)
        cx += 85 + d.textlength(label, font=font) + 60
    if spec.get("legend_note"):
        d.text((lx + 20, ly + 36), spec["legend_note"], font=F["m"], fill=MUTED)

    for key, ln in lanes.items():
        x0, x1 = ln["x0"], ln["x1"]
        d.rectangle([x0 - 10, 200, x1 + 10, H - 200], fill="#f7faff" if key == ctl else "#fcfcfd", outline=GRID)
        d.rectangle([x0 - 10, 200, x1 + 10, 286], fill=ln["fill"], outline=ln["ink"], width=2)
        d.text((x0, 208), ln["title"], font=F["h"], fill=ln["ink"])
        yy = 234
        for s in wrap(d, ln.get("subtitle", ""), F["m"], x1 - x0):
            d.text((x0, yy), s, font=F["m"], fill=INK)
            yy += 17

    if spec.get("lane_note"):
        note = spec["lane_note"]
        d.text((lanes[note["lane"]]["x0"] + 10, H - 192), note["text"], font=F["n"], fill=note["color"])

    chips = spec.get("chip_colors", [])
    for s, (ry, rh) in zip(spec["steps"], rows):
        d.line([20, ry + rh - 6, W - 20, ry + rh - 6], fill=GRID, width=1)
        c = lanes[ctl]
        dx0, dx1 = c["x0"], c["x1"]
        d.ellipse([dx0, ry + 6, dx0 + 34, ry + 40], fill=BADGE)
        tw = d.textlength(s["n"], font=F["step"])
        d.text((dx0 + 17 - tw / 2, ry + 13), s["n"], font=F["step"], fill="white")
        d.text((dx0 + BADGE_W, ry + 12), s["t"], font=F["h"], fill=INK)
        hdr = 30
        if s.get("cond"):
            d.text((dx0 + BADGE_W, ry + 36), s["cond"], font=F["n"], fill=COND)
            hdr += 22
        by = ry + hdr + 14
        emph, bold = s.get("emph", []), s.get("bold", [])
        boxes = {}
        h = draw_box(d, F, dx0 + BADGE_W, by, dx1, s[ctl],
                     EMPH_FILL if ctl in emph else c["fill"], EMPH_BORDER if ctl in emph else c["ink"],
                     bw=3 if ctl in emph or ctl in bold else 2)
        boxes[ctl] = (dx0 + BADGE_W, by, dx1, by + h)
        for k in owners:
            if k in s:
                ln = lanes[k]
                hh = draw_box(d, F, ln["x0"], by, ln["x1"], s[k], ln["fill"], ln["ink"], bw=3 if k in bold else 2)
                boxes[k] = (ln["x0"], by, ln["x1"], by + hh)
        for ar in s.get("arrows", []):
            kind = ar[0]
            color, width, dashed, head, dy = ARROWS[kind]
            src, dst = (ctl, ar[1]) if len(ar) == 2 else (ar[1], ar[2])
            a, b = boxes[src], boxes[dst]
            yy = by + dy
            if kind == "ret":
                arrow(d, b[0], yy, a[2], yy, color=color, width=width, dashed=dashed, head=head)
            elif kind == "weights":
                arrow(d, a[2] + 2, yy, b[0] - 2, yy, color=color, width=width, head=head)
                if len(ar) > 3:
                    d.text((a[2] + 6, yy + 12), ar[3], font=F["b"], fill=color)
            else:
                arrow(d, a[2], yy, b[0], yy, color=color, width=width, dashed=dashed, head=head)
        if ledger:
            bx0, bx1 = lanes[ledger]["x0"], lanes[ledger]["x1"]
            cy = by
            for text, ci in s.get(ledger, []):
                if text.startswith(("meta", "(", "returns", "—")):
                    d.text((bx0 + 4, cy + 5), text, font=F["m"], fill=MUTED)
                else:
                    col = (chips[ci] if ci < len(chips) else "") or "#dbe7f7"
                    tw = d.textlength(text, font=F["m"])
                    d.rounded_rectangle([bx0, cy, min(bx0 + tw + 18, bx1), cy + 24], radius=6, fill=col, outline="#8c959f")
                    d.text((bx0 + 9, cy + 4), text, font=F["m"], fill=INK)
                cy += 30

    if spec.get("loop"):
        ly0, ly1 = rows[0][0] + 22, rows[-1][0] + 22
        d.line([16, ly1, 8, ly1, 8, ly0, 16, ly0], fill=BADGE, width=3)
        arrow(d, 8, ly0, 30, ly0, color=BADGE, width=3)

    fy = H - 160
    d.text((MARGIN, fy), spec.get("footer_title", "Reading the flow"), font=F["h"], fill=INK)
    yy = fy + 28
    for note in spec.get("footer", []):
        for s in wrap(d, note, F["n"], W - 80):
            d.text((MARGIN, yy), s, font=F["n"], fill=INK)
            yy += 21

    img.save(out_png)
    img.save(out_png.rsplit(".", 1)[0] + ".pdf", resolution=200)
    return img.size
