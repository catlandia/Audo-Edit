#!/bin/bash
# Auto Edit Setup Script

echo "================================"
echo "Auto Edit - Setup"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8+ required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version"

# Check FFmpeg
echo "Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠ FFmpeg not found. Please install FFmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org"
    exit 1
fi
echo "✓ FFmpeg installed"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "✗ Error installing dependencies"
    exit 1
fi

# Create .env file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
else
    echo "✓ .env file exists"
fi

# Create directories
echo ""
echo "Creating directories..."
mkdir -p input output temp models training_data
echo "✓ Directories created"

# Make auto_edit.py executable
chmod +x auto_edit.py

echo ""
echo "================================"
echo "Setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Place your stream VOD in input/"
echo "  3. Run: python auto_edit.py edit input/your_video.mp4"
echo ""
echo "For help: python auto_edit.py --help"
echo "Read README.md for full documentation"
echo ""
