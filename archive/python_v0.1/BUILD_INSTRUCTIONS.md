# Building OpenTurbine Binaries

## Quick Start

Choose the right script for your operating system:

| OS | Script | How to Run |
|----|--------|------------|
| **Windows** | `build_binary.bat` | Double-click or run in Command Prompt |
| **Linux** | `build_binary.sh` | `./build_binary.sh` in terminal |
| **macOS** | `build_binary.sh` | `./build_binary.sh` in terminal |
| **WSL/Linux** | `build_binary.sh` | `./build_binary.sh` in WSL terminal |

## Windows

Double-click `build_binary.bat` or run in Command Prompt:
```
build_binary.bat 0.1.0
```

Or in PowerShell:
```
.\build_binary.bat 0.1.0
```

## Linux

```bash
chmod +x build_binary.sh
./build_binary.sh 0.1.0
```

Or specify your distribution's package manager (auto-detected):
- Fedora/RHEL/CentOS: dnf
- Debian/Ubuntu: apt-get
- Arch Linux: pacman
- openSUSE: zypper
- Alpine: apk

## macOS

```bash
chmod +x build_binary.sh
./build_binary.sh 0.1.0
```

Requires Homebrew. If not installed, the script will prompt you.

## All Platforms (Auto-Detect)

```bash
./build_binary.sh 0.1.0
```

The script auto-detects your OS and runs the appropriate build.

## Build Outputs

After building, binaries are in the `dist/` folder:

| Platform | Filename |
|----------|----------|
| Linux | `openturbine-X.X.X-linux` |
| Windows | `openturbine-X.X.X-windows.exe` |
| macOS | `openturbine-X.X.X-macos` |

## Requirements

- Python 3.9 or higher
- pip
- Internet connection (to download dependencies)

The scripts will install all required Python packages automatically.
