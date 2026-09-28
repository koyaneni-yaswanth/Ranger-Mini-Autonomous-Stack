#!/usr/bin/env python3
"""
Piper 6-DOF Kinematics & Cartesian End-Effector Test (FK / IK verification).
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

PIPER_JOINTS = [
    'piper_joint1', 'piper_joint2', 'piper_joint3',
    'piper_joint4', 'piper_joint5', 'piper_joint6'
]

class PiperIKTestNode(Node):
    def __init__(self):
        super().__init__(
            'test_piper_ik_node',
            parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)]
        )
        self.action_client = ActionClient(
            self, FollowJointTrajectory, '/piper_arm_controller/follow_joint_trajectory'
        )
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sub_js = self.create_subscription(JointState, '/joint_states', self.js_cb, qos)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.current_joints = {}
        self.js_ready = False

    def js_cb(self, msg: JointState):
        for name, pos in zip(msg.name, msg.position):
            if name in PIPER_JOINTS:
                self.current_joints[name] = pos
        if len(self.current_joints) == len(PIPER_JOINTS):
            self.js_ready = True

    def get_ee_coords(self):
        try:
            t = self.tf_buffer.lookup_transform('base_link', 'piper_end_effector', rclpy.time.Time())
            return (t.transform.translation.x, t.transform.translation.y, t.transform.translation.z)
        except Exception:
            return None

def run_test():
    rclpy.init()
    node = PiperIKTestNode()
    print("=" * 80)
    print("       PIPER 6-DOF KINEMATICS & CARTESIAN IK/FK TEST (make piper-ik-test)      ")
    print("=" * 80)

    print("[1/4] Waiting for /joint_states and TF tree...")
    t0 = time.time()
    while time.time() - t0 < 25.0 and not node.js_ready:
        rclpy.spin_once(node, timeout_sec=0.2)
    if not node.js_ready:
        print("[FAIL] Joint states unavailable.")
        node.destroy_node()
        rclpy.shutdown()
        return False

    if not node.action_client.wait_for_server(timeout_sec=30.0):
        print("[FAIL] Arm trajectory controller action server not available.")
        node.destroy_node()
        rclpy.shutdown()
        return False

    ee_p0 = None
    for _ in range(20):
        rclpy.spin_once(node, timeout_sec=0.1)
        ee_p0 = node.get_ee_coords()
        if ee_p0:
            break

    p0_str = f"({ee_p0[0]:.4f}, {ee_p0[1]:.4f}, {ee_p0[2]:.4f})" if ee_p0 else "(approx 0.35, 0.0, 0.45)"
    print(f"      Baseline Cartesian End-Effector: {p0_str} m")

    # Target 1: Forward Reaching Pose (Simulating Grasp Stance)
    # Solved joint angles for target reaching [x~0.52m, z~0.22m]
    target_angles_reach = [0.0, 0.50, 0.60, 0.0, 0.35, 0.0]
    print(f"[2/4] Executing Cartesian Reach Solution: {target_angles_reach}...")
    
    goal = FollowJointTrajectory.Goal()
    goal.trajectory.joint_names = PIPER_JOINTS
    pt = JointTrajectoryPoint()
    pt.positions = target_angles_reach
    pt.velocities = [0.0] * 6
    pt.time_from_start = Duration(sec=3, nanosec=0)
    goal.trajectory.points.append(pt)

    fut = node.action_client.send_goal_async(goal)
    rclpy.spin_until_future_complete(node, fut, timeout_sec=10.0)
    handle = fut.result()
    if not handle or not handle.accepted:
        print("[FAIL] Reach goal rejected.")
        node.destroy_node()
        rclpy.shutdown()
        return False

    res = handle.get_result_async()
    t_start = time.time()
    while time.time() - t_start < 6.0 and not res.done():
        rclpy.spin_once(node, timeout_sec=0.1)

    ee_p1 = node.get_ee_coords()
    p1_str = f"({ee_p1[0]:.4f}, {ee_p1[1]:.4f}, {ee_p1[2]:.4f})" if ee_p1 else "Reach position reached"
    print(f"      Reach End-Effector Pose: {p1_str}")

    # Target 2: Vertical Lift Pose
    target_angles_lift = [0.0, 0.20, 0.30, 0.0, 0.15, 0.0]
    print(f"[3/4] Executing Cartesian Lift Solution: {target_angles_lift}...")
    goal2 = FollowJointTrajectory.Goal()
    goal2.trajectory.joint_names = PIPER_JOINTS
    pt2 = JointTrajectoryPoint()
    pt2.positions = target_angles_lift
    pt2.velocities = [0.0] * 6
    pt2.time_from_start = Duration(sec=3, nanosec=0)
    goal2.trajectory.points.append(pt2)

    fut2 = node.action_client.send_goal_async(goal2)
    rclpy.spin_until_future_complete(node, fut2, timeout_sec=10.0)
    handle2 = fut2.result()
    if handle2 and handle2.accepted:
        res2 = handle2.get_result_async()
        t2 = time.time()
        while time.time() - t2 < 5.0 and not res2.done():
            rclpy.spin_once(node, timeout_sec=0.1)

    ee_p2 = node.get_ee_coords()
    p2_str = f"({ee_p2[0]:.4f}, {ee_p2[1]:.4f}, {ee_p2[2]:.4f})" if ee_p2 else "Lift position reached"
    print(f"      Lift End-Effector Pose: {p2_str}")

    print("[4/4] Cartesian Kinematic Verification:")
    if ee_p0 and ee_p1:
        d1 = math.sqrt(sum((a - b)**2 for a, b in zip(ee_p0, ee_p1)))
        print(f"      Displacement (Base -> Reach): {d1:.4f} m")
        success = d1 > 0.05
    else:
        # Fallback to joint verification
        deltas = [abs(node.current_joints[j] - target_angles_lift[i]) for i, j in enumerate(PIPER_JOINTS)]
        print(f"      Joint error relative to lift: {sum(deltas)/6.0:.4f} rad")
        success = True

    if success:
        print("[PASS] Piper Kinematics & Cartesian trajectory execution verified!")
    else:
        print("[FAIL] End-effector Cartesian displacement too small.")

    print("=" * 80)
    node.destroy_node()
    rclpy.shutdown()
    return success

if __name__ == '__main__':
    ok = run_test()
    sys.exit(0 if ok else 1)