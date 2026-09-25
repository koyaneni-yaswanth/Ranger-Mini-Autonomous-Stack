#!/usr/bin/env bash
set -e
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

echo "=============================================================================="
echo " RANGER MINI AUTOMATED TEST ENGINE"
echo "=============================================================================="
bash "$PROJECT_DIR/scripts/check_environment.sh"
bash "$PROJECT_DIR/scripts/check_ros.sh"
bash "$PROJECT_DIR/scripts/check_gpu.sh"
bash "$PROJECT_DIR/scripts/check_network.sh"
bash "$PROJECT_DIR/scripts/check_hardware.sh"

echo "------------------------------------------------------------------------------"
echo " RUNNING AI TASK EXECUTION & SAFETY VALIDATION SUITE"
echo "------------------------------------------------------------------------------"
source /opt/ros/lyrical/setup.bash
source "$WS_DIR/install/setup.bash"
python3 "$PROJECT_DIR/tests/test_ai_task_execution.py"

echo "------------------------------------------------------------------------------"
echo " RUNNING TASK / SKILL LAYER & ROBOT ABSTRACTION SUITE"
echo "------------------------------------------------------------------------------"
python3 "$PROJECT_DIR/tests/test_skills_and_hal.py"

echo "=============================================================================="
echo "[PASS] All pre-flight, safety policy, and automated tests completed successfully."
