#!/bin/bash
# Build script for OpenTurbine - Auto-detects OS
# Usage: ./build_binary.sh [version]

set -e

VERSION=${1:-"0.1.0"}

echo "============================================"
echo "OpenTurbine Build Script"
echo "============================================"
echo "Version: $VERSION"
echo ""

# Detect operating system
OS_TYPE=""
case "$(uname -s)" in
    Linux*)
        if grep -qEi "Microsoft|WSL" /proc/version 2>/dev/null; then
            OS_TYPE="linux-wsl"
            echo "Detected: Windows Subsystem for Linux (WSL)"
        else
            OS_TYPE="linux"
            echo "Detected: Linux"
        fi
        ;;
    Darwin*)
        OS_TYPE="macos"
        echo "Detected: macOS"
        ;;
    CYGWIN*|MINGW*|MSYS*)
        OS_TYPE="windows"
        echo "Detected: Windows (Git Bash/MinGW)"
        ;;
    *)
        echo "Unknown OS: $(uname -s)"
        exit 1
        ;;
esac

echo ""

# Detect Linux distribution and set package manager
detect_linux_pkg_manager() {
    if command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v apt-get &> /dev/null; then
        echo "apt-get"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    elif command -v zypper &> /dev/null; then
        echo "zypper"
    elif command -v apk &> /dev/null; then
        echo "apk"
    else
        echo ""
    fi
}

# Linux build function
build_linux() {
    echo "Building for Linux..."
    
    PKG_MGR=$(detect_linux_pkg_manager)
    echo "Package manager: $PKG_MGR"
    
    # Install system dependencies
    echo "[1/6] Installing system dependencies..."
    if [ "$PKG_MGR" = "dnf" ]; then
        sudo dnf install -y @development-tools
        sudo dnf install -y mesa-libGL glib2 libSM libXrender libXext libXrandr libXcomposite libXdamage libxkbcommon atk at-spi2-atk cups-libs libdrm dbus-libs at-spi2-core fontconfig freetype pixman libxcb gcc gcc-c++ python3 python3-pip python3-virtualenv
    elif [ "$PKG_MGR" = "apt-get" ]; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 libgomp1 libxrandr2 libxcomposite1 libxdamage1 libxkbcommon0 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libdbus-1-3 libatspi2.0-0 libfontconfig1 libfreetype6 libpixman-1-0 libxcb-shm0 libxcb-render0 libxcb-render-util0 build-essential
    elif [ "$PKG_MGR" = "pacman" ]; then
        sudo pacman -S --noconfirm python python-pip python-virtualenv mesa libglvnd glib2 libsm libxrender libxext libxrandr libxcomposite libxdamage libxkbcommon atk at-spi2-atk cups libdrm dbus fontconfig freetype pixman libxcb base-devel
    elif [ "$PKG_MGR" = "zypper" ]; then
        sudo zypper install -y python3 python3-pip python3-virtualenv Mesa-libGL1 glib2-devel libSM-devel libXrender-devel libXext-devel libXrandr-devel libXcomposite-devel libXdamage-devel libxkbcommon-devel atk-devel at-spi2-atk cups-devel libdrm dbus-1 fontconfig freetype pixman libxcb make gcc gcc-c++
    elif [ "$PKG_MGR" = "apk" ]; then
        apk add --no-cache python3 py3-pip mesa-gl libglvnd glib libsm libxrender libxext libxrandr libxcomposite libxdamage libxkbcommon atk at-spi2-cups fontconfig freetype pixman libxcb build-base
    else
        echo "Warning: No supported package manager found. Please install dependencies manually."
    fi
    
    # Create virtual environment
    echo "[2/6] Setting up Python virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    # Install Python dependencies
    echo "[3/6] Installing Python dependencies..."
    pip install --upgrade pip
    pip install numpy scipy matplotlib pandas pyqtgraph PySide6 vtk pyvista pyinstaller
    pip install -e .
    
    # Build binary
    echo "[4/6] Building Linux binary..."
    mkdir -p dist
    pyinstaller --onefile --windowed \
        --name "openturbine-${VERSION}-linux" \
        --add-data "configs:openturbine/configs" \
        --distpath dist \
        src/openturbine/ui/main_window.py
    
    echo "[5/6] Making executable..."
    chmod +x "dist/openturbine-${VERSION}-linux"
    
    echo "[6/6] Done!"
    echo ""
    echo "============================================"
    echo "Build complete!"
    echo "============================================"
    ls -lh dist/
    echo ""
    echo "To run: ./dist/openturbine-${VERSION}-linux"
}

# macOS build function
build_macos() {
    echo "Building for macOS..."
    
    # Check for Homebrew
    echo "[1/6] Checking Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install dependencies
    echo "[2/6] Installing system dependencies..."
    brew install python@3.10 qt vtk autoconf automake libtool pkg-config
    
    # Set up Python
    echo "[3/6] Setting up Python..."
    PYTHON_CMD="python3"
    $PYTHON_CMD --version
    
    # Create virtual environment
    echo "[4/6] Creating virtual environment..."
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
    fi
    source venv/bin/activate
    
    # Install Python dependencies
    echo "[5/6] Installing Python dependencies..."
    pip install --upgrade pip
    pip install numpy scipy matplotlib pandas pyqtgraph PySide6 vtk pyvista pyinstaller
    pip install -e .
    
    # Build binary
    echo "[6/6] Building macOS binary..."
    mkdir -p dist
    pyinstaller --onefile --windowed \
        --name "openturbine-${VERSION}-macos" \
        --add-data "configs:openturbine/configs" \
        --distpath dist \
        src/openturbine/ui/main_window.py
    
    chmod +x "dist/openturbine-${VERSION}-macos"
    
    echo ""
    echo "============================================"
    echo "Build complete!"
    echo "============================================"
    ls -lh dist/
    echo ""
    echo "To run: ./dist/openturbine-${VERSION}-macos"
    echo ""
    echo "Note: You may need to allow the app in System Preferences > Security"
}

# Windows build function
build_windows() {
    echo "Building for Windows..."
    
    # Check for Python
    echo "[1/6] Checking Python..."
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        echo "ERROR: Python not found!"
        echo "Please install Python from: https://www.python.org/downloads/"
        exit 1
    fi
    
    PYTHON_CMD="python"
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    fi
    $PYTHON_CMD --version
    
    # Create virtual environment
    echo "[2/6] Creating virtual environment..."
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
    fi
    source venv/Scripts/activate
    
    # Install Python dependencies
    echo "[3/6] Installing Python dependencies..."
    pip install --upgrade pip
    pip install numpy scipy matplotlib pandas pyqtgraph PySide6 vtk pyvista pyinstaller
    pip install -e .
    
    # Build binary
    echo "[4/6] Building Windows binary..."
    mkdir -p dist
    pyinstaller --onefile --windowed \
        --name "openturbine-${VERSION}-windows.exe" \
        --add-data "configs;openturbine/configs" \
        --distpath dist \
        src/openturbine/ui/main_window.py
    
    echo "[5/6] Done!"
    echo ""
    echo "============================================"
    echo "Build complete!"
    echo "============================================"
    ls -lh dist/
    echo ""
    echo "To run: dist\\openturbine-${VERSION}-windows.exe"
}

# Run the appropriate build
case "$OS_TYPE" in
    linux)
        build_linux
        ;;
    linux-wsl)
        build_windows
        ;;
    windows)
        build_windows
        ;;
    macos)
        build_macos
        ;;
esac
