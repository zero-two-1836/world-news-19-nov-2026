#!/usr/bin/env python3
"""Render the 19 Nov 2026 world-news poster (1024x1024) with PIL.

Round 6 rebuild. Layout is a premium newspaper front page: navy
masthead with edition marks, a red kicker with flanking rules,
three hero cards with fully drawn illustrated scenes and serif
display headlines, a 3x3 grid of the remaining stories with colour
accent bars, a gold-ruled numbers strip and a source footer. All
12 stories from NEWS.md are present and legible.

Round 6 changes: the whole poster is rendered supersampled (SS=2)
through the SD draw proxy and downscaled with LANCZOS, so edges
and text come out clean and anti-aliased; the hero scenes are
richer (neon VICE CITY sign and a second car, an APEC SUMMIT
banner in place of the check badge, a denser IPO candlestick
chart with an area fill under the trend line); the cyclone and
bridge grid icons are redrawn to read unmistakably; the numbers
strip uses DejaVu Serif Bold so the euro sign cannot be misread.
Pillow is the only dependency; output is deterministic.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
SS = 2  # supersampling factor: draw at 2048, downscale to 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "entry.png")

# ---- palette ---------------------------------------------------------
NAVY = (13, 27, 56)
NAVY_SOFT = (30, 50, 92)
GOLD = (242, 193, 78)
GOLD_DEEP = (214, 164, 48)
RED = (176, 58, 46)
RED_DARK = (148, 44, 34)
PAPER = (249, 245, 234)
CARD = (255, 255, 255)
INK = (26, 26, 26)
GRAY = (94, 94, 94)
BORDER = (212, 206, 190)
SHADOW = (228, 223, 208)
GREEN = (46, 160, 90)

FDIR = "/usr/share/fonts/truetype"
SERIF_D = os.path.join(FDIR, "noto", "NotoSerifDisplay-Black.ttf")
SERIF_B = os.path.join(FDIR, "noto", "NotoSerifDisplay-Bold.ttf")
SERIF = os.path.join(FDIR, "dejavu", "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FDIR, "dejavu", "DejaVuSans-Bold.ttf")
SANS = os.path.join(FDIR, "dejavu", "DejaVuSans.ttf")
MONO_B = os.path.join(FDIR, "dejavu", "DejaVuSansMono-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size * SS)


class SD:
    """ImageDraw proxy that scales logical coordinates by SS.

    Every painter below works in the poster's logical 1024x1024
    space; the proxy maps coordinates, line widths and radii onto
    the supersampled canvas, and textlength back into logical
    units, so layout arithmetic is unchanged.
    """

    def __init__(self, draw, s):
        self._d = draw
        self._s = s

    def _xy(self, xy):
        s = self._s
        if xy and isinstance(xy[0], (list, tuple)):
            return [(x * s, y * s) for x, y in xy]
        return [v * s for v in xy]

    def _box(self, box):
        s = self._s
        return [box[0] * s, box[1] * s, box[2] * s, box[3] * s]

    def line(self, xy, fill=None, width=1, joint=None):
        self._d.line(self._xy(xy), fill=fill,
                     width=max(1, int(width * self._s)), joint=joint)

    def rectangle(self, box, fill=None, outline=None, width=1):
        self._d.rectangle(self._box(box), fill=fill, outline=outline,
                          width=max(1, int(width * self._s)))

    def rounded_rectangle(self, box, radius=0, fill=None, outline=None,
                          width=1):
        self._d.rounded_rectangle(self._box(box),
                                  radius=radius * self._s, fill=fill,
                                  outline=outline,
                                  width=max(1, int(width * self._s)))

    def ellipse(self, box, fill=None, outline=None, width=1):
        self._d.ellipse(self._box(box), fill=fill, outline=outline,
                        width=max(1, int(width * self._s)))

    def polygon(self, pts, fill=None, outline=None):
        self._d.polygon(self._xy(pts), fill=fill, outline=outline)

    def arc(self, box, start, end, fill=None, width=1):
        self._d.arc(self._box(box), start, end, fill=fill,
                    width=max(1, int(width * self._s)))

    def text(self, xy, text, font=None, fill=None, anchor=None):
        self._d.text((xy[0] * self._s, xy[1] * self._s), text,
                     font=font, fill=fill, anchor=anchor)

    def textlength(self, text, font=None):
        return self._d.textlength(text, font=font) / self._s


def fit_font(path, size, max_w, draw, text):
    """Largest size <= `size` for which `text` fits `max_w`."""
    while size > 10:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(path, 10)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for y in range(y0, y1):
        # a 1-logical-pixel-tall rectangle, so the supersampling
        # proxy fills every real row (a hairline would skip rows)
        draw.rectangle([x0, y, x1, y + 1],
                       fill=lerp(top, bottom, (y - y0) / h))


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def diamond(draw, cx, cy, r, fill):
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)],
                 fill=fill)


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ---- hero illustrations (drawn fresh for round 4) --------------------
def hero_vice_city(draw, box):
    """Synthwave Vice City: denser star field, haloed slit sun,
    layered skyline with a spire tower, a neon VICE CITY sign,
    palms, and two cars cruising the neon road."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(draw, box, (58, 20, 84), (238, 96, 62))
    rnd = random.Random(19)
    # star field in the upper sky, a few with sparkle crosses
    for _ in range(44):
        sx = x0 + rnd.randint(4, w - 4)
        sy = y0 + rnd.randint(4, int(h * 0.30))
        r = rnd.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r],
                     fill=(255, 235, 200))
        if r == 2:
            draw.line([(sx - 4, sy), (sx + 4, sy)], fill=(255, 235, 200),
                      width=1)
            draw.line([(sx, sy - 4), (sx, sy + 4)], fill=(255, 235, 200),
                      width=1)
    # big slit sun with a thin halo ring
    sx, sy, sr = x0 + w * 0.66, y0 + h * 0.36, 48
    draw.ellipse([sx - sr - 7, sy - sr - 7, sx + sr + 7, sy + sr + 7],
                 outline=(255, 170, 90), width=3)
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 214, 90))
    for yy, hh in [(sy - 8, 4), (sy + 6, 5), (sy + 20, 6), (sy + 34, 7)]:
        draw.rectangle([sx - sr, yy, sx + sr, yy + hh], fill=(238, 96, 62))
    # skyline, two depths, one tower with a spire + beacon
    base = y1 - 34
    for col, hmin, hmax in (((44, 18, 66), 40, 112), ((28, 10, 48), 22, 66)):
        bx = x0
        while bx < x1 - 8:
            bw = rnd.randint(18, 32)
            bh = rnd.randint(hmin, hmax)
            draw.rectangle([bx, base - bh, bx + bw, base], fill=col)
            for wy in range(base - bh + 8, base - 6, 12):
                for wx in range(bx + 4, bx + bw - 3, 9):
                    if rnd.random() < 0.55:
                        draw.rectangle([wx, wy, wx + 3, wy + 4],
                                       fill=(255, 205, 90))
            bx += bw + rnd.randint(2, 8)
    spire_x = x0 + int(w * 0.30)
    draw.rectangle([spire_x - 9, base - 132, spire_x + 9, base],
                   fill=(44, 18, 66))
    draw.polygon([(spire_x - 9, base - 132), (spire_x + 9, base - 132),
                  (spire_x, base - 158)], fill=(44, 18, 66))
    draw.ellipse([spire_x - 3, base - 164, spire_x + 3, base - 158],
                 fill=(255, 80, 90))
    # neon sign on a front building, naming the city in the picture
    sg_w, sg_x, sg_y = 78, x0 + 8, base - 88
    draw.rectangle([sg_x, sg_y, sg_x + sg_w, sg_y + 22], fill=(26, 6, 44))
    draw.rectangle([sg_x, sg_y, sg_x + sg_w, sg_y + 22],
                   outline=(255, 80, 160), width=2)
    draw.text((sg_x + sg_w // 2, sg_y + 4), "VICE CITY",
              font=font(SANS_B, 12), fill=(255, 140, 210), anchor="ma")
    # palms
    for px, ph in [(x0 + 30, 46), (x1 - 36, 54), (x0 + int(w * 0.50), 38)]:
        draw.line([(px, base), (px + 4, base - ph)], fill=(24, 8, 40),
                  width=4)
        for dx, dy in [(-16, -8), (-10, -16), (0, -18), (10, -16), (16, -8)]:
            draw.arc([px + dx - 8, base - ph + dy - 6,
                      px + dx + 8, base - ph + dy + 6],
                     200, 340, fill=(24, 8, 40), width=3)
    # neon road with a hot-pink car, its headlight beam, and a
    # second smaller teal car further down the road
    draw.rectangle([x0, base, x1, y1], fill=(20, 8, 36))
    car_x, car_y = x0 + int(w * 0.42), y1 - 24
    draw.rounded_rectangle([car_x, car_y, car_x + 52, car_y + 12], radius=5,
                           fill=(255, 80, 160))
    draw.polygon([(car_x + 10, car_y), (car_x + 18, car_y - 9),
                  (car_x + 36, car_y - 9), (car_x + 44, car_y)],
                 fill=(255, 140, 200))
    draw.ellipse([car_x + 8, car_y + 8, car_x + 16, car_y + 16],
                 fill=(40, 40, 48))
    draw.ellipse([car_x + 36, car_y + 8, car_x + 44, car_y + 16],
                 fill=(40, 40, 48))
    draw.rectangle([car_x + 52, car_y + 3, car_x + 62, car_y + 7],
                   fill=(255, 240, 150))
    draw.polygon([(car_x + 62, car_y + 3), (car_x + 94, car_y - 2),
                  (car_x + 94, car_y + 12), (car_x + 62, car_y + 7)],
                 fill=(255, 224, 130))
    c2x, c2y = x0 + int(w * 0.76), y1 - 19
    draw.rounded_rectangle([c2x, c2y, c2x + 38, c2y + 9], radius=4,
                           fill=(64, 200, 220))
    draw.polygon([(c2x + 7, c2y), (c2x + 13, c2y - 7),
                  (c2x + 27, c2y - 7), (c2x + 32, c2y)],
                 fill=(150, 230, 240))
    draw.ellipse([c2x + 6, c2y + 6, c2x + 12, c2y + 12], fill=(40, 40, 48))
    draw.ellipse([c2x + 26, c2y + 6, c2x + 32, c2y + 12],
                 fill=(40, 40, 48))
    for dx in range(x0 + 6, x1 - 10, 26):
        draw.rectangle([dx, y1 - 10, dx + 14, y1 - 6], fill=(255, 80, 160))


def hero_shenzhen(draw, box):
    """Shenzhen summit: hazy skyline with a needle landmark tower,
    drifting clouds, three flags and a red carpet to the handshake."""
    x0, y0, x1, y1 = box
    w = x1 - x0
    vgrad(draw, box, (188, 208, 228), (240, 240, 234))
    rnd = random.Random(7)
    # soft clouds
    for cx, cy, cr in [(0.22, 0.16, 26), (0.78, 0.10, 30), (0.55, 0.22, 20)]:
        px, py = x0 + int(w * cx), y0 + int((y1 - y0) * cy)
        draw.ellipse([px - cr, py - cr // 2, px + cr, py + cr // 2],
                     fill=(255, 255, 255))
    # skyline
    base = y1 - 46
    bx = x0
    while bx < x1 - 10:
        bw = rnd.randint(22, 38)
        bh = rnd.randint(52, 112)
        col = (126 + rnd.randint(-14, 14), 136 + rnd.randint(-10, 10),
               148 + rnd.randint(-10, 10))
        draw.rectangle([bx, base - bh, bx + bw, base], fill=col)
        for wy in range(base - bh + 8, base - 8, 13):
            for wx in range(bx + 5, bx + bw - 4, 10):
                if rnd.random() < 0.5:
                    draw.rectangle([wx, wy, wx + 4, wy + 5],
                                   fill=(240, 244, 248))
        bx += bw + rnd.randint(3, 9)
    # needle landmark tower
    tx = x0 + int(w * 0.62)
    draw.polygon([(tx - 16, base), (tx - 6, base - 128),
                  (tx + 6, base - 128), (tx + 16, base)],
                 fill=(96, 106, 120))
    draw.line([(tx, base - 128), (tx, base - 150)], fill=(96, 106, 120),
              width=3)
    draw.ellipse([tx - 3, base - 154, tx + 3, base - 148], fill=(220, 40, 40))
    # ground + narrow red carpet
    draw.rectangle([x0, base, x1, y1], fill=(88, 96, 106))
    draw.polygon([(x0 + w // 2 - 28, y1), (x0 + w // 2 + 28, y1),
                  (x0 + w // 2 + 12, base), (x0 + w // 2 - 12, base)],
                 fill=(150, 30, 44))
    # three flag poles
    poles = [int(x0 + w * 0.18), int(x0 + w * 0.50), int(x0 + w * 0.82)]
    flag_w, flag_h = 52, 34
    fy = y0 + 16
    for px in poles:
        draw.line([(px, fy), (px, base)], fill=(60, 60, 60), width=3)
    fx = poles[0] + 2
    for i in range(7):
        draw.rectangle([fx, fy + i * 5, fx + flag_w, fy + i * 5 + 5],
                       fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    draw.rectangle([fx, fy, fx + 22, fy + 17], fill=(40, 60, 120))
    for sy in range(fy + 3, fy + 16, 5):
        for sx in range(fx + 3, fx + 20, 5):
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    fx = poles[1] + 2
    draw.rectangle([fx, fy, fx + flag_w, fy + flag_h], fill=(222, 32, 24))
    draw.polygon(star_points(fx + 10, fy + 9, 6, 2.5), fill=(255, 222, 0))
    for sx, sy in [(26, 6), (31, 11), (31, 17), (26, 21)]:
        draw.polygon(star_points(fx + sx, fy + sy, 3, 1.2),
                     fill=(255, 222, 0))
    fx = poles[2] + 2
    for i, col in enumerate([(255, 255, 255), (0, 90, 180), (220, 40, 40)]):
        draw.rectangle([fx, fy + i * 11, fx + flag_w, fy + (i + 1) * 11],
                       fill=col)
    # summit banner across the plaza, naming the event in the picture
    bn_w = 184
    bn_x = x0 + w // 2 - bn_w // 2
    bn_y = y1 - 30
    draw.rounded_rectangle([bn_x, bn_y, bn_x + bn_w, bn_y + 20], radius=4,
                           fill=(122, 22, 36))
    draw.text((x0 + w // 2, bn_y + 4), "APEC SUMMIT · SHENZHEN",
              font=font(SANS_B, 12), fill=(255, 226, 150), anchor="ma")


def hero_ipo(draw, box):
    """Anthropic IPO: navy terminal grid, ticker tape, huge $83,
    seven candlesticks over rising bars, an area fill under the
    gold trend line and its arrow."""
    x0, y0, x1, y1 = box
    w = x1 - x0
    draw.rectangle(box, fill=NAVY)
    for gx in range(x0 + 24, x1 - 10, 34):
        draw.line([(gx, y0), (gx, y1)], fill=(32, 56, 100), width=1)
    for gy in range(y0 + 16, y1 - 10, 30):
        draw.line([(x0, gy), (x1, gy)], fill=(32, 56, 100), width=1)
    # ticker tape with the day's three IPO numbers
    tape = "ANT $83.00 ▲ RAISES $81.3BN ▲ $1.4TN"
    f_tape = fit_font(MONO_B, 12, w - 24, draw, tape)
    draw.text((x0 + 12, y0 + 6), tape, font=f_tape, fill=GOLD)
    draw.line([(x0, y0 + 26), (x1, y0 + 26)], fill=(32, 56, 100), width=1)
    # big price, with the exchange label beside it (clear of the chart)
    f_big = font(SERIF_D, 62)
    draw.text((x0 + 16, y0 + 30), "$83", font=f_big, fill=GOLD)
    f_sub = font(SANS_B, 13)
    draw.text((x0 + 178, y0 + 58), "ANT · NASDAQ", font=f_sub,
              fill=(255, 255, 255))
    # candlesticks + bars; tops computed first for the area fill
    base = y1 - 14
    heights = [18, 30, 26, 42, 38, 56, 72]
    bw, gap = 24, 10
    bx = x0 + 16
    tops = []
    for hh in heights:
        tops.append((bx + bw // 2, base - hh - 10))
        bx += bw + gap
    pts = [(x, y - 4) for x, y in tops]
    # area fill under the trend line, behind the candles
    draw.polygon(pts + [(pts[-1][0], base - 12), (pts[0][0], base - 12)],
                 fill=(26, 48, 88))
    bx = x0 + 16
    for hh in heights:
        # candle body + wick
        cx = bx + bw // 2
        draw.line([(cx, base - hh - 10), (cx, base - hh + 8)],
                  fill=(120, 220, 150), width=2)
        draw.rectangle([bx, base - hh, bx + bw, base - hh + 16],
                       fill=GREEN)
        draw.rectangle([bx, base - 10, bx + bw, base], fill=(30, 90, 60))
        bx += bw + gap
    # trend line with arrow
    draw.line(pts, fill=GOLD, width=4, joint="curve")
    ex, ey = pts[-1]
    draw.polygon([(ex, ey - 10), (ex + 14, ey + 2), (ex - 2, ey + 8)],
                 fill=GOLD)


# ---- grid icons --------------------------------------------------------
def icon(draw, kind, box, bg):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=12, fill=bg)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    white = (255, 255, 255)
    if kind == "star":
        draw.polygon(star_points(cx, cy, 24, 10), fill=white)
        draw.arc([cx - 30, cy - 30, cx + 30, cy + 30], 300, 60,
                 fill=white, width=3)
    elif kind == "drop":
        draw.polygon([(cx, cy - 22), (cx + 15, cy + 4), (cx - 15, cy + 4)],
                     fill=white)
        draw.ellipse([cx - 15, cy - 4, cx + 15, cy + 22], fill=white)
    elif kind == "euro":
        f = font(SANS_B, 40)
        draw.text((cx - 13, cy - 26), "€", font=f, fill=white)
    elif kind == "bridge":
        # suspension bridge: two towers, sagging main cables,
        # suspenders and a deck
        deck = cy + 14
        for tx in (cx - 16, cx + 16):
            draw.line([(tx, cy - 16), (tx, deck)], fill=white, width=4)
        draw.line([(cx - 27, deck), (cx + 27, deck)], fill=white, width=4)
        draw.line([(cx - 27, cy + 0), (cx - 16, cy - 14)], fill=white,
                  width=3)
        draw.line([(cx - 16, cy - 14), (cx, cy + 5), (cx + 16, cy - 14)],
                  fill=white, width=3, joint="curve")
        draw.line([(cx + 16, cy - 14), (cx + 27, cy + 0)], fill=white,
                  width=3)
        for dx, top in ((-8, cy - 5), (0, cy + 5), (8, cy - 5)):
            draw.line([(cx + dx, top), (cx + dx, deck)], fill=white,
                      width=2)
        for px in (-22, 22):
            draw.line([(cx + px, deck), (cx + px, deck + 7)],
                      fill=white, width=3)
    elif kind == "waves":
        # cyclone spiral: swept concentric arcs around a calm eye
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=white)
        for r, a0 in ((8, 20), (13, 110), (18, 200), (23, 290)):
            draw.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 250,
                     fill=white, width=4)
    elif kind == "brush":
        draw.line([(cx - 16, cy + 16), (cx + 6, cy - 6)], fill=white,
                  width=6)
        draw.polygon([(cx + 6, cy - 6), (cx + 20, cy - 20),
                      (cx + 14, cy - 2)], fill=white)
    elif kind == "scales":
        draw.line([(cx, cy - 20), (cx, cy + 20)], fill=white, width=4)
        draw.line([(cx - 18, cy - 12), (cx + 18, cy - 12)], fill=white,
                  width=4)
        draw.arc([cx - 26, cy - 12, cx - 10, cy + 4], 0, 180, fill=white,
                 width=3)
        draw.arc([cx + 10, cy - 12, cx + 26, cy + 4], 0, 180, fill=white,
                 width=3)
        draw.line([(cx - 18, cy - 12), (cx - 18, cy + 2)], fill=white,
                  width=2)
        draw.line([(cx + 18, cy - 12), (cx + 18, cy + 2)], fill=white,
                  width=2)
    elif kind == "dome":
        draw.arc([cx - 18, cy - 16, cx + 18, cy + 12], 180, 360,
                 fill=white, width=5)
        draw.line([(cx - 20, cy - 2), (cx + 20, cy - 2)], fill=white,
                  width=4)
        for dx in (-14, -5, 5, 14):
            draw.line([(cx + dx, cy + 2), (cx + dx, cy + 18)], fill=white,
                      width=3)
        draw.line([(cx - 22, cy + 20), (cx + 22, cy + 20)], fill=white,
                  width=4)
    elif kind == "atom":
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=white)
        draw.ellipse([cx - 24, cy - 10, cx + 24, cy + 10], outline=white,
                     width=3)
        draw.ellipse([cx - 10, cy - 24, cx + 10, cy + 24], outline=white,
                     width=3)


HEROES = [
    ("LEAD · VICE CITY",
     "GAMERS ENTER VICE CITY AS GTA VI ROLLS OUT",
     "Rockstar's epic launches worldwide after a 13-year wait.",
     hero_vice_city),
    ("DIPLOMACY · SHENZHEN",
     "TRUMP, XI AND PUTIN SHAKE HANDS IN SHENZHEN",
     "Trilateral talks at the APEC summit; Ukraine on the agenda.",
     hero_shenzhen),
    ("MARKETS · IPO",
     "ANTHROPIC DEBUTS AT $83 IN THE BIGGEST IPO EVER",
     "$81.3bn raised — the largest stock market debut in history.",
     hero_ipo),
]

GRID = [
    ("SPACE", "VOYAGER 1 HITS ONE LIGHT-DAY OUT",
     "50 years on, the probe is 16 billion miles away.", "star",
     (24, 52, 96)),
    ("THE GULF", "U.S. AND IRAN TRADE FIRE AGAIN",
     "Tehran widens attacks to Kuwait and Bahrain.", "drop",
     (178, 44, 44)),
    ("UKRAINE", "EU PROPOSES €45BN UKRAINE LOAN",
     "Repaid after Russia pays reparations.", "euro",
     (150, 130, 30)),
    ("WAR", "CRIMEAN BRIDGE ATTACKED AGAIN",
     "Russian officials report a fresh strike.", "bridge",
     (70, 76, 84)),
    ("WEATHER", "CYCLONE AKVAN NEARS INDIA'S COAST",
     "Landfall expected between Machilipatnam and Puri.", "waves",
     (36, 110, 180)),
    ("ART", "VAN GOGH SELLS FOR A RECORD $190.4M",
     "Price row over its Nazi-era history.", "brush",
     (124, 62, 168)),
    ("JUSTICE", "MYANMAR FACES GENOCIDE VERDICT",
     "UN court rules on the Rohingya case.", "scales",
     (18, 130, 120)),
    ("UNITED STATES", "JEFFRIES SET TO BE FIRST BLACK SPEAKER",
     "Democrats nominate him to lead the House.", "dome",
     (140, 42, 52)),
    ("ENERGY", "FINLAND OKS FIRST NUCLEAR WASTE STORE",
     "World's first spent-fuel repository approved.", "atom",
     (90, 90, 150)),
]

NUMBERS = [
    ("$81.3BN", "ANTHROPIC IPO"),
    ("$190.4M", "VAN GOGH SALE"),
    ("16BN MI", "VOYAGER 1 OUT"),
    ("€45BN", "EU UKRAINE LOAN"),
    ("19", "KILLED IN JET CRASH"),
]


def build():
    img = Image.new("RGB", (W * SS, H * SS), PAPER)
    d = SD(ImageDraw.Draw(img), SS)
    mx = 28  # side margin

    # ---- masthead: navy band, display-serif title, edition marks ----
    d.rectangle([0, 0, W, 92], fill=NAVY)
    f_title = fit_font(SERIF_D, 56, 720, d,
                       "THE WORLD IN ONE PICTURE")
    d.text((W // 2, 6), "THE WORLD IN ONE PICTURE", font=f_title,
           fill=(255, 255, 255), anchor="ma")
    f_ed = font(SANS_B, 10)
    d.text((mx + 4, 34), "VOL. I — No. 323", font=f_ed,
           fill=(170, 185, 210))
    d.text((W - mx - 4, 34), "PRICE: ONE PICTURE", font=f_ed,
           fill=(170, 185, 210), anchor="ra")
    f_date = font(SANS_B, 19)
    d.text((W // 2, 64),
           "THURSDAY 19 NOVEMBER 2026  ·  12 STORIES  ·  6 CONTINENTS",
           font=f_date, fill=GOLD, anchor="ma")
    # double rule under the masthead: gold hairline + red band
    d.rectangle([0, 92, W, 93], fill=GOLD)
    d.rectangle([0, 94, W, 98], fill=RED)

    # ---- kicker with flanking rules ----------------------------------
    f_kick = font(SANS_B, 19)
    kick = "THE DAY VICE CITY OPENED — AND THREE LEADERS SHOOK HANDS"
    kw = d.textlength(kick, font=f_kick)
    d.text((W // 2, 108), kick, font=f_kick, fill=RED, anchor="ma")
    d.line([(mx, 118), (W // 2 - kw // 2 - 14, 118)], fill=RED, width=2)
    d.line([(W // 2 + kw // 2 + 14, 118), (W - mx, 118)], fill=RED,
           width=2)

    # ---- hero cards ----------------------------------------------------
    hy0, hy1 = 134, 476
    img_h = 184
    cw = (W - 2 * mx - 2 * 12) // 3
    f_hkick = font(SANS_B, 12)
    f_hhead = font(SERIF_B, 21)
    f_hdeck = font(SANS, 13)
    for i, (kick_t, head, deck, painter) in enumerate(HEROES):
        x0 = mx + i * (cw + 12)
        x1 = x0 + cw
        # soft shadow, then the card
        d.rounded_rectangle([x0 + 2, hy0 + 3, x1 + 2, hy1 + 3], radius=6,
                            fill=SHADOW)
        d.rounded_rectangle([x0, hy0, x1, hy1], radius=6, fill=CARD,
                            outline=BORDER, width=1)
        d.rounded_rectangle([x0, hy0, x1, hy0 + img_h], radius=6,
                            fill=(240, 240, 240))
        d.rectangle([x0, hy0 + img_h - 26, x1, hy0 + img_h],
                    fill=(240, 240, 240))
        painter(d, (x0 + 1, hy0 + 1, x1 - 1, hy0 + img_h))
        d.rounded_rectangle([x0, hy0, x1, hy0 + img_h], radius=6,
                            outline=BORDER, width=1)
        tx = x0 + 12
        ty = hy0 + img_h + 10
        d.text((tx, ty), kick_t, font=f_hkick, fill=RED)
        d.line([(tx, ty + 18), (tx + 34, ty + 18)], fill=GOLD, width=3)
        ty += 26
        lines = wrap(d, head, f_hhead, cw - 24)
        ty = draw_lines(d, lines, tx, ty, f_hhead, INK, 25)
        ty += 5
        deck_lines = wrap(d, deck, f_hdeck, cw - 24)
        draw_lines(d, deck_lines, tx, ty, f_hdeck, GRAY, 17)

    # ---- section header ------------------------------------------------
    f_sec = font(SANS_B, 20)
    d.rectangle([mx, 490, mx + 14, 504], fill=GOLD)
    d.text((mx + 22, 486), "MORE FROM THURSDAY", font=f_sec, fill=RED)
    d.line([(mx + 252, 498), (W - mx, 498)], fill=BORDER, width=2)

    # ---- grid 3x3 with colour accent bars -----------------------------
    gy0 = 516
    gh = 112
    gw = (W - 2 * mx - 2 * 12) // 3
    f_gkick = font(SANS_B, 11)
    f_ghead = font(SANS_B, 16)
    f_gdeck = font(SANS, 12)
    for i, (kick_t, head, deck, kind, col) in enumerate(GRID):
        r, c = divmod(i, 3)
        x0 = mx + c * (gw + 12)
        y0 = gy0 + r * gh
        x1 = x0 + gw
        y1 = y0 + gh - 10
        d.rounded_rectangle([x0 + 2, y0 + 2, x1 + 2, y1 + 2], radius=6,
                            fill=SHADOW)
        d.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=CARD,
                            outline=BORDER, width=1)
        # left accent bar in the story colour
        d.rectangle([x0 + 1, y0 + 6, x0 + 5, y1 - 6], fill=col)
        icon(d, kind, (x0 + 14, y0 + 19, x0 + 78, y0 + 83), col)
        tx = x0 + 88
        ty = y0 + 10
        d.text((tx, ty), kick_t, font=f_gkick, fill=RED)
        ty += 17
        lines = wrap(d, head, f_ghead, gw - 98)
        ty = draw_lines(d, lines[:2], tx, ty, f_ghead, INK, 19)
        ty += 2
        deck_lines = wrap(d, deck, f_gdeck, gw - 98)
        draw_lines(d, deck_lines[:2], tx, ty, f_gdeck, GRAY, 15)

    # ---- numbers strip --------------------------------------------------
    ny0, ny1 = 872, 940
    d.rectangle([0, ny0, W, ny0 + 2], fill=GOLD)
    d.rectangle([0, ny0 + 2, W, ny1], fill=NAVY)
    # DejaVu Serif Bold: its $ and € glyphs stay unambiguous at
    # small sizes, unlike the display face's euro, which reads as C
    f_num = font(SERIF, 27)
    f_nlab = font(SANS_B, 11)
    seg = W // 5
    for i, (num, lab) in enumerate(NUMBERS):
        cx = seg * i + seg // 2
        d.text((cx, ny0 + 10), num, font=f_num, fill=GOLD, anchor="ma")
        d.text((cx, ny0 + 42), lab, font=f_nlab, fill=(255, 255, 255),
               anchor="ma")
        if i:
            diamond(d, seg * i, ny0 + 34, 5, GOLD_DEEP)

    # ---- footer ---------------------------------------------------------
    d.line([(mx, 948), (W - mx, 948)], fill=BORDER, width=1)
    f_foot = font(SANS, 11)
    d.text((W // 2, 956),
           "COMPILED FROM BBC, REUTERS, AP, AL JAZEERA AND NPR REPORTING OF 19 NOVEMBER 2026.",
           font=f_foot, fill=GRAY, anchor="ma")
    d.text((W // 2, 976),
           "ALSO: ISRAELI GROUND OPERATION IN GAZA  ·  RUSSIAN JET CRASH KILLS 19 IN SIBERIA  ·  NVIDIA ACTING CEO PROMISES EARLIER PAY RAISES",
           font=f_foot, fill=GRAY, anchor="ma")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(OUT, "PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()
