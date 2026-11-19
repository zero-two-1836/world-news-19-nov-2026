#!/usr/bin/env python3
"""Render the 19 November 2026 world-news poster as a 1024x1024 PNG.

Pure standard library: a tiny raster canvas, a 5x7 pixel typeface
drawn at several scales, and a hand-written PNG encoder (zlib +
struct). No third-party packages, no network, fully deterministic.

Layout (top to bottom): navy masthead with the paper name and the
day line, a red rule, a one-line kicker, three illustrated lead
stories, an eight-story grid with pictogram icons, a numbers strip,
and a sources footer. Twelve stories in total, six continents.

Run:  python3 build_image.py
Writes: assets/entry.png  (1024x1024 RGB PNG)
"""

import hashlib
import math
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
CREAM = (245, 239, 224)      # page background
PAPER = (255, 252, 244)      # card background
NAVY = (27, 42, 74)          # masthead / numbers strip
NAVY_DEEP = (15, 26, 52)     # IPO panel
GOLD = (216, 178, 58)        # masthead subline, IPO figure
RED = (176, 42, 48)          # rule, kickers, labels
INK = (30, 30, 30)           # headlines
GREY = (105, 105, 100)       # body copy, footer
LINE = (198, 190, 172)       # card outlines
SKY = (198, 211, 220)        # Shenzhen sky
GREEN = (46, 160, 90)        # IPO bars / trend
GREEN_LT = (110, 220, 150)   # IPO trend line


# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is empty.
# All poster copy is set in capitals, so the face only needs
# A-Z, 0-9 and the punctuation the headlines use.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '\u2014': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '\u00b7': (".....", ".....", ".##..", ".##..", ".....", ".....", "....."),
    '$': ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    '\u20ac': (".###.", "#...#", "#....", "####.", "#....", "#...#", ".###."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#.#.#", "#...#"),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
}
BLANK = (".....",) * 7


def glyph(ch):
    """Return the 7-row bitmap for a character (blank if unknown)."""
    return FONT.get(ch, BLANK)


def text_width(s, scale):
    """Pixel width of a string at a scale (glyph 5*scale + 1*scale gap)."""
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def wrap(s, scale, max_w):
    """Split a string into lines that fit max_w pixels at a scale."""
    words = s.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    """An RGB raster backed by a bytearray, with rect/circle/line/text."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.buf[o:o + 3] = bytes(c)

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.buf[o:o + len(row)] = row

    def outline(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, length, c, t=1):
        self.fill_rect(x, y - t // 2, length, t, c)

    def vline(self, x, y, length, c, t=1):
        self.fill_rect(x - t // 2, y, t, length, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        """Bresenham line with a square brush of side t."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        half = t // 2
        while True:
            self.fill_rect(x - half, y - half, t, t, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def polyline(self, pts, c, t=1):
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            self.line(ax, ay, bx, by, c, t)

    def disc(self, cx, cy, r, c):
        """Filled circle, scanline by scanline."""
        for dy in range(-r, r + 1):
            half = int(math.sqrt(max(r * r - dy * dy, 0)))
            self.fill_rect(cx - half, cy + dy, half * 2 + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for dy in range(-r, r + 1):
            half = int(math.sqrt(max(r * r - dy * dy, 0)))
            inner = int(math.sqrt(max((r - t) * (r - t) - dy * dy, 0))) if r - t > 0 else 0
            self.fill_rect(cx - half, cy + dy, half - inner, 1, c)
            self.fill_rect(cx + inner, cy + dy, half - inner + 1, 1, c)

    def polygon(self, pts, c):
        """Scanline-filled polygon (any vertex count)."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
                if (ay <= y < by) or (by <= y < ay):
                    xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
            xs.sort()
            for x0, x1 in zip(xs[::2], xs[1::2]):
                self.fill_rect(int(math.ceil(x0)), y, int(math.floor(x1)) - int(math.ceil(x0)) + 1, 1, c)

    def star(self, cx, cy, r_out, r_in, c, points=5, rot=-math.pi / 2):
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = rot + i * math.pi / points
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.polygon(pts, c)

    def text(self, s, x, y, scale, c, bold=False):
        """Draw a string; returns the x just past the last glyph.

        With bold=True each set pixel is one unit wider, which
        thickens the strokes so headlines stay readable when the
        poster is shrunk to ~300px across. The advance width is
        unchanged, so centring and wrapping still work.
        """
        cx = x
        pw = scale + 1 if bold else scale
        for ch in s:
            g = glyph(ch)
            for row, bits in enumerate(g):
                for col, bit in enumerate(bits):
                    if bit == '#':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       pw, scale, c)
            cx += 6 * scale
        return cx

    def text_centred(self, s, cx, y, scale, c, bold=False):
        self.text(s, cx - text_width(s, scale) // 2, y, scale, c, bold=bold)

    def para(self, s, x, y, scale, max_w, c, leading=None, bold=False):
        """Wrapped paragraph; returns the y just past the last line."""
        lh = leading if leading is not None else 9 * scale
        for line in wrap(s, scale, max_w):
            self.text(line, x, y, scale, c, bold=bold)
            y += lh
        return y


# ---------------------------------------------------------------- scenes
def draw_sunset(cv, x, y, w, h):
    """Vice City sunset: banded sky, striped sun, palms, skyline, road."""
    bands = [((64, 32, 96), 0.00), ((150, 40, 110), 0.28),
             ((232, 84, 60), 0.55), ((245, 150, 60), 0.78),
             ((250, 200, 90), 1.00)]
    for (col, f0), (_, f1) in zip(bands, bands[1:] + [(None, 1.0)]):
        cv.fill_rect(x, y + int(h * f0), w, int(h * (f1 - f0)) + 1, col)
    # striped sun, upper right
    sx, sy, sr = x + w - 78, y + 52, 36
    cv.disc(sx, sy, sr, (250, 224, 130))
    for dy in (-8, 4, 16):
        cv.fill_rect(sx - sr, sy + dy, sr * 2, 5, (232, 84, 60))
    # skyline silhouettes
    base = y + h - 46
    bx = x + 6
    heights = [52, 34, 66, 44, 78, 38, 58, 30, 70, 48]
    for hh in heights:
        bw = 26
        cv.fill_rect(bx, base - hh, bw, hh + 46, (38, 18, 52))
        for wy in range(base - hh + 8, base - 6, 12):
            cv.fill_rect(bx + 6, wy, 4, 5, (250, 200, 90))
        bx += bw + 4
    # road with dashes
    cv.fill_rect(x, y + h - 22, w, 22, (28, 14, 40))
    for dx in range(x + 8, x + w - 12, 30):
        cv.fill_rect(dx, y + h - 12, 16, 3, (250, 200, 90))
    # two palms, left and right
    for px, lean in ((x + 34, -14), (x + w - 40, 12)):
        top = (px + lean, y + 58)
        cv.line(px, y + 128, top[0], top[1], (28, 14, 40), 5)
        for ang in (-70, -35, 0, 35, 70):
            a = math.radians(ang - 90)
            ex = top[0] + int(30 * math.cos(a))
            ey = top[1] + int(30 * math.sin(a)) + 8
            cv.line(top[0], top[1], ex, ey, (28, 14, 40), 3)


def draw_shenzhen(cv, x, y, w, h):
    """Three flags over a Shenzhen skyline, gold deal disc below."""
    cv.fill_rect(x, y, w, h, SKY)
    # skyline, two depths
    for bx, bh, col in ((x + 4, 58, (120, 134, 148)),
                        (x + 52, 84, (96, 110, 124)),
                        (x + 108, 66, (120, 134, 148)),
                        (x + 158, 96, (88, 100, 114)),
                        (x + 214, 70, (120, 134, 148)),
                        (x + 262, 52, (96, 110, 124))):
        cv.fill_rect(bx, y + h - 44 - bh, 44, bh + 44, col)
    # ground
    cv.fill_rect(x, y + h - 44, w, 44, (74, 84, 96))
    # three flagpoles and flags
    pole_tops = y + 26
    pole_bot = y + h - 44
    flags = [
        (x + 44, 'us'), (x + 136, 'cn'), (x + 228, 'ru'),
    ]
    for fx, kind in flags:
        cv.vline(fx, pole_tops, pole_bot - pole_tops, (40, 40, 40), 3)
        fw, fh = 46, 28
        if kind == 'us':
            for i in range(7):
                cv.fill_rect(fx + 2, pole_tops + i * 4, fw, 4,
                             (176, 42, 48) if i % 2 == 0 else PAPER)
            cv.fill_rect(fx + 2, pole_tops, 20, 16, NAVY)
        elif kind == 'cn':
            cv.fill_rect(fx + 2, pole_tops, fw, fh, (206, 32, 32))
            cv.star(fx + 12, pole_tops + 9, 6, 3, GOLD)
            cv.star(fx + 28, pole_tops + 6, 3, 1, GOLD)
            cv.star(fx + 33, pole_tops + 13, 3, 1, GOLD)
        else:
            cv.fill_rect(fx + 2, pole_tops, fw, 9, PAPER)
            cv.fill_rect(fx + 2, pole_tops + 9, fw, 10, (36, 84, 180))
            cv.fill_rect(fx + 2, pole_tops + 19, fw, 9, (206, 32, 32))
    # gold disc with a check = the deal
    cx, cy = x + w // 2, y + h - 78
    cv.disc(cx, cy, 24, GOLD)
    cv.ring(cx, cy, 24, (150, 118, 30), 2)
    cv.polyline([(cx - 11, cy), (cx - 3, cy + 9), (cx + 12, cy - 10)],
                (30, 30, 30), 4)


def draw_ipo(cv, x, y, w, h):
    """Anthropic IPO: giant gold $83, ticker line, rising bars + trend."""
    cv.fill_rect(x, y, w, h, NAVY_DEEP)
    cv.text("$83", x + 16, y + 14, 7, GOLD)
    cv.text("ANT \u00b7 NASDAQ", x + 18, y + 66, 2, PAPER)
    # rising bars
    base = y + h - 16
    bars = [34, 52, 44, 66, 84]
    bw, gap = 34, 14
    bx = x + 22
    tops = []
    for bh in bars:
        cv.fill_rect(bx, base - bh, bw, bh, GREEN)
        tops.append((bx + bw // 2, base - bh - 8))
        bx += bw + gap
    # trend line with arrowhead
    cv.polyline(tops, GREEN_LT, 4)
    ax, ay = tops[-1]
    cv.polygon([(ax + 16, ay - 12), (ax + 2, ay - 2), (ax + 16, ay + 4)],
               GREEN_LT)


# ---------------------------------------------------------------- icons
def icon_star(cv, x, y, s):
    cv.star(x + s // 2, y + s // 2, s // 2 - 6, (s // 2 - 6) // 2 + 2, PAPER)


def icon_drop(cv, x, y, s):
    cx, cy = x + s // 2, y + s // 2 + 6
    cv.polygon([(cx, y + 8), (cx - 16, cy + 2), (cx + 16, cy + 2)], PAPER)
    cv.disc(cx, cy + 2, 16, PAPER)


def icon_euro(cv, x, y, s):
    cv.text("\u20ac", x + 16, y + 12, 6, PAPER)


def icon_bridge(cv, x, y, s):
    cv.fill_rect(x + 10, y + s - 22, s - 20, 5, PAPER)          # deck
    cv.fill_rect(x + 16, y + 22, 6, s - 44, PAPER)              # tower L
    cv.fill_rect(x + s - 22, y + 22, 6, s - 44, PAPER)          # tower R
    pts = [(x + 16, y + 26)]
    for i in range(9):
        t = i / 8
        pts.append((int(x + 16 + t * (s - 32)),
                    int(y + 26 - 14 * math.sin(t * math.pi))))
    pts.append((x + s - 22, y + 26))
    cv.polyline(pts, PAPER, 3)


def icon_wind(cv, x, y, s):
    for j, yy in enumerate((y + 20, y + 34, y + 48)):
        pts = []
        for i in range(13):
            t = i / 12
            pts.append((int(x + 10 + t * (s - 26)),
                        int(yy + 4 * math.sin(t * math.pi * 2 + j))))
        cv.polyline(pts, PAPER, 3)
        cv.fill_rect(x + s - 18, yy - 2, 8, 3, PAPER)


def icon_brush(cv, x, y, s):
    cv.line(x + 16, y + s - 16, x + s - 26, y + 22, PAPER, 6)
    cv.polygon([(x + s - 26, y + 22), (x + s - 12, y + 16),
                (x + s - 14, y + 32)], PAPER)
    cv.fill_rect(x + 12, y + s - 20, 8, 8, PAPER)


def icon_scales(cv, x, y, s):
    cx = x + s // 2
    cv.vline(cx, y + 12, s - 30, PAPER, 4)
    cv.hline(x + 10, y + 18, s - 20, PAPER, 4)
    for sx in (x + 14, x + s - 14):
        cv.vline(sx, y + 18, 14, PAPER, 2)
        cv.polygon([(sx - 12, y + 32), (sx + 12, y + 32), (sx, y + 46)],
                   PAPER)
    cv.fill_rect(cx - 12, y + s - 16, 24, 5, PAPER)


def icon_capitol(cv, x, y, s):
    cx = x + s // 2
    cv.disc(cx, y + 34, 18, PAPER)
    cv.fill_rect(cx - 18, y + 34, 36, 6, PAPER)   # hide lower half
    cv.fill_rect(cx - 24, y + 40, 48, 8, PAPER)   # entablature
    cv.fill_rect(cx - 20, y + 48, 40, 12, PAPER)  # base
    cv.vline(cx, y + 10, 8, PAPER, 2)


ICONS = {
    'star': (NAVY, icon_star),
    'drop': (RED, icon_drop),
    'euro': ((138, 125, 43), icon_euro),
    'bridge': ((74, 74, 74), icon_bridge),
    'wind': ((46, 111, 183), icon_wind),
    'brush': ((123, 75, 166), icon_brush),
    'scales': ((46, 125, 107), icon_scales),
    'capitol': ((139, 46, 46), icon_capitol),
}


# ---------------------------------------------------------------- content
HEROES = [
    {
        'label': "LEAD \u00b7 VICE CITY",
        'headline': "GAMERS ENTER VICE CITY AS GTA VI ROLLS OUT",
        'sub': "ROCKSTAR'S EPIC LAUNCHES WORLDWIDE AFTER A 13-YEAR WAIT.",
        'scene': draw_sunset,
    },
    {
        'label': "DIPLOMACY \u00b7 SHENZHEN",
        'headline': "TRUMP, XI AND PUTIN SHAKE HANDS IN SHENZHEN",
        'sub': "TRILATERAL TALKS AT THE APEC SUMMIT; UKRAINE ON THE AGENDA.",
        'scene': draw_shenzhen,
    },
    {
        'label': "MARKETS \u00b7 IPO",
        'headline': "ANTHROPIC DEBUTS AT $83 IN THE BIGGEST IPO EVER",
        'sub': "$81.3BN RAISED \u2014 THE LARGEST STOCK MARKET DEBUT IN HISTORY.",
        'scene': draw_ipo,
    },
]

GRID = [
    ('star', "SPACE", "VOYAGER 1 HITS ONE LIGHT-DAY OUT",
     "50 YEARS ON, THE PROBE IS 16 BILLION MILES AWAY."),
    ('drop', "THE GULF", "U.S. AND IRAN TRADE FIRE AGAIN",
     "TEHRAN WIDENS ATTACKS TO KUWAIT AND BAHRAIN."),
    ('euro', "UKRAINE", "EU PROPOSES \u20ac45BN UKRAINE LOAN",
     "REPAID AFTER RUSSIA PAYS REPARATIONS."),
    ('bridge', "WAR", "CRIMEAN BRIDGE ATTACKED AGAIN",
     "RUSSIAN OFFICIALS REPORT A FRESH STRIKE."),
    ('wind', "WEATHER", "CYCLONE AKVAN NEARS INDIA'S COAST",
     "LANDFALL EXPECTED BETWEEN MACHILIPATNAM AND PURI."),
    ('brush', "ART", "VAN GOGH SELLS FOR RECORD $190.4M",
     "PRICE ROW OVER ITS NAZI-ERA HISTORY."),
    ('scales', "JUSTICE", "MYANMAR FACES GENOCIDE VERDICT",
     "UN COURT RULES ON THE ROHINGYA CASE."),
    ('capitol', "UNITED STATES", "JEFFRIES SET TO BE FIRST BLACK SPEAKER",
     "DEMOCRATS NOMINATE HIM TO LEAD THE HOUSE."),
]

NUMBERS = [
    ("$81.3BN", "ANTHROPIC IPO"),
    ("$190.4M", "VAN GOGH SALE"),
    ("16BN MI", "VOYAGER 1 OUT"),
    ("\u20ac45BN", "EU UKRAINE LOAN"),
    ("19", "KILLED IN JET CRASH"),
]

FOOTER_1 = "COMPILED FROM BBC, REUTERS, AP, AL JAZEERA AND NPR REPORTING OF 19 NOVEMBER 2026."
FOOTER_2 = ("ALSO: ISRAELI GROUND OPERATION IN GAZA \u00b7 RUSSIAN JET CRASH KILLS 19 "
            "IN SIBERIA \u00b7 FINLAND OKS FIRST NUCLEAR WASTE STORE")


# ---------------------------------------------------------------- build
def build():
    cv = Canvas(W, H, CREAM)
    mx = 28  # side margin

    # masthead
    cv.fill_rect(0, 0, W, 92, NAVY)
    cv.text_centred("THE WORLD IN ONE PICTURE", W // 2, 16, 5, PAPER,
                    bold=True)
    cv.text_centred("THURSDAY 19 NOVEMBER 2026 \u00b7 12 STORIES \u00b7 6 CONTINENTS",
                    W // 2, 60, 2, GOLD)
    cv.fill_rect(0, 92, W, 6, RED)

    # kicker
    cv.text_centred("THE DAY VICE CITY OPENED \u2014 AND THREE LEADERS SHOOK HANDS",
                    W // 2, 110, 2, RED)

    # three hero panels
    pw, gap = 312, 16
    hy, hh = 134, 292
    img_h, txt_h = 186, 106
    for i, hero in enumerate(HEROES):
        px = mx + i * (pw + gap)
        cv.fill_rect(px, hy, pw, hh, PAPER)
        cv.outline(px, hy, pw, hh, LINE, 1)
        hero['scene'](cv, px, hy, pw, img_h)
        ty = hy + img_h
        cv.text(hero['label'], px + 12, ty + 10, 1, RED)
        y = cv.para(hero['headline'], px + 12, ty + 28, 2, pw - 24,
                    INK, leading=17, bold=True)
        cv.para(hero['sub'], px + 12, y + 4, 1, pw - 24, GREY, leading=10)

    # grid header
    gy = hy + hh + 16
    cv.text("MORE FROM THURSDAY", mx, gy, 2, RED)

    # eight-story grid, 2 columns x 4 rows
    cw, ch, cgap, rgap = 476, 100, 16, 8
    gy += 26
    for i, (icon, cat, head, sub) in enumerate(GRID):
        row, col = divmod(i, 2)
        cx = mx + col * (cw + cgap)
        cy = gy + row * (ch + rgap)
        cv.fill_rect(cx, cy, cw, ch, PAPER)
        cv.outline(cx, cy, cw, ch, LINE, 1)
        bg, draw = ICONS[icon]
        cv.fill_rect(cx + 12, cy + 14, 72, 72, bg)
        draw(cv, cx + 12, cy + 14, 72)
        tx = cx + 98
        cv.text(cat, tx, cy + 12, 1, RED)
        y = cv.para(head, tx, cy + 28, 2, cw - 110, INK, leading=17,
                    bold=True)
        cv.para(sub, tx, y + 3, 1, cw - 110, GREY, leading=10)

    # numbers strip
    ny = gy + 4 * ch + 3 * rgap + 14
    cv.fill_rect(0, ny, W, 60, NAVY)
    cell = (W - 2 * mx) // 5
    for i, (num, lab) in enumerate(NUMBERS):
        ccx = mx + i * cell + cell // 2
        cv.text_centred(num, ccx, ny + 8, 3, GOLD)
        cv.text_centred(lab, ccx, ny + 36, 1, CREAM)

    # footer
    fy = ny + 60 + 12
    cv.text(FOOTER_1, mx, fy, 1, GREY)
    cv.text(FOOTER_2, mx, fy + 12, 1, GREY)

    final_y = fy + 12 + 7
    assert final_y <= H, f"layout overflow: final y {final_y} > {H}"
    return cv, final_y


# ---------------------------------------------------------------- png out
def _chunk(typ, data):
    out = struct.pack('>I', len(data)) + typ + data
    out += struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
    return out


def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    blob = (b'\x89PNG\r\n\x1a\n'
            + _chunk(b'IHDR', ihdr)
            + _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + _chunk(b'IEND', b''))
    Path(path).write_bytes(blob)
    return len(blob)


def main():
    cv, final_y = build()
    out = Path(__file__).resolve().parent / 'assets' / 'entry.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    size = write_png(out, cv)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"wrote {out} ({size} bytes, sha256 {digest})")
    print(f"layout final y = {final_y} of {H}")


if __name__ == '__main__':
    main()
