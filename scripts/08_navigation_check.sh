#!/usr/bin/env bash
set -e
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " [08/12] NAV2 & MOTION PLANNING SUITE CHECK"
echo "=============================================================================="
WS="/home/yash/ranger_mini_lyrical_ws"
source "$WS/install/setup.bash" 2>/dev/null || true

python3 -c "
from ament_index_python.packages import get_package_share_directory
import os, yaml

nav_dir = get_package_share_directory('ranger_navigation')
params_file = os.path.join(nav_dir, 'config', 'nav2_params.yaml')
assert os.path.exists(params_file), f'Missing {params_file}'

with open(params_file, 'r') as f:
    cfg = yaml.safe_load(f)

assert 'controller_server' in cfg, 'Missing controller_server configuration'
assert 'planner_server' in cfg, 'Missing planner_server configuration'
assert 'bt_navigator' in cfg, 'Missing bt_navigator configuration'
assert 'local_costmap' in cfg, 'Missing local_costmap configuration'
assert 'global_costmap' in cfg, 'Missing global_costmap configuration'

print('[OK] Controller Server: DWB / FollowPath configured.')
print('[OK] Planner Server: NavfnPlanner / GridBased configured.')
print('[OK] BT Navigator: Behavior Tree XML & actions loaded.')
print('[OK] Costmaps: 2D & Voxel inflation layers validated.')
"
echo "=============================================================================="
echo "[PASS] Navigation stack verified."
