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

# Run the appropriate build script
case "$OS_TYPE" in
    linux)
        echo "Running Linux build..."
        ./build_linux.sh "$VERSION"
        ;;
    linux-wsl)
        echo "Running Windows (WSL) build..."
        ./build_windows.sh "$VERSION"
        ;;
    windows)
        echo "Running Windows build..."
        ./build_windows.sh "$VERSION"
        ;;
    macos)
        echo "Running macOS build..."
        ./build_macos.sh "$VERSION"
        ;;
esac
