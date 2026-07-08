from pathlib import Path

import cv2
import json
import numpy as np
import pyrealsense2 as rs


SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR.parents[2] / "outputs" / "realsense_test"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    align = rs.align(rs.stream.color)
    pipeline.start(config)

    for _ in range(30):
        pipeline.wait_for_frames()

    frames = pipeline.wait_for_frames()
    aligned = align.process(frames)
    color_frame = aligned.get_color_frame()
    depth_frame = aligned.get_depth_frame()
    if not color_frame or not depth_frame:
        raise RuntimeError("No frames received")

    color = np.asanyarray(color_frame.get_data())
    depth = np.asanyarray(depth_frame.get_data())
    intr = color_frame.profile.as_video_stream_profile().intrinsics

    cv2.imwrite(str(OUT_DIR / "color_0000.png"), color)
    cv2.imwrite(str(OUT_DIR / "depth_0000.png"), depth)
    with (OUT_DIR / "intrinsics.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "width": intr.width,
                "height": intr.height,
                "fx": intr.fx,
                "fy": intr.fy,
                "cx": intr.ppx,
                "cy": intr.ppy,
            },
            f,
            indent=2,
        )

    pipeline.stop()
    print("Saved RealSense smoke-test outputs to:", OUT_DIR)


if __name__ == "__main__":
    main()
