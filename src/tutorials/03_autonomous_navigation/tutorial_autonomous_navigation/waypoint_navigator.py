#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose

class WaypointNavigator(Node):
    """
    Tutorial 03 Node:
    Sends a sequence of predefined inspection waypoints to the Nav2 action server.
    """
    def __init__(self):
        super().__init__('waypoint_navigator')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Defined warehouse inspection route: (x, y, yaw)
        self.waypoints = [
            (2.0, 0.0, 0.0),
            (4.0, 2.0, 1.57),
            (2.0, 4.0, 3.14),
            (0.0, 0.0, 0.0)
        ]
        self.current_idx = 0
        self.timer = self.create_timer(1.0, self.start_mission)
        self.get_logger().info('Tutorial 03 Waypoint Navigator initialized')

    def start_mission(self):
        self.timer.cancel()
        self.get_logger().info('Connecting to Nav2 NavigateToPose action server...')
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().warn('Nav2 action server not yet available. Retrying in background.')
            return
        self.send_next_waypoint()

    def send_next_waypoint(self):
        if self.current_idx >= len(self.waypoints):
            self.get_logger().info('Mission Complete! All waypoints successfully navigated.')
            return

        x, y, yaw = self.waypoints[self.current_idx]
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.orientation.w = 1.0  # Simplified orientation
        
        self.get_logger().info(f'Dispatching Waypoint {self.current_idx+1}/{len(self.waypoints)} -> ({x:.1f}, {y:.1f})')
        send_future = self._action_client.send_goal_async(goal_msg)
        send_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Waypoint rejected by Nav2 server.')
            return
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        self.get_logger().info(f'Waypoint {self.current_idx+1} reached!')
        self.current_idx += 1
        self.send_next_waypoint()

def main(args=None):
    rclpy.init(args=args)
    node = WaypointNavigator()
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
