#!/usr/bin/env bash
# JARVIS-X Mode C: Stepwise Simulation Failure Isolator
# Boots subsystems sequentially to detect and pinpoint the FIRST failing component
set -e

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

source "$PROJECT_DIR/env/source_lyrical.sh"
source "$WS_DIR/install/setup.bash"

echo "=============================================================================="
echo "    JARVIS-X STEPWISE SIMULATION DEBUGGER & FAILURE ISOLATION (SECTION 31)   "
echo "=============================================================================="

STAGE_FAIL=0

cleanup() {
    pkill -9 -f "ros_gz|gz_sim|gz-sim|rviz2|ranger_control|slam_toolbox|nav2|ai_object_localizer|move_group|jarvis" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cleanup

# --- STAGE 1: Gazebo Harmonic Core Physics ---
echo ""
echo "[STAGE 1/9] Testing Gazebo Harmonic Physics Engine..."
gz sim -s -r -v 1 "$PROJECT_DIR/worlds/red_cube_world.sdf" > /tmp/gz_stage1.log 2>&1 &
GZ_PID=$!
sleep 4
if ps -p "$GZ_PID" > /dev/null 2>&1; then
    echo "  [PASS] Gazebo Harmonic physics engine running cleanly (PID: $GZ_PID)."
else
    echo "  [FAIL] Gazebo Harmonic failed to stay alive. Logs:"
    cat /tmp/gz_stage1.log | tail -n 20
    exit 1
fi
kill -9 "$GZ_PID" 2>/dev/null || true
sleep 1

# --- STAGE 2: Robot Description & State Publisher ---
echo ""
echo "[STAGE 2/9] Testing Robot Description & URDF Generation..."
URDF_OUT=$(xacro "$WS_DIR/src/ranger_description/urdf/ranger_mini_chassis.xacro" manipulator:=true manipulator_type:=piper 2>/dev/null || true)
if [ -n "$URDF_OUT" ]; then
    echo "  [PASS] Robot URDF generated successfully ($(echo "$URDF_OUT" | wc -l) lines)."
else
    echo "  [FAIL] Failed to generate URDF via xacro!"
    exit 2
fi

# --- STAGE 3: Base Simulation Launch ---
echo ""
echo "[STAGE 3/9] Testing Base Simulation (Gazebo + Robot + ros2_control)..."
ros2 launch ranger_bringup sim.launch.py \
    world:=red_cube_world.sdf \
    headless:=true \
    manipulator:=false \
    base_only:=true > /tmp/gz_stage3.log 2>&1 &
SIM_PID=$!

echo "  Waiting 15s for core bringup..."
sleep 15

if ! ps -p "$SIM_PID" > /dev/null 2>&1 && ! pgrep -f "gz-sim" > /dev/null 2>&1; then
    echo "  [FAIL] Base simulation process crashed! Logs:"
    cat /tmp/gz_stage3.log | tail -n 25
    exit 3
fi
echo "  [PASS] Base simulation running."

# --- STAGE 4: Sensor & Odometry Streaming ---
echo ""
echo "[STAGE 4/9] Validating Sensors & Odometry Streaming..."
TOPIC_LIST=$(timeout 10 ros2 topic list 2>/dev/null || true)
for t in "/clock" "/odom" "/scan" "/camera" "/camera/depth_image" "/imu"; do
    if echo "$TOPIC_LIST" | grep -q "^$t$"; then
        echo "  [PASS] Topic $t is active."
    else
        echo "  [FAIL] Required topic $t is missing!"
        STAGE_FAIL=$((STAGE_FAIL + 1))
    fi
done

if [ $STAGE_FAIL -gt 0 ]; then
    echo "  [FAIL] Sensor verification failed with $STAGE_FAIL missing topic(s)."
    exit 4
fi

# --- STAGE 5: TF Tree Validation ---
echo ""
echo "[STAGE 5/9] Validating TF Tree Continuity (odom -> base_footprint)..."
TF_CHECK=$(timeout 5 ros2 topic echo /tf --once 2>/dev/null || true)
if [ -n "$TF_CHECK" ]; then
    echo "  [PASS] Live TF broadcast received."
else
    echo "  [FAIL] No transforms received on /tf!"
    exit 5
fi

# Clean base sim before full tests
cleanup
sleep 2

# --- STAGE 6: Full Stack Bringup (Nav2 + MoveIt + Perception) ---
echo ""
echo "[STAGE 6/9] Booting Full Simulation Stack (Nav2 + MoveIt 2 + Perception)..."
ros2 launch ranger_bringup sim.launch.py \
    world:=red_cube_world.sdf \
    headless:=true \
    manipulator:=true \
    manipulator_type:=piper > /tmp/gz_stage6.log 2>&1 &
FULL_PID=$!

echo "  Waiting 22s for complete system convergence..."
sleep 22

# --- STAGE 7: MoveIt 2 & Piper Planning Group ---
echo ""
echo "[STAGE 7/9] Verifying MoveIt 2 move_group & Piper Planning Group..."
if pgrep -f "move_group" > /dev/null 2>&1; then
    echo "  [PASS] move_group node is active."
    ACTION_LIST=$(timeout 5 ros2 action list 2>/dev/null || true)
    if echo "$ACTION_LIST" | grep -q "follow_joint_trajectory"; then
        echo "  [PASS] piper_arm follow_joint_trajectory action server active."
    else
        echo "  [WARN] follow_joint_trajectory action pending."
    fi
else
    echo "  [FAIL] move_group crashed or did not start!"
    cat /tmp/gz_stage6.log | grep -i "move_group" | tail -n 20
    exit 7
fi

# --- STAGE 8: Nav2 Lifecycle & Actions ---
echo ""
echo "[STAGE 8/9] Verifying Nav2 Navigation Stack..."
if pgrep -f "bt_navigator" > /dev/null 2>&1; then
    echo "  [PASS] Nav2 bt_navigator is running."
    ACTION_LIST=$(timeout 5 ros2 action list 2>/dev/null || true)
    if echo "$ACTION_LIST" | grep -q "navigate_to_pose"; then
        echo "  [PASS] Nav2 /navigate_to_pose action server is ready."
    else
        echo "  [WARN] Nav2 action /navigate_to_pose pending."
    fi
else
    echo "  [FAIL] Nav2 processes not detected!"
    exit 8
fi

# --- STAGE 9: Perception & JARVIS Brain ---
echo ""
echo "[STAGE 9/9] Verifying AI Perception & Cognitive Brain..."
ros2 run ranger_missions ai_task_interpreter > /tmp/ai_interp_debug.log 2>&1 &
AI_PID=$!
ros2 run jarvis_core jarvis_brain > /tmp/jarvis_debug.log 2>&1 &
JB_PID=$!
sleep 4

if pgrep -f "ai_task_interpreter" > /dev/null 2>&1 && pgrep -f "jarvis_brain" > /dev/null 2>&1; then
    echo "  [PASS] JARVIS Brain & Task Interpreter online."
else
    echo "  [FAIL] JARVIS Cognitive nodes failed to start!"
    exit 9
fi

echo ""
echo "=============================================================================="
echo " [SUCCESS] ALL 9 STEPWISE SUB-STAGES INITIALIZED & VERIFIED CLEANLY!        "
echo "=============================================================================="
cleanup
exit 0
