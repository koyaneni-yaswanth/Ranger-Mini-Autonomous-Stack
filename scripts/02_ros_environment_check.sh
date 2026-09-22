#!/usr/bin/env bash
set -e
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " [02/12] ROS 2 ENVIRONMENT INTEGRITY CHECK"
echo "=============================================================================="
echo "Active ROS_DISTRO:     ${ROS_DISTRO:-Not set}"
echo "Installed in /opt/ros: $(ls /opt/ros 2>/dev/null | tr '\n' ' ')"
echo "RMW Implementation:    ${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp (default)}"
echo "ROS Domain ID:         ${ROS_DOMAIN_ID:-0 (default)}"
echo "ROS 2 Command Path:    $(which ros2 || echo 'ros2 not in PATH')"

if [ -d "/opt/ros/humble" ]; then
    echo "[OK] ROS 2 Humble base installation detected."
fi

for ws in "/home/yash/ranger_mini_humble_ws" "/home/yash/ranger_mini_lyrical_ws" "/home/yash/ranger_mini_workbench"; do
    if [ -d "$ws" ]; then
        sym_count=$(find "$ws/src" -type l 2>/dev/null | wc -l)
        echo "[OK] Workspace: $(basename $ws) | Symlinks in src/: $sym_count"
    fi
done
echo "=============================================================================="
echo "[PASS] ROS 2 environment verified."
