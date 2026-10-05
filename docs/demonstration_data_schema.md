# JARVIS-X Multimodal Demonstration & Episode Data Schema
## Standard HDF5 / JSON Specification for Robotic Embodied AI

**Schema Version:** `2.1.0-aloha-compatible`  
**Applicability:** Human Teleoperation, Simulation Capture, Physical Deployment, and Replay Logs  

---

## 1. Episode Identification & Strict Source Labeling

Every episode file (`ep_<timestamp>_<uuid>.json` or `.h5`) must possess an immutable metadata header. Mixing source labels is strictly forbidden:

```json
{
  "metadata": {
    "episode_id": "ep_20261003_120000_a1b2c3",
    "task_instruction": "Pick up the red cube from the workstation table",
    "robot_model": "ranger_mini_v2_piper_6dof",
    "model_version": "v1.0.0-provisional",
    "source_label": "SIMULATION", 
    "hardware_identity": "sim_gazebo_harmonic_wslg",
    "tf_calibration_version": "calib_2026_09_28_v1",
    "start_time_iso": "2026-10-03T12:00:00.123456Z",
    "end_time_iso": "2026-10-03T12:00:15.987654Z",
    "duration_sec": 15.864,
    "total_timesteps": 793,
    "recording_frequency_hz": 50.0,
    "success_label": true,
    "human_intervention": false,
    "termination_reason": "TASK_SUCCESS_VERIFIED"
  }
}
```

### Allowed Values for `source_label`:
- `SIMULATION`: Generated inside Gazebo Harmonic or NVIDIA Isaac Sim.
- `HARDWARE`: Recorded from physical Ranger Mini chassis and physical Piper manipulator.
- `DEMONSTRATION`: Recorded via physical leader arm, SpaceMouse, or human teleoperator.
- `REPLAY`: Software-in-the-loop replay of a previous trajectory.
- `SYNTHETIC`: Procedurally generated trajectory or domain-randomized synthetic rollout.

---

## 2. Timestep Telemetry Schema (Synchronized at 50 Hz)

Each step index $t \in [0, N-1]$ contains synchronized sensor readings and control actions:

| Field Path | Type | Dimension / Shape | Units | Description |
| :--- | :--- | :--- | :--- | :--- |
| `timestamp` | Float64 | Scalar | seconds | Wall-clock / Sim time relative to episode start |
| `chassis/odom/position` | Float64 | `[3]` | meters | Global base position `[x, y, z]` |
| `chassis/odom/orientation` | Float64 | `[4]` | unit quaternion | Base orientation `[qx, qy, qz, qw]` |
| `chassis/cmd_vel` | Float64 | `[2]` | `m/s, rad/s` | Commanded `[linear_x, angular_z]` |
| `manipulator/joint_positions` | Float64 | `[6]` | radians | 6-DOF joint angles `[q1, q2, q3, q4, q5, q6]` |
| `manipulator/joint_velocities`| Float64 | `[6]` | rad/s | 6-DOF joint rates `[dq1, dq2, dq3, dq4, dq5, dq6]` |
| `manipulator/joint_efforts` | Float64 | `[6]` | $\text{N}\cdot\text{m}$ | Measured actuator torques |
| `manipulator/tcp_pose` | Float64 | `[7]` | meters / quat | Tool Center Point `[x, y, z, qx, qy, qz, qw]` |
| `gripper/stroke` | Float64 | Scalar | meters | Opening distance `[0.0, 0.070]` m |
| `gripper/effort` | Float64 | Scalar | Newtons | Grip force feedback |
| `action/target_joint_positions`| Float64| `[6]` | radians | Trajectory command dispatched to controller |
| `action/target_gripper_stroke` | Float64| Scalar | meters | Gripper command dispatched to controller |
| `perception/target_object_pose`| Float64| `[7]` | meters / quat | Tracked cube position & orientation |

---

## 3. ALOHA HDF5 Group Structure Mapping

For compatibility with ALOHA training pipelines (`act-plus-plus`, `diffusion_policy`), the data is mapped to standard HDF5 datasets:
- `/observations/qpos`: `[T, 14]` (Chassis 2 + Arm 6 + Gripper 1 + Target 5)
- `/observations/qvel`: `[T, 14]`
- `/observations/images/top`: `[T, 480, 640, 3]` (RGB array)
- `/observations/images/wrist`: `[T, 480, 640, 3]` (Wrist camera RGB)
- `/action`: `[T, 14]` (Target joint positions and velocities)

