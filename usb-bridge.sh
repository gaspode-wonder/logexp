#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------
# Homebrew-free USB pass-through for macOS
# Creates a stable symlink (/tmp/geiger-bridge)
# that Docker can always mount as /dev/ttyUSB0.
#
# Requirements:
#   - ~/bin/socat (standalone binary)
#   - macOS (Intel or Apple Silicon)
#
# Usage:
#   ./usb-bridge.sh /dev/tty.usbserial-XXXX
#
# After running:
#   docker-compose.yml never changes:
#       devices:
#         - "/tmp/geiger-bridge:/dev/ttyUSB0"
# ---------------------------------------------

REAL_USB="$1"
STABLE_LINK="$HOME/.geiger-bridge"

if [[ ! -e "$REAL_USB" ]]; then
    echo "Error: Device $REAL_USB does not exist."
    exit 1
fi

if [[ ! -x "$HOME/bin/socat" ]]; then
    echo "Error: ~/bin/socat not found or not executable."
    exit 1
fi

echo "Creating virtual PTY pair..."

# Start PTY creation in background, capture PID
PTY_LOG=$(mktemp)
"$HOME/bin/socat" -d -d pty,raw,echo=0 pty,raw,echo=0 2> "$PTY_LOG" &
PTY_PID=$!

# Wait for PTY paths to appear
sleep 0.5

# Extract first PTY
VM_PTY=$(grep -m1 "PTY is" "$PTY_LOG" | awk '{print $7}')

if [[ -z "$VM_PTY" ]]; then
    echo "Error: Could not determine virtual PTY path."
    kill "$PTY_PID" || true
    exit 1
fi

echo "✅ Virtual PTY created: $VM_PTY"

# Kill the PTY-creation socat (we only needed the PTYs)
kill "$PTY_PID" || true
sleep 0.2

echo "Creating stable symlink: $STABLE_LINK"
rm -f "$STABLE_LINK"
ln -s "$VM_PTY" "$STABLE_LINK"
echo "✅ Symlink created: $STABLE_LINK → $VM_PTY"

echo ""
echo "Bridging $REAL_USB → $VM_PTY"
echo "Leave this terminal open to maintain the bridge."
echo ""

# Start the long-running bridge
exec "$HOME/bin/socat" "$REAL_USB" "$VM_PTY"
