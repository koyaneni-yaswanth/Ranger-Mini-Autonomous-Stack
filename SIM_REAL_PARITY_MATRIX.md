# SIMULATION <-> REAL HARDWARE PARITY MATRIX

| Functional Stream | Topic Name | Message Type | Rate | Frame ID | Simulation Source | Real Hardware Source | Parity Validation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Motion Command** | `/cmd_vel` | `geometry_msgs/Twist` | 50 Hz | `base_footprint` | Nav2 / Teleop | Nav2 / Teleop | **PARITY CONFIRMED** |
| **Drive Odometry** | `/odom` | `nav_msgs/Odometry` | 50 Hz | `odom` -> `base_footprint` | Gazebo OdometryPub | AgileX `ranger_base` | **PARITY CONFIRMED** |
| **Transform Tree** | `/tf`, `/tf_static`| `tf2_msgs/TFMessage` | 50 Hz | (Full Tree) | Gazebo + RSP | EKF Localizer + RSP | **PARITY CONFIRMED** |
| **2D Laser Scan** | `/scan` | `sensor_msgs/LaserScan` | 10 Hz | `lidar_link` | PointCloud2LaserScan | Livox LiDAR Driver | **PARITY CONFIRMED** |
| **Camera RGB** | `/camera/image_raw`| `sensor_msgs/Image` | 30 Hz | `camera_color_optical_frame` | Gazebo Camera | `realsense2_camera` | **PARITY CONFIRMED** |
| **Depth Cloud** | `/camera/points` | `sensor_msgs/PointCloud2`| 15 Hz | `camera_depth_optical_frame` | Gazebo Depth Cam | `realsense2_camera` | **PARITY CONFIRMED** |
| **Inertial Data** | `/imu` | `sensor_msgs/Imu` | 100 Hz| `imu_link` | Gazebo IMU Plugin | Physical 9-DOF IMU | **PARITY CONFIRMED** |
| **Battery State** | `/battery_state` | `sensor_msgs/BatteryState`| 1 Hz | `base_link` | Sim Battery Node | AgileX BMS via CAN | **PARITY CONFIRMED** |
