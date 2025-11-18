# Auto Edit - Automatic FFmpeg Installer for Windows
# This script automatically downloads and installs FFmpeg

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Auto Edit - FFmpeg Auto-Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if FFmpeg is already installed
Write-Host "[1/4] Checking for existing FFmpeg installation..." -ForegroundColor Yellow
$ffmpegExists = Get-Command ffmpeg -ErrorAction SilentlyContinue

if ($ffmpegExists) {
    Write-Host "FFmpeg is already installed!" -ForegroundColor Green
    ffmpeg -version | Select-Object -First 1
    Write-Host ""
    Write-Host "Installation complete! You can close this window." -ForegroundColor Green
    pause
    exit 0
}

Write-Host "FFmpeg not found. Installing automatically..." -ForegroundColor Yellow
Write-Host ""

# Create installation directory
$installDir = "C:\ffmpeg"
Write-Host "[2/4] Creating installation directory: $installDir" -ForegroundColor Yellow

if (!(Test-Path $installDir)) {
    New-Item -Path $installDir -ItemType Directory -Force | Out-Null
    Write-Host "Directory created!" -ForegroundColor Green
} else {
    Write-Host "Directory already exists!" -ForegroundColor Green
}
Write-Host ""

# Download FFmpeg
Write-Host "[3/4] Downloading FFmpeg..." -ForegroundColor Yellow
Write-Host "This may take a few minutes depending on your internet speed..." -ForegroundColor Gray

$downloadUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zipFile = "$env:TEMP\ffmpeg.zip"

try {
    # Download with progress
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    $ProgressPreference = 'Continue'
    Write-Host "Download complete!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to download FFmpeg!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual installation:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor Yellow
    Write-Host "2. Extract to C:\ffmpeg" -ForegroundColor Yellow
    Write-Host "3. Run this script again" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""

# Extract FFmpeg
Write-Host "[4/4] Extracting FFmpeg..." -ForegroundColor Yellow

try {
    # Extract zip
    Expand-Archive -Path $zipFile -DestinationPath "$env:TEMP\ffmpeg_extract" -Force

    # Find the extracted folder (it has a version number)
    $extractedFolder = Get-ChildItem "$env:TEMP\ffmpeg_extract" | Select-Object -First 1

    # Copy bin folder contents to C:\ffmpeg\bin
    $binSource = Join-Path $extractedFolder.FullName "bin"
    $binDest = Join-Path $installDir "bin"

    if (!(Test-Path $binDest)) {
        New-Item -Path $binDest -ItemType Directory -Force | Out-Null
    }

    Copy-Item -Path "$binSource\*" -Destination $binDest -Force -Recurse

    # Cleanup
    Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:TEMP\ffmpeg_extract" -Recurse -Force -ErrorAction SilentlyContinue

    Write-Host "Extraction complete!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to extract FFmpeg!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""

# Add to PATH
Write-Host "[5/5] Adding FFmpeg to system PATH..." -ForegroundColor Yellow

try {
    $binPath = Join-Path $installDir "bin"

    # Get current PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

    # Check if already in PATH
    if ($currentPath -notlike "*$binPath*") {
        $newPath = $currentPath + ";" + $binPath
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")

        # Also update current session
        $env:Path = $env:Path + ";" + $binPath

        Write-Host "FFmpeg added to PATH!" -ForegroundColor Green
    } else {
        Write-Host "FFmpeg already in PATH!" -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING: Could not automatically add to PATH" -ForegroundColor Yellow
    Write-Host "You may need to add C:\ffmpeg\bin to PATH manually" -ForegroundColor Yellow
}

Write-Host ""

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")

Start-Sleep -Seconds 2

$ffmpegTest = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpegTest) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SUCCESS! FFmpeg installed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    ffmpeg -version | Select-Object -First 1
    Write-Host ""
    Write-Host "FFmpeg is ready to use!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Installation complete, but FFmpeg not found in PATH yet." -ForegroundColor Yellow
    Write-Host "You may need to restart your terminal/PowerShell." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "You can close this window now." -ForegroundColor Cyan
pause
