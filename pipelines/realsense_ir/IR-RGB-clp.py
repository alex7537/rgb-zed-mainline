from pathlib import Path

import cv2
import json
import numpy as np
import open3d as o3d


SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR.parents[2] / "outputs" / "realsense_ir"
FS_DEPTH_PATH = OUT_DIR / "depth_meter.npy"


def project_ir_depth_to_color(depth_ir_m, k_ir, k_color, r_ir2color, t_ir2color, color_img_bgr):
    h_ir, w_ir = depth_ir_m.shape
    assert h_ir == k_ir["height"] and w_ir == k_ir["width"]

    vs, us = np.meshgrid(np.arange(h_ir), np.arange(w_ir), indexing="ij")
    valid = depth_ir_m > 0
    if not np.any(valid):
        return None, None, None

    fx_ir, fy_ir = k_ir["fx"], k_ir["fy"]
    cx_ir, cy_ir = k_ir["cx"], k_ir["cy"]
    x_ir = (us - cx_ir) * depth_ir_m / fx_ir
    y_ir = (vs - cy_ir) * depth_ir_m / fy_ir
    pts_ir = np.stack([x_ir[valid], y_ir[valid], depth_ir_m[valid]], axis=1)

    pts_color = (r_ir2color @ pts_ir.T + t_ir2color).T
    x_c, y_c, z_c = pts_color[:, 0], pts_color[:, 1], pts_color[:, 2]
    valid_c = z_c > 0
    x_c, y_c, z_c = x_c[valid_c], y_c[valid_c], z_c[valid_c]
    pts_color = np.stack([x_c, y_c, z_c], axis=1)

    fx_c, fy_c = k_color["fx"], k_color["fy"]
    cx_c, cy_c = k_color["cx"], k_color["cy"]
    w_c, h_c = k_color["width"], k_color["height"]
    u_c = np.round(fx_c * x_c / z_c + cx_c).astype(int)
    v_c = np.round(fy_c * y_c / z_c + cy_c).astype(int)
    in_bounds = (u_c >= 0) & (u_c < w_c) & (v_c >= 0) & (v_c < h_c)
    u_c, v_c, z_c = u_c[in_bounds], v_c[in_bounds], z_c[in_bounds]
    pts_color = pts_color[in_bounds]

    depth_color_m = np.zeros((h_c, w_c), dtype=np.float32)
    for z_val, uu, vv in zip(z_c, u_c, v_c):
        if depth_color_m[vv, uu] == 0 or z_val < depth_color_m[vv, uu]:
            depth_color_m[vv, uu] = z_val

    color_rgb = cv2.cvtColor(color_img_bgr, cv2.COLOR_BGR2RGB)
    cols_color = color_rgb[v_c, u_c].astype(np.float32) / 255.0
    return depth_color_m, pts_color, cols_color


def main():
    with (OUT_DIR / "ir_intrinsics.json").open("r", encoding="utf-8") as f:
        k_ir = json.load(f)
    with (OUT_DIR / "color_intrinsics.json").open("r", encoding="utf-8") as f:
        k_color = json.load(f)
    with (OUT_DIR / "ir2color_extrinsics.json").open("r", encoding="utf-8") as f:
        extr = json.load(f)

    r_ir2color = np.array(extr["R"], dtype=np.float32)
    t_ir2color = np.array(extr["t"], dtype=np.float32)
    color = cv2.imread(str(OUT_DIR / "color_raw_0000.png"), cv2.IMREAD_COLOR)
    depth_ir = np.load(FS_DEPTH_PATH).astype(np.float32)

    depth_color, pts_color, cols_color = project_ir_depth_to_color(
        depth_ir, k_ir, k_color, r_ir2color, t_ir2color, color
    )
    if pts_color is None:
        print("No valid projected points.")
        return

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts_color)
    pcd.colors = o3d.utility.Vector3dVector(cols_color)
    o3d.io.write_point_cloud(str(OUT_DIR / "cloud_fs_ir2rgb.ply"), pcd)

    depth_fs_u16 = (depth_color * 1000.0).astype(np.uint16)
    cv2.imwrite(str(OUT_DIR / "depth_fs_ir2rgb_0000.png"), depth_fs_u16)
    print("Saved aligned FS depth and colored point cloud to:", OUT_DIR)


if __name__ == "__main__":
    main()
