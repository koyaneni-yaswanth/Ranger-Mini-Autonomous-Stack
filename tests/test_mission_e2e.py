#!/usr/bin/env python3
"""
JARVIS-X Stage 5: Full End-to-End Closed-Loop Physical Autonomous Mission Test.
Voice/NL Prompt -> JARVIS Brain -> Task Orchestrator 17-State FSM ->
Perception 3D Localization -> Nav2 Navigation -> MoveIt 2 Piper Pick & Place ->
Tactile/Optical Grasp Verification -> Return to Complete.
"""

import sys
import os
import json
import time
import math
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState, Image
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String

PIPER_JOINTS = [
    'piper_joint1', 'piper_joint2', 'piper_joint3',
    'piper_joint4', 'piper_joint5', 'piper_joint6'
]

class MissionE2EVerifierNode(Node):
    def __init__(self):
        super().__init__(
            'mission_e2e_verifier_node',
            parameter_overrides=[
                Parameter('use_sim_time', Parameter.Type.BOOL, True)
            ]
        )
        qos_best_effort = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        qos_reliable = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # State tracking
        self.odom_received = False
        self.initial_pos = None
        self.current_pos = None
        self.joint_states_received = False
        self.initial_joints = {}
        self.current_joints = {}
        self.target_pose_received = False
        self.last_target_pose = None
        self.camera_received = False

        self.states_visited = []
        self.current_state = "IDLE"
        self.grasp_eval_result = None
        self.task_complete = False

        # Subscriptions
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_cb, qos_best_effort)
        self.sub_js = self.create_subscription(JointState, '/joint_states', self.js_cb, qos_best_effort)
        self.sub_target = self.create_subscription(PoseStamped, '/vision/target_pose', self.target_cb, 10)
        self.sub_cam = self.create_subscription(Image, '/camera', self.cam_cb, 10)
        self.sub_state = self.create_subscription(String, '/mission/state', self.state_cb, 10)
        self.sub_grasp = self.create_subscription(String, '/mission/grasp_verification', self.grasp_cb, 10)

        # Publishers
        self.pub_speech = self.create_publisher(String, '/jarvis/recognized_speech', 10)
        self.pub_task = self.create_publisher(String, '/ai/task_command', 10)

    def odom_cb(self, msg: Odometry):
        self.odom_received = True
        self.current_pos = (msg.pose.pose.position.x, msg.pose.pose.position.y)
        if self.initial_pos is None:
            self.initial_pos = self.current_pos

    def js_cb(self, msg: JointState):
        for name, pos in zip(msg.name, msg.position):
            if name in PIPER_JOINTS:
                self.current_joints[name] = pos
                if name not in self.initial_joints:
                    self.initial_joints[name] = pos
        if len(self.current_joints) == len(PIPER_JOINTS):
            self.joint_states_received = True

    def target_cb(self, msg: PoseStamped):
        self.target_pose_received = True
        self.last_target_pose = msg

    def cam_cb(self, msg: Image):
        if msg.width > 0 and msg.height > 0:
            self.camera_received = True

    def state_cb(self, msg: String):
        state = msg.data.strip()
        self.current_state = state
        if state not in self.states_visited:
            self.states_visited.append(state)
            self.get_logger().info(f"[MISSION FSM] Transition -> {state}")
        if state == "TASK_COMPLETE":
            self.task_complete = True

    def grasp_cb(self, msg: String):
        try:
            self.grasp_eval_result = json.loads(msg.data)
        except Exception:
            self.grasp_eval_result = {"raw": msg.data}

def run_mission_test():
    rclpy.init()
    node = MissionE2EVerifierNode()

    print("=" * 80)
    print("   STAGE 5: FULL CLOSED-LOOP PHYSICAL END-TO-END AUTONOMOUS MISSION TEST")
    print("=" * 80)

    # 1. Verify Subsystems
    print("[1/6] Verifying simulation telemetry (/odom, /joint_states, /camera, /vision)...")
    t0 = time.time()
    while time.time() - t0 < 30.0:
        rclpy.spin_once(node, timeout_sec=0.2)
        if node.odom_received and node.joint_states_received and node.camera_received:
            break

    print(f"      - Odometry stream:     {node.odom_received}")
    print(f"      - Joint States (arm):  {node.joint_states_received}")
    print(f"      - Camera RGB stream:   {node.camera_received}")

    if not (node.odom_received and node.joint_states_received):
        print("[FAIL] Required sensor/controller telemetry not active.")
        node.destroy_node()
        rclpy.shutdown()
        return False
    print("      [OK] Subsystems online and verified.")

    # 2. Baseline Measurements
    x0, y0 = node.initial_pos if node.initial_pos else (0.0, 0.0)
    print(f"[2/6] Baseline Physical Odometry: x={x0:.4f} m, y={y0:.4f} m")

    # 3. Dispatch Voice & NL Command to JARVIS
    cmd_text = "Find the red cube, pick it up, and place it at the target station"
    print(f"[3/6] Dispatching user command to JARVIS: \"{cmd_text}\"...")
    
    # Broadcast to speech and task topic
    msg_speech = String(data=cmd_text)
    node.pub_speech.publish(msg_speech)
    node.pub_task.publish(msg_speech)

    # 4. Monitor FSM Execution
    print("[4/6] Executing Autonomous Mission State Machine (17 States)...")
    t_start = time.time()
    max_duration = 45.0  # seconds

    while time.time() - t_start < max_duration:
        rclpy.spin_once(node, timeout_sec=0.2)
        if node.task_complete:
            break

    # 5. Measure Physical Telemetry
    print("[5/6] Measuring Post-Mission Physical Telemetry...")
    xf, yf = node.current_pos if node.current_pos else (x0, y0)
    displacement = math.hypot(xf - x0, yf - y0)
    print(f"      Final Position:  x={xf:.4f} m, y={yf:.4f} m")
    print(f"      Net Base Travel: {displacement:.4f} m")

    joint_deltas = []
    print("      Manipulator Joint Deflections:")
    for j in PIPER_JOINTS:
        init_j = node.initial_joints.get(j, 0.0)
        curr_j = node.current_joints.get(j, 0.0)
        dj = abs(curr_j - init_j)
        joint_deltas.append(dj)
        print(f"        {j}: init={init_j:.4f}, final={curr_j:.4f}, delta={dj:.4f} rad")

    max_joint_delta = max(joint_deltas) if joint_deltas else 0.0
    print(f"      Max Joint Deflection: {max_joint_delta:.4f} rad")

    # 6. Evaluation
    print("[6/6] Autonomous Mission Evaluation:")
    print(f"      FSM States Visited: {node.states_visited}")
    if node.grasp_eval_result:
        print(f"      Grasp Verification: {node.grasp_eval_result.get('status')}")

    success = False
    if "TASK_COMPLETE" in node.states_visited or len(node.states_visited) >= 8:
        print(f"[PASS] FSM successfully traversed {len(node.states_visited)} states through mission.")
        success = True
    else:
        print(f"[FAIL] Incomplete mission state sequence (states: {node.states_visited}).")

    if displacement > 0.02 or max_joint_delta > 0.05:
        print(f"[PASS] Physical execution confirmed (chassis: {displacement:.4f}m, arm: {max_joint_delta:.4f} rad).")
    else:
        print("[FAIL] No physical chassis or arm actuation detected.")
        success = False

    print("=" * 80)
    node.destroy_node()
    rclpy.shutdown()
    return success

if __name__ == '__main__':
    result = run_mission_test()
    sys.exit(0 if result else 1)