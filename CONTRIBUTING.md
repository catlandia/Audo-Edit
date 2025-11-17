# Contributing to Auto Edit

Thank you for your interest in contributing to Auto Edit! This document provides guidelines and information for contributors.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Audo-Edit.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit: `git commit -m "Add: your feature description"`
7. Push: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Prerequisites
- Python 3.8+
- FFmpeg
- Git

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Audo-Edit.git
cd Audo-Edit

# Run setup
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=auto_edit
```

## Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Maximum line length: 100 characters

### Example:

```python
def process_video(video_path: str, config: Config) -> List[Clip]:
    """
    Process video and return selected clips.

    Args:
        video_path: Path to input video
        config: Configuration object

    Returns:
        List of selected clips
    """
    # Implementation
    pass
```

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Alphabetical within groups

```python
import os
import sys
from pathlib import Path

import cv2
import numpy as np

from auto_edit.config import Config
from auto_edit.utils import format_duration
```

## Commit Messages

### Format
```
Type: Brief description (50 chars or less)

More detailed explanation if needed (wrap at 72 chars).
Explain what and why, not how.

- Bullet points are okay
- Use present tense: "Add feature" not "Added feature"
```

### Types
- **Add:** New feature
- **Fix:** Bug fix
- **Update:** Modify existing feature
- **Remove:** Remove feature/code
- **Refactor:** Code restructuring
- **Docs:** Documentation changes
- **Test:** Add or modify tests
- **Style:** Code style changes (formatting, etc.)
- **Perf:** Performance improvements

### Examples
```
Add: Chat density detection signal

Implement motion-based chat activity detection that analyzes
scrolling speed in configurable chat region.

- Add ChatDetector class
- Configure chat region in YAML
- Add tests for chat detection
```

## Pull Request Process

1. **Update Documentation**
   - Update README.md if adding features
   - Update USAGE.md for new commands
   - Add docstrings to new code

2. **Add Tests**
   - Write tests for new features
   - Ensure existing tests pass
   - Aim for >80% code coverage

3. **Update Changelog**
   - Add entry to CHANGELOG.md
   - Describe changes clearly

4. **Code Review**
   - Respond to reviewer feedback
   - Make requested changes
   - Keep discussion professional

5. **Merge**
   - Maintainer will merge when approved
   - Delete your branch after merge

## Areas for Contribution

### High Priority
- [ ] Performance optimization for large files
- [ ] Additional signal sources (alerts, game APIs)
- [ ] ML model for style learning (Phase 3)
- [ ] Web UI for configuration
- [ ] Video quality improvements

### Medium Priority
- [ ] Additional output formats
- [ ] Batch processing improvements
- [ ] Better error handling
- [ ] More example configurations
- [ ] Video tutorials

### Low Priority
- [ ] Logo and branding
- [ ] Internationalization (i18n)
- [ ] Plugin system
- [ ] Cloud processing support

## Signal Source Development

### Adding a New Signal Source

1. **Add to signal_detector.py**

```python
def detect_new_signal(self, video_path: str, ...) -> List[SignalEvent]:
    """
    Detect new signal type.

    Args:
        video_path: Path to video
        ...

    Returns:
        List of signal events
    """
    events = []

    # Your detection logic

    return events
```

2. **Add configuration to config.yaml**

```yaml
signals:
  new_signal:
    enabled: false
    weight: 1.0
    # Signal-specific parameters
```

3. **Update detect_all_signals()**

```python
if 'new_signal' in self.enabled_signals:
    all_signals['new_signal'] = self.detect_new_signal(...)
```

4. **Add tests**

```python
def test_new_signal_detection():
    # Test signal detection
    pass
```

5. **Update documentation**
- Add to README.md signal list
- Add to USAGE.md with explanation
- Create example configuration

## Testing Guidelines

### Unit Tests
- Test individual functions
- Mock external dependencies
- Use pytest fixtures

### Integration Tests
- Test complete workflows
- Use small test videos
- Verify output files

### Test Data
- Keep test files small (< 1MB)
- Store in `tests/data/`
- Don't commit large videos

### Example Test

```python
import pytest
from auto_edit import Config, SignalDetector

def test_audio_peak_detection():
    config = Config('tests/test_config.yaml')
    detector = SignalDetector(config)

    # Create test audio
    audio = np.random.randn(22050 * 10)  # 10 seconds
    sr = 22050

    events = detector.detect_audio_peaks(audio, sr)

    assert isinstance(events, list)
    assert all(isinstance(e, SignalEvent) for e in events)
```

## Documentation

### README.md
- Overview and quick start
- Feature highlights
- Installation instructions
- Basic usage examples

### USAGE.md
- Detailed command reference
- Configuration guide
- Advanced examples
- Troubleshooting

### Code Documentation
- Docstrings for all public APIs
- Type hints
- Inline comments for complex logic

## Bug Reports

### Good Bug Report Includes:
1. **Description:** Clear description of the bug
2. **Steps to Reproduce:** Exact steps to trigger bug
3. **Expected Behavior:** What should happen
4. **Actual Behavior:** What actually happens
5. **Environment:**
   - OS and version
   - Python version
   - FFmpeg version
   - Auto Edit version
6. **Logs:** Relevant error messages
7. **Video Info:** (if applicable)
   - Duration
   - Resolution
   - Codec
   - File size

### Example Bug Report

```markdown
## Bug: Chat detection not working on 1080p streams

### Description
Chat density signal doesn't detect any events on 1080p streams,
but works fine on 720p streams.

### Steps to Reproduce
1. Use 1080p stream with visible chat
2. Enable chat_density signal
3. Run `python auto_edit.py analyze stream.mp4`
4. Check signal output

### Expected
Chat activity events detected

### Actual
0 chat activity events found

### Environment
- OS: Ubuntu 22.04
- Python: 3.10.8
- FFmpeg: 4.4.2
- Auto Edit: 0.1.0

### Logs
```
Detecting chat activity...
Found 0 chat activity events
```

### Video Info
- Duration: 2h 15m
- Resolution: 1920x1080
- Format: MP4
- Chat position: Right side
```

## Feature Requests

### Good Feature Request Includes:
1. **Use Case:** Why is this needed?
2. **Description:** What should it do?
3. **Examples:** How would it work?
4. **Alternatives:** Other approaches considered?

## Questions?

- Open a GitHub Discussion
- Check existing issues
- Read documentation first

## Code of Conduct

### Our Standards
- Be respectful and professional
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be added to:
- CONTRIBUTORS.md file
- Release notes
- Special thanks in README

Thank you for contributing to Auto Edit! 🎉
