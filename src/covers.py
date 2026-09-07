"""Generate Instagram highlight covers in several visual directions.

Writes covers/<Direction>/01_StartHere.png ... 06_OffCourse.png.
Canvas 1080x1920; all artwork stays inside a 640 px circle at (540, 960).

Run:  python3 src/covers.py
Then: python3 src/contact_sheet.py   # and read the 68 px row — that is the test
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path("/tmp/fonts")

W, H = 1080, 1920
CX, CY, R = 540, 960, 320            # the safe circle Instagram keeps

CREAM, GOLD, CHARCOAL = "#F5F1E8", "#B8924A", "#1A1A1A"
FOREST, BONE = "#1F382C", "#E8E2D5"

COVERS = [
    ("01_StartHere", "START HERE"),
    ("02_Drills", "DRILLS"),
    ("03_Comeback", "THE COMEBACK"),
    ("04_ProShop", "PRO SHOP"),
    ("05_Wellness", "WELLNESS"),
    ("06_OffCourse", "OFF COURSE"),
]

# ---------------------------------------------------------------- fonts

def font(name, size, weight=None):
    files = {
        "playfair": "PlayfairDisplay[wght].ttf",
        "playfair-italic": "PlayfairDisplay-Italic[wght].ttf",
        "montserrat": "Montserrat[wght].ttf",
        "dmserif": "DMSerifDisplay-Regular.ttf",
        "cormorant": "CormorantGaramond[wght].ttf",
    }
    f = ImageFont.truetype(str(FONTS / files[name]), size)
    if weight is not None:
        f.set_variation_by_axes([weight])   # variable fonts open at their thinnest
    return f

# ---------------------------------------------------------------- tracked type

def tracked_width(f, text, gap):
    return sum(f.getlength(ch) for ch in text) + gap * (len(text) - 1)


def draw_tracked(d, x, y, text, f, gap, fill):
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + gap


def wrap(label):
    words = label.split()
    if len(words) == 1:
        return None
    i = min(range(1, len(words)),
            key=lambda k: abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
    return [" ".join(words[:i]), " ".join(words[i:])]

# ---------------------------------------------------------------- fitting

def layout(lines, f, size, leading, cy):
    """Visual (cap-height) boxes for each line, centred as a block on cy."""
    cap_top, cap_bot = f.getbbox("H")[1], f.getbbox("H")[3]
    cap_h = cap_bot - cap_top
    line_h = size * leading
    block_h = line_h * (len(lines) - 1) + cap_h
    top = cy - block_h / 2
    out = []
    for i, line in enumerate(lines):
        y_vis = top + i * line_h
        out.append(dict(text=line, y_draw=y_vis - cap_top, y0=y_vis, y1=y_vis + cap_h))
    return out


def chord_halfwidth(r, y0, y1, cy=CY):
    """Half the circle's chord at the line's edge farthest from centre."""
    dy = max(abs(y0 - cy), abs(y1 - cy))
    return math.sqrt(max(r * r - dy * dy, 0))


def fit(label, fontfn, tracking, r_inner, cy=CY, leading=1.3,
        max_size=150, min_size=30, margin=18):
    """Largest size whose lines each fit the circle's chord at their own height.

    Tries one line first; falls back to two. Never hard-codes a size per word.
    """
    for size in range(max_size, min_size - 1, -2):
        f = fontfn(size)
        gap = size * tracking
        for lines in ([label], wrap(label)):
            if not lines:
                continue
            rows = layout(lines, f, size, leading, cy)
            ok = all(tracked_width(f, r["text"], gap) <= 2 * (chord_halfwidth(r_inner, r["y0"], r["y1"], cy) - margin)
                     for r in rows)
            if ok:
                return f, gap, rows
    raise ValueError(f"{label!r} does not fit inside r={r_inner}")


def place(d, rows, f, gap, fill):
    for r in rows:
        w = tracked_width(f, r["text"], gap)
        draw_tracked(d, CX - w / 2, r["y_draw"], r["text"], f, gap, fill)
    return min(r["y0"] for r in rows), max(r["y1"] for r in rows)

# ---------------------------------------------------------------- ornaments

def ring(d, r, thickness, fill):
    d.ellipse([CX - r, CY - r, CX + r, CY + r], outline=fill, width=thickness)


def rule(d, y, width, fill, thickness=2):
    d.rectangle([CX - width / 2, y, CX + width / 2, y + thickness], fill=fill)


def arched(img, text, f, radius, fill, start_deg, gap_deg, top=True):
    """Draw text glyph by glyph along an arc, each glyph rotated to the tangent.

    start_deg is the angle of the first glyph's centre, measured clockwise from
    12 o'clock. Text on the top arc reads left to right; on the bottom arc the
    glyphs are flipped so it still reads left to right.
    """
    angles = [start_deg + i * gap_deg for i in range(len(text))]
    for ch, a in zip(text, angles):
        rad = math.radians(a)
        x = CX + radius * math.sin(rad)
        y = CY - radius * math.cos(rad)
        bbox = f.getbbox(ch)
        gw, gh = bbox[2] - bbox[0] + 8, bbox[3] - bbox[1] + 8
        glyph = Image.new("RGBA", (gw * 3, gh * 3), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glyph)
        gd.text((gw * 1.5 - (bbox[0] + bbox[2]) / 2, gh * 1.5 - (bbox[1] + bbox[3]) / 2),
                ch, font=f, fill=fill)
        rot = -a if top else 180 - a
        glyph = glyph.rotate(rot, resample=Image.BICUBIC, expand=False)
        img.paste(glyph, (int(x - glyph.width / 2), int(y - glyph.height / 2)), glyph)


def arc_span(f, text, radius, gap_frac=0.35):
    """Total sweep in degrees for text drawn along a circle of `radius`."""
    step = f.size * (1 + gap_frac)
    return math.degrees(step / radius), math.degrees(step * (len(text) - 1) / radius)

# ---------------------------------------------------------------- directions

def hairline(label):
    """Serif word alone, gold hairline rules above and below. Core palette."""
    img = Image.new("RGB", (W, H), CHARCOAL); d = ImageDraw.Draw(img)
    f, gap, rows = fit(label, lambda s: font("playfair", s, 600), 0.10, R, max_size=130)
    y0, y1 = place(d, rows, f, gap, CREAM)
    rule(d, y0 - 60, 160, GOLD); rule(d, y1 + 58, 160, GOLD)
    return img


def keyline(label):
    """Charcoal serif inside a thin gold keyline ring on cream. Core palette."""
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    ring(d, 296, 3, GOLD)
    f, gap, rows = fit(label, lambda s: font("playfair", s, 800), 0.06, 270, max_size=130)
    place(d, rows, f, gap, CHARCOAL)
    return img


def disc(label):
    """Sans reversed out of a solid charcoal disc, cream halo. Core palette."""
    img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
    r = 292
    d.ellipse([CX - r, CY - r, CX + r, CY + r], fill=CHARCOAL)
    f, gap, rows = fit(label, lambda s: font("montserrat", s, 600), 0.12, r, max_size=130)
    place(d, rows, f, gap, CREAM)
    return img


def numeral(label, idx):
    """Large serif numeral in gold, small tracked label beneath. Core palette.

    Fragile by design: Instagram re-sorts highlights on every edit (CLAUDE.md).
    """
    img = Image.new("RGB", (W, H), CHARCOAL); d = ImageDraw.Draw(img)
    nf = font("playfair", 250, 400)
    num = f"{idx:02d}"
    nb = nf.getbbox(num)
    nx, ny = CX - (nb[0] + nb[2]) / 2, CY - 80 - (nb[1] + nb[3]) / 2
    d.text((nx, ny), num, font=nf, fill=GOLD)
    f, gap, rows = fit(label, lambda s: font("montserrat", s, 600), 0.16, R, cy=CY + 140, max_size=64)
    place(d, rows, f, gap, CREAM)
    return img


def crest(label):
    """Badge: double gold ring, arched name top and place bottom, serif label centre.
    Heritage palette."""
    img = Image.new("RGB", (W, H), FOREST); d = ImageDraw.Draw(img)
    ring(d, 304, 2, GOLD); ring(d, 292, 2, GOLD)
    af = font("montserrat", 23, 600)
    for text, is_top in (("EMMA TEEPLES GOLF", True), ("REDDING · CALIFORNIA", False)):
        step, sweep = arc_span(af, text, 258)
        start = -sweep / 2 if is_top else 180 + sweep / 2
        arched(img, text, af, 258, BONE, start, step if is_top else -step, top=is_top)
    f, gap, rows = fit(label, lambda s: font("dmserif", s), 0.03, 222, max_size=120)
    place(d, rows, f, gap, BONE)
    return img


def sans(label):
    """Widely letterspaced gold sans on charcoal, no serif, no ornament. Core palette."""
    img = Image.new("RGB", (W, H), CHARCOAL); d = ImageDraw.Draw(img)
    f, gap, rows = fit(label, lambda s: font("montserrat", s, 600), 0.22, R, max_size=120)
    place(d, rows, f, gap, GOLD)
    return img


def bleed(label):
    """Full-bleed forest ground, big bone serif at maximum scale, one gold mark.
    Heritage palette."""
    img = Image.new("RGB", (W, H), FOREST); d = ImageDraw.Draw(img)
    f, gap, rows = fit(label, lambda s: font("dmserif", s), 0.05, R, leading=1.15, max_size=170, margin=14)
    y0, y1 = place(d, rows, f, gap, BONE)
    rule(d, y1 + 56, 44, GOLD, 4)
    return img


DIRECTIONS = {
    "Hairline": lambda label, i: hairline(label),
    "Keyline":  lambda label, i: keyline(label),
    "Disc":     lambda label, i: disc(label),
    "Numeral":  lambda label, i: numeral(label, i),
    "Crest":    lambda label, i: crest(label),
    "Sans":     lambda label, i: sans(label),
    "Bleed":    lambda label, i: bleed(label),
}


def main():
    for name, render in DIRECTIONS.items():
        out = ROOT / "covers" / name
        out.mkdir(parents=True, exist_ok=True)
        for i, (fname, label) in enumerate(COVERS, start=1):
            render(label, i).save(out / f"{fname}.png")
        print(f"{name:9s} {len(COVERS)} covers -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
