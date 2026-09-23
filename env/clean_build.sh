#!/usr/bin/env bash
WS_DIR="${WS_DIR:-$(cd "$PROJECT_DIR/../ranger_mini_lyrical_2604_ws" 2>/dev/null && pwd)}"
echo "[INFO] Cleaning build artifacts from $WS_DIR..."
rm -rf "$WS_DIR/build" "$WS_DIR/install" "$WS_DIR/log"
echo "[PASS] Clean complete."
