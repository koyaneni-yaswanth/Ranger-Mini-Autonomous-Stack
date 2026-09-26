# JARVIS-X: KNOWN ISSUES & REPAIR RUNBOOK

## 1. Resolved Issues

### Issue 1: Costmap Voxel Boundary Out-of-Bounds Error
- **Symptom:** `Sensor origin at (-5.39, -2.94, 0.83) is out of map bounds (-6.90, -4.30, 0.00) to (-3.90, -1.30, 0.80)`.
- **Root Cause:** In `ranger_navigation/config/nav2_params.yaml`, the local costmap `voxel_layer` configured `z_voxels: 16` and `z_resolution: 0.05`, bounding vertical space to $16 \times 0.05 = 0.80\text{m}$. The Livox Mid-360 LiDAR sensor sits on the mast platform at $Z \approx 0.831\text{m}$.
- **Resolution:** Updated `z_voxels: 32`, expanding the volume to $1.60\text{m}$ ($0.77\text{m}$ engineering margin). Verified with automated regression test `test_costmap_bounds_regression.py`.

### Issue 2: Standalone Python `jarvis_core` Import Resolution
- **Symptom:** `ModuleNotFoundError: No module named 'jarvis_core'`.
- **Root Cause:** Running Python directly outside a sourced ROS workspace could not discover workspace packages, and eager importing of `rclpy` in top-level `__init__.py` caused C-extension library linking failures.
- **Resolution:** Made ROS node imports decoupled and lazy, registered `/opt/ros/lyrical/lib` in `/etc/ld.so.conf.d/ros_lyrical.conf`, and added workspace `.pth` site-package discovery.

### Issue 3: RViz2 TF Time Jump Exception
- **Symptom:** `tf2::LookupException: Static cache is empty`.
- **Root Cause:** RViz was launched using system wall time rather than simulation time published by Gazebo `/clock`.
- **Resolution:** Updated `run_rviz.sh` to pass `--ros-args -p use_sim_time:=true` by default.

### Issue 4: Docker Environment Availability
- **Audit Finding:** Host environment reports `docker: command not found`.
- **Status:** Docker is documented as optional for containerized CI; native host WSL2 Ubuntu-26.04 execution is fully supported and active.
