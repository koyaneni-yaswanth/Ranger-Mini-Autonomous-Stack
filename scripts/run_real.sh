#!/usr/bin/env bash
PROJECT_DIR="/home/yash/ranger_mini_lyrical_2604_project"
source "$PROJECT_DIR/env/source_lyrical.sh"

echo "=============================================================================="
echo " LAUNCHING PHYSICAL RANGER MINI HARDWARE INTERFACE"
echo "=============================================================================="
if ! ip link show can0 >/dev/null 2>&1; then
    echo "[BLOCKED] Physical hardware not detected (can0 not found). Cannot launch real robot."
    exit 1
fi

ros2 launch ranger_bringup hardware.launch.py can_interface:=can0
