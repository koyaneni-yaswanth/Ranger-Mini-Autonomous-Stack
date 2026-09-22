#!/usr/bin/env bash
# ==============================================================================
# RANGER MINI AUTONOMOUS STACK: ROS 2 HUMBLE ENVIRONMENT SETUP
# ==============================================================================

if [ ! -d "/opt/ros/humble" ]; then
    echo "[ERROR] ROS 2 Humble is not installed in /opt/ros/humble!"
    echo "This script must only be run on an Ubuntu 22.04 LTS host with ROS 2 Humble."
    return 1 2>/dev/null || exit 1
fi

echo "[INFO] Sourcing ROS 2 Humble base (/opt/ros/humble/setup.bash)..."
source /opt/ros/humble/setup.bash

WS_DIR="/home/yash/ranger_mini_humble_ws"
if [ -f "$WS_DIR/install/setup.bash" ]; then
    echo "[INFO] Sourcing Humble Workspace ($WS_DIR/install/setup.bash)..."
    source "$WS_DIR/install/setup.bash"
else
    echo "[WARN] Humble Workspace install/setup.bash not found. Run ./scripts/04_build_all.sh first."
fi

export ROS_DISTRO=humble
export ROS_VERSION=2
export ROS_PYTHON_VERSION=3
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
export IGN_GAZEBO_SYSTEM_PLUGIN_PATH=/opt/ros/humble/lib
export GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/ros/humble/lib

echo "=============================================================================="
echo " ROS 2 Humble Environment Ready"
echo " Active Distro: $ROS_DISTRO | Domain ID: $ROS_DOMAIN_ID | GPU: NVIDIA RTX"
echo "=============================================================================="
