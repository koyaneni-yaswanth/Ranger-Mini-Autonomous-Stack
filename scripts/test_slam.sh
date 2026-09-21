#!/bin/bash
set -e

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$WS_DIR/install/setup.bash" 2>/dev/null || source /opt/ros/humble/setup.bash

echo "=== SLAM TOOLBOX CONFIGURATION TEST ==="
test -f "$WS_DIR/src/ranger_slam/config/mapper_params_online_async.yaml"
echo "[OK] SLAM Toolbox configuration verified."
exit 0
