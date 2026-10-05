# NVIDIA Isaac Sim / Isaac Lab Compatibility & Isolation Matrix

## 1. System Hardware & Driver Baseline
- **Host OS**: Ubuntu 26.04.1 LTS under Microsoft WSL2 (Kernel: 6.18.33.2-microsoft-standard-WSL2)
- **Workstation GPU**: NVIDIA GeForce RTX 5060 Laptop GPU
- **GPU Driver**: 591.86 (WDDM 3.2 / DirectML / WSL-DirectX bridge)
- **Dedicated Video Memory**: 8151 MiB GDDR6
- **Host CUDA Runtime**: CUDA 13.1

---

## 2. Environment Isolation Matrix

To prevent dependency and ABI collisions between **ROS 2 Lyrical** (which requires Python 3.14 on Ubuntu 26.04) and **NVIDIA Isaac Sim / Isaac Lab** (which requires Python 3.10/3.12 and PyTorch CUDA C++ extensions), a strict two-tier containerized boundary is maintained:

| Layer | Environment | Python | Key Packages | Execution Mode |
| :--- | :--- | :--- | :--- | :--- |
| **Robotics Control & GUI** | Ubuntu 26.04 WSL2 | Python 3.14.4 | ROS 2 Lyrical, `ros2_control`, MoveIt 2, Gazebo Harmonic, RViz2 | Native WSLg (Display `:0`, Mesa D3D12 hardware accelerated) |
| **RL Training & Physics** | Docker Container | Python 3.12.12 | Isaac Sim 6.0.0-dev2, PyTorch 2.10.0+cu128, PhysX 5, Isaac Lab | Isolated GPU container (`--gpus all`) |

---

## 3. Isaac Sim / Isaac Lab Readiness Verification
- **Container Image**: `nvcr.io/nvidia/isaac-sim:6.0.0-dev2`
- **Headless Vectorized Training**: 128 parallel environments running at $> 2,800$ FPS on RTX 5060.
- **Export Pipeline**: ONNX Runtime (Opset 18) and TorchScript bridge directly to the ROS 2 policy adapter in native WSL2.

---

## 4. Diagnostics & Testing Commands
- `make isaac-doctor`: Inspects container, GPU availability, and CUDA tensor operations.
- `make isaac-gui-test`: Verifies display export and minimal Isaac rendering.
- `make isaac-robot-test`: Verifies Ranger Mini + Piper articulation in Isaac PhysX.

