from pathlib import Path

import cv2
import numpy as np


ROOT_DIR = Path(__file__).resolve().parents[2]
RGB_PATH = ROOT_DIR / "samples" / "zed_alignment_check" / "left_000004.png"
DEPTH_PATH = ROOT_DIR / "samples" / "zed_alignment_check" / "depth.png"
OUTPUT_PATH = ROOT_DIR / "outputs" / "zed_depth" / "align_overlay.png"


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rgb = cv2.imread(str(RGB_PATH))
    depth16 = cv2.imread(str(DEPTH_PATH), cv2.IMREAD_UNCHANGED)
    assert rgb is not None, f"Cannot read {RGB_PATH}"
    assert depth16 is not None, f"Cannot read {DEPTH_PATH}"
    assert depth16.dtype == np.uint16
    assert rgb.shape[:2] == depth16.shape[:2]

    d = depth16.astype(np.float32)
    d[d == 0] = np.nan
    vmin = np.nanpercentile(d, 5)
    vmax = np.nanpercentile(d, 95)
    d8 = (np.clip((d - vmin) / (vmax - vmin + 1e-6), 0, 1) * 255).astype(np.uint8)
    d8 = np.nan_to_num(d8).astype(np.uint8)
    edges = cv2.Canny(d8, 40, 120)
    overlay = rgb.copy()
    overlay[edges > 0] = (0, 0, 255)
    cv2.imwrite(str(OUTPUT_PATH), overlay)
    print("Saved", OUTPUT_PATH)


if __name__ == "__main__":
    main()
