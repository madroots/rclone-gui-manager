#!/bin/bash
# Script to build AppImage locally (requires docker)

echo "Building AppImage using Docker..."

# Create build directory
mkdir -p build
cd build

# Run AppImage build in Docker container
# Using a more appropriate Docker image for Python AppImage building
docker run --rm -v "$(pwd)/..":/app -w /app ubuntu:20.04 bash -c "
  apt-get update && 
  apt-get install -y wget desktop-file-utils libfuse2 &&
  wget -O python.AppImage \"https://github.com/niess/python-appimage/releases/download/python3.9/python3.9.23-cp39-cp39-manylinux2014_x86_64.AppImage\" &&
  chmod +x python.AppImage &&
  ./python.AppImage --appimage-extract >/dev/null 2>&1 &&
  mkdir -p AppDir/usr/bin &&
  cp -r squashfs-root/usr/bin/* AppDir/usr/bin/ &&
  cp -r squashfs-root/usr/lib AppDir/usr/ &&
  cp -r squashfs-root/usr/share AppDir/usr/ || echo \"No share directory to copy\" &&
  cp -r squashfs-root/opt AppDir/ || echo \"No opt directory to copy\" &&
  # Remove the existing AppRun symlink
  rm -f AppDir/AppRun &&
  cp /app/rclone-gui-manager.py AppDir/usr/bin/ &&
  chmod 755 AppDir/usr/bin/rclone-gui-manager.py &&
  echo '#!/bin/bash' > AppDir/usr/bin/rclone-gui-manager &&
  echo 'DIR=\"$(dirname \"\$0\")\"' >> AppDir/usr/bin/rclone-gui-manager &&
  echo '\"\$DIR/python3.9\" \"\$DIR/rclone-gui-manager.py\" \"\$@\"' >> AppDir/usr/bin/rclone-gui-manager &&
  chmod 755 AppDir/usr/bin/rclone-gui-manager &&
  echo '[Desktop Entry]' > AppDir/rclone-gui-manager.desktop &&
  echo 'Type=Application' >> AppDir/rclone-gui-manager.desktop &&
  echo 'Name=Rclone GUI Manager' >> AppDir/rclone-gui-manager.desktop &&
  echo 'Comment=Manage rclone remotes with a GUI' >> AppDir/rclone-gui-manager.desktop &&
  echo 'Exec=rclone-gui-manager' >> AppDir/rclone-gui-manager.desktop &&
  echo 'Icon=rclone-gui-manager' >> AppDir/rclone-gui-manager.desktop &&
  echo 'Terminal=false' >> AppDir/rclone-gui-manager.desktop &&
  echo 'Categories=Utility;FileTools;' >> AppDir/rclone-gui-manager.desktop &&
  chmod 644 AppDir/rclone-gui-manager.desktop &&
  cp AppDir/rclone-gui-manager.desktop AppDir/usr/share/applications/ &&
  if [ -f \"/app/rclone-gui-manager.svg\" ]; then
    cp /app/rclone-gui-manager.svg AppDir/rclone-gui-manager.svg &&
    cp /app/rclone-gui-manager.svg AppDir/usr/share/icons/hicolor/256x256/apps/rclone-gui-manager.svg &&
    chmod 644 AppDir/rclone-gui-manager.svg &&
    chmod 644 AppDir/usr/share/icons/hicolor/256x256/apps/rclone-gui-manager.svg
  fi &&
  # Create AppRun script with proper permissions (overwrite any existing one)
  echo '#!/bin/bash' > AppDir/AppRun &&
  echo 'HERE=\"$(dirname \"$(readlink -f \"\$0\")\")\"' >> AppDir/AppRun &&
  echo 'exec \"\$HERE/usr/bin/rclone-gui-manager\" \"\$@\"' >> AppDir/AppRun &&
  chmod 755 AppDir/AppRun &&
  wget -O appimagetool \"https://github.com/AppImage/appimagetool/releases/download/1.9.0/appimagetool-x86_64.AppImage\" &&
  chmod +x appimagetool &&
  ARCH=x86_64 ./appimagetool AppDir/ &&
  if [ -f \"Rclone_GUI_Manager-x86_64.AppImage\" ]; then
    mv Rclone_GUI_Manager-x86_64.AppImage rclone-gui-manager-x86_64.AppImage
  elif ls Rclone_GUI_Manager*.AppImage 1> /dev/null 2>&1; then
    mv Rclone_GUI_Manager*.AppImage rclone-gui-manager-x86_64.AppImage
  elif ls *.AppImage 1> /dev/null 2>&1; then
    mv *.AppImage rclone-gui-manager-x86_64.AppImage
  fi &&
  chmod +x rclone-gui-manager-x86_64.AppImage
"

echo "AppImage build complete!"
echo "Check build/ directory for the AppImage file."