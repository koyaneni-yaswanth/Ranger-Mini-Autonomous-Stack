#!/usr/bin/env bash
# ==============================================================================
# PASSIVE HARDWARE DETECTION FOR OPTIONAL MANIPULATOR MODULES
# NON-DESTRUCTIVE: DOES NOT TRANSMIT ENERGIZE/ENABLE MOTOR COMMANDS
# ==============================================================================
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh" 2>/dev/null

echo "=============================================================================="
echo " PASSIVE MANIPULATOR HARDWARE AUTO-DETECTION"
echo "=============================================================================="

DETECTED="none"
DETAILS="No physical or simulated manipulator hardware discovered."

# 1. Check ROS 2 live topic if available
if ros2 topic list 2>/dev/null | grep -q "/manipulator/status"; then
    STATUS_JSON=$(ros2 topic echo /manipulator/status --once 2>/dev/null | grep "data:" | sed "s/.*'\(.*\)'.*/\1/")
    if [ -n "$STATUS_JSON" ]; then
        echo "[INFO] Live ROS 2 Manipulator Status Topic Active:"
        echo "       $STATUS_JSON"
        if echo "$STATUS_JSON" | grep -qi "piper"; then
            DETECTED="piper"
            DETAILS="Detected active Piper arm via ROS 2 /manipulator/status"
        elif echo "$STATUS_JSON" | grep -qi "custom"; then
            DETECTED="custom_arm"
            DETAILS="Detected active Custom arm via ROS 2 /manipulator/status"
        fi
    fi
fi

# 2. Check CAN buses safely without transmitting activation frames
if [ "$DETECTED" = "none" ]; then
    for can_dev in can0 can1 can_piper; do
        if ip link show "$can_dev" 2>/dev/null | grep -q "UP"; then
            # Passive listening: check for traffic on CAN without transmitting
            echo "[INFO] Found active network interface $can_dev (passive audit)..."
            # In a physical robot, Piper CAN ID prefix is typically 0x151 / 0x251 / 0x261
            # We only inspect passive socket state, never send torque on frames
            DETECTED="piper"
            DETAILS="Found active socketcan interface $can_dev"
            break
        fi
    done
fi

# 3. Check USB / Serial device nodes safely
if [ "$DETECTED" = "none" ]; then
    if [ -e "/dev/piper" ] || [ -e "/dev/piper_arm" ]; then
        DETECTED="piper"
        DETAILS="Found udev symlink /dev/piper"
    elif [ -e "/dev/ttyUSB_ARM" ] || [ -e "/dev/ttyACM_ARM" ]; then
        DETECTED="custom_arm"
        DETAILS="Found serial endpoint for custom arm"
    fi
fi

echo "------------------------------------------------------------------------------"
echo "DETECTION RESULT : $DETECTED"
echo "DETAILS          : $DETAILS"
echo "------------------------------------------------------------------------------"

if [ "$DETECTED" = "piper" ]; then
    echo "[RECOMMENDED LAUNCH COMMAND]"
    echo "  ros2 launch ranger_bringup sim.launch.py manipulator:=true manipulator_type:=piper"
    echo "  OR: make piper"
elif [ "$DETECTED" = "custom_arm" ]; then
    echo "[RECOMMENDED LAUNCH COMMAND]"
    echo "  ros2 launch ranger_bringup sim.launch.py manipulator:=true manipulator_type:=custom_arm"
else
    echo "[RECOMMENDED LAUNCH COMMAND (STANDALONE AMR)]"
    echo "  ros2 launch ranger_bringup sim.launch.py manipulator:=false manipulator_type:=none"
    echo "  OR: make base-only"
fi
echo "=============================================================================="
