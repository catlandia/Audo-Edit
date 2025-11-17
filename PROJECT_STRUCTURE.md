# Auto Edit - Project Structure

## Directory Tree

```
Audo-Edit/
├── auto_edit/                    # Main Python package
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── video_processor.py       # Video/audio processing
│   ├── signal_detector.py       # Signal detection (core feature)
│   ├── clip_selector.py         # Clip selection and scoring
│   ├── video_assembler.py       # Video assembly and export
│   ├── style_learner.py         # Style learning system (Phase 3)
│   └── utils.py                 # Utility functions
│
├── examples/                     # Example configurations
│   ├── config_small_stream.yaml # Small stream setup
│   ├── config_large_stream.yaml # Large stream with chat
│   ├── config_reaction_content.yaml  # Reaction content
│   └── config_horror_gaming.yaml     # Horror game setup
│
├── input/                       # Input videos (gitignored)
│   └── .gitkeep
│
├── output/                      # Generated highlights (gitignored)
│   └── .gitkeep
│
├── temp/                        # Temporary processing files (gitignored)
│   └── .gitkeep
│
├── models/                      # Trained models (gitignored)
│   └── .gitkeep
│
├── training_data/              # Training examples (gitignored)
│   └── .gitkeep
│
├── auto_edit.py                # Main CLI entry point
├── config.yaml                 # Default configuration
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── setup.sh                    # Installation script
│
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
│
├── README.md                   # Main documentation
├── USAGE.md                    # Detailed usage guide
├── QUICK_START.md             # Quick start guide
├── CONTRIBUTING.md            # Contribution guidelines
├── CHANGELOG.md               # Version history
├── LICENSE                    # MIT License
└── PROJECT_STRUCTURE.md       # This file
```

## Component Overview

### Core Modules

#### `config.py`
- Loads and manages YAML configuration
- Environment variable support
- Signal weight management
- Mode configuration

#### `video_processor.py`
- Video metadata extraction
- Audio extraction and loading
- Frame extraction
- Audio segment analysis
- FFmpeg integration

#### `signal_detector.py`
- **Audio signals:**
  - Voice activity detection
  - Audio peak detection
  - Silence-to-chaos patterns
- **Visual signals:**
  - Motion detection
  - Scene change detection
- **Optional signals:**
  - Chat density (motion-based)
  - Facecam emotion detection

#### `clip_selector.py`
- Moment scoring
- Signal aggregation
- Clip clustering
- Timeline analysis
- Clip boundary determination

#### `video_assembler.py`
- Clip extraction
- Video concatenation
- Metadata export
- Clip list generation
- Preview creation

#### `style_learner.py` (Phase 3)
- Training example management
- Style model training
- Pattern recognition
- Personalized scoring
- Model persistence

#### `utils.py`
- Logging setup
- Duration formatting
- Progress tracking
- Pretty printing
- File validation

### CLI Interface

#### `auto_edit.py`
Main command-line interface with commands:

**Phase 1 Commands:**
- `edit` - Create highlight video
- `analyze` - Test signal detection
- `config-show` - Display configuration
- `signal` - Toggle signal sources
- `set-mode` - Change editing mode

**Phase 3 Commands:**
- `add-example` - Add training pair
- `train` - Train style model
- `style-info` - View model status

## Data Flow

```
Input Video (VOD)
      ↓
Video Processor
  ├─→ Extract Audio
  ├─→ Extract Metadata
  └─→ Frame Analysis
      ↓
Signal Detector
  ├─→ Audio Analysis
  │   ├─→ Voice Activity
  │   ├─→ Audio Peaks
  │   └─→ Silence-to-Chaos
  ├─→ Visual Analysis
  │   ├─→ Motion Detection
  │   └─→ Scene Changes
  └─→ Optional Signals
      ├─→ Chat Density
      └─→ Facecam Emotion
      ↓
Clip Selector
  ├─→ Score Moments
  ├─→ Cluster Events
  ├─→ Select Top Clips
  └─→ Determine Boundaries
      ↓
Video Assembler
  ├─→ Extract Clips
  ├─→ Concatenate
  ├─→ Export Video
  └─→ Generate Metadata
      ↓
Output Highlights
  ├─→ Video File (.mp4)
  ├─→ Clip List (.txt)
  └─→ Metadata (.json)
```

## Configuration System

### Hierarchy
1. `config.yaml` - Default configuration
2. Environment variables (`.env`) - Override paths
3. Command-line arguments - Override mode, duration

### Configuration Sections

**modes:**
- my_style - Personal learned style
- general_interest - Universal signals
- hybrid - Combined approach

**signals:**
- Signal source definitions
- Enabled/disabled state
- Weight values
- Signal-specific parameters

**output:**
- Target duration
- Resolution and FPS
- Codec settings
- File format options

**selection:**
- Interest threshold
- Clustering parameters
- Context inclusion
- Clip duration constraints

**processing:**
- Chunk size
- Worker count
- Multiprocessing settings

## File Formats

### Input
Supported video formats:
- MP4, MKV, AVI, MOV
- FLV, WebM, TS

### Output

**Video:** `{name}_highlights.mp4`
- H.264 codec
- AAC audio
- Configurable resolution/bitrate

**Clip List:** `clip_list.txt`
```
Clip 1:
  Time: 125.50s - 145.75s (20.25s)
  Score: 0.892
  Reason: Laughter detected
  Signals: laughter, audio_peak
```

**Metadata:** `{name}_highlights.json`
```json
{
  "clips": [...],
  "summary": {
    "total_clips": 12,
    "total_duration": 1234.5,
    "avg_clip_duration": 102.875,
    "avg_score": 0.756
  }
}
```

## Dependencies

### Core
- `opencv-python` - Video processing
- `librosa` - Audio analysis
- `ffmpeg-python` - Video manipulation
- `moviepy` - Video editing

### Analysis
- `numpy` - Numerical computation
- `scipy` - Signal processing
- `scikit-learn` - ML utilities

### ML (Phase 3)
- `torch` - Neural networks
- `transformers` - NLP models

### CLI
- `click` - Command-line interface
- `tqdm` - Progress bars
- `colorama` - Colored output
- `pyyaml` - Configuration

## Extension Points

### Adding New Signals

1. Implement detection method in `signal_detector.py`
2. Add configuration to `config.yaml`
3. Update `detect_all_signals()` dispatcher
4. Add documentation and examples

### Custom Processing

1. Extend `VideoProcessor` class
2. Override methods as needed
3. Plug into pipeline

### Alternative Modes

1. Implement mode logic in `clip_selector.py`
2. Add mode configuration
3. Update CLI mode selection

## Future Architecture

### Phase 2: Signal System
- Plugin architecture for signals
- Real-time signal preview
- Web UI for configuration

### Phase 3: Learning System
- ML pipeline for style extraction
- Feature engineering system
- Model training infrastructure
- Continuous learning

### Phase 4: Mode System
- Advanced mode mixer
- Per-signal mode overrides
- Custom mode definitions

### Phase 5: Refinement
- Distributed processing
- Cloud integration
- Advanced narrative analysis
- Quality enhancement

## Performance Considerations

### Memory
- Chunk-based processing
- Lazy frame loading
- Efficient audio handling

### Speed
- Multiprocessing support
- Frame sampling
- Cached computations

### Storage
- Temporary file management
- Cleanup after processing
- Configurable temp directory

## Testing Structure

```
tests/
├── test_config.py
├── test_video_processor.py
├── test_signal_detector.py
├── test_clip_selector.py
├── test_video_assembler.py
├── test_style_learner.py
├── test_integration.py
└── data/
    ├── test_video_short.mp4
    └── test_config.yaml
```

## Deployment

### Development
```bash
python auto_edit.py edit video.mp4
```

### Installed
```bash
pip install -e .
auto-edit edit video.mp4
```

### Docker (Future)
```bash
docker run auto-edit edit video.mp4
```

## Documentation Structure

- **README.md** - Overview, features, installation
- **QUICK_START.md** - Get started in 5 minutes
- **USAGE.md** - Comprehensive usage guide
- **CONTRIBUTING.md** - Development guide
- **CHANGELOG.md** - Version history
- **PROJECT_STRUCTURE.md** - Architecture (this file)

## Resources

- Repository: [GitHub URL]
- Issues: [GitHub Issues]
- Discussions: [GitHub Discussions]
- Documentation: [Docs URL]

---

This structure supports the full vision from Phase 1 through Phase 5 while remaining maintainable and extensible.
