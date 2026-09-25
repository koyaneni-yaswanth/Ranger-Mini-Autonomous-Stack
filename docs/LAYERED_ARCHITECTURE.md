# Layered Autonomous Mobile Manipulation Architecture

## 1. System Architecture Hierarchy

```text
                    USER TASK
                       │
                       ▼
               AI TASK PLANNER
                       │
                       ▼
              TASK / SKILL LAYER
                       │
          ┌────────────┴────────────┐
          │                         │
       NAVIGATION               MANIPULATION
          │                         │
         Nav2                    MoveIt 2
          │                         │
          └────────────┬────────────┘
                       │
                 ROBOT ABSTRACTION
                       │
        ┌──────────────┼──────────────┐
        │              │              │
     Gazebo        Isaac Sim      Real Robot
        │              │              │
      Test        Train/Validate     Jetson
                       │
                SIM → REAL
```

---

## 2. Layer-by-Layer Architectural Breakdown

### Layer 1: User Task (Human-Robot Interface)
- **Role**: Entrypoint for operator intentions and high-level mission requests.
- **Interface**:
  - Interactive CLI (`make cli` / `scripts/interactive_task_cli.py`)
  - ROS 2 Topic: `/ai/task_command` (`std_msgs/msg/String`)
- **Canonical Tasks**:
  * `"Find the red object, pick it up, and place it at the target station"`
  * `"Pick up the blue box and place it in the assembly bin"`
  * `"Inspect the inspection table"`
  * `"Dock at home dock"`

---

### Layer 2: AI Task Planner
- **Implementation**: `ranger_missions.ai_task_interpreter`
- **Role**: Synthesizes unstructured human language into deterministic, typed, and safety-verified execution plans.
- **Components**:
  1. **Natural Language Parser**: Extracts actions (`pick_and_place`, `inspect`, `dock`), target objects (`cube`, `box`, `bottle`), colors, and destination stations.
  2. **Schema Validator**: Enforces strict conformance to `config/task_schema.json` via JSONSchema validation.
  3. **Safety Policy Engine (Rule 13)**: Strictly rejects direct motor, velocity (`/cmd_vel`), or raw joint angle commands from external prompt injections.
  4. **Capability Gating**: Checks `/manipulator/status`. Rejects arm manipulation requests when robot is in Base-Only mode (`manipulator:=false`).

---

### Layer 3: Task / Skill Layer
- **Implementation**: `ranger_missions.skill_library` & `ranger_missions.autonomous_task_orchestrator`
- **Role**: Bridges high-level symbolic plans to composable, reusable, atomic robot capabilities.
- **Skill Library**:
  * `LocateObjectSkill`: Subscribes to `/vision/detected_objects` and queries `SemanticWorldModel` for 3D coordinates.
  * `ApproachTargetSkill`: Closed-loop visual standoff approach to 0.48m front offset.
  * `PickSkill`: Coordinated 6-DOF MoveIt 2 arm trajectory execution (`PRE_GRASP` -> `GRASP` -> `LIFT`).
  * `VerifyGraspSkill`: Multi-modal validation of finger gap (0.058m), motor torque (1.25 Nm), and depth camera occlusion (`SUCCESS` / `FAILED` / `UNCERTAIN`).
  * `TransportSkill`: Stows arm in compact low-inertia configuration for base transit.
  * `NavigateToStationSkill`: Dispatches Nav2 waypoint navigation to target station.
  * `PlaceSkill`: Controlled descent and release on workstation surface.
  * `VerifyPlaceSkill`: End-effector clear confirmation and retreat.
  * `DockSkill`: Returns arm to `HOME` and chassis to charging bay.

---

### Layer 4: Navigation (Nav2) & Manipulation (MoveIt 2)

#### Navigation Subsystem (Nav2)
- **Path Planning & Control**: MPPI / Regulated Pure Pursuit Controller (`controller_server`).
- **Costmaps**: 2D/3D Obstacle Inflation and Layered Footprint clearance (`0.35m`).
- **Safety Watchdog**: `collision_monitor` with footprint stopping polygons.
- **Behavior Server**: Recovery behaviors (Spin, Backup, Wait).

#### Manipulation Subsystem (MoveIt 2 & ros2_control)
- **Kinematic Solver**: KDL / Trac-IK inverse kinematics for Piper 6-DOF arm.
- **Joint Trajectory Controller**: `piper_arm_controller` executing smooth cubic-spline trajectories on `piper_joint1` through `piper_joint6`.
- **Grasp Evaluation**: Force/current feedback monitoring on gripper servo.

---

### Layer 5: Robot Abstraction (HAL)
- **Implementation**: `ranger_missions.robot_abstraction`
- **Role**: Hardware Abstraction Layer isolating all higher-level skill logic from the underlying execution runtime.
- **Standardized API**:
  * `send_base_velocity(vx, wz, vy)`: Hardware-clamped omnidirectional and differential drive.
  * `send_arm_pose(pose_name, duration_sec)`: Pre-validated 6-DOF joint trajectory commands.
  * `get_robot_map_pose()`: Global TF buffer lookup (`map -> base_link`).
  * `trigger_estop(engage)`: Centralized software and hardware E-Stop dispatch.
  * `get_manipulator_status()`: Dynamic detection of base-only vs arm configurations.

---

### Layer 6: Execution Backends (Sim-to-Real)

| Backend | Purpose | Environment / Interface | Hardware / Driver |
| :--- | :--- | :--- | :--- |
| **Gazebo Harmonic** | Fast functional testing, multi-node regression, CI/CD | `gz-sim` + `ros_gz_bridge` | Simulated ODE/Bullet physics, synthetic LiDAR/RGB-D |
| **NVIDIA Isaac Sim** | Photorealistic rendering, synthetic data generation, Isaac ROS | Omniverse USD + ROS 2 Bridge | PhysX 5 GPU acceleration, RTX raytracing |
| **Real Robot (Jetson Orin)** | Physical industrial production deployment | Ubuntu 22.04/24.04/26.04 + JetPack 6.x | AgileX CAN (`can0`), Piper CAN (`can1`), Livox Eth, RealSense USB3 |

---

## 3. Sim-to-Real Transfer & Parity Contract
1. **Identical Topic Topologies**: Higher-level software does not distinguish between Gazebo, Isaac Sim, or the real robot. `/cmd_vel`, `/joint_trajectory`, `/odom`, `/lidar/points`, and `/camera/*` use identical message types across all backends.
2. **Zero Fabrication Enforcement**: Hardware detection scripts (`check_hardware.sh`) verify physical CAN adapters and USB devices before running real robot routines, cleanly falling back to simulation if unattached.
3. **Safety Parity**: E-stop interlocks, velocity limits, and collision monitor footprints are enforced identically across simulation and physical hardware.
