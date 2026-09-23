#!/usr/bin/env bash
PROJECT_DIR="/home/yash/ranger_mini_lyrical_2604_project"
source "$PROJECT_DIR/env/source_lyrical.sh"
MAP_FILE="${1:-/home/yash/ranger_mini_workbench/backups/my_warehouse_map.yaml}"

echo "=============================================================================="
echo " LAUNCHING NAV2 AUTONOMOUS NAVIGATION (Map: $MAP_FILE)"
echo "=============================================================================="
ros2 launch ranger_navigation navigation.launch.py map:="$MAP_FILE"
