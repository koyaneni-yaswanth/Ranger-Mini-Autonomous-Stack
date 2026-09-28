# JARVIS-X Policy Deployment Specification
## Piper 6-DOF Reinforcement Learning Reaching & Grasping Policy

---

## 1. Model Artifacts

| Artifact Path | Format | Size | Description |
| :--- | :--- | :--- | :--- |
| `models/exported/piper_reach_policy.pt` | TorchScript (JIT) | 179 KB | Traced deterministic inference graph |
| `models/exported/piper_reach_policy.onnx` | ONNX (Opset 17/18) | 166 KB | Open Neural Network Exchange graph + weights |
| `models/exported/policy_metadata.json` | JSON | 1.1 KB | Schema definitions, bounds, and parity metrics |

---

## 2. Model Tensor Signatures & Physical Units

### 2.1 Observation Input Vector: `observation` (`float32[batch_size, 24]`)

| Index Range | Field Name | Unit | Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `0..5` | $q_1 \dots q_6$ | $\text{rad}$ | $[-\pi, +\pi]$ (Joint specific) | Current measured 6-DOF joint positions |
| `6..11` | $\dot{q}_1 \dots \dot{q}_6$ | $\text{rad/s}$ | $[-2.0, +2.0]$ | Current measured 6-DOF joint velocities |
| `12..14` | $p_{ee\_x}, p_{ee\_y}, p_{ee\_z}$ | $\text{meters}$ | $x \in [0.15, 0.65], y \in [-0.35, 0.35], z \in [0.05, 0.70]$ | End-effector TCP position in `base_link` frame |
| `15..18` | $q_{x}, q_{y}, q_{z}, q_{w}$ | Unit Quat | $[-1.0, +1.0]$ | End-effector orientation quaternion in `base_link` frame |
| `19..21` | $p_{tgt\_x}, p_{tgt\_y}, p_{tgt\_z}$ | $\text{meters}$ | Target position | Cube target position in `base_link` frame |
| `22..23` | $g_1, g_2$ | $\text{meters}$ | $[0.005, 0.035]$ | Parallel gripper finger positions |

### 2.2 Action Output Vector: `action` (`float32[batch_size, 7]`)

| Index | Field Name | Unit | Raw Range | Scaled Effect |
| :--- | :--- | :--- | :--- | :--- |
| `0..5` | $\Delta q_1 \dots \Delta q_6$ | Scaled Delta | $[-1.0, +1.0]$ | Multiplied by $\Delta q_{\max} = 0.04\text{ rad}$ per step ($50\text{ Hz}$) |
| `6` | $u_{\text{gripper}}$ | Command | $[-1.0, +1.0]$ | $> 0$: Close gripper; $\le 0$: Open gripper |

---

## 3. Mathematical Parity & Benchmark Performance

- **TorchScript vs PyTorch Parity**: $\max |y_{\text{pt}} - y_{\text{torch}}| = 0.000\times 10^0$ (Exact)
- **ONNX Runtime vs PyTorch Parity**: $\max |y_{\text{onnx}} - y_{\text{torch}}| = 5.960\times 10^{-7} < 10^{-4}$ (**PASS**)
- **Mean Single-Sample Inference Latency**: $0.21\text{ ms}$ on CPU, $0.08\text{ ms}$ on GPU (Exceeds $50\text{ Hz}$ requirement of $20\text{ ms}$).

---

## 4. Safety Wrapper & Guardrails

The deployment node (`ros2_policy_adapter_node.py`) enforces strict physical invariant checks before sending commands to `piper_arm_controller`:

1. **Velocity Limiting**: Max joint velocity is capped at $\dot{q}_{\max} = 1.0\text{ rad/s}$ ($|\Delta q| \le 0.02\text{ rad}$ per $50\text{ Hz}$ tick).
2. **Workspace Bounding Box**: Target TCP command must satisfy:
   $$x \in [0.15, 0.65]\text{ m}, \quad y \in [-0.35, 0.35]\text{ m}, \quad z \in [0.05, 0.70]\text{ m}$$
   Any command breaching these boundaries triggers emergency clamp and holds current joint positions.
3. **Emergency Stop (E-Stop)**: When an active E-Stop or human proximity violation is published on `/safety/emergency_stop`, policy inference is immediately paused, and all arm joints are locked.
4. **Fallback Mechanism**: If the target distance fails to decrease over 40 consecutive policy steps ($0.8\text{ s}$), the adapter aborts RL execution and returns control to the calibrated analytical IK planner.