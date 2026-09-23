#!/usr/bin/env bash
echo "=============================================================================="
echo " RANGER MINI NEXT-GEN PLATFORM: HEALTH CHECK"
echo "=============================================================================="
PROJECT_DIR="/home/yash/ranger_mini_lyrical_2604_project"
WS_DIR="/home/yash/ranger_mini_lyrical_2604_ws"

# 1. Environment check
if [ -d "/opt/ros/lyrical" ] || [ -d "/opt/ros/humble" ]; then
    echo "[OK] Base ROS 2 installation present."
else
    echo "[FAIL] No ROS 2 installation found."
fi

# 2. GPU Check
if nvidia-smi >/dev/null 2>&1; then
    echo "[OK] NVIDIA GPU detected via WSL GPU-PV."
else
    echo "[WARN] NVIDIA GPU not responding via nvidia-smi."
fi

# 3. Workspace check
if [ -f "$WS_DIR/install/setup.bash" ]; then
    echo "[OK] Lyrical workspace built and ready."
else
    echo "[INFO] Workspace not yet built. Run ./env/build_lyrical.sh."
fi

# 4. Display check
if [ -n "$DISPLAY" ]; then
    echo "[OK] Display server active: $DISPLAY."
else
    echo "[WARN] DISPLAY variable not set."
fi
echo "=============================================================================="
