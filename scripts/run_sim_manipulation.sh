#!/usr/bin/env bash
# JARVIS-X Stage 3: Piper 6-DOF Physical Manipulation Launcher & Verifier
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
echo "    LAUNCHING JARVIS-X STAGE 3: PIPER 6-DOF MANIPULATION SIMULATION           "
echo "=============================================================================="
echo " World:            $WORLD"
echo " Headless:         $HEADLESS"
echo " Auto Test:        $AUTO_TEST"
echo " Display:          $DISPLAY (NVIDIA RTX 5060 / D3D12)"
echo " Subsystems:       Gazebo + ros2_control + Piper Arm + MoveIt 2"
echo "=============================================================================="

SIM_PID=""
RVIZ_PID=""

cleanup() {
    echo ""
    echo "Stopping Manipulation Simulation..."
    [ -n "$RVIZ_PID" ] && kill -2 "$RVIZ_PID" 2>/dev/null || true
    [ -n "$SIM_PID" ] && kill -2 "$SIM_PID" 2>/dev/null || true
    sleep 2
    pkill -9 -f "move_group" 2>/dev/null || true
    pkill -9 -f "ros_gz" 2>/dev/null || true
    pkill -9 -f "gz_sim|gz-sim" 2>/dev/null || true
    pkill -9 -f "rviz2" 2>/dev/null || true
    echo "[OK] Manipulation Simulation stopped cleanly."
}
trap cleanup EXIT INT TERM

# Launch Gazebo + Base Robot + Piper Arm + ros2_control + MoveIt 2
ros2 launch ranger_bringup sim.launch.py \
    world:="$WORLD" \
    headless:="$HEADLESS" \
    manipulator:=true \
    manipulator_type:=piper \
    base_only:=false \
    enable_nav:=false \
    enable_vision:=false \
    enable_moveit:=true > /tmp/sim_manipulation.log 2>&1 &
SIM_PID=$!

echo "Waiting for simulation /clock and joint states..."
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
    cat /tmp/sim_manipulation.log | tail -n 25
    exit 1
fi

echo "Waiting for ros2_control piper_arm_controller to activate..."
PIPER_ONLINE=false
for i in {1..35}; do
    if ros2 control list_controllers 2>/dev/null | grep -q "piper_arm_controller.*active"; then
        echo "[OK] piper_arm_controller online ($i s)."
        PIPER_ONLINE=true
        break
    fi
    sleep 1
done

if [ "$PIPER_ONLINE" != "true" ]; then
    echo "[WARN] piper_arm_controller not active after 35s. Current controllers:"
    ros2 control list_controllers || true
fi

echo "Waiting for /piper_arm_controller/follow_joint_trajectory action server..."
ACTION_READY=false
for i in {1..30}; do
    if ros2 action list 2>/dev/null | grep -q "/piper_arm_controller/follow_joint_trajectory"; then
        echo "[OK] /piper_arm_controller/follow_joint_trajectory action server online ($i s)."
        ACTION_READY=true
        break
    fi
    sleep 1
done

# Launch RViz visualizer if not headless and not auto test
if [ "$HEADLESS" != "true" ] && [ "$AUTO_TEST" != "true" ]; then
    echo "Launching RViz2 visualizer..."
    rviz2 -d "$WS_DIR/src/ranger_description/rviz/description.rviz" --ros-args -p use_sim_time:=true >/dev/null 2>&1 &
    RVIZ_PID=$!
fi

# Health Status Report
echo ""
echo "=============================================================================="
echo "          JARVIS-X PIPER MANIPULATION SIMULATION RUNTIME HEALTH STATUS        "
echo "=============================================================================="

TOPICS=$(ros2 topic list 2>/dev/null || true)
CTRLS=$(ros2 control list_controllers 2>/dev/null || true)
ACTIONS=$(ros2 action list 2>/dev/null || true)

GZ_STATUS="FAIL"
CLOCK_STATUS="FAIL"
ROBOT_STATUS="FAIL"
CTRL_STATUS="FAIL"
JS_STATUS="FAIL"
PIPER_STATUS="FAIL"
ACTION_STATUS="FAIL"
MOVEGROUP_STATUS="FAIL"

pgrep -f "gz-sim|gz sim" >/dev/null 2>&1 && GZ_STATUS="ALIVE"
echo "$TOPICS" | grep -q "^/clock$" && CLOCK_STATUS="STREAMING"
pgrep -f "robot_state_publisher" >/dev/null 2>&1 && ROBOT_STATUS="PRESENT"
echo "$CTRLS" | grep -q "traction_controller.*active" && CTRL_STATUS="ACTIVE"
echo "$TOPICS" | grep -q "^/joint_states$" && JS_STATUS="STREAMING"
echo "$CTRLS" | grep -q "piper_arm_controller.*active" && PIPER_STATUS="ACTIVE"
echo "$ACTIONS" | grep -q "/piper_arm_controller/follow_joint_trajectory" && ACTION_STATUS="READY"
pgrep -f "move_group" >/dev/null 2>&1 && MOVEGROUP_STATUS="ONLINE"

echo " Gazebo:              $GZ_STATUS"
echo " /clock:              $CLOCK_STATUS"
echo " Ranger entity:       $ROBOT_STATUS"
echo " Base Controllers:    $CTRL_STATUS"
echo " /joint_states:       $JS_STATUS"
echo " Piper Controller:    $PIPER_STATUS"
echo " FollowJointAction:   $ACTION_STATUS"
echo " MoveGroup (MoveIt2): $MOVEGROUP_STATUS"
echo "=============================================================================="

if [ "$AUTO_TEST" = "true" ]; then
    echo "Running automated Piper 6-DOF physical trajectory execution test..."
    python3 "$PROJECT_DIR/tests/test_piper_trajectory.py"
    TEST_EXIT=$?
    if [ $TEST_EXIT -eq 0 ]; then
        echo "=============================================================================="
        echo "      [STAGE 3 PIPER MANIPULATION: VERIFIED & PASS]                           "
        echo "=============================================================================="
        exit 0
    else
        echo "[STAGE 3 FAIL] Piper trajectory test failed with code $TEST_EXIT."
        exit $TEST_EXIT
    fi
fi

echo " Stage 3 Manipulation Simulation Active. Controller ready for trajectories."
echo " Press Enter or Ctrl+C to terminate."
echo "=============================================================================="

read -r || true