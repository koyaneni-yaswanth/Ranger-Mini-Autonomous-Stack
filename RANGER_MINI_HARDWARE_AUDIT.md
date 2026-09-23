# RANGER MINI HARDWARE AUDIT

## 1. Drivetrain & Kinematic Configuration
- **Model:** AgileX Ranger Mini (V1 / V2)
- **Drivetrain Type:** 4-Wheel Independent Steering & 4-Wheel Independent Driving (4WIS / 4WID / Dual-Ackermann / Omnidirectional).
- **Wheelbase ($L$):** $0.500\,	ext{m}$ ($500\,	ext{mm}$)
- **Track Width ($W$):** $0.470\,	ext{m}$ ($470\,	ext{mm}$)
- **Wheel Radius ($R$):** $0.090\,	ext{m}$ ($90\,	ext{mm}$)
- **Max Linear Velocity ($v_{\max}$):** $1.5\,	ext{m/s}$
- **Max Angular Velocity ($\omega_{\max}$):** $2.0\,	ext{rad/s}$
- **Max Incline:** $10^\circ$

## 2. Low-Level Control Protocol (SocketCAN)
- **Interface Type:** SocketCAN `can0`
- **Default Baudrate:** $500{,}000\,	ext{bps}$ ($500\,	ext{kbps}$)
- **CAN ID Range:**
  - Control Frame: `0x111` (Motion command $v, \omega, \gamma$)
  - System State: `0x211` (Vehicle status, mode, battery voltage)
  - Motor Feedback (1-4): `0x251 - 0x254` (Current, velocity, encoder pulses)
  - Actuator State (1-4): `0x261 - 0x264` (Steering angle feedback)
- **Watchdog Timeout:** $200\,	ext{ms}$ (automatic zero-velocity hold if heartbeat ceases).
- **Physical Connectors:** Aviation multi-pin CAN / Power / Serial port.

## 3. Sensors
- **3D LiDAR:** Livox MID-360 (Ethernet UDP, 100 Mbps, static IP 192.168.1.50).
- **RGB-D Camera:** Intel RealSense D435 / D435i (USB 3.0 Type-C, 640x480 @ 30fps).
- **IMU:** 9-DOF High-Precision IMU (built into Livox MID-360 or dedicated CAN node).
