#!/usr/bin/env bash
set -e
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
bash "$PROJECT_DIR/env/build_lyrical.sh"
