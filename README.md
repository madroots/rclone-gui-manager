# Rclone GUI Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

A simple and modern graphical user interface for managing [rclone](https://rclone.org) remotes. This tool allows you to easily mount and unmount your cloud storage remotes with a user-friendly interface.

<img width="804" height="638" alt="image" src="https://github.com/user-attachments/assets/cc75c06f-6d5f-4d54-92ae-25f2fc9f686a" />


## Features

- **Remote Management**: View all configured rclone remotes in a clean table interface
- **One-Click Mounting**: Mount/unmount remotes with a single click
- **Connection Testing**: Test remote connections before mounting to avoid errors
- **Auto-Mount at Startup**: Automatically mount selected remotes at system startup via crontab integration
- **Smart Mount Points**: Automatically creates and manages mount points in user space (`~/mnt/[remote_name]`)
- **Folder Access**: Directly open mounted folders in your file manager

## Run as AppImage
Download appimage from release page. App expects rclone to be present on your machine.

> [!CAUTION]  
> **Do not use App Image Launcher**: Unfortunately, appimagelauncher has issues opening certain appimages, it seems its affecting new builds like mine. [Here](https://github.com/TheAssassin/AppImageLauncher/issues/656) and [here](https://github.com/TheAssassin/AppImageLauncher/issues/681) is more information.
>
> For an alternative launcher, you might look at [Gear Lever](https://github.com/mijorus/gearlever)

## Manual Installation

### 1. Install System Dependencies

- Python 3.6+
- rclone
- tkinter (usually included with Python)
- `mountpoint` command (available in most Linux distributions)
- FUSE (for mounting functionality)

First, ensure you have rclone installed and configured:
```bash
# Install rclone (if not already installed)
# Visit https://rclone.org/downloads/ for installation instructions

# Configure rclone with your remotes
rclone config
```

Then install the required system packages:

**Ubuntu/Debian:**
```bash
sudo apt install python3-tk fuse util-linux
```

**Fedora:**
```bash
sudo dnf install tkinter fuse util-linux
```

**Arch Linux:**
```bash
sudo pacman -S tk fuse util-linux
```

### 2. Install Rclone GUI Manager

Clone this repository and run the installation script:
```bash
git clone https://github.com/yourusername/rclone-gui-manager.git
cd rclone-gui-manager
chmod +x install.sh
./install.sh
```

This will:
- Install the application system-wide to `/usr/local/bin/`
- Create a desktop entry for menu access
- Set appropriate permissions

### 3. Launch the Application

After installation, you can launch the application in any of these ways:

- **From Applications Menu**: Look for "Rclone GUI Manager" in your Utilities or System Tools
- **From Terminal**: Simply type `rclone-gui-manager`
- **Using Keyboard Shortcut**: If your system supports it, you can search for "Rclone" in your application launcher

## Uninstallation

To completely remove the application:

```bash
cd rclone-gui-manager  # Navigate to your cloned repository
chmod +x uninstall.sh
./uninstall.sh
```

This will:
- Remove system-wide application files
- Remove desktop menu entry
- Remove user configuration files (`~/.config/rclone-gui-manager/`)
- Optionally remove mount points in `~/mnt` (with user confirmation)
- Remove any rclone mount entries from crontab

Note: The source files in the repository directory will be preserved.

## How It Works

### Remote Discovery
The application reads your rclone configuration file (`~/.config/rclone/rclone.conf`) to discover all configured remotes.

### Mount Points
When mounting a remote, the application creates a directory in `~/mnt/[remote_name]` and mounts the remote there. This location is chosen to avoid permission issues.

### Mounting
Uses `rclone mount --vfs-cache-mode writes` for optimal performance and compatibility.

### Unmounting
Uses `fusermount -u` (preferred) or `umount` to unmount remotes.

### Connection Testing
Before mounting, the application tests the connection to ensure the remote is accessible using `rclone lsf`.

### Automatic Mounting
You can enable automatic mounting at startup by adding entries to your crontab with `@reboot` entries.

## User Interface

The application features a clean, modern interface with:
- A main window showing all configured remotes in a sortable table
- Status bar with clear feedback messages
- Progress indicator for ongoing operations
- Theme toggle button for light/dark mode
- Action buttons for mounting, unmounting, testing, and refreshing

Mounted remotes are highlighted in green (or dark green in dark mode) for easy identification.

## Troubleshooting

- **Mounting fails**: Check that rclone is properly configured and the remote is accessible via command line
- **Permission errors**: Ensure you have the necessary permissions to create directories in your home folder
- **FUSE issues**: Make sure `fusermount` is available in your PATH (part of fuse package)
- **Application doesn't appear in menu**: Try logging out and back in, or restart your desktop environment
- **Theme not changing**: The theme change will take effect after restarting the application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details on releases and changes.

## Acknowledgments

- [rclone](https://rclone.org) - The tool that makes this all possible
- Python tkinter - For providing a simple GUI framework
- All contributors and users who have provided feedback and suggestions

---

**Note**: This is an unofficial GUI wrapper for rclone. For issues with rclone itself, please refer to the [rclone project](https://github.com/rclone/rclone).
