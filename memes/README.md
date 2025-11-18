# Meme Library

Place your meme images here for automatic insertion into videos!

## Naming Convention

Name your meme files based on the type of moment they should appear in:

- `laughing_*.png/jpg` - For laughter moments
- `lmao_*.png/jpg` - For extreme laughter
- `screaming_*.png/jpg` - For shouting moments
- `shocked_*.png/jpg` - For surprise/shocked moments
- `hype_*.png/jpg` - For excitement/hype moments
- `poggers_*.png/jpg` - For exciting moments
- `epic_*.png/jpg` - For epic moments
- `loud_*.png/jpg` - For loud audio peaks
- `boom_*.png/jpg` - For explosion/impact moments

## Supported Formats

- PNG (recommended for transparency)
- JPG

## Image Requirements

- Transparent background (PNG) works best
- Recommended size: 512x512 to 1024x1024
- Keep file sizes reasonable (< 5MB)

## Examples

Good filenames:
- `laughing_emoji.png`
- `shocked_pikachu.png`
- `poggers_emote.png`
- `boom_explosion.png`
- `hype_lets_go.jpg`

## Auto-Generated Memes

Text-based memes are generated automatically. You can also add your own images!

## Usage

Memes are automatically detected and inserted based on:
1. Signal type (laughter, shouting, etc.)
2. Signal intensity (higher = more likely)
3. Your meme library contents

Enable/disable in `config.yaml`:
```yaml
memes:
  enabled: true
  style: both  # text, image, or both
```
