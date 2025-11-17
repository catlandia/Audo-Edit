# Auto Edit - Automated Stream Highlight Editor

An intelligent application that automatically edits long-form stream VODs into engaging, watchable highlight videos that match your personal editing style.

## Features

### Phase 1: Foundation (Current)
- **Multi-Signal Detection**
  - Audio analysis (voice reactions, peaks, silence-to-chaos patterns)
  - Visual activity detection (motion, scene changes)
  - Optional chat density detection (motion-based)
  - Optional facecam emotion detection

- **Flexible Configuration**
  - Toggleable signal sources
  - Adjustable weights per signal
  - Three editing modes: General Interest, My Style, Hybrid

- **Smart Clip Selection**
  - Intelligent moment clustering
  - Context-aware clip boundaries
  - Configurable duration targets

- **High-Quality Output**
  - Automated video assembly
  - Metadata export
  - Clip list generation

### Future Phases
- **Phase 2**: Enhanced signal system and UI
- **Phase 3**: Style learning from paired examples
- **Phase 4**: Advanced mode system with weighting
- **Phase 5**: Performance optimization and advanced features

## Installation

### Requirements
- Python 3.8+
- FFmpeg (must be installed separately)

### Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

### Install Auto Edit

1. Clone the repository:
```bash
git clone <repository-url>
cd Audo-Edit
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy example configuration:
```bash
cp .env.example .env
```

## Quick Start

### Basic Usage

Edit a stream VOD with default settings:
```bash
python auto_edit.py edit input_stream.mp4
```

Specify output path and target duration:
```bash
python auto_edit.py edit input_stream.mp4 -o highlights.mp4 -d 15
```

Generate a quick preview (top 5 clips only):
```bash
python auto_edit.py edit input_stream.mp4 --preview
```

### Analyze Without Editing

See what signals are detected without creating output:
```bash
python auto_edit.py analyze input_stream.mp4
```

### Configuration

View current configuration:
```bash
python auto_edit.py config-show
```

Toggle signal sources:
```bash
python auto_edit.py signal chat_density on
python auto_edit.py signal facecam_emotion off
```

Change editing mode:
```bash
python auto_edit.py set-mode general_interest
```

## Configuration Guide

### Signal Sources

#### Core Signals (Recommended Always On)

**audio_voice_analysis**
- Detects laughter, shouting, excitement in your voice
- Weight: 1.0 (default)
- Best for: Reaction content, gaming streams

**audio_game_peaks**
- Detects audio peaks and loud moments
- Configurable threshold (dB)
- Best for: Action games, intense moments

**visual_activity**
- Detects motion and scene changes
- Best for: Fast-paced gameplay

**silence_to_chaos**
- Finds dramatic transitions from quiet to chaotic
- Best for: Jump scares, unexpected moments

#### Optional Signals

**chat_density**
- Detects chat activity from video overlay
- Enable only with active chat (5+ messages/min)
- Configure region in config.yaml

**facecam_emotion**
- Detects movement in facecam region
- Enable if you use a webcam
- Configure region in config.yaml

### Editing Modes

**General Interest Mode** (default)
- Uses universal engagement signals
- Works without training data
- Good for first-time use

**My Style Mode** (Phase 3)
- Uses learned personal preferences
- Requires trained model
- Needs 5+ training examples

**Hybrid Mode** (Phase 3)
- Combines both approaches
- Adjustable weighting
- Best results after training

### Output Settings

Edit `config.yaml` to customize:

```yaml
output:
  target_duration_minutes: 20
  min_clip_length_seconds: 3
  max_clip_length_seconds: 45
  fps: 30
  resolution: [1280, 720]
  codec: libx264
```

## Style Learning (Phase 3)

### Adding Training Examples

Provide pairs of raw stream + your edited highlights:

```bash
python auto_edit.py add-example raw_stream.mp4 my_edited_highlights.mp4
```

Add 5-10 examples for initial training, 20-50+ for best results.

### Training the Model

After adding examples:

```bash
python auto_edit.py train
```

### Using Your Style

```bash
python auto_edit.py set-mode my_style
python auto_edit.py edit stream.mp4
```

Check model status:
```bash
python auto_edit.py style-info
```

## Examples

### Small Stream Setup

For streams with little/no chat activity:

```yaml
signals:
  audio_voice_analysis:
    enabled: true
    weight: 1.2

  audio_game_peaks:
    enabled: true
    weight: 1.0

  visual_activity:
    enabled: true
    weight: 0.9

  chat_density:
    enabled: false  # Disabled for small streams

  facecam_emotion:
    enabled: true  # If you use webcam
    weight: 0.7
```

### Large Stream Setup

For streams with active chat:

```yaml
signals:
  chat_density:
    enabled: true
    weight: 0.8
    min_messages_per_minute: 5
```

### Reaction Content

Optimize for reactions and commentary:

```yaml
signals:
  audio_voice_analysis:
    enabled: true
    weight: 1.5  # Boost voice detection
    detect_laughter: true
    detect_shouting: true

  facecam_emotion:
    enabled: true
    weight: 1.0
```

## File Structure

```
Audo-Edit/
├── auto_edit/           # Main package
│   ├── __init__.py
│   ├── config.py        # Configuration management
│   ├── video_processor.py  # Video/audio processing
│   ├── signal_detector.py  # Signal detection
│   ├── clip_selector.py    # Clip selection logic
│   ├── video_assembler.py  # Video assembly
│   ├── style_learner.py    # Style learning (Phase 3)
│   └── utils.py         # Utility functions
├── auto_edit.py         # Main CLI
├── config.yaml          # Configuration file
├── requirements.txt     # Python dependencies
├── input/              # Input videos (default)
├── output/             # Output highlights
├── models/             # Trained models
└── training_data/      # Training examples
```

## Troubleshooting

### FFmpeg Not Found
```
Error: ffmpeg: command not found
```
Solution: Install FFmpeg (see Installation section)

### Out of Memory
For very large files (20GB+):
- Reduce `processing.max_workers` in config.yaml
- Process in smaller chunks
- Close other applications

### No Clips Selected
```
No clips selected. Try adjusting signal settings...
```
Solutions:
- Lower `selection.interest_threshold` in config.yaml
- Enable more signal sources
- Adjust signal weights
- Check that signals are being detected with `analyze` command

### Chat Detection Not Working
Chat density requires:
- Active chat overlay visible in video
- At least 5+ messages per minute
- Correct region configured
- Consider disabling for small streams

## Performance

Typical processing times (on modern hardware):

- 2-hour stream (720p): ~10-15 minutes
- 4-hour stream (1080p): ~20-30 minutes
- 9-hour stream (720p): ~45-60 minutes

Signal detection is the most time-intensive step, especially visual analysis.

## Roadmap

- [x] Phase 1: Foundation (v0.1.0)
  - Core signal detection
  - Basic clip assembly
  - General interest mode

- [ ] Phase 2: Signal System (v0.2.0)
  - Enhanced signal detection
  - Web UI for settings
  - Real-time preview

- [ ] Phase 3: Learning System (v0.3.0)
  - Style pattern recognition
  - Model training pipeline
  - My Style mode

- [ ] Phase 4: Mode System (v0.4.0)
  - Hybrid mode implementation
  - Advanced weighting controls
  - Per-signal mode options

- [ ] Phase 5: Refinement (v0.5.0)
  - Performance optimization
  - Game API integration
  - Alert detection
  - Advanced narrative understanding

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your chosen license]

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation

## Credits

Built with:
- OpenCV for video processing
- librosa for audio analysis
- FFmpeg for video manipulation
- Click for CLI interface
