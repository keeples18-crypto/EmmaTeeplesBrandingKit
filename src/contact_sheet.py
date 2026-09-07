"""Build the 68 px contact sheets.

Circle-crops every cover in covers/<Direction>/ at 220 px (inspection) and
68 px (true phone size). Writes one sheet per direction to build/<Direction>.png
and a combined build/contact_sheet.png with every direction stacked.

Open the combined sheet and judge the 68 px rows on distinctiveness and
cohesion. Instagram prints the highlight name under the circle, so the word
itself need not be readable; the construction must still register as a mark.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path("/tmp/fonts")
COVERS, BUILD = ROOT / "covers", ROOT / "build"

CX, CY, R = 540, 960, 320
SIZES = (220, 68)
PAD, GUTTER, LABEL_H = 40, 24, 30
SHEET_BG, INK = "#FFFFFF", "#1A1A1A"


def circle_crop(path, size):
    img = Image.open(path).convert("RGB").crop((CX - R, CY - R, CX + R, CY + R))
    img = img.resize((size, size), Image.LANCZOS)
    big = size * 4
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, big - 1, big - 1], fill=255)
    out = Image.new("RGB", (size, size), SHEET_BG)
    out.paste(img, (0, 0), mask.resize((size, size), Image.LANCZOS))
    return out


def direction_sheet(direction, font):
    pngs = sorted(direction.glob("*.png"))
    n = len(pngs)
    width = PAD * 2 + n * SIZES[0] + (n - 1) * GUTTER
    height = PAD * 2 + LABEL_H + sum(SIZES) + GUTTER * (len(SIZES) - 1)
    sheet = Image.new("RGB", (width, height), SHEET_BG)
    d = ImageDraw.Draw(sheet)
    d.text((PAD, PAD), f"{direction.name}   ·   220 px  /  68 px", font=font, fill=INK)
    y = PAD + LABEL_H
    for size in SIZES:
        for i, png in enumerate(pngs):
            x = PAD + i * (SIZES[0] + GUTTER) + (SIZES[0] - size) // 2
            sheet.paste(circle_crop(png, size), (x, y))
        y += size + GUTTER
    return sheet


def main():
    dirs = sorted(p for p in COVERS.iterdir() if p.is_dir())
    if not dirs:
        raise SystemExit("no directions in covers/ — run src/covers.py first")
    font = ImageFont.truetype(str(FONTS / "Montserrat[wght].ttf"), 20)
    font.set_variation_by_axes([600])

    BUILD.mkdir(exist_ok=True)
    sheets = []
    for direction in dirs:
        s = direction_sheet(direction, font)
        s.save(BUILD / f"{direction.name}.png")
        sheets.append(s)

    width = max(s.width for s in sheets)
    combined = Image.new("RGB", (width, sum(s.height for s in sheets)), SHEET_BG)
    y = 0
    for s in sheets:
        combined.paste(s, (0, y)); y += s.height
    out = BUILD / "contact_sheet.png"
    combined.save(out)
    print(f"wrote {len(sheets)} direction sheets and {out.relative_to(ROOT)} ({combined.width}x{combined.height})")


if __name__ == "__main__":
    main()
