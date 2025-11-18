@echo off
REM FFmpeg Automatic Installer
REM Runs the PowerShell installation script

echo ========================================
echo   FFmpeg Automatic Installer
echo ========================================
echo.
echo This will automatically download and install FFmpeg.
echo.
echo Press any key to continue...
pause >nul

REM Run PowerShell script with execution policy bypass
powershell.exe -ExecutionPolicy Bypass -File "%~dp0install_ffmpeg.ps1"

echo.
echo Installation script completed.
pause
