@echo off
REM Auto Edit GUI Launcher
REM Double-click this file to start the graphical interface

echo ========================================
echo   Auto Edit - Starting GUI...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run setup_windows.bat first to install Auto Edit.
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

REM Start GUI
echo Launching Auto Edit GUI...
echo.
python auto_edit_gui.py

REM If GUI exits with error
if errorlevel 1 (
    echo.
    echo GUI closed with an error.
    pause
)
