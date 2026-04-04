#!/bin/bash
# Build script for OpenTurbine on Linux
# Usage: ./build_linux.sh [version]

set -e

VERSION=${1:-"0.1.0"}
echo "============================================"
echo "Building OpenTurbine v${VERSION} for Linux"
echo "============================================"

# Detect Linux distribution and set package manager
echo "[1/6] Detecting Linux distribution..."
DETECTED_PKG_MGR=""
PKG_INSTALL=""

if command -v dnf &> /dev/null; then
    DETECTED_PKG_MGR="dnf"
    echo "Detected: Fedora/Red Hat/CentOS/RHEL"
    PKG_INSTALL="sudo dnf install -y"
elif command -v apt-get &> /dev/null; then
    DETECTED_PKG_MGR="apt-get"
    echo "Detected: Debian/Ubuntu"
    PKG_INSTALL="sudo apt-get install -y"
elif command -v pacman &> /dev/null; then
    DETECTED_PKG_MGR="pacman"
    echo "Detected: Arch Linux"
    PKG_INSTALL="sudo pacman -S --noconfirm"
elif command -v zypper &> /dev/null; then
    DETECTED_PKG_MGR="zypper"
    echo "Detected: openSUSE"
    PKG_INSTALL="sudo zypper install -y"
elif command -v apk &> /dev/null; then
    DETECTED_PKG_MGR="apk"
    echo "Detected: Alpine Linux"
    PKG_INSTALL="apk add --no-cache"
else
    echo "Warning: No supported package manager found."
    echo "Please install dependencies manually."
    echo ""
fi

# Check for required system packages
echo "[2/6] Checking system dependencies..."
MISSING_DEPS=()

command -v python3 >/dev/null 2>&1 || MISSING_DEPS+=("python3")
command -v pip3 >/dev/null 2>&1 || MISSING_DEPS+=("python3-pip")

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "Installing missing: ${MISSING_DEPS[*]}"
    if [ -n "$PKG_INSTALL" ]; then
        if [ "$DETECTED_PKG_MGR" = "dnf" ]; then
            $PKG_INSTALL python3 python3-pip python3-virtualenv
        elif [ "$DETECTED_PKG_MGR" = "apt-get" ]; then
            $PKG_INSTALL python3 python3-pip python3-venv
        elif [ "$DETECTED_PKG_MGR" = "pacman" ]; then
            $PKG_INSTALL python python-pip python-virtualenv
        elif [ "$DETECTED_PKG_MGR" = "zypper" ]; then
            $PKG_INSTALL python3 python3-pip python3-virtualenv
        elif [ "$DETECTED_PKG_MGR" = "apk" ]; then
            $PKG_INSTALL py3-pip
        fi
    else
        echo "Please install: ${MISSING_DEPS[*]}"
        exit 1
    fi
fi

# Install required system libraries for Qt/VTK
echo "[3/6] Installing system libraries for Qt and VTK..."
if [ -n "$PKG_INSTALL" ]; then
    if [ "$DETECTED_PKG_MGR" = "dnf" ]; then
        sudo dnf groupinstall -y "Development Tools"
        sudo dnf install -y \
            mesa-libGL \
            glib2 \
            libSM \
            libXrender \
            libXext \
            libXrandr \
            libXcomposite \
            libXdamage \
            libXkbcommon \
            atk \
            at-spi2-atk \
            cups-libs \
            libdrm \
            dbus-libs \
            at-spi2-core \
            fontconfig \
            freetype \
            pixman \
            libxcb \
            gcc \
            gcc-c++
    elif [ "$DETECTED_PKG_MGR" = "apt-get" ]; then
        sudo apt-get update
        sudo apt-get install -y \
            python3 python3-pip python3-venv \
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
            libxcb-render-util0 \
            build-essential
    elif [ "$DETECTED_PKG_MGR" = "pacman" ]; then
        sudo pacman -S --noconfirm \
            python python-pip python-virtualenv \
            mesa libglvnd \
            glib2 libsm libxrender libxext libxrandr \
            libxcomposite libxdamage libxkbcommon atk \
            at-spi2-atk cups libdrm dbus fontconfig freetype pixman \
            libxcb base-devel
    elif [ "$DETECTED_PKG_MGR" = "zypper" ]; then
        sudo zypper install -y \
            python3 python3-pip python3-virtualenv \
            Mesa-libGL1 glib2-devel libSM-devel libXrender-devel \
            libXext-devel libXrandr-devel libXcomposite-devel \
            libXdamage-devel libxkbcommon-devel atk-devel \
            at-spi2-atk cups-devel libdrm dbus-1 fontconfig \
            freetype pixman libxcb make gcc gcc-c++
    elif [ "$DETECTED_PKG_MGR" = "apk" ]; then
        apk add --no-cache \
            python3 py3-pip \
            mesa-gl libglvnd glib libsm libxrender libxext \
            libxrandr libxcomposite libxdamage libxkbcommon \
            atk at-spi2-cups fontconfig freetype pixman \
            libxcb build-base
    fi
fi

# Create virtual environment
echo "[4/6] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Upgrade pip
echo "[5/6] Installing Python dependencies..."
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
echo "[6/6] Building Linux binary..."
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
