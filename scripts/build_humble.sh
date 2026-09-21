#!/bin/bash
set -e

cd "$HOME/ranger_mini_humble_ws"
source /opt/ros/humble/setup.bash
colcon build --symlink-install --event-handlers console_direct+
