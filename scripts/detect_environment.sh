#!/bin/bash
set -e

echo "=== ENVIRONMENT AUDIT ==="
echo "OS: $(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"')"
echo "Kernel: $(uname -r)"
echo "CPU: $(uname -m)"
echo "Active ROS_DISTRO: ${ROS_DISTRO:-NONE}"
echo "WSLg X11 Display: ${DISPLAY:-NONE}"
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)"
else
    echo "GPU: Integrated / Fallback"
fi
exit 0
