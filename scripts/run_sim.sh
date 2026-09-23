#!/usr/bin/env bash
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh"
WORLD="${1:-simple_indoor}"

echo "=============================================================================="
echo " LAUNCHING RANGER MINI SIMULATION (World: $WORLD)"
echo "=============================================================================="
ros2 launch ranger_bringup sim.launch.py world:="$WORLD"
