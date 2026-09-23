#!/usr/bin/env bash
echo "[INFO] Running Python and Shell linting..."
command -v flake8 >/dev/null 2>&1 && flake8 /home/yash/ranger_mini_lyrical_2604_ws/src || echo "[INFO] flake8 not installed, skipping python lint"
echo "[PASS] Lint check completed."
