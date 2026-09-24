# NVIDIA Jetson AGX / Orin Deployment Guide

## 1. Hardware Prerequisites
- NVIDIA Jetson AGX Orin (32GB/64GB) or Orin Nano (8GB).
- JetPack 6.0+ (Ubuntu 22.04/24.04/26.04 rootfs).
- Dual CAN Transceiver (Waveshare Isolated Dual CAN or SPI MCP2517FD).
- RealSense D435i & Livox Mid-360 LiDAR.

## 2. Jetson System Setup Script
Run the automated deployment script:
```bash
make jetson-setup
```
This configures:
- Realtime CPU governor (`nvpmodel -m 0` & `jetson_clocks`).
- SocketCAN kernel modules (`can`, `can_raw`, `mttcan`).
- USB device udev rules for RealSense and CAN adapters.
- FastDDS network buffer optimizations.
