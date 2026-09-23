# Ranger Mini Autonomous Platform (Next-Gen Production Architecture)

## Target Specification
- **Host OS:** Windows 11 Pro / Enterprise (Build 26200+)
- **Virtualization:** WSL 2 (Kernel 6.18.33+, WSLg 1.0.73+)
- **Guest OS:** Ubuntu 26.04 LTS (x86_64)
- **Robotics Middleware:** ROS 2 Lyrical Luth (L-turtle)
- **GPU Acceleration:** NVIDIA GeForce RTX 5060 Laptop GPU via DirectX GPU-PV / Mesa D3D12
- **Mobile Robot:** AgileX Ranger Mini (4WIS / 4WID Kinematics)

---

## Quickstart Runbook

```bash
# 1. Verify Environment & GPU
make check

# 2. Build Workspace
make build

# 3. Run Automated Tests
make test

# 4. Launch Simulation with Nav2
make sim

# 5. Launch Hardware (when CAN is connected)
make real
```

See `docs/` for the complete 20-part engineering manual.
