# Auto Edit - Complete Installation Guide

This guide covers installation on Windows, macOS, and Linux with troubleshooting tips for common issues.

## Table of Contents
- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation by Platform](#installation-by-platform)
- [Installation Options](#installation-options)
- [Troubleshooting](#troubleshooting)
- [Manual Installation](#manual-installation)

---

## Quick Start

### Windows (Easiest)
1. Install **Python 3.8+** from https://python.org
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation!
2. Double-click `INSTALL.bat`
3. Wait 5-10 minutes
4. Run `run_gui.bat` to start!

### macOS / Linux
1. Ensure Python 3.8+ is installed: `python3 --version`
2. Run: `./install.sh` (or `bash install.sh`)
3. Follow the prompts
4. Run: `source venv/bin/activate && python auto_edit_gui.py`

---

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher (3.10 or 3.11 recommended)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 10GB free (5GB for installation, 5GB for processing)
- **FFmpeg**: Required for video processing

### Recommended for Better Performance
- **RAM**: 16GB+ for large videos
- **GPU**: NVIDIA/AMD/Intel GPU for faster encoding
- **SSD**: For faster video processing
- **Internet**: Stable connection for dependency download

### Supported Platforms
- ✅ Windows 10/11 (64-bit)
- ✅ macOS 10.15+ (Catalina or newer)
- ✅ Linux (Ubuntu 20.04+, Fedora 35+, Arch, etc.)
- ✅ WSL2 (Windows Subsystem for Linux)

---

## Installation by Platform

### Windows Installation

#### Method 1: One-Click Installer (Recommended)

1. **Install Python 3.8+**
   - Download from: https://www.python.org/downloads/
   - **CRITICAL**: Check "Add Python to PATH" during installation
   - Verify: Open Command Prompt and run `python --version`

2. **Run Installer**
   - Double-click `INSTALL.bat`
   - Choose installation type:
     - **Full**: Includes ML features (~2GB download, 10-15 mins)
     - **Minimal**: Faster, smaller, recommended for most (~1GB, 5-8 mins)

3. **Verify Installation**
   - The installer will automatically run system checks
   - If all checks pass, you're ready to go!

4. **Launch Auto Edit**
   - Double-click `run_gui.bat` (GUI mode)
   - OR double-click `run_auto_edit.bat` (CLI mode)

#### Method 2: Manual Install

```batch
# Check Python version
python --version

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies (choose one)
pip install -r requirements.txt          # Full install
pip install -r requirements-minimal.txt  # Minimal install

# Create directories
mkdir input output temp models memes sounds music images

# Run system check
python check_system.py

# Launch GUI
python auto_edit_gui.py
```

---

### macOS Installation

#### Method 1: Installation Script (Recommended)

1. **Install Homebrew** (if not already installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python and FFmpeg**
   ```bash
   brew install python@3.11 ffmpeg
   ```

3. **Run Installer**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. **Launch Auto Edit**
   ```bash
   source venv/bin/activate
   python auto_edit_gui.py
   ```

#### Method 2: Manual Install

```bash
# Verify Python 3.8+
python3 --version

# Install FFmpeg
brew install ffmpeg

# Clone or download Auto Edit
# cd to the Auto Edit directory

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies (choose one)
pip install -r requirements.txt          # Full
pip install -r requirements-minimal.txt  # Minimal

# Create directories
mkdir -p input output temp models memes sounds music images

# Run system check
python check_system.py

# Launch GUI
python auto_edit_gui.py
```

---

### Linux Installation

#### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg

# Run installer
chmod +x install.sh
./install.sh

# Or manual installation
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-minimal.txt
python check_system.py
python auto_edit_gui.py
```

#### Fedora

```bash
# Install system dependencies
sudo dnf install -y python3 python3-pip ffmpeg

# Run installer
chmod +x install.sh
./install.sh
```

#### Arch Linux

```bash
# Install system dependencies
sudo pacman -S python python-pip ffmpeg

# Run installer
chmod +x install.sh
./install.sh
```

---

## Installation Options

### Full vs Minimal Installation

#### Full Installation
- **Size**: ~2GB download
- **Time**: 10-15 minutes
- **Includes**: All features including ML/style learning (Phase 3+)
- **Requirements**: More disk space and RAM
- **Install**: `pip install -r requirements.txt`

#### Minimal Installation (Recommended)
- **Size**: ~1GB download
- **Time**: 5-8 minutes
- **Includes**: All basic video editing features
- **Excludes**: PyTorch, transformers, advanced ML features
- **Install**: `pip install -r requirements-minimal.txt`

**Which should you choose?**
- Choose **Minimal** if:
  - You want faster installation
  - You have limited disk space
  - You only need basic highlight creation
  - You're testing Auto Edit

- Choose **Full** if:
  - You want style learning features (Phase 3)
  - You have plenty of disk space and time
  - You're a developer/advanced user

You can always upgrade later: `pip install -r requirements.txt`

---

## Troubleshooting

### Common Issues

#### "Python is not recognized"
**Problem**: Python not in PATH
**Solution**:
- Windows: Reinstall Python, check "Add Python to PATH"
- Mac/Linux: Use `python3` instead of `python`

#### "FFmpeg is not installed"
**Problem**: FFmpeg not found
**Solution**:
- Windows: Run `install_ffmpeg.bat` or download from https://www.gyan.dev/ffmpeg/builds/
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg` (Ubuntu/Debian)

#### "pip install" fails
**Problem**: Dependency installation errors
**Solution**:
- Upgrade pip: `python -m pip install --upgrade pip`
- Try minimal install: `pip install -r requirements-minimal.txt`
- Check internet connection
- Disable antivirus temporarily
- Check disk space: `python check_system.py`

#### "No module named 'cv2'" or similar
**Problem**: Packages not installed in virtual environment
**Solution**:
- Activate venv first:
  - Windows: `venv\Scripts\activate.bat`
  - Mac/Linux: `source venv/bin/activate`
- Then install: `pip install -r requirements.txt`

#### Installation is very slow
**Problem**: Large downloads (especially PyTorch)
**Solution**:
- Use minimal install: `pip install -r requirements-minimal.txt`
- Check internet speed
- Be patient (PyTorch is 700MB+)

#### "Permission denied" errors (Linux/Mac)
**Problem**: Script not executable
**Solution**:
```bash
chmod +x install.sh check_system.py
```

#### Python 3.12+ compatibility issues
**Problem**: Some packages not yet compatible with very new Python
**Solution**:
- Use Python 3.10 or 3.11 instead (most stable)
- Create venv with specific version: `python3.11 -m venv venv`

### System Check Tool

Run the system checker to diagnose issues:

```bash
# Windows
python check_system.py

# Mac/Linux
python3 check_system.py
```

This will check:
- Python version
- pip installation
- FFmpeg installation
- Disk space
- Installed dependencies
- GPU encoders
- Optional features

---

## Manual Installation

If automated installers don't work, follow these steps:

### 1. Install System Dependencies

#### Windows
- Python 3.8+: https://www.python.org/downloads/
- FFmpeg: https://www.gyan.dev/ffmpeg/builds/

#### macOS
```bash
brew install python@3.11 ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# Windows:
venv\Scripts\activate.bat
# Mac/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Python Packages

```bash
# Option 1: Full installation
pip install -r requirements.txt

# Option 2: Minimal installation (faster)
pip install -r requirements-minimal.txt

# Option 3: Install from setup.py
pip install -e .
```

### 4. Create Directories

```bash
mkdir -p input output temp models training_data memes sounds music images
```

### 5. Verify Installation

```bash
python check_system.py
```

### 6. Run Auto Edit

```bash
# GUI mode
python auto_edit_gui.py

# CLI mode
python auto_edit.py --help
```

---

## Post-Installation

### Verify Everything Works

1. **Check system**:
   ```bash
   python check_system.py
   ```

2. **Test with small video**:
   ```bash
   python auto_edit.py edit test_video.mp4 --preview
   ```

3. **Launch GUI**:
   ```bash
   python auto_edit_gui.py
   ```

### Optional: Create Desktop Shortcuts

#### Windows
- Right-click `run_gui.bat` → Send to → Desktop (create shortcut)

#### macOS
- Create Automator Application:
  1. Open Automator
  2. New → Application
  3. Add "Run Shell Script"
  4. Script: `cd /path/to/auto-edit && source venv/bin/activate && python auto_edit_gui.py`
  5. Save as "Auto Edit.app"

#### Linux
Create `auto-edit.desktop`:
```ini
[Desktop Entry]
Name=Auto Edit
Exec=/path/to/auto-edit/venv/bin/python /path/to/auto-edit/auto_edit_gui.py
Icon=/path/to/auto-edit/icon.png
Type=Application
Categories=AudioVideo;
```

---

## Getting Help

If you're still having issues:

1. **Run system check**: `python check_system.py`
2. **Check README.md** for documentation
3. **Check SECURITY.md** for security-related issues
4. **Open an issue** on GitHub with:
   - Your OS and Python version
   - Output of `python check_system.py`
   - Error messages
   - What you've tried

---

## Next Steps

After successful installation:

1. **Read the documentation**: See `README.md`
2. **Configure settings**: Edit `config.yaml`
3. **Add assets**: Put memes/sounds/music in respective folders
4. **Process your first video**: Use the GUI or CLI
5. **Enjoy your highlights!** 🎉

---

## Installation Summary

### Quick Reference

| Platform | Command | Time |
|----------|---------|------|
| Windows | Double-click `INSTALL.bat` | 5-10 min |
| macOS | `./install.sh` | 5-10 min |
| Linux | `./install.sh` | 5-10 min |
| Manual | See [Manual Installation](#manual-installation) | 10-15 min |

### File Sizes

| Install Type | Download Size | Disk Space |
|--------------|---------------|------------|
| Minimal | ~1GB | ~3GB |
| Full | ~2GB | ~5GB |

### Support Matrix

| Python Version | Status |
|----------------|--------|
| 3.7 and below | ❌ Not supported |
| 3.8 | ✅ Supported |
| 3.9 | ✅ Supported |
| 3.10 | ✅ Recommended |
| 3.11 | ✅ Recommended |
| 3.12+ | ⚠️ May have issues |

---

Happy Editing! 🎬
