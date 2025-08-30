#!/bin/bash

# Rclone GUI Manager Installation Script

echo "Installing Rclone GUI Manager system-wide..."

# Check for required tools
echo "Checking for required tools..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

# Check for rclone
if ! command -v rclone &> /dev/null; then
    echo "Warning: rclone is not installed. Please install rclone before using this application."
    echo "See: https://rclone.org/downloads/"
fi

# Check for tkinter
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "Warning: tkinter is not installed. Please install tkinter for Python 3."
fi

# Check if we have sudo access
if ! command -v sudo &> /dev/null; then
    echo "Error: sudo is not available. Cannot install system-wide."
    exit 1
fi

# Test sudo access
if ! sudo -v &> /dev/null; then
    echo "Error: Unable to obtain sudo privileges. Cannot install system-wide."
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install the Python script system-wide
echo "Installing application files..."
sudo install -m 755 "$SCRIPT_DIR/rclone-gui-manager.py" /usr/local/bin/

# Create a launcher script
echo "Creating system launcher..."
sudo tee /usr/local/bin/rclone-gui-manager > /dev/null << 'EOF'
#!/bin/bash
# System-wide launcher script for Rclone GUI Manager
python3 /usr/local/bin/rclone-gui-manager.py "$@"
EOF

# Make the launcher executable
sudo chmod 755 /usr/local/bin/rclone-gui-manager

# Also create a desktop entry for the current user
DESKTOP_FILE="$HOME/.local/share/applications/rclone-gui-manager.desktop"
mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Rclone GUI Manager
Comment=Manage rclone remotes with a GUI
Exec=/usr/local/bin/rclone-gui-manager
Icon=drive-harddisk
Terminal=false
Categories=Utility;FileTools;
EOF

echo "Installation complete!"
echo "You can now run the application by typing: rclone-gui-manager"
echo "Or find it in your applications menu as 'Rclone GUI Manager'"