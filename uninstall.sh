#!/bin/bash

# Rclone GUI Manager Uninstallation Script

echo "Uninstalling Rclone GUI Manager..."

# Remove system-wide files
echo "Removing system-wide installation..."
sudo rm -f /usr/local/bin/rclone-gui-manager.py
sudo rm -f /usr/local/bin/rclone-gui-manager

# Remove desktop entry for the current user
DESKTOP_FILE="$HOME/.local/share/applications/rclone-gui-manager.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    echo "Removing desktop entry: $DESKTOP_FILE"
    rm -f "$DESKTOP_FILE"
fi

# Remove configuration files
CONFIG_DIR="$HOME/.config/rclone-gui-manager"
if [ -d "$CONFIG_DIR" ]; then
    echo "Removing configuration directory: $CONFIG_DIR"
    rm -rf "$CONFIG_DIR"
else
    echo "Configuration directory not found: $CONFIG_DIR"
fi

# Ask user if they want to remove mount points
echo ""
echo "Do you want to remove all mount points in ~/mnt? (y/n)"
echo "Note: This will only remove empty directories in ~/mnt"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    MNT_DIR="$HOME/mnt"
    if [ -d "$MNT_DIR" ]; then
        echo "Removing mount point directory: $MNT_DIR"
        # Only remove if it's empty or contains only empty directories
        rmdir "$MNT_DIR" 2>/dev/null || {
            # Try to remove empty subdirectories
            if [ -d "$MNT_DIR" ]; then
                find "$MNT_DIR" -type d -empty -delete 2>/dev/null
                # Try to remove the main directory again
                rmdir "$MNT_DIR" 2>/dev/null || echo "Mount directory not empty or in use, skipping..."
            fi
        }
    else
        echo "Mount directory not found: $MNT_DIR"
    fi
fi

# Remove cron entries (if any)
echo ""
echo "Checking for and removing cron entries..."
# Check if crontab exists
if crontab -l >/dev/null 2>&1; then
    # Create a temporary file to store filtered crontab
    TEMP_CRON=$(mktemp)
    
    # Get current crontab and filter out rclone entries
    crontab -l 2>/dev/null | grep -v "rclone mount" > "$TEMP_CRON" 2>/dev/null
    
    # Only update crontab if there were changes
    if crontab -l 2>/dev/null | grep -q "rclone mount"; then
        echo "Removing rclone mount entries from crontab..."
        crontab "$TEMP_CRON"
    else
        echo "No rclone mount entries found in crontab"
    fi
    
    # Clean up
    rm -f "$TEMP_CRON"
else
    echo "No crontab found or not accessible"
fi

echo ""
echo "Uninstallation complete!"
echo "The source files in this directory have been preserved."
echo "To completely remove the source files, delete this directory manually."