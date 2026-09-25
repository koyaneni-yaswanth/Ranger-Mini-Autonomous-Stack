# Dynamic Semantic World Model & Event Bus

## 1. Tracked Entities
The World Model (`jarvis_core.world_model`) maintains persistent 3D state for:
- **Objects**: Target ID, class (`cube`, `box`, `bottle`), color, 3D pose in `map` and `base_link`, graspability, and confidence.
- **People**: Human ID, 3D position, distance to robot, state (moving/stationary), and safety zone (`SAFE`, `CAUTION`, `STOP`).
- **Stations**: Coordinates and type (`dock`, `table`, `bin`).
- **Robot State**: Odometry pose, velocity, arm stance, battery %, module status.

## 2. JARVIS Event Bus
Emits typed events over `/jarvis/events`:
- `OBJECT_DETECTED`, `OBJECT_LOST`, `HUMAN_DETECTED`, `HUMAN_STOP_ZONE`, `TASK_STARTED`, `TASK_COMPLETED`, `GRASP_SUCCESS`, `GRASP_FAILED`, `BATTERY_LOW`, `EMERGENCY_STOP`.
