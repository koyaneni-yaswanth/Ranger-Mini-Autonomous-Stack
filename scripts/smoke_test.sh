#!/bin/bash
set -e

echo "===================================="
echo "AMR-X Automated Smoke Test"
echo "===================================="

# 1. Check Environment
source /opt/ros/humble/setup.bash
source ~/ranger_mini_lyrical_ws/install/install/setup.bash
echo "[OK] ROS 2 Environment Sourced"

# 2. Check Build
cd ~/ranger_mini_lyrical_ws/install
if colcon build > /dev/null; then
    echo "[OK] colcon build passes"
else
    echo "[FAILED] colcon build failed"
    exit 1
fi

# 3. Validate Nodes (Offline Check)
echo "[OK] All custom packages located:"
ros2 pkg list | grep amr_

echo "[OK] Smoke test execution complete. System is ready for Master Demo Launch."
