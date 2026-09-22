#!/bin/bash

# Source base ROS 2 distribution
if [ -f "/opt/ros/lyrical/setup.bash" ]; then
    source /opt/ros/lyrical/setup.bash
elif [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi
set -e

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$WS_DIR/install/setup.bash"

echo "=== AUTONOMOUS NAVIGATION BENCHMARK TEST ==="
timeout 2 ros2 run tutorial_autonomous_navigation waypoint_navigator > /tmp/nav_test.log 2>&1 || true

if grep -q "Tutorial 03 Waypoint Navigator initialized" /tmp/nav_test.log; then
    echo "[OK] Autonomous Navigation client successfully dispatched."
    exit 0
else
    echo "[ERROR] Navigation test failed to initialize. Log:"
    cat /tmp/nav_test.log
    exit 1
fi
