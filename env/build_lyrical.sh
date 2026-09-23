#!/usr/bin/env bash
set -e
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh"

if [ "$ROS_DISTRO" != "lyrical" ]; then
    echo "[ERROR] Expected ROS_DISTRO=lyrical, but detected $ROS_DISTRO! Aborting."
    exit 1
fi

WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"
cd "$WS_DIR"
echo "[INFO] Compiling Lyrical Workspace at $WS_DIR..."
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source "$WS_DIR/install/setup.bash"
echo "[PASS] Lyrical Workspace build succeeded."
