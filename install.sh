#!/bin/bash
# ============================================
# Auto Edit - Installation Script (Linux/Mac)
# ============================================
# This script automatically sets up Auto Edit
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Print functions
print_header() {
    echo -e "\n${BLUE}${BOLD}========================================${NC}"
    echo -e "${BLUE}${BOLD}$1${NC}"
    echo -e "${BLUE}${BOLD}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$ID
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="mac"
        DISTRO="macos"
    else
        OS="unknown"
        DISTRO="unknown"
    fi
}

# Check Python version
check_python() {
    print_header "Checking Python Installation"

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed!"
        print_info "Install instructions:"

        if [[ "$OS" == "linux" ]]; then
            if [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "debian" ]]; then
                echo "  sudo apt update && sudo apt install python3 python3-pip python3-venv"
            elif [[ "$DISTRO" == "fedora" ]]; then
                echo "  sudo dnf install python3 python3-pip"
            elif [[ "$DISTRO" == "arch" ]]; then
                echo "  sudo pacman -S python python-pip"
            else
                echo "  Use your distribution's package manager to install python3"
            fi
        elif [[ "$OS" == "mac" ]]; then
            echo "  Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "  Then run: brew install python3"
        fi

        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"

    # Check Python version is 3.8+
    MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
        print_error "Python 3.8+ required, found $PYTHON_VERSION"
        exit 1
    fi

    print_success "Python version is compatible"
}

# Check FFmpeg
check_ffmpeg() {
    print_header "Checking FFmpeg Installation"

    if ! command -v ffmpeg &> /dev/null; then
        print_warning "FFmpeg is not installed"
        print_info "Install instructions:"

        if [[ "$OS" == "linux" ]]; then
            if [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "debian" ]]; then
                echo "  sudo apt update && sudo apt install ffmpeg"
            elif [[ "$DISTRO" == "fedora" ]]; then
                echo "  sudo dnf install ffmpeg"
            elif [[ "$DISTRO" == "arch" ]]; then
                echo "  sudo pacman -S ffmpeg"
            else
                echo "  Use your distribution's package manager to install ffmpeg"
            fi
        elif [[ "$OS" == "mac" ]]; then
            echo "  brew install ffmpeg"
        fi

        echo ""
        read -p "Would you like to continue without FFmpeg? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        FFMPEG_VERSION=$(ffmpeg -version | head -n1)
        print_success "FFmpeg found: $FFMPEG_VERSION"
    fi
}

# Create virtual environment
setup_venv() {
    print_header "Setting Up Virtual Environment"

    if [ -d "venv" ]; then
        print_info "Virtual environment already exists"
        read -p "Recreate it? This will delete existing venv. (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
            print_success "Virtual environment recreated"
        else
            print_info "Using existing virtual environment"
        fi
    else
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi

    # Activate venv
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Upgrade pip
upgrade_pip() {
    print_header "Upgrading pip"

    python -m pip install --upgrade pip --quiet
    print_success "pip upgraded to latest version"
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"

    echo "Choose installation type:"
    echo "  1) Full install (includes ML features, ~2GB download)"
    echo "  2) Minimal install (faster, smaller, no ML features)"
    echo "  3) Cancel"
    echo ""
    read -p "Enter choice (1-3): " -n 1 -r
    echo ""

    case $REPLY in
        1)
            print_info "Installing full dependencies..."
            echo "This will take 5-15 minutes depending on your internet speed"
            sleep 2
            pip install -r requirements.txt
            print_success "Full installation complete!"
            ;;
        2)
            print_info "Installing minimal dependencies..."
            echo "This will take 3-8 minutes"
            sleep 2
            pip install -r requirements-minimal.txt
            print_success "Minimal installation complete!"
            print_info "Note: Style learning features (Phase 3) won't be available"
            ;;
        3)
            print_warning "Installation cancelled"
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# Run system check
run_system_check() {
    print_header "Running System Check"

    if python check_system.py; then
        print_success "All system checks passed!"
    else
        print_warning "Some checks failed, but you can still try using Auto Edit"
    fi
}

# Create necessary directories
create_directories() {
    print_header "Creating Directories"

    mkdir -p input output temp models training_data memes sounds music images
    print_success "Created necessary directories"
}

# Final instructions
show_instructions() {
    print_header "Installation Complete!"

    echo -e "${GREEN}${BOLD}✓ Auto Edit is ready to use!${NC}\n"

    echo "Quick Start:"
    echo "  1. Activate virtual environment: ${BOLD}source venv/bin/activate${NC}"
    echo "  2. Run GUI: ${BOLD}python auto_edit_gui.py${NC}"
    echo "  3. Or use CLI: ${BOLD}python auto_edit.py edit video.mp4${NC}"
    echo ""
    echo "For more help, see:"
    echo "  - README.md for full documentation"
    echo "  - QUICK_START.md for step-by-step guide"
    echo "  - config.yaml for configuration options"
    echo ""

    if [[ "$OS" == "mac" ]] || [[ "$OS" == "linux" ]]; then
        echo "Pro tip: Create an alias for easy access:"
        echo "  echo 'alias auto-edit=\"cd $(pwd) && source venv/bin/activate && python auto_edit.py\"' >> ~/.bashrc"
        echo ""
    fi
}

# Main installation flow
main() {
    clear
    echo -e "${BLUE}${BOLD}"
    cat << "EOF"
    ___        __          ______    ___ __
   / _ | __ __/ /____     / __/ /___/ (_) /_
  / __ |/ // / __/ _ \   / _// / _  / / __/
 /_/ |_|\_,_/\__/\___/  /___/_/\_,_/_/\__/

 Automated Stream Highlight Editor
 Installation Script v0.4.0
EOF
    echo -e "${NC}\n"

    print_info "Detected OS: $OS ($DISTRO)"
    echo ""

    # Run checks and installation
    detect_os
    check_python
    check_ffmpeg
    setup_venv
    upgrade_pip
    install_dependencies
    create_directories
    run_system_check
    show_instructions

    # Offer to run system check
    echo ""
    read -p "Would you like to test the installation now? (Y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        python check_system.py
    fi

    echo -e "\n${GREEN}${BOLD}Installation complete! Enjoy Auto Edit!${NC}\n"
}

# Run main installation
main
