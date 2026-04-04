#!/bin/bash
# Build script for OpenTurbine binaries
# Usage: ./build_binary.sh [version] [platform]
#   platform: linux, windows, macos, or all (default: linux)

set -e

VERSION=${1:-"0.1.0"}
PLATFORM=${2:-"linux"}

echo "Building OpenTurbine v${VERSION} binaries for $PLATFORM..."

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

mkdir -p dist

build_linux() {
    echo "Building Linux binary..."
    pyinstaller --onefile --windowed \
        --name "openturbine-${VERSION}-linux" \
        --add-data "configs:openturbine/configs" \
        --distpath dist \
        src/openturbine/ui/main_window.py
    echo "Linux binary: dist/openturbine-${VERSION}-linux"
}

build_windows() {
    echo "Building Windows binary..."
    pyinstaller --onefile --windowed \
        --name "openturbine-${VERSION}-windows.exe" \
        --add-data "configs;openturbine/configs" \
        --distpath dist \
        src/openturbine/ui/main_window.py
    echo "Windows binary: dist/openturbine-${VERSION}-windows.exe"
}

build_macos() {
    echo "Building macOS binary..."
    pyinstaller --onefile --windowed \
        --name "openturbine-${VERSION}-macos" \
        --add-data "configs:openturbine/configs" \
        --distpath dist \
        src/openturbine/ui/main_window.py
    echo "macOS binary: dist/openturbine-${VERSION}-macos"
}

case "$PLATFORM" in
    linux)
        build_linux
        ;;
    windows)
        build_windows
        ;;
    macos)
        build_macos
        ;;
    all)
        build_linux
        build_windows
        build_macos
        ;;
    *)
        echo "Unknown platform: $PLATFORM"
        echo "Usage: ./build_binary.sh [version] [platform]"
        echo "  platform: linux, windows, macos, or all"
        exit 1
        ;;
esac

echo ""
echo "Build complete!"
ls -la dist/
