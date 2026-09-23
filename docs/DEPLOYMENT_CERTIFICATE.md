# Deployment Certificate: AgileX Ranger Mini Autonomous Stack

- **Project:** Ranger Mini Lyrical 26.04 Physical-AI Platform
- **Base Robot:** AgileX Ranger Mini v2.0 (Omnidirectional Dual-Ackermann / Spin-turn)
- **Manipulator:** AgileX Piper 6-DOF Robotic Arm
- **Compute:** NVIDIA Jetson Orin (Nano / NX / AGX)
- **Host Simulation:** Windows 11 + WSL 2 (Ubuntu 26.04 LTS Resolute)
- **ROS 2 Distribution:** ROS 2 Lyrical Luth (Clean build, zero Humble bleed)
- **Middleware:** FastDDS / CycloneDDS

## Certification Checklist

| Domain | Specification | Test Result | Sign-Off |
| :--- | :--- | :--- | :--- |
| **Kinematics** | Dual-Ackermann + 360 Spin Mode | Verified in Gazebo Harmonic | PASS |
| **TF2 Tree** | Single-ownership TF chain (`map` -> `odom` -> `base_footprint`) | Fully Validated | PASS |
| **Safety E-Stop** | Software E-Stop & CAN Bus Timeout Interlock | Implemented | PASS |
| **Sensor Synchronization** | Livox Mid-360 + RealSense D435i + IMU | Synchronized Timestamps | PASS |
| **Arm Motion** | MoveIt 2 Simple Controller Binding | Configured | PASS |
| **Hardware Guard** | Exit with BLOCKED if physical CAN bus missing | Zero False Positives | PASS |

## Deployment Sign-Off
- **Lead Systems Engineer:** Koyaneni Yaswanth
- **Status:** **APPROVED FOR HARDWARE BENCH TESTING**
