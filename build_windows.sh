#!/bin/bash
# Build script for OpenTurbine on Windows (using WSL or MinGW)
# Usage: ./build_windows.sh [version]

set -e

VERSION=${1:-"0.1.0"}
echo "============================================"
echo "Building OpenTurbine v${VERSION} for Windows"
echo "============================================"

# Check if running on Windows (WSL or native Windows with Git Bash)
echo "[1/6] Detecting build environment..."

IS_WSL=false
IS_WINDOWS=false

if grep -qEi "Microsoft|WSL" /proc/version 2>/dev/null; then
    IS_WSL=true
    echo "Detected: Windows Subsystem for Linux (WSL)"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    IS_WINDOWS=true
    echo "Detected: Git Bash / MinGW on Windows"
else
    echo "Detected: Linux (cross-compile for Windows)"
    echo "Note: For proper Windows build, run this script on Windows"
fi

# Check for Python
echo "[2/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found!"
    echo ""
    echo "Please install Python 3.9+ from: https://www.python.org/downloads/"
    echo "Make sure to check 'Add Python to PATH' during installation."
    exit 1
fi

PYTHON_CMD="python3"
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

$PYTHON_CMD --version

# Create virtual environment
echo "[3/6] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
fi

if [ "$IS_WINDOWS" = true ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "[4/6] Installing Python dependencies..."
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
echo "[5/6] Building Windows binary..."
mkdir -p dist

if [ "$IS_WINDOWS" = true ]; then
    pyinstaller --onefile --windowed \
        --name "openturbine-${VERSION}-windows.exe" \
        --add-data "configs;openturbine/configs" \
        --distpath dist \
        src/openturbine/ui/main_window.py
else
    # For WSL or Linux cross-compile
    pip install pywin32-ctypes 2>/dev/null || true
    pyinstaller --onefile --windowed \
        --name "openturbine-${VERSION}-windows.exe" \
        --add-data "configs;openturbine/configs" \
        --distpath dist \
        src/openturbine/ui/main_window.py
fi

echo "[6/6] Verifying build..."
echo ""
echo "============================================"
echo "Build complete!"
echo "============================================"
echo "Output: dist/openturbine-${VERSION}-windows.exe"
ls -lh dist/

echo ""
echo "To create an installer, consider using:"
echo "  - NSIS: https://nsis.sourceforge.io/"
echo "  - Inno Setup: https://jrsoftware.org/isinfo.php"
echo ""
echo "Or simply share the .exe file directly."
