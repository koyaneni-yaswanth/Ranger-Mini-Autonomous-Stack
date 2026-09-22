#!/usr/bin/env bash
# ==============================================================================
# RANGER MINI AUTONOMOUS STACK: SIMULATION RUNTIME ENVIRONMENT
# ==============================================================================

export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
export IGN_GAZEBO_RENDER_ENGINE=ogre
export GZ_SIM_RENDER_ENGINE=ogre
export IGN_GAZEBO_SYSTEM_PLUGIN_PATH=/opt/ros/humble/lib
export GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/ros/humble/lib

# Resource paths
WS_DIR="${1:-/home/yash/ranger_mini_workbench}"
export IGN_GAZEBO_RESOURCE_PATH="$WS_DIR/src:$WS_DIR/src/ranger_simulation/worlds"
export GZ_SIM_RESOURCE_PATH="$WS_DIR/src:$WS_DIR/src/ranger_simulation/worlds"

echo "[INFO] Simulation Environment Configured:"
echo "  - Render Engine: OGRE (Mesa D3D12 NVIDIA Binding)"
echo "  - Resource Path: $IGN_GAZEBO_RESOURCE_PATH"
echo "  - Plugin Path:   $IGN_GAZEBO_SYSTEM_PLUGIN_PATH"
