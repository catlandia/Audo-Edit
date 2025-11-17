# Changelog

All notable changes to Auto Edit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-XX

### Added
- Initial release (Phase 1: Foundation)
- Core video and audio processing pipeline
- Multi-signal detection system:
  - Audio voice analysis (laughter, shouting, excitement)
  - Audio peak detection
  - Visual activity detection (motion, scene changes)
  - Silence-to-chaos pattern detection
  - Optional chat density detection
  - Optional facecam emotion detection
- Intelligent clip selection and scoring
- Automated video assembly and export
- CLI interface with commands:
  - `edit` - Create highlight videos
  - `analyze` - Test signal detection
  - `config-show` - View configuration
  - `signal` - Toggle signals
  - `set-mode` - Change editing mode
- Toggleable signal sources with configurable weights
- General Interest editing mode
- Configuration system via YAML
- Comprehensive documentation (README, USAGE)
- Example configurations for different use cases:
  - Small streams
  - Large streams
  - Reaction content
  - Horror gaming
- Style learning architecture (Phase 3 placeholder):
  - `add-example` - Add training pairs
  - `train` - Train personal style model
  - `style-info` - View model status
- Setup script for easy installation
- Metadata export (JSON)
- Clip list export (TXT)
- Preview mode (top 5 clips)

### Technical Details
- Built with OpenCV, librosa, FFmpeg
- Supports videos up to 9 hours, 21GB (tested)
- Efficient chunk-based processing
- Modular architecture for future expansion

## [Unreleased]

### Planned for Phase 2 (v0.2.0)
- Enhanced signal detection algorithms
- Web UI for configuration
- Real-time preview
- Additional signal sources:
  - Alert detection (subs, donations)
  - Game-specific API integration
- Performance optimizations

### Planned for Phase 3 (v0.3.0)
- Full style learning implementation
- ML-based pattern recognition
- Training pipeline
- My Style mode activation
- Model improvement over time

### Planned for Phase 4 (v0.4.0)
- Hybrid mode implementation
- Advanced weighting controls
- Per-signal mode options
- Custom signal definitions

### Planned for Phase 5 (v0.5.0)
- Performance optimization for large files
- Advanced narrative understanding
- Transition effects
- Quality improvements
- Additional export formats

## Version History

### Version Numbering
- **0.1.x** - Phase 1: Foundation
- **0.2.x** - Phase 2: Signal System
- **0.3.x** - Phase 3: Learning System
- **0.4.x** - Phase 4: Mode System
- **0.5.x** - Phase 5: Refinement
- **1.0.0** - First stable release

## Migration Guides

### Upgrading from Future Versions
(Migration guides will be added as new versions are released)
