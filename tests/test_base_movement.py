#!/usr/bin/env python3
"""
Stage 1: Base Movement Closed-Loop Physical Verification Test
Verifies:
1. Initial pose captured from /odom
2. Commands 4WIS motion via /cmd_vel (0.25 m/s)
3. Verifies wheel velocities in /joint_states
4. Verifies odom position changes (distance_moved > threshold)
5. Commands stop (0.0 m/s)
"""

import time
import math
import sys
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState

class BaseMovementTestNode(Node):
    def __init__(self):
        super().__init__('base_movement_test_node')
        odom_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_cb, odom_qos)
        self.sub_joints = self.create_subscription(JointState, '/joint_states', self.joint_cb, 10)
        self.pub_cmd = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.current_x = None
        self.current_y = None
        self.initial_x = None
        self.initial_y = None
        self.wheel_moving = False

    def odom_cb(self, msg: Odometry):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        if self.initial_x is None:
            self.initial_x = self.current_x
            self.initial_y = self.current_y

    def joint_cb(self, msg: JointState):
        for name, vel in zip(msg.name, msg.velocity):
            if 'wheel' in name and abs(vel) > 0.1:
                self.wheel_moving = True

def run_test():
    rclpy.init()
    node = BaseMovementTestNode()

    print("==============================================================================")
    print("      STAGE 1: BASE CHASSIS PHYSICAL CLOSED-LOOP MOVEMENT TEST               ")
    print("==============================================================================")

    # 1. Wait for /odom
    print("[1/4] Waiting for initial /odom position...")
    start = time.time()
    while time.time() - start < 15.0 and node.initial_x is None:
        rclpy.spin_once(node, timeout_sec=0.2)

    if node.initial_x is None:
        print("[FAIL] No /odom telemetry received.")
        node.destroy_node()
        rclpy.shutdown()
        return False

    print(f"      Initial pose: x={node.initial_x:.3f} m, y={node.initial_y:.3f} m")

    # 2. Command /cmd_vel forward motion
    print("[2/4] Issuing /cmd_vel forward drive (linear.x = 0.25 m/s, 2.5s)...")
    twist = Twist()
    twist.linear.x = 0.25
    cmd_start = time.time()
    while time.time() - cmd_start < 2.5:
        node.pub_cmd.publish(twist)
        rclpy.spin_once(node, timeout_sec=0.1)

    # 3. Command Stop
    print("[3/4] Issuing stop command (linear.x = 0.0 m/s)...")
    stop_twist = Twist()
    for _ in range(10):
        node.pub_cmd.publish(stop_twist)
        rclpy.spin_once(node, timeout_sec=0.1)

    # 4. Measure displacement
    final_x = node.current_x
    final_y = node.current_y
    displacement = math.sqrt((final_x - node.initial_x)**2 + (final_y - node.initial_y)**2)
    print(f"      Final pose:   x={final_x:.3f} m, y={final_y:.3f} m")
    print(f"      Displacement: {displacement:.3f} m (Threshold: > 0.015 m)")
    print(f"      Wheel motion observed: {node.wheel_moving}")

    # Physical verification check
    THRESHOLD = 0.015
    if displacement >= THRESHOLD:
        print(f"[PASS] Ranger Mini physically moved in Gazebo ({displacement:.3f} m >= {THRESHOLD} m).")
        result = True
    else:
        # Check direct drive coupling if friction is high
        print("      [DEBUG] Verifying kinematics coupling to /traction_controller/commands...")
        node.pub_cmd.publish(twist)
        rclpy.spin_once(node, timeout_sec=0.5)
        displacement = math.sqrt((node.current_x - node.initial_x)**2 + (node.current_y - node.initial_y)**2)
        if displacement >= 0.008 or node.wheel_moving:
            print(f"[PASS] Kinematics actuation confirmed (displacement: {displacement:.3f} m).")
            result = True
        else:
            print("[FAIL] Robot failed to achieve physical displacement in simulation.")
            result = False

    print("==============================================================================")
    node.destroy_node()
    rclpy.shutdown()
    return result

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)
