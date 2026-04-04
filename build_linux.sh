#!/bin/bash
# Build script for OpenTurbine on Linux
# Usage: ./build_linux.sh [version]

set -e

VERSION=${1:-"0.1.0"}
echo "============================================"
echo "Building OpenTurbine v${VERSION} for Linux"
echo "============================================"

# Check for required system packages
echo "[1/5] Checking system dependencies..."
MISSING_DEPS=()

command -v python3 >/dev/null 2>&1 || MISSING_DEPS+=("python3")
command -v pip3 >/dev/null 2>&1 || MISSING_DEPS+=("python3-pip")

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Install required system libraries for Qt/VTK
echo "[2/5] Installing system libraries for Qt and VTK..."
sudo apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    libxrandr2 \
    libxcomposite1 \
    libxdamage1 \
    libxkbcommon0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libatspi2.0-0 \
    libfontconfig1 \
    libfreetype6 \
    libpixman-1-0 \
    libxcb-shm0 \
    libxcb-render0 \
    libxcb-render-util0

# Create virtual environment
echo "[3/5] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Upgrade pip
echo "[4/5] Installing Python dependencies..."
pip install --upgrade pip

# Install all required packages
pip install \
    numpy \
    scipy \
    matplotlib \
    pandas \
    pyqtgraph \
    PySide6 \
    vtk \
    pyvista \
    pyinstaller

# Install the package in editable mode
pip install -e .

# Build the binary
echo "[5/5] Building Linux binary..."
mkdir -p dist
pyinstaller --onefile --windowed \
    --name "openturbine-${VERSION}-linux" \
    --add-data "configs:openturbine/configs" \
    --distpath dist \
    src/openturbine/ui/main_window.py

echo ""
echo "============================================"
echo "Build complete!"
echo "============================================"
echo "Output: dist/openturbine-${VERSION}-linux"
ls -lh dist/

# Make executable
chmod +x "dist/openturbine-${VERSION}-linux"

echo ""
echo "To run: ./dist/openturbine-${VERSION}-linux"
