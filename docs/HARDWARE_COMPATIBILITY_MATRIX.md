# Hardware Compatibility Matrix
## Autonomous Multi-Robot Platform: AgileX Ranger Mini + Piper + NERO

This matrix documents the verification status, interface requirements, and drivers across Simulation, NVIDIA Jetson Orin, and Real Physical Hardware.

| Subsystem / Component | Simulation (Gazebo Harmonic) | Jetson Orin (ARM64 / aarch64) | Physical Hardware | Required Driver / SDK | Integration Status | Notes / Blockers |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Mobile Base** (AgileX Ranger Mini v2) | **VERIFIED** (`gz_ros2_control` 4WIS) | **PENDING DRIVER BUILD** (ARM64) | **READY** (CAN bus 500k) | `ranger_base` + `ugv_sdk` (C++17) | **STATICALLY VERIFIED** | Requires `can0` interface active at 500,000 bps. |
| **Manipulator** (AgileX Piper 6-DOF) | **VERIFIED** (MoveIt 2 + `joint_trajectory_controller`) | **PENDING DRIVER BUILD** (ARM64) | **READY** (CAN bus 500k / 1M) | `piper_bringup` + `piper_sdk` | **STATICALLY VERIFIED** | Controlled via ROS 2 `FollowJointTrajectory`. |
| **End-Effector Gripper** | **VERIFIED** (Parallel Finger Joint) | **PENDING DRIVER BUILD** (ARM64) | **READY** (Integrated CAN) | `piper_gripper_controller` | **STATICALLY VERIFIED** | Joint position / torque feedback over CAN. |
| **3D LiDAR** (Livox Mid-360) | **VERIFIED** (Gazebo GPU LiDAR 32-beam) | **PENDING SDK BUILD** (ARM64) | **READY** (Ethernet 100BASE-TX) | `livox_ros_driver2` + `Livox-SDK2` | **STATICALLY VERIFIED** | Requires static IP (`192.168.1.50`) on eth0 and UDP port 56000. |
| **RGB-D Camera** (Intel RealSense D455) | **VERIFIED** (Gazebo RGBD Sensor) | **COMPATIBLE** (`librealsense2` Jetson deb) | **READY** (USB 3.2 Gen 1) | `realsense2_camera` + `librealsense2` | **STATICALLY VERIFIED** | Requires `99-realsense-libusb.rules` and USB 3.0 port. |
| **IMU** (Chassis / Sensor IMU) | **VERIFIED** (Gazebo IMU sensor) | **VERIFIED** (ROS 2 `sensor_msgs/Imu`) | **READY** (Internal to Base/LiDAR) | `ranger_base` (0x211 CAN frame) | **VERIFIED** | Publishes `/imu` with frame `imu_link` at 100 Hz. |
| **GPS / GNSS** | **VERIFIED** (Gazebo NavSat sensor) | **COMPATIBLE** (`nmea_navsat_driver`) | **OPTIONAL** (USB Serial RTK) | `nmea_navsat_driver` | **OPTIONAL** | Publishes `/gps/fix` with frame `gps_link`. |
| **Wheel Encoders & Steer Sensors** | **VERIFIED** (`gz_ros2_control` states) | **VERIFIED** (CAN telemetry) | **READY** (4WIS/4WID optical encoders) | `ranger_base` | **VERIFIED** | 50 Hz odometry telemetry via SocketCAN. |
| **CAN Bus Interface** | **N/A** (Simulated via topics) | **REQUIRED** (Native CAN or USB-CAN) | **MANDATORY** (CAN 2.0B, 500 kbps) | `mttcan` (Orin native) / `gs_usb` (USB) | **BLOCKED (Hardware Disconnected)** | Requires `ip link set can0 up type can bitrate 500000`. |
| **USB 3.0 Host** | **N/A** (Internal memory) | **VERIFIED** (Type-A USB 3.2 ports) | **MANDATORY** (RealSense + CAN) | Linux `xhci_hcd` kernel driver | **VERIFIED** | Sufficient power delivery (900 mA per port). |
| **Ethernet Host** | **VERIFIED** (Virtual WSL bridge) | **VERIFIED** (Gigabit RJ45) | **MANDATORY** (Livox LiDAR) | Linux `r8169` / `eqos` kernel driver | **VERIFIED** | Dedicated IP subnet for sensor streaming. |

---

## Jetson Orin Hardware Architecture & OS Compatibility

| Specification | Development Host (WSL 2) | Target Jetson Orin (Nano / NX / AGX) | Impact & Action Required |
| :--- | :--- | :--- | :--- |
| **CPU Architecture** | `x86_64` (Intel/AMD) | `aarch64` (ARM Cortex-A78AE) | **Cannot run x86 binaries.** All ROS packages and C++ drivers must be compiled from source on Jetson. |
| **GPU Architecture** | NVIDIA RTX 5060 Laptop GPU | NVIDIA Ampere (Orin GPU, 1024-2048 cores) | Native unified memory (UMA). TensorRT engine files must be generated directly on Orin. |
| **Operating System** | Ubuntu 26.04 LTS (Resolute) | Ubuntu 22.04 LTS (JetPack 5.1 / 6.0) / Ubuntu 24.04 (JetPack 6.1) | JetPack does not support Ubuntu 26.04. Target **ROS 2 Humble / Jazzy** for native hardware deployment. |
| **Storage / Rootfs** | 1 TB NVMe Host Drive | 64GB - 1TB M.2 NVMe SSD | Sufficient space for ROS 2, PyTorch, and TensorRT. |
| **Thermal / Power** | Dynamic Windows Power Plan | `nvpmodel -m 0` (MAXN mode) + `jetson_clocks` | Scripted automated performance mode configuration. |
