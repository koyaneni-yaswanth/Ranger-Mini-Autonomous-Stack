#!/bin/bash
set -e

if [ -f "/opt/ros/humble/setup.bash" ]; then
    source "/opt/ros/humble/setup.bash"
else
    echo "[ERROR] ROS 2 Humble installation not found in /opt/ros/humble!"
    exit 1
fi

echo "=========================================================="
echo " Building Standalone ROS 2 Humble Workspace"
echo " Workspace: $HOME/ranger_mini_humble_ws"
echo " Distribution: $ROS_DISTRO"
echo "=========================================================="

cd "$HOME/ranger_mini_humble_ws"
colcon build --symlink-install --event-handlers console_direct+

echo "=========================================================="
echo " Humble Workspace Build Complete!"
echo " Source environment with: source install/setup.bash"
echo "=========================================================="
