#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import math
import threading

# Simulated Vector Database / LLM Knowledge Base
# In a production system, an LLM would extract these coordinates dynamically 
# using a Visual Language Model (VLM) combined with the SLAM map.
LOCATION_MEMORY = {
    "center": (0.0, 0.0),
    "corner": (2.0, 2.0),
    "origin": (0.0, 0.0),
    "boxes": (1.5, -1.5),
    "dock": (-1.0, 0.0)
}

class AICommander(Node):
    def __init__(self):
        super().__init__('ai_commander')
        
        self.navigator = BasicNavigator()
        self.get_logger().info("Waiting for Nav2 to activate...")
        self.navigator.waitUntilNav2Active(localizer='bt_navigator')
        self.get_logger().info("AI Commander Online. Ready for Natural Language Commands!")

        # Subscribe to our AI voice command topic
        self.subscription = self.create_subscription(
            String,
            '/ai/command',
            self.command_callback,
            10
        )

    def create_pose(self, x, y):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0
        pose.pose.orientation.w = 1.0
        return pose

    def command_callback(self, msg):
        command = msg.data.lower()
        self.get_logger().info(f"\n[AI] Received command: '{command}'")
        
        # NLP Parsing Simulation
        target_name = None
        for loc in LOCATION_MEMORY.keys():
            if loc in command:
                target_name = loc
                break
                
        if target_name:
            x, y = LOCATION_MEMORY[target_name]
            self.get_logger().info(f"[AI] Extracted intent: Go to '{target_name}'. Coordinates: ({x}, {y})")
            self.get_logger().info(f"[AI] Dispatching Nav2 Goal...")
            
            goal_pose = self.create_pose(x, y)
            self.navigator.goToPose(goal_pose)
            
            # We launch a thread so we don't block the ROS callback
            threading.Thread(target=self.monitor_goal).start()
        else:
            self.get_logger().warning("[AI] I'm sorry, I don't know where that is in the warehouse.")

    def monitor_goal(self):
        while not self.navigator.isTaskComplete():
            pass
            
        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("[AI] Successfully arrived at destination.")
        elif result == TaskResult.CANCELED:
            self.get_logger().info("[AI] Command canceled.")
        elif result == TaskResult.FAILED:
            self.get_logger().error("[AI] Navigation failed.")

def main(args=None):
    rclpy.init(args=args)
    node = AICommander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
