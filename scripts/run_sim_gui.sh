#!/usr/bin/env bash
# JARVIS-X Master Simulation Launcher (Gazebo Harmonic GUI + Robot + Piper + RViz2)
set -e

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

source "$PROJECT_DIR/env/source_lyrical.sh"
source "$WS_DIR/install/setup.bash"

export DISPLAY="${DISPLAY:-:0}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"
export QT_X11_NO_MITSHM=1

WORLD="${1:-red_cube_world.sdf}"
MANIPULATOR="${MANIPULATOR:-true}"
MANIPULATOR_TYPE="${MANIPULATOR_TYPE:-piper}"

echo "=============================================================================="
echo "    LAUNCHING JARVIS-X GAZEBO HARMONIC FULL SIMULATION (GUI ACTIVE)"
echo "=============================================================================="
echo " World:            $WORLD"
echo " Manipulator:      $MANIPULATOR ($MANIPULATOR_TYPE 6-DOF)"
echo " GUI Display:      $DISPLAY / D3D12 NVIDIA"
echo "=============================================================================="

SIM_PID=""
RVIZ_PID=""

cleanup() {
    echo ""
    echo "Stopping simulation stack..."
    [ -n "$RVIZ_PID" ] && kill -2 "$RVIZ_PID" 2>/dev/null || true
    [ -n "$SIM_PID" ] && kill -2 "$SIM_PID" 2>/dev/null || true
    sleep 2
    pkill -9 -f "ros_gz" 2>/dev/null || true
    pkill -9 -f "gz_sim" 2>/dev/null || true
    pkill -9 -f "rviz2" 2>/dev/null || true
    echo "[OK] Gazebo simulation stopped cleanly."
}
trap cleanup EXIT INT TERM

# Launch Gazebo + Full Simulation Bringup
ros2 launch ranger_bringup sim.launch.py \
    world:="$WORLD" \
    headless:=false \
    manipulator:="$MANIPULATOR" \
    manipulator_type:="$MANIPULATOR_TYPE" &
SIM_PID=$!

echo "Waiting for simulation /clock..."
for i in {1..30}; do
    if ros2 topic list 2>/dev/null | grep -q "/clock"; then
        echo "[OK] Simulation clock active."
        break
    fi
    sleep 1
done

# Launch RViz2 Autonomy Visualizer
echo "Launching RViz2 visualizer..."
rviz2 -d "$PROJECT_DIR/config/slam.rviz" --ros-args -p use_sim_time:=true >/dev/null 2>&1 &
RVIZ_PID=$!

echo ""
echo "=============================================================================="
echo " SIMULATION ACTIVE: Gazebo Harmonic & RViz2 running."
echo " Press Ctrl+C to shutdown."
echo "=============================================================================="

wait "$SIM_PID"
