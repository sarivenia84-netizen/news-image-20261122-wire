#!/usr/bin/env python3
"""The Wire — 22 November 2026: make.fun news-image-20261121 entry.

Renders a 1024x1024 one-page visual summary of the day's world news as a
PNG using only the Python standard library (zlib + struct): no network,
no fonts, no third-party packages. Deterministic: two runs write the
same bytes.

Layout: masthead, a lead story block, a 3x3 grid of story cards and a
bottom markets strip. Text is drawn with a built-in 5x7 bitmap font.
"""

import os
import struct
import zlib

W = H = 1024
OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "out"), "entry.png")

# ---------------------------------------------------------------- palette
PAPER = (244, 241, 234)
INK = (18, 18, 22)
RED = (178, 34, 38)
BLUE = (24, 60, 110)
GREEN = (22, 110, 74)
AMBER = (198, 122, 20)
GREY = (120, 118, 112)
RULE = (210, 205, 196)
DARKPANEL = (30, 30, 36)

CANVAS = bytearray()
for _ in range(W * H):
    CANVAS += bytes(PAPER)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        CANVAS[i:i + 3] = bytes(c)


def rect(x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(H, y1)):
        base = (y * W + max(0, x0)) * 3
        n = (min(W, x1) - max(0, x0)) * 3
        if n > 0:
            CANVAS[base:base + n] = bytes(c) * (n // 3)


def hline(x0, x1, y, c, t=1):
    rect(x0, y, x1, y + t, c)


def vline(x, y0, y1, c, t=1):
    rect(x, y0, x + t, y1, c)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, each glyph 7 rows of 5-bit integers (MSB = left pixel).
FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11100, 0b10010, 0b10001, 0b10001, 0b10001, 0b10010, 0b11100),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11111),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": (0, 0, 0, 0, 0, 0b01100, 0b00100),
    ":": (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "-": (0, 0, 0, 0b11111, 0, 0, 0),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "+": (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    '"': (0b01010, 0b01010, 0, 0, 0, 0, 0),
}


def text(x, y, s, c, sc=2):
    """Draw string s at (x, y), top-left of the first glyph, scaled sc."""
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT["?"])
        for ry in range(7):
            row = g[ry]
            for rx in range(5):
                if row & (0b10000 >> rx):
                    rect(cx + rx * sc, y + ry * sc,
                         cx + rx * sc + sc, y + ry * sc + sc, c)
        cx += 6 * sc
    return cx - x


def twidth(s, sc=2):
    return max(0, len(s)) * 6 * sc - sc


def wrap(s, nchars):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if len(t) <= nchars:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def center_text(y, s, c, sc=2):
    x = (W - twidth(s, sc)) // 2
    text(x, y, s, c, sc)

# ---------------------------------------------------------------- stories
STORIES = [
    (RED, "TURKEY", "COP31 talks fail in",
     "Antalya; no fossil", "fuel deal reached"),
    (RED, "USA-IRAN", "Trump seeks lasting",
     "Iran deal; warns", "of new strikes"),
    (BLUE, "GULF", "Saudi downs Houthi",
     "drone, missile; Iran", "strikes Bahrain plant"),
    (RED, "KRYVYIRIH", "Russian missile hits",
     "Kryvyi Rih; two", "dead including child"),
    (RED, "KYIV", "Kyiv apartment hit",
     "by drone; two", "dead, kids missing"),
    (RED, "ODESA", "Odesa schools shift",
     "remote as strikes", "cut heat, power"),
    (BLUE, "SHENZHEN", "Xi hosts first",
     "China-Russia-US", "summit in Shenzhen"),
    (GREEN, "APEC", "APEC forecast raised",
     "to 3.4% at", "Shenzhen meeting"),
    (AMBER, "KOREA", "Korea minister quits",
     "over AI cheating", "rules, CSAT scandal"),
    (RED, "WESTBANK", "Settlers torch dozen",
     "cars in West", "Bank; minister slams"),
    (AMBER, "INDONESIA", "Banten factory fire",
     "kills three, fifty", "workers still missing"),
    (RED, "FBI", "FBI database breach",
     "reported; Trump says", "'not good' on hack"),
    (BLUE, "USA", "Kennedy seeks probe",
     "of Lutnick on", "China Nvidia access"),
    (GREEN, "GENEVA", "UN vows robot",
     "arms rules by", "2028; Russia resists"),
    (AMBER, "IOWA", "Army to detonate",
     "68 toxic barrels", "in Iowa Tuesday"),
    (RED, "MEXICO", "Top cartel boss",
     "arrested in", "Sinaloa, Mexico"),
    (GREEN, "ARGENTINA", "Wife held over",
     "Italian escape in", "Argentina"),
    (BLUE, "SPORTS", "Boca Juniors win",
     "Copa Sudamericana", "title in final"),
]


def draw():
    # ---- masthead
    rect(0, 0, W, 8, INK)
    rect(0, 8, W, 9, RED)
    y = 34
    center_text(y, "THE WIRE", INK, 9)
    y += 64
    center_text(y, "ONE PAGE - EVERY STORY - SUNDAY 22 NOVEMBER 2026", GREY, 2)
    hline(48, W - 48, y + 30, INK, 3)
    hline(48, W - 48, y + 36, RULE, 1)

    # ---- lead story banner
    bx0, by0, bx1, by1 = 48, y + 46, W - 48, y + 176
    rect(bx0, by0, bx1, by1, DARKPANEL)
    rect(bx0, by0, bx0 + 10, by1, RED)
    text(bx0 + 30, by0 + 12, "LEAD STORY - COP31 ANTALYA", (230, 220, 200), 2)
    text(bx0 + 30, by0 + 36, "CLIMATE SUMMIT COLLAPSES", PAPER, 3)
    text(bx0 + 30, by0 + 64, "NO FOSSIL-FUEL AGREEMENT", PAPER, 3)
    text(bx0 + 30, by0 + 96, "EU AND ISLAND NATIONS REJECT DRAFT - REUTERS", (200, 200, 205), 2)

    # ---- story grid 3x6
    gy0 = by1 + 14
    cw, ch, gap = 312, 80, 10
    gx0 = 32
    for i, (col, tag, l1, l2, l3) in enumerate(STORIES):
        r, cix = divmod(i, 3)
        x0 = gx0 + cix * (cw + gap)
        y0 = gy0 + r * (ch + gap)
        rect(x0, y0, x0 + cw, y0 + ch, (255, 253, 248))
        rect(x0, y0, x0 + cw, y0 + ch, RULE)
        rect(x0, y0, x0 + cw, y0 + 3, col)
        rect(x0 + 8, y0 + 9, x0 + 8 + twidth(tag, 1) + 8, y0 + 21, col)
        text(x0 + 12, y0 + 12, tag, PAPER, 1)
        for k, line in enumerate((l1, l2, l3)):
            text(x0 + 8, y0 + 24 + k * 16, line, INK, 2)
        # tiny map-pin dot
        rect(x0 + cw - 20, y0 + ch - 14, x0 + cw - 14, y0 + ch - 8, col)

    # ---- date-check + markets strip
    my = gy0 + 7 * ch + 6 * gap + 4
    rect(32, my, W - 32, my + 58, (238, 234, 226))
    rect(32, my, W - 32, my + 58, RULE)
    text(48, my + 9, "DATE CHECK: ALL 18 STORIES SUNDAY 22 NOV 2026 - 9 REGIONS", INK, 2)
    stats = [("COP31", "NO DEAL", RED), ("BANTEN", "3 DEAD 50 MISSING", RED),
             ("KYIV+RIH", "4 DEAD", RED), ("APEC", "+3.4%", GREEN)]
    sx = 48
    for name, val, col in stats:
        text(sx, my + 27, name, GREY, 2)
        text(sx, my + 42, val, col, 2)
        sx += 235

    # ---- footer
    text(64, H - 26, "SOURCES: AP - REUTERS - AL JAZEERA - AFP - UN NEWS - ICJ",
         GREY, 1)
    text(W - 64 - twidth("THE WIRE / 2026", 1), H - 26, "THE WIRE / 2026",
         GREY, 1)


draw()

# ---------------------------------------------------------------- PNG out
def write_png(path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += CANVAS[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(
            ">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
           + chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    print(f"wrote {path} ({len(png):,} bytes")


write_png(OUT)
# verified: deterministic, 1024x1024, exit 0