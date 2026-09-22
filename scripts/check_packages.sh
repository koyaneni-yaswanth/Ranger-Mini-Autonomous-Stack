#!/bin/bash
set -e

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$WS_DIR/install/setup.bash" ]; then
    source "$WS_DIR/install/setup.bash"
else
    echo "[ERROR] install/setup.bash not found. Run ./build.sh first."
    exit 1
fi

REQUIRED_PACKAGES=(
    "amr_x_interfaces"
    "ranger_description"
    "ranger_control"
    "ranger_navigation"
    "ranger_perception"
    "nero_description"
    "ranger_dashboard"
    "ranger_manipulation"
    "ranger_missions"
    "ranger_slam"
    "ranger_tests"
    "ranger_vision"
    "ranger_bringup"
    "ranger_simulation"
    "amr_active_perception"
    "amr_fleet_manager"
    "amr_world_model"
    "tutorial_basic_teleop"
    "tutorial_sensor_verification"
    "tutorial_autonomous_navigation"
    "tutorial_manipulation_pick_place"
)

echo "=== VERIFYING PACKAGE DISCOVERY (21 PACKAGES) ==="
MISSING=0
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ros2 pkg prefix "$pkg" >/dev/null 2>&1; then
        echo "  [FOUND] $pkg -> $(ros2 pkg prefix "$pkg")"
    else
        echo "  [MISSING] $pkg"
        MISSING=$((MISSING + 1))
    fi
done

if [ "$MISSING" -eq 0 ]; then
    echo "[OK] All 21 required packages successfully discovered."
    exit 0
else
    echo "[ERROR] $MISSING package(s) missing from discovery!"
    exit 1
fi
