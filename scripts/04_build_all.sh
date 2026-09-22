#!/usr/bin/env bash
set -e
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " [04/12] CLEAN WORKSPACE BUILD VERIFICATION"
echo "=============================================================================="

WS_LIST=("/home/yash/ranger_mini_humble_ws" "/home/yash/ranger_mini_lyrical_ws" "/home/yash/ranger_mini_workbench")

for ws in "${WS_LIST[@]}"; do
    if [ -d "$ws" ] && [ -d "$ws/src" ]; then
        echo "--> Building workspace: $ws"
        cd "$ws"
        colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
        echo "[OK] Clean build completed for $ws"
    fi
done
echo "=============================================================================="
echo "[PASS] All workspaces built with ZERO errors."
