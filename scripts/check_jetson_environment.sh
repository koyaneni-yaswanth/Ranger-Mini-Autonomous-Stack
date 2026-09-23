#!/usr/bin/env bash
# ==============================================================================
# Jetson Orin Edge Environment Audit & Diagnostic Tool
# Validates Tegra platform, JetPack L4T, GPU/TensorRT, CAN, Sensors & Power Mode
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=============================================================================="
echo "          NVIDIA JETSON ORIN HARDWARE & ENVIRONMENT AUDIT"
echo "=============================================================================="

IS_JETSON=0
ARCH="$(uname -m)"

# 1. Architecture Check
echo -n "[CHECK] System Architecture: "
if [ "${ARCH}" = "aarch64" ]; then
    echo "PASS (ARM64 / aarch64 detected)"
else
    echo "WARNING: ${ARCH} detected. Native Jetson Orin requires ARM64 (aarch64)."
fi

# 2. Jetson / Tegra SOC Detection
echo -n "[CHECK] Tegra Platform Detection: "
if [ -f /etc/nv_tegra_release ] || [ -d /sys/devices/soc0 ]; then
    IS_JETSON=1
    echo "PASS (NVIDIA Tegra SOC detected)"
    if [ -f /etc/nv_tegra_release ]; then
        head -n 1 /etc/nv_tegra_release
    fi
else
    echo "SIMULATED / NON-JETSON (x86_64 host or virtual WSL2 environment)"
fi

# 3. GPU & CUDA Acceleration
echo -n "[CHECK] NVIDIA CUDA Stack: "
if command -v nvcc &> /dev/null; then
    CUDA_VER="$(nvcc --version | grep "release" | awk '{print $5}' | sed 's/,//')"
    echo "PASS (CUDA ${CUDA_VER})"
elif [ -d /usr/local/cuda ]; then
    echo "PASS (CUDA directory found at /usr/local/cuda)"
else
    echo "INFO: nvcc not in PATH (WSL2 uses direct /usr/lib/wsl/lib driver bridge)"
fi

# 4. TensorRT Inference Engine
echo -n "[CHECK] TensorRT Runtime: "
if dpkg -l | grep -q "libnvinfer" 2>/dev/null; then
    TRT_VER="$(dpkg -l | grep "libnvinfer" | head -n 1 | awk '{print $3}')"
    echo "PASS (TensorRT ${TRT_VER})"
elif python3 -c "import tensorrt" &>/dev/null; then
    echo "PASS (Python tensorrt module found)"
else
    echo "NOTICE: Native TensorRT not installed. CPU PyTorch/HOG fallback active."
fi

# 5. SocketCAN Interface (can0)
echo -n "[CHECK] SocketCAN Interface (can0): "
if ip link show can0 &> /dev/null; then
    CAN_STATE="$(ip -brief link show can0 | awk '{print $2}')"
    echo "PASS (can0 present, state: ${CAN_STATE})"
else
    echo "NOT FOUND: can0 interface not detected. Physical robot CAN bus disconnected."
fi

# 6. USB Peripheral Bus (RealSense / LiDAR / Serial)
echo -n "[CHECK] USB Video / Camera Devices: "
if ls /dev/video* &> /dev/null; then
    V_DEVS="$(ls /dev/video* | tr '\n' ' ')"
    echo "PASS (Found ${V_DEVS})"
else
    echo "NONE: No /dev/video* devices found."
fi

# 7. Jetson Power / Thermal Profile (nvpmodel)
echo -n "[CHECK] Power & Clock Profile: "
if command -v nvpmodel &> /dev/null; then
    MODE="$(nvpmodel -q 2>/dev/null | grep -E "NV Power Mode|MODE" | head -n 1 || echo "Active")"
    echo "PASS (${MODE})"
else
    echo "N/A (nvpmodel only available on native Tegra hardware)"
fi

echo "=============================================================================="
if [ "${IS_JETSON}" -eq 1 ] && ip link show can0 &>/dev/null; then
    echo ">>> RESULT: JETSON ORIN READY FOR HARDWARE BRINGUP <<<"
    exit 0
else
    echo ">>> RESULT: ENVIRONMENT VERIFIED (SIMULATION / WORKSTATION MODE) <<<"
    echo ">>> NOTE: To run real hardware, connect to physical Jetson Orin with can0. <<<"
    exit 0
fi
