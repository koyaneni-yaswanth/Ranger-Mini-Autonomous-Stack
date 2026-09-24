# Simulation-to-Real Transfer & Parity

## 1. Parity Matrix
| Subsystem | Gazebo Harmonic Simulation | Physical Hardware Platform | Parity Mechanism |
| :--- | :--- | :--- | :--- |
| Mobile Base Control | `gz_ros2_control` Diff/Omni plugin | AgileX CAN SDK (`can0`) | Identical `/cmd_vel` & Odometry API |
| Arm Control | `joint_trajectory_controller` | Piper CAN SDK (`can1`) | Identical JointTrajectory topic interface |
| 3D LiDAR | `ros_gz_sim` LiDAR Sensor | Livox Mid-360 Ethernet Driver | PointCloud2 & LaserScan topics |
| RGB-D Vision | `ros_gz_sim` Depth Camera | RealSense D435i USB Driver | sensor_msgs/Image (RGB + 16UC1 Depth) |
| TF Tree | Robot State Publisher | Robot State Publisher | Exact identical URDF / Xacro source |

## 2. Zero Fabrication Policy
All hardware scripts (`check_hardware.sh`, `run_real.sh`) check for physical CAN interfaces and hardware USB devices. If real hardware is absent, the system explicitly reports `[BLOCKED]` and falls back cleanly to simulation.
