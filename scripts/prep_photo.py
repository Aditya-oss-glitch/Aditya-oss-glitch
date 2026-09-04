from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py source-photo.jpg")
        sys.exit(1)

    source = Path(sys.argv[1])

    if not source.exists():
        print(f"Error: {source} does not exist.")
        sys.exit(1)

    output = source.parent / "source-prepped.png"

    print(f"[1/4] Loading {source}...")
    image = Image.open(source).convert("RGBA")

    print("[2/4] Removing background...")
    cutout = remove(image).convert("RGBA")

    # White canvas.
    rgba = np.array(cutout)

    rgb = rgba[:, :, :3].astype(np.float32)
    alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0

    white = np.full_like(rgb, 255.0)

    # Composite subject over pure white.
    composited = rgb * alpha + white * (1.0 - alpha)
    composited = np.clip(composited, 0, 255).astype(np.uint8)

    print("[3/4] Improving local contrast with CLAHE...")

    # Convert to grayscale.
    gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)

    # CLAHE boosts local highlights/shadows without simply
    # making the whole image globally darker.
    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(gray)

    # Keep a clean grayscale PNG.
    print("[4/4] Saving prepped image...")

    result = Image.fromarray(enhanced, mode="L")
    result.save(output)

    print(f"Done: {output}")
    print(f"Size: {result.width} x {result.height}")


if __name__ == "__main__":
    main()
