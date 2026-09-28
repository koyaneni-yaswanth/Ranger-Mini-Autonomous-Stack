# JARVIS-X Baseline Environment & Simulation Audit
## AgileX Ranger Mini v2 + Piper 6-DOF Manipulator + Isaac Sim RL Subsystem

---

## 1. Executive Summary

This document establishes the official **Baseline Hardware, Simulation, and RL Stack Audit** for Project JARVIS-X. The audit confirms the operational readiness of the NVIDIA RTX 5060 hardware, the dual-runtime architecture (ROS 2 Lyrical on Ubuntu 26.04 and NVIDIA Isaac Sim 6.0.0 inside Ubuntu 22.04 Docker), and the existing verified manipulation primitives.

---

## 2. Hardware Compute & Accelerator Audit

| Property | Value / Specification | Verification Source |
| :--- | :--- | :--- |
| **GPU Model** | NVIDIA GeForce RTX 5060 Laptop GPU | `nvidia-smi` |
| **GPU Memory (VRAM)** | 8151 MiB GDDR6 | `nvidia-smi --query-gpu=memory.total` |
| **Host Driver Version** | 591.86 | NVIDIA Display Driver / WSLg |
| **CUDA Host Capability** | CUDA 13.1 (Compute Capability 12.0) | `nvidia-smi` |
| **Host Kernel** | Linux 6.18.33.2-microsoft-standard-WSL2 | `uname -r` |
| **Host OS** | Ubuntu 26.04.1 LTS (Noble-based / dev) | `/etc/os-release` |
| **Host Python** | Python 3.14.4 | `python3 --version` |

---

## 3. Simulation & Runtime Environments

### 3.1 ROS 2 & Gazebo Harmonic Stack (Ubuntu 26.04)
- **ROS Distro**: ROS 2 Lyrical (Development branch for Ubuntu 26.04)
- **Robotics Middleware**: `rmw_fastrtps_cpp` / `ROS_DOMAIN_ID=10`
- **Simulator**: Gazebo Harmonic (8.x) with `ros_gz_bridge` and `ros_gz_sim`
- **Arm Controller**: `piper_arm_controller` (`joint_trajectory_controller/JointTrajectoryController`)
- **Gripper Controller**: `piper_gripper_controller` (`position_controllers/GripperActionController`)
- **Chassis Controller**: `ranger_base_controller` (4WIS Ackermann/Dual-Ackermann kinematics)
- **Planning Pipeline**: Analytical IK + MoveIt 2 (`move_group`)

### 3.2 NVIDIA Isaac Sim Stack (Ubuntu 22.04 Docker)
- **Docker Image**: `nvcr.io/nvidia/isaac-sim:6.0.0-dev2` (Size: 28.5 GB)
- **Container Python**: Python 3.12.12
- **PyTorch Version**: 2.10.0+cu128
- **PyTorch CUDA Acceleration**: `torch.cuda.is_available() == True`
- **PyTorch Device Ordinal**: `NVIDIA GeForce RTX 5060` (Device Count: 1)
- **Extensions Installed**:
  - `isaacsim.asset.importer.urdf`
  - `isaacsim.core.api`
  - `isaacsim.core.prims`
  - `isaacsim.robot.manipulators`
  - `isaacsim.robot.wheeled_robots`
  - `isaacsim.ros2.bridge`
  - `isaacsim.simulation_app`
  - `omni.isaac.ml_archive`
  - `cumotion` / `nvidia_lula_no_cuda`

---

## 4. Model Asset & Description Inventory

| Model Asset | Format | Location | Joint & Link Status |
| :--- | :--- | :--- | :--- |
| **Ranger Mini v2** | URDF / Xacro | `ranger_description/urdf/ranger_mini.urdf.xacro` | 4 steering joints (`fl, fr, rl, rr`), 4 drive wheels |
| **Piper 6-DOF Arm** | URDF / Xacro | `ranger_description/urdf/piper_arm.xacro` | 6 revolute joints (`joint1` to `joint6`), calibrated limits |
| **Parallel Gripper** | URDF / Xacro | `ranger_description/urdf/piper_arm.xacro` | 2 prismatic fingers (`gripper_finger_joint1, joint2`) |
| **Combined System** | URDF / Xacro | `ranger_description/urdf/ranger_mini.urdf.xacro` | Rigid mounting plate on top platform |
| **Red Cube Target** | SDF / URDF | `worlds/red_cube_world.sdf` | $0.05\text{ m} \times 0.05\text{ m} \times 0.05\text{ m}$, mass $0.10\text{ kg}$ |
| **Workstation Table** | SDF / URDF | `worlds/red_cube_world.sdf` | Height: $0.30\text{ m}$, surface: $0.60\text{ m} \times 0.60\text{ m}$ |

---

## 5. Baseline Physical Test Verification Summary

All baseline hardware and physics regression benchmarks were executed live in Gazebo Harmonic with observable physical lift and contact measurements:

| Benchmark Target | Observable Physical Criterion | Live Measured Result | Status |
| :--- | :--- | :--- | :--- |
| `make cube-pick-test` | Gripper grasp + vertical lift $\Delta z \ge 0.08\text{ m}$ | $z_0 = 0.3300\text{ m} \to z_1 = 0.8466\text{ m}$ ($\Delta z = 0.5166\text{ m}$) | **PASS** |
| `make place-test` | Table descent, full detach, zero velocity | Released at $z=0.33\text{ m}$, stable on table surface | **PASS** |
| `make manipulation-doctor` | 21 subsystem health checks | 21/21 checks report `PASS` | **PASS** |
| `make simulation-e2e-test` | 16-stage autonomous mission verification | All 16 verification stages validated | **PASS** |

---

## 6. Audit Conclusion & Risk Mitigations

1. **Python Incompatibility**: Ubuntu 26.04 uses Python 3.14, whereas Isaac Sim 6.0 uses Python 3.12.
   * *Mitigation*: Complete isolation via Docker container. Ubuntu 26.04 acts as the ROS 2 orchestrator; Isaac Sim container performs GPU RL training and policy export.
2. **GPU Memory Ceiling**: RTX 5060 has 8 GB VRAM.
   * *Mitigation*: Vectorized RL environments in Isaac Sim will use $N=64$ to $N=256$ parallel actors, optimizing batch sizes to stay well within 4.5 GB active allocation.
3. **Policy Export Parity**:
   * *Mitigation*: Direct export to standard ONNX (opset 17) and TorchScript, with automated unit testing ensuring deviation $< 10^{-4}$ prior to ROS 2 runtime loading.