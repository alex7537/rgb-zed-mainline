from pathlib import Path

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
CALIB_FILE = SCRIPT_DIR / "stereo_calib_rgb.npz"
OUT_DIR = SCRIPT_DIR.parents[2] / "outputs" / "dual_rgb"
OUT_K_PATH = OUT_DIR / "K_d435_2RGB.txt"


def main():
    calib = np.load(CALIB_FILE)
    p1 = calib["P1"]
    t = calib["T"].reshape(3, 1)

    k_rect = p1[:, :3]
    baseline = float(np.linalg.norm(t))
    k_flat = k_rect.reshape(-1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_K_PATH.open("w", encoding="utf-8") as f:
        f.write(" ".join(map(str, k_flat.tolist())) + "\n")
        f.write(f"{baseline}\n")

    print("Wrote FoundationStereo intrinsic file to:", OUT_K_PATH)
    print("baseline (m) =", baseline)


if __name__ == "__main__":
    main()
