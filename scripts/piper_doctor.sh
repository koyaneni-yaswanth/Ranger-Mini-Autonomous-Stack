#!/usr/bin/env bash
# JARVIS-X Piper 6-DOF Forensic Doctor & Health Audit
set -e

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"

source "$PROJECT_DIR/env/source_lyrical.sh"
source "$WS_DIR/install/setup.bash"

echo "=============================================================================="
echo "            JARVIS-X PIPER MANIPULATOR FORENSIC AUDIT (DOCTOR)                "
echo "=============================================================================="

PASS_COUNT=0
TOTAL_COUNT=0

check() {
    local name="$1"
    local status="$2"
    local detail="$3"
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
    if [ "$status" = "PASS" ]; then
        PASS_COUNT=$((PASS_COUNT + 1))
        printf "  %-45s [PASS] %s\n" "$name" "$detail"
    else
        printf "  %-45s [FAIL] %s\n" "$name" "$detail"
    fi
}

echo "[1/6] Piper URDF & Kinematic Model Integrity..."
URDF_PATH="/tmp/piper_doctor.urdf"
xacro "$WS_DIR/src/ranger_description/urdf/ranger_mini.urdf.xacro" \
    manipulator:=true manipulator_type:=piper base_only:=false > "$URDF_PATH" 2>/dev/null || true

if [ -s "$URDF_PATH" ]; then
    check "URDF Xacro Generation" "PASS" "Generated successfully"
    
    # Check all 6 arm joints + gripper
    for j in piper_joint1 piper_joint2 piper_joint3 piper_joint4 piper_joint5 piper_joint6 piper_finger_left_joint piper_finger_right_joint; do
        if grep -q "joint name=\"$j\"" "$URDF_PATH"; then
            check "Joint: $j" "PASS" "Defined in URDF"
        else
            check "Joint: $j" "FAIL" "Missing in URDF"
        fi
    done
else
    check "URDF Xacro Generation" "FAIL" "Failed to generate $URDF_PATH"
fi

echo ""
echo "[2/6] MoveIt 2 SRDF & Planning Configuration..."
SRDF_PATH="$WS_DIR/src/ranger_manipulation/config/ranger_piper.srdf"
if [ -f "$SRDF_PATH" ]; then
    check "SRDF File Exists" "PASS" "$SRDF_PATH"
    grep -q "group name=\"piper_arm\"" "$SRDF_PATH" && check "SRDF Group: piper_arm" "PASS" "Found" || check "SRDF Group: piper_arm" "FAIL" "Missing"
    grep -q "group name=\"piper_gripper\"" "$SRDF_PATH" && check "SRDF Group: piper_gripper" "PASS" "Found" || check "SRDF Group: piper_gripper" "FAIL" "Missing"
    grep -q "end_effector name=\"gripper\"" "$SRDF_PATH" && check "SRDF End Effector" "PASS" "Found" || check "SRDF End Effector" "FAIL" "Missing"
else
    check "SRDF File Exists" "FAIL" "Missing $SRDF_PATH"
fi

echo ""
echo "[3/6] ros2_control Controller Configuration..."
CTRL_YAML="$WS_DIR/src/ranger_control/config/controller.yaml"
if [ -f "$CTRL_YAML" ]; then
    grep -q "piper_arm_controller:" "$CTRL_YAML" && check "Arm Controller Defined" "PASS" "piper_arm_controller in YAML" || check "Arm Controller Defined" "FAIL" "Missing"
    grep -q "piper_gripper_controller:" "$CTRL_YAML" && check "Gripper Controller Defined" "PASS" "piper_gripper_controller in YAML" || check "Gripper Controller Defined" "FAIL" "Missing"
fi

echo ""
echo "[4/6] Gazebo Sim ros2_control Hardware Interface..."
GZ_XACRO="$WS_DIR/src/ranger_description/urdf/gazebo.xacro"
if [ -f "$GZ_XACRO" ]; then
    grep -q "gz_ros2_control/GazeboSimSystem" "$GZ_XACRO" && check "Gazebo Sim Plugin" "PASS" "gz_ros2_control plugin configured" || check "Gazebo Sim Plugin" "FAIL" "Missing"
    grep -q "joint name=\"piper_joint1\"" "$GZ_XACRO" && check "Gazebo Arm Joint Interfaces" "PASS" "Hardware interfaces mapped" || check "Gazebo Arm Joint Interfaces" "FAIL" "Missing"
    grep -q "joint name=\"piper_finger_left_joint\"" "$GZ_XACRO" && check "Gazebo Gripper Interface" "PASS" "Hardware interface mapped" || check "Gazebo Gripper Interface" "FAIL" "Missing"
fi

echo ""
echo "[5/6] Live Controller & Action Server Telemetry (if simulation active)..."
TOPICS=$(timeout 2 ros2 topic list 2>/dev/null || true)
CTRLS=$(timeout 2 ros2 control list_controllers 2>/dev/null || true)
ACTIONS=$(timeout 2 ros2 action list 2>/dev/null || true)

if echo "$TOPICS" | grep -q "^/joint_states$"; then
    check "Live /joint_states Topic" "PASS" "Active and streaming"
else
    check "Live /joint_states Topic" "INFO" "Offline (start make piper-sim or make demo)"
fi

if echo "$CTRLS" | grep -q "piper_arm_controller.*active"; then
    check "Live piper_arm_controller" "PASS" "Active in controller_manager"
else
    check "Live piper_arm_controller" "INFO" "Offline (start make piper-sim)"
fi

if echo "$CTRLS" | grep -q "piper_gripper_controller.*active"; then
    check "Live piper_gripper_controller" "PASS" "Active in controller_manager"
else
    check "Live piper_gripper_controller" "INFO" "Offline (start make piper-sim)"
fi

if echo "$ACTIONS" | grep -q "/piper_arm_controller/follow_joint_trajectory"; then
    check "Live Arm FollowJointTrajectory Action" "PASS" "Action Server online"
fi

if echo "$ACTIONS" | grep -q "/piper_gripper_controller/follow_joint_trajectory"; then
    check "Live Gripper FollowJointTrajectory Action" "PASS" "Action Server online"
fi

echo ""
echo "=============================================================================="
echo " PIPER DOCTOR AUDIT SUMMARY: $PASS_COUNT checks verified."
echo "=============================================================================="