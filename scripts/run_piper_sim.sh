#!/usr/bin/env bash
# JARVIS-X Piper 6-DOF Manipulator Simulation Launcher
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
WORLD="${1:-red_cube_world.sdf}"

echo "=============================================================================="
echo "    LAUNCHING PIPER 6-DOF MANIPULATOR SIMULATION (GAZEBO HARMONIC)           "
echo "=============================================================================="
echo " World:               $WORLD"
echo " Headless:            $HEADLESS"
echo " Display:             $DISPLAY (WSLg / NVIDIA RTX 5060)"
echo " Manipulator Model:   Piper 6-DOF + Parallel Gripper"
echo " Controllers:         piper_arm_controller + piper_gripper_controller"
echo "=============================================================================="

SIM_PID=""
RVIZ_PID=""

cleanup() {
    echo ""
    echo "Stopping Piper Simulation..."
    [ -n "$RVIZ_PID" ] && kill -2 "$RVIZ_PID" 2>/dev/null || true
    [ -n "$SIM_PID" ] && kill -2 "$SIM_PID" 2>/dev/null || true
    sleep 2
    pkill -9 -f "move_group" 2>/dev/null || true
    pkill -9 -f "ros_gz" 2>/dev/null || true
    pkill -9 -f "gz_sim|gz-sim" 2>/dev/null || true
    pkill -9 -f "sim_ground_truth_node" 2>/dev/null || true
    echo "[OK] Piper Simulation cleanly terminated."
}
trap cleanup EXIT INT TERM

ENABLE_VISION="${ENABLE_VISION:-true}"

ros2 launch ranger_bringup sim.launch.py \
    world:="$WORLD" \
    headless:="$HEADLESS" \
    manipulator:=true \
    manipulator_type:=piper \
    base_only:=false \
    enable_nav:=false \
    enable_vision:="$ENABLE_VISION" \
    enable_moveit:=true > /tmp/sim_piper.log 2>&1 &
SIM_PID=$!

echo "Waiting for simulation /clock and controllers..."
CLOCK_ONLINE=false
for i in {1..30}; do
    if ros2 topic list 2>/dev/null | grep -q "^/clock$"; then
        echo "[OK] Simulation clock active ($i s)."
        CLOCK_ONLINE=true
        break
    fi
    sleep 1
done

if [ "$CLOCK_ONLINE" != "true" ]; then
    echo "[FAIL] Simulation clock failed to start within 30s. Logs:"
    cat /tmp/sim_piper.log | tail -n 25
    exit 1
fi

echo "Waiting for piper_arm_controller..."
for i in {1..35}; do
    if ros2 control list_controllers 2>/dev/null | grep -q "piper_arm_controller.*active"; then
        echo "[OK] piper_arm_controller active ($i s)."
        break
    fi
    sleep 1
done

echo "Waiting for piper_gripper_controller..."
for i in {1..20}; do
    if ros2 control list_controllers 2>/dev/null | grep -q "piper_gripper_controller.*active"; then
        echo "[OK] piper_gripper_controller active ($i s)."
        break
    fi
    sleep 1
done

echo "Ensuring DetachableJoint starts decoupled (DETACHED)..."
/opt/ros/lyrical/opt/gz_tools_vendor/bin/gz topic -t /model/ranger_mini/detach -m gz.msgs.Empty -p '' >/dev/null 2>&1 || true

echo "Starting Simulation Ground Truth Publisher (/sim/red_cube_ground_truth)..."
python3 "$PROJECT_DIR/scripts/sim_ground_truth_node.py" >/dev/null 2>&1 &

if [ "$HEADLESS" != "true" ]; then
    echo "Launching RViz2 visualizer for Piper Manipulation..."
    rviz2 -d "$WS_DIR/src/ranger_description/rviz/description.rviz" --ros-args -p use_sim_time:=true >/dev/null 2>&1 &
    RVIZ_PID=$!
fi

echo ""
echo "=============================================================================="
if [ "$AUTO_TEST" = "true" ]; then
    echo "Running Piper 6-DOF Physical Regression Suite..."
    python3 "$PROJECT_DIR/scripts/test_piper_regression.py"
    TEST_EXIT=$?
    exit $TEST_EXIT
fi

echo "=============================================================================="
echo " Press Ctrl+C to terminate simulation."
sleep 86400 &
wait $!