#!/usr/bin/env python3
"""Round 3 renderer - "Night Edition".

Draws entry.png (1024x1024): one front page summing up the world news of
Tuesday 17 November 2026. Deep-navy theme, four flat-vector scene panels
(Kerch Bridge lead, Starship catch, carriers in the Gulf, Brazil 7-0),
an integrated world map with region-coloured numbered markers, briefs
for every remaining story and a markets strip. 100% programmatic PIL
text - no generated imagery, no garbled text. Deterministic: no clock,
no network, fixed seed only for star placement.
"""
import random

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(FONT_DIR + name, size)


F_TITLE = font(54, True)
F_DATE = font(33, True)
F_DATE_R = font(19, True)
F_KICK = font(17, True)
F_LEAD = font(50, True)
F_SUM = font(18)
F_SCENE_H = font(18, True)
F_SCENE_S = font(13)
F_MAP_H = font(18, True)
F_SMALL = font(13)
F_LEG = font(16, True)
F_LEG_N = font(15)
F_BRIEF_H = font(17, True)
F_BRIEF = font(13)
F_BRIEF_N = font(13, True)
F_MKT = font(17, True)
F_MARK = font(13, True)

# --- palette: night edition -------------------------------------------------
BG = (10, 22, 38)          # deep navy page
PANEL = (16, 35, 58)       # panel fill
PANEL_EDGE = (39, 75, 110)
CREAM = (244, 237, 222)
MUTED = (185, 198, 212)
GOLD = (240, 180, 28)
NAVY_TXT = (10, 22, 38)
SILHOUETTE = (8, 17, 32)
LAND = (27, 58, 92)
LAND_EDGE = (53, 100, 143)
OCEAN = (13, 31, 56)
GRATICULE = (24, 48, 78)

REGIONS = {
    "EU": ("Europe", (77, 163, 255)),
    "ME": ("Middle East", (255, 159, 46)),
    "AS": ("Asia", (255, 90, 90)),
    "NA": ("North America", (46, 211, 166)),
    "SA": ("South America", (185, 140, 255)),
    "AF": ("Africa", (255, 111, 181)),
}
STORY_REGION = {
    1: "EU", 2: "EU", 3: "ME", 4: "ME", 5: "ME", 6: "AS", 7: "ME", 8: "ME",
    9: "EU", 10: "AS", 11: "AS", 12: "EU", 13: "AS", 14: "NA", 15: "NA",
    16: "NA", 17: "NA", 18: "NA", 19: "NA", 20: "NA", 21: "NA", 22: "SA",
    23: "AF", 24: "AF",
}

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
WARNINGS = []


def tw(fnt, s):
    return d.textlength(s, font=fnt)


def check(fnt, s, maxw, label):
    w = tw(fnt, s)
    if w > maxw:
        WARNINGS.append(f"OVERFLOW {label}: {s!r} {w:.0f}px > {maxw}px")
    return w


def wrap(fnt, s, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if tw(fnt, trial) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_bands(x0, y0, x1, y1, top, bottom):
    """Vertical gradient made of 1px bands (deterministic)."""
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0))
        d.line([(x0, y), (x1, y)], fill=lerp(top, bottom, t))


def marker(cx, cy, num, region, r=11):
    col = REGIONS[region][1]
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=BG, width=2)
    s = str(num)
    w = tw(F_MARK, s)
    d.text((cx - w / 2, cy - 8), s, font=F_MARK, fill=NAVY_TXT)


# =============================================================================
# Illustrations (flat vector, one consistent silhouette style)
# =============================================================================

def illo_kerch(x0, y0, x1, y1):
    """Lead scene: Kerch Bridge at dusk, one span down in the water."""
    sky_bands(x0, y0, x1, y1 - 92, (38, 62, 102), (232, 135, 91))
    # sun low on the horizon
    d.ellipse([x1 - 128, y1 - 148, x1 - 72, y1 - 92], fill=(246, 205, 130))
    # sea
    d.rectangle([x0, y1 - 92, x1, y1], fill=(18, 48, 78))
    for i, wy in enumerate(range(y1 - 78, y1 - 8, 13)):
        off = (i % 3) * 26
        for wx in range(x0 + 14 + off, x1 - 30, 64):
            d.line([(wx, wy), (wx + 22, wy)], fill=(64, 110, 150), width=2)
    deck_y = y0 + 118
    # standing deck, left part
    d.rectangle([x0, deck_y, x0 + 268, deck_y + 9], fill=SILHOUETTE)
    # pylons
    for px in (x0 + 74, x0 + 196):
        d.rectangle([px, deck_y - 62, px + 12, deck_y + 44], fill=SILHOUETTE)
    # stay cables from pylon tops
    for px in (x0 + 80, x0 + 202):
        for dx in (-58, -34, 34, 58):
            d.line([(px, deck_y - 62), (px + dx, deck_y)], fill=SILHOUETTE, width=2)
    # collapsed span: tipped deck segment dropping into the sea
    d.polygon([(x0 + 268, deck_y + 2), (x0 + 348, deck_y + 46),
               (x0 + 344, deck_y + 56), (x0 + 268, deck_y + 12)], fill=SILHOUETTE)
    d.rectangle([x0 + 330, deck_y + 40, x0 + 338, y1 - 60], fill=SILHOUETTE)
    # foam where the span hit the water
    for fx, fw in ((x0 + 300, 66), (x0 + 268, 40), (x0 + 342, 34)):
        d.ellipse([fx, y1 - 90, fx + fw, y1 - 78], fill=(207, 227, 238))
    # far shore silhouette on the right
    d.polygon([(x0 + 392, deck_y + 6), (x1, deck_y - 6), (x1, deck_y + 12),
               (x0 + 392, deck_y + 14)], fill=SILHOUETTE)
    # smoke plume above the break
    for cx, cy, r in ((x0 + 306, deck_y - 30, 20), (x0 + 330, deck_y - 52, 26),
                      (x0 + 360, deck_y - 70, 32), (x0 + 396, deck_y - 82, 26)):
        d.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62], fill=(122, 130, 140))
    d.rectangle([x0, y0, x1, y1], outline=GOLD, width=2)


def illo_starship(x0, y0, x1, y1):
    """SpaceX Starship caught by the tower arms."""
    sky_bands(x0, y0, x1, y1, (10, 26, 52), (30, 62, 102))
    rng = random.Random(7)
    for _ in range(46):
        sx, sy = rng.randint(x0 + 4, x1 - 4), rng.randint(y0 + 4, y1 - 40)
        d.point((sx, sy), fill=(220, 230, 245))
    gy = y1 - 14
    d.rectangle([x0, gy, x1, y1], fill=SILHOUETTE)
    tx = x0 + 96  # tower (lighter than pure silhouette so it reads on the sky)
    tower_col = (30, 54, 82)
    d.rectangle([tx, y0 + 16, tx + 16, gy], fill=tower_col)
    for wy in range(y0 + 26, gy - 8, 16):  # tower cross braces
        d.line([(tx, wy), (tx + 16, wy + 10)], fill=(84, 118, 152), width=2)
    # chopstick arms reaching right, holding the ship
    d.polygon([(tx + 16, y0 + 40), (tx + 74, y0 + 52), (tx + 74, y0 + 60),
               (tx + 16, y0 + 52)], fill=tower_col)
    d.polygon([(tx + 16, y0 + 66), (tx + 74, y0 + 60), (tx + 74, y0 + 68),
               (tx + 16, y0 + 76)], fill=tower_col)
    # the ship: silver cylinder with a pointed nose, fins at the base
    sx = tx + 82
    d.polygon([(sx, y0 + 32), (sx + 13, y0 + 8), (sx + 26, y0 + 32)], fill=(216, 222, 232))
    d.rectangle([sx, y0 + 32, sx + 26, gy - 16], fill=(216, 222, 232))
    d.polygon([(sx, gy - 30), (sx - 12, gy - 2), (sx, gy - 2)], fill=(160, 170, 184))
    d.polygon([(sx + 26, gy - 30), (sx + 38, gy - 2), (sx + 26, gy - 2)], fill=(160, 170, 184))
    d.line([(sx, y0 + 52), (sx + 26, y0 + 52)], fill=(120, 130, 145), width=2)


def illo_carrier(x0, y0, x1, y1):
    """Aircraft carrier group in the Gulf at dawn."""
    sky_bands(x0, y0, x1, y1 - 30, (44, 66, 104), (238, 160, 96))
    d.ellipse([x0 + 36, y0 + 12, x0 + 76, y0 + 52], fill=(246, 205, 130))
    d.rectangle([x0, y1 - 30, x1, y1], fill=(16, 44, 74))
    for wx in range(x0 + 12, x1 - 20, 52):
        d.line([(wx, y1 - 12), (wx + 20, y1 - 12)], fill=(64, 110, 150), width=2)
    hy = y1 - 44  # hull line
    # main carrier: long flat deck, island, hull
    d.polygon([(x0 + 58, hy), (x0 + 268, hy), (x0 + 256, hy + 14),
               (x0 + 76, hy + 14)], fill=SILHOUETTE)
    d.rectangle([x0 + 52, hy - 7, x0 + 274, hy], fill=SILHOUETTE)
    d.rectangle([x0 + 196, hy - 26, x0 + 214, hy - 7], fill=SILHOUETTE)
    d.line([(x0 + 205, hy - 40), (x0 + 205, hy - 26)], fill=SILHOUETTE, width=3)
    # escort ship behind, smaller
    d.polygon([(x0 + 236, hy + 4), (x0 + 300, hy + 4), (x0 + 294, hy + 12),
               (x0 + 244, hy + 12)], fill=(20, 34, 54))
    d.rectangle([x0 + 258, hy - 4, x0 + 270, hy + 4], fill=(20, 34, 54))
    # wake
    d.line([(x0 + 40, hy + 16), (x0 + 76, hy + 16)], fill=(150, 185, 210), width=2)


def illo_football(x0, y0, x1, y1):
    """Football pitch: striped grass, line markings, a ball."""
    for i in range(6):
        col = (27, 110, 63) if i % 2 == 0 else (34, 128, 74)
        d.rectangle([x0 + i * (x1 - x0) // 6, y0, x0 + (i + 1) * (x1 - x0) // 6, y1], fill=col)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.line([(cx, y0 + 4), (cx, y1 - 4)], fill=(230, 240, 230), width=2)
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=(230, 240, 230), width=2)
    d.rectangle([x0 + 6, cy - 24, x0 + 34, cy + 24], outline=(230, 240, 230), width=2)
    d.rectangle([x1 - 34, cy - 24, x1 - 6, cy + 24], outline=(230, 240, 230), width=2)
    # ball
    bx, by = x1 - 84, y0 + 26
    d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=(245, 245, 245))
    d.polygon([(bx - 4, by - 4), (bx + 4, by - 4), (bx + 6, by + 3),
               (bx, by + 7), (bx - 6, by + 3)], fill=SILHOUETTE)


# =============================================================================
# World map (stylised equirectangular polygons, lon/lat)
# =============================================================================

CONTINENTS = [
    # North America
    [(-168, 65), (-150, 70), (-135, 69), (-125, 71), (-110, 72), (-95, 76),
     (-88, 77), (-82, 74), (-80, 72), (-86, 68), (-93, 66), (-95, 60),
     (-92, 57), (-86, 54), (-82, 48), (-79, 44), (-75, 40), (-70, 44),
     (-66, 45), (-70, 42), (-74, 39), (-77, 35), (-80, 32), (-81, 26),
     (-84, 30), (-89, 29), (-94, 29), (-97, 26), (-97, 21), (-94, 18),
     (-90, 15), (-86, 13), (-83, 9), (-79, 9), (-84, 12), (-90, 14),
     (-96, 16), (-102, 18), (-106, 21), (-110, 23), (-114, 28), (-117, 33),
     (-122, 37), (-124, 46), (-130, 54), (-142, 60), (-156, 58), (-165, 60)],
    # Greenland
    [(-46, 60), (-32, 68), (-22, 70), (-20, 76), (-28, 82), (-44, 80),
     (-54, 76), (-57, 68), (-53, 60)],
    # South America
    [(-79, 9), (-75, 11), (-70, 12), (-64, 10), (-55, 6), (-50, 0),
     (-44, -3), (-35, -8), (-39, -13), (-40, -20), (-48, -26), (-52, -32),
     (-58, -38), (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54),
     (-73, -49), (-73, -42), (-72, -34), (-70, -24), (-70, -18), (-75, -15),
     (-79, -8), (-81, -4), (-80, 1), (-77, 4), (-79, 9)],
    # Africa
    [(-6, 35), (0, 36), (10, 37), (20, 32), (30, 31), (34, 28), (36, 23),
     (38, 20), (40, 15), (43, 12), (49, 11), (51, 12), (48, 4), (42, -2),
     (40, -9), (38, -18), (36, -22), (33, -27), (28, -33), (20, -35),
     (17, -32), (15, -27), (13, -18), (12, -11), (13, -5), (9, -1),
     (9, 4), (3, 6), (-4, 5), (-9, 5), (-14, 8), (-17, 13), (-17, 16),
     (-16, 21), (-15, 26), (-13, 29), (-9, 32), (-6, 35)],
    # Eurasia (coarse single landmass)
    [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-5, 48), (0, 49), (2, 51),
     (7, 54), (8, 57), (5, 58), (6, 61), (12, 56), (18, 56), (21, 60),
     (24, 66), (31, 70), (45, 68), (58, 69), (70, 72), (82, 73), (95, 76),
     (105, 77), (115, 74), (128, 72), (142, 72), (155, 70), (168, 67),
     (178, 65), (178, 62), (164, 60), (159, 55), (152, 48), (143, 44),
     (141, 40), (136, 35), (130, 33), (127, 38), (122, 38), (121, 34),
     (122, 30), (119, 26), (114, 22), (109, 19), (107, 13), (104, 6),
     (101, 7), (99, 11), (96, 16), (93, 17), (90, 22), (87, 21), (85, 19),
     (80, 14), (77, 8), (76, 11), (73, 18), (71, 21), (67, 24), (62, 25),
     (58, 25), (55, 25), (52, 28), (50, 29), (49, 26), (51, 24), (55, 24),
     (58, 22), (59, 21), (56, 18), (54, 16), (51, 14), (47, 13), (44, 12),
     (43, 13), (41, 17), (39, 21), (36, 25), (35, 29), (34, 31), (36, 36),
     (31, 36), (28, 37), (24, 36), (20, 39), (16, 38), (13, 38), (10, 37),
     (7, 37), (3, 37), (0, 36), (-3, 36), (-6, 36), (-9, 37)],
    # UK
    [(-5, 50), (-3, 53), (-4, 56), (-6, 57), (-8, 54), (-8, 51), (-5, 50)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (139, 38), (141, 41), (142, 44),
     (140, 42), (138, 37), (134, 34), (131, 32)],
    # Indonesia (stylised island chain)
    [(96, 5), (101, 1), (107, -3), (113, -3), (119, -2), (125, -1),
     (131, -3), (136, -2), (131, 1), (122, 1), (113, 1), (104, 3), (98, 6)],
    # Australia
    [(113, -22), (114, -29), (116, -34), (120, -34), (126, -32), (131, -32),
     (134, -33), (136, -35), (139, -37), (144, -38), (148, -38), (151, -34),
     (153, -28), (153, -24), (149, -20), (145, -16), (142, -11), (141, -15),
     (140, -18), (136, -15), (135, -12), (132, -11), (129, -14), (125, -15),
     (121, -18), (117, -20), (113, -22)],
    # New Zealand
    [(167, -46), (171, -44), (173, -41), (176, -38), (175, -40), (172, -43),
     (169, -47), (167, -46)],
]

MARKERS = {  # story: (lon, lat, dx_px, dy_px) - nudges spread the clusters
    1: (37.0, 45.0, 2, -12), 2: (30.5, 50.4, -10, -8), 3: (50.6, 26.2, 2, -12),
    4: (51.4, 35.7, -6, -16), 5: (56.3, 26.5, 16, 2), 6: (121.0, 14.6, 0, 0),
    7: (35.2, 31.8, -12, -4), 8: (35.4, 31.9, 10, 12), 9: (0.0, 51.5, -7, -5),
    10: (116.4, 39.9, 0, 0), 11: (139.7, 35.7, 0, 0), 12: (6.1, 46.2, 5, 5),
    13: (78.0, 21.0, 0, 0), 14: (-93.0, 42.0, -26, -14), 15: (-74.0, 40.7, 24, -16),
    16: (-122.0, 37.4, 0, 0), 17: (-77.0, 38.9, -8, 2), 18: (-77.1, 38.9, 26, 16),
    19: (-80.2, 25.8, 10, 14), 20: (-97.2, 25.9, -16, 12), 21: (-155.0, 19.0, 0, 0),
    22: (-52.0, -10.0, 0, 0), 23: (36.8, -1.3, 0, 0), 24: (28.0, -26.2, 0, 0),
}


def draw_map(x0, y0, x1, y1):
    """Render the map on its own layer so land polygons clip at the panel."""
    layer = Image.new("RGB", (x1 - x0, y1 - y0), OCEAN)
    md = ImageDraw.Draw(layer)
    lat_top, lat_bot = 58.0, -32.0
    sx = (x1 - x0) / 360.0
    sy = (y1 - y0) / (lat_top - lat_bot)

    def px(lon, lat):
        return ((lon + 180) * sx, (lat_top - lat) * sy)

    for glon in range(-150, 181, 30):
        gx, _ = px(glon, 0)
        md.line([(gx, 0), (gx, y1 - y0)], fill=GRATICULE, width=1)
    for glat in range(-30, 61, 30):
        _, gy = px(0, glat)
        md.line([(0, gy), (x1 - x0, gy)], fill=GRATICULE, width=1)
    for poly in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in poly]
        md.polygon(pts, fill=LAND, outline=LAND_EDGE)
    img.paste(layer, (x0, y0))
    d.rectangle([x0, y0, x1, y1], outline=PANEL_EDGE, width=1)
    for num, (lon, lat, dx, dy) in MARKERS.items():
        cx, cy = px(lon, lat)
        marker(int(x0 + cx + dx), int(y0 + cy + dy), num, STORY_REGION[num], r=10)


# =============================================================================
# Page composition
# =============================================================================

MX = 26            # side margin
RIGHT = W - MX     # 998

# --- masthead ---------------------------------------------------------------
title = "THE WORLD IN ONE DAY"
check(F_TITLE, title, RIGHT - MX, "title")
d.text(((W - tw(F_TITLE, title)) / 2, 18), title, font=F_TITLE, fill=CREAM)
d.line([(MX, 88), (RIGHT, 88)], fill=GOLD, width=3)

# --- date ribbon --------------------------------------------------------------
d.rectangle([MX, 96, RIGHT, 144], fill=GOLD)
d.text((MX + 16, 104), "TUESDAY 17 NOVEMBER 2026", font=F_DATE, fill=NAVY_TXT)
rt = "24 STORIES · 6 REGIONS"
check(F_DATE_R, rt, 300, "ribbon-right")
d.text((RIGHT - 16 - tw(F_DATE_R, rt), 111), rt, font=F_DATE_R, fill=NAVY_TXT)

# --- lead story: Kerch Bridge ---------------------------------------------------
LY0, LY1 = 158, 414
illo_kerch(MX, LY0, 486, LY1)
marker(MX + 24, LY0 + 24, 1, "EU")
LX = 508
d.rectangle([LX, LY0 + 2, LX + 14, LY0 + 20], fill=REGIONS["EU"][1])
kick = "LEAD STORY — EUROPE"
d.text((LX + 22, LY0), kick, font=F_KICK, fill=GOLD)
for i, line in enumerate(("KERCH BRIDGE", "IN RUINS")):
    check(F_LEAD, line, RIGHT - LX, "lead headline")
    d.text((LX, LY0 + 34 + i * 60), line, font=F_LEAD, fill=CREAM)
summary = ("A Ukrainian strike collapses a span of the bridge linking Russia "
           "to Crimea. Moscow vows to rebuild - while Russian missiles cut "
           "power and water in Kyiv.")
sy = LY0 + 162
for line in wrap(F_SUM, summary, RIGHT - LX):
    d.text((LX, sy), line, font=F_SUM, fill=MUTED)
    sy += 25
d.text((LX, LY1 - 20), "BBC · Reuters", font=F_SMALL, fill=(140, 158, 176))

# --- scene strip: three drawn panels -------------------------------------------
SCENES = [
    (20, illo_starship, "SPACEX CATCHES STARSHIP",
     "Tower arms catch ship after 14 orbits"),
    (5, illo_carrier, "THIRD U.S. CARRIER IN GULF",
     "Tanker hit near the Strait of Hormuz"),
    (22, illo_football, "BRAZIL HIT SINGAPORE 7-0",
     "Vinicius hat-trick in 21 minutes"),
]
SY0, SY1, PW, GAP = 430, 592, 316, 12
for i, (num, illo, head, sub) in enumerate(SCENES):
    px0 = MX + i * (PW + GAP)
    px1 = px0 + PW
    d.rectangle([px0, SY0, px1, SY1], fill=PANEL, outline=PANEL_EDGE, width=1)
    illo(px0 + 3, SY0 + 3, px1 - 3, SY0 + 99)
    marker(px0 + 24, SY0 + 24, num, STORY_REGION[num])
    check(F_SCENE_H, head, PW - 20, "scene headline")
    d.text((px0 + 10, SY0 + 108), head, font=F_SCENE_H, fill=CREAM)
    check(F_SCENE_S, sub, PW - 20, "scene sub")
    d.text((px0 + 10, SY0 + 134), sub, font=F_SCENE_S, fill=MUTED)

# --- map band --------------------------------------------------------------------
MY0 = 608
d.text((MX, MY0), "THE DAY ON THE MAP", font=F_MAP_H, fill=GOLD)
note = "every number is a story on this page"
d.text((RIGHT - tw(F_SMALL, note), MY0 + 3), note, font=F_SMALL, fill=MUTED)
draw_map(MX, 636, 666, 796)
LX2 = 682
counts = {"EU": 4, "ME": 5, "AS": 4, "NA": 8, "SA": 1, "AF": 2}
ly = 642
for key in ("EU", "ME", "AS", "NA", "SA", "AF"):
    name, col = REGIONS[key]
    d.rectangle([LX2, ly + 2, LX2 + 14, ly + 16], fill=col)
    d.text((LX2 + 22, ly), name, font=F_LEG, fill=CREAM)
    nw = tw(F_LEG, name)
    cword = "story" if counts[key] == 1 else "stories"
    d.text((LX2 + 30 + nw, ly + 1), f"· {counts[key]} {cword}",
           font=F_LEG_N, fill=MUTED)
    ly += 26
d.text((LX2, ly + 2), "Markers match the story numbers below.",
       font=F_SMALL, fill=MUTED)

# --- briefs ----------------------------------------------------------------------
BY0 = 812
d.text((MX, BY0), "THE REST OF THE DAY — IN BRIEF", font=F_BRIEF_H, fill=GOLD)
src = "Sources: Reuters · BBC · AP · CNN · NYT + more"
d.text((RIGHT - tw(F_SMALL, src), BY0 + 3), src, font=F_SMALL, fill=MUTED)

BRIEFS = [
    (2, "Kyiv bridges hit; power, water cut"),
    (3, "Iran drones hit U.S. radar — downed"),
    (4, "U.S. says Iran weighs 'dirty bomb'"),
    (6, "Trump in Asia: ASEAN, APEC, Xi talks"),
    (7, "Netanyahu allies in vote probe"),
    (8, "Settlers kill woman, 72, near Jericho"),
    (9, "Britain sanctions settler firms"),
    (10, "Xi, Carney cut tariffs ~$280m"),
    (11, "Japan jets scramble on Russian planes"),
    (12, "128 nations weigh robot-weapons ban"),
    (13, "Climate talks split over IPCC reports"),
    (14, "Data centres emit like Denmark"),
    (15, "JPMorgan bug disrupts U.S. banks"),
    (16, "Nvidia results due after the bell"),
    (17, "U.S. closes AI-chip loophole on China"),
    (18, "Pentagon fails 9th straight audit"),
    (19, "GTA VI: 10m pre-orders, out Thursday"),
    (21, "Voyager 1 now one light-day out"),
    (23, "South Africa edge Kenya 2-1"),
    (24, "17 shot dead in South Africa"),
]
COLS = [BRIEFS[0:7], BRIEFS[7:14], BRIEFS[14:20]]
for ci, col_items in enumerate(COLS):
    cx0 = MX + ci * (PW + GAP)
    for ri, (num, text) in enumerate(col_items):
        ry = 842 + ri * 16
        ns = str(num)
        d.text((cx0, ry), ns, font=F_BRIEF_N, fill=REGIONS[STORY_REGION[num]][1])
        off = tw(F_BRIEF_N, ns) + 6
        check(F_BRIEF, text, PW - off, f"brief {num}")
        d.text((cx0 + off, ry), text, font=F_BRIEF, fill=CREAM)

# --- markets strip -----------------------------------------------------------------
d.rectangle([MX, 962, RIGHT, 1002], fill=GOLD)
mkt = ("MARKETS — Dow futures -0.6% · Nasdaq +0.5% · Gold $3,860 · "
       "Brent $93 · Bitcoin $64,500")
check(F_MKT, mkt, RIGHT - MX - 20, "markets")
d.text(((W - tw(F_MKT, mkt)) / 2, 973), mkt, font=F_MKT, fill=NAVY_TXT)

for wmsg in WARNINGS:
    print("WARN:", wmsg)
img.save("entry.png")
print("saved entry.png", img.size)
