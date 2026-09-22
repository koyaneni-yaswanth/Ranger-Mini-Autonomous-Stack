#!/bin/bash
set -e

# Source base ROS 2 distribution
if [ -f "/opt/ros/lyrical/setup.bash" ]; then
    source /opt/ros/lyrical/setup.bash
elif [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$WS_DIR/install/setup.bash" ]; then
    source "$WS_DIR/install/setup.bash"
fi

URDF_XACRO="$WS_DIR/src/ranger_description/urdf/ranger_mini.urdf.xacro"

echo "=== ROBOT DESCRIPTION & KINEMATICS AUDIT ==="
echo "Source Xacro: $URDF_XACRO"

TMP_URDF="/tmp/ranger_mini_audit.urdf"
xacro "$URDF_XACRO" > "$TMP_URDF"
check_urdf "$TMP_URDF"
echo "[OK] URDF parsed cleanly without kinematic or inertial breaks."
exit 0
