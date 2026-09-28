# JARVIS-X Sim-to-Real Transfer & Domain Randomization Plan
## AgileX Ranger Mini v2 + Piper 6-DOF Manipulator

---

## 1. Executive Summary

This plan outlines the systematic methodology for deploying reinforcement learning policies and autonomous manipulation skills from simulation (Gazebo Harmonic / NVIDIA Isaac Sim) onto the physical **AgileX Ranger Mini v2** mobile base and **Piper 6-DOF** manipulator.

---

## 2. Reality Gap Taxonomy & Mitigations

| Gap Dimension | Simulation Characteristic | Physical Hardware Reality | Mitigation & Randomization Range |
| :--- | :--- | :--- | :--- |
| **Actuator Latency** | Instantaneous physics step ($20\text{ ms}$) | CAN bus jitter + actuator buffer ($10-25\text{ ms}$) | Action history observation buffer + randomized delay injection ($\Delta t \in [10, 30]\text{ ms}$) |
| **Friction & Contact** | Rigid contact / DetachableJoint plugin | Rubber finger pads, surface shear, micro-slips | Friction coefficient randomization $\mu \in [0.4, 1.2]$, contact compliance modeling |
| **Sensor Perception** | Exact depth raycast / ground truth | Optical noise, ambient glare, missing depth holes | Color jitter, depth Gaussian noise ($\sigma = 3\text{ mm}$), synthetic hole dropout |
| **Kinematic Calibration** | Exact mathematical URDF origins | Assembly tolerances, gear backlash ($\sim 0.5\text{ mrad}$) | Joint zero-point randomization ($\pm 0.015\text{ rad}$) |
| **Payload Variance** | Fixed mass $0.10\text{ kg}$ | Physical objects varying between $0.05-0.25\text{ kg}$ | Inertia & mass randomization ($m \in [0.05, 0.25]\text{ kg}$) |

---

## 3. Domain Randomization Formulation

During Isaac Sim / PyTorch RL policy training, each environment episode randomly samples:
1. **Target Cube Pose**:
   $$x_{\text{spawn}} \sim \mathcal{U}(0.42, 0.50)\text{ m}, \quad y_{\text{spawn}} \sim \mathcal{U}(-0.10, +0.10)\text{ m}, \quad z_{\text{table}} \sim \mathcal{U}(0.29, 0.31)\text{ m}$$
2. **Initial Joint Displacements**:
   $$q_{\text{init}} = q_{\text{ready}} + \epsilon_q, \quad \epsilon_q \sim \mathcal{N}(0, 0.02^2\cdot \mathbf{I})$$
3. **Observation Perturbation**:
   $$\tilde{p}_{\text{target}} = p_{\text{target}} + \mathbf{w}_p, \quad \mathbf{w}_p \sim \mathcal{N}(0, 0.003^2\cdot \mathbf{I})$$
4. **Action Rate Clamping**:
   $$\Delta q_t = \text{clip}(a_t \cdot \Delta q_{\max}, -\Delta q_{\max}, \Delta q_{\max}), \quad \Delta q_{\max} = 0.03\text{ rad}$$

---

## 4. Hardware Staging & Deployment Protocol

1. **Phase A: Tethered Standby & CAN Health**:
   - Verify `can0` active at $1\text{ Mbps}$ with zero frame drops (`ip -s link show can0`).
   - Run `manipulation_doctor.py` verifying joint feedback across all 6 Piper axes.
2. **Phase B: Zero-Gravity / Compliance Check**:
   - Move arm by hand through workspace bounding box to verify encoder alignment with simulation TF frames.
3. **Phase C: Shadow Policy Execution**:
   - Policy evaluates live sensor inputs in real time without sending motor torque commands; verify outputs match expected trajectories.
4. **Phase D: Low-Speed Hardware Trials**:
   - Scale action velocity by $0.25\times$; execute physical reach with software and physical E-Stop buttons primed.
5. **Phase E: Full Autonomous Mission**:
   - Enable closed-loop vision + RL policy execution with automatic fallback to analytical hold.