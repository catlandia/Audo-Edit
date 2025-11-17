# Auto Edit - Detailed Usage Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Command Reference](#command-reference)
3. [Configuration](#configuration)
4. [Signal Sources Explained](#signal-sources-explained)
5. [Workflow Examples](#workflow-examples)
6. [Tips & Best Practices](#tips--best-practices)

## Getting Started

### First Run

1. **Prepare your video**
   - Place your stream VOD in the `input/` folder
   - Supported formats: MP4, MKV, AVI, MOV, FLV, WebM, TS

2. **Run basic edit**
   ```bash
   python auto_edit.py edit input/my_stream.mp4
   ```

3. **Check the results**
   - Output video: `output/my_stream_highlights.mp4`
   - Clip list: `output/clip_list.txt`
   - Metadata: `output/my_stream_highlights.json`

### Understanding the Output

After running edit, you'll get:

1. **Highlight Video** - The assembled highlight reel
2. **Clip List** - Text file showing selected clips with timestamps
3. **Metadata JSON** - Detailed information about each clip

## Command Reference

### edit - Create Highlights

```bash
python auto_edit.py edit INPUT_VIDEO [OPTIONS]
```

**Options:**
- `-o, --output PATH` - Specify output video path
- `-d, --duration INT` - Target duration in minutes (default: 20)
- `-m, --mode CHOICE` - Editing mode: general, my_style, hybrid
- `-c, --config PATH` - Config file (default: config.yaml)
- `--preview` - Generate quick preview (top 5 clips)
- `-v, --verbose` - Show detailed logging

**Examples:**

Create 15-minute highlights:
```bash
python auto_edit.py edit stream.mp4 -d 15
```

Create preview to test settings:
```bash
python auto_edit.py edit stream.mp4 --preview
```

Custom output location:
```bash
python auto_edit.py edit stream.mp4 -o ~/Videos/highlights.mp4
```

Verbose mode for debugging:
```bash
python auto_edit.py edit stream.mp4 -v
```

### analyze - Test Signal Detection

```bash
python auto_edit.py analyze INPUT_VIDEO
```

Use this to:
- Test signal detection without creating output
- See what moments are being detected
- Verify settings before running full edit
- Check signal statistics

**Example output:**
```
Detected Signals Summary
=================================
Total events: 142

By signal type:
  high_motion................  45 events (avg intensity: 0.78)
  audio_peak.................  38 events (avg intensity: 0.65)
  laughter...................  22 events (avg intensity: 0.82)
  excitement.................  18 events (avg intensity: 0.71)
  silence_to_chaos...........  12 events (avg intensity: 0.89)
```

### config-show - View Settings

```bash
python auto_edit.py config-show
```

Shows:
- Active editing mode
- Enabled signals and their weights
- Output settings
- Processing configuration

### signal - Toggle Signals

```bash
python auto_edit.py signal SIGNAL_NAME on|off
```

**Available signals:**
- `audio_voice_analysis` - Voice reactions
- `audio_game_peaks` - Audio peaks
- `visual_activity` - Motion and scene changes
- `silence_to_chaos` - Dramatic transitions
- `chat_density` - Chat activity
- `facecam_emotion` - Facecam reactions

**Examples:**

Enable chat detection:
```bash
python auto_edit.py signal chat_density on
```

Disable facecam:
```bash
python auto_edit.py signal facecam_emotion off
```

### set-mode - Change Editing Mode

```bash
python auto_edit.py set-mode MODE
```

**Modes:**
- `general_interest` - Universal signals (default)
- `my_style` - Personal learned style (requires training)
- `hybrid` - Combination of both

### add-example - Add Training Data (Phase 3)

```bash
python auto_edit.py add-example RAW_VIDEO EDITED_VIDEO
```

Provide pairs of:
- RAW_VIDEO: Your original stream VOD
- EDITED_VIDEO: Your hand-edited highlights

**Example:**
```bash
python auto_edit.py add-example input/stream_2024_01_15.mp4 input/highlights_2024_01_15.mp4
```

### train - Train Style Model (Phase 3)

```bash
python auto_edit.py train
```

Trains the model using all added examples. Requires minimum 5 examples.

### style-info - Model Status (Phase 3)

```bash
python auto_edit.py style-info
```

Shows:
- Training status
- Number of examples
- Learned preferences

## Configuration

### config.yaml Structure

```yaml
# Active editing mode
active_mode: general_interest

# Signal sources
signals:
  audio_voice_analysis:
    enabled: true
    weight: 1.0
    detect_laughter: true
    detect_shouting: true
    detect_excitement: true

  audio_game_peaks:
    enabled: true
    weight: 0.8
    peak_threshold: -20  # dB

  visual_activity:
    enabled: true
    weight: 0.9
    scene_change_threshold: 30
    motion_threshold: 0.3

  chat_density:
    enabled: false
    weight: 0.7
    region: [0.7, 0.0, 1.0, 1.0]  # Right 30% of screen

# Output settings
output:
  target_duration_minutes: 20
  min_clip_length_seconds: 3
  max_clip_length_seconds: 45
  fps: 30
  resolution: [1280, 720]

# Selection settings
selection:
  interest_threshold: 0.6  # 0-1 (lower = more clips)
  cluster_nearby_moments: true
  cluster_window_seconds: 60
  include_context_before_seconds: 5
  include_context_after_seconds: 3
```

### Key Settings to Adjust

**interest_threshold** (0.0-1.0)
- Lower = more clips selected
- Higher = only best moments
- Default: 0.6
- Try: 0.4 for more content, 0.8 for highlights only

**Signal weights** (0.0-2.0)
- Boost important signals
- Reduce noisy signals
- Default: 0.8-1.0
- Example: Set `audio_voice_analysis.weight: 1.5` for reaction content

**Clip duration**
- `min_clip_length_seconds`: Minimum clip duration
- `max_clip_length_seconds`: Maximum clip duration
- Adjust based on content pacing

**Context inclusion**
- `include_context_before_seconds`: Lead-up time
- `include_context_after_seconds`: Follow-through time
- Important for narrative flow

## Signal Sources Explained

### audio_voice_analysis

**What it detects:**
- Laughter
- Shouting
- Excitement/high energy
- Vocal reactions

**Best for:**
- Reaction content
- Commentary streams
- Just Chatting

**How it works:**
- Analyzes voice frequency patterns
- Detects energy spikes
- Identifies characteristic patterns

**Tuning:**
- Always leave enabled
- Increase weight for reaction content
- Disable specific types if too sensitive

### audio_game_peaks

**What it detects:**
- Loud audio moments
- Sound effects
- Music beats
- Explosions/action

**Best for:**
- Gaming streams
- Music streams
- Action-heavy content

**How it works:**
- Measures audio energy (RMS)
- Finds peaks above threshold
- Tracks sustained loud periods

**Tuning:**
- Adjust `peak_threshold` (default: -20 dB)
- Lower value = more sensitive
- Higher value = only loudest moments

### visual_activity

**What it detects:**
- Fast motion
- Scene changes
- Gameplay action
- Visual transitions

**Best for:**
- Fast-paced games
- Action sequences
- Cinematic moments

**How it works:**
- Frame difference analysis
- Motion detection
- Histogram comparison for scene changes

**Tuning:**
- `motion_threshold`: Sensitivity (default: 0.3)
- `scene_change_threshold`: Scene detection (default: 30)

### silence_to_chaos

**What it detects:**
- Quiet moments followed by chaos
- Jump scares
- Unexpected events
- Dramatic transitions

**Best for:**
- Horror games
- Suspenseful content
- Surprise moments

**How it works:**
- Finds silent periods (< -40 dB)
- Looks for sudden loud moments (> -15 dB)
- Captures the transition

**Tuning:**
- `silence_threshold`: Quiet level (default: -40 dB)
- `chaos_threshold`: Loud level (default: -15 dB)

### chat_density

**What it detects:**
- Chat activity from video overlay
- Message bursts
- High engagement moments

**Best for:**
- Streams with 10+ active chatters
- Viewer interaction moments
- Chat-driven content

**How it works:**
- Motion detection in chat region
- Scrolling speed = message frequency
- No OCR needed

**Configuration:**
```yaml
chat_density:
  enabled: true
  region: [0.7, 0.0, 1.0, 1.0]  # [x1, y1, x2, y2] normalized
```

**Region setup:**
- [0.7, 0.0, 1.0, 1.0] = right 30%
- [0.0, 0.0, 0.3, 1.0] = left 30%
- Adjust based on your overlay layout

**When to disable:**
- Small streams (< 5 messages/min)
- No chat overlay visible
- Chat in non-standard location

### facecam_emotion

**What it detects:**
- Movement in facecam area
- Visible reactions
- Emotional responses

**Best for:**
- Streams with facecam
- Reaction content
- Expression-heavy commentary

**How it works:**
- Motion detection in facecam region
- Finds sudden changes
- Tracks activity spikes

**Configuration:**
```yaml
facecam_emotion:
  enabled: true
  facecam_region: [0.0, 0.7, 0.25, 1.0]  # Bottom-left 25%
```

## Workflow Examples

### Example 1: First-Time Gaming Stream

**Goal:** Create highlights from a 3-hour gaming stream

**Steps:**

1. Test signal detection:
```bash
python auto_edit.py analyze my_stream.mp4
```

2. Review detected signals, adjust if needed

3. Create preview:
```bash
python auto_edit.py edit my_stream.mp4 --preview
```

4. Watch preview, tune settings

5. Create full highlights:
```bash
python auto_edit.py edit my_stream.mp4 -d 20
```

### Example 2: Reaction Content

**Goal:** Optimize for reactions and commentary

**Steps:**

1. Edit config.yaml:
```yaml
signals:
  audio_voice_analysis:
    enabled: true
    weight: 1.5  # Boost voice detection

  facecam_emotion:
    enabled: true
    weight: 1.0

  audio_game_peaks:
    weight: 0.6  # Reduce game audio importance
```

2. Run edit:
```bash
python auto_edit.py edit reaction_stream.mp4
```

### Example 3: Stream with Active Chat

**Goal:** Include chat interaction moments

**Steps:**

1. Enable chat detection:
```bash
python auto_edit.py signal chat_density on
```

2. Configure chat region in config.yaml:
```yaml
chat_density:
  region: [0.75, 0.0, 1.0, 1.0]  # Adjust to your layout
  min_messages_per_minute: 8
```

3. Run edit:
```bash
python auto_edit.py edit stream.mp4
```

### Example 4: Building Personal Style (Phase 3)

**Goal:** Train model on your editing style

**Steps:**

1. Add training examples (5-10 pairs):
```bash
python auto_edit.py add-example raw_1.mp4 edited_1.mp4
python auto_edit.py add-example raw_2.mp4 edited_2.mp4
# ... add more
```

2. Train model:
```bash
python auto_edit.py train
```

3. Check model:
```bash
python auto_edit.py style-info
```

4. Use trained style:
```bash
python auto_edit.py set-mode my_style
python auto_edit.py edit new_stream.mp4
```

## Tips & Best Practices

### Getting Better Results

1. **Start with preview**
   - Always test with `--preview` first
   - Faster to iterate on settings
   - Only run full edit when satisfied

2. **Tune gradually**
   - Change one setting at a time
   - Run analyze after each change
   - Document what works for your content

3. **Use appropriate weights**
   - Boost signals that matter for your content
   - Reduce noisy signals
   - Typical range: 0.5-1.5

4. **Adjust threshold**
   - Lower `interest_threshold` if too few clips
   - Raise if getting too many clips
   - Sweet spot usually 0.5-0.7

### Content-Specific Tips

**Gaming Streams:**
- Enable: audio_peaks, visual_activity
- Boost: game audio weight
- Use: shorter max clip length (30s)

**Just Chatting:**
- Enable: audio_voice_analysis, facecam_emotion
- Boost: voice analysis weight
- Use: longer max clip length (45s+)

**Horror Games:**
- Enable: silence_to_chaos
- Keep: all audio signals
- Use: more context_before (setup scares)

**Competitive Gaming:**
- Enable: visual_activity, audio_peaks
- Use: tight clips (minimal context)
- Focus: action moments

### Performance Tips

1. **Large files (> 10GB)**
   - Reduce visual analysis sample rate
   - Process overnight
   - Use SSD for temp files

2. **Faster iteration**
   - Use `--preview` for testing
   - Analyze first, edit second
   - Cache audio extraction

3. **Quality vs Speed**
   - High quality: Keep all signals enabled
   - Fast preview: Disable visual_activity
   - Balance: Disable chat/facecam for general

### Common Issues

**Issue: No clips selected**
- Lower `interest_threshold` to 0.4
- Check signal detection with `analyze`
- Verify signals are enabled
- Increase signal weights

**Issue: Too many clips**
- Raise `interest_threshold` to 0.7
- Reduce signal weights
- Increase `cluster_window_seconds`

**Issue: Clips feel choppy**
- Increase `include_context_before_seconds`
- Increase `include_context_after_seconds`
- Raise `min_clip_length_seconds`

**Issue: Chat detection not working**
- Verify chat overlay visible in video
- Adjust `chat_density.region`
- Check `min_messages_per_minute`
- Ensure sufficient chat activity

**Issue: Missing important moments**
- Lower `interest_threshold`
- Enable more signals
- Check signal weights
- Review with `analyze`

### Optimizing for Upload

**YouTube:**
- Target: 15-25 minutes
- Use: tight editing (less context)
- Focus: highest-score clips

**TikTok/Shorts:**
- Target: 1-3 minutes
- Use: `--preview` with manual selection
- Focus: single best moments

**Twitter/X:**
- Target: 2-3 minutes
- Export individual clips from metadata
- Use: highest single clip

## Advanced Usage

### Batch Processing

Process multiple streams:

```bash
for video in input/*.mp4; do
  python auto_edit.py edit "$video" -d 15
done
```

### Custom Scripts

Python API usage:

```python
from auto_edit import Config, VideoProcessor, SignalDetector, ClipSelector

config = Config('config.yaml')
processor = VideoProcessor(config)
detector = SignalDetector(config)
selector = ClipSelector(config)

# Your custom logic
```

### Integration

Export clips for manual editing:

1. Generate highlights
2. Review `clip_list.txt`
3. Import timestamps into video editor
4. Fine-tune manually

## Getting Help

- Check README.md for overview
- Review USAGE.md (this file) for details
- Run commands with `--help` flag
- Open GitHub issue for bugs
- Check example configurations
