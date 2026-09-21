#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class TeleopSupervisor(Node):
    """
    Tutorial 01 Node:
    Monitors teleoperation cmd_vel, validates velocity bounds,
    and publishes diagnostic kinematics status.
    """
    def __init__(self):
        super().__init__('teleop_supervisor')
        self.cmd_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_callback, 10
        )
        self.clamped_pub = self.create_publisher(
            Twist, '/ranger/cmd_vel_safe', 10
        )
        self.status_pub = self.create_publisher(
            String, '/ranger/kinematics_status', 10
        )
        
        # Velocity constraints for Ranger Mini
        self.max_linear_x = 1.5   # m/s
        self.max_linear_y = 1.0   # m/s (crab drive)
        self.max_angular_z = 1.2  # rad/s
        
        self.get_logger().info('Tutorial 01 Teleop Supervisor Initialized')
        self.get_logger().info(f'Max Limits: vx={self.max_linear_x}m/s, vy={self.max_linear_y}m/s, wz={self.max_angular_z}rad/s')

    def cmd_callback(self, msg: Twist):
        safe_msg = Twist()
        # Clamp linear velocities
        safe_msg.linear.x = max(min(msg.linear.x, self.max_linear_x), -self.max_linear_x)
        safe_msg.linear.y = max(min(msg.linear.y, self.max_linear_y), -self.max_linear_y)
        safe_msg.angular.z = max(min(msg.angular.z, self.max_angular_z), -self.max_angular_z)
        
        # Determine active kinematics mode
        if abs(safe_msg.linear.y) > 0.05 and abs(safe_msg.linear.x) > 0.05:
            mode = "OMNIDIRECTIONAL_DIAGONAL"
        elif abs(safe_msg.linear.y) > 0.05:
            mode = "CRAB_DRIVE_LATERAL"
        elif abs(safe_msg.angular.z) > 0.05 and abs(safe_msg.linear.x) < 0.05:
            mode = "IN_PLACE_SPIN"
        elif abs(safe_msg.linear.x) > 0.05:
            mode = "ACKERMANN_FORWARD"
        else:
            mode = "STANDSTILL"

        self.clamped_pub.publish(safe_msg)
        status_msg = String()
        status_msg.data = f"Mode: {mode} | vx={safe_msg.linear.x:.2f} vy={safe_msg.linear.y:.2f} wz={safe_msg.angular.z:.2f}"
        self.status_pub.publish(status_msg)

def main(args=None):
    rclpy.init(args=args)
    node = TeleopSupervisor()
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
