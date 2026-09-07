"""Build the legibility contact sheet.

Circle-crops every cover in covers/<Direction>/ and lays them out at 220 px and
68 px. Writes build/contact_sheet.png. Open it and read the 68 px row: if a
label is not legible there, the direction fails.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path("/tmp/fonts")
COVERS, BUILD = ROOT / "covers", ROOT / "build"

CX, CY, R = 540, 960, 320
SIZES = (220, 68)
PAD, GUTTER, LABEL_H = 40, 24, 28
SHEET_BG, INK = "#FFFFFF", "#1A1A1A"


def circle_crop(path, size):
    img = Image.open(path).convert("RGB").crop((CX - R, CY - R, CX + R, CY + R))
    img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4,) * 2, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    out = Image.new("RGB", (size, size), SHEET_BG)
    out.paste(img, (0, 0), mask.resize((size, size), Image.LANCZOS))
    return out


def main():
    dirs = sorted(p for p in COVERS.iterdir() if p.is_dir())
    if not dirs:
        raise SystemExit("no directions in covers/ — run src/covers.py first")
    font = ImageFont.truetype(str(FONTS / "Montserrat[wght].ttf"), 18)
    font.set_variation_by_axes([500])

    n = max(len(list(d.glob("*.png"))) for d in dirs)
    row_h = sum(SIZES) + GUTTER * (len(SIZES) - 1) + LABEL_H
    width = PAD * 2 + n * SIZES[0] + (n - 1) * GUTTER
    height = PAD * 2 + len(dirs) * row_h + (len(dirs) - 1) * PAD

    sheet = Image.new("RGB", (width, height), SHEET_BG)
    d = ImageDraw.Draw(sheet)
    y = PAD
    for direction in dirs:
        d.text((PAD, y), f"{direction.name}  ·  220 px / 68 px", font=font, fill=INK)
        y += LABEL_H
        for size in SIZES:
            for i, png in enumerate(sorted(direction.glob("*.png"))):
                x = PAD + i * (SIZES[0] + GUTTER) + (SIZES[0] - size) // 2
                sheet.paste(circle_crop(png, size), (x, y))
            y += size + GUTTER
        y += PAD - GUTTER

    BUILD.mkdir(exist_ok=True)
    out = BUILD / "contact_sheet.png"
    sheet.save(out)
    print(f"wrote {out.relative_to(ROOT)}  ({width}x{height})")


if __name__ == "__main__":
    main()
