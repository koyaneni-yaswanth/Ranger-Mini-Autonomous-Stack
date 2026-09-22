#!/usr/bin/env bash
# ==============================================================================
# RANGER MINI AUTONOMOUS STACK: ROS 2 LYRICAL ENVIRONMENT SETUP
# ==============================================================================

WS_DIR="/home/yash/ranger_mini_lyrical_ws"

if [ ! -d "$WS_DIR" ]; then
    echo "[ERROR] Lyrical Workspace not found at $WS_DIR!"
    return 1 2>/dev/null || exit 1
fi

echo "[INFO] Configuring Standalone ROS 2 Lyrical Workspace..."

# Sourcing base ROS if native, else isolated workspace
if [ -d "/opt/ros/lyrical" ]; then
    source /opt/ros/lyrical/setup.bash
elif [ -d "/opt/ros/humble" ]; then
    source /opt/ros/humble/setup.bash
fi

if [ -f "$WS_DIR/install/setup.bash" ]; then
    echo "[INFO] Sourcing Lyrical Workspace ($WS_DIR/install/setup.bash)..."
    source "$WS_DIR/install/setup.bash"
else
    echo "[WARN] Lyrical Workspace install/setup.bash not found. Run ./scripts/04_build_all.sh first."
fi

export ROS_DISTRO=lyrical
export ROS_VERSION=2
export ROS_PYTHON_VERSION=3
export ROS_DOMAIN_ID=10
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
export IGN_GAZEBO_SYSTEM_PLUGIN_PATH=/opt/ros/humble/lib

echo "=============================================================================="
echo " ROS 2 Lyrical Environment Ready (Isolated Workspace)"
echo " Active Target: ROS 2 Lyrical | Domain ID: $ROS_DOMAIN_ID | GPU: NVIDIA RTX"
echo " Containerized Target: $WS_DIR/docker/lyrical/"
echo "=============================================================================="
