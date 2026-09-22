#!/usr/bin/env bash
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " RANGER MINI HEALTH CHECK (GO / NO-GO)"
echo "=============================================================================="
GO=1

if [ -d "/opt/ros/humble" ]; then
    echo "[OK] ROS 2 Humble installed."
else
    echo "[NO-GO] ROS 2 Humble missing."
    GO=0
fi

for ws in "/home/yash/ranger_mini_workbench" "/home/yash/ranger_mini_lyrical_ws" "/home/yash/ranger_mini_humble_ws"; do
    if [ -f "$ws/install/setup.bash" ]; then
        echo "[OK] Built workspace: $(basename $ws)"
    else
        echo "[WARN] Workspace not built: $(basename $ws)"
    fi
done

if [ -n "$DISPLAY" ]; then
    echo "[OK] Graphical display active: $DISPLAY"
else
    echo "[WARN] No DISPLAY detected. Run in headless mode."
fi

if [ $GO -eq 1 ]; then
    echo "=============================================================================="
    echo " HEALTH CHECK RESULT: [GO] (Ready for Simulation / Supervised Hardware Test)"
    echo "=============================================================================="
else
    echo "=============================================================================="
    echo " HEALTH CHECK RESULT: [NO-GO] (Resolve blockers before proceeding)"
    echo "=============================================================================="
fi
