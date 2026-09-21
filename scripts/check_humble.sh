#!/bin/bash
set -e

echo "=== HUMBLE ENVIRONMENT CHECK ==="
if [ -f "/opt/ros/humble/setup.bash" ]; then
    echo "[OK] Found /opt/ros/humble/setup.bash"
else
    echo "[ERROR] /opt/ros/humble/setup.bash not found!"
    exit 1
fi
if [ -f "$HOME/ranger_mini_humble_ws/install/setup.bash" ]; then
    echo "[OK] Found ~/ranger_mini_humble_ws/install/setup.bash"
else
    echo "[WARNING] Humble workspace not yet built. Run ./build.sh."
fi
exit 0
