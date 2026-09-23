#!/usr/bin/env bash
echo "=============================================================================="
echo " [HARDWARE CHECK] SOCKETCAN & SENSOR AUDIT (ZERO FABRICATION RULE)"
echo "=============================================================================="
if ip link show can0 >/dev/null 2>&1; then
    echo "[OK] SocketCAN can0 detected."
    ip -details link show can0
else
    echo "[BLOCKED] Physical robot hardware not connected (can0 not found)."
fi

if ls /dev/ttyUSB* /dev/ttyACM* 1>/dev/null 2>&1; then
    echo "[OK] Serial sensor devices found:"
    ls -l /dev/ttyUSB* /dev/ttyACM*
else
    echo "[BLOCKED] Physical USB sensors (LiDAR / Camera) not attached."
fi
echo "=============================================================================="
echo "[STATUS] Hardware audit complete."
