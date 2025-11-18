# Sound Effects Assets

Place sound effect files here to enhance key moments in your highlight videos.

## Directory Structure

- **`pool/`** - Sound effects the system CAN use (intelligent placement at appropriate moments)
- **`required/`** - Sound effects that MUST be included in every video

## Supported Formats

- MP3 (`.mp3`)
- WAV (`.wav`)
- OGG (`.ogg`)
- M4A (`.m4a`)

## How It Works

### Pool Sounds (Optional)

Place sound effects in `sounds/pool/` and the system will intelligently insert them at appropriate moments based on:
- Detected signal types (laughter, excitement, shouting, etc.)
- Signal intensity
- Context of the moment

**Trigger Type Detection:**
The system automatically detects trigger types from filenames:
- `laugh`, `lol` → Played during laughter moments
- `excite`, `hype`, `pog` → Played during excitement/hype moments
- `shout`, `scream` → Played during shouting moments
- `wow`, `amaze` → Played during amazing moments
- `fail`, `sad` → Played during negative/fail moments
- No keywords → Can be used for any moment

### Required Sounds (Must Include)

Place sound effects in `sounds/required/` and they will be guaranteed to appear in the video at high-intensity moments.

## Naming Examples

### Pool Sounds
```
sounds/pool/laugh_track.mp3       # Plays during laughter moments
sounds/pool/airhorn_hype.mp3      # Plays during excitement
sounds/pool/scream_sound.mp3      # Plays during shouting
sounds/pool/wow_amazed.mp3        # Plays during amazing moments
sounds/pool/sad_trombone_fail.mp3 # Plays during fails
sounds/pool/generic_whoosh.mp3    # Can play at any moment
```

### Required Sounds
```
sounds/required/signature_sound.mp3  # Always included somewhere
sounds/required/intro_sfx.mp3        # Always included
```

## Tips

- **Duration**: Keep sound effects short (1-3 seconds) for best results
- **Volume**: Sound effects are mixed to blend with video audio
- **Placement**: Pool sounds have ~30% chance of playing at suitable moments (configurable)
- **Reusability**: Pool sounds can be reused multiple times; required sounds play once
- **Timing**: Sounds are timed to match the peak of the detected moment

## Example Workflow

1. Add some hype sound effects to `sounds/pool/`:
   ```
   airhorn_hype.mp3
   lets_go_excite.mp3
   poggers_hype.wav
   ```

2. Add laughter sounds:
   ```
   laugh_track_1.mp3
   lmao_laugh.mp3
   ```

3. Add a signature sound to `sounds/required/`:
   ```
   channel_sfx.mp3
   ```

4. Run Auto Edit:
   ```bash
   python auto_edit.py edit your_stream.mp4
   ```

The system will:
- Always include your channel signature sound at a hype moment
- Intelligently place airhorns during excitement peaks
- Add laughter tracks during funny moments
- Mix all sounds at appropriate volumes

## Sound Effect Resources

Free sound effect websites:
- [Freesound.org](https://freesound.org/) - Community uploaded sounds (CC licensed)
- [Zapsplat](https://www.zapsplat.com/) - Free for personal/commercial use
- [Mixkit](https://mixkit.co/free-sound-effects/) - Free sound effects
- [BBC Sound Effects](http://bbcsfx.acropolis.org.uk/) - 16,000+ BBC archive sounds

**Remember to check licenses before using!**
