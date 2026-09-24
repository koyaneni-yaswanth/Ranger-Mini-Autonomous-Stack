# Modular Robot Architecture — Ranger Mini AMR & Mobile Manipulator

This document defines the unified, fully decoupled architecture separating the **Ranger Mini Autonomous Mobile Robot (AMR)** from optional attachable modules (e.g., AgileX Piper 6-DOF Manipulator or Custom End-Effector Systems).

---

## 1. System Architecture Diagram

```text
                               +----------------------------+
                               |     MISSION ORCHESTRATION  |
                               | (master_mission_orchestrator|
                               +--------------+-------------+
                                              |
                                              | /manipulator/status & /capabilities
                                              v
                              +-------------------------------+
                              |   MANIPULATOR MANAGER NODE    |
                              |  (Dynamic Capability Registry)|
                              +---------------+---------------+
                                              |
               ===============================+===============================
               |                                                             |
               v                                                             v
+-------------------------------+                             +-------------------------------+
|      CORE AMR PLATFORM        |                             |     OPTIONAL MANIPULATOR      |
|  (Stand-alone Mobile Base)    |                             |      (Attachable Module)      |
+-------------------------------+                             +-------------------------------+
| • 4WIS Steering Kinematics    |                             | • AgileX Piper 6-DOF Arm      |
| • Nav2 Navigation Stack       |                             | • Parallel Jaw Gripper        |
| • SLAM Toolbox Mapping        |                             | • MoveIt 2 Motion Planning    |
| • Livox LiDAR 3D Perception   |                             | • Trajectory Controllers      |
| • RealSense D435i / YOLO      |                             | • Dedicated CAN Bus (can0)    |
| • Joint State Broadcaster     |                             | • Conditional URDF Inclusion  |
| • Universal Mechanical Plate  |                             | • Zero-Leakage AMR Reversion  |
+-------------------------------+                             +-------------------------------+
               |                                                             |
               +------------------------------+------------------------------+
                                              |
                                              v
                              +-------------------------------+
                              |    STANDARDIZED MOUNT PLATE   |
                              |      `manipulator_mount`      |
                              | (x: 0.15m, y: 0.0m, z: 0.01m) |
                              +-------------------------------+
```

---

## 2. Mechanical Interface Specification

The standardized mechanical interface allows tool-free or rapid 4-bolt payload attachment without disassembling chassis components or disturbing base perception sensors.

### 2.1 Mounting Geometry & Dimensions
- **Reference Frame:** `manipulator_mount` rigidly coupled to `top_deck_link`
- **Offset relative to base footprint:**
  - `x = +0.150 m` (forward biased to maximize forward reach)
  - `y =  0.000 m` (laterally centered)
  - `z = +0.271 m` (deck plate surface plane)
- **Bolt Pattern:** Standardized 4x M5 threaded pattern on a 60 mm x 60 mm pitch, compatible with ISO 9409-1-50-4-M6 adapter plates.
- **Top Platform Dimensions:** 420 mm (L) x 340 mm (W) anodized aircraft-grade aluminum (6061-T6), 5 mm thickness.

### 2.2 Payload & Center of Gravity (COG) Limits
| Parameter | Standalone AMR Mode | Piper Manipulator Mode | Safety Margin |
|---|---|---|---|
| **Max Payload Capacity** | 50.0 kg | 50.0 kg (Total gross) | 1.8x Design Factor |
| **Module Arm Mass** | 0.0 kg | 4.2 kg | Nominal |
| **Max Manipulator Payload** | N/A | 1.5 kg (at max reach) | 1.5x Dynamic Margin |
| **Usable Deck Payload Remaining**| 50.0 kg | 44.3 kg | Safe Transit Load |
| **Nominal Base Mass** | 25.0 kg | 29.2 kg (with arm) | Nominal |
| **COG Height ($Z_{cg}$)** | 0.125 m | 0.182 m (arm stowed) | Tip-over stable <= 35 deg |

---

## 3. Electrical Interface Specification

### 3.1 Power Supply
- **Input Supply:** Direct 24V DC unregulated bus from robot BMS (21.0V minimum discharged, 29.4V maximum float).
- **Connector Type:** High-current Amass XT30 or XT60 with IP65 silicone weather boot.
- **Current Requirements:**
  - Piper Standby / Logic: 24V @ 0.5A (12 W)
  - Piper Operational Nominal: 24V @ 3.5A (84 W)
  - Piper Peak Joint Stall: 24V @ 10.0A (240 W, limited to 500 ms)
- **Protection:** 15A inline automotive blade fuse + transient voltage suppressor (TVS) diode (SMBJ28A).

### 3.2 Emergency Stop (E-Stop) Integration
- The robot chassis is equipped with an ISO 13850 certified normally-closed (NC) dual-channel safety circuit.
- The manipulator power circuit is routed through a secondary safety contactor coil.
- **Safety Interlock Behavior:**
  - E-Stop Pressed: Instantly de-energizes the 24V power to all manipulator actuator coils and base motor drives.
  - Safe Recovery: E-Stop release does NOT automatically re-energize joints; software arm re-homing is strictly required.

---

## 4. Communication Interface Specification

### 4.1 CAN Bus Topology
- **Standard Protocol:** CAN 2.0B active at 1.0 Mbps baud rate.
- **Channel Assignment:** Dedicated socketcan interface (`can0` for base + arm or dedicated `can1`).
- **CAN ID Allocation Table:**
  | Node / Device | CAN ID (Hex) | Direction | Description |
  |---|---|---|---|
  | **Ranger Base Motion Cmd** | `0x111` | Host -> Base | Linear/Angular velocities |
  | **Ranger Base Status** | `0x211` | Base -> Host | Base state & fault flags |
  | **Ranger Base Odometry** | `0x221` | Base -> Host | Motor encoders & wheel speeds|
  | **Ranger BMS Telemetry** | `0x311` | Base -> Host | Battery voltage, current, SOC |
  | **Piper Joint 1 Cmd/Fbk** | `0x151` / `0x251` | Bi-directional | Base rotation joint |
  | **Piper Joint 2 Cmd/Fbk** | `0x152` / `0x252` | Bi-directional | Shoulder pitch joint |
  | **Piper Joint 3 Cmd/Fbk** | `0x153` / `0x253` | Bi-directional | Elbow pitch joint |
  | **Piper Joint 4 Cmd/Fbk** | `0x154` / `0x254` | Bi-directional | Wrist roll joint |
  | **Piper Joint 5 Cmd/Fbk** | `0x155` / `0x255` | Bi-directional | Wrist pitch joint |
  | **Piper Joint 6 Cmd/Fbk** | `0x156` / `0x256` | Bi-directional | Wrist roll 2 / yaw joint |
  | **Piper Gripper** | `0x157` / `0x257` | Bi-directional | Parallel jaw position & torque|

---

## 5. Software Interface & State Parity Matrix

### 5.1 Transform Tree (TF) Comparison
```text
[Base-Only Mode]
odom
 └── base_footprint
      └── base_link
           ├── fl_steering_link -> fl_wheel_link
           ├── fr_steering_link -> fr_wheel_link
           ├── rl_steering_link -> rl_wheel_link
           ├── rr_steering_link -> rr_wheel_link
           ├── livox_frame
           ├── camera_link -> camera_optical_frame
           ├── imu_link
           └── top_deck_link
                └── manipulator_mount  <-- Empty mount terminal plate

[Piper Manipulator Mode]
odom
 └── base_footprint
      └── ...
           └── manipulator_mount
                └── piper_base_link
                     └── piper_link1
                          └── piper_link2
                               └── piper_link3
                                    └── piper_link4
                                         └── piper_link5
                                              └── piper_link6
                                                   └── piper_gripper_base
                                                        ├── piper_finger_left
                                                        └── piper_finger_right
```

### 5.2 Active Controller & Topic Parity
| Component | Base-Only Mode (`manipulator:=false`) | Piper Mode (`manipulator:=true`) |
|---|---|---|
| **ros2_control Controllers** | • `joint_state_broadcaster`<br>• `steering_controller`<br>• `traction_controller` | • `joint_state_broadcaster`<br>• `steering_controller`<br>• `traction_controller`<br>• `piper_arm_controller` |
| **MoveIt Nodes** | NONE (`move_group` inactive) | `move_group` active with Piper SRDF |
| **`/manipulator/status`** | `{"enabled": false, "type": "none"}` | `{"enabled": true, "type": "piper", "ready": true}` |
| **`/manipulator/capabilities`**| `can_pick: false`, `can_place: false` | `can_pick: true`, `can_place: true`, `can_move_arm: true` |
| **Trajectory Topics** | NONE | `/piper_arm_controller/joint_trajectory` |
