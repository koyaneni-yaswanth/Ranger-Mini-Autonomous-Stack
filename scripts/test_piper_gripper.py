#!/usr/bin/env python3
"""
Dedicated Piper Parallel Gripper Action & Stroke Test.
Commands OPEN (0.03m) and CLOSE (0.00m) and asserts physical finger displacement.
"""

import sys
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import JointState
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

GRIPPER_JOINT = 'piper_finger_left_joint'

class PiperGripperTestNode(Node):
    def __init__(self):
        super().__init__(
            'test_piper_gripper_node',
            parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)]
        )
        self.action_client = ActionClient(
            self, FollowJointTrajectory, '/piper_gripper_controller/follow_joint_trajectory'
        )
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sub_js = self.create_subscription(JointState, '/joint_states', self.js_cb, qos)
        self.current_finger_pos = None
        self.initial_finger_pos = None

    def js_cb(self, msg: JointState):
        for name, pos in zip(msg.name, msg.position):
            if name == GRIPPER_JOINT:
                self.current_finger_pos = pos
                if self.initial_finger_pos is None:
                    self.initial_finger_pos = pos

    def command_gripper(self, pos_target: float, duration_sec: float = 2.0):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = [GRIPPER_JOINT]
        pt = JointTrajectoryPoint()
        pt.positions = [float(pos_target)]
        pt.velocities = [0.0]
        pt.time_from_start = Duration(sec=int(duration_sec), nanosec=int((duration_sec % 1) * 1e9))
        goal.trajectory.points.append(pt)

        fut = self.action_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, fut, timeout_sec=10.0)
        handle = fut.result()
        if not handle or not handle.accepted:
            return False

        res = handle.get_result_async()
        t0 = time.time()
        while time.time() - t0 < (duration_sec + 2.0) and not res.done():
            rclpy.spin_once(self, timeout_sec=0.1)
        return True

def run_test():
    rclpy.init()
    node = PiperGripperTestNode()
    print("=" * 80)
    print("      PIPER PARALLEL GRIPPER ACTION & STROKE TEST (make piper-gripper-test)    ")
    print("=" * 80)

    print("[1/4] Waiting for gripper /joint_states...")
    t0 = time.time()
    while time.time() - t0 < 25.0 and node.current_finger_pos is None:
        rclpy.spin_once(node, timeout_sec=0.2)
    if node.current_finger_pos is None:
        print("[FAIL] piper_finger_left_joint not found in /joint_states.")
        node.destroy_node()
        rclpy.shutdown()
        return False
    print(f"      Baseline finger position: {node.initial_finger_pos:.4f} m")

    print("[2/4] Connecting to /piper_gripper_controller/follow_joint_trajectory...")
    if not node.action_client.wait_for_server(timeout_sec=30.0):
        print("[FAIL] Gripper action server unavailable.")
        node.destroy_node()
        rclpy.shutdown()
        return False
    print("      [OK] Gripper action server is READY.")

    # Command OPEN (0.03 m)
    print("[3/4] Commanding Gripper OPEN (target: 0.030 m / full stroke)...")
    ok = node.command_gripper(0.030, duration_sec=2.0)
    if not ok:
        print("[FAIL] Open goal rejected.")
        node.destroy_node()
        rclpy.shutdown()
        return False

    pos_open = node.current_finger_pos
    stroke_open = abs(pos_open - node.initial_finger_pos)
    print(f"      Finger position after OPEN: {pos_open:.4f} m (delta: {stroke_open:.4f} m)")

    # Command CLOSE (0.00 m)
    print("[4/4] Commanding Gripper CLOSE (target: 0.000 m)...")
    ok = node.command_gripper(0.000, duration_sec=2.0)
    if not ok:
        print("[FAIL] Close goal rejected.")
        node.destroy_node()
        rclpy.shutdown()
        return False

    pos_close = node.current_finger_pos
    stroke_close = abs(pos_open - pos_close)
    print(f"      Finger position after CLOSE: {pos_close:.4f} m (stroke closed: {stroke_close:.4f} m)")

    MIN_STROKE = 0.015  # at least 15mm stroke verified
    if stroke_open >= MIN_STROKE or stroke_close >= MIN_STROKE:
        print(f"[PASS] Physical gripper actuation verified (stroke {max(stroke_open, stroke_close):.4f} m >= {MIN_STROKE} m)!")
        success = True
    else:
        print(f"[FAIL] Insufficient gripper stroke ({max(stroke_open, stroke_close):.4f} m < {MIN_STROKE} m).")
        success = False

    print("=" * 80)
    node.destroy_node()
    rclpy.shutdown()
    return success

if __name__ == '__main__':
    ok = run_test()
    sys.exit(0 if ok else 1)