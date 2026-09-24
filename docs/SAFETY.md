# Safety Architecture & Emergency Protocols

## 1. Safety Hierarchy
1. **Layer 0 (Hardware E-Stop)**: Physical mushroom button on sensor mast cuts motor actuator power immediately via safety contactor.
2. **Layer 1 (Firmware Interlock)**: Driver-level heartbeat watchdog. If heartbeat drops for > 100ms, chassis and arm brake into safe stop.
3. **Layer 2 (Software E-Stop)**: ROS topic `/safety/estop_active` published by safety monitor, halting all state machine actions.
4. **Layer 3 (Navigation Costmaps)**: Nav2 2D/3D obstacle inflation layer maintaining 0.35m minimum standoff from all static and dynamic hazards.
5. **Layer 4 (AI Safety Policy)**: Rule 13 prohibits raw motor/joint velocity overrides from external user or AI agents.
