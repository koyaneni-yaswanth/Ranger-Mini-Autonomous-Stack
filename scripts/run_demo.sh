#!/usr/bin/env bash
# JARVIS-X Master End-to-End Embodied AI Autonomous Demonstration
set -e

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

source "$PROJECT_DIR/env/source_lyrical.sh"
source "$WS_DIR/install/setup.bash"

export DISPLAY="${DISPLAY:-:0}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export MESA_D3D12_DEFAULT_ADAPTER_NAME="NVIDIA"
export QT_X11_NO_MITSHM=1

# By default, open GUI unless HEADLESS=true is explicitly requested
HEADLESS="${HEADLESS:-false}"
KEEP_ALIVE="${KEEP_ALIVE:-true}"
WORLD="${1:-red_cube_world.sdf}"
MISSION_PROMPT="${2:-JARVIS, find the red cube, pick it up, and put it on the table}"

echo "=============================================================================="
echo "      JARVIS-X GAZEBO DEMONSTRATION & AUTONOMOUS EMBODIED PIPELINE            "
echo "=============================================================================="
echo " Mode:            Modular Piper 6-DOF AMR-X"
echo " World:           $WORLD"
echo " Headless:        $HEADLESS"
echo " Display:         $DISPLAY (WSLg / NVIDIA RTX 5060)"
echo " User Command:    \"$MISSION_PROMPT\""
echo " Subsystems:      Gazebo + ros2_control + Nav2 + MoveIt 2 + Vision + JARVIS"
echo "=============================================================================="

SIM_PID=""
RVIZ_PID=""
INTERP_PID=""
WORLD_PID=""
ORCH_PID=""
BRAIN_PID=""

cleanup() {
    echo ""
    echo "=============================================================================="
    echo " SHUTTING DOWN DEMONSTRATION NODES..."
    echo "=============================================================================="
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
    echo "[OK] Clean shutdown complete."
}
trap cleanup EXIT INT TERM

# Step 1: Launch Gazebo Harmonic + Robot Base + Sensors + ros2_control + Nav2 + MoveIt + Vision
echo "[1/10] Starting Gazebo Harmonic physics & GUI window..."
echo "[2/10] Loading world: $WORLD..."
echo "[3/10] Spawning Ranger Mini + Piper 6-DOF..."
echo "[4/10] Starting ros2_control & 4WIS kinematics..."
echo "[5/10] Starting LiDAR, RGB camera, depth camera, IMU..."
echo "[6/10] Starting TF transform tree..."
echo "[7/10] Starting Nav2 navigation stack..."
echo "[8/10] Starting MoveIt 2 motion planning..."
echo "[9/10] Starting AI 3D object perception..."

ros2 launch ranger_bringup sim.launch.py \
    world:="$WORLD" \
    headless:="$HEADLESS" \
    manipulator:=true \
    manipulator_type:=piper \
    base_only:=false \
    enable_nav:=true \
    enable_vision:=true \
    enable_moveit:=true > /tmp/sim_demo.log 2>&1 &
SIM_PID=$!

# Wait for simulation clock & core nodes
echo "      Waiting for simulation initialization (up to 30s)..."
for i in {1..30}; do
    if ros2 topic list 2>/dev/null | grep -q "/clock"; then
        echo "      [OK] Clock active ($i s)."
        break
    fi
    sleep 1
done

# Step 10: Launch JARVIS Embodied Brain & Orchestration
echo "[10/10] Starting JARVIS Embodied Cognitive Stack..."
ros2 run ranger_missions ai_task_interpreter > /tmp/ai_interp.log 2>&1 &
INTERP_PID=$!

ros2 run ranger_missions semantic_world_model > /tmp/world_model.log 2>&1 &
WORLD_PID=$!

ros2 run ranger_missions autonomous_task_orchestrator > /tmp/orchestrator.log 2>&1 &
ORCH_PID=$!

ros2 run jarvis_core jarvis_brain_node.py > /tmp/jarvis_brain.log 2>&1 &
BRAIN_PID=$!

# Launch RViz Visualizer whenever HEADLESS is false
if [ "$HEADLESS" != "true" ]; then
    echo "Launching RViz 3D Autonomy Visualizer on screen..."
    rviz2 -d "$PROJECT_DIR/config/slam.rviz" --ros-args -p use_sim_time:=true >/dev/null 2>&1 &
    RVIZ_PID=$!
fi

sleep 4

# Run the live closed-loop test to execute the full pick and place
echo "Executing Full Closed-Loop Embodied Mission Test..."
python3 "$PROJECT_DIR/tests/test_mission_e2e.py" || true

echo "=============================================================================="
echo " [OK] Demonstration executed."
if [ "$HEADLESS" != "true" ] && [ "$KEEP_ALIVE" = "true" ]; then
    echo " Simulation GUI and RViz2 are ACTIVE on your desktop screen."
    echo " You can observe the robot, manipulate the camera, and inspect topics."
    echo " Keeping GUI open. Press Ctrl+C or terminate task to close."
    echo "=============================================================================="
    # Keep alive so user can view the simulation
    sleep 3600 &
    wait $!
fi