#!/bin/bash
set -e

echo "Installing ROS 2 Humble Environment (Native)......"

sudo apt-get update
sudo apt-get install -y ros-humble-desktop ros-humble-ros-gz ros-humble-ros2-control ros-humble-gz-ros2-control ros-humble-nav2-bringup ros-humble-moveit

echo "Humble native installation complete."
