# NVIDIA Isaac Sim Digital Twin

## 1. USD Digital Twin
The platform provides a USD digital twin of the Ranger Mini v2 + Piper 6-DOF manipulator matching physical masses, inertias, joint limits, and sensor brackets.

## 2. Omniverse ROS 2 Bridge
Configured via `config/isaac_sim_bridge.yaml`:
- Synchronized simulation clock (`/clock` @ 60 Hz).
- Bidirectional joint states & trajectory commands (`/joint_states`, `/piper_arm_controller/joint_trajectory`).
- Synthetic perception streams (`/camera`, `/camera/depth_image`, `/lidar/points`).
