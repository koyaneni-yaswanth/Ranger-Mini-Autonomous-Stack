# JARVIS-X: INTERFACE & COMMUNICATION CONTRACTS

## 1. Skill Contract Specification
Every skill implements `SkillContract` with:
- `name: str`
- `required_capabilities: List[str]`
- `check_preconditions(context: Dict) -> bool`
- `execute(params: Dict) -> SkillResult`
- `verify_postconditions(context: Dict) -> bool`

## 2. Core ROS 2 Topic Contracts
| Topic | Message Type | Purpose |
| :--- | :--- | :--- |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Slew-rate clamped base velocity command |
| `/odom` | `nav_msgs/msg/Odometry` | Ground truth or fused base odometry |
| `/scan` | `sensor_msgs/msg/LaserScan` | 2D projection for costmap obstacle marking |
| `/lidar/points` | `sensor_msgs/msg/PointCloud2` | 3D Pointcloud from Livox Mid-360 |
| `/emergency_stop` | `std_msgs/msg/Bool` | Physical or software E-Stop interlock |
| `/jarvis/voice_command` | `std_msgs/msg/String` | Incoming natural language prompt |
| `/jarvis/speech_output` | `std_msgs/msg/String` | Outgoing synthesized vocal report |
| `/jarvis/health` | `std_msgs/msg/String` | System diagnostic heartbeat |
