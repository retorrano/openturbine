#!/bin/bash
# Build script for OpenTurbine on Windows
# Supports: Native Windows, WSL (Windows Subsystem for Linux), Git Bash, MinGW
# Usage: ./build_windows.sh [version]

set -e

VERSION=${1:-"0.1.0"}
echo "============================================"
echo "Building OpenTurbine v${VERSION} for Windows"
echo "============================================"

# Detect environment
echo "[1/6] Detecting build environment..."

IS_WSL=false
IS_MINGW=false
IS_NATIVE=false

if grep -qEi "Microsoft|WSL" /proc/version 2>/dev/null; then
    IS_WSL=true
    echo "Environment: Windows Subsystem for Linux (WSL)"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    IS_MINGW=true
    echo "Environment: Git Bash / MinGW"
elif [[ "$OSTYPE" == "win32" || -n "$WINDIR" ]]; then
    IS_NATIVE=true
    echo "Environment: Native Windows"
else
    echo "Environment: Unknown - assuming Windows"
fi

# Check for Python
echo "[2/6] Checking Python installation..."
PYTHON_CMD=""

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif [ -n "$PYTHON_PATH" ]; then
    PYTHON_CMD="$PYTHON_PATH"
elif [ -n "$LOCALAPPDATA" ] && [ -d "$LOCALAPPDATA/Programs/Python" ]; then
    PYTHON_CMD="$LOCALAPPDATA/Programs/Python/Python311/python.exe"
elif [ -n "$PROGRAMFILES" ] && [ -d "$PROGRAMFILES/Python" ]; then
    PYTHON_CMD="$PROGRAMFILES/Python/Python311/python.exe"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "ERROR: Python not found!"
    echo ""
    echo "Please install Python 3.9+ from: https://www.python.org/downloads/"
    echo ""
    echo "During installation, make sure to:"
    echo "  1. Check 'Add Python to PATH'"
    echo "  2. Check 'Install pip'"
    echo ""
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Create virtual environment
echo "[3/6] Setting up Python virtual environment..."

if [ "$IS_WSL" = true ] || [ "$IS_MINGW" = true ]; then
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
    fi
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
else
    # Native Windows
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
    fi
    source venv/Scripts/activate
fi

# Upgrade pip
echo "[4/6] Installing Python dependencies..."
pip install --upgrade pip

# Install all required packages
echo "[5/6] Installing required packages (this may take a while)..."
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
echo "[6/6] Building Windows binary..."
mkdir -p dist

# Determine path separator
if [ "$IS_WSL" = true ] || [ "$IS_MINGW" = true ]; then
    PATH_SEP=";"
else
    PATH_SEP=";"
fi

pyinstaller --onefile --windowed \
    --name "openturbine-${VERSION}-windows.exe" \
    --add-data "configs;openturbine/configs" \
    --distpath dist \
    src/openturbine/ui/main_window.py

echo ""
echo "============================================"
echo "Build complete!"
echo "============================================"
echo "Output: dist/openturbine-${VERSION}-windows.exe"
ls -lh dist/

echo ""
echo "Note: On first run, Windows may show a SmartScreen warning."
echo "Click 'More info' and 'Run anyway' to proceed."
echo ""
echo "To create an installer, consider using:"
echo "  - NSIS: https://nsis.sourceforge.io/"
echo "  - Inno Setup: https://jrsoftware.org/isinfo.php"
