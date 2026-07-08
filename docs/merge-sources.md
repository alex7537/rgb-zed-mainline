# Merge Sources

This file records where the merged content in `rgb-zed-mainline` came from.

## Primary sources

- `Z:\Github\pipeline-RGB`
- `Z:\Github\ZED`

## Secondary sources

- `Z:\Github\foundationstereo-industrial-6dpose`
- `Z:\Github\match`

## Imported into this repository

### From `pipeline-RGB`

- `RGB-pipeline/` -> `pipelines/dual_rgb/RGB-pipeline/`
- `realsense_IR_v1.py` -> `pipelines/realsense_ir/realsense_IR_v1.py`
- `IR-RGB-clp.py` -> `pipelines/realsense_ir/IR-RGB-clp.py`
- `fs_depth_to_rgb_alignment.py` -> `pipelines/realsense_ir/fs_depth_to_rgb_alignment.py`
- `test_realsense.py` -> `pipelines/realsense_ir/test_realsense.py`
- `zed+depth可视化/` -> `tools/zed_depth/zed_visualization/`
- `pose数据/` -> `references/pose_data/pose数据/`

### From `ZED`

- `zed-rgb.py` -> `pipelines/zed_rgb/zed-rgb.py`
- `zed_capture/` -> `samples/zed_capture/`
- `对齐检测/` -> `samples/zed_alignment_check/`
- `depth_compare.py` -> `tools/zed_depth/depth_compare.py`
- `depth_uberprufen.py` -> `tools/zed_depth/depth_uberprufen.py`
- `npy_png.py` -> `tools/zed_depth/npy_png.py`

### From `foundationstereo-industrial-6dpose`

- `IR_farben.py` -> `pipelines/realsense_ir/IR_farben.py`
- `rs_calib_d435.json` -> `pipelines/realsense_ir/rs_calib_d435.json`

## Not merged intentionally

### `FoundationStereo_copy`

Not merged because it is upstream model code and should stay external.

### `match`

No unique core pipeline code was found beyond scripts already duplicated elsewhere.

### `foundationpose`

Not merged because the repository is empty.
