from pathlib import Path

import cv2
import json
import numpy as np
import open3d as o3d


SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR.parents[2] / "outputs" / "realsense_ir"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def assert_intr_matches_image(k, img, name):
    h, w = img.shape[:2]
    assert k["width"] == w and k["height"] == h, f"{name} intrinsics size mismatch"


def backproject_depth_to_points(depth_m, k):
    h, w = depth_m.shape
    fx, fy = k["fx"], k["fy"]
    cx, cy = k["cx"], k["cy"]
    v, u = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    z = depth_m.astype(np.float32)
    valid = np.isfinite(z) & (z > 0)
    if not np.any(valid):
        return None
    u = u[valid].astype(np.float32)
    v = v[valid].astype(np.float32)
    z = z[valid]
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    return np.stack([x, y, z], axis=1)


def transform_points(pts, r, t):
    return (r @ pts.T + t.reshape(3, 1)).T


def main():
    fs_depth_path = OUT_DIR / "depth_meter.npy"
    color_path = OUT_DIR / "color_raw_0000.png"
    ir_intr_path = OUT_DIR / "ir_intrinsics.json"
    color_intr_path = OUT_DIR / "color_intrinsics.json"
    ir2color_extr_path = OUT_DIR / "ir2color_extrinsics.json"
    ply_out = OUT_DIR / "cloud_fs_ir2rgb_colored.ply"
    depth_png_out = OUT_DIR / "depth_fs_ir2rgb_0000.png"

    k_ir = load_json(ir_intr_path)
    k_color = load_json(color_intr_path)
    extr = load_json(ir2color_extr_path)
    r = np.array(extr["R"], dtype=np.float32)
    t = np.array(extr["t"], dtype=np.float32)
    color_bgr = cv2.imread(str(color_path), cv2.IMREAD_COLOR)
    depth_ir_m = np.load(fs_depth_path).astype(np.float32)

    assert_intr_matches_image(k_color, color_bgr, "color")
    pts_ir = backproject_depth_to_points(depth_ir_m, k_ir)
    if pts_ir is None:
        print("No valid depth points in FS depth map.")
        return

    pts_c = transform_points(pts_ir, r, t)
    fx, fy = k_color["fx"], k_color["fy"]
    cx, cy = k_color["cx"], k_color["cy"]
    h_c, w_c = color_bgr.shape[:2]
    x, y, z = pts_c[:, 0], pts_c[:, 1], pts_c[:, 2]
    valid = np.isfinite(z) & (z > 0)
    x, y, z = x[valid], y[valid], z[valid]
    pts_c = pts_c[valid]
    u = np.round(fx * x / z + cx).astype(np.int32)
    v = np.round(fy * y / z + cy).astype(np.int32)
    inb = (u >= 0) & (u < w_c) & (v >= 0) & (v < h_c)
    u, v, z = u[inb], v[inb], z[inb]
    pts_c = pts_c[inb]

    depth_color_m = np.zeros((h_c, w_c), dtype=np.float32)
    for z_val, uu, vv in zip(z, u, v):
        if depth_color_m[vv, uu] == 0 or z_val < depth_color_m[vv, uu]:
            depth_color_m[vv, uu] = z_val

    color_rgb = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    cols = color_rgb[v, u]
    depth_mm = np.clip(depth_color_m * 1000.0, 0, 65535).astype(np.uint16)
    cv2.imwrite(str(depth_png_out), depth_mm)

    keep = (pts_c[:, 2] > 0.1) & (pts_c[:, 2] < 2.0)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts_c[keep])
    pcd.colors = o3d.utility.Vector3dVector(cols[keep])
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    o3d.io.write_point_cloud(str(ply_out), pcd)
    print("Saved aligned RealSense RGB-depth artifacts to:", OUT_DIR)


if __name__ == "__main__":
    main()
