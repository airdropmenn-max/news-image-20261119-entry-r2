#!/usr/bin/env python3
"""Render 'The World in One Day' - Thursday 19 November 2026.

A dense newspaper front page drawn entirely with PIL shapes:
masthead + date, 3 big illustrated hero stories, 10 small stories
with bold icons, a numbered 14-45 brief list, a world map with
big numbered pins, and a sources footer. All 45 stories happened
or were first reported on Thursday 19 November 2026.
Deterministic: same bytes on every run. No network, no randomness.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

PAPER = (247, 242, 231)
INK = (26, 26, 26)
MUTED = (90, 86, 78)
RED = (178, 34, 34)
RULE = (60, 58, 52)
SEA = (223, 233, 236)
LAND = (196, 198, 168)
LAND_EDGE = (90, 85, 70)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
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
    return lines


def text(d, xy, s, fnt, fill=INK, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)


# (number, region, headline, summary, pin lon, pin lat)
BIG = [
    (1, "NORTH AMERICA", "Vice City opens its doors",
     "Grand Theft Auto VI begins its global rollout after a 13-year wait, "
     "with gamers queueing worldwide.", -80, 26),
    (2, "ASIA", "Three leaders, one table in Shenzhen",
     "Trump, Xi and Putin hold trilateral talks on the sidelines of the "
     "APEC summit in Shenzhen.", 114, 22),
    (3, "SPACE", "Voyager 1, one light-day out",
     "NASA confirms the 48-year-old probe has reached a light-day from "
     "Earth - a first for any spacecraft.", -118, 34),
]

SMALL = [
    (4, "NORTH AMERICA", "Jeffries poised to make history",
     "Democrats nominate Hakeem Jeffries for Speaker; he would be the "
     "first Black Speaker.", -77, 39),
    (5, "MIDDLE EAST", "Gulf strikes widen",
     "US and Iran exchange fire again as Tehran's attacks spread to Kuwait "
     "and Bahrain.", 51, 26),
    (6, "ASIA", "Cyclone Akvan bears down on India",
     "The storm is set to cross the coast between Machilipatnam and Puri.",
     89, 17),
    (7, "EUROPE", "\u20ac45bn lifeline for Kyiv",
     "The EU proposes a loan for Ukraine, to be repaid once Russia pays "
     "reparations.", 4, 51),
    (8, "OCEANIA", "Canberra sanctions settlers",
     "Australia sanctions Israeli settlers and groups over West Bank "
     "expansion.", 149, -35),
    (9, "TECH", "Nvidia cuts China off H-series",
     "The chipmaker halts Hopper shipments to China as acting chief Kress "
     "promises earlier pay rises.", -122, 37),
    (10, "EUROPE", "Tanker sunk by projectiles",
     "An LPG tanker that sank off Bulgaria was hit by projectiles, "
     "officials say.", 28, 43),
    (11, "MIDDLE EAST", "Tanks push into central Gaza",
     "Israeli forces launch a fresh ground operation west of the Yellow "
     "Line.", 34, 31),
    (12, "NORTH AMERICA", "Peltola seals the Senate",
     "Democrat Peltola wins Alaska, giving Democrats a 56-44 Senate "
     "majority.", -150, 64),
    (13, "ASIA", "Royals in Delhi, defence in Tokyo",
     "Modi meets the Prince and Princess of Wales; India and Japan open "
     "2+2 defence talks.", 140, 36),
]

ALSO = [
    "Earth is missing a billion years of history - scientists may have found why.",
    "Fed minutes: most officials expect further rate hikes.",
    "Oil falls as WTI closes at $83.26 amid Gulf tensions.",
    "NSA's classified internal network suffers an outage, reports say.",
    "Somalia accuses the UAE of building secret military bases.",
    "Deutsche Bank handled $582m in Epstein-linked deals, the FT reports.",
    "Saudi forces launch a major attack on Houthi rebels in Yemen.",
    "Riyadh says the danger has passed in three southern cities.",
    "Islam on track to be the world's largest religion by 2035, Pew finds.",
    "Liu Yunping becomes the first Taiwanese American House caucus chair.",
    "Microsoft in talks to sell AI services to ByteDance.",
    "US senators warn AI cyber threats are outpacing defences.",
    "Canada rethinks China ties as Carney chases a US deal.",
    "French minister says Melenchon could win the presidency.",
    "Cocaine and millions of pills seized in eastern Libya.",
    "US proposes tougher green-card rules and longer hiring.",
    "General Pants collapses into administration before Black Friday.",
    "ASX falls for a fifth straight session on a Wall Street rout.",
    "Australia's central bank board split over lifting rates.",
    "Australia moves to ban photographs of defence sites.",
    "Duckett's 133 puts England on top in the third ODI.",
    "Merck launches a self-amplifying mRNA rabies vaccine for pets.",
    "School bus bursts into flames; the driver is hailed a hero.",
    "Mother and daughter freed unharmed in a $1m Melbourne hostage ordeal.",
    "Fifty pupils hospitalised after pollution from a tar-mixing unit in India.",
    "Air India 171 crash probe report at its 'fag end', Centre tells court.",
    "Ukraine 'destroying the occupiers' as Russia attacks, Kyiv says.",
    # 41 rewritten (fix 5): same claim, now a clear standalone headline.
    "Gates: only a huge cyberattack would bring a new expert-led world order (claim).",
    "Huang's Nvidia exit sends shockwaves through the AI world.",
    "Taiwan drafts a transnational-repression crime into law.",
    "Brazil wind additions fall below 400 MW in 2026 as developers shift.",
    "AI data centres could soon rival coal plants on power use.",
]

# Simplified continent outlines in (lon, lat). Coarse on purpose: the
# map must read at ~300px, so bold shapes beat fine detail.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-110, 73), (-95, 80), (-85, 70),
     (-75, 72), (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35),
     (-80, 32), (-84, 30), (-90, 29), (-97, 26), (-105, 20), (-95, 16),
     (-87, 13), (-80, 9), (-83, 9), (-90, 14), (-97, 16), (-105, 20),
     (-110, 23), (-115, 28), (-120, 33), (-125, 40), (-125, 48),
     (-130, 55), (-140, 60), (-155, 58), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 70), (-55, 76), (-65, 75), (-60, 70)],
    # South America
    [(-80, 9), (-75, 11), (-70, 12), (-62, 10), (-55, 6), (-50, 0),
     (-45, -5), (-38, -8), (-35, -10), (-40, -20), (-48, -28), (-55, -35),
     (-62, -40), (-68, -50), (-70, -55), (-73, -50), (-73, -40),
     (-72, -30), (-70, -20), (-75, -15), (-80, -5), (-81, 0)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (45, 0), (40, -10), (35, -20),
     (32, -28), (25, -33), (18, -35), (15, -27), (12, -18), (9, -1),
     (9, 4), (-8, 5), (-13, 8)],
    # Asia (drawn before Europe so Europe sits on top)
    [(30, 70), (40, 68), (50, 69), (60, 70), (70, 72), (80, 73), (90, 75),
     (100, 77), (110, 76), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 69), (170, 66), (178, 65), (170, 60), (162, 58), (158, 52),
     (150, 59), (142, 55), (140, 45), (135, 42), (130, 38), (127, 35),
     (122, 32), (120, 28), (115, 22), (110, 20), (108, 12), (105, 9),
     (100, 8), (98, 12), (95, 16), (92, 20), (88, 22), (85, 19), (80, 15),
     (76, 10), (75, 15), (72, 20), (68, 22), (65, 25), (60, 25), (55, 26),
     (52, 28), (50, 30), (48, 29), (44, 29), (40, 28), (38, 32), (36, 36),
     (33, 36), (30, 38), (28, 41), (30, 45), (30, 55), (30, 65)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (20, 55), (23, 58), (28, 60), (30, 62), (30, 70),
     (25, 71), (18, 69), (12, 65), (5, 60), (5, 58), (-2, 55), (-5, 50),
     (-10, 45)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (137, -38), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 39),
     (141, 41), (140, 44), (142, 44), (144, 43), (141, 40), (139, 37),
     (136, 35), (133, 34), (130, 33)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (174, -41),
     (171, -44), (168, -46)],
]


def draw_hero1(d, x, y, w, h):
    """Vice City / GTA VI: neon sunset skyline, proper pink sports car,
    road markings, queue of gamers. The eye-stopping panel (fix 6)."""
    # Sunset sky: pink -> orange -> dusk purple, in horizontal bands.
    bands = [(255, 96, 150), (255, 140, 110), (255, 178, 90),
             (200, 110, 130), (90, 45, 110), (45, 25, 80)]
    bh = h // len(bands) + 1
    for i, c in enumerate(bands):
        d.rectangle([x, y + i * bh, x + w, y + (i + 1) * bh], fill=c)
    # Low sun with glow.
    sx, sy = x + w - 58, y + 26
    d.ellipse([sx - 30, sy - 30, sx + 30, sy + 30], fill=(255, 200, 120))
    d.ellipse([sx - 20, sy - 20, sx + 20, sy + 20], fill=(255, 232, 160))
    # Skyline silhouettes with lit windows (deterministic pattern).
    towers = [(0, 52, 34), (36, 68, 30), (68, 44, 26), (96, 74, 34),
              (132, 58, 30), (164, 80, 32), (198, 50, 28), (228, 66, 30),
              (260, 56, 28), (290, 70, 32)]
    base = y + 96
    for tx, th, tw in towers:
        d.rectangle([x + tx, base - th, x + tx + tw, base], fill=(28, 18, 48))
        for wy in range(base - th + 6, base - 4, 9):
            for wx in range(x + tx + 5, x + tx + tw - 4, 9):
                if (wx + wy) % 18 == 0:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 220, 120))
    # "VICE CITY" sign on the tallest tower's dark face.
    text(d, (x + 170, base - 62), "VICE CITY", font(SANS_B, 10),
         fill=(255, 240, 200))
    # Palm trees flanking the street.
    for px, flip in ((x + 14, 1), (x + w - 16, -1)):
        d.line([px, base, px + 4 * flip, base - 34], fill=(40, 25, 15), width=4)
        for k in range(5):
            ang = -0.4 - k * 0.35
            ex = px + int(16 * flip * (1 if k % 2 == 0 else 0.6))
            d.arc([px - 14, base - 52, px + 14, base - 22],
                  start=200 + k * 12, end=245 + k * 12,
                  fill=(20, 90, 50), width=3)
    # Street + sidewalk + dashed centre line.
    d.rectangle([x, base, x + w, y + h], fill=(24, 24, 30))
    d.rectangle([x, base, x + w, base + 4], fill=(120, 115, 110))
    for lx in range(x + 6, x + w - 10, 22):
        d.rectangle([lx, y + h - 12, lx + 12, y + h - 9], fill=(250, 250, 250))
    # The pink sports car: proper silhouette, windows, wheels, headlights.
    cx, cy = x + w // 2 - 8, y + h - 26
    d.ellipse([cx - 112, cy + 8, cx + 112, cy + 16], fill=(12, 12, 16))
    body = [(cx - 104, cy + 6), (cx - 100, cy - 12), (cx - 62, cy - 20),
            (cx - 28, cy - 22), (cx + 26, cy - 20), (cx + 72, cy - 14),
            (cx + 102, cy - 4), (cx + 104, cy + 6)]
    d.polygon(body, fill=(255, 64, 158), outline=(150, 10, 80))
    # Cabin windows with a white highlight slash.
    d.polygon([(cx - 56, cy - 18), (cx - 26, cy - 20), (cx - 22, cy - 6),
               (cx - 56, cy - 6)], fill=(18, 24, 44))
    d.polygon([(cx - 14, cy - 20), (cx + 22, cy - 18), (cx + 40, cy - 6),
               (cx - 14, cy - 6)], fill=(18, 24, 44))
    d.line([cx - 48, cy - 17, cx - 34, cy - 8], fill=(255, 255, 255), width=2)
    # Wheels with hubs + headlight beam.
    for wx in (cx - 66, cx + 64):
        d.ellipse([wx - 13, cy - 6, wx + 13, cy + 12], fill=(10, 10, 12),
                  outline=(60, 60, 66), width=2)
        d.ellipse([wx - 5, cy + 1, wx + 5, cy + 9], fill=(200, 200, 210))
    d.ellipse([cx + 96, cy - 8, cx + 106, cy - 1], fill=(255, 244, 190))
    d.polygon([(cx + 104, cy - 6), (cx + 118, cy - 14), (cx + 118, cy + 2),
               (cx + 104, cy - 1)], fill=(255, 240, 170))
    # Queue of gamers at the kerb, right side.
    for i, qx in enumerate((x + w - 96, x + w - 78, x + w - 60)):
        qy = base - 2
        d.ellipse([qx - 4, qy - 26, qx + 4, qy - 18], fill=(235, 200, 170))
        d.rectangle([qx - 6, qy - 17, qx + 6, qy], fill=(30 + i * 20, 30, 60))
    # Small red number badge for the story.
    badge(d, x + 16, y + 14, 1)


def draw_hero2(d, x, y, w, h):
    """Shenzhen summit: three leaders seated at a table (fix 1).
    Warm wood wall, small flags as backdrop only, name plates on table."""
    # Warm wood-panel wall.
    for i in range(0, h, 8):
        c = (168 + (i % 16), 118 + (i % 12), 70 + (i % 10))
        d.rectangle([x, y + i, x + w, y + i + 8], fill=c)
    for vx in range(x + 44, x + w, 44):
        d.line([vx, y, vx, y + h], fill=(120, 82, 48), width=2)
    # Warm ceiling glow, kept inside the panel.
    d.ellipse([x + w // 2 - 90, y + 2, x + w // 2 + 90, y + 30],
              fill=(255, 214, 130))
    # Backdrop flags on poles (small, behind the leaders).
    def flag(fx, kind):
        d.line([fx + 14, y + 6, fx + 14, y + 34], fill=(60, 40, 20), width=2)
        if kind == "us":
            for s in range(6):
                d.rectangle([fx, y + 8 + s * 3, fx + 28, y + 10 + s * 3],
                            fill=(178, 34, 34) if s % 2 == 0 else (255, 255, 255))
            d.rectangle([fx, y + 8, fx + 12, y + 17], fill=(40, 60, 140))
        elif kind == "cn":
            d.rectangle([fx, y + 8, fx + 28, y + 26], fill=(200, 30, 30))
            d.ellipse([fx + 4, y + 11, fx + 10, y + 17], fill=(255, 220, 0))
        else:
            d.rectangle([fx, y + 8, fx + 28, y + 14], fill=(255, 255, 255))
            d.rectangle([fx, y + 14, fx + 28, y + 20], fill=(40, 80, 200))
            d.rectangle([fx, y + 20, fx + 28, y + 26], fill=(200, 30, 30))
    flag(x + 22, "us")
    flag(x + w // 2 - 14, "cn")
    flag(x + w - 50, "ru")
    # Three seated leaders: head + hair + suit + tie, distinct each.
    leaders = [
        (x + 62, (235, 200, 170), (200, 200, 200), (30, 40, 80), (178, 34, 34)),
        (x + w // 2, (225, 190, 160), (40, 35, 30), (45, 45, 50), (40, 80, 200)),
        (x + w - 62, (240, 210, 180), (220, 190, 120), (20, 30, 60), (120, 60, 20)),
    ]
    for lx, skin, hair, suit, tie in leaders:
        # Shoulders / suit.
        d.polygon([(lx - 34, y + 108), (lx - 26, y + 66), (lx + 26, y + 66),
                   (lx + 34, y + 108)], fill=suit)
        # Shirt + tie.
        d.polygon([(lx - 7, y + 68), (lx + 7, y + 68), (lx, y + 84)],
                  fill=(255, 255, 255))
        d.polygon([(lx - 3, y + 70), (lx + 3, y + 70), (lx + 4, y + 92),
                   (lx, y + 98), (lx - 4, y + 92)], fill=tie)
        # Head + hair cap.
        d.ellipse([lx - 14, y + 34, lx + 14, y + 62], fill=skin)
        d.pieslice([lx - 14, y + 34, lx + 14, y + 56], start=180, end=360,
                   fill=hair)
        # Microphone on a thin stem.
        d.line([lx + 20, y + 96, lx + 26, y + 76], fill=(20, 20, 20), width=2)
        d.ellipse([lx + 23, y + 72, lx + 29, y + 78], fill=(20, 20, 20))
    # Long table with name plates.
    d.polygon([(x + 8, y + 108), (x + w - 8, y + 108), (x + w, y + h),
               (x, y + h)], fill=(96, 58, 32))
    d.line([x + 8, y + 108, x + w - 8, y + 108], fill=(190, 140, 90), width=3)
    for lx, _, _, _, _ in leaders:
        d.rectangle([lx - 17, y + 114, lx + 17, y + 126], fill=(250, 246, 236),
                    outline=(120, 100, 80))
        d.rectangle([lx - 17, y + 114, lx - 7, y + 126], fill=(178, 34, 34))
    badge(d, x + 16, y + 14, 2)


def draw_hero3(d, x, y, w, h):
    """Voyager 1: deep space, Earth with clouds, gold probe on a
    dashed trajectory, label readable at small size."""
    d.rectangle([x, y, x + w, y + h], fill=(8, 12, 35))
    # Deterministic star field (no random module).
    for i in range(46):
        sx = x + (i * 53 + 11) % w
        sy = y + (i * 37 + 7) % h
        r = 1 + (i % 3 == 0)
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))
    # Milky Way band of faint dots.
    for i in range(26):
        mx = x + (i * 13) % w
        my = y + 20 + (i * 11) % 60
        d.ellipse([mx - 1, my - 1, mx + 1, my + 1], fill=(170, 190, 230))
    # Earth, lower left, kept fully inside the picture.
    ex, ey, er = x + 70, y + h - 18, 40
    d.ellipse([ex - er - 4, ey - er - 4, ex + er + 4, ey + er + 4],
              fill=(70, 150, 230))
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(38, 108, 198))
    d.ellipse([ex - 30, ey - 34, ex - 6, ey - 18], fill=(64, 164, 96))
    d.ellipse([ex + 2, ey - 8, ex + 30, ey + 12], fill=(64, 164, 96))
    d.ellipse([ex - 38, ey + 4, ex - 12, ey + 16], fill=(150, 120, 80))
    for cxx, cyy in ((ex - 26, ey - 26), (ex + 8, ey - 30), (ex + 16, ey + 12)):
        d.ellipse([cxx - 12, cyy - 4, cxx + 12, cyy + 4], fill=(255, 255, 255))
    # Dashed trajectory from Earth to the probe.
    px, py = x + w - 62, y + 42
    for t in range(0, 11):
        tx = ex + (px - ex) * t / 10
        ty = (ey - 40) + (py - (ey - 40)) * t / 10 - 18 * (t / 10) * (1 - t / 10)
        if t % 2 == 0:
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(255, 255, 255))
    # Gold Voyager probe: dish + body + boom.
    d.line([px - 26, py + 8, px + 26, py - 8], fill=(200, 200, 210), width=2)
    d.ellipse([px - 13, py - 13, px + 13, py + 13], fill=(224, 182, 62),
              outline=(160, 120, 30), width=2)
    d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(255, 230, 140))
    d.rectangle([px + 12, py + 2, px + 30, py + 10], fill=(180, 180, 190))
    text(d, (x + 12, y + 10), "ONE LIGHT-DAY OUT", font(SANS_B, 12),
         fill=(255, 255, 255))
    badge(d, x + w - 16, y + 14, 3)


def badge(d, x, y, n):
    """Numbered red circle badge (white number on red)."""
    r = 13
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED,
              outline=(255, 255, 255), width=2)
    text(d, (x, y), str(n), font(SANS_B, 14), fill=(255, 255, 255),
         anchor="mm")


def draw_icon(d, x, y, s, n):
    """Bold, high-contrast glyph for a small story (fix 4): thick
    strokes, few details, big enough to read at ~300px."""
    bg = {4: (30, 50, 110), 5: (200, 60, 20), 6: (30, 110, 180),
          7: (180, 140, 20), 8: (0, 120, 110), 9: (20, 30, 40),
          10: (30, 90, 160), 11: (110, 110, 60), 12: (110, 60, 140),
          13: (160, 30, 50)}[n]
    d.rounded_rectangle([x, y, x + s, y + s], radius=6, fill=bg)
    cx, cy = x + s // 2, y + s // 2
    if n == 4:  # Capitol dome: white arch + columns + base.
        d.pieslice([cx - 11, cy - 14, cx + 11, cy + 6], start=180, end=360,
                   fill=(255, 255, 255))
        for i in (-8, 0, 8):
            d.rectangle([cx + i - 2, cy - 4, cx + i + 2, cy + 10],
                        fill=(255, 255, 255))
        d.rectangle([cx - 13, cy + 10, cx + 13, cy + 14], fill=(255, 255, 255))
    elif n == 5:  # Flame burst: red-orange starburst + yellow core.
        d.polygon([(cx, cy - 16), (cx + 6, cy - 4), (cx + 16, cy - 2),
                   (cx + 7, cy + 5), (cx + 10, cy + 15), (cx, cy + 9),
                   (cx - 10, cy + 15), (cx - 7, cy + 5), (cx - 16, cy - 2),
                   (cx - 6, cy - 4)], fill=(255, 160, 40))
        d.polygon([(cx, cy - 9), (cx + 4, cy - 1), (cx + 8, cy + 6),
                   (cx, cy + 10), (cx - 8, cy + 6), (cx - 4, cy - 1)],
                  fill=(255, 230, 90))
    elif n == 6:  # Cyclone spiral: three thick white arcs.
        for r in (15, 10, 5):
            d.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=300,
                  fill=(255, 255, 255), width=3)
    elif n == 7:  # Euro coin: gold disc + dark euro sign.
        d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(255, 205, 60),
                  outline=(120, 90, 0), width=2)
        text(d, (cx, cy), "\u20ac", font(SANS_B, 22), fill=(60, 45, 0),
             anchor="mm")
    elif n == 8:  # Southern Cross: four bold white stars.
        for sx, sy in ((cx - 10, cy - 8), (cx + 9, cy - 10), (cx - 4, cy + 2),
                       (cx + 8, cy + 9)):
            d.polygon([(sx, sy - 5), (sx + 2, sy - 2), (sx + 5, sy),
                       (sx + 2, sy + 2), (sx, sy + 5), (sx - 2, sy + 2),
                       (sx - 5, sy), (sx - 2, sy - 2)],
                      fill=(255, 255, 255))
    elif n == 9:  # Chip: green square + pins on four sides.
        d.rectangle([cx - 11, cy - 11, cx + 11, cy + 11], fill=(40, 180, 90),
                    outline=(255, 255, 255), width=2)
        d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=(20, 30, 40))
        for i in (-7, 0, 7):
            d.line([cx + i, cy - 16, cx + i, cy - 11], fill=(255, 255, 255),
                   width=2)
            d.line([cx + i, cy + 11, cx + i, cy + 16], fill=(255, 255, 255),
                   width=2)
            d.line([cx - 16, cy + i, cx - 11, cy + i], fill=(255, 255, 255),
                   width=2)
            d.line([cx + 11, cy + i, cx + 16, cy + i], fill=(255, 255, 255),
                   width=2)
    elif n == 10:  # Tanker: dark hull + white waves.
        d.polygon([(cx - 16, cy - 2), (cx + 16, cy - 2), (cx + 12, cy + 8),
                   (cx - 12, cy + 8)], fill=(20, 30, 45))
        d.rectangle([cx - 2, cy - 10, cx + 8, cy - 2], fill=(20, 30, 45))
        for wx in (cx - 14, cx - 4, cx + 6):
            d.arc([wx - 6, cy + 8, wx + 6, cy + 16], start=180, end=360,
                  fill=(255, 255, 255), width=3)
    elif n == 11:  # Tank: body + turret + barrel + tracks.
        d.rectangle([cx - 14, cy - 2, cx + 14, cy + 8], fill=(60, 70, 40))
        d.rectangle([cx - 4, cy - 10, cx + 6, cy - 2], fill=(60, 70, 40))
        d.line([cx + 6, cy - 7, cx + 17, cy - 7], fill=(60, 70, 40), width=4)
        d.rectangle([cx - 15, cy + 8, cx + 15, cy + 13], fill=(30, 35, 20))
        for wx in (-10, -3, 4, 11):
            d.ellipse([cx + wx - 2, cy + 9, cx + wx + 2, cy + 13],
                      fill=(200, 200, 200))
    elif n == 12:  # Ballot box + red check.
        d.rectangle([cx - 11, cy - 2, cx + 11, cy + 13], fill=(255, 255, 255))
        d.rectangle([cx - 5, cy - 6, cx + 5, cy - 2], fill=(255, 255, 255))
        d.line([cx - 8, cy + 4, cx - 2, cy + 10, cx + 11, cy - 7],
               fill=(220, 40, 40), width=4)
    else:  # 13: gold crown.
        d.polygon([(cx - 13, cy + 10), (cx - 13, cy - 4), (cx - 6, cy + 3),
                   (cx, cy - 10), (cx + 6, cy + 3), (cx + 13, cy - 4),
                   (cx + 13, cy + 10)], fill=(255, 205, 60),
                  outline=(140, 100, 0), width=2)
        for tx in (-13, 0, 13):
            d.ellipse([cx + tx - 2, cy - 7, cx + tx + 2, cy - 3],
                      fill=(255, 230, 120))


def lonlat_to_xy(lon, lat, x, y, w, h):
    px = x + (lon + 170) / 360 * w
    py = y + (85 - lat) / 145 * h
    return px, py


def draw_map(d, x, y, w, h):
    """World map with big numbered pins (fix 3): pin radius 12,
    white ring width 3, bold numbers, strong continent outlines."""
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=RULE, width=1)
    # Faint graticule.
    for lon in range(-150, 181, 30):
        gx, _ = lonlat_to_xy(lon, 0, x, y, w, h)
        d.line([gx, y, gx, y + h], fill=(200, 212, 216), width=1)
    for lat in range(-60, 86, 30):
        _, gy = lonlat_to_xy(0, lat, x, y, w, h)
        d.line([x, gy, x + w, gy], fill=(200, 212, 216), width=1)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, x, y, w, h) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
        d.line(pts + [pts[0]], fill=LAND_EDGE, width=2)
    # Big pins for the 13 illustrated stories.
    for num, _reg, _h, _s, lon, lat in BIG + SMALL:
        px, py = lonlat_to_xy(lon, lat, x, y, w, h)
        r = 12
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=3)
        text(d, (px, py), str(num), font(SANS_B, 14), fill=(255, 255, 255),
             anchor="mm")


def draw_masthead(d):
    text(d, (W // 2, 8), "THE WORLD IN ONE DAY", font(SERIF_B, 50),
         fill=INK, anchor="ma")
    d.line([24, 66, W - 24, 66], fill=RULE, width=2)
    d.line([24, 69, W - 24, 69], fill=RULE, width=1)
    text(d, (24, 76), "THURSDAY, 19 NOVEMBER 2026", font(SANS_B, 18), fill=INK)
    text(d, (W - 24, 78), "45 STORIES \u00b7 6 CONTINENTS \u00b7 ONE DAY",
         font(SANS_B, 13), fill=RED, anchor="ra")
    d.line([24, 98, W - 24, 98], fill=RULE, width=2)


def draw_hero_panel(d, story, x, y, w, h, pic_fn):
    num, region, headline, summary, _lon, _lat = story
    d.rectangle([x, y, x + w, y + h], outline=RULE, width=1)
    pic_fn(d, x + 1, y + 1, w - 2, 128)
    d.line([x, y + 129, x + w, y + 129], fill=RULE, width=1)
    text(d, (x + 10, y + 136), region, font(SANS_B, 11), fill=RED)
    lines = wrap(d, headline, font(SERIF_B, 16), w - 20)[:2]
    for i, ln in enumerate(lines):
        text(d, (x + 10, y + 150 + i * 19), ln, font(SERIF_B, 16), fill=INK)
    slines = wrap(d, summary, font(SANS, 11), w - 20)[:2]
    for i, ln in enumerate(slines):
        text(d, (x + 10, y + 188 + i * 13), ln, font(SANS, 11), fill=MUTED)


def draw_small(d, story, x, y, w):
    num, _region, headline, summary, _lon, _lat = story
    draw_icon(d, x, y, 40, num)
    text(d, (x + 48, y + 1), headline, font(SERIF_B, 13), fill=INK)
    lines = wrap(d, summary, font(SANS, 10), w - 48)[:2]
    for i, ln in enumerate(lines):
        text(d, (x + 48, y + 18 + i * 12), ln, font(SANS, 10), fill=MUTED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    # Hero row.
    pics = [draw_hero1, draw_hero2, draw_hero3]
    for i, story in enumerate(BIG):
        draw_hero_panel(d, story, 24 + i * 330, 106, 322, 212, pics[i])
    d.line([24, 326, W - 24, 326], fill=RULE, width=1)
    # Small stories: 2 columns x 5 rows.
    for i, story in enumerate(SMALL):
        col, row = i % 2, i // 2
        draw_small(d, story, 24 + col * 504, 334 + row * 47, 472)
    d.line([24, 576, W - 24, 576], fill=RULE, width=1)
    # Map section.
    text(d, (24, 582), "WHERE IT HAPPENED \u2014 13 STORIES PINNED",
         font(SANS_B, 15), fill=INK)
    text(d, (W - 24, 584), "NUMBERED 1\u201313", font(SANS_B, 12),
         fill=MUTED, anchor="ra")
    draw_map(d, 24, 602, 976, 200)
    d.line([24, 810, W - 24, 810], fill=RULE, width=1)
    # Briefs 14-45: 2 columns x 16 rows.
    text(d, (24, 816), "ALSO ON 19 NOVEMBER", font(SANS_B, 13), fill=RED)
    for i, item in enumerate(ALSO):
        col, row = i % 2, i // 2
        bx, by = 24 + col * 500, 836 + row * 10
        text(d, (bx, by), str(14 + i) + ".", font(SANS_B, 9), fill=RED)
        text(d, (bx + 22, by), item, font(SANS, 9), fill=INK)
    d.line([24, 1000, W - 24, 1000], fill=RULE, width=1)
    text(d, (W // 2, 1006),
         "Sources: Associated Press, Reuters, Financial Times, Bloomberg "
         "\u2014 19 November 2026",
         font(SANS, 10), fill=MUTED, anchor="ma")
    img.save(OUT)


if __name__ == "__main__":
    main()
