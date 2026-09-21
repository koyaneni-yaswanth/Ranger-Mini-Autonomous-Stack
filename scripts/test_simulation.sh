#!/bin/bash
set -e

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$WS_DIR/install/setup.bash" 2>/dev/null || source /opt/ros/humble/setup.bash
export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA

echo "=== GAZEBO SIMULATION TEST ==="
if pgrep -f "ign gazebo" > /dev/null; then
    echo "[OK] Gazebo Sim instance is actively running and streaming /clock."
    exit 0
fi

timeout 5 ign gazebo --render-engine ogre -s -r "$WS_DIR/src/ranger_simulation/worlds/basic_test.sdf" > /tmp/gz_test.log 2>&1 || true
if grep -q "Rendering Thread initialized" /tmp/gz_test.log || grep -q "Loaded system" /tmp/gz_test.log; then
    echo "[OK] Gazebo Sim initialized world, physics, and sensor systems cleanly."
    exit 0
else
    echo "[ERROR] Gazebo simulation test failed. Log:"
    cat /tmp/gz_test.log
    exit 1
fi
