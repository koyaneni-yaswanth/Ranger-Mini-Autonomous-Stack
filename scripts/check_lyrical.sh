#!/bin/bash
set -e

echo "=== LYRICAL ENVIRONMENT CHECK ==="
if [ -f "$HOME/ranger_mini_lyrical_ws/install/setup.bash" ]; then
    echo "[OK] Found ~/ranger_mini_lyrical_ws/install/setup.bash"
else
    echo "[WARNING] Lyrical workspace not yet built."
fi
SYMLINKS=$(find "$HOME/ranger_mini_lyrical_ws/src" -type l 2>/dev/null | wc -l)
echo "[OK] Lyrical workspace symlinks: $SYMLINKS"
exit 0
