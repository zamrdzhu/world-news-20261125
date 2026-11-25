#!/usr/bin/env python3
"""THE WORLD TODAY -- 25 November 2026.

Renders one 1024x1024 front page summing up Wednesday 25 November 2026's
world news: 57 sourced stories (2 lead stories + 55 across 9 sections),
drawn with a hand-rolled 5x7 bitmap font and a stdlib-only PNG writer.
No network, no randomness, no time dependence: the same bytes every run.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   (writes out/entry.png)
The grader runs it with /output as the writable directory.
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 pixels, '1' on, '0' off. Uppercase only; the
# renderer upper-cases every headline, so lower case is never needed.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}

BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def text_width(text, scale):
    """Pixel width of text at a scale (5 px glyph + 2 px gap, per char)."""
    return len(text) * (5 * scale + 2) - 2


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    """An RGB canvas backed by a bytearray, with rect/text/circle drawing."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i:i + 3] = color

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def circle(self, cx, cy, r, color):
        # Filled circle by horizontal spans (deterministic, no floats).
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, cy + dy, color)

    def ring(self, cx, cy, r, color):
        # 2 px outline circle.
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in (cx - dx, cx + dx):
                self.set(xx, cy + dy, color)
                self.set(xx, cy + dy + 1, color)
        for dx in range(-r, r + 1):
            dy = int((r * r - dx * dx) ** 0.5)
            for yy in (cy - dy, cy + dy):
                self.set(cx + dx, yy, color)
                self.set(cx + dx + 1, yy, color)

    def draw_text(self, x, y, text, scale, color):
        """Draw upper-cased text; returns the x just past the last glyph."""
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 5 * scale + 2
        return cx - 2

    def text_centred(self, y, text, scale, color):
        x = (self.w - text_width(text, scale)) // 2
        self.draw_text(x, y, text, scale, color)


# ---------------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    """Write a 24-bit RGB PNG (filter 0 on every scanline)."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h,
                                       8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------------ palette
PAPER = bytes([251, 247, 236])
INK = bytes([20, 20, 20])
NAVY = bytes([16, 41, 75])
GOLD = bytes([198, 158, 62])
RED = bytes([179, 32, 44])
LEAD_BG = bytes([239, 233, 216])
GREY = bytes([90, 90, 84])
RULE = bytes([180, 172, 150])

SECTION_COLORS = {
    "WORLD": bytes([16, 41, 75]),
    "MIDDLE EAST": bytes([122, 32, 32]),
    "EUROPE": bytes([31, 90, 138]),
    "ASIA-PACIFIC": bytes([14, 107, 107]),
    "AFRICA": bytes([46, 107, 52]),
    "AMERICAS": bytes([91, 58, 142]),
    "MARKETS & TECH": bytes([122, 74, 33]),
    "SCIENCE & SPACE": bytes([58, 74, 90]),
    "SPORT": bytes([140, 40, 90]),
}

# ------------------------------------------------------- the day's stories
# Two lead stories, then 55 body stories in 9 sections. Every headline is
# a real event of 25 November 2026 (or first reported that day), sourced in
# research.md next to the build notes; each headline is kept to 50 chars so
# it wraps to at most two lines in a column.
LEADS = [
    ("CIA AND ODNI HIT BY CYBERATTACK, SOURCES SAY",
     "CNN / REUTERS - REPORTED 25 NOV 2026"),
    ("HUAWEI FOUND GUILTY IN US TRIAL ON 10 OF 12 COUNTS",
     "US DEPT OF JUSTICE / AFP - VERDICT 24 NOV, REPORTED 25 NOV"),
]

SECTIONS = [
    ("WORLD", [
        "ZELENSKIY CONFIRMS UKRAINE HIT RUSSIAN SHIP",
        "NATO TO SEND EARLY-WARNING JETS TO POLAND",
        "S. KOREA SCRAMBLES JETS AS RUSSIAN JETS ENTER ZONE",
        "ASEAN, CHINA FAIL TO AGREE SOUTH CHINA SEA CODE",
        "ICJ: MYANMAR COMMITTED GENOCIDE AGAINST ROHINGYA",
        "US PAUSES JOINT MILITARY OPS WITH ECUADOR",
    ]),
    ("MIDDLE EAST", [
        "HOUTHIS PUSH TO 60 KM FROM ADEN; ARMY: CITY HOLDS",
        "HOUTHI DRONE HITS RIYADH TOWER; 11 INJURED",
        "IRAN: THREE OIL TANKERS HIT BY MINES IN HORMUZ",
        "ISRAEL STRIKE KILLS HAMAS SECURITY CHIEF IN GAZA",
        "ISRAEL APPROVES FLYDUBAI SERVICE TO TEL AVIV",
        "IRAQ PM ORDERS SEIZURE OF KURDISTAN BORDER POSTS",
    ]),
    ("EUROPE", [
        "SARKOZY CORRUPTION CASE ORDERED TO TRIAL",
        "GERMAN BUSINESS MORALE RISES; IFO INDEX 90.6",
        "UK PANEL TO PROBE NUCLEAR TEST VETERANS' HEALTH",
        "UK MINISTERS CONSULT ON CHANGING AGE OF CONSENT",
        "MOLDOVA EXTRADITES UKRAINIAN TORTURE SUSPECT",
        "RUSSIA TIGHTENS MONITORING OF MONEY TRANSFERS",
        "CAS REINSTATES SENEGAL AS AFCON 2025 CHAMPIONS",
    ]),
    ("ASIA-PACIFIC", [
        "SHENZHOU-24 LIFTS OFF WITH FIRST PAKISTANI IN SPACE",
        "AUSTRALIA APOLOGISES TO LGBTQ VETERANS",
        "MODI, MERZ HOLD TALKS ON INDIA-GERMANY TIES",
        "BJP, AKALI DAL ALLY FOR 2027 PUNJAB POLLS",
        "NEPAL PM WRAPS UP FIRST STATE VISIT TO INDIA",
        "5.6 QUAKE HITS NEPAL'S KOSHI PROVINCE",
        "72 ORANGUTANS RESCUED FROM KALIMANTAN WILDFIRES",
        "INDONESIA SEEKS TRADE DEAL WITH BRITAIN",
        "FIJI DECLARES CRISIS AMID EL NINO DROUGHT",
    ]),
    ("AFRICA", [
        "WHO EVACUATES STAFF FROM DR CONGO EBOLA HOSPITAL",
        "ETHIOPIA TO HOST COP32 AFTER DEADLOCKED TALKS",
        "GHANA PROBES SALE OF 300 DIPLOMATIC PASSPORTS",
    ]),
    ("AMERICAS", [
        "TRUMP PARDONS TURKEYS FREEDOM AND FEATHERS",
        "TRUMP AWARDS GIULIANI THE MEDAL OF FREEDOM",
        "ABREGO GARCIA TO LEAVE US VOLUNTARILY",
        "FORT HOOD SHOOTER HASAN SEEKS STAY OF EXECUTION",
        "RADAR OUTAGE DELAYS FLIGHTS AT CHICAGO O'HARE",
        "US ARMY TO DETONATE 68 BARRELS OF LEAD AZIDE",
        "MEXICO INFLATION HITS SIX-MONTH HIGH AT 3.96%",
        "BOLSONARO TAKEN TO ICU WITH BOWEL OBSTRUCTION",
    ]),
    ("MARKETS & TECH", [
        "US SET TO UNVEIL NEW TARIFFS AFTER PROBE",
        "NVIDIA BOUNCE FADES AS SHARES SLIDE 6%",
        "DELL LIFTS FORECASTS ON RECORD AI SERVER QUARTER",
        "MICROSOFT DECLARES 'CODE RED' AFTER HISTORIC OUTAGE",
        "US CONSUMER CONFIDENCE AT HIGHEST IN NEARLY 2 YEARS",
        "SENSEX DROPS 1,484 POINTS IN BROAD SELL-OFF",
    ]),
    ("SCIENCE & SPACE", [
        "ESA TO SHARE FIRST HERA IMAGES OF DIMORPHOS",
        "DWARF PLANET CANDIDATE FOUND ON 281-YEAR ORBIT",
        "STUDY MAKES CASE FOR HIDDEN 'PLANET X2'",
    ]),
    ("SPORT", [
        "CHAMPIONS LEAGUE: ARSENAL HOST DORTMUND",
        "ENGLAND BEAT AUSTRALIA BY 8 WICKETS IN 2ND T20I",
        "INDIA WOMEN BEAT CHINA 6-2 IN FOOTBALL",
        "SOORYAVANSHI SMASHES 204 OFF 53 BALLS FOR INDIA A",
        "MARKRAM'S 150 SETS SOUTH AFRICA RECORD",
        "MUMBAI BEAT ODISHA FOR FIFTH STRAIGHT SMAT WIN",
        "CHESS TITLE MATCH UNDER WAY: GUKESH VS SINDAROV",
    ]),
]

# ------------------------------------------------------------------- layout
MASTHEAD_H = 104
LEAD_TOP, LEAD_H = 112, 108
BODY_TOP, BODY_BOTTOM = 228, 990
COL_W, GUTTER = 314, 16
COL_X = [24, 24 + COL_W + GUTTER, 24 + 2 * (COL_W + GUTTER)]
BODY_SCALE = 2
LINE_H = 15
STORY_GAP = 5
HEADER_H = 22


def draw_masthead(cv):
    cv.rect(0, 0, W, MASTHEAD_H, NAVY)
    # Small globe at the left: gold ring, meridians and equator.
    cx, cy, r = 66, 52, 32
    cv.ring(cx, cy, r, GOLD)
    cv.ring(cx, cy, r - 12, GOLD)
    cv.rect(cx - 1, cy - r, 2, 2 * r, GOLD)
    cv.rect(cx - r, cy - 1, 2 * r, 2, GOLD)
    cv.text_centred(16, "THE WORLD TODAY", 5, PAPER)
    cv.text_centred(66, "WEDNESDAY 25 NOVEMBER 2026", 2, GOLD)
    cv.rect(0, MASTHEAD_H - 4, W, 4, GOLD)
    cv.text_centred(MASTHEAD_H + 2, "", 1, INK)  # no-op, keeps spacing clear


def draw_leads(cv):
    for i, (headline, source) in enumerate(LEADS):
        x = 24 + i * (476 + 24)
        cv.rect(x, LEAD_TOP, 476, LEAD_H, LEAD_BG)
        cv.rect(x, LEAD_TOP, 5, LEAD_H, RED)
        cv.draw_text(x + 16, LEAD_TOP + 10, "LEAD STORY", 1, RED)
        lines = wrap_text(headline, 476 - 32, 3)
        y = LEAD_TOP + 28
        for line in lines:
            cv.draw_text(x + 16, y, line, 3, INK)
            y += 3 * 7 + 4
        cv.draw_text(x + 16, LEAD_TOP + LEAD_H - 18, source, 1, GREY)


def draw_section_header(cv, x, y, name):
    color = SECTION_COLORS[name]
    cv.rect(x, y, COL_W, HEADER_H, color)
    cv.draw_text(x + 8, y + 5, name, 2, PAPER)
    return y + HEADER_H + 6


def draw_story(cv, x, y, headline):
    lines = wrap_text(headline, COL_W, BODY_SCALE)
    for line in lines:
        cv.draw_text(x, y, line, BODY_SCALE, INK)
        y += LINE_H
    return y + STORY_GAP


def draw_body(cv):
    """Flow the sections across the three columns, splitting a section
    across columns when the column runs out of room."""
    col = 0
    y = BODY_TOP
    for name, stories in SECTIONS:
        header_drawn_here = False
        for headline in stories:
            lines = wrap_text(headline, COL_W, BODY_SCALE)
            need = len(lines) * LINE_H + STORY_GAP
            if not header_drawn_here:
                need += HEADER_H + 6
            if y + need > BODY_BOTTOM:
                col += 1
                if col >= len(COL_X):
                    raise SystemExit(
                        "layout overflow: stories do not fit in 3 columns")
                y = BODY_TOP
                header_drawn_here = False
                need = len(lines) * LINE_H + STORY_GAP + HEADER_H + 6
            if not header_drawn_here:
                y = draw_section_header(cv, COL_X[col], y, name)
                header_drawn_here = True
            y = draw_story(cv, COL_X[col], y, headline)
    return col


def draw_footer(cv):
    cv.hline(24, BODY_BOTTOM + 6, W - 48, RULE)
    cv.text_centred(BODY_BOTTOM + 12,
                    "57 STORIES - SOURCES: REUTERS, AP, BBC, AL JAZEERA, CNN",
                    1, GREY)
    cv.text_centred(BODY_BOTTOM + 24,
                    "THE WORLD TODAY - WEDNESDAY 25 NOVEMBER 2026",
                    1, GREY)


def render():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_leads(cv)
    draw_body(cv)
    draw_footer(cv)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, render())
    total = 2 + sum(len(s) for _, s in SECTIONS)
    print(f"wrote {path} ({size} bytes, {W}x{H}, {total} stories)")
    if size > 1048576:
        print("ERROR: entry.png exceeds 1 MiB", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
