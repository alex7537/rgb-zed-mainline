from pathlib import Path

import cv2
import imageio.v2 as imageio
import numpy as np


ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT_DIR / "outputs" / "zed_depth" / "depth_meter.npy"
OUTPUT_PATH = ROOT_DIR / "outputs" / "zed_depth" / "depth_color.png"


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    depth = np.load(INPUT_PATH).astype(np.float32)
    depth_vis = depth.copy()
    depth_vis[~np.isfinite(depth_vis)] = 0
    depth_vis[depth_vis <= 0] = 0
    depth_norm = cv2.normalize(depth_vis, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    depth_color = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)
    imageio.imwrite(OUTPUT_PATH, depth_color)
    print("saved", OUTPUT_PATH)


if __name__ == "__main__":
    main()
