"""Build the reviewer sheet: docs/review_sheet.png.

One image for a non-technical reviewer on a phone. Three rows, one per
shortlisted direction, each with the six covers close up and again at the
size they appear on a phone. 1080 px wide so that on a phone screen the
small row shows at true highlight size.

Run after src/covers.py:  python3 src/review_sheet.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from covers import COVERS, DIRECTIONS, CX, CY, R, FONTS, CHARCOAL  # noqa: E402

OUT = ROOT / "docs" / "review_sheet.png"
W, PAD, GAP = 1080, 40, 16
BIG, SMALL = (W - 2 * PAD - 5 * GAP) // 6, 68
INK, MUTED, BG, RULE = CHARCOAL, "#6B6B6B", "#FFFFFF", "#E3E3E3"   # white, like the profile page

BLURB = {
    "Crest": "A deep green badge with a gold ring, her name curved around the top "
             "and Redding around the bottom, like a club crest.",
    "Bleed": "Deep green right to the edge, with the word large in cream and a small "
             "gold dash beneath it.",
    "Disc":  "A black circle with the word in clean cream lettering and a thin cream "
             "rim around the edge.",
}


def mont(size, weight=500):
    f = ImageFont.truetype(str(FONTS / "Montserrat[wght].ttf"), size)
    f.set_variation_by_axes([weight]); return f


def playfair(size, weight=400):
    f = ImageFont.truetype(str(FONTS / "PlayfairDisplay[wght].ttf"), size)
    f.set_variation_by_axes([weight]); return f


def circle_crop(path, size):
    img = Image.open(path).convert("RGB").crop((CX - R, CY - R, CX + R, CY + R))
    img = img.resize((size, size), Image.LANCZOS)
    big = size * 4
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, big - 1, big - 1], fill=255)
    out = Image.new("RGB", (size, size), BG)
    out.paste(img, (0, 0), mask.resize((size, size), Image.LANCZOS))
    return out


def wrap_text(text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.getlength(trial) <= width:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    title_f, lead_f = playfair(46), mont(24)
    name_f, blurb_f, cap_f = playfair(40), mont(24), mont(18, 500)

    header = [
        ("Highlight covers", title_f, INK),
        ("Three options. Each row is one look for all six highlights.", lead_f, MUTED),
        ("Top line shows them close up. Bottom line shows the size they appear on your phone.", lead_f, MUTED),
    ]
    # measure
    y = PAD
    for text, f, _ in header:
        for _ in wrap_text(text, f, W - 2 * PAD):
            y += int(f.size * 1.4)
    y += 28
    rows = []
    for name in DIRECTIONS:
        blurb_lines = wrap_text(BLURB[name], blurb_f, W - 2 * PAD)
        row_h = (int(name_f.size * 1.3) + len(blurb_lines) * int(blurb_f.size * 1.45) + 18
                 + BIG + 20 + SMALL + 40)
        rows.append((name, blurb_lines, y)); y += row_h
    H = y + PAD // 2

    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    y = PAD
    for text, f, col in header:
        for line in wrap_text(text, f, W - 2 * PAD):
            d.text((PAD, y), line, font=f, fill=col); y += int(f.size * 1.4)

    for name, blurb_lines, y in rows:
        d.rectangle([PAD, y, W - PAD, y + 1], fill=RULE); y += 18
        d.text((PAD, y), name, font=name_f, fill=INK); y += int(name_f.size * 1.3)
        for line in blurb_lines:
            d.text((PAD, y), line, font=blurb_f, fill=MUTED); y += int(blurb_f.size * 1.45)
        y += 18
        pngs = [ROOT / "covers" / name / f"{fname}.png" for fname, _ in COVERS]
        for i, png in enumerate(pngs):
            sheet.paste(circle_crop(png, BIG), (PAD + i * (BIG + GAP), y))
        y += BIG + 20
        for i, png in enumerate(pngs):
            x = PAD + i * (BIG + GAP) + (BIG - SMALL) // 2
            sheet.paste(circle_crop(png, SMALL), (x, y))
        y += SMALL + 40

    OUT.parent.mkdir(exist_ok=True)
    sheet.save(OUT, optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)} ({W}x{H})")


if __name__ == "__main__":
    main()
