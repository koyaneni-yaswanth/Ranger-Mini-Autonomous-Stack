#!/usr/bin/env bash
# ==============================================================================
# Jetson Orin Autonomous Hardware Stack Provisioning Script
# Prepares JetPack / Ubuntu environment, builds drivers, and sets udev rules
# ==============================================================================
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
WS_DIR="${PROJECT_DIR}/../ranger_mini_lyrical_2604_ws"

echo "=============================================================================="
echo "          PROVISIONING STACK FOR NVIDIA JETSON ORIN TARGET"
echo "=============================================================================="

if [ "$EUID" -ne 0 ]; then
    echo "Elevating permissions with sudo..."
    SUDO="sudo"
else
    SUDO=""
fi

echo "[INFO] Installing hardware communication packages..."
$SUDO apt-get update -y
$SUDO apt-get install -y --no-install-recommends \
    can-utils \
    net-tools \
    iproute2 \
    libasio-dev \
    libpcap-dev \
    python3-can \
    v4l-utils

echo "[INFO] Configuring systemd SocketCAN service (can0 @ 500k)..."
$SUDO bash -c 'cat << "EOF" > /etc/systemd/network/80-can0.network
[Match]
Name=can0

[CAN]
BitRate=500000
RestartSec=100ms
EOF' 2>/dev/null || true

echo "[INFO] Installing robot hardware udev rules..."
$SUDO bash -c 'cat << "EOF" > /etc/udev/rules.d/99-ranger-hardware.rules
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE:="0666", SYMLINK+="ranger_can"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE:="0666", SYMLINK+="piper_can"
SUBSYSTEM=="usb", ATTRS{idVendor}=="8086", ATTRS{idProduct}=="0b3a", MODE:="0666", GROUP:="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="8086", ATTRS{idProduct}=="0b07", MODE:="0666", GROUP:="plugdev"
EOF'
$SUDO udevadm control --reload-rules 2>/dev/null || true
$SUDO udevadm trigger 2>/dev/null || true

echo "[INFO] Building ROS 2 packages in ${WS_DIR}..."
if [ -d "${WS_DIR}" ]; then
    cd "${WS_DIR}"
    source /opt/ros/lyrical/setup.bash || true
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
fi

echo "=============================================================================="
echo "[SUCCESS] Jetson Orin Provisioning Complete!"
echo "=============================================================================="
