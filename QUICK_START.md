# 🚀 Quick Start - Get Auto Edit Running in 5 Minutes!

**Welcome! This is the easiest way to install and use Auto Edit.**

---

## ⚡ Super Fast Installation (Recommended)

### Step 1: Install Python (One Time Only)

**Do you have Python?** Open PowerShell and type:
```powershell
python --version
```

- **If you see a version number** (like `Python 3.11.0`): ✅ Skip to Step 2!
- **If you see an error**: ❌ Install Python:
  1. Go to: https://www.python.org/downloads/
  2. Click the big yellow "Download Python" button
  3. Run the installer
  4. **⚠️ IMPORTANT**: Check the box "Add Python to PATH"
  5. Click "Install Now"
  6. Restart your computer

### Step 2: One-Click Install Auto Edit

1. **Download** the Auto Edit folder to your computer
2. **Double-click** `INSTALL.bat`
3. **Wait** 5-10 minutes (it downloads and installs everything automatically)
4. **Done!** The GUI will open automatically

That's it! 🎉

---

## 🎬 How to Use (After Installation)

### Easy Mode - Graphical Interface

**Every time you want to create highlight videos:**

1. Double-click `run_gui.bat`
2. Click "Browse" to select your stream video
3. Adjust the duration slider (how long you want the highlights)
4. Click "Start Processing"
5. Wait (usually 10-30 minutes depending on video length)
6. Your highlight video will be in the `output` folder!

---

## 🎯 Quick Tips

### First Time Users

- **Start with Preview Mode**: Check the "Preview Mode" box for a super fast test (top 5 clips only)
- **Use 720p videos**: Smaller files process faster
- **Close other programs**: Give Auto Edit more RAM to work with

### Making Better Highlights

- **Shorter is better**: 10-20 minute highlights work best
- **Enable Memes**: Adds funny text overlays at exciting moments (fun!)
- **Add your branding**: Put your logo in `images/required/` folder (see ASSETS_GUIDE.md)

---

## ❓ Troubleshooting

### "Python is not recognized"

**Solution**: You didn't check "Add Python to PATH" during Python installation.

Fix:
1. Uninstall Python (Windows Settings → Apps)
2. Reinstall Python from https://www.python.org/downloads/
3. **CHECK THE BOX** "Add Python to PATH"
4. Run `INSTALL.bat` again

### "FFmpeg is not recognized"

**Solution**: The auto-installer failed to install FFmpeg.

Fix:
- Just run `INSTALL.bat` again - it will retry automatically
- OR manually run: `install_ffmpeg.bat`

### Installation is stuck

**Solution**: Be patient! Installing PyTorch and other AI libraries takes time.

- First install: 5-10 minutes
- Slow internet: up to 20 minutes
- Look for "Installing..." messages - if they're still appearing, it's working!

### "Out of memory" errors

**Solution**: Your computer doesn't have enough RAM.

Fix:
1. Close Chrome, Discord, and other programs
2. Edit `config.yaml`:
   ```yaml
   processing:
     max_workers: 2  # Reduce from 4
   ```
3. Try shorter videos first

### GUI won't open

**Solution**: Virtual environment issue.

Fix:
1. Open PowerShell in the Auto Edit folder
2. Run:
   ```powershell
   venv\Scripts\activate
   python auto_edit_gui.py
   ```
3. Check error messages

---

## 📁 What's in the Folders?

After installation, you'll see:

```
Audo-Edit/
├── INSTALL.bat          ← Run this FIRST (one time)
├── run_gui.bat          ← Run this EVERY TIME (easiest!)
├── run_auto_edit.bat    ← Quick mode (no GUI)
├── output/              ← Your finished videos go here!
├── music/               ← Add background music here
├── sounds/              ← Add sound effects here
├── images/              ← Add logos/branding here
├── memes/               ← Meme library
└── venv/                ← Python packages (auto-created)
```

**You only care about:**
- `run_gui.bat` - Start here!
- `output/` - Get your videos here!

---

## 🎓 Learn More

- **WINDOWS_SETUP.md** - Detailed Windows guide
- **ASSETS_GUIDE.md** - How to add music, sounds, logos
- **MEME_GUIDE.md** - Customize memes
- **README.md** - Full documentation

---

## 🆘 Still Need Help?

1. Check `WINDOWS_SETUP.md` (more detailed troubleshooting)
2. Make sure Python 3.8+ is installed
3. Make sure you have at least 8GB RAM
4. Try a shorter video first (under 2 hours)

---

## 🎉 You're Ready!

1. ✅ Run `INSTALL.bat` (one time)
2. ✅ Run `run_gui.bat` (every time)
3. ✅ Create amazing highlight videos!

**It's that simple!** Happy editing! 🎬🎮
