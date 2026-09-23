#!/usr/bin/env bash
WS_DIR="/home/yash/ranger_mini_lyrical_2604_ws"
echo "[INFO] Cleaning build artifacts from $WS_DIR..."
rm -rf "$WS_DIR/build" "$WS_DIR/install" "$WS_DIR/log"
echo "[PASS] Clean complete."
