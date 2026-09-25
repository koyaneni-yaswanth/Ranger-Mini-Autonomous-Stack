#!/usr/bin/env bash
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh"
echo "=============================================================================="
echo " LAUNCHING GAZEBO HARMONIC PHYSICS SIMULATION (MODULAR PIPER 6-DOF)"
echo "=============================================================================="
ros2 launch ranger_bringup sim.launch.py manipulator:=true manipulator_type:=piper headless:=false
