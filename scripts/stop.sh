#!/usr/bin/env bash
echo "Stopping all Gazebo and ROS 2 simulation processes..."
killall -9 gz-sim-main gz-sim-gui-client gz ruby rviz2 2>/dev/null || true
pkill -9 -f "ros2" 2>/dev/null || true
pkill -9 -f "gz" 2>/dev/null || true
pkill -9 -f "yolo_detector" 2>/dev/null || true
pkill -9 -f "parameter_bridge" 2>/dev/null || true
pkill -9 -f "robot_state_publisher" 2>/dev/null || true
pkill -9 -f "teleop" 2>/dev/null || true
pkill -9 -f "manipulator_manager_node" 2>/dev/null || true
pkill -9 -f "ranger_control" 2>/dev/null || true
pkill -9 -f "ranger_missions" 2>/dev/null || true
pkill -9 -f "ranger_navigation" 2>/dev/null || true
pkill -9 -f "spawner" 2>/dev/null || true
pkill -9 -f "controller_manager" 2>/dev/null || true
pkill -9 -f "move_group" 2>/dev/null || true
pkill -9 -f "nav2" 2>/dev/null || true
pkill -9 -f "slam_toolbox" 2>/dev/null || true
pkill -9 -f "sensor_fusion" 2>/dev/null || true
pkill -9 -f "opennav" 2>/dev/null || true
pkill -9 -f "pointcloud_to_laserscan" 2>/dev/null || true
ros2 daemon stop 2>/dev/null || true
echo "[OK] All background simulation processes stopped cleanly."
