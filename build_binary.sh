#!/bin/bash
# Build script for OpenTurbine binaries
# Usage: ./build_binary.sh [version]

set -e

VERSION=${1:-"0.1.0"}
echo "Building OpenTurbine v${VERSION} binaries..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller PySide6 vtk numpy scipy matplotlib

# Build Linux binary
echo "Building Linux binary..."
pyinstaller --onefile --windowed \
    --name "openturbine-${VERSION}-linux" \
    --add-data "src/openturbine/configs:openturbine/configs" \
    --distpath dist \
    src/openturbine/ui/main_window.py

echo "Build complete!"
echo "Output: dist/openturbine-${VERSION}-linux"
ls -la dist/
