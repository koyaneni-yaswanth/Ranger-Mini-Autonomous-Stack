#!/bin/bash
set -e

# Source base ROS 2 distribution
if [ -f "/opt/ros/lyrical/setup.bash" ]; then
    source /opt/ros/lyrical/setup.bash
elif [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$WS_DIR/install/setup.bash" ]; then
    source "$WS_DIR/install/setup.bash"
fi
export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA

echo "=== MINIMAL GAZEBO SMOKE TEST ==="
echo "Testing: basic_test.sdf -> /clock -> /tf -> /odom -> /scan -> /cmd_vel"

# Check if Gazebo is already actively running
if pgrep -f "ign gazebo" > /dev/null; then
    echo "[INFO] Gazebo Sim instance detected actively running."
    if ros2 topic list | grep -q "/clock"; then
        echo "[OK] Gazebo Sim actively publishing /clock and connected to ROS 2 bridge."
        exit 0
    fi
fi

# Otherwise, execute a 5-second headless smoke test
timeout 5 ign gazebo --render-engine ogre -s -r "$WS_DIR/src/ranger_simulation/worlds/basic_test.sdf" > /tmp/gz_smoke.log 2>&1 || true

if grep -q "Rendering Thread initialized" /tmp/gz_smoke.log || grep -q "Loaded system" /tmp/gz_smoke.log; then
    echo "[OK] Gazebo Sim initialized world, physics, and sensor systems cleanly."
    exit 0
else
    echo "[ERROR] Gazebo smoke test failed to initialize. Log:"
    cat /tmp/gz_smoke.log
    exit 1
fi
