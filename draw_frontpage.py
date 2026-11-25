#!/usr/bin/env python3
"""Draw the 25 November 2026 front page (news-image-20261125 v3b).

One 1024x1024 newspaper front page, drawn from scratch with Pillow:
masthead, stats strip, news ticker, a three-story lead, ten more
illustrated heroes, a region bar, a numbered world map, 23 more stories,
and a DATE CHECK box that names the earlier-day stories left out on
purpose. Every story is genuinely dated 25 November 2026 (UTC); every
story carries its source code. Deterministic: no randomness, no network,
no clock reads — the same run always paints the same pixels.

Usage: python3 draw_frontpage.py <output-dir>   (writes entry.png there)
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (24, 24, 22)
SOFT_INK = (74, 70, 64)
RULE = (24, 24, 22)
ACCENT = (178, 34, 34)
BLUE = (31, 78, 121)
SEA = (214, 231, 238)
LAND = (227, 217, 189)
LAND_EDGE = (168, 152, 120)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    """Greedy word wrap by pixel width; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


BADGE_FILL = {
    "REPORTED": (31, 78, 121),
    "CLAIM": (176, 124, 18),
    "CONFIRMED": (46, 125, 50),
    "ONGOING": (106, 62, 150),
}


def badge(draw, x, y, word):
    fnt = font(SANS_B, 10)
    tw = draw.textlength(word, font=fnt)
    fill = BADGE_FILL[word]
    draw.rounded_rectangle([x, y, x + tw + 12, y + 16], 3, fill=fill)
    draw.text((x + 6, y + 3), word, font=fnt, fill=(255, 255, 255))
    return tw + 12


# (n, region, utc, headline, deck, badge, source, lon, lat, scene key)
HEROES = [
    (1, "North America", "09:00", "US proposes tariffs of 20–40% on 14 partners",
     "USTR Jamieson Greer names 14 economies, citing unfair trade; rates capped 10–20% under deals.",
     "REPORTED", "R", -77.0, 39.0, "tariffs"),
    (2, "Middle East", "03:10", "Iran: two tankers hit mines in Hormuz, on fire",
     "IRGC: vessels used an unauthorised route. Claim unverified.",
     "CLAIM", "R", 56.5, 26.5, "tanker"),
    (3, "Middle East", "06:40", "Houthis say they hit Ras Tanura refinery",
     "Houthis claim fires; coalition says it downed four drones.",
     "CLAIM", "R", 50.2, 26.6, "refinery"),
    (4, "Asia-Pacific", "09:56", "Shenzhou-24 docks; Pakistan's first astronaut",
     "Muhammad Zeeshan Ali reaches Tiangong with two Chinese crew, 3.5 hours after launch.",
     "CONFIRMED", "R", 100.3, 40.0, "rocket"),
    (5, "Global", "08:30", "AI sell-off deepens: KOSPI −6.2%, Nikkei −2.8%",
     "Samsung −9.9%, SK Hynix −11.1%, SoftBank −14.8%; Nasdaq futures down 2.8% pre-bell.",
     "REPORTED", "B", 127.0, 37.5, "chart"),
    (6, "North America", "07:15", "Dell: record $54.9bn sales, shares fall 6%",
     "AI server revenue $22.0bn, up 291%; a record $132.3bn AI backlog — still sold off.",
     "REPORTED", "B", -97.7, 30.3, "servers"),
    (7, "Europe", "04:50", "Ukraine drones set two Rosneft refineries ablaze",
     "Syzran and Kuibyshev hit overnight in Samara; one killed, 145 drones downed.",
     "REPORTED", "R", 50.0, 53.0, "strike"),
    (8, "Latin America", "05:25", "Colombia frees all Cartagena hostages",
     "Security forces storm an Éxito supermarket; every hostage freed, one captor killed.",
     "CONFIRMED", "R", -75.5, 10.4, "rescue"),
    (9, "Africa", "11:20", "RSF drone strikes kill 19 civilians in Sudan",
     "Emergency Lawyers: 19 dead, 20 wounded in two Blue Nile cities on Tuesday.",
     "REPORTED", "R", 34.0, 11.0, "desert"),
    (10, "Oceania", "10:05", "Solomons–Australia sign no-foreign-base treaty",
     "Canberra pact precludes any foreign military or security base on the islands.",
     "CONFIRMED", "AP", 160.0, -9.0, "islands"),
    (11, "Europe", "12:40", "EU Parliament votes to loosen nature laws",
     "367 to 268: the EPP sides with the right to review Birds and Habitats rules.",
     "REPORTED", "EU", 4.4, 50.8, "parliament"),
    (12, "Europe", "13:10", "EU unveils €50bn quantum and tech fund",
     "A Quantum Act plus a Sovereign Tech Equity Fund to keep strategic tech European.",
     "REPORTED", "EU", 7.0, 52.0, "quantum"),
    (13, "Asia-Pacific", "08:00", "Bogor mine toll reaches 6; 20 still trapped",
     "Three more bodies recovered from a flooded unauthorised gold mine in West Java.",
     "REPORTED", "AP", 106.8, -6.6, "mine"),
]

# (n, region, utc, headline, source)
ALSO_ON = [
    (14, "Middle East", "03:40", "Israel kills Hamas colonel Abuelouf in Gaza strike", "R"),
    (15, "Europe", "04:15", "Russian strike kills 2 in Odesa; Kyiv flat ablaze", "R"),
    (16, "Europe", "05:20", "Putin vows retaliation over refinery strikes (claim)", "R"),
    (17, "Middle East", "06:05", "US tells citizens to leave Iran immediately", "AP"),
    (18, "Europe", "07:30", "Zelenskyy: Ukraine needs €115bn aid for 2027", "R"),
    (19, "Europe", "08:45", "Eurozone inflation rises to 4.0% in November", "EU"),
    (20, "Europe", "09:10", "EU court orders timeline for cage-farming ban", "EU"),
    (21, "Europe", "09:50", "UK fines fragrance giants £85m for collusion", "N"),
    (22, "Europe", "10:25", "Puigdemont to return to Spain on 12 December", "AP"),
    (23, "Europe", "11:00", "Ofgem lifts energy price cap 26% from January", "N"),
    (24, "Europe", "11:40", "Germany's Q3 growth revised down to 0.1%", "N"),
    (25, "Asia-Pacific", "12:15", "China probes Shanghai party chief Chen Jining", "R"),
    (26, "Asia-Pacific", "12:50", "India opens missile range to Japan, a first", "R"),
    (27, "Asia-Pacific", "13:20", "Asia Power Index: India 3rd; Modi 2nd-best leader", "N"),
    (28, "North America", "13:55", "WHO: three US bird-flu cases, one death in Washington", "AP"),
    (29, "North America", "14:30", "Abrego Garcia leaves US for Spain after 20-month fight", "R"),
    (30, "North America", "15:05", "US Army destroys lead-azide stockpile in Iowa", "AP"),
    (31, "North America", "15:40", "Trump to award Giuliani the Medal of Freedom", "AP"),
    (32, "Latin America", "16:10", "Brazil police freeze $340m in illegal ore probe", "N"),
    (33, "Latin America", "16:45", "Paraná storms kill 6 and hit 10,000 people", "N"),
    (34, "Latin America", "17:20", "Argentina enters technical recession", "N"),
    (35, "Africa", "18:00", "Sports court restores Senegal's AFCON title", "AP"),
    (36, "Oceania", "18:35", "Australia inflation rises to 4.9%", "N"),
]

LEFT_OUT = [
    "Nvidia's Huang reinstated, shares +31% (23 Nov)",
    "Benghazi sea-drone attack on a Russian corvette (23 Nov)",
    "Hormuz 3-tanker claim (23 Nov)",
    "Riyadh tower drone, 11 hurt (24 Nov)",
    "Huawei guilty verdict (24 Nov)",
    "Dow closes above 50,000 (24 Nov)",
    "India beat China 6–2, hockey (24 Nov)",
]

TICKER = ("COP31 ENDS WITH NO FOSSIL-FUEL DEAL  •  POPE LEO WARNS ON CLIMATE  •  "
          "ANTHROPIC BELOW IPO PRICE  •  AMAZON BUYS DECART  •  ROCHE WINS FDA NOD")

REGIONS = [("North America", 6), ("Europe", 12), ("Middle East", 4),
           ("Asia-Pacific", 5), ("Africa", 2), ("Latin America", 4),
           ("Oceania", 2), ("Global", 1)]

# Simplified continent outlines, as (lon, lat) points — my own rough
# sketch of the world, good enough to place numbered pins on.
CONTINENTS = [
    [(-168, 65), (-150, 70), (-130, 71), (-115, 68), (-100, 68), (-90, 66),
     (-82, 62), (-76, 62), (-70, 58), (-65, 60), (-60, 55), (-55, 52),
     (-60, 47), (-70, 44), (-75, 40), (-80, 32), (-81, 26), (-85, 20),
     (-90, 15), (-95, 16), (-100, 20), (-105, 23), (-110, 28), (-115, 32),
     (-120, 38), (-125, 48), (-130, 58), (-145, 60), (-160, 58), (-168, 65)],
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-25, 70), (-35, 74),
     (-50, 74), (-58, 70), (-55, 60)],
    [(-80, 10), (-75, 12), (-70, 11), (-62, 10), (-55, 6), (-50, 0),
     (-44, -3), (-38, -5), (-35, -8), (-40, -15), (-48, -22), (-55, -30),
     (-62, -38), (-68, -45), (-70, -52), (-72, -50), (-73, -40), (-72, -30),
     (-70, -20), (-75, -15), (-80, -8), (-81, -2), (-80, 5), (-80, 10)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 52), (8, 55), (10, 58),
     (12, 56), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (28, 65),
     (25, 68), (20, 70), (15, 70), (12, 68), (8, 62), (5, 58), (0, 55),
     (-5, 50), (-9, 43), (-10, 36)],
    [(-6, 35), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28), (38, 22),
     (43, 12), (48, 11), (51, 10), (46, 5), (42, 0), (40, -8), (36, -18),
     (32, -26), (28, -33), (20, -35), (15, -30), (12, -18), (12, -8),
     (9, 4), (4, 6), (-2, 5), (-8, 4), (-12, 8), (-16, 12), (-17, 15),
     (-16, 20), (-15, 25), (-10, 30), (-6, 35)],
    [(30, 62), (40, 68), (50, 70), (60, 70), (70, 72), (80, 73), (90, 75),
     (100, 76), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 66), (170, 66), (178, 65), (170, 60), (162, 60), (158, 55),
     (150, 60), (142, 55), (140, 45), (135, 42), (130, 38), (127, 35),
     (122, 32), (120, 28), (115, 22), (110, 20), (105, 15), (100, 10),
     (98, 8), (95, 12), (92, 16), (90, 22), (88, 22), (85, 20), (80, 15),
     (77, 8), (75, 12), (72, 20), (68, 23), (65, 25), (60, 25), (57, 26),
     (54, 26), (52, 28), (50, 30), (48, 30), (45, 28), (42, 25), (40, 22),
     (38, 20), (35, 28), (33, 30), (30, 36), (28, 40), (26, 40), (23, 36),
     (26, 38), (30, 42), (30, 45), (30, 50), (28, 55), (30, 62)],
    [(113, -22), (114, -30), (115, -35), (120, -35), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (140, -12), (136, -12), (132, -12),
     (128, -14), (124, -15), (120, -18), (115, -20), (113, -22)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-3, 50), (-5, 50)],
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 37), (141, 40),
     (142, 43), (144, 44), (142, 42), (140, 39), (138, 36), (135, 33),
     (132, 32), (130, 31)],
    [(95, 5), (100, 0), (104, -3), (106, -6), (104, -5), (100, 0), (95, 5)],
    [(109, 1), (113, 4), (117, 2), (118, -2), (116, -4), (112, -3), (109, 1)],
    [(131, -1), (136, -2), (141, -3), (141, -6), (136, -7), (131, -4), (131, -1)],
    [(167, -45), (170, -42), (174, -39), (177, -38), (175, -41), (172, -43),
     (168, -46), (167, -45)],
]


def scene(draw, key, x, y, w, h):
    """One small original drawn scene per hero story, Pillow primitives."""
    bgs = {"tariffs": (41, 84, 128), "tanker": (30, 68, 96), "refinery": (122, 62, 28),
           "rocket": (18, 24, 54), "chart": (128, 30, 30), "servers": (34, 64, 44),
           "strike": (96, 32, 28), "rescue": (28, 84, 62), "desert": (178, 132, 58),
           "islands": (24, 96, 110), "parliament": (58, 62, 120), "quantum": (52, 34, 96),
           "mine": (84, 66, 44)}
    draw.rectangle([x, y, x + w, y + h], fill=bgs[key])
    cx, cy = x + w // 2, y + h // 2
    if key == "tariffs":
        draw.rectangle([x + 8, cy + 6, x + w - 8, cy + 16], fill=(20, 40, 66))
        for i in range(3):
            draw.rectangle([x + 16 + i * 26, cy - 16, x + 36 + i * 26, cy + 6],
                           fill=(214, 112, 48) if i != 1 else (232, 196, 90))
        draw.text((x + w - 62, y + 4), "20–40%", font=font(SANS_B, 14), fill=(255, 255, 255))
    elif key == "tanker":
        draw.rectangle([x + 10, cy - 2, x + w - 10, cy + 10], fill=(30, 30, 34))
        draw.rectangle([x + w - 34, cy - 14, x + w - 22, cy - 2], fill=(30, 30, 34))
        draw.ellipse([x + 14, cy - 26, x + 30, cy - 10], fill=(40, 40, 44))
        for dx, dy in [(-6, -6), (6, -6), (-8, 0), (8, 0), (0, -8)]:
            draw.line([x + 22 + dx, cy - 18 + dy, x + 22 - dx, cy - 18 - dy],
                      fill=(255, 255, 255), width=2)
        draw.polygon([(x + w - 52, cy - 30), (x + w - 44, cy - 44), (x + w - 36, cy - 30)],
                     fill=(240, 120, 30))
    elif key == "refinery":
        for i, tw in enumerate([10, 14, 10]):
            bx = x + 14 + i * 26
            draw.rectangle([bx, cy - 22, bx + tw, cy + 12], fill=(52, 52, 56))
        draw.polygon([(x + w - 30, cy - 34), (x + w - 20, cy - 52), (x + w - 10, cy - 34)],
                     fill=(240, 140, 30))
        draw.ellipse([x + w - 26, cy - 44, x + w - 14, cy - 32], fill=(250, 200, 60))
    elif key == "rocket":
        draw.polygon([(cx, y + 4), (cx + 9, cy - 2), (cx + 6, cy + 12),
                      (cx - 6, cy + 12), (cx - 9, cy - 2)], fill=(235, 235, 235))
        draw.ellipse([cx - 4, cy + 12, cx + 4, cy + 20], fill=(240, 140, 30))
        for sx, sy in [(x + 12, y + 10), (x + w - 14, y + 16), (x + 20, y + h - 12)]:
            draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))
    elif key == "chart":
        pts = [(x + 8, y + 14), (x + w // 3, y + 22), (x + 2 * w // 3, y + 34),
               (x + w - 10, y + h - 12)]
        draw.line(pts, fill=(255, 255, 255), width=4, joint="curve")
        draw.polygon([(x + w - 22, y + h - 22), (x + w - 8, y + h - 22), (x + w - 8, y + h - 8)],
                     fill=(255, 255, 255))
        draw.text((x + 8, y + h - 22), "−6.2%", font=font(SANS_B, 14), fill=(255, 220, 220))
    elif key == "servers":
        for i in range(3):
            bx = x + 12 + i * 30
            draw.rectangle([bx, y + 8, bx + 24, y + h - 8], fill=(18, 38, 26))
            for r in range(3):
                draw.ellipse([bx + 4, y + 14 + r * 14, bx + 8, y + 18 + r * 14],
                             fill=(90, 220, 130))
        draw.text((x + w - 54, y + 4), "$132bn", font=font(SANS_B, 12), fill=(255, 255, 255))
    elif key == "strike":
        draw.polygon([(cx - 26, cy + 14), (cx - 8, cy - 6), (cx, cy - 16), (cx + 8, cy - 6),
                      (cx + 26, cy + 14), (cx + 10, cy + 8), (cx, cy + 18), (cx - 10, cy + 8)],
                     fill=(250, 190, 60))
        draw.ellipse([cx - 22, y + 6, cx + 22, y + 16], fill=(60, 60, 64))
        draw.rectangle([cx - 22, y + 10, cx + 22, y + 12], fill=(60, 60, 64))
    elif key == "rescue":
        draw.rectangle([x + 10, cy - 4, x + w - 10, cy + 16], fill=(240, 240, 235))
        draw.rectangle([x + 10, cy - 12, x + w - 10, cy - 4], fill=(28, 84, 62))
        draw.ellipse([cx - 12, cy - 26, cx + 12, cy - 2], fill=(255, 255, 255))
        draw.line([cx - 6, cy - 14, cx - 2, cy - 8, cx + 7, cy - 19], fill=(28, 84, 62), width=3)
    elif key == "desert":
        draw.ellipse([x + w - 26, y + 6, x + w - 8, y + 24], fill=(250, 210, 110))
        draw.polygon([(x, y + h), (x + w // 3, cy - 6), (x + 2 * w // 3, y + h)],
                     fill=(150, 104, 44))
        draw.polygon([(x + w // 2, y + h), (x + 5 * w // 6, cy - 2), (x + w, y + h)],
                     fill=(120, 82, 34))
        draw.ellipse([cx - 16, y + 8, cx + 16, y + 14], fill=(70, 70, 74))
    elif key == "islands":
        for ix, iy, r in [(0.25, 0.55, 16), (0.55, 0.4, 12), (0.8, 0.62, 10)]:
            draw.ellipse([x + w * ix - r, y + h * iy - r // 2, x + w * ix + r,
                          y + h * iy + r // 2], fill=(64, 176, 110))
        draw.arc([x + 8, y + 6, x + w - 8, y + h - 6], 200, 340, fill=(255, 255, 255), width=3)
    elif key == "parliament":
        for i in range(5):
            ang = 200 + i * 10
            import math
            px = cx + int(30 * math.cos(math.radians(ang)))
            py = cy + 8 + int(16 * math.sin(math.radians(ang)))
            draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 215, 90))
        draw.arc([cx - 34, cy - 18, cx + 34, cy + 22], 180, 360, fill=(255, 255, 255), width=3)
    elif key == "quantum":
        draw.rectangle([cx - 14, cy - 14, cx + 14, cy + 14], fill=(220, 220, 230))
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=(52, 34, 96))
        draw.ellipse([cx - 26, cy - 12, cx + 26, cy + 12], outline=(255, 255, 255), width=2)
        draw.ellipse([cx - 12, cy - 26, cx + 12, cy + 26], outline=(255, 215, 90), width=2)
    elif key == "mine":
        draw.polygon([(x, y + h), (x + w // 2, y + 6), (x + w, y + h)], fill=(110, 88, 58))
        draw.pieslice([cx - 16, cy - 2, cx + 16, cy + 26], 180, 360, fill=(20, 16, 12))
        draw.ellipse([cx - 3, cy + 6, cx + 3, cy + 12], fill=(250, 220, 90))


def card(draw, story, x, y, w, h, lead=False):
    n, region, utc, head, deck, bdg, src, lon, lat, key = story
    draw.rectangle([x, y, x + w, y + h], outline=(150, 142, 128), width=1)
    if lead:
        scene(draw, key, x + 1, y + 1, 200, h - 2)
        tx = x + 212
        tw = w - 224
        num = font(SERIF, 26)
        draw.text((tx, y + 6), str(n), font=num, fill=ACCENT)
        bw = badge(draw, tx + 34, y + 12, bdg)
        draw.text((tx + 34 + bw + 8, y + 12), f"{utc} UTC · {region}  [{src}]",
                  font=font(SANS_B, 10), fill=SOFT_INK)
        lines = wrap(draw, head, font(SERIF, 21), tw)
        yy = y + 38
        for ln in lines[:2]:
            draw.text((tx, yy), ln, font=font(SERIF, 21), fill=INK)
            yy += 25
        dlines = wrap(draw, deck, font(SANS, 12), tw)
        for ln in dlines[:2]:
            draw.text((tx, yy), ln, font=font(SANS, 12), fill=SOFT_INK)
            yy += 15
    else:
        scene(draw, key, x + 1, y + 1, w - 2, 58)
        draw.text((x + 6, y + 62), str(n), font=font(SERIF, 15), fill=ACCENT)
        badge(draw, x + 24, y + 63, bdg)
        lines = wrap(draw, head, font(SANS_B, 12), w - 12)
        yy = y + 82
        for ln in lines[:2]:
            draw.text((x + 6, yy), ln, font=font(SANS_B, 12), fill=INK)
            yy += 14


def small_card(draw, story, x, y, w, h):
    n, region, utc, head, deck, bdg, src, lon, lat, key = story
    draw.rectangle([x, y, x + w, y + h], outline=(150, 142, 128), width=1)
    scene(draw, key, x + 1, y + 1, 108, h - 2)
    tx = x + 116
    draw.text((tx, y + 5), str(n), font=font(SERIF, 16), fill=ACCENT)
    badge(draw, tx + 22, y + 7, bdg)
    lines = wrap(draw, head, font(SANS_B, 12), w - 124)
    yy = y + 26
    for ln in lines[:2]:
        draw.text((tx, yy), ln, font=font(SANS_B, 12), fill=INK)
        yy += 14
    dlines = wrap(draw, deck, font(SANS, 10), w - 124)
    for ln in dlines[:1]:
        draw.text((tx, yy), ln, font=font(SANS, 10), fill=SOFT_INK)


def build(out_dir):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, 7], fill=INK)

    # Masthead
    d.text((16, 16), "The World Today", font=font(SERIF, 46), fill=INK)
    d.text((16, 68), "ONE PAGE  •  EVERY STORY THAT MATTERED",
           font=font(SANS_B, 11), fill=SOFT_INK)
    right = "TUESDAY 25 NOVEMBER 2026"
    d.text((W - 16 - d.textlength(right, font=font(SERIF, 24)), 22), right,
           font=font(SERIF, 24), fill=INK)
    sub = "36 stories  •  8 regions  •  all times UTC"
    d.text((W - 16 - d.textlength(sub, font=font(SANS_B, 12)), 56), sub,
           font=font(SANS_B, 12), fill=SOFT_INK)
    d.text((W - 16 - d.textlength("No. 329 — 25 Nov 2026", font=font(SANS, 10)), 74),
           "No. 329 — 25 Nov 2026", font=font(SANS, 10), fill=SOFT_INK)
    d.line([16, 96, W - 16, 96], fill=RULE, width=2)
    d.line([16, 100, W - 16, 100], fill=RULE, width=1)

    # Stats strip
    stats = [("36", "STORIES"), ("8", "REGIONS"), ("13", "ILLUSTRATED"),
             ("23", "ALSO ON"), ("$100", "TOP 50 WIN")]
    sx = 16
    for num, label in stats:
        d.rectangle([sx, 108, sx + 190, 134], outline=(150, 142, 128), width=1)
        num_font = font(SERIF, 18)
        d.text((sx + 10, 112), num, font=num_font, fill=ACCENT)
        d.text((sx + 18 + d.textlength(num, font=num_font), 118), label,
               font=font(SANS_B, 11), fill=INK)
        sx += 198
    d.line([16, 142, W - 16, 142], fill=RULE, width=1)
    d.text((16, 146), TICKER, font=font(SANS_B, 10), fill=BLUE)
    d.line([16, 162, W - 16, 162], fill=RULE, width=1)

    # Lead row: story 1 large left, stories 2-3 stacked right
    lead = HEROES[0]
    card(d, lead, 16, 170, 496, 158, lead=True)
    small_card(d, HEROES[1], 520, 170, 488, 76)
    small_card(d, HEROES[2], 520, 252, 488, 76)

    # Heroes 4-13: five columns, two rows
    gx, gy = 16, 336
    cw, chh, gap = 192, 108, 8
    for i, story in enumerate(HEROES[3:]):
        cx = gx + (i % 5) * (cw + gap)
        cy = gy + (i // 5) * (chh + gap)
        card(d, story, cx, cy, cw, chh)

    # Region bar
    ry = 566
    d.text((16, ry), "WHERE THE NEWS CAME FROM — STORIES PER REGION",
           font=font(SANS_B, 11), fill=INK)
    bx, by = 16, 584
    for name, count in REGIONS:
        label = f"{name} {count}"
        fnt = font(SANS_B, 11)
        tw = d.textlength(label, font=fnt)
        d.rounded_rectangle([bx, by, bx + tw + 16, by + 22], 4,
                            outline=(150, 142, 128), width=1)
        d.text((bx + 8, by + 5), label, font=fnt, fill=INK)
        bx += tw + 26

    # World map with numbered pins
    my = 616
    d.text((16, my), "WHERE IT HAPPENED — PINS ARE NUMBERED TO MATCH THE STORIES",
           font=font(SANS_B, 11), fill=INK)
    mx0, my0, mx1, my1 = 16, 634, 1008, 778
    d.rectangle([mx0, my0, mx1, my1], fill=SEA, outline=(150, 142, 128), width=1)

    def proj(lon, lat):
        px = mx0 + (lon + 180.0) / 360.0 * (mx1 - mx0)
        py = my0 + (75.0 - lat) / 150.0 * (my1 - my0)
        return (px, py)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=LAND_EDGE)
    pin_font = font(SANS_B, 10)
    offsets = {12: (14, -12)}
    for story in HEROES:
        n, region, utc, head, deck, bdg, src, lon, lat, key = story
        px, py = proj(lon, lat)
        ox, oy = offsets.get(n, (0, 0))
        px, py = px + ox, py + oy
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=ACCENT,
                  outline=(255, 255, 255), width=2)
        label = str(n)
        d.text((px - d.textlength(label, font=pin_font) / 2, py - 7),
               label, font=pin_font, fill=(255, 255, 255))

    # Also on
    ay = 788
    d.text((16, ay), "ALSO ON — 23 MORE STORIES, ALL 25 NOVEMBER (UTC)",
           font=font(SANS_B, 12), fill=INK)
    d.line([16, ay + 18, W - 16, ay + 18], fill=RULE, width=1)
    row_font = font(SANS, 11)
    for i, (n, region, utc, head, src) in enumerate(ALSO_ON):
        col = i // 12
        row = i % 12
        rx = 16 + col * 500
        ry2 = ay + 26 + row * 12
        d.text((rx, ry2), f"{n:>2}", font=font(SERIF, 11), fill=ACCENT)
        d.text((rx + 24, ry2), utc, font=font(SANS_B, 10), fill=SOFT_INK)
        d.text((rx + 62, ry2), head, font=row_font, fill=INK)
        d.text((rx + 470, ry2), f"[{src}]", font=font(SANS_B, 10), fill=BLUE)

    # Date check box
    dy = 958
    d.rectangle([16, dy, W - 16, dy + 48], outline=ACCENT, width=2)
    d.text((26, dy + 5), "DATE CHECK — LEFT OUT ON PURPOSE (23–24 NOV, NOT TODAY):",
           font=font(SANS_B, 11), fill=ACCENT)
    d.text((26, dy + 21), "  •  ".join(LEFT_OUT[:4]), font=font(SANS, 10), fill=SOFT_INK)
    d.text((26, dy + 34), "  •  ".join(LEFT_OUT[4:]), font=font(SANS, 10), fill=SOFT_INK)

    # Footer
    d.text((16, 1012),
           "Sources: Reuters (R) • Associated Press (AP) • Bloomberg (B) • EU institutions (EU) • national outlets (N) — every story carries its code. Scenes are original drawings, not photographs.",
           font=font(SANS, 9), fill=SOFT_INK)

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path} {W}x{H}")
    return path


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "/output")
