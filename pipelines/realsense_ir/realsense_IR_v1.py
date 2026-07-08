from pathlib import Path

import cv2
import json
import numpy as np
import open3d as o3d
import pyrealsense2 as rs


SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR.parents[2] / "outputs" / "realsense_ir"
SERIAL_IR_CAM = "923322072633"
W, H = 640, 480


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device(SERIAL_IR_CAM)
    config.enable_stream(rs.stream.color, W, H, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, W, H, rs.format.z16, 30)
    config.enable_stream(rs.stream.infrared, 1, W, H, rs.format.y8, 30)
    config.enable_stream(rs.stream.infrared, 2, W, H, rs.format.y8, 30)

    align = rs.align(rs.stream.color)
    profile = pipeline.start(config)
    depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()

    for _ in range(30):
        pipeline.wait_for_frames()

    frames = pipeline.wait_for_frames()
    aligned = align.process(frames)
    color_raw_frame = frames.get_color_frame()
    color_frame = aligned.get_color_frame()
    depth_frame = aligned.get_depth_frame()
    ir_left_frame = frames.get_infrared_frame(1)
    ir_right_frame = frames.get_infrared_frame(2)

    if not color_frame or not depth_frame:
        raise RuntimeError("No frames received")

    color_raw = np.asanyarray(color_raw_frame.get_data())
    color = np.asanyarray(color_frame.get_data())
    depth = np.asanyarray(depth_frame.get_data())
    ir_left = np.asanyarray(ir_left_frame.get_data())
    ir_right = np.asanyarray(ir_right_frame.get_data())
    ir_left_rgb = cv2.cvtColor(ir_left, cv2.COLOR_GRAY2RGB)
    ir_right_rgb = cv2.cvtColor(ir_right, cv2.COLOR_GRAY2RGB)

    intr_left = ir_left_frame.profile.as_video_stream_profile().intrinsics
    intr_color = color_raw_frame.profile.as_video_stream_profile().intrinsics
    extr = ir_left_frame.profile.get_extrinsics_to(ir_right_frame.profile)
    baseline = np.linalg.norm(extr.translation)

    k_left = {
        "width": intr_left.width,
        "height": intr_left.height,
        "fx": intr_left.fx,
        "fy": intr_left.fy,
        "cx": intr_left.ppx,
        "cy": intr_left.ppy,
        "baseline_m": baseline,
    }
    k_color = {
        "width": intr_color.width,
        "height": intr_color.height,
        "fx": intr_color.fx,
        "fy": intr_color.fy,
        "cx": intr_color.ppx,
        "cy": intr_color.ppy,
    }

    z = depth.astype(np.float32) * depth_scale
    h_d, w_d = z.shape
    vs, us = np.meshgrid(np.arange(h_d), np.arange(w_d), indexing="ij")
    x = (us - intr_color.ppx) * z / intr_color.fx
    y = (vs - intr_color.ppy) * z / intr_color.fy
    valid = z > 0
    pts = np.stack((x[valid], y[valid], z[valid]), axis=-1)
    cols = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)[valid].reshape(-1, 3) / 255.0

    pcd_rs = o3d.geometry.PointCloud()
    pcd_rs.points = o3d.utility.Vector3dVector(pts)
    pcd_rs.colors = o3d.utility.Vector3dVector(cols)
    o3d.io.write_point_cloud(str(OUT_DIR / "cloud_rs_capture.ply"), pcd_rs)

    cv2.imwrite(str(OUT_DIR / "color_raw_0000.png"), color_raw)
    cv2.imwrite(str(OUT_DIR / "color_0000.png"), color)
    cv2.imwrite(str(OUT_DIR / "depth_0000.png"), depth)
    cv2.imwrite(str(OUT_DIR / "ir_left_0000.png"), ir_left_rgb)
    cv2.imwrite(str(OUT_DIR / "ir_right_0000.png"), ir_right_rgb)

    with (OUT_DIR / "ir_intrinsics.json").open("w", encoding="utf-8") as f:
        json.dump(k_left, f, indent=2)
    with (OUT_DIR / "color_intrinsics.json").open("w", encoding="utf-8") as f:
        json.dump(k_color, f, indent=2)

    extr_ir2color = ir_left_frame.profile.get_extrinsics_to(color_raw_frame.profile)
    r_ir2color = np.array(extr_ir2color.rotation).reshape(3, 3)
    t_ir2color = np.array(extr_ir2color.translation).reshape(3, 1)
    with (OUT_DIR / "ir2color_extrinsics.json").open("w", encoding="utf-8") as f:
        json.dump({"R": r_ir2color.tolist(), "t": t_ir2color.tolist()}, f, indent=2)

    pipeline.stop()
    print("Saved RealSense IR pipeline outputs to:", OUT_DIR)


if __name__ == "__main__":
    main()
