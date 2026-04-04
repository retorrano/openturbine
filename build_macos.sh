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

command -v python3 >/dev/null 2>&1 || {
    echo ""
    echo "Python 3 not found!"
    echo ""
    echo "Please install Python 3.9+ from: https://www.python.org/downloads/mac-osx/"
    echo ""
    echo "Or using Homebrew:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "  brew install python@3.10"
    echo ""
    exit 1
}

# Check macOS version
MACOS_VERSION=$(sw_vers -productVersion 2>/dev/null || echo "Unknown")
echo "macOS Version: $MACOS_VERSION"

# Detect Apple Silicon or Intel
ARCH_TYPE=$(uname -m)
if [ "$ARCH_TYPE" = "arm64" ]; then
    echo "Architecture: Apple Silicon (M1/M2/M3)"
else
    echo "Architecture: Intel (x86_64)"
fi

# Check if Homebrew is available
echo "[2/7] Checking Homebrew..."
HOMEBREW_PREFIX=""
if command -v brew &> /dev/null; then
    HOMEBREW_PREFIX=$(brew --prefix 2>/dev/null || echo "/opt/homebrew")
else
    echo ""
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    HOMEBREW_PREFIX=$(brew --prefix)
fi
echo "Homebrew prefix: $HOMEBREW_PREFIX"

# Install system dependencies using Homebrew
echo "[3/7] Installing system dependencies..."
brew install \
    python@3.10 \
    qt \
    vtk \
    autoconf \
    automake \
    libtool \
    pkg-config

# Set up paths for Qt
export PATH="$HOMEBREW_PREFIX/opt/qt/bin:$PATH"
export PKG_CONFIG_PATH="$HOMEBREW_PREFIX/opt/qt/lib/pkgconfig:$PKG_CONFIG_PATH"
export CMAKE_PREFIX_PATH="$HOMEBREW_PREFIX/opt/qt:$CMAKE_PREFIX_PATH"

# Set up Python
echo "[4/7] Setting up Python..."
PYTHON_CMD="python3"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Python command: $PYTHON_CMD"
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
echo "[7/7] Installing Python packages..."
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
echo ""
echo "Building macOS binary..."
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
echo "============================================"
echo "IMPORTANT: Security Notes"
echo "============================================"
echo ""
echo "On first run, macOS may block the app:"
echo ""
echo "1. Open System Preferences > Security & Privacy > General"
echo "2. You should see a message about 'openturbine-${VERSION}-macos'"
echo "3. Click 'Open Anyway'"
echo ""
echo "Or from terminal, run:"
echo "  xattr -d com.apple.quarantine dist/openturbine-${VERSION}-macos"
echo ""
echo "To run: open dist/openturbine-${VERSION}-macos"
echo "Or: ./dist/openturbine-${VERSION}-macos"
