# Ranger Mini Autonomous Stack — System Architecture

```text
                            APPLICATION LAYER
       ┌─────────────────────────────────────────────────────────┐
       │     Navigation (Nav2) │ SLAM │ Perception │ Missions     │
       └────────────────────────────┬────────────────────────────┘
                                    │ /cmd_vel, /odom, /scan, /camera, /imu, /tf
                       COMMON ROS 2 ROBOT INTERFACE
       ┌────────────────────────────┴────────────────────────────┐
       │                                                         │
  SIMULATION BACKEND                                     REAL HARDWARE BACKEND
┌───────────────────────┐                               ┌──────────────────────┐
│ Gazebo Sim (Fortress) │                               │ AgileX SocketCAN     │
│ ROS-GZ Bridge         │                               │ Livox MID-360 LiDAR  │
│ Virtual Sensors       │                               │ Intel RealSense D435 │
│ Simulated Kinematics  │                               │ 9-DOF Hardware IMU   │
└───────────────────────┘                               └──────────────────────┘
```
