# Meme & Image Insertion Guide

Complete guide to using Auto Edit's meme insertion features!

## Overview

Auto Edit can automatically insert memes, images, and text overlays into your highlight videos at the perfect moments. The system analyzes your clips and intelligently places memes based on:

- **Signal types** (laughter, shouting, excitement, etc.)
- **Intensity** (higher intensity = more likely to get a meme)
- **Moment context** (what's happening in the clip)

## Quick Start

### 1. Enable Memes

Memes are enabled by default! Check `config.yaml`:

```yaml
memes:
  enabled: true  # Set to false to disable
  style: text  # 'text', 'image', or 'both'
```

### 2. Run Auto Edit

```bash
python auto_edit.py edit your_stream.mp4
```

Your highlights will automatically include memes at funny/exciting moments!

## Meme Styles

### Text Only (Default)

Pure text overlays with context-aware messages:

```yaml
memes:
  style: text
```

**Examples:**
- Laughter moments: "LMAO", "DEAD 💀", "IM DYING"
- Shouting: "WHAT!?", "NO WAY!", "BRUH"
- Excitement: "LETS GO!", "POGGERS", "HYPE!"

### Image Only

Uses images from your meme library:

```yaml
memes:
  style: image
```

### Both (Text + Images)

Combines text and images for maximum impact:

```yaml
memes:
  style: both
```

## Adding Your Own Memes

### 1. Create Memes Folder

Already done! The `memes/` folder is ready.

### 2. Add Meme Images

Place your meme images in `memes/` with descriptive names:

```
memes/
├── laughing_emoji.png
├── shocked_pikachu.png
├── poggers_emote.png
├── boom_explosion.jpg
├── hype_lets_go.png
└── dead_skull.png
```

### 3. Naming Convention

Name files based on when they should appear:

- `laughing_*` - Laughter moments
- `shocked_*` - Surprise/shock moments
- `hype_*` - Excitement/hype moments
- `boom_*` - Loud/explosion moments
- `poggers_*` - Epic/exciting moments
- `screaming_*` - Shouting moments

## Meme Insertion Logic

### When Memes Are Inserted

Memes appear when:

1. **High Intensity** - Signal intensity > 0.7
2. **Multiple Signals** - 2+ strong signals at once
3. **Meme-Worthy Types** - Laughter, shouting, shock, reactions

### Positioning

Memes are smartly positioned based on moment type:

| Moment Type | Position |
|-------------|----------|
| Laughter | Bottom center |
| Shouting | Center |
| Excitement | Top center |
| Audio peak | Top |
| Facecam reaction | Top right |
| Chat activity | Bottom right |

### Duration

- Base duration: 2 seconds (configurable)
- Adapts to clip length (max 30% of clip)
- Intensity affects opacity and size

## Configuration Options

### Basic Settings

```yaml
memes:
  enabled: true
  style: both  # text, image, or both
  intensity_threshold: 0.5  # Minimum intensity (0-1)
  max_per_clip: 2  # Max memes per clip
```

### Advanced Settings

```yaml
memes:
  default_duration: 2.0  # Seconds
  default_size: 0.25  # Relative to screen (0-1)
  default_opacity: 0.9  # Transparency (0-1)
  meme_library: ./memes  # Custom path
```

## Custom Text Templates

Want custom text? Edit `auto_edit/meme_generator.py`:

```python
TEXT_TEMPLATES = {
    'laughter': ['LMAO', 'DEAD', 'YOUR CUSTOM TEXT'],
    'excitement': ['POGGERS', 'HYPE', 'YOUR CUSTOM HYPE'],
}
```

## Image Requirements

### Format
- **PNG** (recommended) - Supports transparency
- **JPG** - Solid backgrounds

### Size
- Recommended: 512x512 to 1024x1024
- Max: 2048x2048 (larger = slower processing)
- Keep under 5MB per file

### Transparency
- Use PNG with alpha channel for best results
- Transparent backgrounds blend naturally

## Examples

### Example 1: Twitch Emote Style

Add popular emotes:

```
memes/
├── poggers_pepe.png
├── laughing_omegalul.png
├── shocked_pog.png
└── hype_hypers.gif
```

### Example 2: Classic Memes

Add internet classics:

```
memes/
├── shocked_pikachu.png
├── drake_approval.png
├── distracted_boyfriend.jpg
└── surprised_tom.png
```

### Example 3: Custom Branding

Add your own branding:

```
memes/
├── yourbrand_logo.png
├── yourbrand_hype.png
└── yourbrand_reaction.png
```

## Meme Output

After editing, check:

```
output/
├── highlights.mp4  # Video with memes!
└── meme_inserts.txt  # List of all inserted memes
```

### Meme List Format

```
Meme 1 (Clip 0):
  Timestamp: 125.50s
  Duration: 2.00s
  Type: laughter
  Text: LMAO
  Image: laughing_emoji.png
  Position: bottom
```

## Tips & Tricks

### 1. Test Different Styles

Try each style to see what fits your content:

```bash
# Text only (fast, works everywhere)
sed -i 's/style: .*/style: text/' config.yaml
python auto_edit.py edit stream.mp4

# Images (requires meme library)
sed -i 's/style: .*/style: image/' config.yaml
python auto_edit.py edit stream.mp4

# Both (maximum impact)
sed -i 's/style: .*/style: both/' config.yaml
python auto_edit.py edit stream.mp4
```

### 2. Adjust Intensity Threshold

Too many memes? Increase threshold:

```yaml
intensity_threshold: 0.7  # Only very intense moments
```

Too few? Decrease:

```yaml
intensity_threshold: 0.4  # More memes
```

### 3. Disable for Serious Content

For professional/serious content:

```yaml
memes:
  enabled: false
```

### 4. Per-Signal Control

Want memes only for laughter? Disable other signals:

```yaml
signals:
  audio_voice_analysis:
    enabled: true  # Keeps laughter

  audio_game_peaks:
    enabled: false  # No memes for loud sounds
```

## Advanced: Creating Meme Templates

Auto Edit can generate classic meme templates:

```python
from auto_edit import MemeGenerator, Config

cfg = Config()
meme_gen = MemeGenerator(cfg)

# Create "TOP TEXT / BOTTOM TEXT" meme
meme_gen.create_meme_template(
    text_top="WHEN THE",
    text_bottom="IMPOSTER IS SUS",
    background_color=(255, 0, 0)
)
```

## Troubleshooting

### No Memes Appearing

**Check:**
1. Memes enabled: `memes.enabled: true`
2. Intensity threshold not too high
3. Meme-worthy moments exist (laughter, excitement, etc.)
4. Check `output/meme_inserts.txt` for analysis

### Images Not Loading

**Fix:**
1. Check image format (PNG/JPG)
2. Verify file paths in `memes/`
3. Check file permissions
4. Look for errors in console output

### Memes Too Big/Small

**Adjust size:**

```yaml
memes:
  default_size: 0.15  # Smaller (15% of screen)
  default_size: 0.35  # Bigger (35% of screen)
```

### Memes Too Transparent

**Adjust opacity:**

```yaml
memes:
  default_opacity: 1.0  # Fully opaque
```

## Performance Notes

- **Text memes**: Very fast, minimal overhead
- **Image memes**: Slower, depends on image size
- **Both**: Slowest, but most impact

For quick edits, use `style: text`.

## Best Practices

1. **Start simple** - Use text mode first
2. **Build library gradually** - Add 5-10 good memes
3. **Match your brand** - Use memes that fit your style
4. **Test threshold** - Adjust intensity_threshold for your content
5. **Review output** - Check meme_inserts.txt to see what was placed

## Integration with Other Features

Memes work alongside:

- ✅ Thumbnail extraction
- ✅ Sound clip extraction
- ✅ All signal detection modes
- ✅ Style learning (Phase 3)

## Community Meme Packs

Want to share meme packs? Create a folder structure:

```
my-meme-pack/
├── README.md
├── laughing/
│   ├── lmao_1.png
│   └── lmao_2.png
├── shocked/
│   ├── shock_1.png
│   └── shock_2.png
└── hype/
    ├── hype_1.png
    └── hype_2.png
```

Then copy to `memes/` folder!

## Example Workflow

1. **Record stream** (2-4 hours)
2. **Run Auto Edit**
   ```bash
   python auto_edit.py edit stream.mp4 -d 15
   ```
3. **Check meme_inserts.txt** - See what memes were added
4. **Add custom memes** - Put your favorites in `memes/`
5. **Re-run if needed** - Tweak settings and re-edit
6. **Upload** - Share your meme-enhanced highlights!

## FAQ

**Q: Can I disable memes for specific moments?**
A: Yes, disable the relevant signals or increase intensity_threshold.

**Q: Can I use GIFs?**
A: Currently PNG/JPG only. GIFs may be added in future versions.

**Q: How many memes is too many?**
A: Default max_per_clip: 2 is balanced. 3+ can be overwhelming.

**Q: Can I customize text color/font?**
A: Yes! Edit `meme_generator.py` and modify the text rendering section.

**Q: Do memes work with preview mode?**
A: Yes! Memes are inserted in preview mode too.

## Support

Having issues? Check:
1. README.md - General docs
2. USAGE.md - Detailed usage
3. This guide - Meme-specific help
4. GitHub Issues - Report bugs

Happy meming! 🎭🔥
