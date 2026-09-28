#!/usr/bin/env python3
"""
JARVIS-X ROS 2 RL Policy Adapter Node
Executes the trained PPO neural policy in real time (50 Hz),
interfacing live ROS 2 joint states and perception with piper_arm_controller.
Enforces kinematic bounding boxes, velocity limits, and emergency stop hooks.
"""

import os
import sys
import time
import math
import json
import numpy as np
import subprocess

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import PointStamped, PoseStamped
from std_msgs.msg import Bool, String, Empty

class ROS2PolicyAdapterNode(Node):
    def __init__(self):
        super().__init__('ros2_policy_adapter_node')
        self.get_logger().info("Initializing JARVIS-X ROS 2 RL Policy Adapter...")

        # 1. Load Policy Weights
        weights_path = "/home/yash/ranger_mini_lyrical_2604_project/models/exported/piper_reach_policy_weights.npz"
        if not os.path.exists(weights_path):
            self.get_logger().error(f"Policy weights not found: {weights_path}")
            raise FileNotFoundError(weights_path)

        data = np.load(weights_path)
        self.w1, self.b1 = data['w1'], data['b1']
        self.g1, self.bn1 = data['g1'], data['bn1']
        self.w2, self.b2 = data['w2'], data['b2']
        self.g2, self.bn2 = data['g2'], data['bn2']
        self.w3, self.b3 = data['w3'], data['b3']
        self.get_logger().info("Successfully loaded policy weights into memory.")

        # Kinematic Parameters
        self.joint_names = [
            "piper_joint1", "piper_joint2", "piper_joint3",
            "piper_joint4", "piper_joint5", "piper_joint6"
        ]
        self.q_min = np.array([-3.14, -1.57, -2.00, -3.14, -1.57, -3.14])
        self.q_max = np.array([ 3.14,  1.57,  2.00,  3.14,  1.57,  3.14])
        self.max_delta_q = 0.03  # rad per step at 50 Hz

        # Current Robot State
        self.current_q = np.array([0.0, 0.40, 1.20, 0.0, 0.20, 0.0])
        self.current_dq = np.zeros(6)
        self.target_pos = np.array([0.45, 0.0, 0.33])
        self.cube_pos = np.array([0.45, 0.0, 0.33])
        self.gripper_state = np.array([0.035, 0.035])

        # Execution Flags
        self.is_active = False
        self.emergency_stopped = False
        self.step_count = 0
        self.max_steps = 150  # 3.0 seconds max
        self.target_reached = False
        self.grasped = False

        # ROS 2 Subscribers
        self.sub_js = self.create_subscription(JointState, '/joint_states', self.joint_state_cb, 10)
        self.sub_cube = self.create_subscription(PointStamped, '/sim/red_cube_ground_truth', self.cube_cb, 10)
        self.sub_estop = self.create_subscription(Bool, '/safety/emergency_stop', self.estop_cb, 10)
        self.sub_cmd = self.create_subscription(Bool, '/jarvis/execute_rl_reach', self.cmd_cb, 10)

        # ROS 2 Publishers
        self.pub_arm = self.create_publisher(JointTrajectory, '/piper_arm_controller/joint_trajectory', 10)
        self.pub_attach = self.create_publisher(Empty, '/sim/gripper_attach', 10)
        self.pub_detach = self.create_publisher(Empty, '/sim/gripper_detach', 10)
        self.pub_status = self.create_publisher(String, '/jarvis/rl_policy_status', 10)

        # 50 Hz Control Loop
        self.timer = self.create_timer(0.02, self.control_loop)
        self.get_logger().info("RL Policy Adapter ready on /jarvis/execute_rl_reach.")

    def joint_state_cb(self, msg: JointState):
        name_map = {name: i for i, name in enumerate(msg.name)}
        for idx, j_name in enumerate(self.joint_names):
            if j_name in name_map:
                p_idx = name_map[j_name]
                self.current_q[idx] = msg.position[p_idx]
                if len(msg.velocity) > p_idx:
                    self.current_dq[idx] = msg.velocity[p_idx]

    def cube_cb(self, msg: PointStamped):
        self.cube_pos[0] = msg.point.x
        self.cube_pos[1] = msg.point.y
        self.cube_pos[2] = msg.point.z
        self.target_pos = self.cube_pos.copy()

    def estop_cb(self, msg: Bool):
        self.emergency_stopped = msg.data
        if self.emergency_stopped and self.is_active:
            self.get_logger().warn("EMERGENCY STOP TRIGGERED: Pausing RL policy execution.")
            self.is_active = False

    def cmd_cb(self, msg: Bool):
        if msg.data:
            self.get_logger().info("Starting RL Closed-Loop Reaching & Grasping Routine...")
            self.is_active = True
            self.step_count = 0
            self.target_reached = False
            self.grasped = False
        else:
            self.is_active = False
            self.get_logger().info("RL Execution stopped by command.")

    def forward_kinematics(self, q):
        # Base offset on Ranger Mini
        base_x, base_y, base_z = 0.10, 0.0, 0.22
        # Simple analytical FK for Piper
        q1, q2, q3, q4, q5, q6 = q

        # Link frames
        x = base_x + 0.30 * math.sin(q2) + 0.20 * math.sin(q2 + q3) + 0.14 * math.sin(q2 + q3 + q5)
        y = base_y - math.sin(q1) * x * 0.5
        z = base_z + 0.16 + 0.30 * math.cos(q2) + 0.20 * math.cos(q2 + q3) + 0.14 * math.cos(q2 + q3 + q5)
        return np.array([x, y, z])

    def evaluate_policy(self, obs):
        x = obs
        # Layer 1
        x = x @ self.w1.T + self.b1
        m1, v1 = x.mean(), x.var()
        x = (x - m1) / np.sqrt(v1 + 1e-5) * self.g1 + self.bn1
        x = np.where(x > 0, x, np.exp(x) - 1.0)
        # Layer 2
        x = x @ self.w2.T + self.b2
        m2, v2 = x.mean(), x.var()
        x = (x - m2) / np.sqrt(v2 + 1e-5) * self.g2 + self.bn2
        x = np.where(x > 0, x, np.exp(x) - 1.0)
        # Layer 3
        x = x @ self.w3.T + self.b3
        return np.tanh(x)

    def control_loop(self):
        if not self.is_active or self.emergency_stopped:
            return

        self.step_count += 1
        ee_pos = self.forward_kinematics(self.current_q)
        dist = np.linalg.norm(ee_pos - self.cube_pos)

        # Check for grasp contact
        if dist < 0.045 and not self.grasped:
            self.grasped = True
            self.get_logger().info(f"Target reached (dist={dist*100:.1f}cm). Triggering Physical Grasp & DetachableJoint...")
            self.pub_attach.publish(Empty())
            # Invoke gz topic directly
            subprocess.run(
                ["/opt/ros/lyrical/opt/gz_tools_vendor/bin/gz", "topic", "-t", "/model/ranger_mini/attach", "-m", "gz.msgs.Empty", "-p", "''"],
                capture_output=True, timeout=5
            )

        # Assemble observation vector [24]
        ee_quat = np.array([0.0, 1.0, 0.0, 0.0])
        obs = np.concatenate([
            self.current_q,          # 6
            self.current_dq,         # 6
            ee_pos,                  # 3
            ee_quat,                 # 4
            self.target_pos,         # 3
            self.gripper_state       # 2
        ])

        # Evaluate policy
        action = self.evaluate_policy(obs)
        arm_action = action[:6]
        delta_q = arm_action * self.max_delta_q

        # Safety Check: Kinematic clamp
        cmd_q = np.clip(self.current_q + delta_q, self.q_min, self.q_max)

        # Publish JointTrajectory Command
        traj = JointTrajectory()
        traj.header.stamp.sec = 0
        traj.header.stamp.nanosec = 0
        traj.header.frame_id = "base_link"
        traj.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = [float(x) for x in cmd_q]
        point.velocities = [float(v) for v in (delta_q / 0.02)]
        point.time_from_start.nanosec = int(0.04 * 1e9)  # 40ms lookahead
        traj.points.append(point)

        self.pub_arm.publish(traj)

        # Publish status
        status_msg = String()
        status_msg.data = json.dumps({
            "step": self.step_count,
            "dist_mm": round(float(dist * 1000.0), 1),
            "grasped": self.grasped,
            "current_q": [round(float(q), 3) for q in self.current_q]
        })
        self.pub_status.publish(status_msg)

        # Lift & Completion check
        if self.grasped and self.step_count > 60:
            self.get_logger().info("Grasp secured! Commanding vertical lift...")
            lift_q = [0.0, 0.35, 1.00, 0.0, 0.40, 0.0]
            lift_traj = JointTrajectory()
            lift_traj.header.stamp.sec = 0
            lift_traj.header.stamp.nanosec = 0
            lift_traj.joint_names = self.joint_names
            pt = JointTrajectoryPoint()
            pt.positions = [float(x) for x in lift_q]
            pt.time_from_start.sec = 2
            lift_traj.points.append(pt)
            self.pub_arm.publish(lift_traj)

            self.target_reached = True
            self.is_active = False
            self.get_logger().info(">>> RL Reaching, Grasping, and Lifting Routine COMPLETED <<<")

        elif self.step_count >= self.max_steps:
            self.get_logger().warn("RL Reaching routine timed out (max steps reached).")
            self.is_active = False

def main(args=None):
    rclpy.init(args=args)
    node = ROS2PolicyAdapterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()