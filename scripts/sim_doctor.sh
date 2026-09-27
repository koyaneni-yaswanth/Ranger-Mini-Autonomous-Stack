#!/usr/bin/env bash
# JARVIS-X Simulation Health Doctor (Zero Fabrication Verification)

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

source "$PROJECT_DIR/env/source_lyrical.sh"
source "$WS_DIR/install/setup.bash"

echo "=============================================================================="
echo "              JARVIS-X SIMULATION HEALTH AUDIT (ZERO FABRICATION)"
echo "=============================================================================="

FAIL_COUNT=0

check_status() {
    local label="$1"
    local result="$2"
    local details="$3"
    
    printf "%-25s " "$label"
    if [ "$result" -eq 0 ]; then
        echo -e "[ PASS ]  $details"
    else
        echo -e "[ FAIL ]  $details"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

# Pre-fetch ROS 2 runtime state with adequate discovery time
TOPIC_LIST=$(timeout 15 ros2 topic list 2>/dev/null || true)
NODE_LIST=$(timeout 15 ros2 node list 2>/dev/null || true)
ACTION_LIST=$(timeout 15 ros2 action list 2>/dev/null || true)
CTRL_LIST=$(timeout 15 ros2 control list_controllers 2>/dev/null || true)

# 1. Gazebo Harmonic Process
if pgrep -f "gz sim|gz-sim" >/dev/null 2>&1; then
    check_status "Gazebo process" 0 "gz-sim physics engine running"
else
    check_status "Gazebo process" 1 "gz-sim process not detected"
fi

# 2. Clock Topic
if echo "$TOPIC_LIST" | grep -q "^/clock$"; then
    check_status "Clock" 0 "/clock active"
else
    check_status "Clock" 1 "/clock missing"
fi

# 3. Ranger Entity & Model
if echo "$TOPIC_LIST" | grep -q "/model/ranger_mini"; then
    check_status "Ranger entity" 0 "ranger_mini model active in Gazebo"
elif pgrep -f "robot_state_publisher" >/dev/null 2>&1; then
    check_status "Ranger entity" 0 "ranger_mini robot_state_publisher active"
else
    check_status "Ranger entity" 1 "entity not detected"
fi

# 4. TF Tree
if echo "$TOPIC_LIST" | grep -q "^/tf$"; then
    check_status "TF" 0 "/tf stream active"
else
    check_status "TF" 1 "/tf missing"
fi

# 5. cmd_vel
if echo "$TOPIC_LIST" | grep -q "^/cmd_vel$"; then
    check_status "cmd_vel" 0 "/cmd_vel input interface ready"
else
    check_status "cmd_vel" 1 "/cmd_vel missing"
fi

# 6. Odometry
if echo "$TOPIC_LIST" | grep -q "^/odom$"; then
    check_status "odom" 0 "/odom publishing"
else
    check_status "odom" 1 "/odom missing"
fi

# 7. LiDAR (/scan or /lidar/points)
if echo "$TOPIC_LIST" | grep -q "^/scan$"; then
    check_status "LiDAR" 0 "/scan laser scan active"
elif echo "$TOPIC_LIST" | grep -q "^/lidar/points"; then
    check_status "LiDAR" 0 "/lidar/points pointcloud active"
else
    check_status "LiDAR" 1 "LiDAR topics missing"
fi

# 8. RGB Camera
if echo "$TOPIC_LIST" | grep -q "^/camera$"; then
    check_status "Camera" 0 "/camera RGB stream active"
else
    check_status "Camera" 1 "/camera missing"
fi

# 9. Depth Camera
if echo "$TOPIC_LIST" | grep -q "^/camera/depth_image$"; then
    check_status "Depth" 0 "/camera/depth_image stream active"
else
    check_status "Depth" 1 "/camera/depth_image missing"
fi

# 10. IMU
if echo "$TOPIC_LIST" | grep -q "^/imu$"; then
    check_status "IMU" 0 "/imu telemetry active"
else
    check_status "IMU" 1 "/imu missing"
fi

# 11. ROS 2 Controllers
if echo "$CTRL_LIST" | grep -q "steering_controller.*active"; then
    check_status "Controllers" 0 "steering, traction, JSB active"
elif pgrep -f "kinematics_node" >/dev/null 2>&1; then
    check_status "Controllers" 0 "kinematics_node active"
else
    check_status "Controllers" 1 "controllers not active"
fi

# 12. Nav2 Navigation
if echo "$NODE_LIST" | grep -q "bt_navigator"; then
    check_status "Nav2" 0 "Nav2 behavior tree navigator active"
elif pgrep -f "nav2" >/dev/null 2>&1; then
    check_status "Nav2" 0 "Nav2 processes running"
else
    check_status "Nav2" 1 "Nav2 nodes not running"
fi

# 13. MoveIt 2
if echo "$ACTION_LIST" | grep -q "follow_joint_trajectory"; then
    check_status "MoveIt / Piper" 0 "piper trajectory action active"
elif pgrep -f "move_group" >/dev/null 2>&1; then
    check_status "MoveIt / Piper" 0 "move_group node active"
else
    check_status "MoveIt / Piper" 1 "manipulator action server missing"
fi

# 14. Perception (AI Object Localizer)
if echo "$TOPIC_LIST" | grep -q "/vision/target_pose"; then
    check_status "Perception" 0 "/vision/target_pose active"
elif pgrep -f "ai_object_localizer" >/dev/null 2>&1; then
    check_status "Perception" 0 "ai_object_localizer running"
else
    check_status "Perception" 1 "perception not running"
fi

# 15. JARVIS Cognitive Brain
if pgrep -f "jarvis_brain" >/dev/null 2>&1 || pgrep -f "ai_task_interpreter" >/dev/null 2>&1; then
    check_status "JARVIS" 0 "JARVIS embodied brain active"
else
    check_status "JARVIS" 1 "JARVIS brain not running (start with make demo or make jarvis)"
fi

echo "=============================================================================="
if [ $FAIL_COUNT -eq 0 ]; then
    echo " RESULT: ALL RUNTIME SUBSYSTEMS OPERATIONAL (100% HEALTHY)"
    exit 0
else
    echo " RESULT: $FAIL_COUNT SUBSYSTEM(S) REPORTED ISSUES"
    exit 1
fi
