@echo off
:: Build script for OpenTurbine on Windows
:: Usage: build_binary.bat [version]

setlocal enabledelayedexpansion

set "VERSION=%1"
if "%VERSION%"=="" set "VERSION=0.1.0"

echo ============================================
echo Building OpenTurbine v%VERSION% for Windows
echo ============================================
echo.

:: Check for Python
echo [1/8] Checking Python installation...
where python >nul 2>&1
if errorlevel 1 (
    where python3 >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ERROR: Python not found!
        echo.
        echo Please install Python 3.9+ from: https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    ) else (
        set "PYTHON=python3"
    )
) else (
    set "PYTHON=python"
)

%PYTHON% --version
echo.

:: Check for CMake
echo [2/8] Checking CMake installation...
where cmake >nul 2>&1
if errorlevel 1 (
    echo ERROR: CMake not found!
    echo Please install CMake from: https://cmake.org/download/
    pause
    exit /b 1
)
cmake --version
echo.

:: Create virtual environment
echo [3/8] Setting up Python virtual environment...
if not exist "venv" (
    %PYTHON% -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

:: Upgrade pip and install dependencies
echo [4/8] Installing Python dependencies...
python -m pip install --upgrade pip
pip install pybind11 numpy scipy matplotlib pandas pyqtgraph PySide6 vtk pyvista pyinstaller
echo.

:: Download and extract Eigen
echo [5/8] Setting up Eigen dependency...
if not exist "eigen-3.4.0" (
    if not exist "eigen.zip" (
        echo Downloading Eigen 3.4.0...
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.zip' -OutFile 'eigen.zip'"
    )
    echo Extracting Eigen...
    powershell -Command "Expand-Archive -Path 'eigen.zip' -DestinationPath '.' -Force"
)

:: Find Eigen directory
for /d %%i in (eigen-3.4.0*) do set EIGEN_ROOT=%CD%\%%i
echo EIGEN_ROOT=%EIGEN_ROOT%
echo.

:: Build C++ extensions with CMake
echo [6/8] Building C++ extensions with CMake...
if not exist "build" mkdir build
cd build

:: Get pybind11 CMake directory and Python executable path
for /f "tokens=*" %%i in ('python -c "import pybind11; print(pybind11.get_cmake_dir().replace('\\', '/'))"') do set PYBIND11_DIR=%%i
for /f "tokens=*" %%i in ('where python') do (
    set "PYTHON_EXE=%%i"
    goto :found_python
)
:found_python

echo Using PYBIND11_DIR: %PYBIND11_DIR%
echo Using PYTHON_EXE: %PYTHON_EXE%

cmake .. -G "Visual Studio 17 2022" -A x64 ^
    -Dpybind11_DIR="%PYBIND11_DIR%" ^
    -DPython3_EXECUTABLE="%PYTHON_EXE%" ^
    -DEIGEN3_INCLUDE_DIR="%EIGEN_ROOT%"

if errorlevel 1 (
    echo.
    echo ERROR: CMake configuration failed!
    cd ..
    pause
    exit /b 1
)

cmake --build . --config Release

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    cd ..
    pause
    exit /b 1
)

cd ..
echo.

:: Install the package in editable mode
echo [7/8] Installing package...
pip install -e .
echo.

:: Build the binary with PyInstaller
echo [8/8] Building Windows binary with PyInstaller...
if not exist "dist" mkdir dist

:: Note: We add the core DLL and the pybind .pyd module
:: The .pyd filename varies with Python version, so we use a wildcard
pyinstaller --onefile --windowed ^
    --name "OpenTurbine" ^
    --add-binary "build\bin\Release\openturbine_core.dll;." ^
    --add-binary "build\bin\Release\openturbine\openturbine_pybind.cp*;openturbine" ^
    --add-data "configs;configs" ^
    --distpath dist ^
    src\openturbine\ui\main_window.py

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build complete!
echo ============================================
echo Output: dist\OpenTurbine.exe
echo.
echo Note: On first run, Windows SmartScreen may show a warning.
echo Click "More info" and "Run anyway" to proceed.
echo.
pause
