# Ranger Mini Autonomous Stack — ROS 2 Lyrical Tutorials

Welcome to the hands-on tutorial suite for the **Ranger Mini Autonomous Stack** running on **ROS 2 Lyrical**. This tutorial series walks through the entire autonomy pipeline from low-level teleoperation and sensor validation to autonomous navigation and robotic manipulation.

---

## Tutorial Catalog

| Tutorial | Directory | Focus Area | Key Concepts |
| :--- | :--- | :--- | :--- |
| **01. Basic Teleoperation** | `01_basic_teleop` | Vehicle Dynamics & Control | Omnidirectional kinematics, Twist MUX, speed limits, safety watchdog |
| **02. Sensor Verification** | `02_sensor_verification` | Perception & State Estimation | LiDAR 360°, RealSense D435 RGB-D, IMU, TF2 verification |
| **03. Autonomous Navigation** | `03_autonomous_navigation` | Nav2 & Motion Planning | Costmap inflation, Regulated Pure Pursuit, waypoint sequencing, obstacle avoidance |
| **04. Manipulation & Pick-Place** | `04_manipulation_pick_place` | MoveIt 2 Mobile Manipulation | 6-DOF Piper arm kinematics, Cartesian trajectory execution, tabletop pick-and-place |

---

## Prerequisites & Environment Setup

Before running these tutorials, ensure your ROS 2 environment is sourced and the workspace is built:

```bash
# In ~/ranger_mini_lyrical_ws
source /opt/ros/$ROS_DISTRO/setup.bash
source ~/ranger_mini_lyrical_ws/install/setup.bash
```

---

## 1. Tutorial 01: Basic Teleoperation & Kinematics Control

Launch the simulation in a calibration arena and verify vehicle motion modes:

```bash
# Terminal 1: Launch simulation world with Ranger Mini
ros2 launch ranger_simulation simulation.launch.py world:=basic_test.sdf

# Terminal 2: Run teleoperation tutorial node
ros2 run tutorial_basic_teleop teleop_supervisor
```

### What it demonstrates:
- Steering kinematics validation for 4-wheel independent steering (4WIS) and skid steering.
- Command velocity multiplexing: prioritizes autonomy goals, manual teleoperation, and safety abort commands.
- Live verification of `/cmd_vel` output clamped to linear limits (1.5 m/s) and angular limits (1.0 rad/s).

---

## 2. Tutorial 02: Sensor Verification & Health Diagnostics

Verify that all onboard sensor pipelines and coordinate frames are functioning properly:

```bash
# Terminal 1: Launch simulation with all sensors enabled
ros2 launch ranger_simulation simulation.launch.py world:=warehouse.sdf

# Terminal 2: Run the automated sensor diagnostic verification
ros2 run tutorial_sensor_verification sensor_health_checker
```

### What it demonstrates:
- 2D/3D LiDAR scan rate validation on `/scan` (>= 10 Hz).
- RGB camera and Depth map stream validation on `/camera/image_raw` and `/camera/depth/image_raw`.
- IMU angular velocity and linear acceleration on `/imu/data`.
- Real-time TF tree integrity checking (`base_link` -> `laser_link`, `camera_link`, `imu_link`).

---

## 3. Tutorial 03: Autonomous Navigation & Obstacle Avoidance

Run autonomous waypoint navigation through dynamic and static obstacles in the warehouse:

```bash
# Terminal 1: Launch complete navigation stack with SLAM/AMCL
ros2 launch ranger_bringup full_system.launch.py world:=warehouse.sdf

# Terminal 2: Dispatch waypoint mission
ros2 run tutorial_autonomous_navigation waypoint_navigator
```

### What it demonstrates:
- Waypoint dispatch to Nav2 action server (`/navigate_to_pose`).
- Costmap clearance monitoring and dynamic replanning around obstacles.
- Continuous pose feedback and goal arrival tolerances (+/- 0.05 m).

---

## 4. Tutorial 04: Mobile Manipulation (MoveIt 2)

Execute arm trajectory planning and pick-and-place tasks with the 6-DOF Piper arm:

```bash
# Terminal 1: Launch manipulation simulation world
ros2 launch ranger_simulation simulation.launch.py world:=manipulation.sdf

# Terminal 2: Execute pick-and-place sequence
ros2 run tutorial_manipulation_pick_place pick_and_place_tutorial
```

### What it demonstrates:
- MoveIt 2 joint-space goal planning (Home, Ready, Pre-grasp, Grasp, Lift, Place).
- Cartesian path interpolation for collision-free end-effector approaches.
- Parallel-jaw gripper open/close control.
