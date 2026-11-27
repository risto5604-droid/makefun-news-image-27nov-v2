#!/usr/bin/env python3
"""Render Friday 27 November 2026's world news as one 1024x1024 image.

Pure stdlib + Pillow, no network. Deterministic: fixed fonts from the
repo's own fonts/ folder, no timestamps, no randomness.
Writes to /output/entry.png by default, or $OUT when set.
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
FONTS = BASE / "fonts"

W, H = 1024, 1024

# --- palette (restrained: paper, ink, one red accent, slate neutrals) ---
PAPER = (248, 245, 238)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
ACCENT = (185, 28, 28)
SLATE = (71, 85, 105)
LIGHT_LINE = (216, 210, 196)
CARD_BG = (255, 255, 255)
MAP_BG = (233, 238, 243)
LAND = (157, 176, 140)
LAND_EDGE = (110, 130, 100)
SEA_LINE = (201, 212, 222)
MUTED = (100, 100, 96)

# --- data -----------------------------------------------------------------
HEROES = [
    {
        "tag": "MIDDLE EAST",
        "headline": "Iran drone attack kills two Italians in Kuwait",
        "deck": "Rheinmetall Italia technicians hit at an air-defence "
                "surveillance station; Italy and Kuwait blame Iran; "
                "Tehran denies involvement.",
        "icon": "drone",
        "pin": "Kuwait",
        "lat": 29.3,
        "lon": 47.9,
    },
    {
        "tag": "EUROPE",
        "headline": "Russia hits two grain ships off Odesa",
        "deck": "Two foreign bulk carriers carrying 100,000+ tonnes of "
                "grain attacked overnight near Odesa; Zelenskyy warns "
                "Russia is preparing a new mass strike.",
        "icon": "ship",
        "pin": "Odesa",
        "lat": 46.5,
        "lon": 30.7,
    },
    {
        "tag": "N. AMERICA",
        "headline": "Black Friday: cautious shoppers brace for inflation",
        "deck": "US holiday sales seen topping $1 trillion (NRF +4.2% "
                "YoY) despite price strain; 82% of consumers managing "
                "holiday costs.",
        "icon": "bag",
        "pin": "New York",
        "lat": 40.7,
        "lon": -74.0,
    },
    {
        "tag": "S. ASIA",
        "headline": "Karachi building collapse kills 4, 17 missing",
        "deck": "Six-storey under-construction building in Baloch Colony "
                "collapsed Wed 25 Nov; 14 injured; building approved for "
                "3 floors, built to 7; SBCA chief removed, 16 officials "
                "suspended.",
        "icon": "building",
        "pin": "Karachi",
        "lat": 24.9,
        "lon": 67.0,
    },
    {
        "tag": "EUROPE",
        "headline": "Serbia sets presidential vote for 27 December",
        "deck": "Parliament Speaker Aleksandar Cupic called the early "
                "election after Vucic resigned in September and the "
                "student-led Student List won the 25 Oct parliamentary "
                "vote.",
        "icon": "ballot",
        "pin": "Belgrade",
        "lat": 44.8,
        "lon": 20.5,
    },
    {
        "tag": "E. ASIA",
        "headline": "Hong Kong marks a year since fire that killed 168",
        "deck": "First anniversary of the Wang Fuk Court fire (26 Nov "
                "2025); residents laid flowers in Tai Po; no official "
                "ceremony held.",
        "icon": "flame",
        "pin": "Hong Kong",
        "lat": 22.3,
        "lon": 114.2,
    },
]

# Region groups in display order; left column first three, right the rest.
LIST_GROUPS = [
    ("EUROPE", [
        "UK train stabber guilty on 14 counts",
        "Czech president urges NATO to down Russian missiles",
        "Lithuania detains 5 over Russian state TV links",
        "EU leaders urged to compromise on bloc budget",
        "Netanyahu says corruption trial has 'collapsed'",
        "Putin pushes broad AI rollout",
        "Russia deputy air chief held on graft charges",
        "Heathrow expansion fails climate tests",
    ]),
    ("MIDDLE EAST", [
        "Houthi hit on Saudi Jizan refinery kills 1 (Nepali worker; "
        "coalition hit launcher in Hodeidah)",
        "Brent tops $94 on Iran mine claims",
        "Iran: two tankers hit mines near Oman",
        "Iraq jails 8 French IS militants for life",
        "UN body backs Palestinian recovery plan",
        "Israeli drone strike kills 3 in Gaza City",
    ]),
    ("N. AMERICA", [
        "Trump: Putin must end aggression",
        "US hails Syria Captagon seizures",
        "US markets shut for Thanksgiving",
    ]),
    ("S. AMERICA", [
        "Brazil mid-Nov inflation eases to 4.64%",
        "Brazil condemns Trump tariff proposals",
    ]),
    ("S. ASIA", [
        "Bangladesh police gas wage protesters",
        "India rupee bulls return after 18 months",
        "Myanmar rejects parts of ICJ Rohingya ruling",
    ]),
    ("E. ASIA", [
        "Bank of Korea hikes rate to 3.25%",
        "Thai refinery blast injures 7",
        "China launches Earth-observation satellites",
        "AI fakes target Taiwan polls",
    ]),
    ("AFRICA", [
        "Sudan rejects Ethiopia peace initiative",
        "Kenya court halts US-backed Ebola facility",
    ]),
    ("CULTURE", [
        "Duran Duran's Andy Taylor dies at 65",
    ]),
    ("OCEANIA", [
        "Sandpapergate forum won't assign blame",
    ]),
]

# Simplified continent outlines (lon, lat), invented for this graphic.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-117, 32), (-125, 40), (-124, 48), (-140, 60),
     (-165, 60)],
    # South America
    [(-80, 10), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-58, -35), (-65, -41), (-70, -52), (-73, -37), (-70, -20),
     (-77, -12), (-80, -3)],
    # Europe
    [(-10, 36), (-9, 43), (0, 48), (-2, 50), (5, 53), (8, 57), (18, 56),
     (21, 55), (28, 60), (30, 70), (40, 68), (45, 60), (40, 50),
     (30, 46), (28, 41), (23, 40), (19, 42), (12, 44), (8, 44), (3, 43),
     (-2, 37)],
    # Africa
    [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12),
     (51, 11), (48, 0), (40, -10), (35, -18), (32, -26), (26, -34),
     (19, -35), (15, -27), (12, -18), (9, -1), (9, 4), (-8, 5),
     (-13, 8), (-17, 15), (-16, 25), (-10, 31)],
    # Asia
    [(40, 68), (60, 69), (75, 73), (90, 75), (110, 77), (130, 72),
     (160, 70), (178, 66), (170, 60), (162, 56), (158, 50), (142, 45),
     (140, 40), (135, 35), (127, 33), (122, 30), (120, 25), (110, 20),
     (105, 10), (100, 8), (97, 16), (92, 22), (88, 22), (80, 15),
     (76, 8), (72, 20), (66, 25), (60, 25), (55, 27), (50, 29),
     (48, 30), (43, 38), (40, 42), (38, 46), (30, 46), (28, 41),
     (30, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (124, -33), (129, -32),
     (137, -35), (140, -38), (147, -39), (150, -37), (153, -27),
     (146, -19), (142, -11), (136, -12), (132, -12), (126, -14),
     (122, -17), (118, -20)],
]

# --- fonts ----------------------------------------------------------------
def load_font(name, size):
    path = FONTS / name
    try:
        return ImageFont.truetype(str(path), size)
    except (OSError, IOError):
        return ImageFont.load_default()


def fonts():
    return {
        "title": load_font("DejaVuSerif-Bold.ttf", 34),
        "subtitle": load_font("DejaVuSans.ttf", 13),
        "tag": load_font("DejaVuSans-Bold.ttf", 11),
        "headline": load_font("DejaVuSans-Bold.ttf", 15),
        "deck": load_font("DejaVuSans.ttf", 11),
        "map_label": load_font("DejaVuSans-Bold.ttf", 10),
        "pin": load_font("DejaVuSans-Bold.ttf", 10),
        "section": load_font("DejaVuSans-Bold.ttf", 15),
        "region": load_font("DejaVuSans-Bold.ttf", 11),
        "item": load_font("DejaVuSans.ttf", 11),
        "footer": load_font("DejaVuSans.ttf", 11),
    }


# --- text helpers -----------------------------------------------------------
def text_w(font, text):
    return font.getbbox(text)[2]


def wrap_text(font, text, max_width):
    """Greedy word wrap; every returned line fits max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if text_w(font, trial) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def fit_lines(font, text, max_width, max_lines):
    """Wrap text and clip to max_lines with an ellipsis if needed."""
    lines = wrap_text(font, text, max_width)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    last = lines[-1]
    while last and text_w(font, last + "...") > max_width:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    lines[-1] = last + "..."
    return lines


def draw_lines(draw, lines, x, y, font, fill, leading):
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=font, fill=fill)
    return y + len(lines) * leading


# --- pictograms (simple geometric drawings, one per hero story) ------------
def draw_drone(d, x0, y0, x1, y1):
    # Diagonal missile/drone body with fins and a small flame.
    d.polygon([(x0 + 8, y1 - 8), (x1 - 12, y0 + 8), (x1 - 8, y0 + 12),
               (x0 + 12, y1 - 12)], fill=SLATE)
    d.polygon([(x1 - 12, y0 + 8), (x1 - 2, y0 + 2), (x1 - 2, y0 + 12)],
              fill=ACCENT)
    d.polygon([(x0 + 8, y1 - 8), (x0 + 2, y1 - 2), (x0 + 12, y1 - 14)],
              fill=SLATE)
    d.polygon([(x0 + 14, y1 - 6), (x0 + 6, y1 - 14), (x0 + 16, y1 - 16)],
              fill=SLATE)
    d.polygon([(x0 + 6, y1 - 6), (x0 + 1, y1 - 1), (x0 + 10, y1 - 1)],
              fill=(217, 119, 6))
    d.line([(x0 + 2, y0 + 10), (x0 + 10, y0 + 4)], fill=MUTED, width=2)
    d.line([(x0 + 2, y0 + 18), (x0 + 12, y0 + 10)], fill=MUTED, width=2)


def draw_ship(d, x0, y0, x1, y1):
    d.polygon([(x0 + 3, y0 + 24), (x1 - 3, y0 + 24), (x1 - 8, y0 + 33),
               (x0 + 8, y0 + 33)], fill=SLATE)
    d.rectangle([x0 + 12, y0 + 14, x0 + 26, y0 + 24], fill=INK)
    d.rectangle([x0 + 16, y0 + 7, x0 + 21, y0 + 14], fill=ACCENT)
    d.line([(x0 + 4, y0 + 37), (x1 - 4, y0 + 37)], fill=(96, 165, 250),
           width=2)
    d.line([(x0 + 9, y0 + 30), (x0 + 14, y0 + 30)], fill=PAPER, width=2)
    d.line([(x0 + 24, y0 + 30), (x0 + 29, y0 + 30)], fill=PAPER, width=2)


def draw_bag(d, x0, y0, x1, y1):
    d.rectangle([x0 + 6, y0 + 13, x1 - 6, y1 - 3], fill=ACCENT)
    d.arc([x0 + 12, y0 + 3, x1 - 12, y0 + 19], 180, 360, fill=INK, width=3)
    d.rectangle([x0 + 16, y0 + 20, x1 - 16, y0 + 23], fill=PAPER)
    d.line([(x0 + 13, y0 + 13), (x0 + 13, y0 + 17)], fill=INK, width=2)
    d.line([(x1 - 13, y0 + 13), (x1 - 13, y0 + 17)], fill=INK, width=2)


def draw_building(d, x0, y0, x1, y1):
    d.rectangle([x0 + 9, y0 + 3, x0 + 24, y1 - 3], fill=SLATE)
    d.rectangle([x0 + 24, y0 + 14, x1 - 6, y1 - 3], fill=(148, 163, 184))
    for wy in (8, 16, 24):
        d.rectangle([x0 + 13, y0 + wy, x0 + 19, y0 + wy + 4], fill=PAPER)
    for wy in (19, 27):
        d.rectangle([x0 + 27, y0 + wy, x1 - 9, y0 + wy + 4], fill=PAPER)
    d.line([(x0 + 24, y0 + 14), (x0 + 18, y0 + 22), (x0 + 24, y0 + 28)],
           fill=ACCENT, width=2)
    d.rectangle([x0 + 14, y1 - 10, x0 + 19, y1 - 3], fill=INK)


def draw_ballot(d, x0, y0, x1, y1):
    d.polygon([(x0 + 10, y0 + 4), (x0 + 24, y0 + 2), (x0 + 28, y0 + 12),
               (x0 + 14, y0 + 14)], fill=PAPER, outline=INK)
    d.line([(x0 + 15, y0 + 7), (x0 + 20, y0 + 11)], fill=ACCENT, width=2)
    d.rectangle([x0 + 6, y0 + 15, x1 - 6, y1 - 3], fill=SLATE)
    d.rectangle([x0 + 13, y0 + 18, x1 - 13, y0 + 21], fill=INK)
    d.rectangle([x0 + 16, y0 + 26, x0 + 22, y0 + 32], fill=PAPER)


def draw_flame(d, x0, y0, x1, y1):
    cx = (x0 + x1) // 2
    d.polygon([(cx, y0 + 2), (x1 - 6, y0 + 18), (x1 - 10, y0 + 30),
               (x0 + 10, y0 + 30), (x0 + 6, y0 + 18)], fill=(234, 88, 12))
    d.polygon([(cx, y0 + 14), (x1 - 10, y0 + 24), (x0 + 14, y0 + 32),
               (x0 + 10, y0 + 24)], fill=(250, 204, 21))
    d.polygon([(cx, y0 + 22), (x1 - 12, y0 + 30), (x0 + 12, y0 + 30)],
              fill=(185, 28, 28))


ICONS = {
    "drone": draw_drone,
    "ship": draw_ship,
    "bag": draw_bag,
    "building": draw_building,
    "ballot": draw_ballot,
    "flame": draw_flame,
}


# --- sections ---------------------------------------------------------------
def draw_banner(d, f):
    d.rectangle([0, 0, W, 76], fill=NAVY)
    title = "THE WORLD IN ONE IMAGE"
    d.text(((W - text_w(f["title"], title)) // 2, 10), title,
           font=f["title"], fill=(255, 255, 255))
    sub = "Friday, 27 November 2026 \u2014 the day\u2019s world news"
    d.text(((W - text_w(f["subtitle"], sub)) // 2, 52), sub,
           font=f["subtitle"], fill=(203, 213, 225))
    d.rectangle([0, 76, W, 80], fill=ACCENT)


def draw_heroes(d, f):
    card_w, card_h, gap = 312, 150, 12
    y0 = 92
    for i, hero in enumerate(HEROES):
        col, row = i % 3, i // 3
        x = 24 + col * (card_w + gap)
        y = y0 + row * (card_h + 10)
        d.rectangle([x, y, x + card_w, y + card_h], fill=CARD_BG,
                    outline=LIGHT_LINE, width=1)
        d.rectangle([x, y, x + card_w, y + 4], fill=ACCENT)
        d.text((x + 12, y + 12), hero["tag"], font=f["tag"], fill=ACCENT)
        ICONS[hero["icon"]](d, x + card_w - 52, y + 10,
                            x + card_w - 12, y + 50)
        inner_w = card_w - 24
        # Headline starts below the tag/icon row so the pictogram can
        # never cover headline text.
        hl = fit_lines(f["headline"], hero["headline"], inner_w, 2)
        hy = y + 54
        draw_lines(d, hl, x + 12, hy, f["headline"], INK, 18)
        deck = fit_lines(f["deck"], hero["deck"], inner_w, 4)
        deck_top = hy + len(hl) * 18 + 4
        deck_bottom = draw_lines(d, deck, x + 12, deck_top,
                                 f["deck"], SLATE, 13)
        # Layout guard: deck text must end inside its card, and no
        # headline or deck may have been silently clipped with "...".
        assert deck_bottom <= y + card_h - 4, (
            "deck overflows card for: " + hero["headline"])
        assert "..." not in " ".join(hl), (
            "headline truncated for: " + hero["headline"])
        assert "..." not in " ".join(deck), (
            "deck truncated for: " + hero["headline"])


def project(lon, lat, mx0, my0, mx1, my1):
    x = mx0 + (lon + 180.0) / 360.0 * (mx1 - mx0)
    y = my0 + (85.0 - lat) / 145.0 * (my1 - my0)
    return (x, y)


def draw_map(d, f):
    d.rectangle([24, 412, 1000, 548], fill=MAP_BG, outline=SEA_LINE,
                width=1)
    d.text((36, 419), "WHERE IT HAPPENED", font=f["map_label"], fill=SLATE)
    mx0, my0, mx1, my1 = 30, 436, 994, 542
    for lon in (-120, -60, 0, 60, 120):
        x, _ = project(lon, 85, mx0, my0, mx1, my1)
        d.line([(x, my0), (x, my1)], fill=SEA_LINE, width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx0, my0, mx1, my1) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    for i, hero in enumerate(HEROES, start=1):
        px, py = project(hero["lon"], hero["lat"], mx0, my0, mx1, my1)
        r = 10
        d.ellipse([px - r - 2, py - r - 2, px + r + 2, py + r + 2],
                  fill=(255, 255, 255))
        d.ellipse([px - r, py - r, px + r, py + r], fill=ACCENT,
                  outline=(255, 255, 255), width=1)
        num = str(i)
        d.text((px - text_w(f["pin"], num) / 2, py - 7), num,
               font=f["pin"], fill=(255, 255, 255))


def draw_list(d, f):
    d.text((24, 560), "MORE FROM 27 NOVEMBER", font=f["section"], fill=INK)
    d.rectangle([24, 584, 1000, 586], fill=ACCENT)
    left_groups = LIST_GROUPS[:3]
    right_groups = LIST_GROUPS[3:]
    bottom = 0
    for col_x, groups in ((24, left_groups), (524, right_groups)):
        y = 596
        for region, items in groups:
            d.text((col_x, y), region, font=f["region"], fill=ACCENT)
            y += 18
            for item in items:
                lines = wrap_text(f["item"], "\u2022  " + item, 476)
                y = draw_lines(d, lines, col_x, y, f["item"], INK, 14)
                y += 3
            y += 6
        bottom = max(bottom, y)
    return bottom


def draw_footer(d, f):
    d.rectangle([0, 992, W, H], fill=NAVY)
    line = ("Sources: Reuters  \u00b7  CNN  \u00b7  The Wall Street Journal  "
            "\u00b7  NRF   \u2014   27 November 2026")
    d.text(((W - text_w(f["footer"], line)) // 2, 1004), line,
           font=f["footer"], fill=(203, 213, 225))


def render():
    # Content guards: exactly six heroes and exactly thirty list items.
    assert len(HEROES) == 6, "expected 6 hero stories"
    total_items = sum(len(items) for _, items in LIST_GROUPS)
    assert total_items == 30, "expected 30 list items, got %d" % total_items
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    f = fonts()
    draw_banner(d, f)
    draw_heroes(d, f)
    draw_map(d, f)
    list_bottom = draw_list(d, f)
    # Layout guard: the list must end above the footer band (y=992).
    assert list_bottom <= 984, "list overflows into footer: %d" % list_bottom
    draw_footer(d, f)
    return img


def main():
    out = os.environ.get("OUT") or "/output/entry.png"
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    img = render()
    img.save(str(path), format="PNG")
    print("wrote", path, img.size)


if __name__ == "__main__":
    main()
