#!/usr/bin/env bash
set -e
[ -f "/opt/ros/humble/setup.bash" ] && source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=============================================================================="
echo " [01/12] SYSTEM & OPERATING SYSTEM AUDIT"
echo "=============================================================================="
echo "OS:             $(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2)"
echo "Kernel:         $(uname -r)"
echo "Architecture:   $(uname -m)"
echo "Python:         $(python3 --version 2>&1)"
echo "GCC:            $(gcc --version | head -n 1)"
echo "CMake:          $(cmake --version | head -n 1)"
echo "Git:            $(git --version)"
echo "Docker:         $(docker --version 2>/dev/null || echo 'Not installed')"
echo "GPU / SMI:      $(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null || echo 'NVIDIA GPU via WSLg/Mesa')"
echo "Display Server: DISPLAY=$DISPLAY | WAYLAND_DISPLAY=$WAYLAND_DISPLAY"
echo "=============================================================================="
echo "[PASS] System audit completed."
