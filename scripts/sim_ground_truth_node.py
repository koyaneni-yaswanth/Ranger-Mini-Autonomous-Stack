#!/usr/bin/env python3
"""
JARVIS-X Simulation Ground Truth Publisher Node.
Continuously queries Gazebo Harmonic for model ground-truth poses and publishes
geometry_msgs/msg/PoseStamped on /sim/red_cube_ground_truth.
Strictly isolated to simulation validation and benchmark error measurement.
"""

import sys
import re
import subprocess
import time
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import PoseStamped

class SimGroundTruthNode(Node):
    def __init__(self):
        super().__init__(
            'sim_ground_truth_node',
            parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)]
        )
        self.pub_world_gt = self.create_publisher(PoseStamped, '/sim/red_cube_world_gt', 10)
        self.pub_cube_gt = self.create_publisher(PoseStamped, '/sim/red_cube_ground_truth', 10)
        self.timer = self.create_timer(0.15, self.publish_ground_truth) # ~6.7 Hz
        self.get_logger().info('Simulation Ground Truth Publisher active on /sim/red_cube_world_gt and /sim/red_cube_ground_truth')

    def publish_ground_truth(self):
        try:
            cmd = ['gz', 'topic', '-e', '-t', '/world/red_cube_world/dynamic_pose/info', '-n', '1']
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=1.0)
            if res.returncode != 0 or not res.stdout:
                return

            m = re.search(r'name:\s*"target_cube_red"[\s\S]*?position\s*\{\s*x:\s*([-\d.e+]+)\s*y:\s*([-\d.e+]+)\s*z:\s*([-\d.e+]+)', res.stdout)
            if m:
                x, y, z = float(m.group(1)), float(m.group(2)), float(m.group(3))
                msg = PoseStamped()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.header.frame_id = 'red_cube_world'
                msg.pose.position.x = x
                msg.pose.position.y = y
                msg.pose.position.z = z
                msg.pose.orientation.w = 1.0
                self.pub_world_gt.publish(msg)
                self.pub_cube_gt.publish(msg)
        except Exception:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = SimGroundTruthNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
