#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Sunday 22 November 2026.

A one-page visual summary of the day's world news: 30 date-checked stories
across 6 regions, rendered as a 1024x1024 PNG using only the Python standard
library (zlib + struct). No network, no fonts, no third-party packages.
Deterministic: two runs write identical bytes.

Sections: top bar, serif masthead, red subheadline, stat band, region nav,
day-in-UTC strip, three lead stories with vector illustrations, twelve
medium cards, dotted world map with numbered markers, a two-column
"also on Sunday" list, a DATE CHECK strip and a sources/certainty footer.
"""

import os
import struct
import zlib

W = H = 1024

# ---------------------------------------------------------------- palette
PAPER = (243, 239, 230)
CARD = (250, 247, 240)
INK = (21, 24, 30)
RED = (176, 32, 36)
DEEPRED = (128, 18, 22)
BLUE = (22, 58, 106)
NAVY = (24, 34, 52)
GREEN = (20, 96, 70)
AMBER = (176, 108, 20)
GREY = (110, 108, 102)
RULE = (206, 200, 188)
CREAMTXT = (232, 224, 208)

OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "out"), "entry.png")

CANVAS = bytearray(bytes(PAPER) * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        CANVAS[i:i + 3] = bytes(c)


def rect(x0, y0, x1, y1, c):
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for y in range(y0, y1):
        i = (y * W + x0) * 3
        CANVAS[i:i + len(row)] = row


def hline(x0, x1, y, c, t=1):
    rect(x0, y, x1, y + t, c)


def vline(x, y0, y1, c, t=1):
    rect(x, y0, x + t, y1, c)


def frame(x0, y0, x1, y1, c, t=1):
    rect(x0, y0, x1, y0 + t, c)
    rect(x0, y1 - t, x1, y1, c)
    rect(x0, y0, x0 + t, y1, c)
    rect(x1 - t, y0, x1, y1, c)


# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph: 7 rows of 5-bit ints, MSB = leftmost pixel.
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
    "a": (0, 0b01110, 0b00001, 0b01111, 0b10001, 0b10001, 0b01111),
    "b": (0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b11110),
    "c": (0, 0b01110, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "d": (0b00001, 0b00001, 0b01111, 0b10001, 0b10001, 0b10001, 0b01111),
    "e": (0, 0b01110, 0b10001, 0b11111, 0b10000, 0b10001, 0b01110),
    "f": (0b00110, 0b01001, 0b01000, 0b11100, 0b01000, 0b01000, 0b01000),
    "g": (0, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "h": (0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "i": (0b00100, 0, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110),
    "j": (0b00010, 0, 0b00110, 0b00010, 0b00010, 0b10010, 0b01100),
    "k": (0b10000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "l": (0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "m": (0, 0b11010, 0b11111, 0b10101, 0b10101, 0b10101, 0b10101),
    "n": (0, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001),
    "o": (0, 0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "p": (0, 0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000),
    "q": (0, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b00001),
    "r": (0, 0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10000),
    "s": (0, 0b01111, 0b10000, 0b01110, 0b00001, 0b10001, 0b01110),
    "t": (0b01000, 0b01000, 0b11100, 0b01000, 0b01000, 0b01001, 0b00110),
    "u": (0, 0b10001, 0b10001, 0b10001, 0b10001, 0b10011, 0b01101),
    "v": (0, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "w": (0, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "x": (0, 0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001),
    "y": (0, 0b10001, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "z": (0, 0b11111, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
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
    "*": (0, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0),
    "=": (0, 0, 0b11111, 0, 0b11111, 0, 0),
    ">": (0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000),
    "<": (0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010),
    "#": (0b01010, 0b11111, 0b01010, 0b01010, 0b01010, 0b11111, 0b01010),
    "~": (0, 0, 0b01001, 0b10101, 0b10010, 0, 0),
    "1/2": (0b00100, 0b00100, 0b11111, 0b00100, 0b11111, 0, 0b00100),
}


def text(x, y, s, c, sc=1):
    """Draw s at (x, y) - top-left of first glyph - scaled by sc."""
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT["?"])
        for ry in range(7):
            row = g[ry]
            if not row:
                continue
            for rx in range(5):
                if row & (0b10000 >> rx):
                    rect(cx + rx * sc, y + ry * sc,
                         cx + rx * sc + sc, y + ry * sc + sc, c)
        cx += 6 * sc
    return cx - x


def twidth(s, sc=1):
    return max(0, len(s)) * 6 * sc - sc


def bold_text(x, y, s, c, sc=1):
    """Pseudo-bold: double strike offset by one pixel."""
    text(x, y, s, c, sc)
    text(x + 1, y, s, c, sc)


def center_text(y, s, c, sc=1, x0=0, x1=W):
    x = x0 + (x1 - x0 - twidth(s, sc)) // 2
    text(x, y, s, c, sc)
    return x


def wrap(s, nchars):
    words, lines, cur = [], [], ""
    for w_ in s.split():
        if len(w_) > nchars and "-" in w_:
            parts = w_.split("-")
            words.append(parts[0] + "-")
            words.extend(p + "-" for p in parts[1:-1])
            words.append(parts[-1])
        else:
            words.append(w_)
    for w_ in words:
        t = (cur + " " + w_).strip()
        if len(t) <= nchars:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- stories
# cert: REPORTED / CLAIM / FORECAST. marker: (map col, row) or None.
# Illustration key drives the small vector art block.
S = [
    dict(id=1, region="EUROPE", place="KYIV REGION, UKRAINE", cert="REPORTED",
         head="Russia fires 153 drones overnight; Kyiv flats hit",
         body="A night wave of 153 strike drones hit Kyiv region - an apartment block was struck and collapsed with children among the missing. In Zelenskyy's hometown Kryvyi Rih a ballistic-missile strike left 73 injured, nine of them children. (AP; Reuters)",
         src="AP / Reuters", art="drones", marker=(35, 5), mk="1"),
    dict(id=2, region="EUROPE", place="ANTALYA, TURKIYE", cert="REPORTED",
         head="COP31 collapses: final draft omits fossil fuels",
         body="Two days into overtime, the presidency draft made no mention of coal, oil or gas. The EU and island states rejected the 'Antalya Pact' - 'it does not meet the moment' - and no deal was approved at the closing plenary. (Al Jazeera; Reuters)",
         src="Reuters / Al Jazeera", art="cop", marker=(36, 8), mk="2"),
    dict(id=3, region="MIDDLE EAST", place="MANAMA, BAHRAIN", cert="CLAIM",
         head="Iran-linked strikes hit Bahrain; Saudi downs Houthi fire",
         body="Bahrain says an Iranian attack struck a civilian industrial facility, starting a fire and hurting two; Iranian state media says the IRGC targeted US facilities. Saudi Arabia intercepted a Houthi drone and missile. Iran's FM says talks remain open. (CNBC)",
         src="CNBC / Xinhua", art="gulf", marker=(38, 10), mk="3"),
    dict(id=4, region="ASIA-PACIFIC", place="SHENZHEN, CHINA", cert="REPORTED",
         head="First China-Russia-US summit opens in Shenzhen",
         body="Xi Jinping hosts Putin and Trump in Shenzhen for the first-ever trilateral summit; Trump hails 'one of the most momentous in years'. (Xinhua)", src="Xinhua", art="summit", marker=(49, 11), mk="4"),
    dict(id=5, region="ASIA-PACIFIC", place="SHENZHEN, CHINA", cert="FORECAST",
         head="APEC closes with 2026 growth upgraded to 3.4%",
         body="Xi chairs the 33rd APEC leaders' meeting, hailing an 'Asia-Pacific miracle' community; the bloc's 2026 growth forecast is raised to 3.4%. (Xinhua)", src="Xinhua", art="chartup", marker=(50, 12), mk="5"),
    dict(id=6, region="ASIA-PACIFIC", place="SEOUL, SOUTH KOREA", cert="REPORTED",
         head="Seoul minister quits over CSAT AI-cheating rules",
         body="Education Minister Choi Kyo-jin resigns after the college-entrance exam's anti-AI cheating rules sparked a national scandal. (NYT)", src="NYT", art="robot", marker=(51, 8), mk="6"),
    dict(id=7, region="MIDDLE EAST", place="WEST BANK", cert="REPORTED",
         head="Settlers torch cars across the West Bank",
         body="At least a dozen cars are torched and homes vandalised in settler attacks; a rival Israeli minister decries 'Jewish terrorism'. (CNN)", src="CNN", art="flame", marker=(36, 9), mk="7"),
    dict(id=8, region="ASIA-PACIFIC", place="BANTEN, INDONESIA", cert="REPORTED",
         head="Candy factory fire: 3 dead, about 50 missing",
         body="A massive blaze tears through a factory in Banten province; at least three workers are dead and around 50 are still missing as crews fight hotspots. (Wires)", src="Wires", art="flame", marker=(48, 17), mk="8"),
    dict(id=9, region="AMERICAS", place="WASHINGTON, USA", cert="REPORTED",
         head="FBI criminal-justice database reported hacked",
         body="A breach of the FBI's criminal-justice database is reported; Trump says it is 'not good' but 'could have some benefits'. (Euronews)", src="Euronews", art="lock", marker=(17, 7), mk="9"),
    dict(id=10, region="AMERICAS", place="WASHINGTON, USA", cert="REPORTED",
         head="Senator urges probe of Lutnick over Nvidia-to-China",
         body="Sen. John Kennedy calls on Congress to scrutinise Commerce Secretary Lutnick over Chinese access to Nvidia chips. (WaPo)", src="WaPo", art="chip", marker=(14, 6), mk="10"),
    dict(id=11, region="EUROPE", place="GENEVA, SWITZERLAND", cert="REPORTED",
         head="UN pledges 'killer robot' rules by 2028",
         body="UN talks end with a pledge to regulate autonomous weapons by 2028 - an outcome weakened by Russia's opposition. (CNBC)", src="CNBC", art="robot", marker=(31, 6), mk="11"),
    dict(id=12, region="AMERICAS", place="IOWA, USA", cert="REPORTED",
         head="Army to blow up 68 toxic barrels in Iowa",
         body="The US Army says it will detonate 68 barrels of toxic lead azide by Tuesday under emergency powers, bypassing a court order. (Reuters)", src="Reuters", art="barrel", marker=(13, 7), mk="12"),
    dict(id=13, region="AMERICAS", place="SINALOA, MEXICO", cert="REPORTED",
         head="FBI most-wanted drug lord seized in Sinaloa",
         body="A cartel boss on the FBI most-wanted list is arrested by Mexican forces in Sinaloa. (Wire)", src="Wire", art="cuff", marker=(12, 10), mk="13"),
    dict(id=14, region="AFRICA", place="BENGHAZI, LIBYA", cert="REPORTED",
         head="Russian corvette Merkury sunk at Benghazi",
         body="An early-Sunday explosion, suspected drone attack, capsizes and sinks the Russian navy corvette Merkury at the Benghazi naval base; injuries, no deaths reported. (DW)", src="DW", art="ship", marker=(33, 9), mk="14"),
    dict(id=15, region="EUROPE", place="GULF OF FINLAND", cert="REPORTED",
         head="Ukrainian drone hits sanctioned ship Sparta II",
         body="A Ukrainian drone strike sets the sanctioned Russian cargo ship Sparta II ablaze in the Gulf of Finland; Finland's PM says the war is 'spilling over'. (Guardian)", src="Guardian", art="ship", marker=(34, 3), mk="15"),
    dict(id=16, region="MIDDLE EAST", place="RIYADH, SAUDI ARABIA", cert="CLAIM",
         head="Houthis hit Saudi refinery and radar",
         body="Houthi forces strike a Saudi oil refinery and radar site; Riyadh says at least six people were hurt. (Reuters)", src="Reuters", art="flame", marker=(38, 11), mk="16"),
    dict(id=17, region="MIDDLE EAST", place="MANAMA, BAHRAIN", cert="CLAIM",
         head="IRGC says it struck two US bases in Bahrain",
         body="Iran's IRGC claims missile and drone strikes on two US bases; the UAE condemns the renewed attacks. (Xinhua)", src="Xinhua", art="gulf", marker=(39, 11), mk="17"),
    dict(id=18, region="ASIA-PACIFIC", place="PYONGYANG, DPRK", cert="REPORTED",
         head="Kim rebuffs Trump's talks offer",
         body="Kim Jong-un rejects Trump's outreach, stresses 'sovereignty' and quietly expands the nuclear arsenal. (Wires)", src="Wires", art="rocket", marker=(51, 7), mk="18"),
    dict(id=19, region="EUROPE", place="BRUSSELS, EU", cert="FORECAST",
         head="EU must rush about 70bn euros to Ukraine",
         body="Kyiv's financial needs put the EU under pressure to fast-track roughly 70bn euros in fresh Ukraine aid. (Reuters)", src="Reuters", art="chartup", marker=(31, 5), mk="19"),
    dict(id=20, region="AFRICA", place="KHARTOUM, SUDAN", cert="REPORTED",
         head="Drone strikes hit UN building in Khartoum",
         body="Drone strikes hit a UN building in a residential area of the Sudanese capital. (DW)", src="DW", art="flame", marker=(35, 12), mk="20"),
    dict(id=21, region="ASIA-PACIFIC", place="TAIPEI, TAIWAN", cert="REPORTED",
         head="Taiwan bans short selling as AI slump sinks stocks",
         body="The FSC completely prohibits short selling below the closing price as the AI downturn sinks Asian equities. (Fri 20 Nov)", src="Wires", art="chartdown", marker=(50, 10), mk="21"),
    dict(id=22, region="ASIA-PACIFIC", place="CANBERRA, AUSTRALIA", cert="REPORTED",
         head="COP31 backlash: resignation calls in Australia",
         body="Finger-pointing and resignation calls at home as the talks collapse; Pacific nations express despair. (Wires)", src="Wires", art="cop", marker=(55, 22), mk="22"),
    dict(id=23, region="WORLD", place="GULF OF OMAN", cert="REPORTED",
         head="Tanker incident reported in the Gulf of Oman",
         body="UKMTO says it received a report of an incident involving a tanker and military forces; investigations are ongoing. (Reuters)", src="Reuters", art="ship", marker=(41, 11), mk="23"),
    dict(id=24, region="WORLD", place="GLOBAL MARKETS", cert="REPORTED",
         head="Oil falls amid AI-driven equity sell-off",
         body="Crude slides as the global equity sell-off deepens; AI-sector concerns limit the losses. (Reuters)", src="Reuters", art="chartdown", marker=None, mk="24"),
    dict(id=25, region="MIDDLE EAST", place="WASHINGTON, USA", cert="CLAIM",
         head="Trump: 'permanent' Iran deal - or new strikes",
         body="Trump says he wants a permanent deal with Iran and is inclined to resume strikes after the New Year if talks fail; 'blockade runners will be sunk'. (CBS; Fox)", src="CBS / Fox", art="rocket", marker=(16, 8), mk="25"),
    dict(id=26, region="WORLD", place="WASHINGTON / BEIJING", cert="REPORTED",
         head="China opposes US FCC telecom access ban",
         body="Beijing objects to the US FCC ban on Chinese telecoms' direct access to US phone numbers. (Reuters)", src="Reuters", art="lock", marker=(18, 8), mk="26"),
    dict(id=27, region="EUROPE", place="ODESA, UKRAINE", cert="REPORTED",
         head="Odesa schools go remote as utilities fail",
         body="Russian strikes disrupt heating, electricity and water; Odesa's schools switch to remote learning. (WaPo)", src="WaPo", art="drones", marker=(36, 6), mk="27"),
    dict(id=28, region="AMERICAS", place="BUENOS AIRES, ARGENTINA", cert="REPORTED",
         head="Wife held over Italian fugitive's escape",
         body="The wife of an Italian fugitive is held over his daring escape in Argentina. (Wire)", src="Wire", art="cuff", marker=(20, 22), mk="28"),
    dict(id=29, region="AMERICAS", place="BUENOS AIRES, ARGENTINA", cert="REPORTED",
         head="Boca Juniors win the Copa Sudamericana",
         body="Boca Juniors lift the Copa Sudamericana trophy. (Rio Times)", src="Rio Times", art="trophy", marker=(21, 23), mk="29"),
    dict(id=30, region="EUROPE", place="WARSAW, POLAND", cert="REPORTED",
         head="Nato vows to defend 'every inch' of Poland",
         body="After two Russian missiles and a drone crashed in Poland, Rutte guarantees Nato will defend 'every inch' of its territory. (Guardian)", src="Guardian", art="shield", marker=(32, 5), mk="30"),
]

LEAD_IDS = [1, 2, 3]
MEDIUM_IDS = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
ALSO_IDS = [i for i in range(1, 31) if i not in LEAD_IDS and i not in MEDIUM_IDS]

REGION_COLORS = {
    "EUROPE": BLUE,
    "MIDDLE EAST": RED,
    "AMERICAS": AMBER,
    "ASIA-PACIFIC": GREEN,
    "AFRICA": (120, 60, 130),
    "WORLD": GREY,
}
REGION_ORDER = ["EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA-PACIFIC", "AFRICA", "WORLD"]

TIMELINE = [
    ("FRI 20", "Taiwan bans below-close short selling"),
    ("SAT 21", "UN agrees 'killer robot' rules; Sparta II hit"),
    ("SUN 22", "COP31 draft omits fossil fuels; no deal"),
    ("SUN 22", "Bahrain strikes; corvette sunk at Benghazi"),
    ("SUN 22", "153-drone night wave over Ukraine begins"),
    ("MON 23", "EU weighs 70bn-euro Ukraine aid package"),
]

DATE_CHECK = (
    "Left out as other days' news: the ~400-drone and 110-missile barrage (Thu 19-20 Nov); the 48-drone night right after and the "
    "Kryvyi Rih double-tap (Fri 20-Sat 21). Every story on this page is dated Sunday 22 November 2026 unless tagged Fri/Sat/Mon."
)

# ---------------------------------------------------------------- world map
MAP = [
    "                    ###        ##      #  ##      ####  ###### ######   ",
    "   ##     #########  #### ##   #### #     #### ### ####### #############",
    "  ####   ############## ####  #### ##  #   ## ############ #############",
    " ###### ###############  ###   ###  #      ## ############ #############",
    "      ###################       #          ##  ##########  #############",
    "        ################         #         ##   ########   ##########   ",
    "         ##############           #       ####  ### ###   ## ######     ",
    "          ##########               ##     ###### ## ## ## ##  ##  #     ",
    "           ########                 #    ########  ## ##   ##    #      ",
    "            ######                    #  ####### ##  #    #  #          ",
    "             ####                     #   ###### ## # #     #           ",
    "              ####                    ##  #### #  ## #     ## #         ",
    "               ###                     #   ### ##   ##     #### ##      ",
    "                ##                      #   #  #    #      ########     ",
    "                ####                     #   ##     # ###   ########    ",
    "                ######                        #  ## ###### ### ##       ",
    "                #######                        #   # ###### #  #        ",
    "                #######                             #  ####     #       ",
    "                ######                             #   ####    ## ##     ",
    "                 #####                             #    ###    #######   ",
    "                 ####                                  ##    ##########  ",
    "                 ###                                   #    ##########   ",
    "                 ###                                        ##########   ",
    "                 ###                                          #    ##    ",
    "                 ###                                               #      ",
    "                  ##                                                      ",
    "                  ##                                                      ",
]

MW, MH = 60, 27
CELL_W, CELL_H = 8, 4
DOT = 3

MAPX = 16
MAPW = MW * CELL_W
MAPH = MH * CELL_H


def draw_map_markers(y0):
    for s_ in S:
        if s_["marker"]:
            col, row = s_["marker"]
            cx = MAPX + col * CELL_W + CELL_W // 2
            cy = y0 + row * CELL_H + CELL_H // 2
            rect(cx - 5, cy - 5, cx + 5, cy + 5, RED)
            rect(cx - 4, cy - 4, cx + 4, cy + 4, (250, 120, 120))
            rect(cx - 3, cy - 3, cx + 3, cy + 3, RED)
            center_text(cy - 3, s_["mk"], PAPER, 1, cx - 6, cx + 6)


def draw_map(y0):
    rect(MAPX - 6, y0, MAPX + MAPW + 6, y0 + MAPH + 4, NAVY)
    for r, row in enumerate(MAP):
        for c, ch in enumerate(row):
            if ch == "#":
                x = MAPX + c * CELL_W + (CELL_W - DOT) // 2
                y = y0 + r * CELL_H + (CELL_H - DOT) // 2
                rect(x, y, x + DOT, y + DOT, (90, 110, 140))
    draw_map_markers(y0)


# ---------------------------------------------------------------- vector art
def art_drones(x, y, w, h):
    """Dark city block under a drone raid."""
    rect(x, y, x + w, y + h, NAVY)
    for bx in range(8, w - 20, 26):
        bh = 20 + (bx * 7) % 18
        rect(x + bx, y + h - bh, x + bx + 16, y + h, (46, 58, 82))
        for wy in range(h - bh + 3, h - 3, 6):
            for wx in range(bx + 3, bx + 13, 6):
                if (wx + wy) % 3:
                    rect(x + wx, y + wy, x + wx + 2, y + wy + 3, (222, 190, 90))
    for i, dx in enumerate((18, 44, 70)):
        dy = 10 + i * 9
        ax = x + (w - 24) - dx * 2 % (w - 30)
        rect(ax, y + dy, ax + 10, y + dy + 3, (200, 210, 225))
        rect(ax - 3, y + dy - 2, ax + 2, y + dy + 5, (200, 210, 225))
        rect(ax + 11, y + dy - 2, ax + 16, y + dy + 5, (200, 210, 225))


def art_cop(x, y, w, h):
    """Conference table, flags, crossed-out draft."""
    rect(x, y, x + w, y + h, NAVY)
    rect(x + 10, y + h - 16, x + w - 10, y + h - 12, (90, 74, 48))
    for px_ in range(14, w - 14, 22):
        rect(x + px_, y + h - 30, x + px_ + 8, y + h - 16, (70, 82, 110))
        rect(x + px_ + 2, y + h - 36, x + px_ + 6, y + h - 30, RED)
    rect(x + w // 2 - 14, y + 8, x + w // 2 + 14, y + 26, (238, 232, 214))
    for d in range(-16, 17, 2):
        px(x + w // 2 + d + (d + 16) // 8, y + 8 + (d + 16) // 2, RED)
        px(x + w // 2 + d + (d + 16) // 8, y + 26 - (d + 16) // 2, RED)


def art_gulf(x, y, w, h):
    """Missile arcs over sea toward radar + plant."""
    rect(x, y, x + w, y + h, NAVY)
    rect(x, y + h - 10, x + w, y + h, (30, 46, 70))
    rect(x + w - 42, y + h - 26, x + w - 10, y + h - 10, (60, 66, 80))
    rect(x + w - 34, y + h - 34, x + w - 22, y + h - 26, (90, 96, 110))
    rect(x + w - 31, y + h - 44, x + w - 27, y + h - 34, (220, 120, 40))
    rect(x + 8, y + 8, x + 12, y + 18, (220, 120, 40))
    rect(x + 8, y + 18, x + 16, y + 22, (220, 120, 40))
    rect(x + 22, y + 14, x + 26, y + 24, (220, 120, 40))
    rect(x + 22, y + 24, x + 30, y + 28, (220, 120, 40))
    rect(x + 36, y + h - 34, x + 52, y + h - 10, (70, 66, 78))
    rect(x + 40, y + h - 40, x + 46, y + h - 34, (226, 120, 50))


def art_simple(x, y, w, h, key):
    if key == "drones":
        art_drones(x, y, w, h)
        return
    if key == "cop":
        art_cop(x, y, w, h)
        return
    if key == "gulf":
        art_gulf(x, y, w, h)
        return
    rect(x, y, x + w, y + h, NAVY)
    acc = (222, 190, 90)
    if key == "summit":
        for px_ in (14, 34, 54):
            rect(x + px_, y + 14, x + px_ + 10, y + 30, (60, 72, 100))
            rect(x + px_ + 3, y + 8, x + px_ + 5, y + 14, acc)
    elif key == "chartup":
        for i in range(5):
            bh = 8 + i * 5
            rect(x + 10 + i * 11, y + 36 - bh, x + 18 + i * 11, y + 36, acc)
    elif key == "chartdown":
        for i in range(5):
            bh = 30 - i * 5
            rect(x + 10 + i * 11, y + 36 - bh, x + 18 + i * 11, y + 36, (200, 90, 80))
    elif key == "robot":
        rect(x + 26, y + 10, x + 40, y + 20, (70, 82, 110))
        rect(x + 24, y + 20, x + 42, y + 34, (90, 102, 130))
        rect(x + 28, y + 13, x + 31, y + 16, RED)
        rect(x + 35, y + 13, x + 38, y + 16, RED)
    elif key == "flame":
        rect(x + 28, y + 16, x + 40, y + 36, (200, 90, 60))
        rect(x + 32, y + 8, x + 38, y + 18, (230, 140, 60))
        rect(x + 16, y + 30, x + 56, y + 36, (60, 66, 80))
    elif key == "lock":
        rect(x + 26, y + 18, x + 44, y + 34, acc)
        rect(x + 30, y + 8, x + 40, y + 18, (90, 96, 110))
    elif key == "chip":
        rect(x + 26, y + 14, x + 44, y + 32, GREEN)
        rect(x + 30, y + 18, x + 40, y + 28, (24, 60, 40))
    elif key == "barrel":
        rect(x + 24, y + 10, x + 44, y + 36, (70, 66, 78))
        rect(x + 24, y + 18, x + 44, y + 22, RED)
    elif key == "cuff":
        rect(x + 24, y + 14, x + 30, y + 22, acc)
        rect(x + 38, y + 14, x + 44, y + 22, acc)
        rect(x + 24, y + 22, x + 44, y + 28, acc)
    elif key == "ship":
        rect(x + 14, y + 26, x + 54, y + 34, (70, 82, 110))
        rect(x + 26, y + 16, x + 40, y + 26, (90, 102, 130))
        rect(x + 42, y + 10, x + 46, y + 20, (200, 90, 80))
    elif key == "rocket":
        rect(x + 30, y + 8, x + 36, y + 26, (90, 102, 130))
        rect(x + 31, y + 4, x + 35, y + 8, RED)
        rect(x + 26, y + 26, x + 30, y + 32, (60, 72, 100))
        rect(x + 36, y + 26, x + 40, y + 32, (60, 72, 100))
    elif key == "shield":
        rect(x + 26, y + 8, x + 44, y + 26, BLUE)
        rect(x + 30, y + 14, x + 40, y + 30, (90, 102, 130))
    elif key == "trophy":
        rect(x + 28, y + 12, x + 40, y + 26, acc)
        rect(x + 32, y + 26, x + 36, y + 32, acc)
        rect(x + 26, y + 32, x + 42, y + 36, acc)
    else:
        rect(x + 24, y + 14, x + 44, y + 32, (70, 82, 110))


# ---------------------------------------------------------------- sections
MX = 14           # page margin
COLGAP = 10
INNER = W - 2 * MX


def draw_topbar():
    rect(0, 0, W, 24, INK)
    text(MX, 8, "THE WORLD IN ONE DAY", CREAMTXT, 1)
    s = "30 STORIES * 6 REGIONS * EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    text(W - MX - twidth(s, 1), 8, s, CREAMTXT, 1)
    rect(0, 24, W, 26, RED)


def draw_masthead():
    s = "Sunday 22 November 2026"
    sc = 7
    x = (W - twidth(s, sc)) // 2
    bold_text(x, 36, s, INK, sc)
    sub = ("153 drones over Ukraine in one night * COP31 ends with no deal on "
           "fossil fuels * Iran-linked strikes hit Bahrain as Saudi downs Houthi fire")
    center_text(100, sub, DEEPRED, 1)
    hline(MX, W - MX, 116, INK, 2)
    hline(MX, W - MX, 120, RULE, 1)


def draw_stats():
    stats = [
        ("153", "Drones fired over Ukraine in one night", RED),
        ("73", "Injured in Kryvyi Rih strike, 9 children", RED),
        ("44h", "COP31 overtime before the no-deal end", BLUE),
        ("70bn", "Euros in fresh EU aid sought for Kyiv", GREEN),
        ("3.4%", "APEC 2026 growth forecast, upgraded", GREEN),
    ]
    n = len(stats)
    cw = INNER // n
    rect(MX, 124, W - MX, 178, CARD)
    frame(MX, 124, W - MX, 178, RULE)
    for i, (num, cap, col) in enumerate(stats):
        x0 = MX + i * cw
        if i:
            vline(x0, 128, 174, RULE)
        center_text(136, num, col, 3, x0, x0 + cw)
        capl = wrap(cap, (cw - 8) // 6)
        yy = 162
        for ln in capl[:2]:
            center_text(yy, ln, GREY, 1, x0 + 4, x0 + cw - 4)
            yy += 8


def draw_navbar():
    counts = {r: sum(1 for s_ in S if s_["region"] == r) for r in REGION_ORDER}
    total = sum(counts.values())
    rect(MX, 178, W - MX, 196, INK)
    x = MX
    for r in REGION_ORDER:
        seg = max(1, int(round(INNER * counts[r] / total)))
        if x + seg > W - MX:
            seg = W - MX - x
        rect(x, 178, x + seg, 196, REGION_COLORS[r])
        s = "%s %d" % (r.replace("MIDDLE EAST", "MIDEAST")
                       .replace("ASIA-PACIFIC", "ASIA-PC"), counts[r])
        if twidth(s, 1) < seg - 8:
            text(x + 6, 184, s, PAPER, 1)
        x += seg
    rect(MX, 178, W - MX, 179, INK)
    rect(MX, 195, W - MX, 196, INK)


def draw_timeline():
    rect(MX, 202, W - MX, 224, (236, 232, 222))
    frame(MX, 202, W - MX, 224, RULE)
    rect(MX, 202, MX + 108, 224, INK)
    text(MX + 6, 210, "THE DAY IN UTC", CREAMTXT, 1)
    x = MX + 116
    for when, what in TIMELINE:
        if x + twidth(what, 1) + 10 > W - MX:
            break
        text(x, 208, when, RED, 1)
        text(x, 216, what, INK, 1)
        x += twidth(what, 1) + 22


LEAD_H = 214


def draw_leads(y0):
    cw = (INNER - 2 * COLGAP) // 3
    for i, sid in enumerate(LEAD_IDS):
        st = next(s_ for s_ in S if s_["id"] == sid)
        x0 = MX + i * (cw + COLGAP)
        rect(x0, y0, x0 + cw, y0 + LEAD_H, CARD)
        frame(x0, y0, x0 + cw, y0 + LEAD_H, RULE)
        art_simple(x0 + 1, y0 + 1, cw - 2, 64, st["art"])
        tagw = twidth(st["place"], 1) + 8
        rect(x0 + 1, y0 + 65, x0 + 1 + tagw, y0 + 77, REGION_COLORS[st["region"]])
        text(x0 + 5, y0 + 68, st["place"], PAPER, 1)
        cs = st["cert"]
        cc = GREY if cs == "REPORTED" else RED
        text(x0 + cw - twidth("* " + cs, 1) - 6, y0 + 68, "* " + cs, cc, 1)
        yy = y0 + 82
        hl = wrap(st["head"], (cw - 12) // 12)
        for ln in hl[:3]:
            bold_text(x0 + 6, yy, ln, INK, 2)
            yy += 16
        yy += 2
        bl = wrap(st["body"], (cw - 12) // 6)
        for ln in bl[:4]:
            text(x0 + 6, yy, ln, (52, 54, 58), 1)
            yy += 9
        text(x0 + 6, y0 + LEAD_H - 12, st["src"].upper(), GREY, 1)
    return y0 + LEAD_H


MED_H = 150


def draw_cards(y0):
    cw = (INNER - 5 * COLGAP) // 6
    for i, sid in enumerate(MEDIUM_IDS):
        r, cix = divmod(i, 6)
        st = next(s_ for s_ in S if s_["id"] == sid)
        x0 = MX + cix * (cw + COLGAP)
        yy0 = y0 + r * (MED_H + COLGAP)
        rect(x0, yy0, x0 + cw, yy0 + MED_H, CARD)
        frame(x0, yy0, x0 + cw, yy0 + MED_H, RULE)
        art_simple(x0 + 1, yy0 + 1, cw - 2, 34, st["art"])
        num = str(st["id"])
        rect(x0 + 1, yy0 + 35, x0 + 15, yy0 + 46, RED)
        text(x0 + 5, yy0 + 38, num, PAPER, 1)
        tag = ABBR.get(st["region"], st["region"])
        text(x0 + 19, yy0 + 38, tag, REGION_COLORS[st["region"]], 1)
        yy = yy0 + 50
        hl = wrap(st["head"], (cw - 10) // 12)
        for ln in hl[:3]:
            bold_text(x0 + 5, yy, ln, INK, 2)
            yy += 15
        yy += 2
        bl = wrap(st["body"], (cw - 10) // 6)
        for ln in bl[:2]:
            text(x0 + 5, yy, ln, (70, 72, 76), 1)
            yy += 9
        text(x0 + 5, yy0 + MED_H - 11, st["src"].upper(), GREY, 1)
    return y0 + 2 * MED_H + COLGAP


ABBR = {
    "EUROPE": "EUROPE", "MIDDLE EAST": "MIDEAST", "AMERICAS": "AMERICAS",
    "ASIA-PACIFIC": "ASIA-PC", "AFRICA": "AFRICA", "WORLD": "WORLD",
}


def draw_map_also(y0):
    text(MAPX - 2, y0, "WHERE IT HAPPENED - STORY NUMBERS ON MAP", INK, 1)
    draw_map(y0 + 16)
    ax = MAPX + MAPW + 26
    aw = W - MX - ax
    text(ax, y0, "ALSO ON SUNDAY 22 NOVEMBER - %d MORE STORIES" % len(ALSO_IDS), INK, 1)
    colw = (aw - 14) // 2
    for i, sid in enumerate(ALSO_IDS):
        st = next(s_ for s_ in S if s_["id"] == sid)
        cix, row = divmod(i, 8)
        x0 = ax + cix * (colw + 14)
        yy = y0 + 14 + row * 17
        num = str(st["id"])
        rect(x0, yy - 1, x0 + 13, yy + 11, RED)
        text(x0 + 4, yy + 2, num, PAPER, 1)
        reg = ABBR.get(st["region"], st["region"])
        text(x0 + 17, yy + 2, reg + ":", REGION_COLORS[st["region"]], 1)
        budget = (colw - 20 - twidth(reg + ":", 1)) // 6
        hl = wrap(st["head"], budget)
        text(x0 + 17 + twidth(reg + ":", 1) + 6, yy + 2, hl[0], INK, 1)
    return max(y0 + 16 + MAPH + 4, y0 + 14 + 8 * 17)


def draw_datecheck(y0):
    boxh = 44
    rect(MX, y0, W - MX, y0 + boxh, (250, 240, 236))
    frame(MX, y0, W - MX, y0 + boxh, RED, 2)
    rect(MX, y0, MX + 96, y0 + boxh, RED)
    text(MX + 8, y0 + 16, "DATE CHECK", PAPER, 1)
    yy = y0 + 7
    for ln in wrap(DATE_CHECK, (W - 2 * MX - 110) // 6)[:4]:
        text(MX + 106, yy, ln, INK, 1)
        yy += 10


def draw_footer(y0):
    text(MX, y0, "SOURCES: Reuters, AP, Al Jazeera, Guardian, DW, CNBC, Xinhua, NYT, WaPo, "
         "Euronews, CBS, Fox, CNN, Rio Times, wires. Illustrations and map are stylised, not to scale.", GREY, 1)
    text(MX, y0 + 12, "CERTAINTY: REPORTED = carried by the day's wires * CLAIM = one-side account, "
         "labelled as such * FORECAST = still to happen when drawn", GREY, 1)
    hline(MX, W - MX, y0 + 26, RULE, 1)


def draw_bottombar():
    rect(0, H - 22, W, H, INK)
    rect(0, H - 22, W, H - 20, RED)
    text(MX, H - 14, "THE WORLD IN ONE DAY", CREAMTXT, 1)
    s = "SUNDAY 22 NOVEMBER 2026 * ONE PAGE * 30 STORIES"
    text(W - MX - twidth(s, 1), H - 14, s, CREAMTXT, 1)


def build():
    draw_topbar()
    draw_masthead()
    draw_stats()
    draw_navbar()
    draw_timeline()
    y = draw_leads(232)
    y = draw_cards(y + COLGAP)
    y = draw_map_also(y + 4)
    draw_datecheck(y + 4)
    draw_footer(y + 52)
    draw_bottombar()


build()

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
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    print(f"wrote {path} ({len(png):,} bytes)")


write_png(OUT)
