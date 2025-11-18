# Auto Edit - Windows Setup Guide

Complete setup guide for Windows users.

## Prerequisites

- Windows 10 or 11
- Python 3.8 or higher
- At least 8GB RAM (16GB+ recommended for large videos)
- 10GB+ free disk space

---

## Step-by-Step Installation

### 1. Install Python

1. Download Python from https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```powershell
   python --version
   ```
   Should show: `Python 3.8.x` or higher

### 2. Install FFmpeg

FFmpeg is required for video processing.

**Option A: Simple Method (Recommended)**

1. Download from: https://www.gyan.dev/ffmpeg/builds/
   - Get: `ffmpeg-release-essentials.zip`

2. Extract the ZIP file

3. Move the extracted folder to `C:\ffmpeg`
   - Final path should be: `C:\ffmpeg\bin\ffmpeg.exe`

4. Add FFmpeg to System PATH:
   - Press `Win + X`, select "System"
   - Click "Advanced system settings" (on the right)
   - Click "Environment Variables" button
   - Under "System variables", find "Path", click "Edit"
   - Click "New"
   - Type: `C:\ffmpeg\bin`
   - Click OK on all windows

5. **Restart PowerShell/Command Prompt**

6. Verify FFmpeg is working:
   ```powershell
   ffmpeg -version
   ```
   Should show FFmpeg version information

**Option B: Using Chocolatey (If you have it)**

```powershell
choco install ffmpeg
```

### 3. Download Auto Edit

**Option A: Download ZIP**
1. Download the repository as ZIP
2. Extract to a location like: `C:\Users\YourName\Documents\Audo-Edit`

**Option B: Using Git**
```powershell
git clone <repository-url>
cd Audo-Edit
```

### 4. Set Up Auto Edit

1. **Open PowerShell** in the Audo-Edit directory:
   - Navigate to the folder in File Explorer
   - Hold `Shift` + Right-click in the folder
   - Select "Open PowerShell window here" or "Open in Terminal"

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\activate
   ```

   You should see `(venv)` at the start of your prompt.

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

   This will take a few minutes. Grab a coffee! ☕

5. **Verify installation:**
   ```powershell
   python auto_edit.py --version
   ```

   Should show: `version 0.4.0`

---

## Quick Start - Your First Edit

Now let's create your first highlight video!

### 1. Prepare Your Video

Place your stream VOD in an easy location, like:
```
C:\Users\YourName\Videos\my_stream.mp4
```

### 2. Run Auto Edit

**Make sure your virtual environment is activated** (you should see `(venv)` in your prompt).

If not activated:
```powershell
.\venv\Scripts\activate
```

Then run:
```powershell
python auto_edit.py edit "C:\Users\YourName\Videos\my_stream.mp4"
```

**Note**: Use quotes around paths with spaces!

### 3. Check Output

Your highlight video will be in the `output\` folder:
```
output\my_stream_highlights.mp4
```

Also check:
- `output\clip_list.txt` - List of selected clips
- `output\thumbnails\` - Thumbnail images
- `output\sounds\` - Sound clips
- `output\meme_inserts.txt` - Meme placements

---

## Common Commands

**Always activate the virtual environment first:**
```powershell
.\venv\Scripts\activate
```

**Basic edit:**
```powershell
python auto_edit.py edit "C:\path\to\video.mp4"
```

**Specify output location:**
```powershell
python auto_edit.py edit "C:\path\to\video.mp4" -o "C:\path\to\output.mp4"
```

**Set target duration (in minutes):**
```powershell
python auto_edit.py edit "C:\path\to\video.mp4" -d 15
```

**Quick preview (top 5 clips only):**
```powershell
python auto_edit.py edit "C:\path\to\video.mp4" --preview
```

**Verbose output (see what's happening):**
```powershell
python auto_edit.py edit "C:\path\to\video.mp4" -v
```

**Analyze without editing:**
```powershell
python auto_edit.py analyze "C:\path\to\video.mp4"
```

**View configuration:**
```powershell
python auto_edit.py config-show
```

---

## Using Custom Assets (Music, Sounds, Images)

### 1. Enable Assets

Edit `config.yaml` in the Audo-Edit folder:

Change this line:
```yaml
assets:
  enabled: false
```

To:
```yaml
assets:
  enabled: true
```

### 2. Add Your Files

Place files in these folders:

**Background Music:**
```
music\pool\              - AI picks based on video energy
music\required\          - Always played
```

**Sound Effects:**
```
sounds\pool\             - AI places at funny/exciting moments
sounds\required\         - Always included
```

**Images (Logos, Sponsors, etc.):**
```
images\pool\             - AI shows at key moments
images\required\         - Always shown (branding, sponsors)
```

### 3. Smart Naming Examples

**Music:**
```
music\pool\epic_battle_high.mp3       - High energy videos
music\pool\lofi_chill_low.mp3        - Low energy videos
music\required\channel_intro.mp3     - Always plays first
```

**Sounds:**
```
sounds\pool\airhorn_hype.mp3         - Plays during excitement
sounds\pool\laugh_lol.mp3            - Plays during laughter
sounds\required\signature_sfx.mp3    - Always included once
```

**Images:**
```
images\required\watermark_bottom-right_small.png    - Small watermark
images\required\sponsor_at60_10s.png                - Show at 1:00 for 10s
images\pool\reaction_surprised.png                  - Random placement
```

See `ASSETS_GUIDE.md` for complete documentation!

---

## Troubleshooting

### "python is not recognized"

**Solution:**
1. Reinstall Python from https://www.python.org/downloads/
2. **Check "Add Python to PATH"** during installation
3. Restart PowerShell

### "ffmpeg is not recognized"

**Solution:**
1. Make sure you added `C:\ffmpeg\bin` to PATH (Step 2.4 above)
2. **Restart PowerShell** (important!)
3. Verify with: `ffmpeg -version`

### "No module named 'X'"

**Solution:**
1. Make sure virtual environment is activated: `.\venv\Scripts\activate`
2. Reinstall dependencies: `pip install -r requirements.txt`

### Virtual environment won't activate

**Solution:**
If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:
```powershell
.\venv\Scripts\activate
```

### "Out of Memory" errors

**Solutions:**
1. Close other applications
2. Edit `config.yaml`, reduce:
   ```yaml
   processing:
     max_workers: 2  # Reduce from 4
   ```
3. Process shorter videos first
4. Upgrade RAM if possible

### Path errors or "File not found"

**Solutions:**
- Always use quotes around paths: `"C:\path\to\file.mp4"`
- Use full paths instead of relative paths
- Avoid special characters in filenames
- Check the file actually exists

### Video won't process

**Check:**
1. Video file format (MP4, MKV, AVI, MOV should work)
2. Video isn't corrupted (can you play it in VLC?)
3. You have enough disk space (check `temp\` folder)
4. FFmpeg is installed correctly: `ffmpeg -version`

### Processing is very slow

**Normal:**
- 2-hour stream: ~10-15 minutes
- 4-hour stream: ~20-30 minutes

**To speed up:**
1. Reduce target duration: `-d 10` instead of `-d 20`
2. Use `--preview` for quick tests
3. Close other programs
4. Disable visual analysis if not needed (edit `config.yaml`)

---

## Performance Tips

### For Best Results:

1. **Close unnecessary programs** while processing
2. **Use SSD** for input/output if available
3. **Adjust settings** in `config.yaml`:
   ```yaml
   processing:
     max_workers: 4  # Lower if you have less than 16GB RAM
   ```

### For Faster Processing:

1. **Use preview mode** for testing:
   ```powershell
   python auto_edit.py edit video.mp4 --preview
   ```

2. **Reduce target duration:**
   ```powershell
   python auto_edit.py edit video.mp4 -d 10
   ```

3. **Disable memes** temporarily in `config.yaml`:
   ```yaml
   memes:
     enabled: false
   ```

---

## Daily Workflow

Here's a typical workflow for Windows:

```powershell
# 1. Navigate to Auto Edit folder
cd C:\Users\YourName\Documents\Audo-Edit

# 2. Activate virtual environment
.\venv\Scripts\activate

# 3. Process your stream
python auto_edit.py edit "D:\Streams\latest_stream.mp4" -d 15 -v

# 4. Check output
explorer output\

# 5. Done! Deactivate when finished
deactivate
```

---

## Tips for Streamers

### Consistent Branding

Add your branding once, use it forever:

```
images\required\
  watermark_bottom-right_tiny.png
  intro_logo_center_at0_3s.png
```

### Highlight Channels

**Gaming Channel:**
```yaml
# config.yaml
signals:
  audio_voice_analysis:
    enabled: true
    weight: 1.2
  visual_activity:
    enabled: true
    weight: 1.0
```

**Talking/Commentary Channel:**
```yaml
signals:
  audio_voice_analysis:
    enabled: true
    weight: 1.5
  visual_activity:
    enabled: false
```

### Quick Testing

Always test with preview first:
```powershell
python auto_edit.py edit video.mp4 --preview -v
```

Then do full edit:
```powershell
python auto_edit.py edit video.mp4 -d 20
```

---

## Getting Help

- Check `README.md` for full documentation
- See `ASSETS_GUIDE.md` for asset system details
- See `MEME_GUIDE.md` for meme customization
- Run `python auto_edit.py --help` for all commands

---

## Uninstallation

To remove Auto Edit:

1. Deactivate virtual environment: `deactivate`
2. Delete the Audo-Edit folder
3. (Optional) Remove FFmpeg from PATH and delete `C:\ffmpeg`

---

**You're all set! Happy editing!** 🎬🎮
