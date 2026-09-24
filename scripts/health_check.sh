#!/usr/bin/env bash
echo "=============================================================================="
echo " RANGER MINI NEXT-GEN PLATFORM: HEALTH CHECK & AUDIT"
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

# 5. Configs & Schemas Check
if [ -f "$PROJECT_DIR/config/task_schema.json" ] && [ -f "$PROJECT_DIR/config/object_database.yaml" ]; then
    echo "[OK] Task Schema and Object Database configurations present."
else
    echo "[FAIL] Missing task_schema.json or object_database.yaml in config/."
fi

# 6. Python AI & Perception Stack Verification
python3 -c "
import yaml, jsonschema, cv2, numpy
print('[OK] Core AI dependencies verified (yaml, jsonschema, cv2, numpy).')
" 2>/dev/null || echo "[FAIL] Missing Python AI dependencies."

# 7. ROS 2 Node Entrypoints Check
if [ -f "$WS_DIR/install/ranger_missions/lib/ranger_missions/ai_task_interpreter" ] && \
   [ -f "$WS_DIR/install/ranger_missions/lib/ranger_missions/autonomous_task_orchestrator" ] && \
   [ -f "$WS_DIR/install/ranger_vision/lib/ranger_vision/ai_object_localizer" ]; then
    echo "[OK] AI Task Interpreter, Orchestrator, and Perception nodes compiled and ready."
else
    echo "[WARN] Some AI/Perception node binaries not yet installed in workspace."
fi

echo "=============================================================================="
