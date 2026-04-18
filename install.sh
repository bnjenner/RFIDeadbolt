#!/usr/bin/env bash
set -euo pipefail

# Get Necessary Directories
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/RFIDeadbolt"
SHARE_DIR="$HOME/.local/share/rfideadbolt"
CONFIG_DIR="$HOME/.config/rfideadbolt"
BIN_DIR="$HOME/.local/bin"
UNIT_DIR="$HOME/.config/systemd/user"

# Check User Group
echo "// Installing RFIDeadbolt"
if ! id -nG "$USER" | grep -qw dialout; then
    echo "// Warning: '$USER' is not in the 'dialout' group."
    echo "//          Run: sudo usermod -aG dialout $USER   (then log out/in)"
fi

# Create Necessary Directories
mkdir -p "$SHARE_DIR" "$CONFIG_DIR" "$BIN_DIR" "$UNIT_DIR"

# Set Proper Permissions
install -m 644 "$SRC_DIR/SerialRFID.py"   "$SHARE_DIR/"
install -m 644 "$SRC_DIR/utils.py"        "$SHARE_DIR/"
install -m 755 "$SRC_DIR/gnome_unlock.py" "$SHARE_DIR/"
install -m 755 "$SRC_DIR/create_key.py"   "$SHARE_DIR/"

# Generate config.json from template (only if it doesn't already exist)
HASH_FILE="$CONFIG_DIR/rfideadbolt.hash"
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    sed "s|__HASH_FILE__|$HASH_FILE|g" "$SRC_DIR/config_template.json" \
        > "$CONFIG_DIR/config.json"
    chmod 644 "$CONFIG_DIR/config.json"
    echo "// Wrote default config to $CONFIG_DIR/config.json"
else
    echo "// Keeping existing $CONFIG_DIR/config.json"
fi

# Create Key
cat > "$BIN_DIR/rfideadbolt-create-key" <<EOF
#!/usr/bin/env bash
cd "$CONFIG_DIR"
exec env PYTHONPATH="$SHARE_DIR" python3 "$SHARE_DIR/create_key.py"
EOF
chmod 755 "$BIN_DIR/rfideadbolt-create-key"

# Create RFIDeadbolt service
cat > "$UNIT_DIR/rfideadbolt.service" <<EOF
[Unit]
Description=RFIDeadbolt GNOME session unlocker
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
WorkingDirectory=$CONFIG_DIR
Environment=PYTHONPATH=$SHARE_DIR
ExecStart=/usr/bin/python3 $SHARE_DIR/gnome_unlock.py

[Install]
WantedBy=graphical-session.target
EOF

# Reload system deamon
systemctl --user daemon-reload

echo ""
echo "// Installed."
echo "// Next steps:"
echo "//   1. Scan your tag:  rfideadbolt-create-key"
echo "//   2. Enable service: systemctl --user enable --now rfideadbolt.service"
echo "//   3. Tail logs:      journalctl --user -u rfideadbolt.service -f"
