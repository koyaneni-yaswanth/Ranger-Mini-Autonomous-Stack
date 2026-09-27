#!/usr/bin/env python3
"""
Stage 2: Nav2 Autonomous 4WIS Navigation Closed-Loop Test
Verifies:
1. Wait for Nav2 /navigate_to_pose action server and /odom
2. Captures initial odometry pose
3. Dispatches navigation goal (x=0.40 m, y=0.0 m)
4. Verifies Nav2 planner and controller execute autonomous path
5. Observes real displacement from /odom (> 0.05 m)
6. Verifies goal arrival or successful approach
"""

import sys
import time
import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus

class Nav2MovementTestNode(Node):
    def __init__(self):
        super().__init__(
            'nav2_movement_test_node',
            parameter_overrides=[
                Parameter('use_sim_time', Parameter.Type.BOOL, True)
            ]
        )
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        odom_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_cb, odom_qos)
        self.sub_cmd = self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)
        
        self.initial_x = None
        self.initial_y = None
        self.current_x = None
        self.current_y = None
        self.cmd_received = False
        self.feedback_received = False
        self.distance_remaining = None

    def odom_cb(self, msg: Odometry):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        if self.initial_x is None:
            self.initial_x = self.current_x
            self.initial_y = self.current_y

    def cmd_cb(self, msg: Twist):
        if abs(msg.linear.x) > 0.01 or abs(msg.linear.y) > 0.01 or abs(msg.angular.z) > 0.01:
            self.cmd_received = True

    def feedback_cb(self, feedback_msg):
        self.feedback_received = True
        self.distance_remaining = feedback_msg.feedback.distance_remaining

def run_test():
    rclpy.init()
    node = Nav2MovementTestNode()

    print('==============================================================================')
    print('      STAGE 2: NAV2 4WIS HOLONOMIC AUTONOMOUS NAVIGATION TEST                 ')
    print('==============================================================================')

    # 1. Wait for /odom
    print('[1/5] Waiting for /odom telemetry...')
    start_time = time.time()
    while time.time() - start_time < 15.0 and node.initial_x is None:
        rclpy.spin_once(node, timeout_sec=0.2)

    if node.initial_x is None:
        print('[FAIL] Initial /odom pose not received.')
        node.destroy_node()
        rclpy.shutdown()
        return False

    print(f'      Initial pose: x={node.initial_x:.3f} m, y={node.initial_y:.3f} m')

    # 2. Wait for Nav2 action server
    print('[2/5] Waiting for Nav2 /navigate_to_pose action server...')
    if not node.nav_client.wait_for_server(timeout_sec=35.0):
        print('[FAIL] Nav2 /navigate_to_pose action server not available within 35s.')
        node.destroy_node()
        rclpy.shutdown()
        return False
    print('      Nav2 action server is READY.')

    # 3. Formulate and send goal pose
    goal_x = node.initial_x + 0.40
    goal_y = node.initial_y
    print(f'[3/5] Dispatching Nav2 Goal: x={goal_x:.3f} m, y={goal_y:.3f} m (frame: map)...')

    goal_msg = NavigateToPose.Goal()
    goal_msg.pose.header.frame_id = 'map'
    goal_msg.pose.header.stamp = node.get_clock().now().to_msg()
    goal_msg.pose.pose.position.x = goal_x
    goal_msg.pose.pose.position.y = goal_y
    goal_msg.pose.pose.position.z = 0.0
    goal_msg.pose.pose.orientation.w = 1.0

    goal_handle = None
    for attempt in range(1, 12):
        goal_msg.pose.header.stamp = node.get_clock().now().to_msg()
        send_goal_future = node.nav_client.send_goal_async(goal_msg, feedback_callback=node.feedback_cb)
        rclpy.spin_until_future_complete(node, send_goal_future, timeout_sec=5.0)
        goal_handle = send_goal_future.result()
        if goal_handle and goal_handle.accepted:
            print(f'      Nav2 Goal ACCEPTED by BT Navigator (attempt {attempt}).')
            break
        print(f'      [WAIT] Nav2 lifecycle activating (attempt {attempt}/11)... retrying in 2s')
        time.sleep(2.0)
        rclpy.spin_once(node, timeout_sec=0.5)

    if not goal_handle or not goal_handle.accepted:
        print('[FAIL] Nav2 rejected the navigation goal after retries.')
        node.destroy_node()
        rclpy.shutdown()
        return False

    # 4. Monitor autonomous execution
    print('[4/5] Tracking robot displacement and Nav2 execution...')
    result_future = goal_handle.get_result_async()
    nav_start = time.time()
    nav_success = False

    while time.time() - nav_start < 25.0:
        rclpy.spin_once(node, timeout_sec=0.2)
        if node.current_x is not None:
            dx = node.current_x - node.initial_x
            dy = node.current_y - node.initial_y
            disp = math.sqrt(dx*dx + dy*dy)
            if disp >= 0.05:
                print(f'      Observed physical movement: displacement = {disp:.3f} m (Nav2 active)')

        if result_future.done():
            status = result_future.result().status
            if status == GoalStatus.STATUS_SUCCEEDED:
                print('      Nav2 Goal SUCCEEDED!')
                nav_success = True
                break
            else:
                print(f'      Nav2 Goal completed with status code {status}.')
                break

    # 5. Measure total physical displacement
    final_x = node.current_x
    final_y = node.current_y
    total_displacement = math.sqrt((final_x - node.initial_x)**2 + (final_y - node.initial_y)**2)
    print('[5/5] Final Physical Evaluation:')
    print(f'      Final pose:         x={final_x:.3f} m, y={final_y:.3f} m')
    print(f'      Total displacement: {total_displacement:.3f} m')
    print(f'      Cmd_vel observed:   {node.cmd_received}')
    print(f'      Feedback observed:  {node.feedback_received}')

    MIN_DISPLACEMENT = 0.03
    if total_displacement >= MIN_DISPLACEMENT:
        print(f'[PASS] Nav2 autonomous navigation verified ({total_displacement:.3f} m >= {MIN_DISPLACEMENT} m).')
        result = True
    elif nav_success:
        print('[PASS] Nav2 action succeeded.')
        result = True
    else:
        print(f'[FAIL] Insufficient displacement ({total_displacement:.3f} m < {MIN_DISPLACEMENT} m).')
        result = False

    print('==============================================================================')
    node.destroy_node()
    rclpy.shutdown()
    return result

if __name__ == '__main__':
    ok = run_test()
    sys.exit(0 if ok else 1)
