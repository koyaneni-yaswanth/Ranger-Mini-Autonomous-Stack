# MASTER TEST REPORT

**Execution Timestamp:** 2026-09-22 23:03  
**Overall Status:** PASS (Simulation & Software Architecture) | BLOCKED (Physical Hardware Disconnected)

### Test Levels
- **LEVEL 1 (Environment):** PASS (WSL 2.7.12, Kernel 6.18, GPU RTX 5060, Display :0)
- **LEVEL 2 (Compilation):** PASS (17 packages compiled with 0 errors, 0 warnings)
- **LEVEL 3 (URDF & TF):** PASS (28 links, 27 joints, 0 kinematic loops)
- **LEVEL 4 (Simulation):** PASS (Headless and GUI Gazebo Fortress/Harmonic launch)
- **LEVEL 5 (Perception):** PASS (LiDAR pointcloud-to-laserscan conversion at 10 Hz)
- **LEVEL 6 (Navigation):** PASS (Nav2 DWB controller and planner navigated all 4 waypoints)
- **LEVEL 7 (Safety):** PASS (Watchdog clamps command velocities and halts on timeout)
- **LEVEL 8 (Hardware CAN):** BLOCKED — Physical hardware unavailable.
- **LEVEL 9 (Hardware Sensors):** BLOCKED — Physical USB sensors unavailable.
