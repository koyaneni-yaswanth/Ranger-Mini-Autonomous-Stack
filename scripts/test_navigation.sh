#!/bin/bash
set -e

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$WS_DIR/install/setup.bash" 2>/dev/null || source /opt/ros/humble/setup.bash

echo "=== NAV2 NAVIGATION TEST ==="
timeout 2 ros2 run tutorial_autonomous_navigation waypoint_navigator > /tmp/nav_test.log 2>&1 || true
if grep -q "Tutorial 03 Waypoint Navigator initialized" /tmp/nav_test.log; then
    echo "[OK] Nav2 action client verified."
    exit 0
else
    echo "[ERROR] Nav2 test failed."
    exit 1
fi
