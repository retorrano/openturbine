#!/bin/bash
# Build script for OpenTurbine on macOS
# Usage: ./build_macos.sh [version]

set -e

VERSION=${1:-"0.1.0"}
echo "============================================"
echo "Building OpenTurbine v${VERSION} for macOS"
echo "============================================"

# Check for required tools
echo "[1/7] Checking build environment..."

MISSING_DEPS=()

command -v python3 >/dev/null 2>&1 || MISSING_DEPS+=("Python 3")
command -v pip3 >/dev/null 2>&1 || MISSING_DEPS+=("pip3")

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo ""
    echo "Missing required tools:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo "Please install from: https://www.python.org/downloads/mac-osx/"
    echo "Or using Homebrew: brew install python3"
    exit 1
fi

# Check macOS version
MACOS_VERSION=$(sw_vers -productVersion)
echo "macOS Version: $MACOS_VERSION"

# Install system dependencies using Homebrew
echo "[2/7] Checking Homebrew..."
if ! command -v brew &> /dev/null; then
    echo ""
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "[3/7] Installing system dependencies..."
brew install \
    python@3.10 \
    pyqt@6 \
    vtk \
    qt@6 \
    autoconf \
    automake \
    libtool

# Set up Python
echo "[4/7] Setting up Python..."
PYTHON_CMD="python3"
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

$PYTHON_CMD --version

# Create virtual environment
echo "[5/7] Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
fi
source venv/bin/activate

# Upgrade pip
echo "[6/7] Installing Python dependencies..."
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
echo "[7/7] Building macOS binary..."
mkdir -p dist
pyinstaller --onefile --windowed \
    --name "openturbine-${VERSION}-macos" \
    --add-data "configs:openturbine/configs" \
    --distpath dist \
    src/openturbine/ui/main_window.py

echo ""
echo "============================================"
echo "Build complete!"
echo "============================================"
echo "Output: dist/openturbine-${VERSION}-macos"
ls -lh dist/

# Make executable
chmod +x "dist/openturbine-${VERSION}-macos"

echo ""
echo "Note: On first run, macOS may require permission:"
echo "  System Preferences > Security & Privacy > General"
echo "  Allow 'openturbine-${VERSION}-macos'"
echo ""
echo "To run: open dist/openturbine-${VERSION}-macos"
