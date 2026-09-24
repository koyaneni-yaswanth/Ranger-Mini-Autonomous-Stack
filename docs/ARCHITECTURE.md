# Autonomous Mobile Manipulator System Architecture

## 1. Executive Summary
The Ranger Mini Autonomous Mobile Manipulator is an industrial-grade robotics platform combining an omnidirectional mobile base (AgileX Ranger Mini v2), an optional modular 6-DOF robotic arm (Piper), an elevated multi-modal perception mast (Livox Mid-360 LiDAR + Intel RealSense D435i), and an AI-driven task execution engine running on ROS 2 Lyrical and Gazebo Harmonic.

```text
                               +-----------------------------+
                               |     Natural Language Task   |
                               |    "Find red object..."     |
                               +--------------+--------------+
                                              |
                                              v
                               +-----------------------------+
                               |     AI Task Interpreter     |
                               |  - Natural Language Parsing |
                               |  - JSON Schema Validation   |
                               |  - Safety Policy Enforcement|
                               +--------------+--------------+
                                              | Validated Task Schema
                                              v
                               +-----------------------------+
                               | Autonomous Task Orchestrator|
                               |   (17-State Execution FSM)  |
                               +-------+---------------+-----+
                                       |               |
               +-----------------------+               +-----------------------+
               v                                                               v
+-----------------------------+                                 +-----------------------------+
|     Nav2 Navigation Stack   |                                 |    Piper MoveIt 2 / ros_ctl |
|  - MPPI / Regulated Pure P. |                                 |  - 6-DOF Joint Trajectory   |
|  - Costmaps / Obstacle Cl.  |                                 |  - Grasp Verification       |
+--------------+--------------+                                 +--------------+--------------+
               |                                                               |
               +-----------------------+               +-----------------------+
                                       v               v
                               +-----------------------------+
                               |     Chassis & Arm HW / Sim  |
                               |  - AgileX CAN Bus (can0)    |
                               |  - Piper CAN Bus (can1)     |
                               |  - Top Deck Enclosure       |
                               +-----------------------------+
```

## 2. Coordinate Frame Architecture (REP-105 & REP-120)
- `map`: Global earth-fixed reference frame published by SLAM Toolbox / AMCL.
- `odom`: Continuous wheel-inertial odometry frame published by `ranger_base_node` or Gazebo plugin.
- `base_footprint`: 2D projection of robot onto the ground surface directly below the chassis center.
- `base_link`: Center of structural lower chassis.
- `body_enclosure_link`: Protective enclosure housing battery, drives, and compute.
- `top_deck_link`: 15mm 6061-T6 structural deck surface (`z = +0.27m`).
- `manipulator_mount`: Rigid reinforced pedestal at `(0.15, 0.0, 0.015)`.
- `piper_base_link`: Base joint of the 6-DOF arm attached directly to `manipulator_mount`.
- `sensor_mast_link`: Dual-column aluminum mast rising 0.35m from rear deck `(-0.18, 0.0, 0.015)`.
- `lidar_link`: Livox Mid-360 mounting bracket at mast summit (`z = 0.356m`, 360° unobstructed horizon).
- `camera_link`: RealSense D435i bracket at `z = 0.24m`, pitched 15° forward-down (`0.2618 rad`) targeting manipulation field.

## 3. Communication Topology & Subsystems
- **DDS Middleware**: FastDDS (`rmw_fastrtps_cpp`), Domain ID `10`.
- **Command Authority Flow**: AI task requests -> Task Schema (`task_schema.json`) -> Orchestrator FSM -> Nav2 / Trajectory Controller -> Motors. Zero direct motor or twist commands are permitted from AI prompts.
