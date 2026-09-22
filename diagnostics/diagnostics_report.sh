#!/usr/bin/env bash
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " RANGER MINI PLATFORM DIAGNOSTICS REPORT"
echo " Generated: $(date)"
echo "=============================================================================="
echo "=== CPU & MEMORY ==="
free -h
top -bn1 | head -n 5

echo -e "\n=== GPU UTILIZATION ==="
nvidia-smi --query-gpu=name,driver_version,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv 2>/dev/null || echo "NVIDIA SMI unavailable"

echo -e "\n=== ACTIVE ROS 2 NODES ==="
ros2 node list 2>/dev/null || echo "No active ROS 2 graph"

echo -e "\n=== ACTIVE ROS 2 TOPICS ==="
ros2 topic list 2>/dev/null || echo "No active topics"
