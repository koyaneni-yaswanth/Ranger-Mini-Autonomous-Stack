# Manipulator Hardware Integration & Power Engineering

This document specifies the low-level physical integration details for mounting and interfacing robotic arms with the AgileX Ranger Mini mobile base and NVIDIA Jetson Orin compute unit.

---

## 1. CAN Bus Hardware Setup & Termination

### 1.1 Bus Architecture
The robot uses a differential CAN 2.0B bus operating at 1.0 Mbps.
- **Differential Signaling:** CAN_H (~3.5V active) and CAN_L (~1.5V active) with a recessive idle state of 2.5V.
- **Bus Termination:** High-speed 1 Mbps CAN strictly requires exactly **two 120 Ω, 0.25 W termination resistors** at each physical end of the bus (total DC bus resistance measured between CAN_H and CAN_L must read ~60 Ω when powered down).
  - Termination Node 1: Internal to Ranger Mini base mainboard.
  - Termination Node 2: Selectable jumper or end-point resistor on Piper arm connector board.

### 1.2 SocketCAN Linux Configuration
To manually establish and test the SocketCAN link on NVIDIA Jetson / Ubuntu Linux:
```bash
# Set bitrate and bring interface up
sudo ip link set can0 type can bitrate 1000000 restart-ms 100
sudo ip link set can0 txqueuelen 1000
sudo ip link set can0 up

# Verify packet statistics
ip -s link show can0
```

---

## 2. Linux udev Device Rules

Place the following rules in `/etc/udev/rules.d/99-ranger-modular.rules`:
```udev
# AgileX Ranger Mini Mobile Base CAN Interface
SUBSYSTEM=="net", ACTION=="add", ATTRS{interface}=="can0", NAME="can0"

# USB-to-CAN Adapters (CANable / Candlelight firmware)
SUBSYSTEM=="net", ACTION=="add", ATTRS{idVendor}=="1d50", ATTRS{idProduct}=="606f", NAME="can_piper"

# Direct Serial / USB Endpoints for Custom Manipulators
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout", SYMLINK+="ttyUSB_ARM"
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout", SYMLINK+="ttyUSB_ARM"
```

Apply rules immediately:
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## 3. Electrical Power Budget & Thermal Analysis

### 3.1 Jetson Orin & Robot Power Audit
| Subsystem | Voltage | Idle Power | Peak Power | Primary Source |
|---|---|---|---|---|
| **Ranger Mini Drive Motors (4x)** | 24V DC | 12.0 W | 250.0 W | 24V LiFePO4 Main Battery (30 Ah) |
| **Steering Actuators (4x)** | 24V DC | 6.0 W | 60.0 W | 24V Main Battery |
| **NVIDIA Jetson Orin Compute** | 19V DC (Buck) | 15.0 W | 40.0 W | 24V->19V Isolated DC-DC |
| **Livox Mid-360 3D LiDAR** | 12V DC (Buck) | 8.0 W | 12.0 W | 24V->12V Isolated DC-DC |
| **RealSense D435i Camera** | 5V DC (USB 3.0)| 1.8 W | 3.5 W | Jetson USB3 Host Port |
| **Subtotal (Base AMR Alone)** | — | **42.8 W** | **365.5 W** | — |
| **Piper 6-DOF Manipulator** | 24V DC | 12.0 W | 240.0 W | 24V Main Battery (Switched) |
| **Total System (AMR + Piper)** | — | **54.8 W** | **605.5 W** | **Battery Peak Limit: 720 W** |

**Runtime Projection:**
- 30 Ah battery @ 24V = 720 Wh total energy capacity.
- Base AMR continuous operation: **~8.5 hours**.
- Combined Mobile Manipulator operational duty cycle (50% drive, 50% pick): **~4.8 hours continuous mission time**.

---

## 4. Passive Non-Destructive Auto-Detection Protocol

In industrial environments, activating actuator torques during hardware probes can cause accidental movement, operator injury, or mechanical collision. The modular detection architecture enforces a strict **zero-energize passive discovery protocol**:
1. **Network Link Audit:** Queries kernel sysfs (`/sys/class/net/can*`) to verify interface state without sending CAN control frames (`0x151` torque command is forbidden).
2. **Device Node Discovery:** Inspects `/dev/piper*` and `/dev/serial/by-id` for vendor VID/PID signatures.
3. **ROS 2 Decoupled Registry:** Reads `/manipulator/status` and `/manipulator/capabilities` from the background manager node.
