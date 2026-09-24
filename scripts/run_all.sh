#!/usr/bin/env bash
# Master Autonomous Mobile Manipulator All-in-One Execution Script
set -e

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

source "$PROJECT_DIR/env/source_lyrical.sh"
source "$WS_DIR/install/setup.bash"

HEADLESS="${HEADLESS:-true}"
MISSION_PROMPT="${1:-Find the red object, pick it up, and place it at the target station}"

echo "=============================================================================="
echo "    RANGER MINI AUTONOMOUS MOBILE MANIPULATOR: RUN-ALL MASTER PIPELINE"
echo "=============================================================================="
echo " Mode: Modular Piper 6-DOF | Headless: $HEADLESS"
echo " Target Mission: \"$MISSION_PROMPT\""
echo "=============================================================================="

# Reset state file
rm -f /tmp/mission_state.txt
echo "IDLE" > /tmp/mission_state.txt

# Trap cleanup to terminate background processes on exit
SIM_PID=""
AI_INTERP_PID=""
WORLD_MODEL_PID=""
ORCHESTRATOR_PID=""

cleanup() {
    echo ""
    echo "=============================================================================="
    echo " SHUTTING DOWN ALL AUTONOMOUS STACK NODES..."
    echo "=============================================================================="
    [ -n "$ORCHESTRATOR_PID" ] && kill -2 "$ORCHESTRATOR_PID" 2>/dev/null || true
    [ -n "$WORLD_MODEL_PID" ] && kill -2 "$WORLD_MODEL_PID" 2>/dev/null || true
    [ -n "$AI_INTERP_PID" ] && kill -2 "$AI_INTERP_PID" 2>/dev/null || true
    [ -n "$SIM_PID" ] && kill -2 "$SIM_PID" 2>/dev/null || true
    sleep 2
    # Ensure all gz and ros2 are stopped
    pkill -9 -f "ros_gz" 2>/dev/null || true
    pkill -9 -f "gz_sim" 2>/dev/null || true
    pkill -9 -f "ranger_missions" 2>/dev/null || true
    pkill -9 -f "ranger_vision" 2>/dev/null || true
    echo "[OK] All processes stopped cleanly."
}
trap cleanup EXIT INT TERM

# 1. Run Pre-flight Health Check
echo "[1/5] Running platform health audit..."
bash "$PROJECT_DIR/scripts/health_check.sh"

# 2. Launch Simulation & Base Stack
echo ""
echo "[2/5] Launching Gazebo Harmonic + Robot Base + Piper 6-DOF + Perception..."
ros2 launch ranger_bringup sim.launch.py \
    headless:="$HEADLESS" \
    manipulator:=true \
    manipulator_type:=piper > /tmp/ranger_sim.log 2>&1 &
SIM_PID=$!
echo "      Simulation started with PID $SIM_PID. Waiting for clock and core topics..."

# Wait for /clock and robot_description
MAX_WAIT=35
WAIT_COUNT=0
while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if ros2 topic list 2>/dev/null | grep -q "/clock"; then
        echo "      [OK] Clock active."
        break
    fi
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
    echo "      [WARN] Simulation startup took longer than $MAX_WAIT seconds. Continuing..."
fi

# 3. Launch AI Stack
echo ""
echo "[3/5] Starting AI Task Interpreter and Semantic World Model..."
ros2 run ranger_missions ai_task_interpreter > /tmp/ai_interpreter.log 2>&1 &
AI_INTERP_PID=$!

ros2 run ranger_missions semantic_world_model > /tmp/world_model.log 2>&1 &
WORLD_MODEL_PID=$!

sleep 2

# 4. Launch Autonomous Task Orchestrator (17-state FSM)
echo ""
echo "[4/5] Starting 17-State Autonomous Task Orchestrator..."
ros2 run ranger_missions autonomous_task_orchestrator > /tmp/task_orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!

sleep 2

# 5. Dispatch Canonical Mission & Monitor
echo ""
echo "=============================================================================="
echo "[5/5] DISPATCHING CANONICAL AI MISSION:"
echo "      \"$MISSION_PROMPT\""
echo "=============================================================================="

# Publish task command
ros2 topic pub --once /ai/task_command std_msgs/msg/String "data: '$MISSION_PROMPT'" >/dev/null 2>&1

echo "Monitoring Mission State Machine Progress (timeout: 60s)..."
echo "------------------------------------------------------------------------------"

TIMEOUT=60
START_TIME=$(date +%s)
CURRENT_STATE=""

while true; do
    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TIME))

    if [ -f /tmp/mission_state.txt ]; then
        STATE_LINE=$(head -n 1 /tmp/mission_state.txt | tr -d '[:space:]')
        if [ -n "$STATE_LINE" ] && [ "$STATE_LINE" != "$CURRENT_STATE" ]; then
            CURRENT_STATE="$STATE_LINE"
            echo " [STATE FSM] (${ELAPSED}s) -> $CURRENT_STATE"
        fi
    fi

    if [ "$CURRENT_STATE" = "TASK_COMPLETE" ] || ([ "$CURRENT_STATE" = "IDLE" ] && [ $ELAPSED -gt 15 ]); then
        echo "------------------------------------------------------------------------------"
        echo "[MISSION SUCCESS] Full autonomous mission completed in $ELAPSED seconds!"
        break
    fi

    if [ "$CURRENT_STATE" = "ABORTED" ]; then
        echo "------------------------------------------------------------------------------"
        echo "[MISSION FAILED] Mission transitioned to ABORTED state."
        break
    fi

    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "------------------------------------------------------------------------------"
        echo "[TIMEOUT] Mission execution reached $TIMEOUT seconds limit. Last State: $CURRENT_STATE"
        break
    fi

    sleep 0.5
done

echo ""
echo "Recent Orchestrator Log Output:"
echo "------------------------------------------------------------------------------"
tail -n 25 /tmp/task_orchestrator.log || true
echo "=============================================================================="
