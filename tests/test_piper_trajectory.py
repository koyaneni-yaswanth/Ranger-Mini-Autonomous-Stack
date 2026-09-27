#!/usr/bin/env python3
"import rclpy and other libs"

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

PIPER_JOINTS = [
    'piper_joint1',
    'piper_joint2',
    'piper_joint3',
    'piper_joint4',
    'piper_joint5',
    'piper_joint6'
]

class PiperTrajectoryTestNode(Node):
    def __init__(self):
        super().__init__(
            'piper_trajectory_test_node',
            parameter_overrides=[
                Parameter('use_sim_time', Parameter.Type.BOOL, True)
            ]
        )
        self.action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/piper_arm_controller/follow_joint_trajectory'
        )
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sub_js = self.create_subscription(JointState, '/joint_states', self.js_cb, qos)
        self.current_positions = {}
        self.initial_positions = {}
        self.js_received = False

    def js_cb(self, msg: JointState):
        for name, pos in zip(msg.name, msg.position):
            if name in PIPER_JOINTS:
                self.current_positions[name] = pos
                if name not in self.initial_positions:
                    self.initial_positions[name] = pos
        if len(self.current_positions) == len(PIPER_JOINTS):
            self.js_received = True

def run_test():
    rclpy.init()
    node = PiperTrajectoryTestNode()
    print('=' * 80)
    print('   STAGE 3: PIPER 6-DOF PHYSICAL TRAJECTORY CLPSED-LOOP TEST')
    print('=' * 80)
    print('[1/4] Waiting for Piper 6-DOF /joint_states telemetry...')
    st = time.time()
    while time.time() - st < 20.0 and not node.js_received:
        rclpy.spin_once(node, timeout_sec=0.2)
    if not node.js_received:
        print('[FAIL] Piper joints not found in /joint_states.')
        node.destroy_node()
        rclpy.shutdown()
        return False
    print('      Piper joints online:')
    for j in PIPER_JOINTS:
        print(f'        {j}: {node.initial_positions.get(j, 0.0):.4f} rad')

    print('[2/4] Waiting for /piper_arm_controller/follow_joint_trajectory action server...')
    if not node.action_client.wait_for_server(timeout_sec=30.0):
        print('[FAIL] FollowJointTrajectory action server not available.')
        node.destroy_node()
        rclpy.shutdown()
        return False
    print('      Action server is READY.')

    target_angles = [0.20, -0.40, 0.50, 0.25, -0.30, 0.15]
    print(f'[3/4] Dispatching 6-DOF Trajectory Goal (target: {target_angles})...')

    goal_msg = FollowJointTrajectory.Goal()
    goal_msg.trajectory.joint_names = PIPER_JOINTS
    p1 = JointTrajectoryPoint()
    p1.positions = target_angles
    p1.velocities = [0.0] * 6
    p1.time_from_start = Duration(sec=3, nanosec=0)
    goal_msg.trajectory.points.append(p1)

    future = node.action_client.send_goal_async(goal_msg)
    rclpy.spin_until_future_complete(node, future, timeout_sec=10.0)
    handle = future.result()
    if not handle or not handle.accepted:
        print('[FAIL] Trajectory goal rejected.')
        node.destroy_node()
        rclpy.shutdown()
        return False

    print('      Goal ACCEPTED by controller. Monitoring live physical joint execution...')
    res_future = handle.get_result_async()
    tstart = time.time()
    while time.time() - tstart < 8.0:
        rclpy.spin_once(node, timeout_sec=0.1)
        if res_future.done():
            break

    final_pos = dict(node.current_positions)
    print('[4/4] Final Physical Joint State Evaluation:')
    displacements = []
    for idx, j in enumerate(PIPER_JOINTS):
        ip = node.initial_positions.get(j, 0.0)
        fp = final_pos.get(j, 0.0)
        d = abs(fp - ip)
        displacements.append(d)
        print(f'        {j}: init={ip:.4f}, final={fp:.4f}, delta={d:.4f} rad')

    mean_d = sum(displacements) / len(displacements)
    max_d = max(displacements)
    print(f'      Mean displacement: {mean_d:.4f} rad')
    print(f'      Max displacement:  {max_d:.4f} rad')

    MIN_DISP = 0.05
    if mean_d >= MIN_DISP:
        print(f'[PASS] Measured physical joint motion ({mean_d:.4f} rad >= {MIN_DISP} rad).')
        result = True
    else:
        print(f'[FAIL] Insufficient joint motion ({mean_d:.4f} rad < {MIN_DISP} rad).')
        result = False

    print('=' * 80)
    node.destroy_node()
    rclpy.shutdown()
    return result

if __name__ == '__main__':
    result = run_test()
    sys.exit(0 if result else 1)
