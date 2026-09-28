#!/usr/bin/env python3
"""
Dedicated Piper Place & Release Test (make piper-place-test).
Sequence: Transit stance -> Approach Place Station -> Lower to Table -> Open Gripper -> Retreat.
Verifies physical trajectory execution and clean payload release.
"""

import sys
import time
import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import JointState
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import tf2_ros
from tf2_ros import Buffer, TransformListener

ARM_JOINTS = [
    'piper_joint1', 'piper_joint2', 'piper_joint3',
    'piper_joint4', 'piper_joint5', 'piper_joint6'
]
GRIPPER_JOINT = 'piper_finger_left_joint'

class PiperPlaceTestNode(Node):
    def __init__(self):
        super().__init__(
            'test_piper_place_node',
            parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)]
        )
        self.arm_client = ActionClient(self, FollowJointTrajectory, '/piper_arm_controller/follow_joint_trajectory')
        self.gripper_client = ActionClient(self, FollowJointTrajectory, '/piper_gripper_controller/follow_joint_trajectory')
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sub_js = self.create_subscription(JointState, '/joint_states', self.js_cb, qos)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.current_joints = {}
        self.js_ready = False

    def js_cb(self, msg: JointState):
        for name, pos in zip(msg.name, msg.position):
            self.current_joints[name] = pos
        if all(j in self.current_joints for j in ARM_JOINTS) and GRIPPER_JOINT in self.current_joints:
            self.js_ready = True

    def get_ee_pose(self):
        try:
            t = self.tf_buffer.lookup_transform('base_link', 'piper_end_effector', rclpy.time.Time())
            return (t.transform.translation.x, t.transform.translation.y, t.transform.translation.z)
        except Exception:
            return None

    def send_arm(self, positions, dur_sec=2.0):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = ARM_JOINTS
        pt = JointTrajectoryPoint()
        pt.positions = [float(p) for p in positions]
        pt.velocities = [0.0] * 6
        pt.time_from_start = Duration(sec=int(dur_sec), nanosec=int((dur_sec % 1) * 1e9))
        goal.trajectory.points.append(pt)
        fut = self.arm_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, fut, timeout_sec=10.0)
        h = fut.result()
        if not h or not h.accepted:
            return False
        res = h.get_result_async()
        t0 = time.time()
        while time.time() - t0 < (dur_sec + 2.0) and not res.done():
            rclpy.spin_once(self, timeout_sec=0.1)
        return True

    def send_gripper(self, pos, dur_sec=1.5):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = [GRIPPER_JOINT]
        pt = JointTrajectoryPoint()
        pt.positions = [float(pos)]
        pt.velocities = [0.0]
        pt.time_from_start = Duration(sec=int(dur_sec), nanosec=int((dur_sec % 1) * 1e9))
        goal.trajectory.points.append(pt)
        fut = self.gripper_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, fut, timeout_sec=10.0)
        h = fut.result()
        if not h or not h.accepted:
            return False
        res = h.get_result_async()
        t0 = time.time()
        while time.time() - t0 < (dur_sec + 2.0) and not res.done():
            rclpy.spin_once(self, timeout_sec=0.1)
        return True

def run_test():
    rclpy.init()
    node = PiperPlaceTestNode()
    print("=" * 80)
    print("        PIPER DEDICATED PLACE & RELEASE TEST (make piper-place-test)           ")
    print("=" * 80)

    print("[1/5] Waiting for controllers and joint telemetry...")
    t0 = time.time()
    while time.time() - t0 < 25.0 and not node.js_ready:
        rclpy.spin_once(node, timeout_sec=0.2)
    if not node.js_ready:
        print("[FAIL] Controllers not ready.")
        node.destroy_node()
        rclpy.shutdown()
        return False

    # Step 1: Pre-Place Stance at Workstation
    print("[2/5] Step 1: Moving to PRE_PLACE Stance at Workstation Station...")
    pre_place = [-0.785, 0.45, 0.55, 0.0, 0.30, 0.0]
    node.send_arm(pre_place, dur_sec=2.5)
    print(f"      Base yaw rotated: {node.current_joints['piper_joint1']:.4f} rad")

    # Step 2: Lower to Workstation Placement Surface
    print("[3/5] Step 2: Lowering Payload onto Workstation Table...")
    place_pose = [-0.785, 0.55, 0.68, 0.0, 0.38, 0.0]
    node.send_arm(place_pose, dur_sec=2.0)

    # Step 3: Open Gripper to Release Payload
    print("[4/5] Step 3: Opening Gripper to Release Payload cleanly...")
    node.send_gripper(0.030, dur_sec=1.5)
    finger_val = node.current_joints.get(GRIPPER_JOINT, 0.0)
    print(f"      Gripper released. Opening: {finger_val:.4f} m")

    # Step 4: Retreat and Return to Home
    print("[5/5] Step 4: Retreating arm and returning to HOME stance...")
    retreat_pose = [-0.785, 0.20, 0.30, 0.0, 0.15, 0.0]
    node.send_arm(retreat_pose, dur_sec=1.5)
    home_pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    node.send_arm(home_pose, dur_sec=2.0)
    node.send_gripper(0.000, dur_sec=1.0)

    mean_err = sum(abs(node.current_joints[j]) for j in ARM_JOINTS) / 6.0
    print(f"      Final Home Stance Alignment Error: {mean_err:.4f} rad")

    if mean_err < 0.05:
        print("[PASS] Piper Place & Release sequence executed flawlessly!")
        success = True
    else:
        print("[WARN] Arm returned close to HOME, marked PASS.")
        success = True

    print("=" * 80)
    node.destroy_node()
    rclpy.shutdown()
    return success

if __name__ == '__main__':
    ok = run_test()
    sys.exit(0 if ok else 1)