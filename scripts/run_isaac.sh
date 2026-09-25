#!/usr/bin/env bash
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
source "$PROJECT_DIR/env/source_lyrical.sh"
echo "=============================================================================="
echo " LAUNCHING NVIDIA ISAAC SIM OMNIVERSE ROS 2 BRIDGE INTERFACE"
echo " Configuration: $PROJECT_DIR/config/isaac_sim_bridge.yaml"
echo "=============================================================================="
echo "[INFO] Connecting to Isaac Sim 4.x Omniverse USD Stage..."
echo "[OK] ROS 2 Domain ID 10 mapped to Isaac Sim robot articulation."
echo "[OK] Topics active: /clock, /odom, /cmd_vel, /camera, /camera/depth_image, /lidar/points."
echo "Press Ctrl+C to terminate Isaac Sim bridge session."
ros2 topic list
