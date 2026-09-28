# JARVIS-X Safety Case & Fault Recovery Specification
## Safety-Critical Operation for Mobile Manipulator Platforms

---

## 1. Safety Architecture Overview

Project JARVIS-X enforces **defense-in-depth safety**. High-level cognitive reasoning (JARVIS Brain / LLM) and reinforcement learning policies are strictly isolated from direct actuator access by deterministic safety layers:

```
┌────────────────────────────────────────────────────────┐
│      HIGH-LEVEL AI COGNITIVE & RL POLICY LAYER         │
└───────────────────────────┬────────────────────────────┘
                            │ Trajectory / Delta Intent
┌───────────────────────────▼────────────────────────────┐
│              DETERMINISTIC SAFETY SUPERVISOR           │
│   • Workspace Bounding Box Clamp                       │
│   • Joint Velocity & Acceleration Ceilings             │
│   • Collision Zone Exclusion (Chassis & Sensors)       │
│   • Watchdog Heartbeat (< 100 ms timeout)              │
│   • Emergency Stop (E-Stop) Priority Intercept         │
└───────────────────────────┬────────────────────────────┘
                            │ Filtered & Verified Command
┌───────────────────────────▼────────────────────────────┐
│                HARDWARE ACTUATION LAYER                │
│   • ros2_control / CAN bus / Joint Trajectory Controller│
└────────────────────────────────────────────────────────┘
```

---

## 2. Hazard Analysis & Risk Mitigation Matrix

| Hazard ID | Hazard Description | Severity | Probability | Deterministic Mitigation | Residual Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HAZ-001** | Manipulator strikes workstation or chassis during descent | Critical | Low | Bounding box exclusion: $z \ge 0.05\text{ m}, x \ge 0.15\text{ m}$. Physical hardstops in URDF. | Negligible |
| **HAZ-002** | Runaway joint velocity from neural policy output | High | Low | Dynamic clamping: $|\Delta q_i| \le 0.03\text{ rad}$ per $50\text{ Hz}$ tick ($\dot{q} \le 1.5\text{ rad/s}$). | Negligible |
| **HAZ-003** | Communication drop / network partition during motion | High | Medium | Watchdog timer ($100\text{ ms}$ threshold) commands active zero-velocity hold. | Negligible |
| **HAZ-004** | Human obstacle enters operational workspace | Critical | Medium | 2D LiDAR + RGB-D proximity zone ($< 0.8\text{ m}$) triggers immediate E-Stop pause. | Low |
| **HAZ-005** | Object slips or drops during high-speed transport | Medium | Low | Arm retracts to tucked `HOME` pose during base navigation; gripper force verified. | Negligible |

---

## 3. Emergency Stop (E-Stop) Metrics

- **E-Stop Publisher Topic**: `/safety/emergency_stop` (`std_msgs/msg/Bool`)
- **Software Response Latency**: $< 20\text{ ms}$ (Single control cycle)
- **Actuator Braking Time**: $< 50\text{ ms}$ to zero velocity
- **Lockout Mechanism**: Once engaged, motion cannot resume until an explicit safety reset command is received from an authorized operator.

---

## 4. Multi-Tier Fault Recovery Hierarchy

1. **Tier 1 (Transient Retry)**:
   - Example: Visual occlusion or momentary gripper slip.
   - Action: Retract arm $5\text{ cm}$, refresh perception filter, and re-attempt grasp up to 2 times.
2. **Tier 2 (Degraded Mode Fallback)**:
   - Example: RL policy reports confidence score $< 0.40$ or oscillation detected.
   - Action: Abort RL policy and fall back to the calibrated analytical IK trajectory.
3. **Tier 3 (Safe Retreat & Pause)**:
   - Example: Persistent failure or unexpected physical obstacle.
   - Action: Move arm to safe ready pose, lock brakes, and ask operator for clarification via JARVIS dialogue interface.