#!/bin/bash
set -e

cd "$HOME/ranger_mini_lyrical_ws"
if [ -f "/opt/ros/lyrical/setup.bash" ]; then
    source /opt/ros/lyrical/setup.bash
elif [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi
colcon build --symlink-install --event-handlers console_direct+
