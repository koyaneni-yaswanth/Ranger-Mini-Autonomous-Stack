#!/usr/bin/env bash
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " [10/12] PHYSICAL HARDWARE & DEVICE CONNECTIVITY CHECK"
echo "=============================================================================="
echo "Auditing SocketCAN interface 'can0'..."
if ip link show can0 2>/dev/null | grep -q "can0"; then
    echo "[PASS] SocketCAN can0 detected on host."
else
    echo "[BLOCKED] Physical robot hardware not connected (can0 not found)."
fi

echo "Auditing USB/Serial sensors (/dev/ttyUSB*, /dev/ttyACM*)..."
if ls /dev/ttyUSB* /dev/ttyACM* 1>/dev/null 2>&1; then
    echo "[PASS] Physical serial devices detected."
    ls -l /dev/ttyUSB* /dev/ttyACM*
else
    echo "[BLOCKED] Physical USB sensors (LiDAR / Camera) not attached to host."
fi
echo "=============================================================================="
echo "[STATUS] Hardware check complete (Strict Zero Fabrication enforced)."
