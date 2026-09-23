#!/usr/bin/env bash
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh"
MAP_FILE="${1:-$PROJECT_DIR/../ranger_mini_lyrical_2604_ws/src/ranger_navigation/maps/warehouse.yaml}"

echo "=============================================================================="
echo " LAUNCHING NAV2 AUTONOMOUS NAVIGATION (Map: $MAP_FILE)"
echo "=============================================================================="
ros2 launch ranger_navigation navigation.launch.py map:="$MAP_FILE"
