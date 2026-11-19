#!/usr/bin/env python3
"""Render the 19 Nov 2026 world-news poster (1024x1024) with PIL.

Build-time dependency only: Pillow. The entrypoint (main.py) is
stdlib-only and just copies the finished PNG to /output/entry.png.
Layout: newspaper front page — masthead, kicker, 3 hero cards with
illustrated scenes, a 3x3 grid of the remaining stories, a numbers
strip and a source footer. All 12 stories from NEWS.md are present.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "assets", "entry.png")

# ---- palette ---------------------------------------------------------
NAVY = (15, 30, 61)
GOLD = (242, 193, 78)
RED = (176, 58, 46)
PAPER = (248, 244, 233)
CARD = (255, 255, 255)
INK = (28, 28, 28)
GRAY = (96, 96, 96)
BORDER = (214, 208, 192)
GREEN = (46, 160, 90)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FONT_DIR, "dejavu", "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FONT_DIR, "dejavu", "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "dejavu", "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, box, top, bottom):
    """Vertical gradient fill inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for y in range(y0, y1):
        draw.line([(x0, y), (x1, y)], fill=lerp(top, bottom, (y - y0) / h))


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w."""
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


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    import math
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ---- hero illustrations ----------------------------------------------
def hero_vice_city(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(draw, box, (64, 22, 88), (238, 96, 62))
    # sun with synthwave slits, high enough to clear the skyline
    sx, sy, sr = x0 + w * 0.68, y0 + h * 0.34, 42
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 214, 90))
    for yy, hh in [(sy - 6, 4), (sy + 8, 5), (sy + 22, 6)]:
        draw.rectangle([sx - sr, yy, sx + sr, yy + hh],
                       fill=(238, 96, 62))
    # skyline silhouettes, two depths
    rnd = random.Random(19)
    base = y1 - 34
    for col, hmin, hmax in (((44, 18, 66), 38, 118), ((28, 10, 48), 20, 70)):
        bx = x0
        while bx < x1 - 8:
            bw = rnd.randint(18, 34)
            bh = rnd.randint(hmin, hmax)
            draw.rectangle([bx, base - bh, bx + bw, base], fill=col)
            for wy in range(base - bh + 8, base - 6, 12):
                for wx in range(bx + 4, bx + bw - 3, 9):
                    if rnd.random() < 0.45:
                        draw.rectangle([wx, wy, wx + 3, wy + 4],
                                       fill=(255, 205, 90))
            bx += bw + rnd.randint(2, 8)
    # palm silhouettes, kept inside the frame
    for px, ph in [(x0 + 30, 46), (x1 - 36, 54)]:
        draw.line([(px, base), (px + 4, base - ph)], fill=(24, 8, 40),
                  width=4)
        for dx, dy in [(-16, -8), (-10, -16), (0, -18), (10, -16), (16, -8)]:
            draw.arc([px + dx - 8, base - ph + dy - 6,
                      px + dx + 8, base - ph + dy + 6],
                     200, 340, fill=(24, 8, 40), width=3)
    # neon road
    draw.rectangle([x0, base, x1, y1], fill=(20, 8, 36))
    for dx in range(x0 + 6, x1 - 10, 26):
        draw.rectangle([dx, y1 - 12, dx + 14, y1 - 8], fill=(255, 80, 160))


def hero_shenzhen(draw, box):
    x0, y0, x1, y1 = box
    w = x1 - x0
    vgrad(draw, box, (196, 214, 230), (238, 238, 232))
    # skyline
    rnd = random.Random(7)
    base = y1 - 46
    bx = x0
    while bx < x1 - 10:
        bw = rnd.randint(22, 40)
        bh = rnd.randint(52, 118)
        col = (126 + rnd.randint(-14, 14), 136 + rnd.randint(-10, 10),
               148 + rnd.randint(-10, 10))
        draw.rectangle([bx, base - bh, bx + bw, base], fill=col)
        for wy in range(base - bh + 8, base - 8, 13):
            for wx in range(bx + 5, bx + bw - 4, 10):
                if rnd.random() < 0.5:
                    draw.rectangle([wx, wy, wx + 4, wy + 5],
                                   fill=(240, 244, 248))
        bx += bw + rnd.randint(3, 9)
    draw.rectangle([x0, base, x1, y1], fill=(88, 96, 106))
    # three flag poles
    poles = [int(x0 + w * 0.20), int(x0 + w * 0.50), int(x0 + w * 0.80)]
    flag_w, flag_h = 52, 34
    fy = y0 + 18
    for px in poles:
        draw.line([(px, fy), (px, base)], fill=(60, 60, 60), width=3)
    # USA flag
    fx = poles[0] + 2
    for i in range(7):
        draw.rectangle([fx, fy + i * 5, fx + flag_w, fy + i * 5 + 5],
                       fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    draw.rectangle([fx, fy, fx + 22, fy + 17], fill=(40, 60, 120))
    for sy in range(fy + 3, fy + 16, 5):
        for sx in range(fx + 3, fx + 20, 5):
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    # China flag
    fx = poles[1] + 2
    draw.rectangle([fx, fy, fx + flag_w, fy + flag_h], fill=(222, 32, 24))
    draw.polygon(star_points(fx + 10, fy + 9, 6, 2.5), fill=(255, 222, 0))
    for sx, sy in [(26, 6), (31, 11), (31, 17), (26, 21)]:
        draw.polygon(star_points(fx + sx, fy + sy, 3, 1.2),
                     fill=(255, 222, 0))
    # Russia flag
    fx = poles[2] + 2
    for i, col in enumerate([(255, 255, 255), (0, 90, 180), (220, 40, 40)]):
        draw.rectangle([fx, fy + i * 11, fx + flag_w, fy + (i + 1) * 11],
                       fill=col)
    # gold handshake badge
    cx, cy, r = x0 + w // 2, base - 6, 30
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD,
                 outline=(255, 255, 255), width=3)
    draw.line([(cx - 13, cy), (cx - 4, cy + 10), (cx + 14, cy - 10)],
              fill=NAVY, width=6)


def hero_ipo(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=NAVY)
    # faint grid
    for gx in range(x0 + 24, x1 - 10, 34):
        draw.line([(gx, y0), (gx, y1)], fill=(32, 56, 100), width=1)
    for gy in range(y0 + 16, y1 - 10, 30):
        draw.line([(x0, gy), (x1, gy)], fill=(32, 56, 100), width=1)
    # big price
    f_big = font(SANS_B, 66)
    draw.text((x0 + 18, y0 + 10), "$83", font=f_big, fill=GOLD)
    f_sub = font(SANS_B, 17)
    draw.text((x0 + 18, y0 + 84), "ANT  ·  NASDAQ", font=f_sub,
              fill=(255, 255, 255))
    # bars
    base = y1 - 16
    heights = [26, 42, 34, 56, 74]
    bw, gap = 34, 12
    bx = x0 + 20
    tops = []
    for hh in heights:
        draw.rectangle([bx, base - hh, bx + bw, base], fill=GREEN)
        tops.append((bx + bw // 2, base - hh))
        bx += bw + gap
    # trend line with arrow
    pts = [(tops[0][0], tops[0][1] - 4)] + \
          [(x, y - 4) for x, y in tops[1:]]
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
        draw.arc([cx - 22, cy - 14, cx + 22, cy + 26], 180, 360,
                 fill=white, width=5)
        draw.line([(cx - 26, cy + 8), (cx + 26, cy + 8)], fill=white,
                  width=4)
        draw.line([(cx - 18, cy + 8), (cx - 18, cy + 22)], fill=white,
                  width=3)
        draw.line([(cx + 18, cy + 8), (cx + 18, cy + 22)], fill=white,
                  width=3)
    elif kind == "waves":
        for yy in (-14, -2, 10):
            draw.arc([cx - 22, cy + yy - 8, cx + 22, cy + yy + 8],
                     180, 360, fill=white, width=4)
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
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 28  # side margin

    # masthead
    d.rectangle([0, 0, W, 92], fill=NAVY)
    f_title = font(SERIF_B, 52)
    d.text((W // 2, 8), "THE WORLD IN ONE PICTURE", font=f_title,
           fill=(255, 255, 255), anchor="ma")
    f_date = font(SANS_B, 18)
    d.text((W // 2, 62),
           "THURSDAY 19 NOVEMBER 2026  ·  12 STORIES  ·  6 CONTINENTS",
           font=f_date, fill=GOLD, anchor="ma")
    d.rectangle([0, 92, W, 97], fill=RED)

    # kicker
    f_kick = font(SANS_B, 20)
    d.text((W // 2, 106),
           "THE DAY VICE CITY OPENED — AND THREE LEADERS SHOOK HANDS",
           font=f_kick, fill=RED, anchor="ma")

    # hero cards
    hy0, hy1 = 134, 470
    cw = (W - 2 * mx - 2 * 12) // 3
    f_hkick = font(SANS_B, 12)
    f_hhead = font(SANS_B, 20)
    f_hdeck = font(SANS, 13)
    for i, (kick, head, deck, painter) in enumerate(HEROES):
        x0 = mx + i * (cw + 12)
        x1 = x0 + cw
        d.rounded_rectangle([x0, hy0, x1, hy1], radius=6, fill=CARD,
                            outline=BORDER, width=1)
        d.rounded_rectangle([x0, hy0, x1, hy0 + 190], radius=6,
                            fill=(240, 240, 240))
        d.rectangle([x0, hy0 + 164, x1, hy0 + 190], fill=(240, 240, 240))
        painter(d, (x0 + 1, hy0 + 1, x1 - 1, hy0 + 190))
        d.rounded_rectangle([x0, hy0, x1, hy0 + 190], radius=6,
                            outline=BORDER, width=1)
        tx = x0 + 12
        ty = hy0 + 200
        d.text((tx, ty), kick, font=f_hkick, fill=RED)
        ty += 20
        lines = wrap(d, head, f_hhead, cw - 24)
        ty = draw_lines(d, lines, tx, ty, f_hhead, INK, 24)
        ty += 4
        deck_lines = wrap(d, deck, f_hdeck, cw - 24)
        draw_lines(d, deck_lines, tx, ty, f_hdeck, GRAY, 17)

    # section header
    f_sec = font(SANS_B, 20)
    d.text((mx, 482), "MORE FROM THURSDAY", font=f_sec, fill=RED)
    d.line([(mx + 250, 496), (W - mx, 496)], fill=BORDER, width=2)

    # grid 3x3
    gy0 = 512
    gh = 114
    gw = (W - 2 * mx - 2 * 12) // 3
    f_gkick = font(SANS_B, 11)
    f_ghead = font(SANS_B, 16)
    f_gdeck = font(SANS, 12)
    for i, (kick, head, deck, kind, col) in enumerate(GRID):
        r, c = divmod(i, 3)
        x0 = mx + c * (gw + 12)
        y0 = gy0 + r * gh
        x1 = x0 + gw
        d.rounded_rectangle([x0, y0, x1, y0 + gh - 10], radius=6,
                            fill=CARD, outline=BORDER, width=1)
        icon(d, kind, (x0 + 10, y0 + 14, x0 + 74, y0 + 78), col)
        tx = x0 + 84
        ty = y0 + 10
        d.text((tx, ty), kick, font=f_gkick, fill=RED)
        ty += 17
        lines = wrap(d, head, f_ghead, gw - 94)
        ty = draw_lines(d, lines[:2], tx, ty, f_ghead, INK, 19)
        ty += 2
        deck_lines = wrap(d, deck, f_gdeck, gw - 94)
        draw_lines(d, deck_lines[:2], tx, ty, f_gdeck, GRAY, 15)

    # numbers strip
    ny0, ny1 = 872, 940
    d.rectangle([0, ny0, W, ny1], fill=NAVY)
    f_num = font(SANS_B, 26)
    f_nlab = font(SANS_B, 11)
    seg = W // 5
    for i, (num, lab) in enumerate(NUMBERS):
        cx = seg * i + seg // 2
        d.text((cx, ny0 + 8), num, font=f_num, fill=GOLD, anchor="ma")
        d.text((cx, ny0 + 40), lab, font=f_nlab, fill=(255, 255, 255),
               anchor="ma")

    # footer
    f_foot = font(SANS, 11)
    d.text((W // 2, 952),
           "COMPILED FROM BBC, REUTERS, AP, AL JAZEERA AND NPR REPORTING OF 19 NOVEMBER 2026.",
           font=f_foot, fill=GRAY, anchor="ma")
    d.text((W // 2, 972),
           "ALSO: ISRAELI GROUND OPERATION IN GAZA  ·  RUSSIAN JET CRASH KILLS 19 IN SIBERIA  ·  NVIDIA ACTING CEO PROMISES EARLIER PAY RAISES",
           font=f_foot, fill=GRAY, anchor="ma")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()
