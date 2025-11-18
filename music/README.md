# Music Assets

Place background music files here to enhance your highlight videos.

## Directory Structure

- **`pool/`** - Music the system CAN choose from (intelligent selection based on video energy)
- **`required/`** - Music that MUST be included in every video

## Supported Formats

- MP3 (`.mp3`)
- WAV (`.wav`)
- OGG (`.ogg`)
- M4A (`.m4a`)
- FLAC (`.flac`)

## How It Works

### Pool Music (Optional)

Place music files in `music/pool/` and the system will intelligently select appropriate tracks based on:
- Video intensity/energy level
- Total video duration
- Overall mood of the content

**Energy Level Detection:**
- Files with `high`, `epic`, or `intense` in the name → High energy moments
- Files with `low`, `chill`, or `calm` in the name → Low energy moments
- Everything else → Medium energy

### Required Music (Must Include)

Place music files in `music/required/` and they will be automatically included in the video output. Multiple required tracks will be played sequentially.

## Naming Examples

### Pool Music
```
music/pool/epic_high.mp3          # Will be used for high-energy videos
music/pool/chill_low.mp3          # Will be used for calm moments
music/pool/background_medium.mp3  # General purpose background music
```

### Required Music
```
music/required/intro_theme.mp3    # Always played at the start
music/required/outro_music.mp3    # Always played after intro
```

## Tips

- **Volume**: Music will be mixed at a lower volume than the video audio (configurable in `config.yaml`)
- **Length**: If music is shorter than video, it will loop; if longer, it will be trimmed
- **Quality**: Use high-quality audio files (at least 192kbps) for best results
- **Copyright**: Only use royalty-free or licensed music you have rights to use

## Example Workflow

1. Add some energetic music to `music/pool/`:
   ```
   epic_battle_high.mp3
   intense_dubstep_high.mp3
   ```

2. Add calmer background tracks:
   ```
   lofi_chill_low.mp3
   ambient_calm_low.mp3
   ```

3. Add your intro music to `music/required/`:
   ```
   channel_intro.mp3
   ```

4. Run Auto Edit:
   ```bash
   python auto_edit.py edit your_stream.mp4
   ```

The system will:
- Always include your channel intro
- Select appropriate high/low energy tracks from the pool based on your content
- Mix the music at the configured volume level
