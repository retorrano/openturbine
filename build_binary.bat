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
echo [1/6] Checking Python installation...
where python >nul 2>&1
if errorlevel 1 (
    where python3 >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ERROR: Python not found!
        echo.
        echo Please install Python 3.9+ from: https://www.python.org/downloads/
        echo.
        echo During installation, make sure to:
        echo   1. Check "Add Python to PATH"
        echo   2. Check "Install pip"
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

:: Check for pip
echo [2/6] Checking pip...
%PYTHON% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip not found!
    echo Please reinstall Python with pip enabled.
    pause
    exit /b 1
)
echo.

:: Create virtual environment
echo [3/6] Setting up Python virtual environment...
if not exist "venv" (
    %PYTHON% -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

:: Upgrade pip
echo [4/6] Installing Python dependencies...
python -m pip install --upgrade pip
echo.

:: Install all required packages
echo [5/6] Installing required packages (this may take a while)...
pip install numpy scipy matplotlib pandas pyqtgraph PySide6 vtk pyvista pyinstaller
echo.

:: Install the package in editable mode
pip install -e .
echo.

:: Build the binary
echo [6/6] Building Windows binary...
if not exist "dist" mkdir dist

pyinstaller --onefile --windowed ^
    --name "openturbine-%VERSION%-windows.exe" ^
    --add-data "configs;openturbine/configs" ^
    --distpath dist ^
    src\openturbine\ui\main_window.py

echo.
echo ============================================
echo Build complete!
echo ============================================
echo Output: dist\openturbine-%VERSION%-windows.exe
dir dist\openturbine-%VERSION%-windows.exe
echo.
echo Note: On first run, Windows SmartScreen may show a warning.
echo Click "More info" and "Run anyway" to proceed.
echo.
echo To create an installer, consider using:
echo   - NSIS: https://nsis.sourceforge.io/
echo   - Inno Setup: https://jrsoftware.org/isinfo.php
echo.
pause
