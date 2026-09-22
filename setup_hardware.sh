#!/usr/bin/env bash
# ==============================================================================
# RANGER MINI AUTONOMOUS STACK: PHYSICAL HARDWARE INTERFACE SETUP
# ==============================================================================

CAN_IF="${1:-can0}"
BITRATE="${2:-500000}"

echo "[INFO] Checking SocketCAN interface '$CAN_IF'..."
if ip link show "$CAN_IF" >/dev/null 2>&1; then
    echo "[INFO] SocketCAN interface '$CAN_IF' detected."
    # Check if UP
    if ip link show "$CAN_IF" | grep -q "UP"; then
        echo "[OK] '$CAN_IF' is already UP."
    else
        echo "[INFO] Bringing up '$CAN_IF' with bitrate $BITRATE..."
        sudo ip link set "$CAN_IF" up type can bitrate "$BITRATE" 2>/dev/null || echo "[WARN] Need sudo permissions to bring up $CAN_IF."
    fi
else
    echo "[WARN] Physical CAN interface '$CAN_IF' NOT found."
    echo "[INFO] For testing without physical hardware, you can load vcan:"
    echo "       sudo modprobe vcan && sudo ip link add dev vcan0 type vcan && sudo ip link set up vcan0"
fi

echo "[INFO] Checking serial/USB peripherals..."
if ls /dev/ttyUSB* /dev/ttyACM* 1>/dev/null 2>&1; then
    echo "[OK] Serial devices found:"
    ls -l /dev/ttyUSB* /dev/ttyACM*
else
    echo "[WARN] No USB serial devices detected."
fi
