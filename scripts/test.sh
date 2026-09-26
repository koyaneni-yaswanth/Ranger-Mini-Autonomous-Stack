#!/usr/bin/env bash
set -e
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

echo "=============================================================================="
echo "          PROJECT JARVIS-X: MASTER AUTOMATED TEST ENGINE"
echo "=============================================================================="
bash "$PROJECT_DIR/scripts/check_environment.sh"
bash "$PROJECT_DIR/scripts/check_ros.sh"
bash "$PROJECT_DIR/scripts/check_gpu.sh"
bash "$PROJECT_DIR/scripts/check_network.sh"
bash "$PROJECT_DIR/scripts/check_hardware.sh"

source /opt/ros/lyrical/setup.bash
source "$WS_DIR/install/setup.bash"

echo "------------------------------------------------------------------------------"
echo " [TEST 1/7] RUNNING AI TASK EXECUTION & SAFETY VALIDATION SUITE"
echo "------------------------------------------------------------------------------"
python3 "$PROJECT_DIR/tests/test_ai_task_execution.py"

echo "------------------------------------------------------------------------------"
echo " [TEST 2/7] RUNNING TASK / SKILL LAYER & ROBOT ABSTRACTION SUITE"
echo "------------------------------------------------------------------------------"
python3 "$PROJECT_DIR/tests/test_skills_and_hal.py"

echo "------------------------------------------------------------------------------"
echo " [TEST 3/7] RUNNING JARVIS COGNITIVE BRAIN & PLANNING SUITE"
echo "------------------------------------------------------------------------------"
python3 "$PROJECT_DIR/tests/test_jarvis_brain.py"

echo "------------------------------------------------------------------------------"
echo " [TEST 4/7] RUNNING VOICE & MULTI-TIER MEMORY SUITES"
echo "------------------------------------------------------------------------------"
python3 "$PROJECT_DIR/tests/test_voice_system.py"
python3 "$PROJECT_DIR/tests/test_memory_system.py"

echo "------------------------------------------------------------------------------"
echo " [TEST 5/7] RUNNING INDEPENDENT SAFETY SUPERVISOR SUITE"
echo "------------------------------------------------------------------------------"
python3 "$PROJECT_DIR/tests/test_safety_manager.py"

echo "------------------------------------------------------------------------------"
echo " [TEST 6/7] RUNNING SECTION 69 TEST MATRIX & SECTION 65 FAILURE MODES"
echo "------------------------------------------------------------------------------"
python3 "$PROJECT_DIR/tests/test_section_69_matrix.py"

echo "------------------------------------------------------------------------------"
echo " [TEST 7/7] RUNNING NAV2 COSTMAP BOUNDS & IMPORT REGRESSION TEST (SECTIONS 20 & 77)"
echo "------------------------------------------------------------------------------"
python3 "$PROJECT_DIR/tests/test_costmap_bounds_regression.py"

echo "=============================================================================="
echo "[PASS] All pre-flight, safety, cognitive, skill, and regression test suites completed successfully."
