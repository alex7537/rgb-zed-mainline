from pathlib import Path

import cv2
import pyzed.sl as sl


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUT_DIR = SCRIPT_DIR.parents[2] / "outputs" / "zed_capture"


def main(
    out_dir=DEFAULT_OUT_DIR,
    num_frames=5,
    fps=15,
    resolution="HD720",
    warmup_frames=30,
):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.camera_fps = fps
    init_params.depth_mode = sl.DEPTH_MODE.NONE

    if resolution.upper() == "HD2K":
        init_params.camera_resolution = sl.RESOLUTION.HD2K
    elif resolution.upper() == "HD1080":
        init_params.camera_resolution = sl.RESOLUTION.HD1080
    elif resolution.upper() == "HD720":
        init_params.camera_resolution = sl.RESOLUTION.HD720
    elif resolution.upper() == "VGA":
        init_params.camera_resolution = sl.RESOLUTION.VGA
    else:
        raise ValueError("Unsupported resolution")

    status = zed.open(init_params)
    if status != sl.ERROR_CODE.SUCCESS:
        print("[ERROR] Cannot open ZED:", status)
        return

    cam_info = zed.get_camera_information()
    calib = cam_info.camera_configuration.calibration_parameters
    fx, fy = calib.left_cam.fx, calib.left_cam.fy
    cx, cy = calib.left_cam.cx, calib.left_cam.cy
    tx, _, _ = calib.stereo_transform.get_translation().get()
    baseline_m = abs(tx) / 1000.0

    k_path = out_dir / "K_rgb_fs.txt"
    with k_path.open("w", encoding="utf-8") as f:
        f.write(f"{fx} 0.0 {cx} 0.0 {fy} {cy} 0.0 0.0 1.0\n")
        f.write(f"{baseline_m}\n")

    runtime = sl.RuntimeParameters()
    left_mat = sl.Mat()
    right_mat = sl.Mat()

    for _ in range(warmup_frames):
        zed.grab(runtime)

    saved = 0
    while saved < num_frames:
        if zed.grab(runtime) != sl.ERROR_CODE.SUCCESS:
            continue
        zed.retrieve_image(left_mat, sl.VIEW.LEFT)
        zed.retrieve_image(right_mat, sl.VIEW.RIGHT)
        left_bgr = cv2.cvtColor(left_mat.get_data(), cv2.COLOR_BGRA2BGR)
        right_bgr = cv2.cvtColor(right_mat.get_data(), cv2.COLOR_BGRA2BGR)
        cv2.imwrite(str(out_dir / f"left_{saved:06d}.png"), left_bgr)
        cv2.imwrite(str(out_dir / f"right_{saved:06d}.png"), right_bgr)
        saved += 1

    zed.close()
    print("Saved ZED sample set to:", out_dir)


if __name__ == "__main__":
    main()
