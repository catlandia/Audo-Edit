@echo off
REM Auto Edit - Windows Setup Script
REM Double-click this file to set up Auto Edit automatically

echo ========================================
echo   Auto Edit - Windows Setup
echo ========================================
echo.

REM Check Python installation
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo Python found!
echo.

REM Check FFmpeg installation
echo [2/4] Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg not found!
    echo.
    echo FFmpeg is required for Auto Edit to work.
    echo.
    echo Installation steps:
    echo 1. Download from: https://www.gyan.dev/ffmpeg/builds/
    echo 2. Extract to C:\ffmpeg
    echo 3. Add C:\ffmpeg\bin to System PATH
    echo 4. Restart this terminal and run setup again
    echo.
    echo See WINDOWS_SETUP.md for detailed instructions.
    echo.
    pause
    exit /b 1
)

echo FFmpeg found!
echo.

REM Create virtual environment
echo [3/4] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created!
)
echo.

REM Activate virtual environment
echo [4/4] Installing dependencies...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Auto Edit is ready to use!
echo.
echo Next steps:
echo   1. Double-click 'run_auto_edit.bat' to process videos
echo   OR
echo   2. Open PowerShell and run:
echo      venv\Scripts\activate
echo      python auto_edit.py edit "C:\path\to\video.mp4"
echo.
echo See WINDOWS_SETUP.md for detailed usage instructions.
echo.
pause
