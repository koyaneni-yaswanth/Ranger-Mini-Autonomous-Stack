#!/usr/bin/env bash
# JARVIS-X Stage 4: AI Perception & 3D Object Localization Launcher & Verifier
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
echo "    LAUNCHING JARVIS-X STAGE 4: AI PERCEPTION & 3D LOCALIZATION               "
echo "=============================================================================="
echo " World:            $WORLD"
echo " Headless:         $HEADLESS"
echo " Auto Test:        $AUTO_TEST"
echo " Display:          $DISPLAY (NVIDIA RTX 5060 / D3D12)"
echo " Subsystems:       Gazebo + ros_gz_bridge + Cameras + AI Localizer Node"
echo "=============================================================================="

SIM_PID=""
RVIZ_PID=""

cleanup() {
    echo ""
    echo "Stopping Perception Simulation..."
    [ -n "$RVIZ_PID" ] && kill -2 "$RVIZ_PID" 2>/dev/null || true
    [ -n "$SIM_PID" ] && kill -2 "$SIM_PID" 2>/dev/null || true
    sleep 2
    pkill -9 -f "ai_object_localizer" 2>/dev/null || true
    pkill -9 -f "sensor_fusion" 2>/dev/null || true
    pkill -9 -f "ros_gz" 2>/dev/null || true
    pkill -9 -f "gz_sim|gz-sim" 2>/dev/null || true
    pkill -9 -f "rviz2" 2>/dev/null || true
    echo "[OK] Perception Simulation stopped cleanly."
}
trap cleanup EXIT INT TERM

# Launch Gazebo + Base Robot + Bridge + Perception & Vision Stack
ros2 launch ranger_bringup sim.launch.py \
    world:="$WORLD" \
    headless:="$HEADLESS" \
    manipulator:=false \
    base_only:=false \
    enable_nav:=false \
    enable_vision:=true \
    enable_moveit:=false > /tmp/sim_perception.log 2>&1 &
SIM_PID=$!

echo "Waiting for simulation /clock and camera topics..."
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
    cat /tmp/sim_perception.log | tail -n 25
    exit 1
fi

echo "Waiting for camera streams from ros_gz_bridge..."
CAM_ONLINE=false
for i in {1..25}; do
    TOPICS=$(ros2 topic list 2>/dev/null || true)
    if echo "$TOPICS" | grep -q "/camera" && echo "$TOPICS" | grep -q "/camera/depth_image"; then
        echo "[OK] Camera and Depth streams online ($i s)."
        CAM_ONLINE=true
        break
    fi
    sleep 1
done

if [ "$CAM_ONLINE" != "true" ]; then
    echo "[WARN] Camera streams took longer than 25s to appear."
fi

echo "Waiting for AI Object Localizer node to initialize..."
for i in {1..20}; do
    if ros2 node list 2>/dev/null | grep -q "ai_object_localizer"; then
        echo "[OK] ai_object_localizer node active ($i s)."
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
echo "          JARVIS-X AI PERCEPTION SIMULATION RUNTIME HEALTH STATUS             "
echo "=============================================================================="

TOPICS=$(ros2 topic list 2>/dev/null || true)
NODES=$(ros2 node list 2>/dev/null || true)

GZ_STATUS="FAIL"
CLOCK_STATUS="FAIL"
ROBOT_STATUS="FAIL"
RGB_STATUS="FAIL"
DEPTH_STATUS="FAIL"
LOCALIZER_STATUS="FAIL"
TARGET_STATUS="FAIL"

pgrep -f "gz-sim|gz sim" >/dev/null 2>&1 && GZ_STATUS="ALIVE"
echo "$TOPICS" | grep -q "^/clock$" && CLOCK_STATUS="STREAMING"
pgrep -f "robot_state_publisher" >/dev/null 2>&1 && ROBOT_STATUS="PRESENT"
echo "$TOPICS" | grep -q "^/camera$" && RGB_STATUS="STREAMING"
echo "$TOPICS" | grep -q "^/camera/depth_image$" && DEPTH_STATUS="STREAMING"
echo "$NODES" | grep -q "ai_object_localizer" && LOCALIZER_STATUS="ONLINE"
echo "$TOPICS" | grep -q "^/vision/target_pose$" && TARGET_STATUS="STREAMING"

echo " Gazebo:               $GZ_STATUS"
echo " /clock:               $CLOCK_STATUS"
echo " Ranger entity:        $ROBOT_STATUS"
echo " /camera (RGB):        $RGB_STATUS"
echo " /camera/depth_image:  $DEPTH_STATUS"
echo " AI Localizer Node:    $LOCALIZER_STATUS"
echo " /vision/target_pose:  $TARGET_STATUS"
echo "=============================================================================="

if [ "$AUTO_TEST" = "true" ]; then
    echo "Running automated AI perception and 3D localization test..."
    python3 "$PROJECT_DIR/tests/test_real_perception.py"
    TEST_EXIT=$?
    if [ $TEST_EXIT -eq 0 ]; then
        echo "=============================================================================="
        echo "      [STAGE 4 AI PERCEPTION & LOCALIZATION: VERIFIED & PASS]                 "
        echo "=============================================================================="
        exit 0
    else
        echo "[STAGE 4 FAIL] Perception test failed with code $TEST_EXIT."
        exit $TEST_EXIT
    fi
fi

echo " Stage 4 Perception Simulation Active. Streams available."
echo " Press Enter or Ctrl+C to terminate."
echo "=============================================================================="

read -r || true