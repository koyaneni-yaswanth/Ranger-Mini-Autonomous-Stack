# SIMULATION LAUNCH ARCHITECTURE: ROS 2 & GAZEBO HARMONIC

## 1. Overview
This document specifies the exact runtime simulation architecture for the AgileX Ranger Mini v2 mobile robot with optional Piper 6-DOF modular manipulator in Gazebo Harmonic (version 10.5.0) under ROS 2 Lyrical Luth.

---

## 2. Launch Tree & Process Hierarchy

```text
make sim / make demo
  |
  +-- ranger_bringup/launch/sim.launch.py
        |
        +-- ranger_simulation/launch/gazebo.launch.py
              |
              +-- [1] Gazebo Harmonic Server & GUI (ros_gz_sim / gz_sim.launch.py)
              |     World: red_cube_world.sdf / workstation_manipulation.sdf
              |     Physics: gz-sim-physics-system (1ms step, real_time_factor 1.0)
              |     Sensors: gz-sim-sensors-system (OGRE render engine)
              |     IMU: gz-sim-imu-system
              |     Odometry: gz-sim-odometry-publisher-system
              |
              +-- [2] Robot State Publisher (ranger_description/launch/display.launch.py)
              |     URDF: ranger_mini.urdf.xacro (manipulator:=true, manipulator_type:=piper)
              |     Publishes: /robot_description, /tf, /tf_static (use_sim_time:=true)
              |
              +-- [3] Robot Spawner (ros_gz_sim create)
              |     Target: robot_description topic -> entity 'ranger_mini' at z=0.2m
              |
              +-- [4] ROS-GZ Parameter Bridge (ros_gz_bridge parameter_bridge)
              |     /clock [gz.msgs.Clock -> rosgraph_msgs/msg/Clock]
              |     /odometry -> /odom [gz.msgs.Odometry -> nav_msgs/msg/Odometry]
              |     /lidar/points/points -> /lidar/points [gz.msgs.PointCloudPacked -> sensor_msgs/msg/PointCloud2]
              |     /camera/image -> /camera [gz.msgs.Image -> sensor_msgs/msg/Image]
              |     /camera/depth_image [gz.msgs.Image -> sensor_msgs/msg/Image]
              |     /camera/camera_info [gz.msgs.CameraInfo -> sensor_msgs/msg/CameraInfo]
              |     /imu [gz.msgs.IMU -> sensor_msgs/msg/Imu]
              |     /gps/fix [gz.msgs.NavSat -> sensor_msgs/msg/NavSatFix]
              |
              +-- [5] ROS 2 Control (ranger_control/launch/control.launch.py)
              |     Plugin: gz_ros2_control/GazeboSimSystem
              |     Spawners:
              |       - joint_state_broadcaster -> /joint_states
              |       - steering_controller (ForwardCommandController: 4 steering joints)
              |       - traction_controller (ForwardCommandController: 4 traction joints)
              |       - piper_arm_controller (JointTrajectoryController: 6 Piper joints)
              |     Nodes:
              |       - ranger_kinematics_node (4WIS inverse kinematics: /cmd_vel -> steering & traction)
              |       - odom_tf_broadcaster (odom -> base_footprint TF broadcaster)
              |       - manipulator_manager_node (/manipulator/status & /manipulator/capabilities)
              |
              +-- [6] Perception & Sensor Processing (ranger_perception/launch/sensor_processing.launch.py)
              |     Node: pointcloud_to_laserscan_node (/lidar/points -> /scan)
              |
              +-- [7] SLAM / Localization (ranger_slam/launch/mapping.launch.py)
              |     Node: async_slam_toolbox_node (map -> odom TF broadcaster)
              |
              +-- [8] Navigation 2 (ranger_navigation/launch/navigation.launch.py)
              |     Nodes: planner_server, controller_server, behavior_server, bt_navigator, waypoint_follower
              |     Costmaps: Global & Local costmaps (voxel_layer height 1.6m, fully unclipped)
              |
              +-- [9] AI Perception & Localizer (ranger_vision/launch/vision.launch.py)
              |     Nodes:
              |       - ai_object_localizer_node (detects physical red cube, publishes /vision/target_pose)
              |       - sensor_fusion_node
              |
              +-- [10] MoveIt 2 Motion Planning (ranger_manipulation/launch/moveit.launch.py)
              |     Node: move_group (interfaces with piper_arm_controller trajectory action)
              |
              +-- [11] JARVIS Embodied Brain & Orchestration
                    Nodes:
                      - jarvis_brain (/jarvis/recognized_speech -> task planning & execution)
                      - autonomous_task_orchestrator (17-state FSM executing pick & place)
                      - semantic_world_model (object tracking & persistence)
```

---

## 3. Interfaces & Topic Contracts

| Topic | Type | Source | Purpose |
|---|---|---|---|
| `/clock` | `rosgraph_msgs/msg/Clock` | `ros_gz_bridge` | Simulation clock synchronization |
| `/odom` | `nav_msgs/msg/Odometry` | `ros_gz_bridge` | Ground truth wheel odometry |
| `/tf` | `tf2_msgs/msg/TFMessage` | `robot_state_publisher`, `odom_tf_broadcaster`, `slam_toolbox` | Transform tree: `map` -> `odom` -> `base_footprint` -> `base_link` -> sensors |
| `/scan` | `sensor_msgs/msg/LaserScan` | `pointcloud_to_laserscan` | 2D LiDAR planar scan for SLAM & Nav2 |
| `/lidar/points` | `sensor_msgs/msg/PointCloud2` | `ros_gz_bridge` | Livox Mid-360 3D Pointcloud |
| `/camera` | `sensor_msgs/msg/Image` | `ros_gz_bridge` | RealSense D455 RGB stream |
| `/camera/depth_image` | `sensor_msgs/msg/Image` | `ros_gz_bridge` | RealSense D455 depth stream |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Nav2 / Teleop / Orchestrator | Input velocity commands |
| `/steering_controller/commands` | `std_msgs/msg/Float64MultiArray` | `ranger_kinematics_node` | 4WIS steering angles |
| `/traction_controller/commands` | `std_msgs/msg/Float64MultiArray` | `ranger_kinematics_node` | 4WIS wheel angular velocities |
| `/piper_arm_controller/joint_trajectory` | `trajectory_msgs/msg/JointTrajectory` | MoveIt 2 / Orchestrator | 6-DOF arm trajectory commands |
| `/vision/target_pose` | `geometry_msgs/msg/PoseStamped` | `ai_object_localizer_node` | 3D localized pose of red cube |
