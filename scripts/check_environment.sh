#!/bin/bash
set -e

echo "Checking Environment..."

# OS Check
source /etc/os-release
echo "OS: $NAME $VERSION"

# ROS Check
if [ -z "$ROS_DISTRO" ]; then
    echo "[ERROR] ROS_DISTRO is not set. Please source a ROS 2 setup.bash file."
    exit 1
else
    echo "ROS_DISTRO: $ROS_DISTRO"
fi

# Workspace Check
if [ -z "$COLCON_PREFIX_PATH" ]; then
    echo "[WARNING] COLCON_PREFIX_PATH is empty. You may not be in an active workspace."
fi

echo "Environment check completed successfully."
