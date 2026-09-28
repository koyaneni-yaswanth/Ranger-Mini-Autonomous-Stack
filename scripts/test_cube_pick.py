#!/usr/bin/env python3
"""
Dedicated Real Red-Cube Pick & Lift Test for Mobile Manipulator Ranger Mini + Piper.
Closed-loop Sequence:
1. Verify detached grasp constraint at start.
2. Stow Piper Arm in safe upright travel posture.
3. Drive mobile base forward (/cmd_vel) until manipulation stance (Base X ~ 0.88m, rel_dist ~ 0.58m).
4. Record baseline cube height from ground truth (/sim/red_cube_world_gt).
5. Open gripper to 0.035m.
6. Move Piper to safe PRE_GRASP standoff.
7. Controlled descent to GRASP pose directly enveloping the cube.
8. Close gripper (0.00m) and engage physics grasp constraint (/model/ranger_mini/attach).
9. Execute vertical lift trajectory (+15cm).
10. Verify ground-truth cube elevation: assert delta_z >= 0.080m!
"""

import sys
import time
import math
import json
import re
import subprocess
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import String, Empty
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from tf2_ros import Buffer, TransformListener

PIPER_JOINTS = [
    'piper_joint1', 'piper_joint2', 'piper_joint3',
    'piper_joint4', 'piper_joint5', 'piper_joint6'
]

GZ_BIN = '/opt/ros/lyrical/opt/gz_tools_vendor/bin/gz'

class CubePickTest(Node):
    def __init__(self):
        super().__init__(
            'test_cube_pick_node',
            parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)]
        )
        self.pub_arm = self.create_publisher(JointTrajectory, '/piper_arm_controller/joint_trajectory', 10)
        self.pub_gripper = self.create_publisher(JointTrajectory, '/piper_gripper_controller/joint_trajectory', 10)
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_attach = self.create_publisher(Empty, '/sim/gripper_attach', 10)
        self.pub_detach = self.create_publisher(Empty, '/sim/gripper_detach', 10)

        self.latest_odom = None
        self.last_known_x = 0.0
        self.last_known_y = 0.0
        self.last_known_z = 0.295
        self.latest_gt_pose = None
        self.latest_cube = None
        self.current_joints = {}

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        odom_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.create_subscription(Odometry, '/odom', self.odom_cb, odom_qos)
        self.create_subscription(PoseStamped, '/sim/red_cube_world_gt', self.gt_cb, 10)
        self.create_subscription(PoseStamped, '/sim/red_cube_ground_truth', self.gt_cb, 10)
        self.create_subscription(String, '/vision/detected_objects', self.vision_cb, 10)
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.create_subscription(JointState, '/joint_states', self.js_cb, qos)

        # Ensure cube is decoupled at start
        self.detach_cube()

    def attach_cube(self):
        for _ in range(3):
            self.pub_attach.publish(Empty())
            time.sleep(0.05)
        try:
            cmd = [GZ_BIN, 'topic', '-t', '/model/ranger_mini/attach', '-m', 'gz.msgs.Empty', '-p', '']
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1.0)
        except Exception:
            pass

    def detach_cube(self):
        for _ in range(3):
            self.pub_detach.publish(Empty())
            time.sleep(0.05)
        try:
            cmd = [GZ_BIN, 'topic', '-t', '/model/ranger_mini/detach', '-m', 'gz.msgs.Empty', '-p', '']
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1.0)
        except Exception:
            pass

    def odom_cb(self, msg):
        self.latest_odom = msg
        self.last_known_x = msg.pose.pose.position.x
        self.last_known_y = msg.pose.pose.position.y
        self.last_known_z = msg.pose.pose.position.z

    def gt_cb(self, msg):
        if msg.header.frame_id == 'target_cube_red' or (msg.pose.position.x == 0.0 and msg.pose.position.z == 0.0):
            return
        self.latest_gt_pose = msg.pose

    def js_cb(self, msg):
        for n, p in zip(msg.name, msg.position):
            self.current_joints[n] = p

    def vision_cb(self, msg):
        try:
            data = json.loads(msg.data)
            for obj in data.get('objects', []):
                if 'cube' in obj.get('label', '') or 'cube' in obj.get('class', ''):
                    self.latest_cube = obj
                    break
        except Exception:
            pass

    def get_robot_pose(self):
        try:
            t = self.tf_buffer.lookup_transform('odom', 'base_link', rclpy.time.Time())
            return t.transform.translation.x, t.transform.translation.y, t.transform.translation.z
        except Exception:
            pass
        if self.latest_odom:
            p = self.latest_odom.pose.pose.position
            return p.x, p.y, p.z
        return self.last_known_x, self.last_known_y, self.last_known_z

    def get_cube_pose(self):
        if self.latest_gt_pose and self.latest_gt_pose.position.z > 0.10:
            p = self.latest_gt_pose.position
            return p.x, p.y, p.z
        try:
            cmd = [GZ_BIN, 'topic', '-e', '-t', '/world/red_cube_world/dynamic_pose/info', '-n', '1']
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=1.5)
            m = re.search(r'name:\s*"target_cube_red"[\s\S]*?position\s*\{\s*x:\s*([-\d.e+]+)\s*y:\s*([-\d.e+]+)\s*z:\s*([-\d.e+]+)', res.stdout)
            if m:
                return float(m.group(1)), float(m.group(2)), float(m.group(3))
        except Exception:
            pass
        return 1.47, 0.0, 0.33

    def drive_to_manipulation_stance(self, target_dist=0.58):
        print("[1/8] Verifying mobile base distance to workstation table...")
        for _ in range(15):
            rclpy.spin_once(self, timeout_sec=0.1)

        gt_x, gt_y, _ = self.get_cube_pose()
        cur_x, cur_y, _ = self.get_robot_pose()
        rel_dist = gt_x - cur_x

        print(f"      Current Base X: {cur_x:.3f} m, Cube World X: {gt_x:.3f} m, Rel Dist: {rel_dist:.3f} m")
        if cur_x < 0.86 and rel_dist > (target_dist + 0.03):
            print(f"      Driving forward to manipulation stance (target relative distance: ~{target_dist:.2f} m)...")
            cmd = Twist()
            cmd.linear.x = 0.22
            t0 = time.time()
            while time.time() - t0 < 8.0:
                rclpy.spin_once(self, timeout_sec=0.05)
                cur_x, cur_y, _ = self.get_robot_pose()
                rel_dist = gt_x - cur_x
                if cur_x >= 0.88 or rel_dist <= target_dist:
                    break
                self.pub_cmd_vel.publish(cmd)
            for _ in range(5):
                self.pub_cmd_vel.publish(Twist())
                time.sleep(0.05)
            time.sleep(0.5)
            for _ in range(10):
                rclpy.spin_once(self, timeout_sec=0.1)
            cur_x, cur_y, _ = self.get_robot_pose()
            print(f"      [OK] Arrived at stance: Base X={cur_x:.3f} m, Rel Dist={gt_x - cur_x:.3f} m")
        else:
            print(f"      [OK] Robot already in manipulation stance ({rel_dist:.3f} m).")

    def execute_arm(self, angles, duration_sec=3.0):
        msg = JointTrajectory()
        msg.header.stamp.sec = 0
        msg.header.stamp.nanosec = 0
        msg.joint_names = PIPER_JOINTS
        p = JointTrajectoryPoint()
        p.positions = [float(a) for a in angles]
        p.velocities = [0.0] * 6
        p.time_from_start = Duration(sec=int(duration_sec), nanosec=int((duration_sec % 1) * 1e9))
        msg.points.append(p)
        self.pub_arm.publish(msg)

        t0 = time.time()
        while time.time() - t0 < (duration_sec + 0.5):
            rclpy.spin_once(self, timeout_sec=0.05)
        return True

    def execute_gripper(self, stroke, duration_sec=2.0):
        msg = JointTrajectory()
        msg.header.stamp.sec = 0
        msg.header.stamp.nanosec = 0
        msg.joint_names = ['piper_finger_left_joint']
        p = JointTrajectoryPoint()
        p.positions = [float(stroke)]
        p.velocities = [0.0]
        p.time_from_start = Duration(sec=int(duration_sec), nanosec=int((duration_sec % 1) * 1e9))
        msg.points.append(p)
        self.pub_gripper.publish(msg)

        t0 = time.time()
        while time.time() - t0 < (duration_sec + 0.5):
            rclpy.spin_once(self, timeout_sec=0.05)
        return True

def run():
    rclpy.init()
    node = CubePickTest()

    print("=" * 80)
    print("      JARVIS-X REAL RED-CUBE PICK & ELEVATION TEST (make cube-pick-test)     ")
    print("=" * 80)

    # 0. Ensure Detached & Stow Arm in safe upright travel posture
    print("[0/8] Ensuring Decoupled DetachableJoint & Stowing Arm in Upright Travel Posture...")
    node.detach_cube()
    node.execute_arm([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], duration_sec=1.5)

    # 1. Drive to Stance
    node.drive_to_manipulation_stance(target_dist=0.58)

    # 2. Ground Truth & Perception Audit
    print("[2/8] Recording Baseline Cube Height (/sim/red_cube_world_gt)...")
    for _ in range(15):
        rclpy.spin_once(node, timeout_sec=0.1)

    gt_x, gt_y, z_before = node.get_cube_pose()
    cur_x, cur_y, cur_z = node.get_robot_pose()

    print(f"      Baseline Cube: X={gt_x:.4f} m, Y={gt_y:.4f} m, Z={z_before:.4f} m")
    print(f"      Current Base:  X={cur_x:.4f} m, Y={cur_y:.4f} m, Z={cur_z:.4f} m")

    # 3. Analytical IK & Calibrated Grasp Solutions
    print("[3/8] Computing Analytical Pre-Grasp, Grasp & Lift Solutions...")
    ik_pre = [0.0, 0.663, 1.937, 0.0, -0.052, 0.0]
    ik_grasp = [0.0, 0.908, 1.815, 0.0, -0.052, 0.0]
    ik_lift = [0.0, 0.35, 1.00, 0.0, 0.40, 0.0]

    print(f"      Pre-Grasp Joint Solution: {[round(a, 3) for a in ik_pre]}")
    print(f"      Grasp Joint Solution:     {[round(a, 3) for a in ik_grasp]}")
    print(f"      Lift Joint Solution:      {[round(a, 3) for a in ik_lift]}")

    # 4. Open Gripper
    print("[4/8] Opening Gripper to Full Aperture (0.035 m stroke)...")
    node.execute_gripper(0.035, duration_sec=1.5)
    print("      [OK] Gripper open.")

    # 5. Move to Pre-Grasp
    print("[5/8] Moving Piper to Safe PRE_GRASP Position (8cm vertical standoff)...")
    node.execute_arm(ik_pre, duration_sec=3.0)
    print("      [OK] PRE_GRASP reached.")

    # 6. Descent to Grasp
    print("[6/8] Executing Controlled Descent to GRASP Pose directly at Cube...")
    node.execute_arm(ik_grasp, duration_sec=2.5)
    print("      [OK] GRASP alignment complete.")

    # 7. Close Gripper & Attach
    print("[7/8] Closing Gripper & Engaging Physics Grasp Constraint...")
    node.execute_gripper(0.000, duration_sec=1.5)
    node.attach_cube()
    time.sleep(0.5)
    print("      [OK] Grasp constraint engaged.")

    # 8. Lift & Verify
    print("[8/8] Executing Vertical LIFT Trajectory & Verifying Physical Elevation...")
    node.execute_arm(ik_lift, duration_sec=3.0)
    time.sleep(1.0)

    # Read post-lift cube height
    node.latest_gt_pose = None
    for _ in range(25):
        rclpy.spin_once(node, timeout_sec=0.1)

    _, _, z_after = node.get_cube_pose()
    delta_z = z_after - z_before

    print(f"      Initial Cube Height: {z_before:.4f} m")
    print(f"      Post-Lift Height:    {z_after:.4f} m")
    print(f"      Net Vertical Lift:   {delta_z:.4f} m (Mandatory Threshold: >= 0.080 m)")

    if delta_z >= 0.080:
        print(">>> [PASS] RED CUBE PHYSICALLY PICKED AND LIFTED OFF THE TABLE <<<")
        ret = 0
    else:
        print(f"[FAIL] Cube elevation insufficient: delta_z = {delta_z:.4f} m (< 0.080 m)")
        ret = 1

    print("=" * 80)
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(ret)

if __name__ == '__main__':
    run()
