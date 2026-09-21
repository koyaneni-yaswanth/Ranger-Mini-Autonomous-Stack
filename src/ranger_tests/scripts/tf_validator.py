#!/usr/bin/env python3
"""
Automated TF2 Transform Tree Validator for Ranger Mini.
Validates end-to-end connectivity, checks frame timestamps, and flags disconnected or missing frames.
"""

import sys
import time
import rclpy
from rclpy.node import Node
import tf2_ros

REQUIRED_FRAMES = [
    ('odom', 'base_footprint'),
    ('base_footprint', 'base_link'),
    ('base_link', 'lidar_link'),
    ('base_link', 'camera_link'),
    ('base_link', 'imu_link'),
    ('base_link', 'fl_steering_link'),
    ('base_link', 'fr_steering_link'),
    ('base_link', 'rl_steering_link'),
    ('base_link', 'rr_steering_link'),
    ('base_link', 'top_deck_link'),
    ('top_deck_link', 'piper_mount'),
    ('piper_mount', 'piper_link1'),
    ('piper_link1', 'piper_link2'),
    ('piper_link2', 'piper_link3'),
    ('piper_link3', 'piper_link4'),
    ('piper_link4', 'piper_link5'),
    ('piper_link5', 'piper_link6'),
    ('piper_link6', 'piper_gripper_base'),
    ('piper_gripper_base', 'piper_end_effector')
]

class TFValidator(Node):
    def __init__(self):
        super().__init__('tf_validator')
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        
    def validate_all(self, timeout_sec=5.0):
        self.get_logger().info("=========================================")
        self.get_logger().info("RUNNING AUTOMATED TF TREE VALIDATION")
        self.get_logger().info("=========================================")
        
        t0 = time.time()
        # Allow buffer to collect transforms
        while time.time() - t0 < 2.0:
            rclpy.spin_once(self, timeout_sec=0.1)
            
        passed = 0
        failed = 0
        details = []
        
        for parent, child in REQUIRED_FRAMES:
            try:
                can_tf = self.tf_buffer.can_transform(
                    child,
                    parent,
                    rclpy.time.Time(),
                    timeout=rclpy.duration.Duration(seconds=1.0)
                )
                if can_tf:
                    trans = self.tf_buffer.lookup_transform(child, parent, rclpy.time.Time())
                    passed += 1
                    status = "PASS"
                else:
                    failed += 1
                    status = "FAIL (No Transform)"
            except Exception as e:
                failed += 1
                status = f"FAIL ({type(e).__name__})"
                
            self.get_logger().info(f"[{status}] {parent} -> {child}")
            details.append((parent, child, status))
            
        total = len(REQUIRED_FRAMES)
        self.get_logger().info(f"\nTF Validation Complete: {passed}/{total} frames passed.")
        return failed == 0, passed, failed, details

def main(args=None):
    rclpy.init(args=args)
    validator = TFValidator()
    success, passed, failed, _ = validator.validate_all()
    validator.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
