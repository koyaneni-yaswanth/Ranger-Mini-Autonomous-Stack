#!/usr/bin/env bash
PROJECT_DIR="/home/yash/ranger_mini_lyrical_2604_project"
source "$PROJECT_DIR/env/source_lyrical.sh"

echo "=============================================================================="
echo " LAUNCHING SLAM TOOLBOX ONLINE ASYNC MAPPING"
echo "=============================================================================="
ros2 launch ranger_slam mapping.launch.py
