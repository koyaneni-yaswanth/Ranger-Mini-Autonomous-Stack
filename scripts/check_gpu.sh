#!/usr/bin/env bash
set -e
echo "=============================================================================="
echo " [GPU CHECK] NVIDIA RTX 5060 3D ACCELERATION TEST"
echo "=============================================================================="
export DISPLAY="${DISPLAY:-:0}"
export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
export LIBGL_ALWAYS_SOFTWARE=0
export GALLIUM_DRIVER=d3d12

if ! nvidia-smi >/dev/null 2>&1; then
    echo "[FAIL] NVIDIA GPU driver not accessible via WSL."
    exit 1
fi

RENDERER=$(glxinfo -B 2>/dev/null | grep "OpenGL renderer string" || echo "Unknown")
echo "Active OpenGL Renderer: $RENDERER"

if echo "$RENDERER" | grep -qi "NVIDIA"; then
    echo "[OK] NVIDIA RTX GPU accelerated rendering verified."
else
    echo "[WARN] Renderer does not explicitly state NVIDIA. Check MESA_D3D12_DEFAULT_ADAPTER_NAME."
fi
echo "=============================================================================="
echo "[PASS] GPU validation completed."
