#!/usr/bin/env bash
# JARVIS-X Stage 5: Full End-to-End Simulation & Autonomous Embodied Mission
# Verified live in Ubuntu 26.04 WSL2 with NVIDIA D3D12 acceleration
set -e

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

source "$PROJECT_DIR/env/source_lyrical.sh"
source "$WS_DIR/install/setup.bash"

export DISPLAY="${DISPLAY:-:0}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"
export QT_X11_NO_MITSHM=1

HEADLESS="${HEADLESS:-false}"
AUTO_TEST="${AUTO_TEST:-false}"
WORLD="${1:-red_cube_world.sdf}"

if [ "$HEADLESS" = "true" ] || [ ! -t 0 ]; then
    AUTO_TEST="true"
fi

echo "=============================================================================="
echo "    LAUNCHING JARVIS-X STAGE 5: FULL AUTONOMOUS EMBODIED MISSION PIPELINE     "
echo "=============================================================================="
echo " World:            $WORLD"
echo " Headless:         $HEADLESS"
echo " Auto Test:        $AUTO_TEST"
echo " Display:          $DISPLAY (NVIDIA RTX 5060 / D3D12)"
echo " Subsystems:       Gazebo + Base + Piper Arm + Nav2 + MoveIt2 + Vision + JARVIS"
echo "=============================================================================="

SIM_PID=""
RVIZ_PID=""
INTERP_PID=""
WORLD_PID=""
ORCH_PID=""
BRAIN_PID=""

cleanup() {
    echo ""
    echo "Stopping Stage 5 Full Simulation..."
    [ -n "$BRAIN_PID" ] && kill -2 "$BRAIN_PID" 2>/dev/null || true
    [ -n "$ORCH_PID" ] && kill -2 "$ORCH_PID" 2>/dev/null || true
    [ -n "$WORLD_PID" ] && kill -2 "$WORLD_PID" 2>/dev/null || true
    [ -n "$INTERP_PID" ] && kill -2 "$INTERP_PID" 2>/dev/null || true
    [ -n "$RVIZ_PID" ] && kill -2 "$RVIZ_PID" 2>/dev/null || true
    [ -n "$SIM_PID" ] && kill -2 "$SIM_PID" 2>/dev/null || true
    sleep 2
    pkill -9 -f "jarvis_brain" 2>/dev/null || true
    pkill -9 -f "autonomous_task_orchestrator" 2>/dev/null || true
    pkill -9 -f "semantic_world_model" 2>/dev/null || true
    pkill -9 -f "ai_task_interpreter" 2>/dev/null || true
    pkill -9 -f "move_group" 2>/dev/null || true
    pkill -9 -f "nav2_" 2>/dev/null || true
    pkill -9 -f "slam_toolbox" 2>/dev/null || true
    pkill -9 -f "ros_gz" 2>/dev/null || true
    pkill -9 -f "gz_sim|gz-sim" 2>/dev/null || true
    pkill -9 -f "rviz2" 2>/dev/null || true
    echo "[OK] Stage 5 Full Simulation stopped cleanly."
}
trap cleanup EXIT INT TERM

# Launch Gazebo + Base + Piper + ros2_control + Nav2 + MoveIt 2 + Vision
ros2 launch ranger_bringup sim.launch.py \
    world:="$WORLD" \
    headless:="$HEADLESS" \
    manipulator:=true \
    manipulator_type:=piper \
    base_only:=false \
    enable_nav:=true \
    enable_vision:=true \
    enable_moveit:=true > /tmp/sim_full.log 2>&1 &
SIM_PID=$!

echo "Waiting for simulation /clock and odometry..."
CLOCK_ONLINE=false
for i in {1..30}; do
    if ros2 topic list 2>/dev/null | grep -q "/clock"; then
        echo "[OK] Simulation clock active ($i s)."
        CLOCK_ONLINE=true
        break
    fi
    sleep 1
done

if [ "$CLOCK_ONLINE" != "true" ]; then
    echo "[FAIL] Simulation clock failed to start within 30s. Logs:"
    cat /tmp/sim_full.log | tail -n 25
    exit 1
fi

echo "Waiting for ros2_control base & arm controllers to activate..."
for i in {1..30}; do
    CTRLS=$(ros2 control list_controllers 2>/dev/null || true)
    if echo "$CTRLS" | grep -q "traction_controller.*active" && echo "$CTRLS" | grep -q "piper_arm_controller.*active"; then
        echo "[OK] Traction and Piper arm controllers active ($i s)."
        break
    fi
    sleep 1
done

echo "Waiting for camera streams & AI object localizer..."
for i in {1..20}; do
    if ros2 node list 2>/dev/null | grep -q "ai_object_localizer"; then
        echo "[OK] ai_object_localizer node active ($i s)."
        break
    fi
    sleep 1
done

# Launch JARVIS Cognitive Stack
echo "Launching JARVIS Embodied Cognitive Stack..."
ros2 run ranger_missions ai_task_interpreter > /tmp/ai_interp.log 2>&1 &
INTERP_PID=$!

ros2 run ranger_missions semantic_world_model > /tmp/world_model.log 2>&1 &
WORLD_PID=$!

ros2 run ranger_missions autonomous_task_orchestrator > /tmp/orchestrator.log 2>&1 &
ORCH_PID=$!

ros2 run jarvis_core jarvis_brain_node.py > /tmp/jarvis_brain.log 2>&1 &
BRAIN_PID=$!

# Launch RViz visualizer if not headless and not auto test
if [ "$HEADLESS" != "true" ] && [ "$AUTO_TEST" != "true" ]; then
    echo "Launching RViz2 visualizer..."
    rviz2 -d "$PROJECT_DIR/config/slam.rviz" --ros-args -p use_sim_time:=true >/dev/null 2>&1 &
    RVIZ_PID=$!
fi

sleep 3

# Health Status Report
echo ""
echo "=============================================================================="
echo "          JARVIS-X FULL EMBODIED MISSION PIPELINE RUNTIME HEALTH STATUS       "
echo "=============================================================================="

TOPICS=$(ros2 topic list 2>/dev/null || true)
CTRLS=$(ros2 control list_controllers 2>/dev/null || true)
NODES=$(ros2 node list 2>/dev/null || true)
ACTIONS=$(ros2 action list 2>/dev/null || true)

GZ_STATUS="FAIL"
CLOCK_STATUS="FAIL"
ROBOT_STATUS="FAIL"
CHASSIS_STATUS="FAIL"
ARM_STATUS="FAIL"
NAV2_STATUS="FAIL"
MOVEIT_STATUS="FAIL"
VISION_STATUS="FAIL"
ORCH_STATUS="FAIL"
BRAIN_STATUS="FAIL"

pgrep -f "gz-sim|gz sim" >/dev/null 2>&1 && GZ_STATUS="ALIVE"
echo "$TOPICS" | grep -q "^/clock$" && CLOCK_STATUS="STREAMING"
pgrep -f "robot_state_publisher" >/dev/null 2>&1 && ROBOT_STATUS="PRESENT"
echo "$CTRLS" | grep -q "traction_controller.*active" && CHASSIS_STATUS="ACTIVE"
echo "$CTRLS" | grep -q "piper_arm_controller.*active" && ARM_STATUS="ACTIVE"
echo "$ACTIONS" | grep -q "/navigate_to_pose" && NAV2_STATUS="READY"
pgrep -f "move_group" >/dev/null 2>&1 && MOVEIT_STATUS="ONLINE"
echo "$TOPICS" | grep -q "^/vision/target_pose$" && VISION_STATUS="STREAMING"
echo "$NODES" | grep -q "autonomous_task_orchestrator" && ORCH_STATUS="ONLINE"
pgrep -f "jarvis_brain" >/dev/null 2>&1 && BRAIN_STATUS="ONLINE"

echo " Gazebo:               $GZ_STATUS"
echo " /clock:               $CLOCK_STATUS"
echo " Ranger entity:        $ROBOT_STATUS"
echo " Chassis Controller:   $CHASSIS_STATUS"
echo " Piper Arm Controller: $ARM_STATUS"
echo " Nav2 Action Server:   $NAV2_STATUS"
echo " MoveIt 2 MoveGroup:   $MOVEIT_STATUS"
echo " AI 3D Perception:     $VISION_STATUS"
echo " Task Orchestrator:    $ORCH_STATUS"
echo " JARVIS Brain:         $BRAIN_STATUS"
echo "=============================================================================="

if [ "$AUTO_TEST" = "true" ]; then
    echo "Running automated Full Autonomous Mission test..."
    python3 "$PROJECT_DIR/tests/test_mission_e2e.py"
    TEST_EXIT=$?
    if [ $TEST_EXIT -eq 0 ]; then
        echo "=============================================================================="
        echo "      [STAGE 5 END-TO-END AUTONOMOUS MISSION: VERIFIED & PASS]                "
        echo "=============================================================================="
        exit 0
    else
        echo "[STAGE 5 FAIL] End-to-end mission test failed with code $TEST_EXIT."
        exit $TEST_EXIT
    fi
fi

echo " Stage 5 Full Simulation Active. Ready for voice/text tasks."
echo " Press Enter or Ctrl+C to terminate."
echo "=============================================================================="

read -r || true