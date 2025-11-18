@echo off
REM Auto Edit - Windows Launcher
REM Double-click this file to run Auto Edit with GUI prompts

echo ========================================
echo   Auto Edit - Highlight Video Creator
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   1. Open PowerShell in this folder
    echo   2. Run: python -m venv venv
    echo   3. Run: venv\Scripts\activate
    echo   4. Run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if activated successfully
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated!
echo.

REM Prompt for video file
set /p VIDEO_PATH="Enter the full path to your video file: "

REM Check if path was provided
if "%VIDEO_PATH%"=="" (
    echo ERROR: No video path provided
    pause
    exit /b 1
)

REM Remove quotes if user included them
set VIDEO_PATH=%VIDEO_PATH:"=%

REM Check if file exists
if not exist "%VIDEO_PATH%" (
    echo ERROR: Video file not found: %VIDEO_PATH%
    pause
    exit /b 1
)

echo.
echo Video file: %VIDEO_PATH%
echo.

REM Prompt for target duration
set /p DURATION="Target duration in minutes (default: 20): "
if "%DURATION%"=="" set DURATION=20

REM Prompt for verbose output
set /p VERBOSE="Verbose output? (y/n, default: n): "
if /i "%VERBOSE%"=="y" (
    set VERBOSE_FLAG=-v
) else (
    set VERBOSE_FLAG=
)

echo.
echo ========================================
echo Starting Auto Edit...
echo ========================================
echo.

REM Run Auto Edit
python auto_edit.py edit "%VIDEO_PATH%" -d %DURATION% %VERBOSE_FLAG%

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Auto Edit failed!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Highlight video created!
echo ========================================
echo.
echo Check the 'output' folder for your video.
echo.

REM Open output folder
explorer output

pause
