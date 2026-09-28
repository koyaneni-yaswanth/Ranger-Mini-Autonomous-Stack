# NVIDIA Isaac Sim & System Version Matrix
## Project JARVIS-X: AgileX Ranger Mini v2 + Piper 6-DOF Manipulator

---

## 1. System Version Matrix

| Layer / Component | Specification | Supported Version | Production Status | Fallback / Alternative |
| :--- | :--- | :--- | :--- | :--- |
| **Host Workstation OS** | Microsoft Windows 11 Pro | 10.0.26100 (x86_64) | Active Host | Native Linux (Ubuntu) |
| **GPU Hardware** | NVIDIA GeForce RTX 5060 | 8151 MiB GDDR6 | Active Primary | Cloud Instance (A100/H100) |
| **Host NVIDIA Driver** | NVIDIA Display Driver | 591.86 | Fully Operational | 550.x+ LTS Driver |
| **Host CUDA Toolkit** | CUDA Driver API | 13.1 (Compute 12.0) | Active | CUDA 12.4 |
| **Primary Development OS** | Ubuntu 26.04 LTS (WSL2) | Linux 6.18.33.2-WSL2 | Active Orchestrator | Ubuntu 24.04 LTS |
| **Primary Python** | CPython | 3.14.4 | Active ROS 2 Host | Python 3.12 venv |
| **Primary ROS 2 Distro** | ROS 2 Lyrical (Development) | Rolling / 26.04 dev | Active Middleware | ROS 2 Jazzy |
| **Physics Simulation (Real-Time)** | Gazebo Harmonic | 8.x (`ros_gz`) | Active Real-Time | Gazebo Fortress |
| **Container Engine** | Docker Engine | 27.x on Ubuntu-22.04 | Active Sandbox | Podman / Apptainer |
| **Isaac Sim Version** | NVIDIA Isaac Sim | 6.0.0-dev2 (Omniverse Kit 107) | Active GPU RL Engine | Isaac Sim 4.2 / 2023.1 |
| **Isaac Sim Python** | CPython (Kit Bundled) | 3.12.12 | Active RL Trainer | Standalone PyTorch venv |
| **Isaac Sim PyTorch** | PyTorch with CUDA | 2.10.0+cu128 | Active Vectorized RL | PyTorch 2.5.1 |
| **Robotics Bridge** | ROS 2 / ONNX Policy Bridge | `ROS_DOMAIN_ID=10` + ONNX Runtime | Active Deployment | Isaac ROS Bridge |

---

## 2. Boundary Isolation Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                   UBUNTU 26.04 (WSL2 ENVIRONMENT)                      │
│                                                                        │
│   • Python 3.14.4 Runtime                                              │
│   • ROS 2 Lyrical (rclpy, ros2_control, MoveIt 2, Nav2)               │
│   • Gazebo Harmonic Simulator (Real-time physics & sensors)           │
│   • JARVIS Cognitive Brain & Task Orchestrator                         │
│   • ROS 2 RL Policy Adapter Node (ONNX Runtime / TorchScript)          │
│                                                                        │
└──────────────────────────────────▲─────────────────────────────────────┘
                                   │  /mnt/wsl/ Shared IPC / File Mount
                                   │  ROS_DOMAIN_ID=10 DDS Topics
┌──────────────────────────────────▼─────────────────────────────────────┐
│                 DOCKER (UBUNTU 22.04 CONTAINER RUNTIME)                │
│                                                                        │
│   • Python 3.12.12 (Omniverse Kit Runtime)                            │
│   • NVIDIA Isaac Sim 6.0.0-dev2 (PhysX 5 GPU Accelerated)             │
│   • PyTorch 2.10.0+cu128 (Direct CUDA on RTX 5060)                     │
│   • Vectorized Reaching & Grasping MDP Environments                   │
│   • PPO Actor-Critic Vectorized Training                              │
│   • Export Pipeline (ONNX / TorchScript) → /workspace/models/exported  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Compatibility Rules & Guardrails

1. **Zero Python Binary Mixing**: Under no circumstances shall wheels from Python 3.12 (container) be imported or installed directly into the Ubuntu 26.04 Python 3.14 environment.
2. **Policy Contract Boundary**: The trained RL policy must always be exported to platform-independent ONNX (opset $\ge 17$) or TorchScript `.pt` artifacts. The ROS 2 policy adapter in Ubuntu 26.04 consumes this exported artifact via standard ONNX runtime or PyTorch C++/Python API.
3. **Safety Fallback**: If the RL policy outputs a joint delta that violates workspace bounds ($x \notin [0.15, 0.65], y \notin [-0.35, 0.35], z \notin [0.05, 0.70]\text{ m}$) or joint limits, the ROS 2 policy adapter clamps the command and flags a safety event, falling back to the calibrated analytical IK trajectory.