#!/usr/bin/env bash
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh"

USE_SIM_TIME="${USE_SIM_TIME:-true}"

echo "=============================================================================="
echo " LAUNCHING RVIZ2 WITH AUTONOMY PRESETS (MAP, ODOM, LIDAR, ROBOT)"
echo " (use_sim_time: $USE_SIM_TIME)"
echo "=============================================================================="
exec rviz2 -d "$PROJECT_DIR/config/slam.rviz" --ros-args -p use_sim_time:="$USE_SIM_TIME" "$@"
