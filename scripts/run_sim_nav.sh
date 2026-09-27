#!/usr/bin/env bash
# JARVIS-X Stage 2: Nav2 Autonomous Navigation Launcher & Verifier
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
echo "    LAUNCHING JARVIS-X STAGE 2: NAV2 4WIS HOLONOMIC AUTONOMOUS NAVIGATION     "
echo "=============================================================================="
echo " World:            $WORLD"
echo " Headless:         $HEADLESS"
echo " Auto Test:        $AUTO_TEST"
echo " Display:          $DISPLAY (NVIDIA RTX 5060 / D3D12)"
echo " Subsystems:       Gazebo + ros2_control + Odom + TF + LiDAR + SLAM + Nav2"
echo "=============================================================================="

SIM_PID=""
RVIZ_PID=""

cleanup() {
    echo ""
    echo "Stopping Nav2 Simulation..."
    [ -n "$RVIZ_PID" ] && kill -2 "$RVIZ_PID" 2>/dev/null || true
    [ -n "$SIM_PID" ] && kill -2 "$SIM_PID" 2>/dev/null || true
    sleep 2
    pkill -9 -f "nav2_" 2>/dev/null || true
    pkill -9 -f "slam_toolbox" 2>/dev/null || true
    pkill -9 -f "ros_gz" 2>/dev/null || true
    pkill -9 -f "gz_sim|gz-sim" 2>/dev/null || true
    pkill -9 -f "rviz2" 2>/dev/null || true
    echo "[OK] Nav2 Simulation stopped cleanly."
}
trap cleanup EXIT INT TERM

# Launch Gazebo + Base Robot + Bridge + Controllers + Perception + SLAM + Nav2
ros2 launch ranger_bringup sim.launch.py \
    world:="$WORLD" \
    headless:="$HEADLESS" \
    manipulator:=false \
    base_only:=false \
    enable_nav:=true \
    enable_vision:=false \
    enable_moveit:=false > /tmp/sim_nav.log 2>&1 &
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
    cat /tmp/sim_nav.log | tail -n 25
    exit 1
fi

echo "Waiting for ros2_control controllers to activate..."
for i in {1..25}; do
    if ros2 control list_controllers 2>/dev/null | grep -q "traction_controller.*active"; then
        echo "[OK] Base traction and steering controllers online ($i s)."
        break
    fi
    sleep 1
done

echo "Waiting for Nav2 /navigate_to_pose action server..."
NAV2_READY=false
for i in {1..35}; do
    if ros2 action list 2>/dev/null | grep -q "/navigate_to_pose"; then
        echo "[OK] Nav2 /navigate_to_pose action server online ($i s)."
        NAV2_READY=true
        break
    fi
    sleep 1
done

if [ "$NAV2_READY" != "true" ]; then
    echo "[WARN] Nav2 action server took longer than 35s. Checking logs..."
    tail -n 20 /tmp/sim_nav.log
fi

# Launch RViz visualizer if not headless and not auto test
if [ "$HEADLESS" != "true" ] && [ "$AUTO_TEST" != "true" ]; then
    echo "Launching RViz2 navigation visualizer..."
    rviz2 -d "$PROJECT_DIR/config/slam.rviz" --ros-args -p use_sim_time:=true >/dev/null 2>&1 &
    RVIZ_PID=$!
fi

# Health Status Report
echo ""
echo "=============================================================================="
echo "               JARVIS-X NAV2 SIMULATION RUNTIME HEALTH STATUS                 "
echo "=============================================================================="

TOPICS=$(ros2 topic list 2>/dev/null || true)
CTRLS=$(ros2 control list_controllers 2>/dev/null || true)
ACTIONS=$(ros2 action list 2>/dev/null || true)

GZ_STATUS="FAIL"
CLOCK_STATUS="FAIL"
ROBOT_STATUS="FAIL"
CTRL_STATUS="FAIL"
ODOM_STATUS="FAIL"
TF_STATUS="FAIL"
SCAN_STATUS="FAIL"
SLAM_STATUS="FAIL"
NAV2_STATUS="FAIL"

pgrep -f "gz-sim|gz sim" >/dev/null 2>&1 && GZ_STATUS="ALIVE"
echo "$TOPICS" | grep -q "^/clock$" && CLOCK_STATUS="STREAMING"
pgrep -f "robot_state_publisher" >/dev/null 2>&1 && ROBOT_STATUS="PRESENT"
echo "$CTRLS" | grep -q "traction_controller.*active" && CTRL_STATUS="ACTIVE"
echo "$TOPICS" | grep -q "^/odom$" && ODOM_STATUS="STREAMING"
echo "$TOPICS" | grep -q "^/tf$" && TF_STATUS="STREAMING"
echo "$TOPICS" | grep -q "^/scan$" && SCAN_STATUS="STREAMING"
echo "$TOPICS" | grep -q "^/map$" && SLAM_STATUS="ACTIVE"
echo "$ACTIONS" | grep -q "^/navigate_to_pose$" && NAV2_STATUS="READY"

echo " Gazebo:           $GZ_STATUS"
echo " /clock:           $CLOCK_STATUS"
echo " Ranger entity:    $ROBOT_STATUS"
echo " Controllers:      $CTRL_STATUS"
echo " /odom:            $ODOM_STATUS"
echo " /tf:              $TF_STATUS"
echo " /scan (LiDAR):    $SCAN_STATUS"
echo " SLAM (/map):      $SLAM_STATUS"
echo " Nav2 action:      $NAV2_STATUS"
echo "=============================================================================="

if [ "$AUTO_TEST" = "true" ]; then
    echo "Running automated Nav2 4WIS closed-loop movement test..."
    python3 "$PROJECT_DIR/tests/test_nav2_movement.py"
    TEST_EXIT=$?
    if [ $TEST_EXIT -eq 0 ]; then
        echo "=============================================================================="
        echo "           [STAGE 2 NAV2 NAVIGATION: VERIFIED & PASS]                         "
        echo "=============================================================================="
        exit 0
    else
        echo "[STAGE 2 FAIL] Nav2 test failed with code $TEST_EXIT."
        exit $TEST_EXIT
    fi
fi

echo " Stage 2 Nav2 Simulation Active. Dispatched goal can be monitored."
echo " Press Enter or Ctrl+C to terminate."
echo "=============================================================================="

read -r || true
