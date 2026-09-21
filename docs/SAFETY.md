# Robot Safety Watchdog & Emergency Stop (Sections 17 & 74)

- **Proximity E-Stop**: Stops robot within 0.052s if obstacle distance < 0.35m.
- **Command Timeout**: Clamps velocity to zero if `/cmd_vel` is silent for > 200ms.
- **Communication Loss**: Automatic safe stop on CAN or ROS node disconnection.
