#!/usr/bin/env bash
set -eo pipefail

echo "=============================================================================="
echo " [ROS CHECK] STRICT ROS 2 DISTRIBUTION & BINARY INTEGRITY AUDIT"
echo "=============================================================================="

PROJECT_DIR="/home/yash/ranger_mini_lyrical_2604_project"
if [ -f "$PROJECT_DIR/env/source_lyrical.sh" ]; then
    source "$PROJECT_DIR/env/source_lyrical.sh" 2>/dev/null || true
fi

echo "--- ENVIRONMENT VARIABLES ---"
echo "ROS_DISTRO:         $ROS_DISTRO"
echo "ROS_VERSION:        $ROS_VERSION"
echo "ROS_DOMAIN_ID:      $ROS_DOMAIN_ID"
echo "RMW_IMPLEMENTATION: $RMW_IMPLEMENTATION"
echo "AMENT_PREFIX_PATH:  $AMENT_PREFIX_PATH"

echo "--- EXECUTABLE RESOLUTION ---"
ROS2_PATH=$(command -v ros2 2>/dev/null || true)
if [ -z "$ROS2_PATH" ]; then
    echo "[FAIL] 'ros2' executable not found in PATH!"
    exit 1
fi

REAL_ROS2_PATH=$(readlink -f "$ROS2_PATH")
echo "which ros2:         $ROS2_PATH"
echo "readlink -f ros2:   $REAL_ROS2_PATH"

echo "--- INSTALLED BASE DISTRIBUTIONS (/opt/ros) ---"
ls -la /opt/ros/ 2>/dev/null || echo "No /opt/ros directory"

echo "--- INTEGRITY & CONTAMINATION VERIFICATION ---"

# Check 1: Does the binary path belong to Humble while claiming Lyrical?
if [[ "$REAL_ROS2_PATH" == *"/opt/ros/humble"* ]] && [ "$ROS_DISTRO" = "lyrical" ]; then
    echo "=============================================================================="
    echo "[FAIL] ROS environment contamination detected!"
    echo "       ROS_DISTRO is set to 'lyrical', but 'ros2' binary is: $REAL_ROS2_PATH"
    echo "       An environment variable alone is NOT proof of an active Lyrical installation."
    echo "=============================================================================="
    exit 1
fi

# Check 2: Does the binary path contain /opt/ros/lyrical?
if [[ "$REAL_ROS2_PATH" != *"/opt/ros/lyrical"* ]] && [[ "$REAL_ROS2_PATH" != *"/lyrical/"* ]]; then
    echo "=============================================================================="
    echo "[FAIL] 'ros2' executable does NOT resolve to a genuine ROS 2 Lyrical installation!"
    echo "       Resolved binary: $REAL_ROS2_PATH"
    echo "=============================================================================="
    exit 1
fi

# Check 3: Does /opt/ros/lyrical actually exist?
if [ ! -d "/opt/ros/lyrical" ]; then
    echo "=============================================================================="
    echo "[FAIL] Directory /opt/ros/lyrical does not exist."
    echo "=============================================================================="
    exit 1
fi

echo "=============================================================================="
echo "[PASS] Genuine ROS 2 Lyrical binary and environment verified."
echo "=============================================================================="
