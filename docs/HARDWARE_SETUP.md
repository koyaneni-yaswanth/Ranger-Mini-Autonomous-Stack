# Hardware Setup & Electrical Wiring

## 1. Power Distribution Architecture
- **Primary Battery**: 24V nominal (28.8V max, 21.0V cutoff) 30Ah LiFePO4.
- **E-Stop Circuit**: Hardwired inline safety contactor breaking 24V supply to actuator motor drives while preserving 12V/19V logic compute power.
- **Power Rails**:
  - Main 24V bus -> AgileX Ranger Mini v2 chassis & Piper arm power input.
  - Regulated 19V rail -> NVIDIA Jetson Orin compute unit.
  - Regulated 12V rail -> Industrial Ethernet switch, Livox Mid-360 LiDAR.
  - Regulated 5V rail -> USB hubs and microcontroller interfaces.

## 2. Data Bus Layout
- `can0` @ 500kbps: AgileX Ranger Mini chassis control and wheel encoders.
- `can1` @ 1Mbps: Piper 6-DOF robotic arm servo controllers and gripper.
- `eth0` Gigabit Ethernet: Livox Mid-360 point cloud stream and host development network.
- `usb3` Type-C: Intel RealSense D435i video and depth stream.
