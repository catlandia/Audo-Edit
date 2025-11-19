@echo off
REM ============================================
REM Auto Edit - ONE-CLICK INSTALLER
REM ============================================
REM This script does EVERYTHING for you!
REM Just double-click and wait!
REM ============================================

color 0A
cls

echo.
echo  ========================================
echo   AUTO EDIT - ONE-CLICK INSTALLER
echo  ========================================
echo.
echo  This will automatically:
echo    1. Check Python installation
echo    2. Install FFmpeg (if needed)
echo    3. Create virtual environment
echo    4. Install all dependencies
echo.
echo  Sit back and relax! This takes 5-10 minutes.
echo.
echo  ========================================
echo.
pause

cls

REM ============================================
REM STEP 1: Check Python
REM ============================================
echo.
echo [STEP 1/4] Checking Python...
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Python is not installed!
    echo.
    echo  Please install Python first:
    echo    1. Go to: https://www.python.org/downloads/
    echo    2. Download Python 3.8 or higher
    echo    3. IMPORTANT: Check "Add Python to PATH" during install
    echo    4. Run this installer again
    echo.
    echo  Press any key to open Python download page...
    pause >nul
    start https://www.python.org/downloads/
    exit /b 1
)

python --version
echo.
echo  Python found! Continuing...
echo.
timeout /t 2 >nul

REM ============================================
REM STEP 2: Install FFmpeg
REM ============================================
cls
echo.
echo [STEP 2/4] Checking FFmpeg...
echo ========================================
echo.

ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo  FFmpeg not found. Installing automatically...
    echo.
    echo  This will download ~100MB. Please wait...
    echo.

    REM Run FFmpeg installer
    powershell.exe -ExecutionPolicy Bypass -File "%~dp0install_ffmpeg.ps1"

    if errorlevel 1 (
        color 0C
        echo.
        echo  ERROR: FFmpeg installation failed!
        echo.
        echo  Please install manually:
        echo    1. Download from: https://www.gyan.dev/ffmpeg/builds/
        echo    2. Extract to C:\ffmpeg
        echo    3. Add C:\ffmpeg\bin to PATH
        echo    4. Restart this installer
        echo.
        pause
        exit /b 1
    )
) else (
    ffmpeg -version | findstr "ffmpeg version"
    echo.
    echo  FFmpeg found! Continuing...
    echo.
    timeout /t 2 >nul
)

REM ============================================
REM STEP 3: Create Virtual Environment
REM ============================================
cls
echo.
echo [STEP 3/4] Setting up virtual environment...
echo ========================================
echo.

if exist "venv" (
    echo  Virtual environment already exists!
    echo  Skipping creation...
) else (
    echo  Creating virtual environment...
    python -m venv venv

    if errorlevel 1 (
        color 0C
        echo.
        echo  ERROR: Failed to create virtual environment!
        echo.
        pause
        exit /b 1
    )

    echo  Virtual environment created!
)

echo.
timeout /t 2 >nul

REM ============================================
REM STEP 4: Install Dependencies
REM ============================================
cls
echo.
echo [STEP 4/4] Installing Python packages...
echo ========================================
echo.
echo  This will take 5-10 minutes...
echo  Downloading and installing packages...
echo.

call venv\Scripts\activate.bat

if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Could not activate virtual environment!
    echo.
    pause
    exit /b 1
)

REM Upgrade pip first
echo  Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Choose installation type
echo.
echo  Choose installation type:
echo    1. FULL install (includes ML features, ~2GB download)
echo    2. MINIMAL install (faster, smaller, recommended for most users)
echo.
choice /C 12 /N /M "Enter choice (1 or 2): "
set INSTALL_TYPE=%ERRORLEVEL%

echo.
if %INSTALL_TYPE%==1 (
    echo  Installing FULL dependencies...
    echo  This will take 5-15 minutes depending on your internet speed
    echo.
    pip install -r requirements.txt
) else (
    echo  Installing MINIMAL dependencies...
    echo  This will take 3-8 minutes
    echo  Note: Style learning features won't be available
    echo.
    pip install -r requirements-minimal.txt
)

if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Failed to install dependencies!
    echo.
    echo  This might be due to:
    echo    - Slow internet connection
    echo    - Antivirus blocking downloads
    echo    - Insufficient disk space
    echo    - Python version incompatibility
    echo.
    echo  Try the other installation type or check:
    echo    python check_system.py
    echo.
    pause
    exit /b 1
)

REM ============================================
REM RUN SYSTEM CHECK
REM ============================================
echo.
echo  Running system check...
echo.
python check_system.py
echo.
pause

REM ============================================
REM SUCCESS!
REM ============================================
cls
color 0A

echo.
echo  ============================================
echo   INSTALLATION COMPLETE!
echo  ============================================
echo.
echo  Auto Edit is ready to use!
echo.
echo  ========================================
echo   HOW TO USE:
echo  ========================================
echo.
echo   EASIEST WAY (Recommended):
echo     Double-click: run_gui.bat
echo.
echo   QUICK WAY:
echo     Double-click: run_auto_edit.bat
echo.
echo   COMMAND LINE:
echo     1. Open PowerShell in this folder
echo     2. Run: venv\Scripts\activate
echo     3. Run: python auto_edit.py edit "video.mp4"
echo.
echo  ========================================
echo   NEXT STEPS:
echo  ========================================
echo.
echo   1. Double-click 'run_gui.bat' to start!
echo   2. Select your stream video
echo   3. Click "Start Processing"
echo   4. Wait for your highlight video!
echo.
echo  See README.md for full documentation
echo.
echo  ========================================
echo   TROUBLESHOOTING:
echo  ========================================
echo.
echo   If you have issues, run: python check_system.py
echo   This will check your system for problems
echo.
echo  ========================================
echo.
echo  Press any key to launch the GUI now...
pause >nul

REM Launch GUI
start "" "%~dp0run_gui.bat"

echo.
echo  GUI launched! This window can be closed.
echo.
timeout /t 3 >nul
exit
