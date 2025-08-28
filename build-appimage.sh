#!/bin/bash
# Script to build AppImage locally (requires docker)

echo "Building AppImage using Docker..."

# Create build directory
mkdir -p build
cd build

# Run AppImage build in Docker container
docker run --rm -v "$(pwd)/..":/app -w /app appimagecraft/appimagecraft:latest

echo "AppImage build complete!"
echo "Check build/ directory for the AppImage file."