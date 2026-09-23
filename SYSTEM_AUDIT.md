# SYSTEM AUDIT REPORT: RANGER MINI AUTONOMOUS PLATFORM

**Audit Date:** 2026-09-22  
**Target Architecture:** Windows 11 + WSL 2 + Ubuntu 26.04 LTS + ROS 2 Lyrical Luth + NVIDIA RTX 5060 + AgileX Ranger Mini  
**Auditor:** Lead Robotics Systems Engineer  

---

## Complete Component Audit Matrix

| Component | Detected Version / Value | Expected Target Version | Status | Evidence (Command & Output) | Required Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Host OS** | Windows 11 Build 10.0.26200.9457 | Windows 11 (23H2/24H2+) | **PASS** | wsl --version reports Windows version: 10.0.26200.9457 | Maintain host OS updates. |
| **WSL 2 Version** | 2.7.12.0 | Latest WSL 2 (>= 2.3.0) | **PASS** | wsl --version -> WSL version: 2.7.12.0 | None. Meets requirements. |
| **WSL Kernel** | 6.18.33.2-2 | Modern Linux 6.x (>= 6.6.x) | **PASS** | wsl --version -> Kernel version: 6.18.33.2-2 | None. Kernel supports GPU-PV and modern netfilter. |
| **WSLg / Display** | 1.0.73.2 / DISPLAY=:0 | WSLg with Wayland & X11 | **PASS** | WSLg version: 1.0.73.2, WAYLAND_DISPLAY=wayland-0 | None. GUI forwarder active. |
| **DirectX / DXCore** | D3D 1.611.1-81528511 / DXCore 10.0.26100.1 | DirectX GPU-PV runtime | **PASS** | ls -la /usr/lib/wsl/lib/libdxcore.so present and bound | None. |
| **GPU Hardware** | NVIDIA GeForce RTX 5060 Laptop GPU | NVIDIA RTX 5060 | **PASS** | 
vidia-smi -> NVIDIA GeForce RTX 5060, 8151 MiB VRAM | None. Dedicated GPU detected. |
| **NVIDIA Driver** | Driver 591.86 / CUDA 13.1 | Modern Game Ready / Studio Driver | **PASS** | 
vidia-smi -> Driver Version: 591.86, CUDA Version: 13.1 | None. Supports WSL GPU compute. |
| **GPU 3D Acceleration**| Mesa 23.2.1 D3D12 (RTX 5060) | Hardware-accelerated OpenGL/Vulkan | **PASS** | MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA glxinfo -B -> OpenGL renderer: D3D12 (NVIDIA GeForce RTX 5060), Accelerated: yes | Enforce adapter environment variable. |
| **Guest OS Distribution**| Ubuntu 22.04.5 LTS (active default) | Ubuntu 26.04 LTS | **INCOMPATIBLE / PENDING** | Active: cat /etc/os-release -> 22.04.5 LTS. Online list: wsl --list --online lists Ubuntu-26.04 Ubuntu 26.04 LTS available. | Provision dedicated Ubuntu 26.04 instance without modifying 22.04. |
| **Architecture** | x86_64 | x86_64 | **PASS** | uname -m -> x86_64 | None. |
| **Compilers (Current)** | gcc 11.4.0, g++ 11.4.0, cmake 3.22.1 | Modern C++17/20 Toolchain | **PASS (for 22.04)** | CLI version checks confirm GCC 11.4.0 | Install build-essential on target 26.04. |
| **Python Version** | Python 3.10.12 | Python 3.12+ (Ubuntu 26.04 standard) | **PASS (for 22.04)** | python3 --version -> Python 3.10.12 | Use target system Python on 26.04. |
| **Docker Engine** | Docker 29.8.1 (build 4a63305) | Docker Engine >= 24.x | **PASS** | docker --version -> Docker version 29.8.1 | Configure container runner as secondary path. |
| **ROS 2 Installed** | /opt/ros/humble | ROS 2 Lyrical Luth | **MIXED / PENDING** | /opt/ros/ has humble. Source workspace anger_mini_lyrical_ws compiles Lyrical packages. | Build/deploy Lyrical on Ubuntu 26.04. |
| **RMW Implementation** | mw_fastrtps_cpp (default) | Eclipse Cyclone DDS (mw_cyclonedds_cpp) | **PENDING** | dpkg -l | grep fastrtps -> installed; cyclonedds not default | Install mw-cyclonedds-cpp and configure cyclonedds.xml. |
| **Gazebo Simulator** | Gazebo Fortress / Harmonic (/usr/bin/ign, gz) | Supported Gazebo version with os_gz | **PASS** | which ign gz -> present; os-humble-ros-gz present | Verify Gazebo integration on target distribution. |
| **Robot Kinematics** | 4-Wheel Independent Steering (4WIS / 4WID) | AgileX Ranger Mini kinematics | **PASS** | Verified in anger_control/scripts/kinematics_node.py (FL, FR, RL, RR steering + traction) | Standardize kinematics controller. |
| **URDF Robot Model** | anger_mini.urdf.xacro (28 links, 27 joints) | Complete verified kinematic tree | **PASS** | check_urdf validated, 0 loops, closed chain | Retain verified URDF in target workspace. |
| **Sensors in Sim** | Livox MID-360 (/scan), RealSense (/camera), IMU | 3D LiDAR, RGB-D Camera, IMU | **PASS** | Topic streams active in simulation bridge | Preserve sensor pipeline parity. |
| **Nav2 Navigation** | Nav2 Humble / Lyrical ported stack | Full autonomous Nav2 stack | **PASS** | Verified in simulation: 4/4 waypoints reached | Port Nav2 configuration to target stack. |
| **Physical SocketCAN**| can0 interface NOT DETECTED | Physical SocketCAN adapter | **BLOCKED** | ip link show can0 -> not found; usbipd list shows no CAN adapter attached | Attach physical CAN hardware via USBIPD when testing real robot. |
| **Physical Sensors** | /dev/ttyUSB*, /dev/ttyACM* NOT DETECTED | Physical LiDAR / RealSense | **BLOCKED** | ls /dev/tty* -> empty | Attach physical sensors when testing real robot. |
| **System Resources** | 12 CPU cores (Ryzen 5 7600X), 15.2 GB RAM, 889 GB free disk | Minimum 8 GB RAM, 4 cores, 20 GB disk | **PASS** | lscpu, ree -h, df -h confirm high headroom | Optimal for full compilation & simulation. |

---

## Safety & Non-Fabrication Summary

1. **Simulation Parity:** Verified in simulation with closed-loop actuation, TF continuity, SLAM mapping, and Nav2 goal execution.
2. **Physical Hardware Reality:** The physical Ranger Mini chassis and physical sensors are **NOT physically connected** to the host machine. All physical hardware tests remain strictly reported as **BLOCKED — Physical hardware unavailable**.
