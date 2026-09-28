# JARVIS-X Data Schema & Logging Specification
## Standardized Multimodal Dataset Format for Embodied Robotic AI

---

## 1. Directory Structure

```
datasets/jarvis_x/
├── index.json                     # Master dataset catalog and summary statistics
├── episodes/
│   ├── episode_0001.json          # Timestamped trajectory, observations, actions, metadata
│   ├── episode_0002.json
│   └── ...
└── models/
    └── fine_tuned/                # Continual learning policy checkpoints
```

---

## 2. Episode Data Schema (`episode_{id}.json`)

Each episode file records the complete closed-loop execution of a JARVIS task:

```json
{
  "$schema": "https://agilex.ai/schemas/jarvis_x/episode_v1.json",
  "metadata": {
    "episode_id": "ep_20260928_180200_001",
    "timestamp_utc": "2026-09-28T18:02:00.123Z",
    "task_name": "red_cube_pick_and_place",
    "execution_mode": "reinforcement_learning_policy",
    "robot_platform": "AgileX Ranger Mini v2 + Piper 6-DOF",
    "simulator": "Gazebo Harmonic / NVIDIA Isaac Sim 6.0",
    "policy_version": "piper_reach_policy_v1.0"
  },
  "initial_conditions": {
    "target_object": "red_cube",
    "target_spawn_xyz": [0.450, 0.000, 0.330],
    "table_surface_z": 0.300,
    "initial_joint_positions": [0.000, 0.400, 1.200, 0.000, 0.200, 0.000]
  },
  "trajectory_stream": [
    {
      "step": 0,
      "time_from_start_s": 0.00,
      "observation": {
        "joint_positions": [0.000, 0.400, 1.200, 0.000, 0.200, 0.000],
        "joint_velocities": [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
        "ee_position": [0.380, 0.000, 0.480],
        "ee_quaternion": [0.000, 1.000, 0.000, 0.000],
        "target_position": [0.450, 0.000, 0.330],
        "gripper_finger_positions": [0.035, 0.035]
      },
      "action": {
        "joint_deltas": [0.000, 0.012, 0.018, 0.000, -0.004, 0.000],
        "gripper_command": -1.0
      },
      "reward_breakdown": {
        "r_dist": -0.75,
        "r_grasp": 0.0,
        "r_lift": 0.0,
        "total": -0.75
      }
    }
  ],
  "verification_verdict": {
    "grasp_verified": true,
    "lift_verified": true,
    "final_height_m": 0.8466,
    "net_lift_m": 0.5166,
    "placement_verified": true,
    "final_position_error_mm": 4.20,
    "execution_duration_s": 6.85,
    "status": "SUCCESS"
  }
}
```

---

## 3. Continuous Improvement & Retraining Protocol

1. **Failure Mining**: Episodes marked with `"status": "RECOVERABLE_FAILURE"` or `"status": "COLLISION_RISK"` are flagged for targeted domain-randomized retraining.
2. **Offline Replay**: Transition tuples $(s_t, a_t, r_t, s_{t+1})$ from verified successful real/sim episodes are appended to an offline demonstration buffer for behavioral cloning or offline RL (e.g. CQL/IQL).
3. **Model Versioning**: Checkpoints exceeding $\ge 95\%$ benchmark success across 500 test trials are promoted to `models/exported/` with semantic version tags.