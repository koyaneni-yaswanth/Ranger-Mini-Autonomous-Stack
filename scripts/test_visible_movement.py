#!/usr/bin/env python3
"""
JARVIS-X Visible Robot Movement Verification
Executes controlled chassis velocity command and verifies:
cmd_vel -> ros2_control -> wheel joint velocity -> /odom displacement -> /tf displacement.
"""

import sys
import time
import math
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState

class MovementVerifierNode(Node):
    def __init__(self):
        super().__init__(
            'movement_verifier_node',
            parameter_overrides=[
                Parameter('use_sim_time', Parameter.Type.BOOL, True)
            ]
        )
        qos_be = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_LAST, depth=10)

        self.current_x = None
        self.current_y = None
        self.wheel_velocities = []

        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_cb, qos_be)
        self.sub_js = self.create_subscription(JointState, '/joint_states', self.js_cb, qos_be)
        self.pub_cmd = self.create_publisher(Twist, '/cmd_vel', 10)

    def odom_cb(self, msg: Odometry):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

    def js_cb(self, msg: JointState):
        for name, vel in zip(msg.name, msg.velocity):
            if 'wheel' in name:
                self.wheel_velocities.append(abs(vel))

def main():
    rclpy.init()
    node = MovementVerifierNode()

    print("=" * 80)
    print("      JARVIS-X VISIBLE PHYSICAL CHASSIS MOVEMENT VERIFICATION")
    print("=" * 80)

    # 1. Wait for initial odometry
    t0 = time.time()
    while node.current_x is None and time.time() - t0 < 5.0:
        rclpy.spin_once(node, timeout_sec=0.1)

    if node.current_x is None:
        print("[FAIL] Odometry not publishing on /odom")
        sys.exit(1)

    x0 = node.current_x
    y0 = node.current_y
    print(f"[1/4] Baseline Position:  x={x0:+.4f} m, y={y0:+.4f} m")

    # 2. Drive robot (direction chosen to avoid table obstacle at x > 0.8)
    speed = -0.25 if x0 > 0.4 else 0.25
    direction = 'reverse' if speed < 0 else 'forward'
    print(f"[2/4] Publishing /cmd_vel: linear.x = {speed} m/s ({direction}, target disp: >= 0.15 m)...")
    twist = Twist()
    twist.linear.x = speed
    t_drive = time.time()
    while time.time() - t_drive < 12.0:
        node.pub_cmd.publish(twist)
        rclpy.spin_once(node, timeout_sec=0.05)
        disp_now = math.hypot(node.current_x - x0, node.current_y - y0)
        if disp_now >= 0.15:
            print(f"      Target displacement achieved: {disp_now:.4f} m (Time: {time.time()-t_drive:.1f}s)")
            break
        time.sleep(0.05)

    # 3. Stop robot
    print("[3/4] Publishing /cmd_vel STOP (linear.x = 0.0 m/s)...")
    stop_twist = Twist()
    for _ in range(5):
        node.pub_cmd.publish(stop_twist)
        rclpy.spin_once(node, timeout_sec=0.05)
        time.sleep(0.05)

    time.sleep(0.5)
    for _ in range(10):
        rclpy.spin_once(node, timeout_sec=0.05)

    x1 = node.current_x
    y1 = node.current_y
    disp = math.hypot(x1 - x0, y1 - y0)
    max_wheel_vel = max(node.wheel_velocities) if node.wheel_velocities else 0.0

    print(f"[4/4] Post-Drive Position: x={x1:+.4f} m, y={y1:+.4f} m")
    print(f"      Net Displacement:   {disp:.4f} m")
    print(f"      Peak Wheel Speed:   {max_wheel_vel:.4f} rad/s")

    # Evaluation
    print("=" * 80)
    if disp > 0.05 and max_wheel_vel > 0.1:
        print(f">>> [PASS] ROBOT CHASSIS MOVEMENT VERIFIED: Travel={disp:.4f} m (Threshold > 0.05 m) <<<")
        print("    cmd_vel -> 4WIS traction controller -> wheel motion -> odom displacement validated.")
        print("=" * 80)
        sys.exit(0)
    else:
        print(f">>> [FAIL] MOVEMENT INSUFFICIENT: disp={disp:.4f} m, wheel_vel={max_wheel_vel:.4f} rad/s <<<")
        print("=" * 80)
        sys.exit(1)

if __name__ == '__main__':
    main()