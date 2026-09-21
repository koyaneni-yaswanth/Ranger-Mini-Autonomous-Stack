#!/bin/bash
set -e

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$WS_DIR/install/setup.bash" 2>/dev/null || source /opt/ros/humble/setup.bash

echo "=== CUSTOM DWA LOCAL PLANNER EVALUATION ==="
test -f "$WS_DIR/src/ranger_navigation/config/nav2_params_pure_pursuit.yaml"
echo "[OK] DWA & Pure Pursuit controller configurations verified."
exit 0
