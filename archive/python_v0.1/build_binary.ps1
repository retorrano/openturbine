# Build script for OpenTurbine on Windows (PowerShell)
# Usage: .\build_binary.ps1 -Version "0.1.0"

param (
    [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Building OpenTurbine v$Version for Windows" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check for Python
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
$PythonExe = Get-Command python.exe, python3.exe -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source
if (-not $PythonExe) {
    Write-Error "Python not found! Please install Python 3.9+ and add it to your PATH."
}
& $PythonExe --version
Write-Host ""

# 2. Check for CMake
Write-Host "[2/8] Checking CMake installation..." -ForegroundColor Yellow
if (-not (Get-Command cmake.exe -ErrorAction SilentlyContinue)) {
    Write-Error "CMake not found! Please install CMake and add it to your PATH."
}
cmake --version
Write-Host ""

# 3. Setup Virtual Environment
Write-Host "[3/8] Setting up Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    & $PythonExe -m venv venv
}
$VenvPython = Join-Path (Get-Location) "venv\Scripts\python.exe"
$VenvPip = Join-Path (Get-Location) "venv\Scripts\pip.exe"
Write-Host "Using venv python: $VenvPython"
Write-Host ""

# 4. Install Dependencies
Write-Host "[4/8] Installing Python dependencies..." -ForegroundColor Yellow
& $VenvPython -m pip install --upgrade pip
& $VenvPip install pybind11 numpy scipy matplotlib pandas pyqtgraph PySide6 vtk pyvista pyinstaller
Write-Host ""

# 5. Download and Extract Eigen
Write-Host "[5/8] Setting up Eigen dependency..." -ForegroundColor Yellow
$EigenZip = "eigen.zip"
$EigenFolder = Get-ChildItem -Directory -Filter "eigen-3.4.0*" | Select-Object -First 1

if (-not $EigenFolder) {
    if (-not (Test-Path $EigenZip)) {
        Write-Host "Downloading Eigen 3.4.0..."
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri "https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.zip" -OutFile $EigenZip
    }
    Write-Host "Extracting Eigen..."
    Expand-Archive -Path $EigenZip -DestinationPath "." -Force
    $EigenFolder = Get-ChildItem -Directory -Filter "eigen-3.4.0*" | Select-Object -First 1
}
$EigenRoot = $EigenFolder.FullName
Write-Host "EIGEN_ROOT=$EigenRoot"
Write-Host ""

# 6. Build C++ extensions with CMake
Write-Host "[6/8] Building C++ extensions with CMake..." -ForegroundColor Yellow
if (-not (Test-Path "build")) { New-Item -ItemType Directory -Path "build" | Out-Null }
Push-Location "build"

# Get pybind11 CMake directory
$Pybind11Dir = & $VenvPython -c "import pybind11; print(pybind11.get_cmake_dir().replace('\\', '/'))"

cmake .. -G "Visual Studio 17 2022" -A x64 `
    -Dpybind11_DIR="$Pybind11Dir" `
    -DPython3_EXECUTABLE="$VenvPython" `
    -DEIGEN3_INCLUDE_DIR="$EigenRoot"

cmake --build . --config Release

Pop-Location
Write-Host ""

# 7. Install package
Write-Host "[7/8] Installing package..." -ForegroundColor Yellow
& $VenvPip install -e .
Write-Host ""

# 8. Build binary with PyInstaller
Write-Host "[8/8] Building Windows binary with PyInstaller..." -ForegroundColor Yellow
if (-not (Test-Path "dist")) { New-Item -ItemType Directory -Path "dist" | Out-Null }

$PyInstaller = Join-Path (Get-Location) "venv\Scripts\pyinstaller.exe"

& $PyInstaller --onefile --windowed `
    --name "OpenTurbine" `
    --add-binary "build\bin\Release\openturbine_core.dll;." `
    --add-binary "build\bin\Release\openturbine\openturbine_pybind.cp*;openturbine" `
    --add-data "configs;configs" `
    --distpath dist `
    src\openturbine\ui\main_window.py

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Build complete!" -ForegroundColor Green
Write-Host "Output: dist\OpenTurbine.exe" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
pause
