#!/usr/bin/env bash
# ==============================================================================
# Safe Staged Bringup for Physical AgileX Ranger Mini Robot
# Performs pre-flight hardware checks before launching real ROS 2 nodes
# ==============================================================================
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
WS_DIR="${PROJECT_DIR}/../ranger_mini_lyrical_2604_ws"

echo "=============================================================================="
echo "             AGILEX RANGER MINI HARDWARE BRINGUP"
echo "=============================================================================="

# 1. Check CAN interface
if ! ip link show can0 &>/dev/null; then
    echo "[ERROR] can0 interface is missing!"
    echo "Please bring up the SocketCAN interface using:"
    echo "  sudo ip link set can0 type can bitrate 500000"
    echo "  sudo ip link set can0 up"
    exit 1
fi

CAN_STATE="$(ip -brief link show can0 | awk '{print $2}')"
if [ "${CAN_STATE}" != "UP" ]; then
    echo "[INFO] Bringing up can0 interface..."
    sudo ip link set can0 up || {
        echo "[ERROR] Failed to bring up can0."; exit 1;
    }
fi

# 2. Source ROS 2 Lyrical & Workspace
source /opt/ros/lyrical/setup.bash
if [ -f "${WS_DIR}/install/setup.bash" ]; then
    source "${WS_DIR}/install/setup.bash"
fi

echo "[STAGE 1] Launching Ranger Mini Hardware Stack (can_interface:=can0)..."
exec ros2 launch ranger_bringup hardware.launch.py can_interface:=can0
