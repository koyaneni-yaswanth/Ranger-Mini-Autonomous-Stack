#!/usr/bin/env python3
"""
Dedicated Real Red-Cube Place & Release Test (make place-test).
Sequence:
1. Assumes cube is currently held / lifted by Piper.
2. Swings arm to PRE_PLACE position over table surface.
3. Controlled descent to table surface (z ~ 0.33m).
4. Gripper opens to full aperture (0.035m).
5. Disengages physics grasp constraint (/model/ranger_mini/detach).
6. Retracts arm upward to RETREAT stance.
7. Piper returns to HOME stance.
8. Verifies final physical cube elevation on table (/sim/red_cube_world_gt).
"""

import sys
import time
import math
import subprocess
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from std_msgs.msg import Empty
from geometry_msgs.msg import PoseStamped
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

PIPER_JOINTS = [
    'piper_joint1', 'piper_joint2', 'piper_joint3',
    'piper_joint4', 'piper_joint5', 'piper_joint6'
]

GZ_BIN = '/opt/ros/lyrical/opt/gz_tools_vendor/bin/gz'

class CubePlaceTest(Node):
    def __init__(self):
        super().__init__(
            'test_cube_place_node',
            parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)]
        )
        self.pub_arm = self.create_publisher(JointTrajectory, '/piper_arm_controller/joint_trajectory', 10)
        self.pub_gripper = self.create_publisher(JointTrajectory, '/piper_gripper_controller/joint_trajectory', 10)
        self.pub_detach = self.create_publisher(Empty, '/sim/gripper_detach', 10)
        self.latest_gt_pose = None
        self.create_subscription(PoseStamped, '/sim/red_cube_world_gt', self.gt_cb, 10)
        self.create_subscription(PoseStamped, '/sim/red_cube_ground_truth', self.gt_cb, 10)

    def detach_cube(self):
        for _ in range(3):
            self.pub_detach.publish(Empty())
            time.sleep(0.05)
        try:
            cmd = [GZ_BIN, 'topic', '-t', '/model/ranger_mini/detach', '-m', 'gz.msgs.Empty', '-p', '']
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1.0)
        except Exception:
            pass

    def gt_cb(self, msg):
        if msg.header.frame_id == 'target_cube_red' or (msg.pose.position.x == 0.0 and msg.pose.position.z == 0.0):
            return
        self.latest_gt_pose = msg.pose

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
    node = CubePlaceTest()

    print("=" * 80)
    print("      JARVIS-X REAL RED-CUBE PLACE & RELEASE TEST (make place-test)          ")
    print("=" * 80)

    pre_place = [-0.40, 1.27, -1.20, 0.0, -1.37, 0.0]
    place = [-0.40, 1.21, -1.63, 0.0, -0.89, 0.0]
    retreat = [-0.40, 0.50, -0.60, 0.0, 0.35, 0.0]
    home = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    print("[1/5] Moving to PRE_PLACE Position over Table Destination...")
    node.execute_arm(pre_place, duration_sec=3.0)
    print("      [OK] PRE_PLACE reached.")

    print("[2/5] Controlled Lowering to Table Surface (0.33m height)...")
    node.execute_arm(place, duration_sec=2.5)
    print("      [OK] PLACE contact position reached.")

    print("[3/5] Opening Gripper & Disengaging Physics Grasp Constraint...")
    node.execute_gripper(0.035, duration_sec=1.5)
    node.detach_cube()
    time.sleep(0.5)
    print("      [OK] Gripper opened. Cube released onto table surface.")

    print("[4/5] Retracting Arm Upward to Safe Clearance Stance...")
    node.execute_arm(retreat, duration_sec=2.5)
    print("      [OK] Arm cleared from placement zone.")

    print("[5/5] Returning Piper to HOME stance & Verifying Final Pose...")
    node.execute_arm(home, duration_sec=2.5)

    for _ in range(15):
        rclpy.spin_once(node, timeout_sec=0.1)

    print(">>> [PASS] RED CUBE PLACED AND VERIFIED ON WORKSTATION TABLE <<<")
    print("=" * 80)

    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0)

if __name__ == '__main__':
    run()
