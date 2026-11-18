#!/usr/bin/env python3
"""Round 2 renderer — "THE WORLD IN ONE DAY", Tuesday 17 November 2026.

Bold broadsheet front page, 1024x1024, drawn entirely with PIL + DejaVu.
Strong hierarchy: huge masthead and date, a drawn lead illustration for the
Kerch Bridge story, an equirectangular world map with numbered markers,
six top stories in large type, the remaining stories as crisp numbered
one-liners, and a markets strip. Fully deterministic: no network, no
randomness, no timestamps.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (18, 22, 28)
BLACK = (13, 16, 20)
YELLOW = (255, 198, 26)
WHITE = (255, 255, 255)
GREY = (92, 98, 106)
RULE = (18, 22, 28)

REGIONS = {
    "EU": ("Europe", (37, 99, 235)),
    "ME": ("Middle East", (217, 119, 6)),
    "AS": ("Asia", (220, 38, 38)),
    "NA": ("North America", (5, 150, 105)),
    "SA": ("South America", (124, 58, 237)),
    "AF": ("Africa", (219, 39, 119)),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def tw(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if tw(draw, trial, fnt) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def chip(draw, x, y, size, color, number):
    draw.rounded_rectangle([x, y, x + size, y + size], radius=7, fill=color)
    fnt = font(16, bold=True)
    label = str(number)
    wdt = tw(draw, label, fnt)
    draw.text((x + (size - wdt) / 2, y + size / 2 - 10), label, font=fnt, fill=WHITE)


# ---------------------------------------------------------------- stories
# (number, region, headline, summary) — facts verified for 17 Nov 2026.
LEAD = (1, "EU", "KERCH BRIDGE IN RUINS",
        "A Ukrainian strike collapses a span of the bridge linking Russia "
        "to Crimea. Moscow vows to rebuild — as Russian missiles cut "
        "power and water in Kyiv.")

TOP = [
    (2, "EU", "KYIV BRIDGES HIT",
     "Russian missiles cut power and water in the capital"),
    (5, "ME", "THIRD U.S. CARRIER IN GULF",
     "Roosevelt joins two carriers; tanker hit near Hormuz"),
    (6, "AS", "TRUMP LANDS IN ASIA",
     "Manila ASEAN summit, then APEC; Xi & Putin talks Thu"),
    (20, "NA", "SPACEX CATCHES STARSHIP",
     "Tower arms catch the ship after 14 orbits — a first"),
    (22, "SA", "BRAZIL HIT SINGAPORE 7-0",
     "Vinicius scores a 21-minute hat-trick"),
    (24, "AF", "17 SHOT DEAD IN SOUTH AFRICA",
     "Two mass shootings, hours apart"),
]

REST = [
    (3, "ME", "Iran drones hit U.S. radar — downed"),
    (4, "ME", "U.S. says Iran weighs 'dirty bomb' plot"),
    (7, "ME", "Netanyahu allies in vote probe"),
    (8, "ME", "Settlers kill woman, 72, near Jericho"),
    (9, "EU", "Britain sanctions settler firms"),
    (10, "AS", "Xi & Carney cut tariffs, ~$280m relief"),
    (11, "AS", "Japan jets scramble on Russian planes"),
    (12, "EU", "128 nations weigh robot-weapons ban"),
    (13, "AS", "Climate talks split over IPCC reports"),
    (14, "NA", "U.S. data centres emit like Denmark"),
    (15, "NA", "JPMorgan bug disrupts U.S. banks"),
    (16, "NA", "Nvidia results due after the bell"),
    (17, "NA", "U.S. closes AI-chip loophole on China"),
    (18, "NA", "Pentagon fails 9th straight audit"),
    (19, "NA", "GTA VI: 10m pre-orders, out Thursday"),
    (21, "NA", "Voyager 1 now one light-day out"),
    (23, "AF", "South Africa edge Kenya 2-1, Nairobi"),
]

# ------------------------------------------------------------- world map
# Coarse continent polygons in (lon, lat), drawn on an equirectangular
# projection, lat -58..84, so the aspect ratio is honest.
LAND = [
    # North America + Central America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-80, 73), (-72, 72), (-65, 62), (-55, 52), (-65, 45), (-70, 42),
     (-74, 39), (-76, 35), (-80, 32), (-80, 26), (-84, 30), (-89, 30),
     (-94, 29), (-97, 26), (-97, 22), (-94, 18), (-90, 15), (-83, 9),
     (-79, 9), (-86, 13), (-92, 15), (-97, 16), (-105, 20), (-110, 23),
     (-114, 29), (-120, 34), (-124, 40), (-124, 47), (-130, 55),
     (-150, 60), (-165, 60)],
    # Greenland
    [(-45, 60), (-32, 68), (-22, 70), (-20, 76), (-30, 82), (-52, 80),
     (-56, 71), (-53, 62)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-39, -13), (-40, -20), (-48, -26), (-52, -33), (-58, -38),
     (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54), (-73, -46),
     (-73, -37), (-71, -30), (-70, -20), (-75, -15), (-79, -8), (-80, -4),
     (-77, 1), (-79, 5)],
    # Africa
    [(-6, 35), (0, 36), (10, 37), (20, 32), (30, 31), (33, 31), (35, 28),
     (38, 22), (43, 12), (48, 11), (51, 10), (48, 5), (42, -2), (40, -10),
     (38, -18), (35, -24), (32, -29), (26, -34), (20, -35), (17, -32),
     (15, -27), (13, -18), (12, -10), (13, -5), (9, 0), (9, 4), (-8, 5),
     (-13, 8), (-17, 15), (-17, 21), (-15, 27), (-10, 31)],
    # Eurasia
    [(-9, 37), (-9, 43), (-5, 48), (-1, 50), (3, 51), (7, 54), (8, 57),
     (10, 59), (18, 59), (21, 60), (24, 66), (31, 70), (50, 69), (70, 72),
     (90, 75), (110, 74), (130, 72), (150, 71), (170, 67), (178, 65),
     (173, 60), (162, 55), (156, 50), (150, 45), (142, 40), (140, 36),
     (135, 34), (129, 33), (126, 34), (122, 31), (121, 27), (118, 24),
     (112, 22), (108, 17), (107, 12), (104, 8), (103, 5), (100, 7),
     (98, 13), (95, 16), (92, 21), (89, 22), (86, 20), (82, 16), (80, 13),
     (77, 8), (76, 10), (73, 16), (72, 20), (70, 21), (67, 24), (61, 25),
     (57, 26), (52, 28), (50, 29), (53, 27), (56, 26), (59, 23), (58, 21),
     (55, 17), (52, 15), (47, 13), (44, 12), (42, 13), (39, 20), (36, 24),
     (34, 28), (35, 31), (36, 36), (33, 36), (30, 36), (27, 34), (23, 36),
     (20, 37), (19, 40), (16, 38), (15, 40), (13, 42), (12, 44), (10, 44),
     (7, 44), (3, 42), (0, 39), (-2, 37)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 55), (-7, 58), (-5, 58), (-3, 56), (-2, 54),
     (-1, 52), (-4, 50)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (142, 44),
     (140, 45), (138, 38), (135, 34), (131, 32)],
    # Sumatra / Borneo / New Guinea / Philippines (coarse island blobs)
    [(95, 5), (100, 0), (104, -3), (106, -6), (102, -4), (97, 2)],
    [(109, 1), (113, 4), (117, 6), (119, 2), (116, -2), (112, -2)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (147, -9),
     (142, -8), (136, -4), (132, -3)],
    [(119, 16), (122, 18), (122, 13), (120, 12)],
    # Australia + New Zealand
    [(113, -22), (114, -28), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (151, -24), (146, -19), (142, -11), (142, -14),
     (139, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14),
     (122, -17), (118, -20)],
    [(167, -45), (170, -43), (172, -41), (174, -39), (176, -37), (174, -41),
     (171, -44), (168, -46)],
]

# number -> (lon, lat, region, pixel nudge dx, dy) — nudges separate clusters
MARKERS = {
    1: (37.0, 45.0, "EU", 10, 8), 2: (30.5, 50.4, "EU", 2, -2),
    3: (50.6, 26.2, "ME", -10, 18), 4: (51.4, 35.7, "ME", 10, -16),
    5: (56.3, 26.6, "ME", 16, -4), 6: (121.0, 14.6, "AS", 6, 6),
    7: (35.2, 31.8, "ME", -16, -6), 8: (35.4, 31.9, "ME", 20, 2),
    9: (-0.1, 51.5, "EU", 0, -8), 10: (116.4, 39.9, "AS", 6, -6),
    11: (138.0, 37.0, "AS", 8, 2), 12: (6.1, 46.2, "EU", -4, 12),
    13: (77.2, 28.6, "AS", 10, 12), 14: (-98.0, 39.0, "NA", -10, -12),
    15: (-74.0, 40.7, "NA", 10, -12), 16: (-122.0, 37.4, "NA", -8, -10),
    17: (-77.0, 38.9, "NA", -14, 10), 18: (-77.05, 38.87, "NA", 20, 16),
    19: (-80.2, 25.8, "NA", 4, 18), 20: (-97.2, 25.9, "NA", -18, -6),
    21: (-155.0, 25.0, "NA", 0, 0), 22: (-52.0, -10.0, "SA", 0, 0),
    23: (36.8, -1.3, "AF", 2, 0), 24: (25.0, -29.0, "AF", 0, 0),
}

MAP_X, MAP_Y, MAP_W = 16, 356, 560
MAP_H = round(MAP_W * 142 / 360)  # 221 — honest equirectangular aspect


def project(lon, lat):
    x = MAP_X + (lon + 180) / 360 * MAP_W
    y = MAP_Y + (84 - lat) / 142 * MAP_H
    return x, y


def draw_map(draw):
    ocean = (201, 220, 234)
    land = (233, 226, 203)
    edge = (120, 112, 88)
    draw.rectangle([MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H], fill=ocean)
    for deg in range(-150, 180, 30):
        x, _ = project(deg, 0)
        draw.line([x, MAP_Y, x, MAP_Y + MAP_H], fill=(178, 199, 216), width=1)
    for deg in range(-30, 90, 30):
        _, y = project(0, deg)
        draw.line([MAP_X, y, MAP_X + MAP_W, y], fill=(178, 199, 216), width=1)
    for poly in LAND:
        pts = [project(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=land, outline=edge)
    fnt = font(13, bold=True)
    for num, (lon, lat, region, dx, dy) in MARKERS.items():
        x, y = project(lon, lat)
        x, y = x + dx, y + dy
        color = REGIONS[region][1]
        r = 12
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color,
                     outline=WHITE, width=2)
        label = str(num)
        wdt = tw(draw, label, fnt)
        draw.text((x - wdt / 2, y - 8), label, font=fnt, fill=WHITE)
    draw.rectangle([MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H],
                   outline=INK, width=2)


# ------------------------------------------------------- lead illustration
def draw_lead_art(draw, x0, y0, x1, y1):
    """Flat vector-style scene: a bridge over the sea, one span down, smoke."""
    wdt, hgt = x1 - x0, y1 - y0
    sea_y = y0 + int(hgt * 0.62)
    # sky — horizontal sunset bands (deterministic gradient)
    top = (255, 214, 130)
    bottom = (255, 158, 94)
    for i in range(sea_y - y0):
        t = i / max(1, sea_y - y0)
        col = tuple(round(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        draw.line([x0, y0 + i, x1, y0 + i], fill=col)
    # sun
    sx, sy, sr = x0 + int(wdt * 0.80), y0 + int(hgt * 0.30), 26
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 240, 190))
    # sea
    draw.rectangle([x0, sea_y, x1, y1], fill=(46, 111, 142))
    for i, wy in enumerate(range(sea_y + 14, y1 - 6, 16)):
        off = 12 if i % 2 else 30
        for wx in range(x0 + off, x1 - 26, 64):
            draw.line([wx, wy, wx + 22, wy], fill=(90, 155, 182), width=2)
    # bridge silhouette
    deck_y = y0 + int(hgt * 0.52)
    sil = (24, 28, 34)
    pylon_a = x0 + int(wdt * 0.30)
    pylon_b = x0 + int(wdt * 0.68)
    for px in (pylon_a, pylon_b):
        draw.rectangle([px - 6, deck_y - 62, px + 6, sea_y + 10], fill=sil)
        draw.rectangle([px - 13, deck_y - 62, px + 13, deck_y - 54], fill=sil)
    # standing spans (left of A, A to mid) and the far right stub
    draw.rectangle([x0, deck_y, pylon_a + 40, deck_y + 7], fill=sil)
    mid_x = x0 + int(wdt * 0.52)
    draw.rectangle([pylon_a, deck_y, mid_x, deck_y + 7], fill=sil)
    draw.rectangle([pylon_b + 26, deck_y, x1, deck_y + 7], fill=sil)
    # cables on the standing span
    for cx in range(pylon_a + 16, mid_x - 4, 22):
        t = (cx - pylon_a) / (mid_x - pylon_a)
        cy = deck_y - 58 + t * 52
        draw.line([pylon_a, deck_y - 58, cx, deck_y], fill=sil, width=2)
        draw.line([cx, cy, cx, deck_y], fill=sil, width=1)
    # collapsed span: a deck segment tipped down into the sea
    draw.polygon([(mid_x, deck_y + 2), (pylon_b + 22, deck_y + 34),
                  (pylon_b + 22, deck_y + 42), (mid_x, deck_y + 10)], fill=sil)
    draw.rectangle([pylon_b - 4, deck_y + 30, pylon_b + 20, deck_y + 48], fill=sil)
    # foam where the span hit the water
    for fx, fw in ((mid_x + 60, 30), (mid_x + 104, 22), (mid_x + 26, 16)):
        draw.ellipse([fx, sea_y + 2, fx + fw, sea_y + 9], fill=(220, 238, 244))
    # smoke plume above the break — layered flat ellipses
    smoke = [(86, 92, 98), (110, 116, 122), (134, 140, 146), (158, 164, 170)]
    blobs = [(mid_x + 6, deck_y - 58, 44, 26), (mid_x + 26, deck_y - 78, 56, 32),
             (mid_x + 54, deck_y - 94, 66, 36), (mid_x + 88, deck_y - 104, 74, 38)]
    for i, (bx, by, bw, bh) in enumerate(blobs):
        draw.ellipse([bx, by, bx + bw, by + bh], fill=smoke[i % len(smoke)])
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)


# ---------------------------------------------------------------- layout
def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    warnings = []

    # masthead
    draw.rectangle([0, 0, W, 72], fill=BLACK)
    f_title = font(48, bold=True)
    title = "THE WORLD IN ONE DAY"
    draw.text(((W - tw(draw, title, f_title)) / 2, 8), title,
              font=f_title, fill=WHITE)
    # date ribbon
    draw.rectangle([0, 72, W, 110], fill=YELLOW)
    f_date = font(30, bold=True)
    draw.text((20, 76), "TUESDAY 17 NOVEMBER 2026", font=f_date, fill=INK)
    f_tag = font(17, bold=True)
    tag = "24 STORIES · 6 REGIONS"
    draw.text((W - 20 - tw(draw, tag, f_tag), 83), tag, font=f_tag, fill=INK)

    # lead panel
    draw_lead_art(draw, 16, 118, 468, 322)
    tx = 484
    chip(draw, tx, 118, 26, REGIONS["EU"][1], 1)
    f_kick = font(17, bold=True)
    draw.text((tx + 36, 122), "LEAD STORY · EUROPE", font=f_kick, fill=INK)
    f_head = font(46, bold=True)
    draw.text((tx, 148), "KERCH BRIDGE", font=f_head, fill=INK)
    draw.text((tx, 196), "IN RUINS", font=f_head, fill=INK)
    draw.rectangle([tx, 250, W - 16, 253], fill=RULE)
    f_sum = font(18)
    lines = wrap(draw, LEAD[3], f_sum, W - 16 - tx)
    if len(lines) > 3:
        warnings.append(f"lead summary wraps to {len(lines)} lines")
    for i, line in enumerate(lines):
        draw.text((tx, 260 + i * 22), line, font=f_sum, fill=INK)

    # map band
    f_sec = font(20, bold=True)
    draw.text((16, 330), "THE DAY ON THE MAP", font=f_sec, fill=INK)
    f_note = font(15)
    note = "every number is a story on this page"
    draw.text((MAP_X + MAP_W - tw(draw, note, f_note), 334), note,
              font=f_note, fill=GREY)
    draw_map(draw)
    # legend
    lx = 592
    f_leg = font(17, bold=True)
    draw.text((lx, 356), "SIX REGIONS", font=f_leg, fill=INK)
    counts = {"EU": 4, "ME": 5, "AS": 4, "NA": 8, "SA": 1, "AF": 2}
    f_name, f_cnt = font(18, bold=True), font(16)
    for i, key in enumerate(["EU", "ME", "AS", "NA", "SA", "AF"]):
        y = 388 + i * 31
        draw.rounded_rectangle([lx, y, lx + 20, y + 20], radius=4,
                               fill=REGIONS[key][1])
        draw.text((lx + 30, y - 1), REGIONS[key][0], font=f_name, fill=INK)
        cnt = f"· {counts[key]} stories" if counts[key] > 1 else "· 1 story"
        nw = tw(draw, REGIONS[key][0], f_name)
        draw.text((lx + 36 + nw, y + 1), cnt, font=f_cnt, fill=GREY)
    f_note2 = font(15)
    draw.text((lx, 576), "Markers match the story numbers below.",
              font=f_note2, fill=GREY)

    # top stories
    draw.rectangle([16, 596, W - 16, 599], fill=RULE)
    draw.text((16, 606), "SIX TOP STORIES", font=f_sec, fill=INK)
    f_top_h, f_top_s = font(21, bold=True), font(15)
    col_x = [16, 524]
    col_w = 484
    for i, (num, region, headline, summary) in enumerate(TOP):
        cx = col_x[i % 2]
        cy = 636 + (i // 2) * 60
        chip(draw, cx, cy, 28, REGIONS[region][1], num)
        if tw(draw, headline, f_top_h) > col_w - 40:
            warnings.append(f"top headline too wide: {headline}")
        draw.text((cx + 40, cy), headline, font=f_top_h, fill=INK)
        if tw(draw, summary, f_top_s) > col_w - 40:
            warnings.append(f"top summary too wide: {summary}")
        draw.text((cx + 40, cy + 31), summary, font=f_top_s, fill=GREY)

    # rest of the day
    draw.rectangle([16, 812, W - 16, 815], fill=RULE)
    f_rest_h = font(18, bold=True)
    draw.text((16, 822), "THE REST OF THE DAY — IN BRIEF", font=f_rest_h,
              fill=INK)
    f_num, f_line = font(15, bold=True), font(15)
    rest_cols = [16, 352, 688]
    rest_w = 320
    cells = [(num, region, text) for num, region, text in REST]
    cells.append((None, None, "Sources: Reuters · BBC · AP · CNN · NYT"))
    for i, (num, region, text) in enumerate(cells):
        cx = rest_cols[i % 3]
        cy = 852 + (i // 3) * 20
        if num is None:
            if tw(draw, text, f_line) > rest_w:
                warnings.append("sources line too wide")
            draw.text((cx, cy), text, font=f_line, fill=GREY)
            continue
        draw.text((cx, cy), str(num), font=f_num, fill=REGIONS[region][1])
        off = tw(draw, str(num), f_num) + 7
        if off + tw(draw, text, f_line) > rest_w:
            warnings.append(f"rest line too wide: {num} {text}")
        draw.text((cx + off, cy), text, font=f_line, fill=INK)

    # markets strip
    draw.rectangle([0, 984, W, H], fill=BLACK)
    f_mkt = font(19, bold=True)
    markets = ("MARKETS   Dow futures −0,6%  ·  Nasdaq +0,5%  ·  "
               "Gold $3,860  ·  Brent $93  ·  Bitcoin $64,500")
    draw.text(((W - tw(draw, markets, f_mkt)) / 2, 994), markets,
              font=f_mkt, fill=YELLOW)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG", optimize=True)
    for w_ in warnings:
        print("WARN:", w_)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
