"""Generate Instagram highlight covers.

Writes covers/<Direction>/01_StartHere.png ... 06_OffCourse.png.
Canvas 1080x1920; all artwork stays inside a 640 px circle at (540, 960).

Run:  python3 src/covers.py
Then: python3 src/contact_sheet.py   # and look at the 68 px column
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path("/tmp/fonts")

W, H = 1080, 1920
CX, CY, R = 540, 960, 320           # safe circle
SAFE_W_ONE = 540                    # one line sits on the circle's widest chord
SAFE_W_TWO = 470                    # two lines sit off-center where the chord narrows

CREAM, GOLD, CHARCOAL = "#F5F1E8", "#B8924A", "#1A1A1A"
FOREST, BONE = "#1F382C", "#E8E2D5"

COVERS = [
    ("01_StartHere", "START HERE"),
    ("02_Drills", "DRILLS"),
    ("03_TheComeback", "THE COMEBACK"),
    ("04_ProShop", "PRO SHOP"),
    ("05_Wellness", "WELLNESS"),
    ("06_OffCourse", "OFF COURSE"),
]

# One dict per direction. Add or remove directions here; nothing else changes.
# No numerals in the artwork: highlight order is fragile (see CLAUDE.md).
DIRECTIONS = {
    "Charcoal": dict(bg=CHARCOAL, text=CREAM, rule=GOLD),
    "Forest":   dict(bg=FOREST,   text=BONE,  rule=GOLD),
}

TRACKING = 0.14       # letter-spacing as a fraction of font size
LEADING = 1.35        # line height as a fraction of font size
MAX_SIZE, MIN_SIZE, STEP = 120, 40, 2
RULE_W, RULE_GAP, RULE_T = 150, 44, 2   # hairline rule width, gap from text, thickness


def label_font(size):
    f = ImageFont.truetype(str(FONTS / "Montserrat[wght].ttf"), size)
    f.set_variation_by_axes([600])   # variable fonts open at 100 otherwise
    return f


def tracked_width(font, text, size):
    gap = size * TRACKING
    w = sum(font.getlength(ch) for ch in text)
    return w + gap * (len(text) - 1)


def draw_tracked(draw, x, y, text, font, size, fill):
    gap = size * TRACKING
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + gap


def wrap(label):
    words = label.split()
    if len(words) == 1:
        return [label]
    # two lines, split at the point that balances the halves
    best = min(range(1, len(words)),
               key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))))
    return [" ".join(words[:best]), " ".join(words[best:])]


def fit(label):
    """Largest size at which the label fits: one line on the wide chord, else two."""
    for size in range(MAX_SIZE, MIN_SIZE - 1, -STEP):
        font = label_font(size)
        one = [label]
        if tracked_width(font, label, size) <= SAFE_W_ONE:
            return font, size, one
        two = wrap(label)
        if len(two) == 2 and max(tracked_width(font, l, size) for l in two) <= SAFE_W_TWO:
            return font, size, two
    raise ValueError(f"{label!r} does not fit at MIN_SIZE {MIN_SIZE}")


def render(label, spec):
    img = Image.new("RGB", (W, H), spec["bg"])
    d = ImageDraw.Draw(img)
    font, size, lines = fit(label)

    ascent, descent = font.getmetrics()
    line_h = size * LEADING
    block_h = line_h * (len(lines) - 1) + ascent + descent
    top = CY - block_h / 2

    for i, line in enumerate(lines):
        w = tracked_width(font, line, size)
        draw_tracked(d, CX - w / 2, top + i * line_h, line, font, size, spec["text"])

    # hairline rules above and below the label block
    for y in (top - RULE_GAP, top + block_h + RULE_GAP):
        d.rectangle([CX - RULE_W / 2, y, CX + RULE_W / 2, y + RULE_T], fill=spec["rule"])

    return img


def main():
    for name, spec in DIRECTIONS.items():
        out = ROOT / "covers" / name
        out.mkdir(parents=True, exist_ok=True)
        for fname, label in COVERS:
            render(label, spec).save(out / f"{fname}.png")
        print(f"{name}: {len(COVERS)} covers -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
