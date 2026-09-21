#!/bin/bash
set -e

echo "=== PHYSICAL HARDWARE INTERFACE AUDIT ==="
echo "Auditing SocketCAN interface 'can0'..."
if ip link show can0 >/dev/null 2>&1; then
    echo "[OK] SocketCAN interface can0 is detected."
else
    echo "[BLOCKED] Physical robot hardware not connected to WSL2 host (can0 not found)."
fi

echo "Auditing USB/Serial sensors..."
SERIAL_COUNT=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | wc -l)
if [ "$SERIAL_COUNT" -gt 0 ]; then
    echo "[OK] Found $SERIAL_COUNT serial devices."
else
    echo "[BLOCKED] Physical USB sensors (LiDAR / Camera) not attached to host."
fi
exit 0
