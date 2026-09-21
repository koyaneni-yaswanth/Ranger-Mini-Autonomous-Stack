#!/usr/bin/env python3
import math
import numpy as np

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray

class RangerMiniKinematicsNode(Node):
    def __init__(self):
        super().__init__('ranger_kinematics_node')
        
        # Robot Parameters
        self.wheelbase = 0.50
        self.track = 0.47
        self.wheel_radius = 0.09
        
        # Wheel positions relative to geometric center: [X, Y]
        # Order: FL, FR, RL, RR (Must match controller.yaml order)
        self.wheels = [
            ('FL', np.array([ self.wheelbase / 2.0,  self.track / 2.0])),
            ('FR', np.array([ self.wheelbase / 2.0, -self.track / 2.0])),
            ('RL', np.array([-self.wheelbase / 2.0,  self.track / 2.0])),
            ('RR', np.array([-self.wheelbase / 2.0, -self.track / 2.0]))
        ]

        # Subscribers
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        # Publishers
        self.steer_pub = self.create_publisher(Float64MultiArray, '/steering_controller/commands', 10)
        self.drive_pub = self.create_publisher(Float64MultiArray, '/traction_controller/commands', 10)
        
        self.get_logger().info("Ranger Mini 4WIS Kinematics Node Started")

    def cmd_vel_callback(self, msg: Twist):
        vx = msg.linear.x
        vy = msg.linear.y
        omega = msg.angular.z
        
        steer_cmds = []
        drive_cmds = []
        
        for name, pos in self.wheels:
            px, py = pos
            
            # Kinematic equations for 4WIS
            vwx = vx - omega * py
            vwy = vy + omega * px
            
            # Steering angle (theta) and driving speed (m/s)
            theta = math.atan2(vwy, vwx)
            speed = math.sqrt(vwx**2 + vwy**2)
            
            # If the robot is perfectly still, hold the last steering angle (default to 0 here for simplicity)
            if abs(vx) < 0.001 and abs(vy) < 0.001 and abs(omega) < 0.001:
                theta = 0.0
                speed = 0.0
            
            # Convert driving speed (m/s) to wheel angular velocity (rad/s)
            wheel_omega = speed / self.wheel_radius
            
            # Normalize angle to [-pi, pi]
            theta = math.atan2(math.sin(theta), math.cos(theta))
            
            # OPTIMIZATION: If steering angle is > 90 deg, flip the wheel direction and reduce angle by 180 deg
            # This prevents the steering mechanism from unwinding unnecessarily
            if theta > math.pi / 2.0:
                theta -= math.pi
                wheel_omega = -wheel_omega
            elif theta < -math.pi / 2.0:
                theta += math.pi
                wheel_omega = -wheel_omega

            if name in ['FR', 'RR']:
                wheel_omega = -wheel_omega

            steer_cmds.append(float(theta))
            drive_cmds.append(float(wheel_omega))
            
        # Publish commands
        steer_msg = Float64MultiArray()
        steer_msg.data = steer_cmds
        self.steer_pub.publish(steer_msg)
        
        drive_msg = Float64MultiArray()
        drive_msg.data = drive_cmds
        self.drive_pub.publish(drive_msg)

def main(args=None):
    rclpy.init(args=args)
    node = RangerMiniKinematicsNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
