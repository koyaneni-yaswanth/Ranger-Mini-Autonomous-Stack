#!/usr/bin/env bash
echo "=============================================================================="
echo " RANGER MINI NEXT-GEN PLATFORM: HEALTH CHECK"
echo "=============================================================================="
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

# 1. Environment check
if [ -d "/opt/ros/lyrical" ]; then
    echo "[OK] ROS 2 Lyrical installation present at /opt/ros/lyrical."
else
    echo "[FAIL] ROS 2 Lyrical installation not found at /opt/ros/lyrical."
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
    echo "[INFO] Workspace not yet built. Run make build."
fi

# 4. Display check
if [ -n "$DISPLAY" ]; then
    echo "[OK] Display server active: $DISPLAY."
else
    echo "[WARN] DISPLAY variable not set."
fi
echo "=============================================================================="
