# Piper 6-DOF Robotic Manipulator Module

## 1. Specifications
- **Degrees of Freedom**: 6 Revolute Joints + 1 Linear Parallel Gripper.
- **Payload Capacity**: 1.5 kg rated payload at maximum reach.
- **Maximum Reach**: 626 mm spherical working envelope.
- **Repeatability**: +/- 0.05 mm.
- **Operating Bus**: CAN 2.0B @ 1 Mbps.
- **Supply Voltage**: 24V DC.

## 2. Joint Configurations & Limits
| Joint Name | Min Angle | Max Angle | Max Velocity | Default Transport |
| :--- | :--- | :--- | :--- | :--- |
| `piper_joint1` | -2.618 rad | +2.618 rad | 2.0 rad/s | 0.000 rad |
| `piper_joint2` | 0.000 rad | +3.141 rad | 2.0 rad/s | 0.100 rad |
| `piper_joint3` | -2.800 rad | 0.000 rad | 2.0 rad/s | 0.200 rad |
| `piper_joint4` | -1.745 rad | +1.745 rad | 2.5 rad/s | 0.000 rad |
| `piper_joint5` | -1.220 rad | +1.220 rad | 2.5 rad/s | 0.100 rad |
| `piper_joint6` | -2.094 rad | +2.094 rad | 3.0 rad/s | 0.000 rad |
