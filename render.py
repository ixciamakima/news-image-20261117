#!/usr/bin/env python3
"""Render the 17 November 2026 world-news front page (1024x1024 PNG).

Deterministic: same input data, same bytes out. Draws with Pillow from the
story table embedded below; no network, no randomness, no timestamps.
Run:  python3 render.py  ->  writes entry.png next to this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

PAPER = (247, 243, 234)
INK = (20, 20, 20)
NAVY = (18, 33, 61)
RED = (178, 18, 46)
SEA = (207, 227, 238)
LAND = (216, 201, 163)
LAND_EDGE = (120, 104, 74)
MUTED = (90, 86, 78)
RULE = (180, 172, 156)

# region -> colour used for map markers and story tags
REGION_COLORS = {
    "Europe": (31, 78, 121),
    "Middle East": (179, 84, 30),
    "Asia": (46, 125, 50),
    "N. America": (106, 27, 154),
    "S. America": (173, 20, 87),
    "Africa": (121, 85, 72),
}

# (number, region, tag, headline, summary, lon, lat)
STORIES = [
    (1, "Europe", "UKRAINE",
     "KERCH BRIDGE IN RUINS",
     "Ukraine strike collapses a span of the bridge to Crimea; Russia vows to rebuild.",
     33.5, 45.3),
    (2, "Europe", "UKRAINE",
     "KYIV BRIDGES HIT",
     "Russian missiles hit the North and South bridges; power and water cut.",
     30.5, 50.4),
    (3, "Middle East", "MIDEAST",
     "IRAN DRONES TARGET U.S. RADAR",
     "Iran fires drones at a U.S. radar site in Bahrain; all intercepted.",
     50.5, 26.2),
    (4, "Middle East", "MIDEAST",
     "U.S. WARNS OF IRAN 'DIRTY BOMB' PLOT",
     "U.S. intelligence says Iran weighs attacks on Trump officials.",
     51.4, 35.7),
    (5, "Middle East", "MIDEAST",
     "THIRD U.S. CARRIER REACHES GULF",
     "USS Theodore Roosevelt joins two carriers as a tanker is hit near Hormuz.",
     56.5, 26.5),
    (6, "Asia", "ASIA",
     "TRUMP LANDS IN ASIA",
     "In Manila for ASEAN, then APEC in Shenzhen; Xi and Putin talks Thursday.",
     121.0, 14.6),
    (7, "Middle East", "MIDEAST",
     "NETANYAHU CAMP IN VOTE PROBE",
     "Allies accused of tipping police to arrest Arab party workers on election day.",
     35.2, 31.8),
    (8, "Middle East", "MIDEAST",
     "SETTLERS KILL WOMAN, 72",
     "Fadha Wadha shot dead near Jericho, Palestinian officials say.",
     35.9, 31.9),
    (9, "Europe", "EUROPE",
     "BRITAIN SANCTIONS SETTLERS",
     "London blacklists eight firms building West Bank settlements.",
     -0.1, 51.5),
    (10, "Asia", "ASIA",
     "XI AND CARNEY CUT TARIFFS",
     "China and Canada agree new tariff relief worth about $280 million.",
     116.4, 39.9),
    (11, "Asia", "ASIA",
     "TOKYO SCRAMBLES JETS",
     "Two suspected Russian jets enter Japan's airspace; Seoul also responds.",
     139.7, 35.7),
    (12, "Europe", "EUROPE",
     "128 NATIONS WEIGH ROBOT-WEAPONS BAN",
     "Geneva talks open on banning lethal autonomous weapons.",
     6.1, 46.2),
    (13, "Europe", "EUROPE",
     "CLIMATE TALKS SPLIT OVER IPCC",
     "At COP31, a bloc led by India and Saudi Arabia seeks to delay reports.",
     32.9, 39.9),
    (14, "N. America", "CLIMATE",
     "DATA CENTRES EMIT LIKE DENMARK",
     "Biggest U.S. data centres produce 25.7m tonnes of CO2 a year.",
     -100.0, 39.0),
    (15, "N. America", "U.S.",
     "JPMORGAN BUG HITS U.S. BANKS",
     "A software fault disrupts online banking and Zelle; not a cyberattack.",
     -74.0, 40.7),
    (16, "N. America", "TECH",
     "NVIDIA REPORTS AFTER THE BELL",
     "First results since Jensen Huang quit; board rules out his return as CEO.",
     -122.0, 37.4),
    (17, "N. America", "TECH",
     "U.S. CLOSES AI-CHIP LOOPHOLE",
     "New rules stop China renting U.S. computing power abroad.",
     -87.6, 41.9),
    (18, "N. America", "U.S.",
     "PENTAGON FAILS AUDIT AGAIN",
     "Ninth straight year with no clean opinion; $4.8 trillion in assets unverified.",
     -77.5, 38.9),
    (19, "N. America", "CULTURE",
     "GTA VI FEVER, TWO DAYS OUT",
     "About 10m pre-orders; fans book time off for Thursday's launch.",
     -80.2, 25.8),
    (20, "N. America", "SPACE",
     "SPACEX CATCHES STARSHIP",
     "Tower arms catch the ship after 14 orbits - a first for a returning spacecraft.",
     -97.2, 25.9),
    (21, "N. America", "SPACE",
     "VOYAGER 1, ONE LIGHT-DAY OUT",
     "NASA's 1977 probe becomes the first human object a light-day from Earth.",
     -80.6, 28.4),
    (22, "S. America", "SPORT",
     "BRAZIL HIT SINGAPORE 7-0",
     "Vinicius scores a 21-minute hat-trick as Brazil bounce back in Singapore.",
     103.8, 1.35),
    (23, "Africa", "SPORT",
     "SOUTH AFRICA EDGE KENYA 2-1",
     "Bafana Bafana win in Nairobi to top their AFCON qualifying group.",
     36.8, -1.3),
    (24, "Africa", "AFRICA",
     "17 SHOT DEAD IN SOUTH AFRICA",
     "Two separate mass shootings hours apart; police say they are unrelated.",
     28.0, -26.2),
]

LEAD = STORIES[0]
GRID = STORIES[1:]

MARKETS = ("MARKETS  —  Dow futures -0.6%  ·  Nasdaq +0.5%  ·  Gold $3,860  ·  "
           "Brent crude $93  ·  Bitcoin $64,500")
FOOTER = ("Compiled from Reuters, BBC, AP, CNN, NYT, AFP and others  ·  "
          "Tuesday 17 November 2026  ·  24 stories, 6 regions")


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w, max_lines=2):
    """Greedy word wrap; truncates with an ellipsis if it still overflows."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "...", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "..."
    return lines


# --- simplified continent outlines (lon, lat), equirectangular, stylised ---
NORTH_AMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
                 (-85, 80), (-80, 73), (-75, 72), (-65, 60), (-55, 52),
                 (-60, 46), (-70, 42), (-75, 35), (-80, 32), (-81, 26),
                 (-90, 21), (-97, 16), (-105, 20), (-110, 23), (-117, 33),
                 (-125, 40), (-124, 48), (-135, 58), (-150, 60), (-165, 60)]
GREENLAND = [(-58, 64), (-45, 60), (-40, 64), (-30, 68), (-25, 70),
             (-35, 76), (-55, 76), (-60, 74)]
SOUTH_AMERICA = [(-80, 10), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
                 (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
                 (-70, -52), (-66, -55), (-65, -45), (-62, -38), (-57, -30),
                 (-52, -28), (-48, -22), (-41, -15), (-35, -8), (-40, -3),
                 (-50, 0), (-55, 5), (-62, 9), (-70, 11), (-77, 8)]
AFRICA = [(-17, 15), (-17, 21), (-10, 31), (-5, 35), (10, 37), (11, 34),
          (20, 32), (30, 31), (32, 31), (34, 28), (35, 23), (37, 18),
          (40, 15), (43, 11), (48, 11), (51, 10), (44, 2), (41, -2),
          (40, -10), (36, -18), (33, -26), (28, -33), (20, -35), (17, -29),
          (14, -22), (12, -12), (13, -5), (9, 4), (-8, 5), (-13, 8), (-17, 12)]
EUROPE = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-2, 48), (-5, 48),
          (-1, 50), (2, 51), (5, 53), (8, 55), (8, 57), (10, 59), (5, 60),
          (5, 62), (10, 64), (12, 66), (18, 69), (25, 71), (30, 70),
          (35, 68), (40, 68), (45, 68), (40, 65), (35, 64), (30, 60),
          (28, 58), (24, 58), (21, 55), (18, 54), (15, 54), (12, 54),
          (8, 54), (3, 53), (0, 50), (-2, 50), (-5, 46), (-9, 43)]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)]
ASIA = [(30, 36), (35, 36), (36, 33), (40, 31), (43, 29), (48, 29),
        (50, 26), (54, 26), (57, 25), (61, 25), (66, 25), (70, 22),
        (72, 20), (76, 18), (80, 15), (80, 13), (77, 8), (80, 7),
        (83, 10), (85, 15), (88, 21), (91, 22), (94, 17), (97, 16),
        (100, 14), (103, 10), (105, 9), (108, 11), (109, 15), (106, 20),
        (108, 21), (110, 20), (114, 22), (116, 23), (118, 25), (120, 28),
        (121, 32), (120, 35), (122, 38), (126, 40), (128, 38), (130, 42),
        (132, 43), (135, 44), (138, 46), (140, 48), (141, 50), (142, 52),
        (142, 55), (141, 59), (140, 60), (136, 59), (135, 55), (130, 52),
        (127, 50), (122, 48), (118, 45), (114, 44), (110, 42), (105, 40),
        (100, 42), (95, 44), (90, 45), (85, 46), (80, 45), (75, 45),
        (70, 42), (65, 40), (60, 38), (55, 37), (50, 37), (45, 38),
        (40, 38), (35, 36)]
JAPAN = [(130, 31), (133, 34), (136, 35), (139, 35), (141, 39), (141, 42),
         (143, 44), (145, 44), (142, 42), (140, 38), (137, 37), (133, 35)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
             (146, -19), (142, -15), (142, -11), (136, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)]
NEW_ZEALAND = [(167, -45), (170, -42), (174, -39), (177, -38), (175, -41),
               (172, -43), (168, -46)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EUROPE,
              BRITAIN, ASIA, JAPAN, AUSTRALIA, NEW_ZEALAND]


def draw_map(d, x0, y0, mw, mh):
    """World map with numbered story markers. Returns nothing; draws in place."""
    d.rectangle([x0, y0, x0 + mw, y0 + mh], fill=SEA)
    # faint latitude/longitude grid
    for lon in range(-150, 181, 30):
        gx = x0 + (lon + 180) / 360.0 * mw
        d.line([(gx, y0), (gx, y0 + mh)], fill=(255, 255, 255), width=1)
    for lat in (-30, 0, 30, 60):
        gy = y0 + (84 - lat) / 142.0 * mh
        d.line([(x0, gy), (x0 + mw, gy)], fill=(255, 255, 255), width=1)

    def proj(lon, lat):
        return (x0 + (lon + 180) / 360.0 * mw,
                y0 + (84 - lat) / 142.0 * mh)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)

    d.text((x0 + 14, y0 + 8), "WHERE THE DAY HAPPENED",
           font=F_SANS_B(15), fill=(60, 70, 80))
    # region legend, bottom-left inside the map (empty Pacific)
    lx, ly = x0 + 14, y0 + mh - 66
    d.rounded_rectangle([lx - 10, ly - 8, lx + 196, y0 + mh - 10],
                        radius=6, fill=(255, 255, 255))
    for i, (name, col) in enumerate(REGION_COLORS.items()):
        yy = ly + i * 11
        d.rectangle([lx, yy, lx + 9, yy + 8], fill=col)
        d.text((lx + 14, yy - 1), name, font=F_SANS(10), fill=INK)
    d.text((lx + 108, ly - 1), "6 regions", font=F_SANS_B(10), fill=MUTED)
    d.text((lx + 108, ly + 10), "24 stories", font=F_SANS_B(10), fill=MUTED)

    # numbered markers; nudges keep close neighbours readable
    offsets = {1: (-20, -14), 2: (18, 16), 3: (-14, -10), 5: (14, 8),
               7: (-14, -12), 8: (14, 12), 12: (0, 14), 13: (-2, 18),
               14: (-12, -12), 15: (-13, -11), 17: (-12, 0), 18: (13, 11),
               19: (-12, 10), 21: (-6, -14)}
    for num, region, _tag, _h, _s, lon, lat in STORIES:
        cx, cy = proj(lon, lat)
        dx, dy = offsets.get(num, (0, 0))
        cx, cy = cx + dx, cy + dy
        col = REGION_COLORS[region]
        r = 11
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col,
                  outline=(255, 255, 255), width=2)
        label = str(num)
        tw = d.textlength(label, font=F_SANS_B(12))
        d.text((cx - tw / 2, cy - 8), label, font=F_SANS_B(12),
               fill=(255, 255, 255))


def draw_masthead(d):
    d.rectangle([0, 0, W, 108], fill=NAVY)
    d.rectangle([0, 0, W, 5], fill=RED)
    d.text((28, 14), "THE WORLD IN ONE DAY", font=F_SERIF_B(40), fill=(255, 255, 255))
    d.text((28, 66), "TUESDAY 17 NOVEMBER 2026", font=F_SANS_B(32), fill=(255, 214, 64))
    right = "24 STORIES  ·  6 REGIONS"
    tw = d.textlength(right, font=F_SANS_B(16))
    d.text((W - 28 - tw, 22), right, font=F_SANS_B(16), fill=(255, 255, 255))
    sub = "The day's world news, in one picture"
    tw = d.textlength(sub, font=F_SANS(14))
    d.text((W - 28 - tw, 70), sub, font=F_SANS(14), fill=(200, 208, 220))


def draw_lead(d):
    num, region, tag, head, summ, _lon, _lat = LEAD
    y0, y1 = 108, 200
    d.rectangle([0, y0, W, y1], fill=(255, 255, 255))
    d.rectangle([28, y0 + 12, 34, y1 - 12], fill=RED)
    d.text((48, y0 + 10), "1  —  LEAD STORY  ·  UKRAINE WAR",
           font=F_SANS_B(14), fill=RED)
    d.text((48, y0 + 28), head, font=F_SANS_B(44), fill=INK)
    d.text((48, y0 + 74), summ, font=F_SANS(16), fill=(60, 58, 52))
    d.line([(0, y1), (W, y1)], fill=RULE, width=2)


def draw_grid(d):
    x0, y0 = 28, 516
    col_w, row_h = 488, 36
    f_tag, f_head, f_sum = F_SANS_B(11), F_SANS_B(14), F_SANS(11)
    for i, (num, region, tag, head, summ, _lon, _lat) in enumerate(GRID):
        col, row = divmod(i, 12)
        gx = x0 + col * (col_w + 12)
        gy = y0 + row * row_h
        colr = REGION_COLORS[region]
        # number badge
        d.ellipse([gx, gy + 2, gx + 24, gy + 26], fill=colr)
        lab = str(num)
        tw = d.textlength(lab, font=F_SANS_B(12))
        d.text((gx + 12 - tw / 2, gy + 6), lab, font=F_SANS_B(12),
               fill=(255, 255, 255))
        tx = gx + 32
        # tag + headline on one line
        tag_txt = tag + "  "
        tw_tag = d.textlength(tag_txt, font=f_tag)
        d.text((tx, gy + 1), tag_txt, font=f_tag, fill=colr)
        head_lines = wrap(d, head, f_head, col_w - 32 - tw_tag, max_lines=1)
        d.text((tx + tw_tag, gy), head_lines[0] if head_lines else "",
               font=f_head, fill=INK)
        # summary line
        sum_lines = wrap(d, summ, f_sum, col_w - 32, max_lines=1)
        d.text((tx, gy + 18), sum_lines[0] if sum_lines else "",
               font=f_sum, fill=(70, 67, 60))
        if row < 11:
            d.line([(gx, gy + 33), (gx + col_w, gy + 33)], fill=(232, 226, 214))
    d.line([(x0 + col_w + 5, y0), (x0 + col_w + 5, y0 + 12 * row_h - 4)],
           fill=RULE, width=1)


def draw_bottom(d):
    y0 = 950
    d.rectangle([0, y0, W, H], fill=NAVY)
    d.text((28, y0 + 10), MARKETS, font=F_SANS_B(15), fill=(255, 214, 64))
    d.text((28, y0 + 38), FOOTER, font=F_SANS(13), fill=(200, 208, 220))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_lead(d)
    draw_map(d, 28, 208, W - 56, 300)
    draw_grid(d)
    draw_bottom(d)
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
