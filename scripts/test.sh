#!/usr/bin/env bash
set -e
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
echo "=============================================================================="
echo " RANGER MINI AUTOMATED TEST ENGINE"
echo "=============================================================================="
bash "$PROJECT_DIR/scripts/check_environment.sh"
bash "$PROJECT_DIR/scripts/check_ros.sh"
bash "$PROJECT_DIR/scripts/check_gpu.sh"
bash "$PROJECT_DIR/scripts/check_network.sh"
bash "$PROJECT_DIR/scripts/check_hardware.sh"
echo "=============================================================================="
echo "[PASS] All pre-flight and automated checks completed successfully."
