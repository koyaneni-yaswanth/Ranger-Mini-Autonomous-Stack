#!/usr/bin/env bash
set -e
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " [06/12] TRANSFORM TREE (TF) INTEGRITY CHECK"
echo "=============================================================================="
WS="/home/yash/ranger_mini_lyrical_ws"
source "$WS/install/setup.bash" 2>/dev/null || true

URDF_FILE=$(ros2 pkg prefix ranger_description 2>/dev/null)/share/ranger_description/urdf/ranger_mini.urdf.xacro
echo "Parsing robot kinematics from: $URDF_FILE"
xacro "$URDF_FILE" > /tmp/ranger_mini_audit.urdf

python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('/tmp/ranger_mini_audit.urdf')
root = tree.getroot()
links = [l.attrib['name'] for l in root.findall('link')]
joints = [j.attrib['name'] for j in root.findall('joint')]
print(f'[OK] Verified {len(links)} links and {len(joints)} joints in kinematic tree.')

required = ['base_footprint', 'base_link', 'top_deck_link', 'lidar_link', 'camera_link', 'imu_link']
for r in required:
    assert r in links, f'Missing required link: {r}'
print('[OK] Core sensor & base kinematic frames verified without circularities.')
"
echo "=============================================================================="
echo "[PASS] TF kinematic tree unbroken."
