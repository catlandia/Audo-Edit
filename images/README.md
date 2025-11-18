# Image Assets

Place image files here to overlay on your highlight videos (separate from meme images).

## Directory Structure

- **`pool/`** - Images the system CAN use (intelligent placement at interesting moments)
- **`required/`** - Images that MUST be included in every video

## Supported Formats

- PNG (`.png`) - **Recommended for transparency**
- JPG/JPEG (`.jpg`, `.jpeg`)
- GIF (`.gif`)
- WEBP (`.webp`)

## How It Works

### Pool Images (Optional)

Place images in `images/pool/` and the system will intelligently overlay them at high-intensity moments. Limited to a few per video to avoid clutter.

**Automatic Metadata from Filename:**
Use special keywords in filenames to control placement:

**Position:**
- `top-left` or `topleft` → Top-left corner
- `top-right` or `topright` → Top-right corner
- `bottom-left` or `bottomleft` → Bottom-left corner
- `bottom-right` or `bottomright` → Bottom-right corner
- `center` → Center of screen
- No keyword → Auto (random position)

**Size:**
- `small` or `tiny` → 10% of screen
- Default (no keyword) → 20% of screen
- `large` or `big` → 30% of screen
- `huge` or `full` → 50% of screen

**Duration:**
- `3s`, `5s`, `10s` → Show for that many seconds
- Default (no keyword) → 2 seconds

### Required Images (Must Include)

Place images in `images/required/` and they will be guaranteed to appear in the video.

**Additional Metadata for Required Images:**

**Timestamp:**
- `at30` → Show at 30 seconds into the video
- `at120` → Show at 2:00 (120 seconds)
- No keyword → Random placement

## Naming Examples

### Pool Images
```
images/pool/logo_top-right_small.png         # Small logo in top-right, 2s duration
images/pool/explosion_center_large_3s.png    # Large centered explosion, 3s
images/pool/reaction_bottom-left.png         # Default size reaction in bottom-left
images/pool/banner.png                       # Random position, default size/duration
```

### Required Images
```
images/required/watermark_bottom-right_small.png    # Always show watermark
images/required/intro_logo_center_at0_5s.png        # Show at start for 5s
images/required/sponsor_bottom-left_at60_10s.png    # Show sponsor at 1:00 for 10s
images/required/end_card_center_huge.png            # Large end card at random time
```

## Tips

- **Transparency**: Use PNG files with transparent backgrounds for best overlay results
- **Resolution**: Use high-resolution images (at least 1920x1080 for full-size overlays)
- **Placement**: Max 3 pool images per video by default (configurable)
- **Branding**: Use watermarks and logos in required/ for consistent branding
- **Contrast**: Ensure images have good contrast against video backgrounds

## Use Cases

### Channel Branding
```
images/required/watermark_top-right_small.png    # Always visible
images/required/logo_intro_center_at0_3s.png     # Intro splash
```

### Sponsorships
```
images/required/sponsor_logo_bottom-left_at60_10s.png
```

### Reactions & Memes
```
images/pool/surprised_pikachu.png
images/pool/thinking_emoji.png
images/pool/celebration.gif
```

### Call-to-Actions
```
images/required/subscribe_bottom-center_huge_at120_5s.png
images/required/follow_socials_center.png
```

## Example Workflow

1. Add your channel watermark to `images/required/`:
   ```
   watermark_bottom-right_small.png
   ```

2. Add some reaction images to `images/pool/`:
   ```
   surprised_center_large.png
   celebration_top-left.gif
   thinking_bottom-right_small.png
   ```

3. Add a sponsor overlay to `images/required/`:
   ```
   sponsor_logo_bottom-left_at30_10s.png
   ```

4. Run Auto Edit:
   ```bash
   python auto_edit.py edit your_stream.mp4
   ```

The system will:
- Always include your watermark (small, bottom-right)
- Show sponsor logo at 30 seconds for 10 seconds
- Intelligently place 1-3 reaction images at exciting moments
- Blend all overlays naturally with the video

## Difference from Memes

- **Memes folder** (`memes/`) → Text overlays and meme templates for jokes
- **Images folder** (`images/`) → Branding, logos, sponsors, reactions, graphics

Both can coexist! Use memes for humor and images for branding/overlays.
