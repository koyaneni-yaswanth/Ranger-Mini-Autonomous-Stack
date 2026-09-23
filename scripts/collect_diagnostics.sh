#!/usr/bin/env bash
PROJECT_DIR="/home/yash/ranger_mini_lyrical_2604_project"
REPORT_DIR="$PROJECT_DIR/diagnostics/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$REPORT_DIR"

echo "[INFO] Collecting system diagnostics into $REPORT_DIR..."
uname -a > "$REPORT_DIR/kernel.log" 2>&1
free -h > "$REPORT_DIR/memory.log" 2>&1
df -h > "$REPORT_DIR/disk.log" 2>&1
nvidia-smi > "$REPORT_DIR/gpu.log" 2>&1 || true
ip a > "$REPORT_DIR/network.log" 2>&1
dmesg | tail -n 100 > "$REPORT_DIR/dmesg_tail.log" 2>&1 || true
echo "[PASS] Diagnostic bundle saved to $REPORT_DIR"
