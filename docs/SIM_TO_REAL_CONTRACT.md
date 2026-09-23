# Sim-to-Real Interface Contract
## AgileX Ranger Mini + Piper + NERO Autonomy Stack

This document formalizes the strict contract between the Simulation environment (Gazebo Harmonic) and the Real Physical Hardware (Jetson Orin + physical sensors and actuators).

---

## 1. Primary Interface Specification

| Topic / Service | ROS Message Type | Source (Sim) | Source (Real Hardware) | Target Consumer | Update Rate | QoS Profile | Frame ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Nav2 / Teleop / Watchdog | Nav2 / Teleop / Watchdog | `ranger_base` / `gz_ros2_control` | 20 - 50 Hz | RELIABLE | `base_footprint` |
| `/odom` | `nav_msgs/msg/Odometry` | `gz-sim-odometry-publisher-system` | `ranger_base_node` (SocketCAN) | Nav2 / EKF / SLAM | 50 Hz | RELIABLE | `odom` (child: `base_footprint`) |
| `/tf` | `tf2_msgs/msg/TFMessage` | Gazebo Bridge + `robot_state_publisher` + SLAM | Base Driver + `robot_state_publisher` + SLAM | All Nodes | Continuous | DYNAMIC | Multiple |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | `robot_state_publisher` (URDF) | `robot_state_publisher` (URDF) | All Nodes | Latched | TRANSIENT_LOCAL | Multiple |
| `/scan` | `sensor_msgs/msg/LaserScan` | `pointcloud_to_laserscan` (Sim LiDAR) | `livox_ros_driver2` -> `pointcloud_to_laserscan` | SLAM / Nav2 Costmaps | 10 - 20 Hz | SENSOR_DATA (Best Effort) | `lidar_link` |
| `/lidar/points` | `sensor_msgs/msg/PointCloud2` | Gazebo GPU LiDAR | Livox Mid-360 Native Driver | Sensor Fusion / Perception | 10 Hz | SENSOR_DATA | `lidar_link` |
| `/camera/image_raw` | `sensor_msgs/msg/Image` | Gazebo RGB Camera | Intel RealSense D455 (`realsense2_camera`) | YOLO / Sensor Fusion | 30 Hz | SENSOR_DATA | `camera_optical_link` |
| `/camera/depth/image_raw` | `sensor_msgs/msg/Image` | Gazebo Depth Camera | Intel RealSense D455 (`realsense2_camera`) | 3D Obstacle / MoveIt | 30 Hz | SENSOR_DATA | `camera_optical_link` |
| `/camera/camera_info` | `sensor_msgs/msg/CameraInfo` | Gazebo Camera Plugin | Intel RealSense Factory Calibration | Perception / Vision Nodes | 30 Hz | SENSOR_DATA | `camera_optical_link` |
| `/imu` | `sensor_msgs/msg/Imu` | Gazebo IMU Sensor | Base CAN IMU / RealSense IMU | EKF Filter / Watchdog | 100 Hz | SENSOR_DATA | `imu_link` |
| `/joint_states` | `sensor_msgs/msg/JointState` | `gz_ros2_control` (Broadcaster) | Hardware Broadcaster + Piper Driver | MoveIt / Robot State Publisher | 50 Hz | RELIABLE | N/A |
| `/piper_arm_controller/follow_joint_trajectory` | `control_msgs/action/FollowJointTrajectory` | `gz_ros2_control` Action Server | `piper_ros` Action Server | MoveIt 2 Motion Planner | On-demand | RELIABLE | N/A |
| `/safety/estop` | `std_msgs/msg/Bool` | Safety Watchdog / UI | Hardware E-Stop Button / Safety Node | All Actuators | 10 Hz | RELIABLE | N/A |

---

## 2. Coordinate Frame Architecture (TF Tree)

The TF hierarchy is strictly invariant between Simulation and Physical Hardware:

```
map
 └── odom                     [Owned by SLAM Toolbox or AMCL]
      └── base_footprint       [Owned by Gazebo Odometry (Sim) OR ranger_base_node (Real)]
           └── base_link       [Owned by robot_state_publisher from URDF]
                ├── fl_steering_link -> fl_wheel_link
                ├── fr_steering_link -> fr_wheel_link
                ├── rl_steering_link -> rl_wheel_link
                ├── rr_steering_link -> rr_wheel_link
                ├── top_deck_link
                │    ├── lidar_link
                │    ├── camera_link -> camera_optical_link
                │    └── piper_mount
                │         └── piper_link1 -> ... -> piper_link6 -> tool0
                ├── imu_link
                └── gps_link
```

### Invariant Rules:
1. **Never create competing TF broadcasters**: In simulation, `publish_odom_tf` in `control.launch.py` is `false` because Gazebo's bridge publishes `odom -> base_footprint`. On real hardware, `ranger_base_node` publishes `odom -> base_footprint`.
2. **Timestamps**: In simulation, all headers use simulation time (`use_sim_time: true`). On real hardware, all headers use host system time (`use_sim_time: false`) synchronized via chrony/NTP.

---

## 3. Physical vs Simulated Deviations & Required Calibrations

| Aspect | Simulation Model | Physical Robot Reality | Calibration Requirement |
| :--- | :--- | :--- | :--- |
| **Wheel Traction & Friction** | Ideal Coulomb friction ($\mu=1.0$) | Floor slip, tire deformation, carpet vs tile | Odometry calibration script (`calibrate_wheel_radius.py`) |
| **Steering Alignment** | Zero mechanical backlash | Linkage play, zero-point offset | Steer offset calibration in `ranger_controllers.yaml` |
| **LiDAR Sensor Noise** | Gaussian noise $\sigma=0.01\,\text{m}$ | Reflectivity dropouts, outdoor ambient sunlight | Intensity threshold filtering in `sensor_processing` |
| **Camera Extrinsics** | Exact CAD coordinates | Assembly mounting tolerance ($\pm 2\,\text{mm}, \pm 1^\circ$) | ArUco target extrinsic calibration (`camera_lidar_calib`) |
| **Arm Zero Position** | Mathematical zero in URDF | Motor zero offset on powerup | Piper homing calibration via CAN service call |
