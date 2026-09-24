# Final Engineering Project Report: Autonomous Mobile Manipulator

## 1. Executive Summary
This project delivers a complete, modular, simulation-to-real autonomous mobile manipulator built upon the AgileX Ranger Mini v2 chassis, Piper 6-DOF robotic arm, elevated sensor mast, and an AI task execution engine under ROS 2 Lyrical.

## 2. Milestone Deliverables
- **Gate 1 & 2 (Mechanical & Enclosure)**: Enclosed three-tier chassis, elevated sensor mast (Livox Mid-360 at 0.35m, RealSense D435i at 15° pitch down), universal 4x M5 mounting pedestal, and emergency stop bezel.
- **Gate 3 (Modularity)**: Full operational parity between Base-Only (`manipulator:=false`) and Manipulator (`manipulator:=true`) configurations without any dangling links or broken dependencies.
- **Gate 4 (AI Task Interpretation)**: Natural language parsing into validated JSON schemas, enforcing zero direct motor control (Safety Rule 13).
- **Gate 5 (Mobile Manipulation & Grasping)**: 17-state autonomous execution machine with pinhole 3D backprojection and multi-stage grasp verification (`SUCCESS`, `FAILED`, `UNCERTAIN`).
- **Gate 6 (Sim-to-Real & Parity)**: Hardware detection scripts, Jetson Orin deployment toolchain, and automated testing suite.

## 3. Verification & Compliance
All unit tests, integration tests, and platform health checks pass with 100% success rate on the target Ubuntu 26.04 LTS / ROS 2 Lyrical environment.
