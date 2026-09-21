#!/bin/bash
set -e

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$WS_DIR/install/setup.bash" 2>/dev/null || source /opt/ros/humble/setup.bash

URDF_XACRO="$WS_DIR/src/ranger_description/urdf/ranger_mini.urdf.xacro"
echo "Validating Xacro: $URDF_XACRO"
TMP_URDF="/tmp/ranger_mini_check.urdf"
xacro "$URDF_XACRO" > "$TMP_URDF"
check_urdf "$TMP_URDF"
echo "[OK] URDF parsed cleanly without kinematic or inertial breaks."
exit 0
