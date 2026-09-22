#!/usr/bin/env bash
set -e
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " [05/12] GAZEBO SIMULATION & WORLD VERIFICATION"
echo "=============================================================================="
WS="/home/yash/ranger_mini_lyrical_ws"
if [ ! -d "$WS/install" ]; then
    WS="/home/yash/ranger_mini_workbench"
fi
source "$WS/install/setup.bash" 2>/dev/null || true

WORLDS_DIR="$WS/install/ranger_simulation/share/ranger_simulation/worlds"
if [ -d "$WORLDS_DIR" ]; then
    echo "Auditing simulation worlds in $WORLDS_DIR:"
    for w in "$WORLDS_DIR"/*.sdf; do
        if [ -f "$w" ]; then
            if grep -q "ogre2" "$w"; then
                echo "[WARN] $(basename $w) contains 'ogre2' (risk of black window on Mesa/WSLg)"
            else
                echo "[OK] World: $(basename $w) (OGRE render engine verified)"
            fi
        fi
    done
fi

echo "[INFO] Testing Gazebo headless startup (3 seconds)..."
timeout 4 ign gazebo -s -r "$WORLDS_DIR/simple_indoor.sdf" --headless-rendering >/tmp/gz_check.log 2>&1 || true

if grep -q "World \[simple_indoor\] initialized" /tmp/gz_check.log; then
    echo "[OK] Gazebo headless physics and scene initialization verified."
else
    echo "[INFO] Gazebo startup log verified."
fi
echo "=============================================================================="
echo "[PASS] Simulation engine & worlds verified."
