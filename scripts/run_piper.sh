#!/usr/bin/env bash
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh"
WORLD="${1:-warehouse.sdf}"
HEADLESS="${HEADLESS:-true}"

echo "=============================================================================="
echo " LAUNCHING RANGER MINI MOBILE MANIPULATOR (PIPER 6-DOF ARM MODE)"
echo " Manipulator: ENABLED (Piper) | World: $WORLD | Headless: $HEADLESS"
echo "=============================================================================="
ros2 launch ranger_bringup sim.launch.py world:="$WORLD" headless:="$HEADLESS" manipulator:=true manipulator_type:=piper
