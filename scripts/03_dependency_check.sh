#!/usr/bin/env bash
set -e
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " [03/12] DEPENDENCY & PREREQUISITE AUDIT"
echo "=============================================================================="
python3 -c "
import sys
modules = ['rclpy', 'tf2_ros', 'cv2', 'numpy', 'matplotlib', 'yaml']
missing = []
for m in modules:
    try:
        __import__(m)
        print(f'[OK] Python module: {m}')
    except ImportError:
        missing.append(m)
        print(f'[FAIL] Missing module: {m}')
if missing:
    sys.exit(1)
"

for tool in xacro check_urdf colcon; do
    if which $tool >/dev/null 2>&1; then
        echo "[OK] CLI Tool: $tool"
    else
        echo "[FAIL] Missing tool: $tool"
        exit 1
    fi
done
echo "=============================================================================="
echo "[PASS] All core dependencies satisfied."
