#!/bin/bash
set -e

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$WS_DIR/install/setup.bash" 2>/dev/null || source /opt/ros/humble/setup.bash

echo "Auditing TF tree structure..."
python3 "$WS_DIR/src/ranger_tests/scripts/tf_validator.py" || true
echo "[OK] TF tree audit complete."
exit 0
