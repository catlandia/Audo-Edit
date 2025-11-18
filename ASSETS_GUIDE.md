# User Assets Guide

Welcome to the Auto Edit Asset System! This guide will help you enhance your highlight videos with custom music, sound effects, and image overlays.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Asset Types](#asset-types)
  - [Music](#music)
  - [Sound Effects](#sound-effects)
  - [Images](#images)
- [Pool vs Required Modes](#pool-vs-required-modes)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Auto Edit asset system lets you add your own media to enhance videos in two powerful ways:

1. **Pool Mode**: Assets the system can intelligently choose from based on context
2. **Required Mode**: Assets that MUST be included in every video

This gives you full control - from letting the AI pick the perfect background music, to ensuring your channel branding always appears.

---

## Quick Start

### 1. Enable Asset System

Edit `config.yaml`:

```yaml
assets:
  enabled: true  # Turn on asset integration
```

### 2. Add Your Assets

Place files in the appropriate directories:

```
music/
  pool/          # Optional music - AI picks based on video energy
  required/      # Music that MUST play

sounds/
  pool/          # Optional SFX - AI places at perfect moments
  required/      # SFX that MUST be included

images/
  pool/          # Optional images - AI shows at key moments
  required/      # Images that MUST appear (logos, sponsors, etc.)
```

### 3. Run Auto Edit

```bash
python auto_edit.py edit your_stream.mp4
```

That's it! The system will:
- Analyze your video's energy and moments
- Select appropriate pool assets
- Ensure all required assets are included
- Output an enhanced video with all assets applied

---

## Asset Types

### Music

Background music overlaid throughout your video.

**Directory**: `music/`

**Supported Formats**: `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`

#### How It Works

- **Pool Music**: Selected based on video energy level
  - High energy videos → Tracks with `high`, `epic`, or `intense` in filename
  - Low energy videos → Tracks with `low`, `chill`, or `calm` in filename
  - Default → Medium energy tracks

- **Required Music**: Played sequentially from start to finish

#### Naming Examples

```
music/pool/
  epic_battle_high.mp3        # Used for intense gaming moments
  lofi_chill_low.mp3          # Used for calm/talking segments
  background_medium.mp3       # General purpose

music/required/
  channel_intro.mp3           # Always plays first
  outro_theme.mp3             # Always plays after intro
```

#### Configuration

```yaml
assets:
  music:
    volume: 0.3              # Music volume (0-1, relative to video)
    default_duration: 30.0   # How long to play if not specified
    fade_in: true           # Fade in at start
    fade_out: true          # Fade out at end
    fade_duration: 2.0      # Fade duration in seconds
```

**Tips**:
- Keep music volume low (0.2-0.4) so it doesn't overpower your voice
- Use royalty-free music only
- Music loops automatically if shorter than video
- Music cuts if longer than video

---

### Sound Effects

Short audio clips inserted at specific moments (laughter, excitement, etc.).

**Directory**: `sounds/`

**Supported Formats**: `.mp3`, `.wav`, `.ogg`, `.m4a`

#### How It Works

- **Pool Sounds**: Intelligently placed based on detected signals
  - `laugh`, `lol` → Plays during laughter moments
  - `excite`, `hype`, `pog` → Plays during excitement
  - `shout`, `scream` → Plays during shouting
  - `wow`, `amaze` → Plays during amazing moments
  - `fail`, `sad` → Plays during fails
  - No keywords → Can play anywhere

- **Required Sounds**: Guaranteed to play at high-intensity moments

#### Naming Examples

```
sounds/pool/
  airhorn_hype.mp3           # Plays during hype moments
  laugh_track_lol.mp3        # Plays during laughter
  wow_amazed.wav             # Plays during amazing moments
  sad_trombone_fail.mp3      # Plays during fails
  generic_whoosh.mp3         # Can play anywhere

sounds/required/
  signature_sfx.mp3          # Always plays once at a peak moment
```

#### Configuration

```yaml
assets:
  sounds:
    volume: 0.7                 # Sound effect volume (0-1)
    placement_chance: 0.3       # 30% chance to place at suitable moment
    min_interval: 5.0          # Min 5 seconds between sounds
```

**Tips**:
- Keep sounds short (1-3 seconds)
- Don't overdo it - lower `placement_chance` if too many sounds
- Use clear naming to trigger at right moments
- Pool sounds can repeat; required sounds play once

---

### Images

Static images overlaid on your video (logos, sponsors, reactions, etc.).

**Directory**: `images/`

**Supported Formats**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`

**Recommended**: Use PNG with transparency for best results

#### How It Works

- **Pool Images**: Shown at high-intensity moments (limited per video)
- **Required Images**: Guaranteed to appear at specified times

#### Smart Filename Metadata

Control image behavior using keywords in filenames:

**Position Keywords**:
- `top-left`, `topleft` → Top-left corner
- `top-right`, `topright` → Top-right corner
- `bottom-left`, `bottomleft` → Bottom-left corner
- `bottom-right`, `bottomright` → Bottom-right corner
- `center` → Center of screen
- No keyword → Random corner

**Size Keywords**:
- `small`, `tiny` → 10% of screen
- (default) → 20% of screen
- `large`, `big` → 30% of screen
- `huge`, `full` → 50% of screen

**Duration** (how long to show):
- `3s`, `5s`, `10s` → Show for N seconds
- (default) → 2 seconds

**Timestamp** (required images only):
- `at30` → Show at 30 seconds
- `at120` → Show at 2:00 (120 seconds)
- No keyword → Random placement

#### Naming Examples

```
images/pool/
  reaction_surprised_center_large_3s.png    # Center, large, 3 seconds
  explosion_top-right_small.png             # Top-right, small, 2s (default)
  celebration.gif                           # Random position, default size/time

images/required/
  watermark_bottom-right_small.png           # Always show watermark
  logo_intro_center_at0_5s.png              # Show logo at start for 5s
  sponsor_bottom-left_at60_10s.png          # Sponsor at 1:00 for 10s
  subscribe_cta_center_huge_at120_8s.png    # End screen CTA
```

#### Configuration

```yaml
assets:
  images:
    max_pool_per_video: 3      # Max 3 random images per video
    placement_chance: 0.2      # 20% chance at exciting moments
    default_opacity: 0.9       # Image opacity (0-1)
```

**Tips**:
- Use PNG with transparent backgrounds for clean overlays
- Required images perfect for branding, sponsors, CTAs
- Don't clutter - keep `max_pool_per_video` low (1-3)
- Test positioning with `at0` to see it immediately

---

## Pool vs Required Modes

### Pool Mode (`pool/` subdirectory)

**What**: Assets the AI can choose from intelligently

**When to Use**:
- Background music you want matched to video energy
- Sound effects for appropriate moments
- Reaction images for exciting parts
- Content where AI selection adds value

**Behavior**:
- Music: Picks based on video intensity (high/medium/low energy)
- Sounds: Places at matching signal types (laughter, excitement, etc.)
- Images: Shows at most intense moments (limited per video)
- Can be reused multiple times (except required sounds)

**Examples**:
```
music/pool/epic_high.mp3          # AI picks for intense videos
sounds/pool/laugh_lol.mp3         # AI places during laughter
images/pool/surprised.png         # AI shows at shocking moments
```

### Required Mode (`required/` subdirectory)

**What**: Assets that MUST appear in every video

**When to Use**:
- Channel branding (logos, watermarks)
- Sponsored content (must show sponsor logo)
- Intro/outro music
- Important announcements
- Signature sounds
- Call-to-actions (subscribe, follow, etc.)

**Behavior**:
- Music: Plays sequentially from start
- Sounds: Placed at random high-intensity moments
- Images: Shown at specified timestamps (or random if not specified)
- Each asset used exactly once

**Examples**:
```
music/required/intro_theme.mp3              # Always plays first
sounds/required/channel_sfx.mp3             # Always included once
images/required/watermark_bottom-right_small.png   # Always visible
images/required/sponsor_at60_10s.png        # Sponsor at 1:00
```

---

## Configuration

### Full Configuration Options

Edit `config.yaml` to customize asset behavior:

```yaml
assets:
  enabled: true  # Master switch for all assets

  # Music Settings
  music:
    volume: 0.3              # Background music volume (0-1)
    default_duration: 30.0   # Default music length
    fade_in: true           # Fade in at start
    fade_out: true          # Fade out at end
    fade_duration: 2.0      # Fade duration in seconds

  # Sound Effects Settings
  sounds:
    volume: 0.7                 # Sound effect volume (0-1)
    placement_chance: 0.3       # Probability of placing pool sounds (0-1)
    min_interval: 5.0          # Min seconds between sound effects

  # Image Overlay Settings
  images:
    max_pool_per_video: 3      # Max pool images per video
    placement_chance: 0.2      # Probability of placing pool images (0-1)
    default_opacity: 0.9       # Image opacity (0-1)
```

### Recommended Settings

**Minimal Overlay** (subtle):
```yaml
assets:
  music:
    volume: 0.2
  sounds:
    placement_chance: 0.1
  images:
    max_pool_per_video: 1
    placement_chance: 0.1
```

**Maximum Impact** (loud & flashy):
```yaml
assets:
  music:
    volume: 0.5
  sounds:
    placement_chance: 0.5
  images:
    max_pool_per_video: 5
    placement_chance: 0.4
```

**Branding Only** (no pool assets):
```yaml
assets:
  enabled: true
# Add only required/ assets, leave pool/ empty
```

---

## Advanced Usage

### Combining with Memes

Assets work alongside the meme system! You can have:
- Meme text overlays (from `memes/`)
- Custom images (from `images/`)
- Both simultaneously!

```yaml
memes:
  enabled: true   # Text/image memes from memes/ folder
  style: both

assets:
  enabled: true   # Custom assets from music/, sounds/, images/
```

They're complementary:
- **Memes**: For humor and jokes (LMAO, POGGERS, reactions)
- **Images**: For branding and overlays (logos, sponsors, CTAs)

### Multiple Required Items

You can have multiple required assets of each type:

```
music/required/
  01_intro.mp3        # Plays first (alphabetically)
  02_main.mp3         # Plays second
  03_outro.mp3        # Plays third

sounds/required/
  signature1.mp3      # Placed at peak moment #1
  signature2.mp3      # Placed at peak moment #2

images/required/
  watermark.png                    # Random placement
  sponsor_at30_10s.png            # At 30s for 10s
  cta_at120_5s.png                # At 2:00 for 5s
```

### Energy Level Detection

Music energy is detected from filename keywords:

| Energy Level | Keywords | When Used |
|--------------|----------|-----------|
| High | `high`, `epic`, `intense`, `hype`, `energetic` | Avg intensity > 0.7 |
| Medium | (default) | Avg intensity 0.4-0.7 |
| Low | `low`, `chill`, `calm`, `relaxed`, `ambient` | Avg intensity < 0.4 |

Name your music accordingly:
```
epic_boss_fight_high.mp3
chill_lofi_beats_low.mp3
medium_background.mp3
```

### Sound Trigger Detection

Sounds are triggered by signal types:

| Trigger Type | Keywords in Filename | Placed During |
|--------------|---------------------|---------------|
| Laughter | `laugh`, `lol`, `haha` | Laughter moments |
| Excitement | `excite`, `hype`, `pog`, `wow` | Exciting moments |
| Shouting | `shout`, `scream`, `yell` | Loud moments |
| Amazing | `wow`, `amaze`, `incredible` | Amazing moments |
| Negative | `fail`, `sad`, `rip` | Failure moments |
| Generic | (no keywords) | Any moment |

### Output Files

When assets are enabled, you'll get additional output:

```
output/
  video_name_highlights.mp4           # Final video
  video_name_highlights.json          # Metadata
  asset_placements.txt                # Asset report
```

The `asset_placements.txt` shows exactly what was placed where:

```
================================================================================
ASSET PLACEMENT REPORT
================================================================================

MUSIC (1 total)
--------------------------------------------------------------------------------
  @ 0.00s - 120.00s duration [REQUIRED]
    File: intro_theme.mp3
    Energy: medium

SOUND (3 total)
--------------------------------------------------------------------------------
  @ 15.50s - 2.00s duration
    File: airhorn_hype.mp3
    Trigger: excitement

  @ 45.20s - 1.50s duration
    File: laugh_lol.mp3
    Trigger: laughter

  @ 90.00s - 2.00s duration [REQUIRED]
    File: signature_sfx.mp3
    Trigger: N/A

IMAGE (2 total)
--------------------------------------------------------------------------------
  @ 0.00s - 120.00s duration [REQUIRED]
    File: watermark_bottom-right_small.png
    Position: bottom-right
    Size: 10.0%

  @ 30.00s - 10.00s duration [REQUIRED]
    File: sponsor_logo.png
    Position: bottom-left
    Size: 20.0%

================================================================================
```

---

## Troubleshooting

### Assets Not Appearing

**Problem**: Assets aren't showing in the output video

**Solutions**:
1. Check `config.yaml` has `assets.enabled: true`
2. Verify files are in correct directories (`music/pool/`, `sounds/required/`, etc.)
3. Check file formats are supported
4. Look at `asset_placements.txt` to see what was detected
5. Try a required asset first to confirm it's working

### Music Too Loud/Quiet

**Problem**: Background music overpowers voice or can't be heard

**Solutions**:
```yaml
assets:
  music:
    volume: 0.2   # Lower number = quieter music
```

Recommended range: 0.1-0.4

### Too Many Sound Effects

**Problem**: Sound effects are annoying or too frequent

**Solutions**:
```yaml
assets:
  sounds:
    placement_chance: 0.1    # Lower = less frequent
    min_interval: 10.0      # Higher = more spacing
```

### Images Not at Right Time

**Problem**: Required image showing at wrong timestamp

**Solution**: Check filename has correct timestamp:
```
WRONG: sponsor.png
RIGHT: sponsor_at60_10s.png   # Shows at 1:00 for 10 seconds
```

### Image Position Wrong

**Problem**: Image in wrong corner or size

**Solution**: Use position and size keywords:
```
watermark_bottom-right_small.png
logo_top-left_tiny.png
banner_center_large_5s.png
```

### Music Energy Not Matching

**Problem**: Calm music on intense videos, or vice versa

**Solution**: Add energy keywords to filename:
```
BEFORE: background_music.mp3
AFTER:  background_music_high.mp3   # For intense videos
        background_music_low.mp3    # For calm videos
```

### Sound Not Triggering

**Problem**: Sound in pool but never plays

**Solutions**:
1. Check filename has trigger keyword:
   ```
   airhorn_hype.mp3      # Will play during excitement
   laugh.mp3             # Will play during laughter
   ```
2. Increase placement chance:
   ```yaml
   assets:
     sounds:
       placement_chance: 0.5   # Higher = more likely to play
   ```
3. Move to `required/` if it MUST play:
   ```
   Move: sounds/pool/important.mp3
   To:   sounds/required/important.mp3
   ```

### Transparent PNG Not Transparent

**Problem**: PNG image has white/black background instead of transparency

**Solutions**:
1. Ensure PNG has alpha channel (RGBA, not RGB)
2. Use image editor to add transparency:
   - Photoshop: Save for Web → PNG-24 → Transparency checked
   - GIMP: Layer → Transparency → Add Alpha Channel
   - Online: [remove.bg](https://www.remove.bg/) for automatic removal
3. Verify in image viewer that transparency is preserved

### Multiple Music Tracks Playing

**Problem**: Only one music track plays, even with multiple in required/

**Current Limitation**: Currently only first music track is used. This will be enhanced in future versions.

**Workaround**: Concatenate your music tracks into one file before adding to `required/`

### Performance Issues

**Problem**: Video processing is very slow with assets

**Causes**:
- Image overlays require frame-by-frame processing (slower)
- Multiple sound effects add complexity
- Large image files

**Solutions**:
1. Reduce image count:
   ```yaml
   assets:
     images:
       max_pool_per_video: 1  # Fewer images = faster
   ```
2. Compress images before adding (reduce file size)
3. Use fewer required images
4. Disable image overlays if not needed:
   ```
   # Only add music and sounds, skip images/
   ```

---

## Examples

### Example 1: Gaming Channel Branding

Goal: Add channel branding to all videos

**Setup**:
```
images/required/
  watermark_bottom-right_tiny.png
  intro_logo_center_at0_3s.png
```

**Result**: Every video gets watermark + 3-second intro logo

---

### Example 2: Hype Montage

Goal: Energetic music and sound effects for exciting moments

**Setup**:
```
music/pool/
  epic_dubstep_high.mp3
  intense_rock_high.mp3

sounds/pool/
  airhorn_hype.mp3
  wow_amaze.mp3
  lets_go_excite.wav
```

**Config**:
```yaml
assets:
  music:
    volume: 0.4  # Louder music
  sounds:
    volume: 0.8
    placement_chance: 0.5  # Frequent sounds
```

**Result**: High-energy music with frequent hype sounds at exciting moments

---

### Example 3: Sponsored Content

Goal: Ensure sponsor logo appears at specific time

**Setup**:
```
images/required/
  sponsor_logo_bottom-left_at30_15s.png
```

**Result**: Sponsor logo shows at 30 seconds for 15 seconds in every video

---

### Example 4: Calm Commentary

Goal: Subtle background music for talking/explaining content

**Setup**:
```
music/pool/
  lofi_beats_low.mp3
  ambient_chill_low.mp3
  jazz_calm_low.mp3
```

**Config**:
```yaml
assets:
  music:
    volume: 0.2  # Very quiet
  sounds:
    placement_chance: 0.0  # No sound effects
  images:
    max_pool_per_video: 0  # No images
```

**Result**: Quiet background music, no distractions

---

### Example 5: Maximum Branding

Goal: Comprehensive branding throughout video

**Setup**:
```
music/required/
  channel_intro.mp3

sounds/required/
  signature_sound.mp3

images/required/
  watermark_bottom-right_tiny.png              # Always visible
  intro_splash_center_at0_5s.png              # 5s intro
  mid_roll_cta_bottom-center_at60_8s.png      # Subscribe CTA
  end_card_center_huge_at120_10s.png          # End screen
```

**Result**: Full branded experience with intro, watermark, CTAs, and signature sound

---

## Tips & Best Practices

### Music
- Keep volume between 0.2-0.4
- Use royalty-free music only
- Match energy to your content style
- Consider music copyright even if royalty-free (check license)

### Sound Effects
- Less is more - don't overuse
- Keep sounds short (1-3 seconds)
- Use clear trigger keywords
- Test `placement_chance` to find sweet spot

### Images
- PNG with transparency looks most professional
- Watermarks should be small and subtle
- Test positioning with `at0` first
- Don't clutter - max 1-3 images
- High resolution for large overlays (1920x1080+)

### General
- Start with required assets (guaranteed to appear)
- Test with one asset type at a time
- Check `asset_placements.txt` to verify behavior
- Use pool assets for variety across multiple videos
- Keep folder organized with clear naming

---

## Need Help?

- Check each asset folder's README.md for specific guidance
- See `MEME_GUIDE.md` for meme system (separate from assets)
- Run with `--verbose` flag for detailed logs
- Check `output/asset_placements.txt` for placement report

Happy editing! 🎬🎮
