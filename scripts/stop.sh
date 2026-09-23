#!/usr/bin/env bash
echo "Stopping any lingering Gazebo and ROS 2 simulation processes..."
killall -9 gz-sim-main gz ruby rviz2 2>/dev/null || true
pkill -9 -f "ros2 launch" 2>/dev/null || true
pkill -9 -f "controller_manager" 2>/dev/null || true
pkill -9 -f "async_slam_toolbox" 2>/dev/null || true
pkill -9 -f "nav2_" 2>/dev/null || true
pkill -9 -f "kinematics_node" 2>/dev/null || true
echo "[OK] All background simulation processes stopped cleanly."
