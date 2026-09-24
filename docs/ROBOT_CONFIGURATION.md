# Robot Configuration & Modular Deployment

## 1. Modular Launch Modes
The platform supports dual runtime configurations controlled via standard ROS 2 launch arguments:

### Base-Only Configuration (Autonomous Mobile Robot)
```bash
ros2 launch ranger_bringup bringup.launch.py manipulator:=false
# or using Makefile
make base-only
```
- Active Nodes: `ranger_base_node`, `lidar_driver`, `camera_driver`, `ekf_node`, `nav2_bringup`.
- Manipulator nodes and MoveIt planning pipelines are completely dormant.
- Hardware topics `/manipulator/status` report `{"attached": false}`.

### Modular Mobile Manipulator Configuration
```bash
ros2 launch ranger_bringup bringup.launch.py manipulator:=true manipulator_type:=piper
# or using Makefile
make piper
```
- Active Nodes: All Base-Only nodes + `piper_arm_controller`, `moveit_pipeline`, `ai_task_interpreter`, `autonomous_task_orchestrator`.
- Hardware topics `/manipulator/status` report `{"attached": true, "type": "piper"}`.

## 2. Configuration Files & Schemas
- `config/object_database.yaml`: Object classes (cube, box, bottle), visual HSV priors, preferred grasps, and workstation coordinates.
- `config/task_schema.json`: Strict JSON Schema defining valid AI tasks, safety limits, and actions.
