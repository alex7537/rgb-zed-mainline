from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parents[2] / "outputs" / "dual_rgb"
FS_INPUT_DIR = OUTPUT_DIR / "shared_fs_test"
DEBUG_OUT_DIR = OUTPUT_DIR / "debug"
CALIB_FILE = SCRIPT_DIR / "stereo_calib_rgb.npz"

LEFT_SERIAL = "727212070348"
RIGHT_SERIAL = "923322072633"
W, H = 1280, 720
FPS = 15


def main():
    calib = np.load(CALIB_FILE)
    k_left = calib["K_left"]
    k_right = calib["K_right"]
    dist_left = calib["dist_left"]
    dist_right = calib["dist_right"]
    r1 = calib["R1"]
    r2 = calib["R2"]
    p1 = calib["P1"]
    p2 = calib["P2"]

    DEBUG_OUT_DIR.mkdir(parents=True, exist_ok=True)
    FS_INPUT_DIR.mkdir(parents=True, exist_ok=True)

    pipeline_left = rs.pipeline()
    config_left = rs.config()
    config_left.enable_device(LEFT_SERIAL)
    config_left.enable_stream(rs.stream.color, W, H, rs.format.bgr8, FPS)

    pipeline_right = rs.pipeline()
    config_right = rs.config()
    config_right.enable_device(RIGHT_SERIAL)
    config_right.enable_stream(rs.stream.color, W, H, rs.format.bgr8, FPS)

    pipeline_left.start(config_left)
    pipeline_right.start(config_right)

    try:
        for _ in range(30):
            pipeline_left.wait_for_frames()
            pipeline_right.wait_for_frames()

        frames_l = pipeline_left.wait_for_frames()
        frames_r = pipeline_right.wait_for_frames()
        color_frame_l = frames_l.get_color_frame()
        color_frame_r = frames_r.get_color_frame()
        if not color_frame_l or not color_frame_r:
            raise RuntimeError("Failed to receive left/right RGB frames")

        color_l = np.asanyarray(color_frame_l.get_data())
        color_r = np.asanyarray(color_frame_r.get_data())

        cv2.imwrite(str(DEBUG_OUT_DIR / "left_raw.png"), color_l)
        cv2.imwrite(str(DEBUG_OUT_DIR / "right_raw.png"), color_r)

        map1_l, map2_l = cv2.initUndistortRectifyMap(
            k_left, dist_left, r1, p1, (W, H), cv2.CV_32FC1
        )
        map1_r, map2_r = cv2.initUndistortRectifyMap(
            k_right, dist_right, r2, p2, (W, H), cv2.CV_32FC1
        )

        left_rect = cv2.remap(color_l, map1_l, map2_l, cv2.INTER_LINEAR)
        right_rect = cv2.remap(color_r, map1_r, map2_r, cv2.INTER_LINEAR)

        left_out = FS_INPUT_DIR / "left_rect.png"
        right_out = FS_INPUT_DIR / "right_rect.png"
        cv2.imwrite(str(left_out), left_rect)
        cv2.imwrite(str(right_out), right_rect)
        cv2.imwrite(str(DEBUG_OUT_DIR / "left_rect.png"), left_rect)
        cv2.imwrite(str(DEBUG_OUT_DIR / "right_rect.png"), right_rect)

        print("Rectified left saved to :", left_out)
        print("Rectified right saved to:", right_out)
        print("Run FoundationStereo with files from:", FS_INPUT_DIR)
    finally:
        pipeline_left.stop()
        pipeline_right.stop()


if __name__ == "__main__":
    main()
