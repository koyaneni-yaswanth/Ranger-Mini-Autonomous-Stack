#!/usr/bin/env bash
set -e
PROJECT_DIR="/home/yash/ranger_mini_lyrical_2604_project"
source "$PROJECT_DIR/env/source_lyrical.sh"

if [ "$ROS_DISTRO" != "lyrical" ]; then
    echo "[ERROR] Expected ROS_DISTRO=lyrical, but detected $ROS_DISTRO! Aborting."
    exit 1
fi

WS_DIR="/home/yash/ranger_mini_lyrical_2604_ws"
cd "$WS_DIR"
echo "[INFO] Compiling Lyrical Workspace at $WS_DIR..."
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source "$WS_DIR/install/setup.bash"
echo "[PASS] Lyrical Workspace build succeeded."
