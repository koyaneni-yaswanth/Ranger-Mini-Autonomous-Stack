#!/usr/bin/env bash
set -e
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
echo "[INFO] Bootstrapping Ranger Mini Next-Gen environment..."
bash "$PROJECT_DIR/scripts/check_environment.sh"
bash "$PROJECT_DIR/scripts/build.sh"
bash "$PROJECT_DIR/scripts/test.sh"
echo "[PASS] Bootstrap complete."
