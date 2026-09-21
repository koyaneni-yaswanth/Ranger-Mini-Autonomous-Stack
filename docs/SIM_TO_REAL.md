# Simulation-to-Real Parity & Acceptance Criteria (Section 64 & 65)

## Parity Matrix
| Interface | Simulation | Hardware | Parity Verified |
| :--- | :--- | :--- | :---: |
| `/cmd_vel` | Gazebo Kinematics Plugin | `ranger_base_node` (can0) | **YES** |
| `/odom` | Odometry Publisher | Optical Wheel Encoders | **YES** |
| `/scan` | Pointcloud to Laserscan | Livox MID-360 Laserscan | **YES** |
| `/camera` | Gazebo RGB-D Plugin | RealSense D435 Driver | **YES** |
| `/imu` | Gazebo IMU System | 9-DOF CAN IMU | **YES** |
| `/tf` | `robot_state_publisher` | `robot_state_publisher` | **YES** |
| `joint_states` | Gazebo Joint State Broadcaster | Ranger Wheel & Steer Encoders | **YES** |

## Acceptance Criteria
- Same command velocity limits (1.5 m/s linear, 1.2 rad/s angular).
- Same frame convention (`map` -> `odom` -> `base_footprint` -> `base_link`).
- Identical Nav2 costmap layers and planners.
