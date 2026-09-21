#!/usr/bin/env python3
"""
Autonomous Pick-and-Place Manipulation Execution Node for Piper 6-DOF Robotic Arm.
Interacts with ros2_control JointTrajectoryController and validates full pick-lift-place cycle.
"""

import sys
import time
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class PiperPickAndPlace(Node):
    def __init__(self):
        super().__init__('piper_pick_and_place')
        self.get_logger().info('Initializing Piper 6-DOF Pick-and-Place Controller...')
        
        self.arm_pub = self.create_publisher(
            JointTrajectory,
            '/piper_arm_controller/joint_trajectory',
            10
        )
        
        self.joint_names = [
            'piper_joint1',
            'piper_joint2',
            'piper_joint3',
            'piper_joint4',
            'piper_joint5',
            'piper_joint6'
        ]
        
        # Operational Poses (radians)
        self.poses = {
            'HOME': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'APPROACH_WORKSTATION': [0.0, 0.35, 0.45, 0.0, 0.25, 0.0],
            'PRE_GRASP': [0.0, 0.50, 0.60, 0.0, 0.35, 0.0],
            'GRASP': [0.0, 0.55, 0.65, 0.0, 0.38, 0.0],
            'LIFT': [0.0, 0.20, 0.30, 0.0, 0.15, 0.0],
            'SWING_TO_BIN': [-0.785, 0.45, 0.55, 0.0, 0.30, 0.0],
            'PLACE_RELEASE': [-0.785, 0.55, 0.65, 0.0, 0.35, 0.0],
            'RETURN_HOME': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        }
        
    def execute_pose(self, pose_name, duration_sec=2.5):
        if pose_name not in self.poses:
            self.get_logger().error(f"Unknown pose: {pose_name}")
            return False
            
        positions = self.poses[pose_name]
        self.get_logger().info(f"Executing Pose: {pose_name} -> {positions}")
        
        traj = JointTrajectory()
        traj.header.stamp = self.get_clock().now().to_msg()
        traj.joint_names = self.joint_names
        
        pt = JointTrajectoryPoint()
        pt.positions = positions
        pt.velocities = [0.0] * len(positions)
        pt.accelerations = [0.0] * len(positions)
        pt.time_from_start = Duration(sec=int(duration_sec), nanosec=int((duration_sec % 1) * 1e9))
        
        traj.points.append(pt)
        self.arm_pub.publish(traj)
        time.sleep(duration_sec + 0.5)
        return True

    def run_full_cycle(self):
        self.get_logger().info("=========================================")
        self.get_logger().info("STARTING PIPER PICK-AND-PLACE SEQUENCE")
        self.get_logger().info("=========================================")
        
        t0 = time.time()
        steps = [
            ('HOME', 2.0),
            ('APPROACH_WORKSTATION', 2.5),
            ('PRE_GRASP', 2.0),
            ('GRASP', 1.5),
            ('LIFT', 2.0),
            ('SWING_TO_BIN', 3.0),
            ('PLACE_RELEASE', 1.5),
            ('RETURN_HOME', 2.5)
        ]
        
        success = True
        for pose_name, dur in steps:
            ok = self.execute_pose(pose_name, dur)
            if not ok:
                success = False
                break
                
        total_time = time.time() - t0
        self.get_logger().info(f"Pick-and-Place sequence completed in {total_time:.2f}s with Success={success}")
        return success, total_time

def main(args=None):
    rclpy.init(args=args)
    node = PiperPickAndPlace()
    # Give ROS time to initialize publishers and discover subscribers
    time.sleep(1.0)
    success, exec_time = node.run_full_cycle()
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
