# AgileX Ranger Mini Autonomous Stack: Master User Manual
## Complete Guide: From High-Fidelity Simulation to Real Hardware Deployment

---

## 1. System Overview & Architecture

This platform provides an end-to-end autonomous mobile manipulation system supporting:
- **Base Platform:** AgileX Ranger Mini v2.0 (Dual-Ackermann, Spin-turn, Crab-steering)
- **Manipulator:** AgileX Piper 6-DOF Robotic Arm with Parallel Gripper
- **Logistics Companion:** NERO Differential-Drive AMR
- **Sensor Suite:** Livox Mid-360 3D LiDAR, Intel RealSense D435i RGB-D Camera, Hardware IMU
- **Target OS:** Ubuntu 26.04 LTS (Resolute) / Ubuntu 22.04 LTS (JetPack 5/6)
- **ROS Version:** ROS 2 Lyrical Luth (Simulation) / ROS 2 Humble/Jazzy (Jetson Orin)
- **Sim-to-Real Engine:** Gazebo Harmonic (gz-sim 10.5) with Hardware Abstraction Layer

```
+-------------------------------------------------------------------------------+
|                           USER APPLICATION / MISSION                          |
|         ranger_missions | BT Navigator | Multi-Robot Fleet Dispatcher        |
+---------------------------------------+---------------------------------------+
                                        |
+---------------------------------------v---------------------------------------+
|                         AUTONOMY & CONTROL LAYER                              |
|   - Navigation: Nav2 (SmacPlannerHybrid + DWB Controller / MPPI)              |
|   - Mapping: SLAM Toolbox (Online Async 2D) / Fast-LIO 3D Odometry            |
|   - Manipulation: MoveIt 2 (OMPL + KDL Kinematics + Simple Controller Mgr)    |
|   - Perception: Pointcloud-to-Laserscan + OpenCV/TensorRT Object Detection   |
+---------------------------------------+---------------------------------------+
                                        |
               +------------------------+------------------------+
               | (use_sim_time: true)                            | (use_sim_time: false)
               v                                                 v
+-----------------------------+                   +-----------------------------+
|      SIMULATION STACK       |                   |    REAL HARDWARE DRIVERS    |
|  - Gazebo Harmonic 10.5     |                   |  - AgileX ugv_sdk (can0)    |
|  - gz_ros2_control          |                   |  - piper_bringup CAN driver |
|  - gz-sim-odometry-pub      |                   |  - livox_ros_driver2 (UDP)  |
|  - ros_gz_bridge            |                   |  - realsense2_camera (USB3) |
+-----------------------------+                   +-----------------------------+
```

---

## PART I: SIMULATION TESTING WORKFLOW

Before connecting to physical hardware, every single subsystem must be validated in Gazebo simulation.

### Step 1.1: System Health & Pre-Flight Verification
Open your WSL 2 terminal and run:
```bash
cd ~/ranger_mini_lyrical_2604_project
make health
```
**Expected Output:**
- `[OK] ROS 2 Lyrical installation present at /opt/ros/lyrical.`
- `[OK] NVIDIA GPU detected via WSL GPU-PV.`
- `[OK] Lyrical workspace built and ready.`
- `[OK] Display server active: :0.`

Run the automated test engine:
```bash
make test
```
All system, environment, network multicast, and ROS integrity tests will run automatically. Note that the hardware audit will truthfully report `[BLOCKED] Physical robot hardware not connected (can0 not found)`—which is normal and expected in simulation mode.

---

### Step 1.2: Launch Full Autonomous Simulation
To start Gazebo Harmonic, the Ranger Mini URDF, sensor bridges, Nav2, SLAM, and the perception pipeline in one command:
```bash
make sim
```
Or launch headlessly with RViz:
```bash
source ~/ranger_mini_lyrical_2604_project/env/source_lyrical.sh
ros2 launch ranger_bringup sim.launch.py headless:=false
```

**What Starts:**
1. **Gazebo Harmonic**: Spawns the `warehouse.sdf` industrial environment.
2. **Robot Entity**: Spawns the Ranger Mini with Piper arm at `(x=0, y=0, z=0.2)`.
3. **Sensor Bridges**:
   - `/clock` -> ROS 2 simulation clock
   - `/odometry` -> `/odom` (50 Hz wheel odometry)
   - `/lidar/points` -> PointCloud2 (10 Hz Livox simulation)
   - `/camera` -> RGB image stream (30 Hz)
   - `/imu` -> 6-axis IMU stream (100 Hz)
4. **Perception**: `pointcloud_to_laserscan_node` converts 3D points to 2D `/scan` in real time.

---

### Step 1.3: Teleoperation & Kinematic Steering Verification
Open a new terminal to command the robot wheels:
```bash
source ~/ranger_mini_lyrical_2604_project/env/source_lyrical.sh
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel
```

**Controls:**
- `i` / `,`: Drive forward / reverse
- `j` / `l`: Turn left / right (Dual-Ackermann steering)
- `u` / `o`: Steer and drive along curves
- `k`: Emergency Stop (zero velocity)

**Verify in another terminal:**
```bash
# Check odometry updates as robot drives
ros2 topic echo /odom --field pose.pose.position
```

---

### Step 1.4: SLAM 2D Warehouse Mapping
In simulation, you can build a 2D occupancy grid map of the warehouse environment:
```bash
make slam
```
1. Drive the robot around the warehouse using the teleoperation terminal.
2. Open RViz2 and observe the `/map` topic expanding.
3. Once the environment is fully explored, save the map:
```bash
ros2 run nav2_map_server map_saver_cli -f ~/ranger_mini_lyrical_2604_project/maps/warehouse_map
```

---

### Step 1.5: Nav2 Autonomous Navigation & Waypoint Following
To test autonomous navigation with obstacle avoidance:
```bash
make nav
```
1. In RViz2, select the **2D Goal Pose** tool in the top toolbar.
2. Click and drag an arrow anywhere in the warehouse to specify target position and orientation.
3. Observe:
   - Nav2 Global Planner generates a smooth path avoiding warehouse shelves.
   - Costmaps inflate obstacles based on the LiDAR scan.
   - The robot maneuvers autonomously to the target waypoint.

---

### Step 1.6: MoveIt 2 Manipulator Planning (Piper 6-DOF Arm)
To test the 6-DOF robotic arm trajectory planner:
```bash
source ~/ranger_mini_lyrical_2604_project/env/source_lyrical.sh
ros2 launch ranger_manipulation manipulation.launch.py
```
1. In the MoveIt Motion Planning display panel, select the `arm` planning group.
2. Drag the end-effector interactive marker to a desired 3D pose.
3. Click **Plan and Execute**.
4. The arm smoothly executes collision-free trajectory interpolation.

---

### Step 1.7: Multi-Robot Fleet Simulation (Ranger Mini + NERO AMR)
To verify multi-agent fleet operations with isolated namespaces:
```bash
source ~/ranger_mini_lyrical_2604_project/env/source_lyrical.sh
ros2 launch ranger_bringup multi_robot.launch.py
```
**Verify Namespace Isolation:**
```bash
ros2 topic list | grep -E "ranger|nero"
```
You will see:
- `/ranger/cmd_vel`, `/ranger/odom`, `/ranger/lidar/points`
- `/nero/cmd_vel`, `/nero/odom`, `/nero/scan`
Each robot has its own TF frame prefix (`ranger/` and `nero/`), completely eliminating TF conflicts.

---

## PART II: HARDWARE WIRING & BENCH SETUP

Once simulation testing passes, prepare the physical hardware platform.

```
       +-----------------------------------------------------------+
       |             NVIDIA JETSON ORIN / WORKSTATION              |
       |  - Eth0: 192.168.1.100 (LiDAR Host Interface)             |
       |  - USB Port A: USB-to-CAN Adapter (can0 @ 500,000 bps)     |
       |  - USB Port B: Intel RealSense D435i (USB 3.0 Type-C)     |
       +--------------+------------------+------------------+------+
                      |                  |                  |
           CAN Bus    |       CAN Bus    |       Ethernet   |   USB 3.0
           (500k)     |       (500k)     |                  |
                      v                  v                  v      v
              +---------------+  +---------------+   +------------+ +-------------+
              | AgileX Ranger |  | AgileX Piper  |   | Livox      | | Intel       |
              | Mini v2.0 Base|  | 6-DOF Arm     |   | Mid-360    | | RealSense   |
              | Driver Board  |  | Driver Box    |   | LiDAR      | | D435i       |
              +---------------+  +---------------+   +------------+ +-------------+
```

### Step 2.1: CAN Bus Cabling & Pinout
The AgileX Ranger Mini communicates via high-speed ISO 11898-2 CAN 2.0B at **500 kbps**.

**AgileX Aviation Connector Pinout:**
| Pin Number | Function | Wire Color | Connect To |
| :--- | :--- | :--- | :--- |
| **Pin 1** | `CAN_H` | Yellow / White | CAN Adapter `CAN_H` |
| **Pin 2** | `CAN_L` | Blue / Green | CAN Adapter `CAN_L` |
| **Pin 3** | `GND` | Black | CAN Adapter `GND` (Shield) |
| **Pin 4** | `VCC` | Red | Reserved / Unconnected |

> [!IMPORTANT]
> Ensure a **120-ohm termination resistor** is present between `CAN_H` and `CAN_L` at both physical ends of the CAN bus line. Most USB-to-CAN dongles (candleLight, Innomaker) have a toggle jumper for this.

---

### Step 2.2: USB-to-CAN Adapter Setup
Connect your USB-to-CAN adapter (such as CANable, InnoMaker, or Waveshare USB-CAN) to the Jetson/workstation USB port:
```bash
# Check if kernel recognized the adapter
dmesg | grep -i -E "can|gs_usb|candlelight|ch341"
```
Bring up the interface:
```bash
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up
```
Verify the interface state is `UP`:
```bash
ip -details link show can0
```

---

### Step 2.3: Livox Mid-360 LiDAR Ethernet Configuration
The Livox Mid-360 uses UDP broadcast packets over Ethernet:
- **Default LiDAR IP:** `192.168.1.102` (or last digits of MAC address)
- **Host Jetson Static IP:** Must be set to `192.168.1.100` with netmask `255.255.255.0`

Configure static IP on the host interface (`eth0`):
```bash
sudo ip addr add 192.168.1.100/24 dev eth0
sudo ip link set eth0 up
```
Verify network ping to LiDAR:
```bash
ping -c 3 192.168.1.102
```

---

### Step 2.4: Intel RealSense D435i USB 3.0 Verification
Connect the camera directly to a high-speed **USB 3.0 (Blue or Type-C)** port.
```bash
lsusb -d 8086:
```
**Expected Output:** Device ID `8086:0b3a` or `8086:0b07` (Intel RealSense).  
Confirm video endpoints exist:
```bash
ls -l /dev/video*
```

---

### Step 2.5: Safety Pre-Flight Bench Setup (Jack Stand Test)
> [!CAUTION]
> **MANDATORY SAFETY PROCEDURE BEFORE FIRST REAL POWER-ON:**  
> Place the robot on secure jack stands or a wooden block so all 4 wheels are completely elevated off the ground. Never turn on real hardware for the first time while it rests on the floor!

1. Confirm the red physical **Emergency Stop mushroom button** is fully functional and easily accessible.
2. Confirm the wireless remote controller is switched ON with SWB in the manual/neutral position.

---

## PART III: REAL HARDWARE EXECUTION

### Step 3.1: Run the 10-Level Hardware Health Audit
In your project directory, execute:
```bash
make hw-health
```
The script will perform a real-time audit:
- `[LVL 1]` Host Architecture / Jetson detection
- `[LVL 2]` SocketCAN `can0` link state (`UP @ 500k`)
- `[LVL 3]` Ranger Mini CAN telemetry probing
- `[LVL 4]` Piper arm CAN heartbeat
- `[LVL 5]` Livox Mid-360 Ethernet reachability
- `[LVL 6]` RealSense D435i USB 3.0 device detection
- `[LVL 7]` Hardware IMU interface
- `[LVL 8]` BMS battery telemetry
- `[LVL 9]` E-Stop switch verification
- `[LVL 10]` ROS 2 environment integrity

**Only proceed to `make real` when all essential levels report `PASS`.**

---

### Step 3.2: Launch Real Robot Hardware
```bash
make real
```
This runs `scripts/run_real.sh`, which performs pre-flight checks and launches:
```bash
ros2 launch ranger_bringup hardware.launch.py can_interface:=can0
```

**Active Real Hardware Topics:**
- `/odom`: Real wheel encoder odometry published by `ranger_base_node` at 50 Hz.
- `/cmd_vel`: Subscribed by `ranger_base_node` to drive physical motor controllers.
- `/lidar/points`: Published by `livox_ros_driver2`.
- `/camera/color/image_raw` & `/camera/depth/image_raw`: Published by `realsense2_camera`.

---

### Step 3.3: Wheels-Off-Ground Teleoperation Sanity Check
In a second terminal:
```bash
source ~/ranger_mini_lyrical_2604_project/env/source_lyrical.sh
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
1. Gently tap `i` to send a small forward velocity (+0.1 m/s).
2. **Verify Wheel Direction:** All 4 wheels must rotate forward.
3. Tap `j` to steer left. All 4 steering pivots must adjust angles in Ackermann geometry.
4. Hit `Space` to stop. Wheels must immediately halt.
5. Hit the physical red **E-Stop button**. The robot base must immediately disconnect motor power and stop responding to `/cmd_vel`.

---

### Step 3.4: Real Hardware SLAM Mapping
Once wheels-off-ground validation is successful, place the robot on an open, flat floor with at least 3 meters of clearance on all sides:
```bash
source ~/ranger_mini_lyrical_2604_project/env/source_lyrical.sh
ros2 launch ranger_slam mapping.launch.py use_sim_time:=false
```
1. Drive slowly using teleoperation (max 0.2 m/s).
2. SLAM Toolbox fuses LiDAR points and wheel odometry into a real-time `/map`.
3. Save the map when complete:
```bash
ros2 run nav2_map_server map_saver_cli -f ~/ranger_mini_lyrical_2604_project/maps/real_facility_map
```

---

### Step 3.5: Real Autonomous Navigation (Nav2)
```bash
source ~/ranger_mini_lyrical_2604_project/env/source_lyrical.sh
ros2 launch ranger_navigation navigation.launch.py use_sim_time:=false map:=$HOME/ranger_mini_lyrical_2604_project/maps/real_facility_map.yaml
```
1. Set Initial Pose estimate in RViz2 using the **2D Pose Estimate** button.
2. Send navigation goals using **2D Goal Pose**.
3. Always keep the remote controller in hand with your finger on the manual override switch during autonomous motion.

---

## PART IV: TROUBLESHOOTING & RECOVERY MATRIX

| Issue / Error | Root Cause | Solution |
| :--- | :--- | :--- |
| `[BLOCKED] can0 not found` | USB-to-CAN adapter unplugged or interface down | Run `sudo ip link set can0 type can bitrate 500000 && sudo ip link set can0 up` |
| `can0: write: No buffer space available` | CAN bus cable disconnected or wrong baud rate | Check physical aviation connector wiring; verify 120-ohm terminator |
| LiDAR points missing in RViz | Network subnet mismatch | Confirm host IP is `192.168.1.100` and ping `192.168.1.102` succeeds |
| Camera image missing | Camera plugged into USB 2.0 port | Move RealSense cable to a USB 3.0 (Blue or Type-C) port |
| Robot turns in reverse direction | Steering kinematic signs reversed | Check `config/calibration/wheel_calibration.yaml` |
| DDS node communication drops | Domain ID conflict on shared LAN | Set unique `export ROS_DOMAIN_ID=10` in `source_lyrical.sh` |

---
*AgileX Ranger Mini Production Autonomous Robotics Platform — Koyaneni Yaswanth*
