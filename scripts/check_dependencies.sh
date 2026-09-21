#!/bin/bash
set -e

echo "=== DEPENDENCY CHECK ==="
python3 -c "
import rclpy, tf2_ros, cv2, numpy, matplotlib, yaml
print('[OK] Core Python libraries verified (rclpy, tf2_ros, cv2, numpy, matplotlib, yaml)')
"
which xacro >/dev/null && echo "[OK] xacro available."
which check_urdf >/dev/null && echo "[OK] check_urdf available."
which colcon >/dev/null && echo "[OK] colcon available."
exit 0
