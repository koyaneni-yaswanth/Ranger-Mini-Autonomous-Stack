#!/usr/bin/env bash
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh"
WORLD="${1:-warehouse.sdf}"
HEADLESS="${HEADLESS:-true}"

echo "=============================================================================="
echo " LAUNCHING RANGER MINI STANDALONE AMR (BASE-ONLY MODE)"
echo " Manipulator: DISABLED | World: $WORLD | Headless: $HEADLESS"
echo "=============================================================================="
ros2 launch ranger_bringup sim.launch.py world:="$WORLD" headless:="$HEADLESS" manipulator:=false manipulator_type:=none
