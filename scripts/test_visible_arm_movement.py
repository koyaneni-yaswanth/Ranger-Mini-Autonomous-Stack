#!/usr/bin/env python3
"""
JARVIS-X Visible Piper Arm Movement Verification
Dispatches a safe joint trajectory and verifies closed-loop joint state displacement:
trajectory -> piper_arm_controller -> Gazebo physics -> /joint_states.
"""

import sys
import time
import math
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Duration

PIPER_JOINTS = [
    'piper_joint1', 'piper_joint2', 'piper_joint3',
    'piper_joint4', 'piper_joint5', 'piper_joint6'
]

class ArmMovementVerifierNode(Node):
    def __init__(self):
        super().__init__(
            'arm_movement_verifier_node',
            parameter_overrides=[
                Parameter('use_sim_time', Parameter.Type.BOOL, True)
            ]
        )
        qos_be = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_LAST, depth=10)

        self.current_joints = {}
        self.initial_joints = {}

        self.sub_js = self.create_subscription(JointState, '/joint_states', self.js_cb, qos_be)
        self.pub_traj = self.create_publisher(JointTrajectory, '/piper_arm_controller/joint_trajectory', 10)

    def js_cb(self, msg: JointState):
        for name, pos in zip(msg.name, msg.position):
            if name in PIPER_JOINTS:
                self.current_joints[name] = pos
                if name not in self.initial_joints:
                    self.initial_joints[name] = pos

def main():
    rclpy.init()
    node = ArmMovementVerifierNode()

    print("=" * 80)
    print("      JARVIS-X VISIBLE PHYSICAL PIPER ARM MOVEMENT VERIFICATION")
    print("=" * 80)

    # 1. Wait for initial joint states
    t0 = time.time()
    while len(node.initial_joints) < len(PIPER_JOINTS) and time.time() - t0 < 5.0:
        rclpy.spin_once(node, timeout_sec=0.1)

    if len(node.initial_joints) < len(PIPER_JOINTS):
        print(f"[FAIL] Piper joints not publishing on /joint_states ({len(node.initial_joints)}/{len(PIPER_JOINTS)})")
        sys.exit(1)

    print("[1/4] Baseline Joint Angles (rad):")
    for j in PIPER_JOINTS:
        print(f"      {j}: {node.initial_joints[j]:+.4f} rad")

    # 2. Dispatch safe search/reach stance [0.0, 0.25, 0.35, 0.0, 0.20, 0.0]
    target_angles = [0.0, 0.25, 0.35, 0.0, 0.20, 0.0]
    print(f"[2/4] Dispatching Target Arm Stance (Duration: 2.0s): {target_angles}")

    traj = JointTrajectory()
    traj.header.stamp.sec = 0
    traj.header.stamp.nanosec = 0
    traj.joint_names = PIPER_JOINTS

    pt = JointTrajectoryPoint()
    pt.positions = target_angles
    pt.velocities = [0.0] * len(PIPER_JOINTS)
    pt.time_from_start = Duration(sec=2, nanosec=0)
    traj.points.append(pt)

    for _ in range(5):
        node.pub_traj.publish(traj)
        time.sleep(0.05)

    # 3. Wait for execution and track deflection
    print("[3/4] Observing Joint Trajectory Execution...")
    t_exec = time.time()
    while time.time() - t_exec < 2.5:
        rclpy.spin_once(node, timeout_sec=0.1)

    # 4. Measure deltas
    deltas = {}
    print("[4/4] Measured Joint State Changes:")
    for i, j in enumerate(PIPER_JOINTS):
        init_val = node.initial_joints[j]
        curr_val = node.current_joints.get(j, init_val)
        d = abs(curr_val - init_val)
        deltas[j] = d
        print(f"      {j}: init={init_val:+.4f}, final={curr_val:+.4f}, delta={d:.4f} rad (Target: {target_angles[i]:+.4f})")

    max_delta = max(deltas.values())
    print("=" * 80)
    if max_delta > 0.15:
        print(f">>> [PASS] PIPER ARM MOVEMENT VERIFIED: Max Joint Delta = {max_delta:.4f} rad (Threshold > 0.15 rad) <<<")
        print("    Trajectory -> piper_arm_controller -> joint_states -> physical motion validated.")
        print("=" * 80)
        sys.exit(0)
    else:
        print(f">>> [FAIL] MOVEMENT INSUFFICIENT: Max Delta = {max_delta:.4f} rad <<<")
        print("=" * 80)
        sys.exit(1)

if __name__ == '__main__':
    main()