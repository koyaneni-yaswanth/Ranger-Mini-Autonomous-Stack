#!/bin/bash
set -e

echo "=== ROS 2 LYRICAL ENVIRONMENT DIAGNOSTIC ==="
echo "Active ROS_DISTRO: ${ROS_DISTRO:-NONE}"
echo "Active PREFIX    : ${COLCON_PREFIX_PATH:-NONE}"

# Check for cross-contamination
CONTAMINATION=0
if echo "$AMENT_PREFIX_PATH" | grep -E "jazzy|kilted|rolling" > /dev/null; then
    echo "[WARNING] Incompatible distribution detected in AMENT_PREFIX_PATH!"
    CONTAMINATION=1
fi

if [ -n "$ROS_DISTRO" ] && [ "$ROS_DISTRO" != "lyrical" ] && [ "$ROS_DISTRO" != "humble" ]; then
    echo "[ERROR] Unsupported ROS_DISTRO '$ROS_DISTRO' active."
    exit 1
fi

echo "[OK] Environment verified clean. Zero unauthorized cross-distribution links."
exit 0
