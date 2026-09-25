#!/usr/bin/env bash
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh"

echo "=============================================================================="
echo " LAUNCHING KEYBOARD TELEOPERATION (cmd_vel)"
echo " Use i/j/k/l keys to drive Ranger Mini"
echo "=============================================================================="
exec ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel "$@"
