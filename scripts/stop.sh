#!/usr/bin/env bash
echo "Stopping all Gazebo and ROS 2 simulation processes..."
killall -9 gz-sim-main gz-sim-gui-client gz ruby rviz2 2>/dev/null || true
pkill -9 -f "ros2" 2>/dev/null || true
pkill -9 -f "gz" 2>/dev/null || true
pkill -9 -f "yolo_detector" 2>/dev/null || true
pkill -9 -f "parameter_bridge" 2>/dev/null || true
pkill -9 -f "robot_state_publisher" 2>/dev/null || true
pkill -9 -f "teleop" 2>/dev/null || true
echo "[OK] All background simulation processes stopped cleanly."
