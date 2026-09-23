#!/usr/bin/env bash
set -e

# Strictly verify and source genuine ROS 2 Lyrical
if [ ! -f "/opt/ros/lyrical/setup.bash" ]; then
    echo "[FAIL] Genuine ROS 2 Lyrical installation not found at /opt/ros/lyrical/setup.bash!"
    return 1 2>/dev/null || exit 1
fi

source /opt/ros/lyrical/setup.bash

export ROS_DISTRO=lyrical
export ROS_VERSION=2
export ROS_PYTHON_VERSION=3
export ROS_DOMAIN_ID=10
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
export LIBGL_ALWAYS_SOFTWARE=0
export GALLIUM_DRIVER=d3d12

WS_DIR="/home/yash/ranger_mini_lyrical_2604_ws"
if [ -f "$WS_DIR/install/setup.bash" ]; then
    source "$WS_DIR/install/setup.bash"
fi

echo "[OK] Genuine ROS 2 Lyrical Environment Active (Distro: $ROS_DISTRO | Binary: $(which ros2))"
