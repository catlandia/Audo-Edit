#!/usr/bin/env python3
"""
Auto Edit GUI - Graphical User Interface for Auto Edit
Easy-to-use Windows application for creating highlight videos
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import sys
import os
from pathlib import Path
import yaml


class AutoEditGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Edit - Highlight Video Creator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Variables
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.target_duration = tk.IntVar(value=20)
        self.preview_mode = tk.BooleanVar(value=False)
        self.verbose_mode = tk.BooleanVar(value=False)
        self.memes_enabled = tk.BooleanVar(value=True)
        self.assets_enabled = tk.BooleanVar(value=False)

        # New variables for advanced features
        self.editing_mode = tk.StringVar(value="general_interest")
        self.memes_folder = tk.StringVar(value="./memes")
        self.music_folder = tk.StringVar(value="./music")
        self.sounds_folder = tk.StringVar(value="./sounds")
        self.images_folder = tk.StringVar(value="./images")

        # Force asset options - make ALL items from folders required
        self.force_all_images = tk.BooleanVar(value=False)
        self.force_all_sounds = tk.BooleanVar(value=False)
        self.force_all_music = tk.BooleanVar(value=False)

        # Image opacity control (0-100%)
        self.image_opacity = tk.IntVar(value=100)

        self.processing = False
        self.process = None

        # Load config
        self.config_path = Path("config.yaml")
        self.load_config()

        # Setup UI
        self.setup_ui()

        # Update button states after UI is setup
        self.update_all_toggle_buttons()

    def load_config(self):
        """Load configuration from config.yaml"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self.target_duration.set(config.get('output', {}).get('target_duration_minutes', 20))
                    self.memes_enabled.set(config.get('memes', {}).get('enabled', True))
                    self.assets_enabled.set(config.get('assets', {}).get('enabled', False))

                    # Load editing mode
                    self.editing_mode.set(config.get('active_mode', 'general_interest'))

                    # Load custom folders
                    self.memes_folder.set(config.get('memes', {}).get('meme_library', './memes'))
                    self.music_folder.set(config.get('assets', {}).get('music_folder', './music'))
                    self.sounds_folder.set(config.get('assets', {}).get('sounds_folder', './sounds'))
                    self.images_folder.set(config.get('assets', {}).get('images_folder', './images'))

                    # Load force asset options
                    self.force_all_images.set(config.get('assets', {}).get('force_all_images', False))
                    self.force_all_sounds.set(config.get('assets', {}).get('force_all_sounds', False))
                    self.force_all_music.set(config.get('assets', {}).get('force_all_music', False))

                    # Load image opacity
                    self.image_opacity.set(config.get('assets', {}).get('image_opacity', 100))
        except Exception as e:
            print(f"Warning: Could not load config: {e}")

    def save_config(self):
        """Save current settings to config.yaml"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)

                # Update config
                if 'output' not in config:
                    config['output'] = {}
                config['output']['target_duration_minutes'] = self.target_duration.get()

                if 'memes' not in config:
                    config['memes'] = {}
                config['memes']['enabled'] = self.memes_enabled.get()
                config['memes']['meme_library'] = self.memes_folder.get()

                if 'assets' not in config:
                    config['assets'] = {}
                config['assets']['enabled'] = self.assets_enabled.get()
                config['assets']['music_folder'] = self.music_folder.get()
                config['assets']['sounds_folder'] = self.sounds_folder.get()
                config['assets']['images_folder'] = self.images_folder.get()
                config['assets']['force_all_images'] = self.force_all_images.get()
                config['assets']['force_all_sounds'] = self.force_all_sounds.get()
                config['assets']['force_all_music'] = self.force_all_music.get()
                config['assets']['image_opacity'] = self.image_opacity.get()

                # Save editing mode
                config['active_mode'] = self.editing_mode.get()

                # Save config
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

                self.log("Settings saved to config.yaml")
        except Exception as e:
            self.log(f"Error saving config: {e}")

    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        title_label = ttk.Label(
            title_frame,
            text="🎬 Auto Edit - Highlight Video Creator",
            font=("Arial", 16, "bold")
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Automatically create highlight videos from your streams",
            font=("Arial", 10)
        )
        subtitle_label.pack()

        # Main container with notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Tab 1: Basic Settings (with scrolling)
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Settings")

        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(basic_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(basic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="10")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.setup_basic_tab(scrollable_frame)

        # Tab 2: Advanced Settings
        advanced_frame = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_frame, text="Advanced Settings")
        self.setup_advanced_tab(advanced_frame)

        # Tab 3: AI Training
        training_frame = ttk.Frame(notebook, padding="10")
        notebook.add(training_frame, text="AI Training")
        self.setup_training_tab(training_frame)

        # Tab 4: Output Log
        log_frame = ttk.Frame(notebook, padding="10")
        notebook.add(log_frame, text="Output Log")
        self.setup_log_tab(log_frame)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(self.root, textvariable=self.status_var)
        status_label.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=2)

        # Control buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))

        self.start_button = ttk.Button(
            button_frame,
            text="🚀 Start Processing",
            command=self.start_processing,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.stop_button = ttk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self.stop_processing,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.output_button = ttk.Button(
            button_frame,
            text="📁 Open Output Folder",
            command=self.open_output_folder
        )
        self.output_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def setup_basic_tab(self, parent):
        """Setup the basic settings tab"""
        # Input video selection
        input_frame = ttk.LabelFrame(parent, text="Input Video", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(input_frame, textvariable=self.video_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="Browse...", command=self.browse_video).pack(side=tk.LEFT)

        # Output folder (optional)
        output_frame = ttk.LabelFrame(parent, text="Output Folder (Optional)", padding="10")
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(output_frame, textvariable=self.output_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="Choose Folder...", command=self.browse_output).pack(side=tk.LEFT)

        hint_label = ttk.Label(output_frame, text="Leave empty to use default output folder, or choose a folder to save there", font=("Arial", 8), foreground="gray")
        hint_label.pack(anchor=tk.W, pady=(5, 0))

        # Duration settings
        duration_frame = ttk.LabelFrame(parent, text="Target Duration", padding="10")
        duration_frame.pack(fill=tk.X, pady=5)

        duration_label = ttk.Label(duration_frame, text=f"Target video length: {self.target_duration.get()} minutes")
        duration_label.pack(anchor=tk.W)

        def update_duration_label(val):
            duration_label.config(text=f"Target video length: {int(float(val))} minutes")

        duration_slider = ttk.Scale(
            duration_frame,
            from_=5,
            to=60,
            variable=self.target_duration,
            orient=tk.HORIZONTAL,
            command=update_duration_label
        )
        duration_slider.pack(fill=tk.X, pady=5)

        # Quick options
        options_frame = ttk.LabelFrame(parent, text="Quick Options", padding="10")
        options_frame.pack(fill=tk.X, pady=5)

        # Preview mode toggle button
        preview_row = ttk.Frame(options_frame)
        preview_row.pack(fill=tk.X, pady=2)
        ttk.Label(preview_row, text="Preview Mode (Top 5 clips only - fast):").pack(side=tk.LEFT, padx=(0, 10))
        self.preview_btn = tk.Button(preview_row, text="OFF", command=self.toggle_preview_mode,
                                     width=10, relief=tk.RAISED, bg="#f0f0f0")
        self.preview_btn.pack(side=tk.LEFT)

        # Verbose mode toggle button
        verbose_row = ttk.Frame(options_frame)
        verbose_row.pack(fill=tk.X, pady=2)
        ttk.Label(verbose_row, text="Verbose Output (Show detailed progress):").pack(side=tk.LEFT, padx=(0, 10))
        self.verbose_btn = tk.Button(verbose_row, text="OFF", command=self.toggle_verbose_mode,
                                     width=10, relief=tk.RAISED, bg="#f0f0f0")
        self.verbose_btn.pack(side=tk.LEFT)

        # Editing Mode
        mode_frame = ttk.LabelFrame(parent, text="Editing Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=5)

        ttk.Label(mode_frame, text="Select how the AI picks clips:").pack(anchor=tk.W, pady=(0, 5))

        ttk.Radiobutton(
            mode_frame,
            text="General Interest (Default - works for everyone)",
            variable=self.editing_mode,
            value="general_interest"
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            mode_frame,
            text="My Style (Learns your preferences - needs training)",
            variable=self.editing_mode,
            value="my_style"
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            mode_frame,
            text="Hybrid (Mix of both - best after training)",
            variable=self.editing_mode,
            value="hybrid"
        ).pack(anchor=tk.W, pady=2)

        # Features
        features_frame = ttk.LabelFrame(parent, text="Features", padding="10")
        features_frame.pack(fill=tk.X, pady=5)

        # Memes toggle button
        memes_row = ttk.Frame(features_frame)
        memes_row.pack(fill=tk.X, pady=2)
        ttk.Label(memes_row, text="Memes (Automatic meme insertion at funny moments):").pack(side=tk.LEFT, padx=(0, 10))
        self.memes_btn = tk.Button(memes_row, text="OFF", command=self.toggle_memes,
                                   width=10, relief=tk.RAISED, bg="#f0f0f0")
        self.memes_btn.pack(side=tk.LEFT)

        # Assets toggle button
        assets_row = ttk.Frame(features_frame)
        assets_row.pack(fill=tk.X, pady=2)
        ttk.Label(assets_row, text="Custom Assets (Music, sounds, images from folders):").pack(side=tk.LEFT, padx=(0, 10))
        self.assets_btn = tk.Button(assets_row, text="OFF", command=self.toggle_assets,
                                    width=10, relief=tk.RAISED, bg="#f0f0f0")
        self.assets_btn.pack(side=tk.LEFT)

        ttk.Label(
            features_frame,
            text="Note: Thumbnails and sound clips are always extracted",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W, pady=(5, 0))

        # Custom Folders
        folders_frame = ttk.LabelFrame(parent, text="Custom Asset Folders (Optional)", padding="10")
        folders_frame.pack(fill=tk.X, pady=5)

        # Memes folder
        memes_row = ttk.Frame(folders_frame)
        memes_row.pack(fill=tk.X, pady=2)
        ttk.Label(memes_row, text="Memes:", width=10).pack(side=tk.LEFT)
        ttk.Entry(memes_row, textvariable=self.memes_folder, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(memes_row, text="Browse...", command=self.browse_memes_folder).pack(side=tk.LEFT)

        # Sounds folder
        sounds_row = ttk.Frame(folders_frame)
        sounds_row.pack(fill=tk.X, pady=2)
        ttk.Label(sounds_row, text="Sounds:", width=10).pack(side=tk.LEFT)
        ttk.Entry(sounds_row, textvariable=self.sounds_folder, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(sounds_row, text="Browse...", command=self.browse_sounds_folder).pack(side=tk.LEFT, padx=2)
        self.force_sounds_btn = tk.Button(sounds_row, text="Force ALL: OFF", command=self.toggle_force_sounds,
                                         width=15, relief=tk.RAISED, bg="#f0f0f0")
        self.force_sounds_btn.pack(side=tk.LEFT, padx=5)

        # Music folder
        music_row = ttk.Frame(folders_frame)
        music_row.pack(fill=tk.X, pady=2)
        ttk.Label(music_row, text="Music:", width=10).pack(side=tk.LEFT)
        ttk.Entry(music_row, textvariable=self.music_folder, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(music_row, text="Browse...", command=self.browse_music_folder).pack(side=tk.LEFT, padx=2)
        self.force_music_btn = tk.Button(music_row, text="Force ALL: OFF", command=self.toggle_force_music,
                                        width=15, relief=tk.RAISED, bg="#f0f0f0")
        self.force_music_btn.pack(side=tk.LEFT, padx=5)

        # Images folder
        images_row = ttk.Frame(folders_frame)
        images_row.pack(fill=tk.X, pady=2)
        ttk.Label(images_row, text="Images:", width=10).pack(side=tk.LEFT)
        ttk.Entry(images_row, textvariable=self.images_folder, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(images_row, text="Browse...", command=self.browse_images_folder).pack(side=tk.LEFT, padx=2)
        self.force_images_btn = tk.Button(images_row, text="Force ALL: OFF", command=self.toggle_force_images,
                                         width=15, relief=tk.RAISED, bg="#f0f0f0")
        self.force_images_btn.pack(side=tk.LEFT, padx=5)

        # Image opacity slider
        opacity_row = ttk.Frame(folders_frame)
        opacity_row.pack(fill=tk.X, pady=(5, 2))
        ttk.Label(opacity_row, text="Image Opacity:", width=12).pack(side=tk.LEFT)
        opacity_label = ttk.Label(opacity_row, text=f"{self.image_opacity.get()}%", width=5)
        opacity_label.pack(side=tk.RIGHT, padx=5)

        def update_opacity_label(val):
            opacity_label.config(text=f"{int(float(val))}%")

        opacity_slider = ttk.Scale(
            opacity_row,
            from_=0,
            to=100,
            variable=self.image_opacity,
            orient=tk.HORIZONTAL,
            command=update_opacity_label
        )
        opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Label(
            folders_frame,
            text="Tip: 'Force ALL' makes every file required. Opacity: 0%=invisible, 100%=solid",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor=tk.W, pady=(5, 0))

    def setup_advanced_tab(self, parent):
        """Setup the advanced settings tab"""
        info_text = """Advanced Settings

These settings are loaded from config.yaml. You can modify them there for fine-tuned control.

Signal Detection:
- Audio voice analysis (laughter, shouting, excitement)
- Audio peaks detection
- Visual activity (motion, scene changes)
- Silence-to-chaos patterns

Output Settings:
- Min/max clip length
- Video quality and codec
- FPS and resolution

Asset Settings (when enabled):
- Music volume and placement
- Sound effect triggers
- Image overlay positioning

Meme Settings (when enabled):
- Meme style (text, image, or both)
- Intensity threshold
- Max memes per clip

See README.md and ASSETS_GUIDE.md for detailed documentation.

To edit advanced settings:
1. Open config.yaml in a text editor
2. Modify the settings
3. Save and restart Auto Edit GUI
        """

        text_widget = tk.Text(parent, wrap=tk.WORD, height=25, width=70)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_widget.insert(1.0, info_text)
        text_widget.config(state=tk.DISABLED)

        # Button to open config
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="📝 Open config.yaml",
            command=self.open_config
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="📄 Open README.md",
            command=self.open_readme
        ).pack(side=tk.LEFT, padx=5)

    def setup_training_tab(self, parent):
        """Setup the AI training tab"""
        # Title and description
        title = ttk.Label(parent, text="AI Style Training", font=("TkDefaultFont", 14, "bold"))
        title.pack(pady=(0, 10))

        info_text = """Train Auto Edit to learn YOUR editing style!

How it works:
1. Put original videos in learning/original/
2. Put your edited versions in learning/edited/ (same filename!)
3. Click 'Train AI' button below
4. AI learns your preferences and applies them to future videos

The AI will:
- Learn which moments you keep vs cut
- Learn your preferred clip lengths
- Learn your pacing and rhythm
- Remember what types of action you prefer

Training Status:"""

        info_label = ttk.Label(parent, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=(0, 10), padx=10)

        # Status frame
        status_frame = ttk.LabelFrame(parent, text="Training Status", padding="10")
        status_frame.pack(fill=tk.X, padx=10, pady=10)

        self.training_status_label = ttk.Label(status_frame, text="Loading...", justify=tk.LEFT)
        self.training_status_label.pack()

        # Buttons frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame,
            text="🔄 Refresh Status",
            command=self.refresh_training_status
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="🧠 Train AI",
            command=self.train_ai
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="📂 Open Learning Folder",
            command=self.open_learning_folder
        ).pack(side=tk.LEFT, padx=5)

        # Instructions frame
        instructions_frame = ttk.LabelFrame(parent, text="Quick Guide", padding="10")
        instructions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        instructions = """Step-by-step:

1. Create video pairs:
   - Copy original video to learning/original/my_video.mp4
   - Copy your edited version to learning/edited/my_video.mp4
   - Filenames MUST match!

2. Repeat for 5-10 videos (more = better AI)

3. Click 'Train AI' button above

4. After training, change mode:
   - Go to Basic Settings tab
   - Set 'Editing Mode' to 'My Style'
   - Process videos - they'll be edited YOUR way!

Tip: You can add more videos anytime and retrain.
     The AI will only train on NEW videos you add!"""

        instructions_label = ttk.Label(instructions_frame, text=instructions, justify=tk.LEFT)
        instructions_label.pack()

        # Initial status load
        self.refresh_training_status()

    def setup_log_tab(self, parent):
        """Setup the log output tab"""
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            height=20,
            width=70,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_log
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Copy Log",
            command=self.copy_log
        ).pack(side=tk.LEFT, padx=5)

    def browse_video(self):
        """Browse for input video file"""
        filename = filedialog.askopenfilename(
            title="Select Stream Video",
            filetypes=[
                ("Video files", "*.mp4 *.mkv *.avi *.mov *.flv *.wmv"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.video_path.set(filename)
            self.log(f"Selected video: {filename}")

    def browse_output(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(
            title="Choose Output Folder"
        )
        if folder:
            self.output_path.set(folder)
            self.log(f"Output folder: {folder}")

    def browse_memes_folder(self):
        """Browse for custom memes folder"""
        folder = filedialog.askdirectory(
            title="Choose Memes Folder",
            initialdir=self.memes_folder.get()
        )
        if folder:
            self.memes_folder.set(folder)
            self.log(f"Memes folder: {folder}")

    def browse_sounds_folder(self):
        """Browse for custom sounds folder"""
        folder = filedialog.askdirectory(
            title="Choose Sounds Folder",
            initialdir=self.sounds_folder.get()
        )
        if folder:
            self.sounds_folder.set(folder)
            self.log(f"Sounds folder: {folder}")

    def browse_music_folder(self):
        """Browse for custom music folder"""
        folder = filedialog.askdirectory(
            title="Choose Music Folder",
            initialdir=self.music_folder.get()
        )
        if folder:
            self.music_folder.set(folder)
            self.log(f"Music folder: {folder}")

    def browse_images_folder(self):
        """Browse for custom images folder"""
        folder = filedialog.askdirectory(
            title="Choose Images Folder",
            initialdir=self.images_folder.get()
        )
        if folder:
            self.images_folder.set(folder)
            self.log(f"Images folder: {folder}")

    def toggle_preview_mode(self):
        """Toggle preview mode"""
        current = self.preview_mode.get()
        self.preview_mode.set(not current)
        self.update_simple_toggle_button(self.preview_btn, self.preview_mode.get())
        self.save_config()  # Auto-save on change

    def toggle_verbose_mode(self):
        """Toggle verbose mode"""
        current = self.verbose_mode.get()
        self.verbose_mode.set(not current)
        self.update_simple_toggle_button(self.verbose_btn, self.verbose_mode.get())
        self.save_config()  # Auto-save on change

    def toggle_memes(self):
        """Toggle memes feature"""
        current = self.memes_enabled.get()
        self.memes_enabled.set(not current)
        self.update_simple_toggle_button(self.memes_btn, self.memes_enabled.get())
        self.save_config()  # Auto-save on change

    def toggle_assets(self):
        """Toggle custom assets feature"""
        current = self.assets_enabled.get()
        self.assets_enabled.set(not current)
        self.update_simple_toggle_button(self.assets_btn, self.assets_enabled.get())
        self.save_config()  # Auto-save on change

    def toggle_force_sounds(self):
        """Toggle force all sounds setting"""
        try:
            current = self.force_all_sounds.get()
            self.force_all_sounds.set(not current)
            self.update_toggle_button(self.force_sounds_btn, self.force_all_sounds.get())
            self.log(f"Force ALL Sounds: {'ON' if self.force_all_sounds.get() else 'OFF'}")
            self.save_config()  # Auto-save on change
        except Exception as e:
            self.log(f"Error toggling force sounds: {e}")

    def toggle_force_music(self):
        """Toggle force all music setting"""
        try:
            current = self.force_all_music.get()
            self.force_all_music.set(not current)
            self.update_toggle_button(self.force_music_btn, self.force_all_music.get())
            self.log(f"Force ALL Music: {'ON' if self.force_all_music.get() else 'OFF'}")
            self.save_config()  # Auto-save on change
        except Exception as e:
            self.log(f"Error toggling force music: {e}")

    def toggle_force_images(self):
        """Toggle force all images setting"""
        try:
            current = self.force_all_images.get()
            self.force_all_images.set(not current)
            self.update_toggle_button(self.force_images_btn, self.force_all_images.get())
            self.log(f"Force ALL Images: {'ON' if self.force_all_images.get() else 'OFF'}")
            self.save_config()  # Auto-save on change
        except Exception as e:
            self.log(f"Error toggling force images: {e}")

    def update_simple_toggle_button(self, button, state):
        """Update simple toggle button appearance based on state"""
        try:
            if state:
                button.config(text="ON", relief=tk.SUNKEN, bg="#90EE90", activebackground="#7CCD7C")
            else:
                button.config(text="OFF", relief=tk.RAISED, bg="#f0f0f0", activebackground="#e0e0e0")
        except Exception as e:
            print(f"Error updating simple toggle button: {e}")

    def update_toggle_button(self, button, state):
        """Update toggle button appearance based on state"""
        try:
            if state:
                button.config(text="Force ALL: ON", relief=tk.SUNKEN, bg="#90EE90", activebackground="#7CCD7C")
            else:
                button.config(text="Force ALL: OFF", relief=tk.RAISED, bg="#f0f0f0", activebackground="#e0e0e0")
        except Exception as e:
            print(f"Error updating toggle button: {e}")

    def update_all_toggle_buttons(self):
        """Update all toggle buttons to match current state"""
        try:
            # Simple toggles
            self.update_simple_toggle_button(self.preview_btn, self.preview_mode.get())
            self.update_simple_toggle_button(self.verbose_btn, self.verbose_mode.get())
            self.update_simple_toggle_button(self.memes_btn, self.memes_enabled.get())
            self.update_simple_toggle_button(self.assets_btn, self.assets_enabled.get())

            # Force ALL toggles
            self.update_toggle_button(self.force_sounds_btn, self.force_all_sounds.get())
            self.update_toggle_button(self.force_music_btn, self.force_all_music.get())
            self.update_toggle_button(self.force_images_btn, self.force_all_images.get())
        except Exception as e:
            print(f"Error updating all toggle buttons: {e}")

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        output_dir = Path("output")
        if output_dir.exists():
            os.startfile(str(output_dir.absolute()))
        else:
            messagebox.showinfo("Output Folder", "Output folder doesn't exist yet. Process a video first!")

    def open_config(self):
        """Open config.yaml in default text editor"""
        if self.config_path.exists():
            os.startfile(str(self.config_path.absolute()))
        else:
            messagebox.showerror("Error", "config.yaml not found!")

    def open_readme(self):
        """Open README.md"""
        readme_path = Path("README.md")
        if readme_path.exists():
            os.startfile(str(readme_path.absolute()))
        else:
            messagebox.showinfo("Info", "README.md not found in current directory")

    def open_learning_folder(self):
        """Open the learning folder in file explorer"""
        learning_dir = Path("learning")
        learning_dir.mkdir(exist_ok=True)
        (learning_dir / "original").mkdir(exist_ok=True)
        (learning_dir / "edited").mkdir(exist_ok=True)
        os.startfile(str(learning_dir.absolute()))

    def refresh_training_status(self):
        """Refresh the training status display"""
        try:
            from auto_edit import Config
            from auto_edit.style_learner import StyleLearner

            cfg = Config('config.yaml')
            learner = StyleLearner(cfg)

            # Scan for pairs
            pairs = learner.scan_learning_folder()

            # Count trained pairs
            trained_count = 0
            untrained_count = 0
            trained_names = []
            untrained_names = []

            for orig, edit in pairs:
                if learner.is_pair_trained(orig, edit):
                    trained_count += 1
                    trained_names.append(Path(orig).name)
                else:
                    untrained_count += 1
                    untrained_names.append(Path(orig).name)

            # Check if model exists
            model_exists = learner.load_model()

            # Build status text
            status = f"Model Status: {'✅ Trained' if model_exists else '❌ Not trained'}\n"
            status += f"Total video pairs found: {len(pairs)}\n"
            status += f"Already trained: {trained_count}\n"
            status += f"Ready to train: {untrained_count}\n\n"

            if trained_names:
                status += "Trained videos:\n"
                for name in trained_names[:5]:  # Show first 5
                    status += f"  ✓ {name}\n"
                if len(trained_names) > 5:
                    status += f"  ... and {len(trained_names) - 5} more\n"
                status += "\n"

            if untrained_names:
                status += "Ready to train:\n"
                for name in untrained_names[:5]:  # Show first 5
                    status += f"  + {name}\n"
                if len(untrained_names) > 5:
                    status += f"  ... and {len(untrained_names) - 5} more\n"
            else:
                if len(pairs) > 0:
                    status += "All videos already trained!\nAdd new videos to continue learning."
                else:
                    status += "No video pairs found.\nAdd videos to learning/original/ and learning/edited/"

            self.training_status_label.config(text=status)

        except Exception as e:
            self.training_status_label.config(text=f"Error loading status:\n{str(e)}")

    def train_ai(self):
        """Train the AI model"""
        try:
            result = messagebox.askyesno(
                "Train AI",
                "Start AI training?\n\nThis will:\n"
                "- Scan learning folder for video pairs\n"
                "- Train only on NEW untrained videos\n"
                "- Save the trained model\n\n"
                "Training may take a few minutes."
            )

            if not result:
                return

            self.log("=" * 60)
            self.log("Starting AI Training...")
            self.log("=" * 60)

            # Run training in background
            cmd = [sys.executable, "auto_edit.py", "train-auto"]

            # Start processing thread
            def run_training():
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=1
                    )

                    for line in process.stdout:
                        self.log(line.rstrip())

                    process.wait()

                    if process.returncode == 0:
                        self.root.after(0, lambda: self.training_complete_success())
                    else:
                        self.root.after(0, lambda: self.training_complete_error())

                except Exception as e:
                    self.root.after(0, lambda: self.training_complete_error(str(e)))

            thread = threading.Thread(target=run_training, daemon=True)
            thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start training:\n{str(e)}")

    def training_complete_success(self):
        """Handle successful training completion"""
        self.log("\n✓ Training Complete!")
        self.refresh_training_status()
        messagebox.showinfo(
            "Training Complete",
            "AI training successful!\n\n"
            "To use your trained style:\n"
            "1. Go to Basic Settings tab\n"
            "2. Set 'Editing Mode' to 'My Style'\n"
            "3. Process your videos!"
        )

    def training_complete_error(self, error=None):
        """Handle training error"""
        self.log("\n✗ Training Failed!")
        if error:
            self.log(f"Error: {error}")
        messagebox.showerror(
            "Training Failed",
            "AI training failed!\n\n"
            "Check the Output Log tab for details.\n\n"
            "Common issues:\n"
            "- Need at least 5 video pairs\n"
            "- Filenames must match in both folders\n"
            "- Videos must be valid formats"
        )
        self.refresh_training_status()

    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)

    def copy_log(self):
        """Copy log to clipboard"""
        log_content = self.log_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        messagebox.showinfo("Copied", "Log copied to clipboard!")

    def start_processing(self):
        """Start video processing"""
        # Validation
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video file first!")
            return

        if not Path(self.video_path.get()).exists():
            messagebox.showerror("Error", f"Video file not found:\n{self.video_path.get()}")
            return

        # Save current settings
        self.save_config()

        # Build command
        cmd = [sys.executable, "auto_edit.py", "edit", self.video_path.get()]

        # Add duration
        cmd.extend(["-d", str(self.target_duration.get())])

        # Add output path if specified
        if self.output_path.get():
            output_path = self.output_path.get()
            # Check if it's a directory or a file path
            if Path(output_path).is_dir():
                # It's a folder - create filename in that folder
                video_name = Path(self.video_path.get()).stem
                output_path = str(Path(output_path) / f"{video_name}_highlights.mp4")
            cmd.extend(["-o", output_path])

        # Add flags
        if self.preview_mode.get():
            cmd.append("--preview")

        if self.verbose_mode.get():
            cmd.append("-v")

        # Update UI
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        self.status_var.set("Processing video...")

        self.log("=" * 60)
        self.log(f"Starting Auto Edit...")
        self.log(f"Command: {' '.join(cmd)}")
        self.log("=" * 60)

        # Start processing in thread
        thread = threading.Thread(target=self.run_process, args=(cmd,), daemon=True)
        thread.start()

    def run_process(self, cmd):
        """Run the auto_edit process"""
        try:
            # Create process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Read output line by line
            for line in self.process.stdout:
                if not self.processing:
                    break
                self.log(line.rstrip())

            # Wait for completion
            returncode = self.process.wait()

            # Update UI
            if returncode == 0:
                self.root.after(0, self.processing_complete_success)
            else:
                self.root.after(0, self.processing_complete_error)

        except Exception as e:
            self.root.after(0, lambda: self.processing_complete_error(str(e)))

    def processing_complete_success(self):
        """Handle successful completion"""
        self.log("=" * 60)
        self.log("✓ SUCCESS! Highlight video created!")
        self.log("=" * 60)

        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_var.set("Complete! Check the output folder.")

        # Show success message
        result = messagebox.askyesno(
            "Success!",
            "Highlight video created successfully!\n\nDo you want to open the output folder?"
        )

        if result:
            self.open_output_folder()

    def processing_complete_error(self, error=None):
        """Handle error"""
        self.log("=" * 60)
        self.log("✗ ERROR: Processing failed!")
        if error:
            self.log(f"Error: {error}")
        self.log("=" * 60)

        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_var.set("Error occurred. Check the log.")

        messagebox.showerror(
            "Error",
            "Processing failed! Check the Output Log tab for details."
        )

    def stop_processing(self):
        """Stop the processing"""
        if self.process:
            self.processing = False
            self.process.terminate()
            self.log("\nProcessing stopped by user.")

            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress.stop()
            self.status_var.set("Stopped")


def main():
    """Main entry point"""
    # Check if we're in the right directory
    if not Path("auto_edit.py").exists():
        messagebox.showerror(
            "Error",
            "auto_edit.py not found!\n\n"
            "Please run this GUI from the Audo-Edit folder."
        )
        sys.exit(1)

    # Create and run GUI
    root = tk.Tk()
    app = AutoEditGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
