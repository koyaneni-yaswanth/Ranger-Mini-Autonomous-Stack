#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time

class PickAndPlaceTutorial(Node):
    """
    Tutorial 04 Node:
    Executes a structured pick-and-place sequence using ros2_control JointTrajectory controller.
    """
    def __init__(self):
        super().__init__('pick_and_place_tutorial')
        self.arm_pub = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )
        self.gripper_pub = self.create_publisher(
            JointTrajectory,
            '/gripper_controller/joint_trajectory',
            10
        )
        self.arm_joints = [
            'joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6'
        ]
        self.gripper_joints = ['gripper_finger_joint1']
        
        self.timer = self.create_timer(1.0, self.run_sequence)
        self.step = 0
        self.get_logger().info('Tutorial 04 Pick and Place Tutorial Initialized')

    def send_arm_pose(self, positions, duration_sec):
        traj = JointTrajectory()
        traj.joint_names = self.arm_joints
        point = JointTrajectoryPoint()
        point.positions = [float(p) for p in positions]
        point.time_from_start = Duration(sec=duration_sec, nanosec=0)
        traj.points.append(point)
        self.arm_pub.publish(traj)

    def send_gripper(self, position, duration_sec=1):
        traj = JointTrajectory()
        traj.joint_names = self.gripper_joints
        point = JointTrajectoryPoint()
        point.positions = [float(position)]
        point.time_from_start = Duration(sec=duration_sec, nanosec=0)
        traj.points.append(point)
        self.gripper_pub.publish(traj)

    def run_sequence(self):
        if self.step == 0:
            self.get_logger().info('[Step 1/6] Moving arm to HOME position...')
            self.send_arm_pose([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 3)
            self.step += 1
        elif self.step == 1:
            self.get_logger().info('[Step 2/6] Opening gripper...')
            self.send_gripper(0.04) # 40mm opening
            self.step += 1
        elif self.step == 2:
            self.get_logger().info('[Step 3/6] Moving to PRE-GRASP pose above object...')
            self.send_arm_pose([0.0, 0.45, 0.60, 0.0, 0.52, 0.0], 3)
            self.step += 1
        elif self.step == 3:
            self.get_logger().info('[Step 4/6] Lowering to GRASP and closing gripper...')
            self.send_arm_pose([0.0, 0.65, 0.85, 0.0, 0.20, 0.0], 2)
            time.sleep(2.0)
            self.send_gripper(0.01) # grasp object
            self.step += 1
        elif self.step == 4:
            self.get_logger().info('[Step 5/6] LIFTING object and rotating to PLACE bin...')
            self.send_arm_pose([1.57, 0.35, 0.50, 0.0, 0.50, 0.0], 4)
            self.step += 1
        elif self.step == 5:
            self.get_logger().info('[Step 6/6] Releasing object into bin and returning to HOME...')
            self.send_gripper(0.04)
            time.sleep(1.0)
            self.send_arm_pose([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 3)
            self.get_logger().info('Pick and Place Sequence Completed Successfully!')
            self.timer.cancel()

def main(args=None):
    rclpy.init(args=args)
    node = PickAndPlaceTutorial()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
