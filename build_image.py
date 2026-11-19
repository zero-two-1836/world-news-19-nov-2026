#!/usr/bin/env python3
"""Build the front-page image for the make.fun bounty
"Sum up 19 November's world news in one image".

A poster, in the style of the news 17/18 v2 rebuilds: three large
flat-illustration hero panels (GTA VI, the Shenzhen trilateral,
Anthropic's IPO), an 8-story grid with one-line headlines, and a
numbers strip. No text under 15px except the source footer. Same
12 stories, same verified facts (see NEWS.md).

Run once, locally, to produce assets/entry.png (1024x1024, <=1 MiB).
The submitted program (main.py) is stdlib-only and copies that asset to
/output/entry.png deterministically; this builder is kept in the repo so
anyone can see exactly how the image was made.

News verified 2026-11-19 from BBC, Reuters/AP wires via One Turn News,
Hansen Intel, Foreign Exchanges, Al Jazeera and NPR summaries of
19 Nov 2026. Procedural drawing only (Pillow): no AI image generation,
no photos.
"""
import math
import random
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (20, 20, 22)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
GREY = (90, 88, 82)
RULE = (180, 175, 160)
CARD = (255, 252, 245)
GOLD = (214, 200, 150)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Word-wrap text to fit pixel width; returns list of lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, width, fill=INK, leading=None):
    lines = wrap(draw, text, fnt, width)
    lh = leading or int(fnt.size * 1.32)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def kicker(draw, x, y, text, color=RED, size=17):
    f = font(SANS_B, size)
    draw.text((x, y), text.upper(), font=f, fill=color)
    return y + size + 6


def fit_font(draw, text, path, start_size, max_width, min_size=15):
    """Largest font size at/below start_size whose text fits max_width."""
    size = start_size
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 1
    return font(path, min_size)


def starburst(d, cx, cy, r_out, r_in, spikes, fill):
    pts = []
    for i in range(spikes * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / spikes - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def bezier(p0, p1, p2, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


# ---------- hero illustrations (flat, procedural) ----------

def draw_gta(d, x0, y0, w, h):
    """Vice City sunset: purple-to-orange sky, slatted sun, palms, skyline."""
    bands = [(88, 28, 88), (150, 40, 110), (198, 58, 110),
             (232, 90, 90), (255, 140, 60), (255, 175, 90)]
    bh = h // len(bands)
    for i, c in enumerate(bands):
        d.rectangle([x0, y0 + i * bh, x0 + w, y0 + (i + 1) * bh], fill=c)
    # sun with horizontal slits, upper right
    sx, sy, sr = x0 + w - 66, y0 + 52, 30
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 232, 160))
    for yy in (sy - 8, sy + 2, sy + 12):
        d.rectangle([sx - sr, yy, sx + sr, yy + 4], fill=(232, 90, 90))
    # palm silhouettes: trunk + 5 fronds each
    def palm(px, py, s, lean):
        d.polygon([(px - 4 * s, py), (px + 4 * s, py),
                   (px + 2 * s + lean, py - 62 * s),
                   (px - 2 * s + lean, py - 62 * s)], fill=(24, 10, 28))
        tx, ty = px + lean, py - 62 * s
        for ang in (-150, -110, -70, -30, 10):
            a = math.radians(ang)
            ex, ey = tx + 34 * s * math.cos(a), ty + 26 * s * math.sin(a)
            d.line([(tx, ty), (ex, ey)], fill=(24, 10, 28), width=int(5 * s))
    palm(x0 + 34, y0 + h - 34, 1.0, 8)
    palm(x0 + w - 40, y0 + h - 34, 0.85, -8)
    # skyline with lit windows, bottom
    d.rectangle([x0, y0 + h - 34, x0 + w, y0 + h], fill=(24, 10, 28))
    rnd = random.Random(19)
    bx = x0 + 8
    while bx < x0 + w - 20:
        bw = rnd.randint(18, 34)
        bh2 = rnd.randint(14, 30)
        d.rectangle([bx, y0 + h - 34 - bh2, bx + bw, y0 + h - 34],
                    fill=(40, 16, 44))
        for wy in range(y0 + h - 30 - bh2, y0 + h - 36, 8):
            for wx in range(bx + 4, bx + bw - 3, 8):
                if rnd.random() < 0.5:
                    d.rectangle([wx, wy, wx + 3, wy + 4],
                                fill=(255, 210, 110))
        bx += bw + 4
    # water shimmer
    d.rectangle([x0, y0 + h - 8, x0 + w, y0 + h], fill=(60, 20, 70))
    for xx in range(6, w, 26):
        d.line([(x0 + xx, y0 + h - 5), (x0 + xx + 12, y0 + h - 5)],
               fill=(255, 175, 120), width=2)


def draw_trilateral(d, x0, y0, w, h):
    """Shenzhen skyline, three flag poles: US, China, Russia."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(198, 208, 220))
    d.rectangle([x0, y0 + h - 52, x0 + w, y0 + h], fill=(70, 76, 88))
    # skyline towers
    rnd = random.Random(11)
    bx = x0 + 6
    while bx < x0 + w - 16:
        bw = rnd.randint(16, 30)
        bh2 = rnd.randint(18, 46)
        d.rectangle([bx, y0 + h - 52 - bh2, bx + bw, y0 + h - 52],
                    fill=(52, 58, 70))
        if rnd.random() < 0.4:
            d.polygon([(bx + bw // 2 - 3, y0 + h - 52 - bh2),
                       (bx + bw // 2 + 3, y0 + h - 52 - bh2),
                       (bx + bw // 2, y0 + h - 62 - bh2)], fill=(52, 58, 70))
        bx += bw + 5
    # flag poles + flags
    poles = [x0 + 52, x0 + w // 2, x0 + w - 62]
    fw, fh = 46, 30
    for i, px in enumerate(poles):
        d.line([(px, y0 + 18), (px, y0 + 118)], fill=(40, 40, 44), width=3)
        fx, fy = px + 2, y0 + 18
        if i == 0:  # United States
            for s in range(7):
                d.rectangle([fx, fy + s * 4, fx + fw, fy + (s + 1) * 4],
                            fill=(178, 34, 34) if s % 2 == 0 else (255, 255, 255))
            d.rectangle([fx, fy, fx + 19, fy + 14], fill=(20, 33, 61))
            for sy in (fy + 3, fy + 7, fy + 11):
                for sx in (fx + 3, fx + 9, fx + 15):
                    d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1],
                              fill=(255, 255, 255))
        elif i == 1:  # China
            d.rectangle([fx, fy, fx + fw, fy + fh], fill=(222, 40, 30))
            starburst(d, fx + 10, fy + 9, 7, 3, 5, (255, 220, 60))
            for (sx, sy) in ((fx + 26, fy + 5), (fx + 32, fy + 10),
                             (fx + 30, fy + 17), (fx + 23, fy + 18)):
                starburst(d, sx, sy, 3, 1, 5, (255, 220, 60))
        else:  # Russia
            for s, c in enumerate(((255, 255, 255), (30, 90, 200),
                                   (210, 40, 40))):
                d.rectangle([fx, fy + s * 10, fx + fw, fy + (s + 1) * 10],
                            fill=c)
    # gold handshake disc between the poles, lower centre
    cx, cy = x0 + w // 2, y0 + 128
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(255, 205, 60),
              outline=(178, 140, 40), width=2)
    d.line([(cx - 11, cy - 2), (cx - 2, cy + 7), (cx + 12, cy - 8)],
           fill=(20, 33, 61), width=4)


def draw_anthropic(d, x0, y0, w, h):
    """Dark board, rising green chart, big $83 and ANT ticker."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 28, 54))
    for yy in range(y0 + 20, y0 + h - 10, 28):
        d.line([(x0 + 8, yy), (x0 + w - 8, yy)], fill=(40, 55, 90), width=1)
    # ascending bars
    rnd = random.Random(5)
    bw, gap = 26, 10
    bx = x0 + 16
    heights = [26, 40, 34, 58, 74]
    for bh2 in heights:
        d.rectangle([bx, y0 + h - 26 - bh2, bx + bw, y0 + h - 26],
                    fill=(34, 120, 80))
        bx += bw + gap
    # rising line with arrow
    pts = [(x0 + 22, y0 + h - 60), (x0 + 80, y0 + h - 88),
           (x0 + 138, y0 + h - 78), (x0 + 196, y0 + h - 112),
           (x0 + 252, y0 + h - 132), (x0 + w - 22, y0 + h - 158)]
    d.line(pts, fill=(80, 220, 130), width=5)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 16, ey - 2), (ex - 6, ey + 12)],
              fill=(80, 220, 130))
    # price
    d.text((x0 + 16, y0 + 10), "$83", font=font(SERIF_B, 46),
           fill=(255, 205, 60))
    d.text((x0 + 16, y0 + 62), "ANT  ·  NASDAQ", font=font(SANS_B, 18),
           fill=(255, 255, 255))


# ---------- small story icons (40x40 rounded square + white glyph) ----------

def icon_star(d, x, y, bg):
    d.rounded_rectangle([x, y, x + 40, y + 40], radius=8, fill=bg)
    starburst(d, x + 20, y + 21, 15, 6, 5, (255, 255, 255))


def icon_flame(d, x, y, bg):
    d.rounded_rectangle([x, y, x + 40, y + 40], radius=8, fill=bg)
    d.polygon([(x + 20, y + 7), (x + 28, y + 18), (x + 30, y + 26),
               (x + 24, y + 33), (x + 16, y + 33), (x + 10, y + 26),
               (x + 12, y + 18)], fill=(255, 255, 255))


def icon_coin(d, x, y, bg):
    d.rounded_rectangle([x, y, x + 40, y + 40], radius=8, fill=bg)
    d.ellipse([x + 8, y + 8, x + 32, y + 32], fill=(255, 255, 255))
    d.text((x + 13, y + 9), "€", font=font(SANS_B, 20), fill=bg)


def icon_bridge(d, x, y, bg):
    d.rounded_rectangle([x, y, x + 40, y + 40], radius=8, fill=bg)
    d.arc([x + 7, y + 12, x + 33, y + 34], 180, 360,
          fill=(255, 255, 255), width=3)
    d.line([(x + 7, y + 28), (x + 33, y + 28)], fill=(255, 255, 255), width=3)
    d.line([(x + 12, y + 28), (x + 12, y + 33)], fill=(255, 255, 255), width=3)
    d.line([(x + 28, y + 28), (x + 28, y + 33)], fill=(255, 255, 255), width=3)


def icon_wave(d, x, y, bg):
    d.rounded_rectangle([x, y, x + 40, y + 40], radius=8, fill=bg)
    for yy in (14, 20, 26):
        d.arc([x + 8, y + yy, x + 32, y + yy + 10], 180, 360,
              fill=(255, 255, 255), width=3)


def icon_paint(d, x, y, bg):
    d.rounded_rectangle([x, y, x + 40, y + 40], radius=8, fill=bg)
    d.line([(x + 12, y + 30), (x + 24, y + 12)], fill=(255, 255, 255), width=4)
    d.polygon([(x + 24, y + 12), (x + 30, y + 8), (x + 32, y + 14),
               (x + 27, y + 17)], fill=(255, 255, 255))
    d.ellipse([x + 9, y + 27, x + 15, y + 33], fill=(255, 255, 255))


def icon_scale(d, x, y, bg):
    d.rounded_rectangle([x, y, x + 40, y + 40], radius=8, fill=bg)
    d.line([(x + 20, y + 8), (x + 20, y + 30)], fill=(255, 255, 255), width=3)
    d.line([(x + 10, y + 12), (x + 30, y + 12)], fill=(255, 255, 255), width=3)
    d.polygon([(x + 6, y + 20), (x + 14, y + 20), (x + 10, y + 27)],
              fill=(255, 255, 255))
    d.polygon([(x + 26, y + 20), (x + 34, y + 20), (x + 30, y + 27)],
              fill=(255, 255, 255))
    d.rectangle([x + 14, y + 30, x + 26, y + 33], fill=(255, 255, 255))


def icon_capitol(d, x, y, bg):
    d.rounded_rectangle([x, y, x + 40, y + 40], radius=8, fill=bg)
    d.pieslice([x + 12, y + 8, x + 28, y + 22], 180, 360,
               fill=(255, 255, 255))
    d.rectangle([x + 9, y + 22, x + 31, y + 25], fill=(255, 255, 255))
    for cx in (13, 20, 27):
        d.rectangle([x + cx - 1, y + 25, x + cx + 1, y + 32],
                    fill=(255, 255, 255))
    d.rectangle([x + 9, y + 32, x + 31, y + 34], fill=(255, 255, 255))


# ---------- page ----------

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
M = 28  # margin

# ---- Masthead ----
d.rectangle([0, 0, W, 88], fill=NAVY)
d.text((M, 14), "THE WORLD IN ONE PICTURE", font=font(SERIF_B, 40),
       fill=(255, 255, 255))
d.text((M, 62), "THURSDAY  19  NOVEMBER  2026  ·  12 STORIES  ·  6 CONTINENTS",
       font=font(SANS_B, 16), fill=GOLD)
d.rectangle([0, 88, W, 92], fill=RED)

# ---- Day line ----
d.text((M, 104),
       "THE DAY VICE CITY OPENED — AND THREE LEADERS SHOOK HANDS",
       font=font(SANS_B, 19), fill=GREY)
d.line([(M, 134), (W - M, 134)], fill=RULE, width=2)

# ---- Hero row: 3 illustrated panels ----
hero_y, hero_h, illus_h = 146, 348, 180
col_w = (W - 2 * M - 2 * 16) // 3
heroes = [
    (draw_gta, "LEAD  ·  VICE CITY",
     "Gamers enter Vice City as GTA VI rolls out",
     "Rockstar's epic launches worldwide after a 13-year wait."),
    (draw_trilateral, "DIPLOMACY  ·  SHENZHEN",
     "Trump, Xi and Putin shake hands in Shenzhen",
     "Trilateral talks at the APEC summit; Ukraine on the agenda."),
    (draw_anthropic, "MARKETS  ·  IPO",
     "Anthropic debuts at $83 in the biggest IPO ever",
     "$81.3bn raised — the largest stock market debut in history."),
]
for i, (draw_fn, tag, head, sub) in enumerate(heroes):
    x = M + i * (col_w + 16)
    d.rectangle([x, hero_y, x + col_w, hero_y + hero_h],
                fill=CARD, outline=RULE, width=2)
    draw_fn(d, x + 2, hero_y + 2, col_w - 4, illus_h)
    ty = hero_y + illus_h + 12
    ty = kicker(d, x + 14, ty, tag, size=13)
    ty = para(d, x + 14, ty, head, font(SERIF_B, 24), col_w - 28, leading=29)
    para(d, x + 14, ty + 2, sub, font(SANS, 15), col_w - 28, leading=19)

# ---- Grid: 8 more stories, 2 columns x 4 rows ----
gy = hero_y + hero_h + 14
gy = kicker(d, M, gy, "More from Thursday", size=16)
gy += 2
grid = [
    (icon_star, (20, 33, 61), "SPACE",
     "Voyager 1 hits one light-day out",
     "50 years on, the probe is 16 billion miles away."),
    (icon_flame, (178, 34, 34), "THE GULF",
     "U.S. and Iran trade fire again",
     "Tehran widens attacks to Kuwait and Bahrain."),
    (icon_coin, (120, 100, 20), "UKRAINE",
     "EU proposes €45bn Ukraine loan",
     "Repaid after Russia pays reparations."),
    (icon_bridge, (70, 72, 78), "WAR",
     "Crimean Bridge attacked again",
     "Russian officials report a fresh strike."),
    (icon_wave, (30, 90, 160), "WEATHER",
     "Cyclone Akvan nears India's coast",
     "Landfall expected between Machilipatnam and Puri."),
    (icon_paint, (100, 60, 140), "ART",
     "Van Gogh sells for record $190.4m",
     "Price row over its Nazi-era history."),
    (icon_scale, (20, 110, 110), "JUSTICE",
     "Myanmar faces genocide verdict",
     "UN court rules on the Rohingya case."),
    (icon_capitol, (140, 40, 40), "UNITED STATES",
     "Jeffries set to be first Black Speaker",
     "Democrats nominate him to lead the House."),
]
gcol_w = (W - 2 * M - 16) // 2
row_h = 80
for i in range(0, len(grid), 2):
    for j, (icon_fn, color, tag, head, sub) in enumerate(grid[i:i + 2]):
        x = M + j * (gcol_w + 16)
        y = gy + (i // 2) * row_h
        d.rounded_rectangle([x, y, x + gcol_w, y + row_h - 10], radius=8,
                            fill=CARD, outline=RULE, width=1)
        icon_fn(d, x + 10, y + 10, color)
        tx = x + 60
        d.text((tx, y + 8), tag, font=font(SANS_B, 12), fill=RED)
        d.text((tx, y + 26), head,
               font=fit_font(d, head, SANS_B, 20, gcol_w - 70), fill=INK)
        d.text((tx, y + 52), sub, font=font(SANS, 15), fill=INK)
gy = gy + 4 * row_h + 8

# ---- Numbers strip ----
d.rectangle([M, gy, W - M, gy + 70], fill=NAVY)
nums = [("$81.3bn", "Anthropic IPO"), ("$190.4m", "Van Gogh sale"),
        ("16bn mi", "Voyager 1 out"), ("€45bn", "EU Ukraine loan"),
        ("19", "killed in jet crash")]
seg = (W - 2 * M) // len(nums)
for i, (n, label) in enumerate(nums):
    cx = M + i * seg + seg // 2
    f1, f2 = font(SANS_B, 26), font(SANS, 13)
    d.text((cx - d.textlength(n, font=f1) / 2, gy + 8), n, font=f1,
           fill=(255, 255, 255))
    d.text((cx - d.textlength(label, font=f2) / 2, gy + 42), label, font=f2,
           fill=GOLD)
gy += 70 + 10

# ---- Footer ----
d.text((M, gy),
       "Compiled from BBC, Reuters, AP, Al Jazeera and NPR reporting of 19 November 2026.",
       font=font(SANS, 14), fill=GREY)
d.text((M, gy + 18),
       "Also: Israeli ground operation in Gaza · Russian jet crash kills 19 in Siberia · Finland OKs first nuclear waste store",
       font=font(SANS, 14), fill=GREY)
gy += 36

img.save("assets/entry.png", optimize=True)
print("saved assets/entry.png", img.size, "final y =", gy)
