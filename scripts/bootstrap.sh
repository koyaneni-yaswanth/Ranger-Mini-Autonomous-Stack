#!/usr/bin/env bash
set -e
PROJECT_DIR="/home/yash/ranger_mini_lyrical_2604_project"
echo "[INFO] Bootstrapping Ranger Mini Next-Gen environment..."
bash "$PROJECT_DIR/scripts/check_environment.sh"
bash "$PROJECT_DIR/scripts/build.sh"
bash "$PROJECT_DIR/scripts/test.sh"
echo "[PASS] Bootstrap complete."
