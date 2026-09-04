from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageOps


INPUT = Path("source-prepped.png")
OUTPUT = Path("avi-ascii.svg")

# More characters = more facial detail.
COLS = 110
ROWS = 62

CELL_W = 7
CELL_H = 13

WIDTH = COLS * CELL_W
HEIGHT = ROWS * CELL_H

# Bright -> dark
RAMP = " .`:-=+*cs#%@"

TEXT_COLOR = "#005411"


def find_subject_bbox(image):
    """
    Find the non-white region created by the background-removal /
    white compositing stage.

    Returns a bounding box around meaningful pixels.
    """

    pixels = np.asarray(image)

    # Anything substantially darker than white is considered subject.
    mask = pixels < 245

    ys, xs = np.where(mask)

    if len(xs) == 0:
        return (0, 0, image.width, image.height)

    left = max(0, xs.min() - 8)
    right = min(image.width, xs.max() + 9)
    top = max(0, ys.min() - 8)
    bottom = min(image.height, ys.max() + 9)

    return left, top, right, bottom


def brightness_to_char(value):
    """
    Convert grayscale brightness to ASCII density.

    White -> space
    Black -> @
    """

    darkness = 255 - value

    index = int(
        darkness / 256 * len(RAMP)
    )

    index = max(
        0,
        min(index, len(RAMP) - 1)
    )

    return RAMP[index]


def main():

    if not INPUT.exists():
        raise FileNotFoundError(
            f"{INPUT} not found. Run prep_photo.py first."
        )

    print("[1/5] Loading preprocessed image...")

    image = Image.open(INPUT).convert("L")

    print("[2/5] Finding subject...")

    bbox = find_subject_bbox(image)

    print(f"Subject bounding box: {bbox}")

    image = image.crop(bbox)

    print("[3/5] Improving contrast...")

    image = ImageOps.autocontrast(image, cutoff=1)

    image = ImageEnhance.Contrast(image).enhance(1.35)

    print("[4/5] Rendering ASCII grid...")

    # Character cells are taller than they are wide.
    # Compensate so the portrait doesn't become vertically distorted.
    image = image.resize(
        (COLS, ROWS),
        Image.Resampling.LANCZOS,
    )

    pixels = np.asarray(image)

    rows = []

    for y in range(ROWS):

        line = []

        for x in range(COLS):

            value = int(pixels[y, x])

            line.append(
                brightness_to_char(value)
            )

        rows.append("".join(line))

    print("[5/5] Building animated SVG...")

    svg = []

    svg.append(
        f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
role="img"
aria-label="Animated ASCII portrait">
'''
    )

    svg.append("""
<style>
.ascii {
    font-family:
        Menlo,
        Monaco,
        Consolas,
        "Courier New",
        monospace;

    font-size: 12px;
    font-weight: 400;
    fill: #8a8a8a;
}

.row {
    opacity: 0;
}

@keyframes rowReveal {

    0% {
        opacity: 0;
        transform: translateX(-10px);
    }

    100% {
        opacity: 1;
        transform: translateX(0);
    }
}
</style>
""")

    for y, row in enumerate(rows):

        delay = y * 0.035

        y_position = (y + 1) * CELL_H

        svg.append(
            f'''
<text
x="0"
y="{y_position}"
class="ascii row"
style="animation:
rowReveal
0.55s
ease-out
{delay:.3f}s
forwards;"
xml:space="preserve">{row}</text>
'''
        )

    svg.append("</svg>")

    OUTPUT.write_text(
        "".join(svg),
        encoding="utf-8",
    )

    print()
    print(f"Created: {OUTPUT}")
    print(f"Grid: {COLS} × {ROWS}")
    print(f"SVG: {WIDTH} × {HEIGHT}")


if __name__ == "__main__":
    main()