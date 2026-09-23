#!/usr/bin/env bash
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh"

echo "=============================================================================="
echo " LAUNCHING SLAM TOOLBOX ONLINE ASYNC MAPPING"
echo "=============================================================================="
ros2 launch ranger_slam mapping.launch.py
