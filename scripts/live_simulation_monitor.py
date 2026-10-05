#!/usr/bin/env python3
"""
JARVIS-X Live Simulation Monitor
Continuously streams concise real-time telemetry from Gazebo Harmonic, ros2_control,
Nav2, MoveIt 2, Perception, and Mission Orchestrator.
"""

import sys
import os
import time
import json
import math
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from rosgraph_msgs.msg import Clock
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import String, Bool

class LiveSimMonitorNode(Node):
    def __init__(self):
        super().__init__(
            'live_sim_monitor_node',
            parameter_overrides=[
                Parameter('use_sim_time', Parameter.Type.BOOL, True)
            ]
        )
        qos_be = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_LAST, depth=5)

        self.sim_time = 0.0
        self.last_clock_wall = time.time()
        self.gz_connected = False

        self.base_x = 0.0
        self.base_y = 0.0
        self.base_yaw = 0.0
        self.base_vel_lin = 0.0
        self.base_vel_ang = 0.0

        self.piper_joints = {}
        self.gripper_gap = 0.0

        self.cube_x = 0.0
        self.cube_y = 0.0
        self.cube_z = 0.0

        self.mission_state = "IDLE"
        self.safety_status = "SAFE"
        self.detections_count = 0

        # Subscriptions
        self.sub_clock = self.create_subscription(Clock, '/clock', self.clock_cb, 10)
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_cb, qos_be)
        self.sub_js = self.create_subscription(JointState, '/joint_states', self.js_cb, qos_be)
        self.sub_cube = self.create_subscription(PoseStamped, '/sim/red_cube_world_gt', self.cube_cb, 10)
        self.sub_state = self.create_subscription(String, '/mission/state', self.state_cb, 10)
        self.sub_vis = self.create_subscription(String, '/vision/detected_objects', self.vis_cb, 10)
        self.sub_estop = self.create_subscription(Bool, '/safety/estop_active', self.estop_cb, 10)

        self.timer = self.create_timer(0.5, self.render_telemetry)

    def clock_cb(self, msg: Clock):
        self.sim_time = msg.clock.sec + msg.clock.nanosec * 1e-9
        self.last_clock_wall = time.time()
        self.gz_connected = True

    def odom_cb(self, msg: Odometry):
        self.base_x = msg.pose.pose.position.x
        self.base_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.base_yaw = math.atan2(siny_cosp, cosy_cosp)
        self.base_vel_lin = msg.twist.twist.linear.x
        self.base_vel_ang = msg.twist.twist.angular.z

    def js_cb(self, msg: JointState):
        for name, pos in zip(msg.name, msg.position):
            if 'piper_joint' in name:
                self.piper_joints[name] = pos
            elif 'piper_finger' in name or 'piper_gripper' in name:
                self.gripper_gap = pos

    def cube_cb(self, msg: PoseStamped):
        self.cube_x = msg.pose.position.x
        self.cube_y = msg.pose.position.y
        self.cube_z = msg.pose.position.z

    def state_cb(self, msg: String):
        self.mission_state = msg.data.strip()

    def vis_cb(self, msg: String):
        try:
            d = json.loads(msg.data)
            if 'count' in d:
                self.detections_count = d['count']
            elif 'objects' in d:
                self.detections_count = len(d['objects'])
        except Exception:
            pass

    def estop_cb(self, msg: Bool):
        self.safety_status = "ESTOP_ENGAGED" if msg.data else "SAFE"

    def render_telemetry(self):
        if time.time() - self.last_clock_wall > 2.0:
            self.gz_connected = False

        conn_str = "\033[92mCONNECTED\033[0m" if self.gz_connected else "\033[91mDISCONNECTED\033[0m"
        
        # Clear screen / carriage return header
        sys.stdout.write("\033[H\033[J")
        sys.stdout.write("======================================================================\n")
        sys.stdout.write("                  JARVIS-X LIVE SIMULATION MONITOR                    \n")
        sys.stdout.write("──────────────────────────────────────────────────────────────────────\n")
        sys.stdout.write(f"  Gazebo Status:     {conn_str}\n")
        sys.stdout.write(f"  Simulation Time:   {self.sim_time:.2f} s\n")
        sys.stdout.write(f"  Ranger Mini Pose:  x={self.base_x:+.4f} m, y={self.base_y:+.4f} m, yaw={math.degrees(self.base_yaw):+.1f}°\n")
        sys.stdout.write(f"  Base Velocity:     linear={self.base_vel_lin:+.3f} m/s, angular={self.base_vel_ang:+.3f} rad/s\n")
        
        # Joint summary
        j_str = ", ".join([f"{k.split('_')[-1]}:{v:+.2f}" for k, v in sorted(self.piper_joints.items())]) if self.piper_joints else "Standby"
        sys.stdout.write(f"  Piper Arm (rad):   {j_str}\n")
        sys.stdout.write(f"  Piper Gripper:     stroke={self.gripper_gap:.4f} m\n")
        sys.stdout.write(f"  Red Cube GT:       x={self.cube_x:+.3f} m, y={self.cube_y:+.3f} m, z={self.cube_z:+.3f} m\n")
        sys.stdout.write(f"  Perception Lock:   {self.detections_count} active object(s) detected\n")
        sys.stdout.write(f"  Safety Supervisor: {self.safety_status}\n")
        sys.stdout.write(f"  Current FSM State: \033[96m{self.mission_state}\033[0m\n")
        sys.stdout.write("======================================================================\n")
        sys.stdout.write("  Press Ctrl+C to exit monitor.\n")
        sys.stdout.flush()

def main():
    rclpy.init()
    node = LiveSimMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()