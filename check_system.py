#!/usr/bin/env python3
"""
System Dependency Checker for Auto Edit
Validates system requirements before installation/runtime
"""

import sys
import subprocess
import platform
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{BLUE}{BOLD}{text:^60}{RESET}")
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ {text}{RESET}")


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Python Version Check")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print(f"Python version: {version_str}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required, found {version_str}")
        return False

    if version.major == 3 and version.minor >= 12:
        print_warning(f"Python {version_str} is very new - some packages may not be compatible yet")
        print_info("Consider using Python 3.11 or 3.10 for best compatibility")
    else:
        print_success(f"Python {version_str} is compatible!")

    return True


def check_pip():
    """Check if pip is available and up to date"""
    print_header("pip (Package Manager) Check")

    try:
        import pip
        pip_version = pip.__version__
        print(f"pip version: {pip_version}")
        print_success("pip is installed!")

        # Check if pip is reasonably recent
        major_version = int(pip_version.split('.')[0])
        if major_version < 21:
            print_warning("pip version is old, consider upgrading: python -m pip install --upgrade pip")

        return True
    except ImportError:
        print_error("pip is not installed!")
        print_info("Install pip: python -m ensurepip --upgrade")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print_header("FFmpeg Check")

    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            # Extract version from output
            first_line = result.stdout.split('\n')[0]
            print(f"FFmpeg: {first_line}")
            print_success("FFmpeg is installed!")

            # Check for hardware encoders
            print("\nChecking for GPU encoders...")
            encoders_result = subprocess.run(
                ['ffmpeg', '-hide_banner', '-encoders'],
                capture_output=True,
                text=True,
                timeout=5
            )

            has_nvidia = 'h264_nvenc' in encoders_result.stdout
            has_amd = 'h264_amf' in encoders_result.stdout
            has_intel = 'h264_qsv' in encoders_result.stdout

            if has_nvidia:
                print_success("NVIDIA GPU encoder (h264_nvenc) available")
            if has_amd:
                print_success("AMD GPU encoder (h264_amf) available")
            if has_intel:
                print_success("Intel GPU encoder (h264_qsv) available")

            if not (has_nvidia or has_amd or has_intel):
                print_info("No GPU encoders found (CPU encoding will be used)")

            return True
        else:
            print_error("FFmpeg command failed")
            return False

    except FileNotFoundError:
        print_error("FFmpeg is not installed or not in PATH!")
        print_info("\nInstallation instructions:")

        system = platform.system()
        if system == "Windows":
            print("  1. Download from: https://www.gyan.dev/ffmpeg/builds/")
            print("  2. Extract to C:\\ffmpeg")
            print("  3. Add C:\\ffmpeg\\bin to PATH")
            print("  OR run: install_ffmpeg.bat")
        elif system == "Darwin":  # macOS
            print("  Install with Homebrew: brew install ffmpeg")
        else:  # Linux
            print("  Ubuntu/Debian: sudo apt install ffmpeg")
            print("  Fedora: sudo dnf install ffmpeg")
            print("  Arch: sudo pacman -S ffmpeg")

        return False
    except subprocess.TimeoutExpired:
        print_error("FFmpeg check timed out")
        return False


def check_disk_space():
    """Check available disk space"""
    print_header("Disk Space Check")

    try:
        import shutil
        stat = shutil.disk_usage(Path.cwd())

        free_gb = stat.free / (1024 ** 3)
        total_gb = stat.total / (1024 ** 3)
        used_percent = (stat.used / stat.total) * 100

        print(f"Free space: {free_gb:.1f} GB / {total_gb:.1f} GB ({100-used_percent:.1f}% free)")

        if free_gb < 5:
            print_error("Less than 5GB free - you may run out of space!")
            print_info("Auto Edit needs space for: dependencies (~2GB), temp files, output videos")
            return False
        elif free_gb < 10:
            print_warning("Less than 10GB free - consider freeing up space")
        else:
            print_success("Sufficient disk space available")

        return True
    except Exception as e:
        print_warning(f"Could not check disk space: {e}")
        return True


def check_dependencies():
    """Check if Python packages are installed"""
    print_header("Python Dependencies Check")

    required_packages = [
        ('numpy', 'numpy'),
        ('cv2', 'opencv-python'),
        ('librosa', 'librosa'),
        ('yaml', 'pyyaml'),
        ('click', 'click'),
        ('PIL', 'pillow'),
    ]

    all_installed = True
    installed_count = 0

    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print_success(f"{package_name}")
            installed_count += 1
        except ImportError:
            print_error(f"{package_name} - NOT INSTALLED")
            all_installed = False

    print(f"\n{installed_count}/{len(required_packages)} core packages installed")

    if not all_installed:
        print_info("\nInstall missing packages:")
        print("  pip install -r requirements.txt")
        print("  OR for minimal install: pip install -r requirements-minimal.txt")

    return all_installed


def check_optional_features():
    """Check optional dependencies"""
    print_header("Optional Features Check")

    # Check for ML packages
    try:
        import torch
        print_success(f"PyTorch (for ML features) - version {torch.__version__}")
    except ImportError:
        print_info("PyTorch not installed - Style learning (Phase 3) not available")

    try:
        import pandas
        print_success(f"Pandas (for data export) - version {pandas.__version__}")
    except ImportError:
        print_info("Pandas not installed - Advanced data export not available")

    # Check for GPU (PyTorch CUDA)
    try:
        import torch
        if torch.cuda.is_available():
            print_success(f"CUDA available - GPU: {torch.cuda.get_device_name(0)}")
        else:
            print_info("CUDA not available - using CPU for ML (if enabled)")
    except (ImportError, Exception):
        pass


def main():
    """Run all system checks"""
    print(f"\n{BOLD}Auto Edit - System Checker{RESET}")
    print("Validating your system for Auto Edit installation/usage\n")

    checks = [
        ("Python Version", check_python_version),
        ("pip", check_pip),
        ("FFmpeg", check_ffmpeg),
        ("Disk Space", check_disk_space),
        ("Dependencies", check_dependencies),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Check failed with exception: {e}")
            results[name] = False

    # Optional checks (don't affect pass/fail)
    try:
        check_optional_features()
    except Exception as e:
        print_warning(f"Optional features check failed: {e}")

    # Summary
    print_header("Summary")

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {name:.<30} {status}")

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print_success("\n✓ Your system is ready for Auto Edit!")
        return 0
    else:
        print_error("\n✗ Some requirements are missing")
        print_info("Please resolve the issues above before using Auto Edit")
        return 1


if __name__ == "__main__":
    sys.exit(main())
