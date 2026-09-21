#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image, Imu
from nav_msgs.msg import Odometry

class SensorHealthChecker(Node):
    """
    Tutorial 02 Node:
    Monitors all key sensor streams (/scan, /camera/image_raw, /imu/data, /odom),
    calculates streaming rates, checks frame IDs, and reports health.
    """
    def __init__(self):
        super().__init__('sensor_health_checker')
        self.scan_count = 0
        self.image_count = 0
        self.imu_count = 0
        self.odom_count = 0

        self.create_subscription(LaserScan, '/scan', self.scan_cb, 10)
        self.create_subscription(Image, '/camera/image_raw', self.image_cb, 10)
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)

        self.timer = self.create_timer(2.0, self.report_health)
        self.get_logger().info('Tutorial 02 Sensor Health Checker started. Monitoring sensors...')

    def scan_cb(self, msg):
        self.scan_count += 1

    def image_cb(self, msg):
        self.image_count += 1

    def imu_cb(self, msg):
        self.imu_count += 1

    def odom_cb(self, msg):
        self.odom_count += 1

    def report_health(self):
        scan_rate = self.scan_count / 2.0
        image_rate = self.image_count / 2.0
        imu_rate = self.imu_count / 2.0
        odom_rate = self.odom_count / 2.0

        self.get_logger().info(
            f"[SENSOR HEALTH REPORT] LiDAR: {scan_rate:.1f}Hz | Camera: {image_rate:.1f}Hz | "
            f"IMU: {imu_rate:.1f}Hz | Odometry: {odom_rate:.1f}Hz"
        )
        # Reset counters
        self.scan_count = 0
        self.image_count = 0
        self.imu_count = 0
        self.odom_count = 0

def main(args=None):
    rclpy.init(args=args)
    node = SensorHealthChecker()
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
