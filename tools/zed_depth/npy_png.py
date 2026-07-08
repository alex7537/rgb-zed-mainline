from pathlib import Path

import imageio.v2 as imageio
import numpy as np


ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT_DIR / "outputs" / "zed_depth" / "depth_meter.npy"
OUTPUT_PATH = ROOT_DIR / "outputs" / "zed_depth" / "depth.png"


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    depth = np.load(INPUT_PATH).astype(np.float32)
    depth_u16 = np.clip(depth * 1000.0, 0, 65535).astype(np.uint16)
    imageio.imwrite(OUTPUT_PATH, depth_u16)
    print("saved", OUTPUT_PATH)


if __name__ == "__main__":
    main()
