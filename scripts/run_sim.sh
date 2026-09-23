#!/usr/bin/env bash
PROJECT_DIR="/home/yash/ranger_mini_lyrical_2604_project"
source "$PROJECT_DIR/env/source_lyrical.sh"
WORLD="${1:-simple_indoor}"

echo "=============================================================================="
echo " LAUNCHING RANGER MINI SIMULATION (World: $WORLD)"
echo "=============================================================================="
ros2 launch ranger_bringup sim.launch.py world:="$WORLD"
