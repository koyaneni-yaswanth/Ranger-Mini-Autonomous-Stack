# NVIDIA Jetson Orin Deployment Guide

## 1. Target Hardware
- NVIDIA Jetson AGX Orin (32GB/64GB) or Orin Nano (8GB).
- JetPack 6.x (Ubuntu 22.04/24.04/26.04 rootfs) with TensorRT, CUDA 12, and cuDNN.
- Dual-channel isolated CAN transceiver (Waveshare or SPI MCP2517FD).

## 2. Setup Commands
```bash
./scripts/setup_jetson.sh
./scripts/build.sh
./scripts/health_check.sh
./scripts/run_jarvis.sh
```
