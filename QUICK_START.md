# Auto Edit - Quick Start Guide

Get started with Auto Edit in 5 minutes!

## Prerequisites

Install FFmpeg first:

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

## Installation

```bash
# Clone repository
git clone <repository-url>
cd Audo-Edit

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Basic Usage

### 1. Place Your Video

Put your stream VOD in the `input/` folder:
```bash
cp ~/Downloads/my_stream.mp4 input/
```

### 2. Run Auto Edit

Create highlights (default 20 minutes):
```bash
python auto_edit.py edit input/my_stream.mp4
```

Create shorter highlights (15 minutes):
```bash
python auto_edit.py edit input/my_stream.mp4 -d 15
```

### 3. Get Your Results

Find your highlights in the `output/` folder:
- `output/my_stream_highlights.mp4` - Your highlight video
- `output/clip_list.txt` - List of selected clips
- `output/my_stream_highlights.json` - Detailed metadata

## Quick Testing

Test with a preview (top 5 clips only, faster):
```bash
python auto_edit.py edit input/my_stream.mp4 --preview
```

Analyze signals without creating video:
```bash
python auto_edit.py analyze input/my_stream.mp4
```

## Common Tweaks

### Get More Clips

Lower the threshold in `config.yaml`:
```yaml
selection:
  interest_threshold: 0.4  # Default is 0.6
```

### Adjust Signal Weights

Edit `config.yaml` to emphasize certain signals:
```yaml
signals:
  audio_voice_analysis:
    weight: 1.5  # Boost voice reactions

  audio_game_peaks:
    weight: 0.6  # Reduce game audio
```

### Change Target Duration

```bash
python auto_edit.py edit input/my_stream.mp4 -d 10  # 10 minutes
```

## Troubleshooting

### No clips selected
- Lower `interest_threshold` in config.yaml
- Enable more signals
- Check that signals are detecting events with `analyze`

### Too many clips
- Raise `interest_threshold` in config.yaml
- Reduce signal weights
- Increase target duration

### Chat detection not working
- Verify chat overlay is visible in video
- Adjust chat region in config.yaml
- Disable if you have minimal chat activity

## Next Steps

1. **Read the full documentation:** See README.md and USAGE.md
2. **Try different configurations:** Check `examples/` folder
3. **Tune for your content:** Adjust signals and weights
4. **Learn your style:** Use Phase 3 features (coming soon)

## Command Cheat Sheet

```bash
# Edit with default settings
python auto_edit.py edit input/video.mp4

# Create 15-minute highlights
python auto_edit.py edit input/video.mp4 -d 15

# Quick preview
python auto_edit.py edit input/video.mp4 --preview

# Analyze only (no output)
python auto_edit.py analyze input/video.mp4

# Show configuration
python auto_edit.py config-show

# Toggle signals
python auto_edit.py signal chat_density on
python auto_edit.py signal facecam_emotion off

# Change mode
python auto_edit.py set-mode general_interest
```

## Example Workflows

### Gaming Stream
```bash
# Use default settings (optimized for gaming)
python auto_edit.py edit input/gaming_stream.mp4 -d 20
```

### Reaction Content
```bash
# Copy reaction config
cp examples/config_reaction_content.yaml config.yaml

# Run edit
python auto_edit.py edit input/reaction_stream.mp4
```

### Horror Game
```bash
# Copy horror config
cp examples/config_horror_gaming.yaml config.yaml

# Run edit
python auto_edit.py edit input/horror_stream.mp4
```

## Performance

Typical processing times:
- 2-hour stream (720p): ~10-15 minutes
- 4-hour stream (1080p): ~20-30 minutes
- 9-hour stream (720p): ~45-60 minutes

## Help

```bash
# Get help on any command
python auto_edit.py --help
python auto_edit.py edit --help
```

For more detailed information, see:
- README.md - Overview and features
- USAGE.md - Detailed usage guide
- examples/ - Example configurations

## Support

- GitHub Issues: Report bugs or request features
- Documentation: Check README.md and USAGE.md
- Examples: See examples/ folder for configurations

---

**That's it! You're ready to create automated highlights.** 🎉

Start with the defaults, analyze the results, and tune the settings to match your content style.
