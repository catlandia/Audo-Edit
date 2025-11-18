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

        self.processing = False
        self.process = None

        # Load config
        self.config_path = Path("config.yaml")
        self.load_config()

        # Setup UI
        self.setup_ui()

    def load_config(self):
        """Load configuration from config.yaml"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    self.target_duration.set(config.get('output', {}).get('target_duration_minutes', 20))
                    self.memes_enabled.set(config.get('memes', {}).get('enabled', True))
                    self.assets_enabled.set(config.get('assets', {}).get('enabled', False))
        except Exception as e:
            self.log(f"Warning: Could not load config: {e}")

    def save_config(self):
        """Save current settings to config.yaml"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)

                # Update config
                if 'output' not in config:
                    config['output'] = {}
                config['output']['target_duration_minutes'] = self.target_duration.get()

                if 'memes' not in config:
                    config['memes'] = {}
                config['memes']['enabled'] = self.memes_enabled.get()

                if 'assets' not in config:
                    config['assets'] = {}
                config['assets']['enabled'] = self.assets_enabled.get()

                # Save config
                with open(self.config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)

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

        # Tab 1: Basic Settings
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="Basic Settings")
        self.setup_basic_tab(basic_frame)

        # Tab 2: Advanced Settings
        advanced_frame = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_frame, text="Advanced Settings")
        self.setup_advanced_tab(advanced_frame)

        # Tab 3: Output Log
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

        # Output location (optional)
        output_frame = ttk.LabelFrame(parent, text="Output Location (Optional)", padding="10")
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(output_frame, textvariable=self.output_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).pack(side=tk.LEFT)

        hint_label = ttk.Label(output_frame, text="Leave empty to use default output folder", font=("Arial", 8), foreground="gray")
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

        ttk.Checkbutton(
            options_frame,
            text="Preview Mode (Top 5 clips only - fast)",
            variable=self.preview_mode
        ).pack(anchor=tk.W, pady=2)

        ttk.Checkbutton(
            options_frame,
            text="Verbose Output (Show detailed progress)",
            variable=self.verbose_mode
        ).pack(anchor=tk.W, pady=2)

        # Features
        features_frame = ttk.LabelFrame(parent, text="Features", padding="10")
        features_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(
            features_frame,
            text="🎭 Enable Memes (Automatic meme insertion at funny moments)",
            variable=self.memes_enabled
        ).pack(anchor=tk.W, pady=2)

        ttk.Checkbutton(
            features_frame,
            text="🎵 Enable Custom Assets (Music, sounds, images from folders)",
            variable=self.assets_enabled
        ).pack(anchor=tk.W, pady=2)

        ttk.Label(
            features_frame,
            text="Note: Thumbnails and sound clips are always extracted",
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
        """Browse for output location"""
        filename = filedialog.asksaveasfilename(
            title="Save Highlight Video As",
            defaultextension=".mp4",
            filetypes=[("MP4 video", "*.mp4"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            self.log(f"Output path: {filename}")

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
            cmd.extend(["-o", self.output_path.get()])

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
