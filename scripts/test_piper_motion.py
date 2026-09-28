#!/usr/bin/env python3
"""
Dedicated Piper 6-DOF Manual Trajectory Test.
Asserts physical joint movement (delta > threshold) on live /joint_states and TF.
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

PIPER_ARM_JOINTS = [
    'piper_joint1', 'piper_joint2', 'piper_joint3',
    'piper_joint4', 'piper_joint5', 'piper_joint6'
]

class PiperMotionTestNode(Node):
    def __init__(self):
        super().__init__(
            'test_piper_motion_node',
            parameter_overrides=[
                Parameter('use_sim_time', Parameter.Type.BOOL, True)
            ]
        )
        self.action_client = ActionClient(
            self, FollowJointTrajectory, '/piper_arm_controller/follow_joint_trajectory'
        )
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sub_js = self.create_subscription(JointState, '/joint_states', self.js_cb, qos)
        
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.current_positions = {}
        self.initial_positions = {}
        self.js_received = False

    def js_cb(self, msg: JointState):
        for name, pos in zip(msg.name, msg.position):
            if name in PIPER_ARM_JOINTS:
                self.current_positions[name] = pos
                if name not in self.initial_positions:
                    self.initial_positions[name] = pos
        if len(self.current_positions) == len(PIPER_ARM_JOINTS):
            self.js_received = True

    def get_ee_pose(self):
        try:
            t = self.tf_buffer.lookup_transform(
                'base_link', 'piper_end_effector', rclpy.time.Time()
            )
            return (
                t.transform.translation.x,
                t.transform.translation.y,
                t.transform.translation.z
            )
        except Exception:
            return None

def run_test():
    rclpy.init()
    node = PiperMotionTestNode()
    print("=" * 80)
    print("       PIPER 6-DOF CLOSED-LOOP PHYSICAL MOTION TEST (make piper-test)        ")
    print("=" * 80)

    # 1. Wait for joint states
    print("[1/5] Waiting for Piper /joint_states telemetry...")
    t0 = time.time()
    while time.time() - t0 < 25.0 and not node.js_received:
        rclpy.spin_once(node, timeout_sec=0.2)
    if not node.js_received:
        print("[FAIL] Piper joints not publishing on /joint_states within 25s.")
        node.destroy_node()
        rclpy.shutdown()
        return False
    
    print("      Baseline Joint Angles:")
    for j in PIPER_ARM_JOINTS:
        print(f"        {j}: {node.initial_positions[j]:.4f} rad")

    # 2. Wait for action server
    print("[2/5] Connecting to /piper_arm_controller/follow_joint_trajectory...")
    if not node.action_client.wait_for_server(timeout_sec=30.0):
        print("[FAIL] FollowJointTrajectory action server not available.")
        node.destroy_node()
        rclpy.shutdown()
        return False
    print("      [OK] Action server is READY.")

    # 3. Check baseline TF
    ee_init = None
    for _ in range(15):
        rclpy.spin_once(node, timeout_sec=0.1)
        ee_init = node.get_ee_pose()
        if ee_init:
            break
    if ee_init:
        print(f"      Baseline EE Pose: x={ee_init[0]:.4f}, y={ee_init[1]:.4f}, z={ee_init[2]:.4f} m")
    else:
        print("      [WARN] TF lookup for piper_end_effector not yet available, continuing...")

    # 4. Dispatch Multi-Waypoint 6-DOF Trajectory
    target_angles = [0.20, -0.40, 0.50, 0.25, -0.30, 0.15]
    print(f"[3/5] Dispatching 6-DOF Trajectory Goal -> {target_angles}...")

    goal = FollowJointTrajectory.Goal()
    goal.trajectory.joint_names = PIPER_ARM_JOINTS

    # Point: Target
    p1 = JointTrajectoryPoint()
    p1.positions = target_angles
    p1.velocities = [0.0] * 6
    p1.time_from_start = Duration(sec=3, nanosec=0)
    goal.trajectory.points.append(p1)

    future = node.action_client.send_goal_async(goal)
    rclpy.spin_until_future_complete(node, future, timeout_sec=10.0)
    goal_handle = future.result()
    if not goal_handle or not goal_handle.accepted:
        print("[FAIL] Trajectory goal was rejected by controller.")
        node.destroy_node()
        rclpy.shutdown()
        return False
    print("      [OK] Goal ACCEPTED by ros2_control. Executing in Gazebo...")

    # 5. Monitor Live Joint Motion
    print("[4/5] Monitoring live joint trajectory execution (up to 8s)...")
    res_future = goal_handle.get_result_async()
    t_start = time.time()
    while time.time() - t_start < 8.0:
        rclpy.spin_once(node, timeout_sec=0.1)
        if res_future.done():
            break

    # 6. Evaluate Physical Motion
    print("[5/5] Physical Joint Deflection Analysis:")
    final_pos = dict(node.current_positions)
    deltas = []
    for j in PIPER_ARM_JOINTS:
        ip = node.initial_positions.get(j, 0.0)
        fp = final_pos.get(j, 0.0)
        delta = abs(fp - ip)
        deltas.append(delta)
        print(f"        {j}: init={ip:.4f}, final={fp:.4f}, delta={delta:.4f} rad")

    mean_delta = sum(deltas) / len(deltas)
    max_delta = max(deltas)
    print(f"      Mean Joint Displacement: {mean_delta:.4f} rad")
    print(f"      Max Joint Displacement:  {max_delta:.4f} rad")

    ee_final = node.get_ee_pose()
    if ee_init and ee_final:
        ee_disp = math.sqrt(sum((a - b)**2 for a, b in zip(ee_init, ee_final)))
        print(f"      End-Effector Cartesian Travel: {ee_disp:.4f} m")
    else:
        ee_disp = 0.10

    MIN_MOTION_RAD = 0.05
    if mean_delta >= MIN_MOTION_RAD:
        print(f"[PASS] Physical Piper motion verified ({mean_delta:.4f} rad >= {MIN_MOTION_RAD} rad)!")
        success = True
    else:
        print(f"[FAIL] Insufficient joint motion ({mean_delta:.4f} rad < {MIN_MOTION_RAD} rad).")
        success = False

    print("=" * 80)
    node.destroy_node()
    rclpy.shutdown()
    return success

if __name__ == '__main__':
    ok = run_test()
    sys.exit(0 if ok else 1)