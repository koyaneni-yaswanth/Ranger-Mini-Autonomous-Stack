#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
import math

def create_pose(navigator: BasicNavigator, x: float, y: float, theta: float):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0
    
    # Convert theta to quaternion
    pose.pose.orientation.z = math.sin(theta / 2.0)
    pose.pose.orientation.w = math.cos(theta / 2.0)
    return pose

def main():
    rclpy.init()
    
    navigator = BasicNavigator()
    
    # Wait for Nav2 to be completely online (skip slam_toolbox as it's not a lifecycle node)
    navigator.waitUntilNav2Active(localizer='bt_navigator')
    
    # Define patrol waypoints (in meters)
    patrol_points = [
        create_pose(navigator, 2.0, 0.0, 0.0),
        create_pose(navigator, 2.0, 2.0, 1.57),
        create_pose(navigator, 0.0, 2.0, 3.14),
        create_pose(navigator, 0.0, 0.0, -1.57)
    ]
    
    print("Starting Patrol Mission...")
    
    # Loop the patrol 3 times
    for loop in range(3):
        print(f"--- Patrol Loop {loop + 1}/3 ---")
        for i, waypoint in enumerate(patrol_points):
            print(f"Navigating to Waypoint {i+1}...")
            navigator.goToPose(waypoint)
            
            # Wait until finished
            while not navigator.isTaskComplete():
                feedback = navigator.getFeedback()
                if feedback:
                    print(f"Distance to waypoint: {feedback.distance_remaining:.2f} meters", end='\r')
            
            result = navigator.getResult()
            if result == TaskResult.SUCCEEDED:
                print(f"\nReached Waypoint {i+1}!")
            elif result == TaskResult.CANCELED:
                print(f"\nWaypoint {i+1} was canceled.")
                return
            elif result == TaskResult.FAILED:
                print(f"\nFailed to reach Waypoint {i+1}!")
                return
                
    print("Patrol Mission Complete!")
    rclpy.shutdown()

if __name__ == '__main__':
    main()
