#!/bin/bash
set -e

PLATFORM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LYRICAL_WS="$PLATFORM_DIR"

# Source base ROS 2
if [ -f "/opt/ros/lyrical/setup.bash" ]; then
    source /opt/ros/lyrical/setup.bash
elif [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
else
    echo "[ERROR] No ROS 2 installation found in /opt/ros/"
    exit 1
fi

# Source Lyrical workspace
if [ ! -f "$LYRICAL_WS/install/setup.bash" ]; then
    echo "[INFO] Lyrical workspace not yet compiled. Building now..."
    cd "$LYRICAL_WS"
    colcon build
fi

source "$LYRICAL_WS/install/setup.bash"
export ROS_DISTRO=lyrical

echo "=========================================================================="
echo "    RANGER MINI AUTONOMOUS STACK: ROS 2 LYRICAL SIMULATION RUNNER         "
echo "=========================================================================="
echo "Workspace        : $LYRICAL_WS"
echo "Active ROS_DISTRO: $ROS_DISTRO"
echo "Target Command   : ${*:-ros2 launch ranger_simulation gazebo.launch.py world:=warehouse.sdf}"
echo "=========================================================================="

if [ "$#" -gt 0 ]; then
    exec "$@"
else
    exec ros2 launch ranger_simulation gazebo.launch.py world:=warehouse.sdf
fi
