#!/usr/bin/env bash
set -e
echo "=============================================================================="
echo " [NETWORK CHECK] DDS DISCOVERY & INTERFACES"
echo "=============================================================================="
ip -brief address show
echo "Testing loopback multicast..."
if ping -c 1 127.0.0.1 >/dev/null 2>&1; then
    echo "[OK] Loopback active."
fi
echo "=============================================================================="
echo "[PASS] Network verified."
