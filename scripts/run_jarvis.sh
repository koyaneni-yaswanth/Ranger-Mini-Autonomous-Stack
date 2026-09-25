#!/usr/bin/env bash
# JARVIS-X Embodied AI Robot Master Interactive Console
set -e

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

source "$PROJECT_DIR/env/source_lyrical.sh"
source "$WS_DIR/install/setup.bash"

echo "=============================================================================="
echo "          PROJECT CODENAME: JARVIS-X EMBODIED AI ROBOT"
echo "  Multimodal AI | Voice | Vision | Memory | Reasoning | Mobile Manipulation"
echo "=============================================================================="

# Launch JARVIS Cognitive Subsystems in background
echo "[1/3] Starting Independent Safety Manager..."
ros2 run jarvis_core safety_manager > /tmp/jarvis_safety.log 2>&1 &
PID_SAFETY=$!

echo "[2/3] Starting Dynamic Semantic World Model..."
ros2 run jarvis_core world_model > /tmp/jarvis_world.log 2>&1 &
PID_WORLD=$!

echo "[3/3] Starting JARVIS-X Central Embodied Brain..."
ros2 run jarvis_core jarvis_brain > /tmp/jarvis_brain.log 2>&1 &
PID_BRAIN=$!

cleanup() {
    echo ""
    echo "Shutting down JARVIS-X cognitive subsystems..."
    kill -2 "$PID_BRAIN" 2>/dev/null || true
    kill -2 "$PID_WORLD" 2>/dev/null || true
    kill -2 "$PID_SAFETY" 2>/dev/null || true
    echo "[OK] JARVIS offline."
}
trap cleanup EXIT INT TERM

sleep 2

echo "=============================================================================="
echo " JARVIS IS ONLINE AND LISTENING."
echo " Try saying or typing:"
echo "   - 'JARVIS, find the red cube, pick it up, and put it on the table.'"
echo "   - 'JARVIS, inspect the room and tell me what you see.'"
echo "   - 'JARVIS, how is the battery?'"
echo "   - 'JARVIS, bring me the box.' (Tests Ambiguity Resolution)"
echo "   - 'JARVIS, stop.' (Immediate Safety Interrupt)"
echo "   - 'quit' or 'exit' to terminate"
echo "=============================================================================="
echo ""

# Interactive conversational prompt
while true; do
    echo -n "USER > "
    read -r user_input || break
    
    if [ -z "$user_input" ]; then
        continue
    fi
    
    if [ "$user_input" = "quit" ] || [ "$user_input" = "exit" ] || [ "$user_input" = "q" ]; then
        break
    fi

    # Dispatch to speech topic
    ros2 topic pub --once /jarvis/recognized_speech std_msgs/msg/String "data: '$user_input'" >/dev/null 2>&1
    sleep 1
done
