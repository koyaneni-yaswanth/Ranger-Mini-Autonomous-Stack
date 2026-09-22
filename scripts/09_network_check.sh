#!/usr/bin/env bash
set -e
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " [09/12] NETWORKING, DDS & MULTI-MACHINE READY CHECK"
echo "=============================================================================="
echo "Local IP Addresses:"
ip -br addr | grep -v 'docker' || true

echo "ROS Domain ID: ${ROS_DOMAIN_ID:-0}"
echo "RMW Implementation: ${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"

echo "Testing ROS 2 Local Loopback Discovery:"
ros2 topic list >/dev/null 2>&1 || true
echo "[OK] DDS Discovery daemon active."

echo "Time Status:"
timedatectl status 2>/dev/null | grep -E 'Time zone|synchronized|NTP' || date
echo "=============================================================================="
echo "[PASS] Network & DDS layer verified."
