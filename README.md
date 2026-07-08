# rgb-zed-mainline

Unified stereo workflow for your two main routes:

- dual RGB cameras
- ZED stereo RGB

RealSense IR support is kept as a secondary helper pipeline, not the main project identity.

## What this repo contains

```text
pipelines/
  dual_rgb/
    RGB-pipeline/
  zed_rgb/
  realsense_ir/
tools/
  zed_depth/
samples/
references/
```

## Main routes

### 1. Dual RGB

Use:

- `pipelines/dual_rgb/RGB-pipeline/save_calib_images_dual_rgb.py`
- `pipelines/dual_rgb/RGB-pipeline/stereo_calibrate_rgb.py`
- `pipelines/dual_rgb/RGB-pipeline/make_fs_intrinsic_from_npz.py`
- `pipelines/dual_rgb/RGB-pipeline/capture_rectified_for_fs.py`

Outputs are written to:

- `outputs/dual_rgb/`

### 2. ZED RGB

Use:

- `pipelines/zed_rgb/zed-rgb.py`
- `tools/zed_depth/npy_png.py`
- `tools/zed_depth/depth_compare.py`
- `tools/zed_depth/depth_uberprufen.py`

Outputs are written to:

- `outputs/zed_capture/`
- `outputs/zed_depth/`

### 3. RealSense IR helper path

Use only when you need IR-to-RGB aligned depth:

- `pipelines/realsense_ir/realsense_IR_v1.py`
- `pipelines/realsense_ir/IR-RGB-clp.py`
- `pipelines/realsense_ir/IR_farben.py`
- `pipelines/realsense_ir/fs_depth_to_rgb_alignment.py`

Outputs are written to:

- `outputs/realsense_ir/`

## Why this is the main repo now

- `pipeline-RGB` had the cleanest dual-RGB calibration flow
- `ZED` had the cleanest direct stereo capture flow
- `foundationstereo-industrial-6dpose` and `match` were mostly duplicated integration snapshots
- `FoundationStereo_copy` should stay external as the upstream model dependency

## Cleanup already done

- removed repeated calibration failure folders
- removed repeated visualization copies
- reduced sample and pose data to minimal representative examples
- replaced old absolute paths with repo-relative output paths
- added `outputs/` to `.gitignore`

## Recommended archive/delete plan

- delete or archive `test`
- delete or archive `test1`
- delete the empty `foundationpose`
- archive `match` after final spot-check
- archive `foundationstereo-industrial-6dpose` after you fully switch to this repo
