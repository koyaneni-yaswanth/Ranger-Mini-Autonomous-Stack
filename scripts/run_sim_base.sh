#!/usr/bin/env bash
# JARVIS-X Mode A: Base Simulation Launcher (No MoveIt or AI required)
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
WORLD="${1:-red_cube_world.sdf}"

echo "=============================================================================="
echo "    LAUNCHING JARVIS-X MODE A: BASE SIMULATION (PHYSICAL CHASSIS + SENSORS)"
echo "=============================================================================="
echo " World:            $WORLD"
echo " Headless:         $HEADLESS"
echo " Display:          $DISPLAY (NVIDIA RTX 5060 / D3D12)"
echo " Subsystems:       Gazebo + ros2_control + Odom + TF + LiDAR + Camera + IMU"
echo "=============================================================================="

SIM_PID=""
RVIZ_PID=""

cleanup() {
    echo ""
    echo "Stopping Base Simulation..."
    [ -n "$RVIZ_PID" ] && kill -2 "$RVIZ_PID" 2>/dev/null || true
    [ -n "$SIM_PID" ] && kill -2 "$SIM_PID" 2>/dev/null || true
    sleep 2
    pkill -9 -f "ros_gz" 2>/dev/null || true
    pkill -9 -f "gz_sim|gz-sim" 2>/dev/null || true
    pkill -9 -f "rviz2" 2>/dev/null || true
    echo "[OK] Base Simulation stopped cleanly."
}
trap cleanup EXIT INT TERM

# Launch Gazebo + Base Robot + Bridge + Controllers + Sensor Processing
ros2 launch ranger_bringup sim.launch.py \
    world:="$WORLD" \
    headless:="$HEADLESS" \
    manipulator:=false \
    base_only:=true > /tmp/sim_base.log 2>&1 &
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
    cat /tmp/sim_base.log | tail -n 25
    exit 1
fi

# Launch RViz visualizer if not headless
if [ "$HEADLESS" != "true" ]; then
    echo "Launching RViz2 base visualizer..."
    rviz2 -d "$PROJECT_DIR/config/slam.rviz" --ros-args -p use_sim_time:=true >/dev/null 2>&1 &
    RVIZ_PID=$!
fi

echo "Waiting for ros2_control controllers to activate..."
for i in {1..20}; do
    if ros2 control list_controllers 2>/dev/null | grep -q "traction_controller.*active"; then
        echo "[OK] Base traction and steering controllers online ($i s)."
        break
    fi
    sleep 1
done

# Real Live Runtime Watchdog
echo ""
echo "=============================================================================="
echo "               JARVIS-X BASE SIMULATION RUNTIME HEALTH STATUS                 "
echo "=============================================================================="

TOPICS=$(ros2 topic list 2>/dev/null || true)
CTRLS=$(ros2 control list_controllers 2>/dev/null || true)

GZ_STATUS="FAIL"
CLOCK_STATUS="FAIL"
ROBOT_STATUS="FAIL"
CTRL_STATUS="FAIL"
ODOM_STATUS="FAIL"
TF_STATUS="FAIL"
LIDAR_STATUS="FAIL"
CAM_STATUS="FAIL"
DEPTH_STATUS="FAIL"
IMU_STATUS="FAIL"

pgrep -f "gz-sim|gz sim" >/dev/null 2>&1 && GZ_STATUS="ALIVE"
echo "$TOPICS" | grep -q "^/clock$" && CLOCK_STATUS="STREAMING"
pgrep -f "robot_state_publisher" >/dev/null 2>&1 && ROBOT_STATUS="PRESENT"
echo "$CTRLS" | grep -q "traction_controller.*active" && CTRL_STATUS="ACTIVE"
echo "$TOPICS" | grep -q "^/odom$" && ODOM_STATUS="STREAMING"
echo "$TOPICS" | grep -q "^/tf$" && TF_STATUS="STREAMING"
(echo "$TOPICS" | grep -q "^/scan$" || echo "$TOPICS" | grep -q "^/lidar/points") && LIDAR_STATUS="STREAMING"
echo "$TOPICS" | grep -q "^/camera$" && CAM_STATUS="STREAMING"
echo "$TOPICS" | grep -q "^/camera/depth_image$" && DEPTH_STATUS="STREAMING"
echo "$TOPICS" | grep -q "^/imu$" && IMU_STATUS="STREAMING"

echo " Gazebo:           $GZ_STATUS"
echo " /clock:           $CLOCK_STATUS"
echo " Ranger entity:    $ROBOT_STATUS"
echo " controllers:      $CTRL_STATUS"
echo " odom:             $ODOM_STATUS"
echo " tf:               $TF_STATUS"
echo " lidar:            $LIDAR_STATUS"
echo " camera:           $CAM_STATUS"
echo " depth:            $DEPTH_STATUS"
echo " imu:              $IMU_STATUS"
echo "=============================================================================="
echo " Mode A Base Simulation Active. Test manual motion in another terminal:"
echo "   ros2 topic pub /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.3}}' -r 10"
echo " Press Enter or Ctrl+C to terminate."
echo "=============================================================================="

if [ "$HEADLESS" = "true" ] || [ "$AUTO_TEST" = "true" ] || [ ! -t 0 ]; then
    echo "Running automated physical base movement test..."
    python3 "$PROJECT_DIR/tests/test_base_movement.py"
    TEST_EXIT=$?
    if [ $TEST_EXIT -eq 0 ]; then
        echo "=============================================================================="
        echo "           [STAGE 1 BASE CHASSIS SIMULATION: VERIFIED & PASS]                 "
        echo "=============================================================================="
        exit 0
    else
        echo "[STAGE 1 FAIL] Physical base movement test failed with code $TEST_EXIT."
        exit $TEST_EXIT
    fi
fi

read -r || true

