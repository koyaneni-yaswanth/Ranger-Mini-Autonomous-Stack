# Safety Architecture & Human Awareness

## 1. Independent Safety Authority
The Safety Manager (`jarvis_core.safety_manager`) operates independently of the AI reasoning layer and possesses absolute authority to halt motion.

## 2. Human Proximity Zones
- **SAFE Zone (> 2.0m)**: Standard operational speeds permitted.
- **CAUTION Zone (1.0m to 2.0m)**: Linear speed automatically capped at 50% (0.4 m/s).
- **STOP Zone (< 1.0m)**: Actuators immediately halted via software interlock until distance opens.

## 3. Emergency Stop & Watchdog
- Hardware mushroom switch directly interrupts actuator power.
- Heartbeat watchdog monitors LiDAR, camera, and compute temperatures; publishes health status to `/jarvis/health`.
