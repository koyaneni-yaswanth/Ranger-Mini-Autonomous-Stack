# Simulation-to-Real Transfer & Parity

## 1. Parity Matrix
| Component | Gazebo Harmonic | Isaac Sim 4.x | Real Jetson Orin |
| :--- | :--- | :--- | :--- |
| Base Control | `gz_ros2_control` | Omniverse ROS 2 Bridge | AgileX CAN SDK (`can0`) |
| Arm Control | `joint_trajectory_controller` | Omniverse Articulation | Piper CAN SDK (`can1`) |
| Perception | Synthetic RGB-D & LiDAR | RTX Raytraced USD Sensors | RealSense D435i & Livox Mid-360 |
| Interfaces | Identical `/cmd_vel`, `/odom`, `/joint_trajectory`, `/camera/*`, `/lidar/points` topics |

## 2. Zero-Fabrication Enforcement
Hardware validation scripts verify physical CAN bus interfaces and USB sensors. If unattached, scripts report `[BLOCKED]` and fall back cleanly to simulation.
