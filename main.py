import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font as tkfont
from pathlib import Path
import json

import cv2
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np


class VideoProcessor:
    """Handles video processing with memory optimization"""
    
    @staticmethod
    def get_video_info(video_path):
        """Get video metadata without loading all frames"""
        cap = cv2.VideoCapture(video_path)
        info = {
            'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0
        }
        cap.release()
        return info
    
    @staticmethod
    def extract_frames(video_path, start_frame=0, end_frame=None, skip_frames=1):
        """Extract frames from video with frame skipping for memory efficiency"""
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = 0
        
        if end_frame is None:
            end_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        while frame_count < (end_frame - start_frame):
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % skip_frames == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)
            
            frame_count += 1
        
        cap.release()
        return frames
    
    @staticmethod
    def apply_filters(frame, brightness=1.0, contrast=1.0, saturation=1.0, 
                     grayscale=False, sepia=False, rotation=0, flip_h=False, flip_v=False):
        """Apply various filters to a frame"""
        img = Image.fromarray(frame)
        
        # Rotation
        if rotation != 0:
            img = img.rotate(-rotation, expand=True)
        
        # Flip
        if flip_h:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if flip_v:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
        # Brightness
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)
        
        # Contrast
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
        
        # Saturation
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(saturation)
        
        # Grayscale
        if grayscale:
            img = img.convert('L').convert('RGB')
        
        # Sepia
        if sepia:
            img = img.convert('L')
            sepia_img = Image.new('RGB', img.size)
            pixels = img.load()
            sepia_pixels = sepia_img.load()
            for y in range(img.height):
                for x in range(img.width):
                    gray = pixels[x, y]
                    sepia_pixels[x, y] = (int(gray * 0.9), int(gray * 0.7), int(gray * 0.4))
            img = sepia_img
        
        return np.array(img)


class GIFMakerV2(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.title('GIF Maker v2.0 - Professional Edition')
        self.geometry('1100x850')
        
        # Theme colors
        self.dark_mode = False
        self.colors = {
            'light': {'bg': '#f0f0f0', 'fg': '#000000', 'canvas': '#ffffff', 'button': '#e0e0e0'},
            'dark': {'bg': '#2b2b2b', 'fg': '#ffffff', 'canvas': '#1e1e1e', 'button': '#3c3c3c'}
        }
        
        # Data
        self.video_path = ''
        self.video_info = None
        self.frames = []
        self.preview_frame_index = 0
        self.preview_running = False
        
        # Settings
        self.start_frame = 0
        self.end_frame = 0
        self.crop_coords = None
        self.text_overlays = []
        self.watermark_path = ''
        
        # Presets
        self.presets = {
            'Twitter': {'fps': 15, 'scale': 0.5, 'colors': 256, 'optimize': True},
            'Instagram': {'fps': 30, 'scale': 0.7, 'colors': 256, 'optimize': True},
            'Discord': {'fps': 20, 'scale': 0.6, 'colors': 128, 'optimize': True},
            'High Quality': {'fps': 30, 'scale': 1.0, 'colors': 256, 'optimize': False},
            'Small File': {'fps': 10, 'scale': 0.3, 'colors': 64, 'optimize': True}
        }
        
        self.create_ui()
        self.apply_theme()
        self.bind_shortcuts()
    
    def create_ui(self):
        """Create the complete UI"""
        
        # Menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Video (Ctrl+O)", command=self.select_video)
        file_menu.add_command(label="Batch Process", command=self.batch_process)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme (Ctrl+T)", command=self.toggle_theme)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main container with notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Main
        self.main_tab = tk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main")
        self.create_main_tab()
        
        # Tab 2: Effects
        self.effects_tab = tk.Frame(self.notebook)
        self.notebook.add(self.effects_tab, text="Effects & Filters")
        self.create_effects_tab()
        
        # Tab 3: Text & Overlays
        self.overlay_tab = tk.Frame(self.notebook)
        self.notebook.add(self.overlay_tab, text="Text & Overlays")
        self.create_overlay_tab()
        
        # Tab 4: Advanced
        self.advanced_tab = tk.Frame(self.notebook)
        self.notebook.add(self.advanced_tab, text="Advanced")
        self.create_advanced_tab()
    
    def create_main_tab(self):
        """Create main tab with video selection and preview"""
        
        # Top section - Video selection
        top_frame = tk.Frame(self.main_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.select_video_button = tk.Button(top_frame, text='📁 Select Video (Ctrl+O)', 
                                             command=self.select_video, font=('Arial', 12, 'bold'))
        self.select_video_button.pack(side=tk.LEFT, padx=5)
        
        self.video_info_label = tk.Label(top_frame, text='No video loaded', font=('Arial', 10))
        self.video_info_label.pack(side=tk.LEFT, padx=20)
        
        # Preview section
        preview_frame = tk.LabelFrame(self.main_tab, text="Video Preview", font=('Arial', 11, 'bold'))
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(preview_frame, width=700, height=400, background='#333333')
        self.canvas.pack(pady=10)
        
        # Enable drag for crop
        self.canvas.bind('<Button-1>', self.start_crop)
        self.canvas.bind('<B1-Motion>', self.draw_crop)
        self.canvas.bind('<ButtonRelease-1>', self.end_crop)
        
        # Preview controls
        control_frame = tk.Frame(preview_frame)
        control_frame.pack(pady=10)
        
        self.play_button = tk.Button(control_frame, text='▶ Play', command=self.toggle_preview)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text='⏮ First', command=self.goto_first_frame).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text='⏭ Last', command=self.goto_last_frame).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text='🔄 Reset Crop', command=self.reset_crop).pack(side=tk.LEFT, padx=5)
        
        # Timeline slider
        timeline_frame = tk.LabelFrame(self.main_tab, text="Timeline Selection", font=('Arial', 10, 'bold'))
        timeline_frame.pack(fill=tk.X, padx=10, pady=10)
        
        slider_frame = tk.Frame(timeline_frame)
        slider_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(slider_frame, text="Start:").pack(side=tk.LEFT)
        self.start_slider = tk.Scale(slider_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     length=300, command=self.update_timeline)
        self.start_slider.pack(side=tk.LEFT, padx=10)
        
        tk.Label(slider_frame, text="End:").pack(side=tk.LEFT, padx=(20, 0))
        self.end_slider = tk.Scale(slider_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                   length=300, command=self.update_timeline)
        self.end_slider.set(100)
        self.end_slider.pack(side=tk.LEFT, padx=10)
        
        self.timeline_label = tk.Label(timeline_frame, text="Selection: 0s - 0s (0 frames)")
        self.timeline_label.pack(pady=5)
        
        # Export section
        export_frame = tk.LabelFrame(self.main_tab, text="Export Settings", font=('Arial', 11, 'bold'))
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        settings_grid = tk.Frame(export_frame)
        settings_grid.pack(padx=10, pady=10)
        
        # Preset selector
        tk.Label(settings_grid, text="Preset:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.preset_var = tk.StringVar(value='Custom')
        preset_menu = ttk.Combobox(settings_grid, textvariable=self.preset_var, 
                                   values=['Custom'] + list(self.presets.keys()), state='readonly')
        preset_menu.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        preset_menu.bind('<<ComboboxSelected>>', self.apply_preset)
        
        # FPS
        tk.Label(settings_grid, text="Speed (FPS):").grid(row=1, column=0, sticky='w', pady=5)
        self.speed_entry = tk.Entry(settings_grid, width=15)
        self.speed_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        self.speed_entry.insert(0, '15')
        
        # Scale
        tk.Label(settings_grid, text="Scale (0.1 - 2.0):").grid(row=2, column=0, sticky='w', pady=5)
        self.scale_entry = tk.Entry(settings_grid, width=15)
        self.scale_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
        self.scale_entry.insert(0, '0.5')
        
        # Output format
        tk.Label(settings_grid, text="Output Format:").grid(row=3, column=0, sticky='w', pady=5)
        self.format_var = tk.StringVar(value='GIF')
        format_menu = ttk.Combobox(settings_grid, textvariable=self.format_var, 
                                   values=['GIF', 'WebP', 'APNG'], state='readonly')
        format_menu.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        
        # Colors
        tk.Label(settings_grid, text="Colors (32-256):").grid(row=1, column=2, sticky='w', pady=5, padx=(20, 0))
        self.colors_entry = tk.Entry(settings_grid, width=15)
        self.colors_entry.grid(row=1, column=3, padx=10, pady=5, sticky='ew')
        self.colors_entry.insert(0, '256')
        
        # Optimize
        self.optimize_var = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_grid, text="Optimize File Size", variable=self.optimize_var).grid(
            row=2, column=2, columnspan=2, sticky='w', pady=5, padx=(20, 0))
        
        # Reverse
        self.reverse_var = tk.BooleanVar(value=False)
        tk.Checkbutton(settings_grid, text="Reverse Playback", variable=self.reverse_var).grid(
            row=3, column=2, columnspan=2, sticky='w', pady=5, padx=(20, 0))
        
        # Size estimation
        self.size_label = tk.Label(export_frame, text="Estimated size: ~ MB", font=('Arial', 9, 'italic'))
        self.size_label.pack(pady=5)
        
        # Export button
        button_frame = tk.Frame(export_frame)
        button_frame.pack(pady=10)
        
        self.export_button = tk.Button(button_frame, text='🎬 Export GIF', command=self.export_gif,
                                       font=('Arial', 12, 'bold'), bg='#4CAF50', fg='white', 
                                       padx=20, pady=10)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(export_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=10)
        
        self.status_label = tk.Label(export_frame, text="Ready", font=('Arial', 9))
        self.status_label.pack()
    
    def create_effects_tab(self):
        """Create effects and filters tab"""
        
        # Adjustments section
        adj_frame = tk.LabelFrame(self.effects_tab, text="Image Adjustments", font=('Arial', 11, 'bold'))
        adj_frame.pack(fill=tk.X, padx=10, pady=10)
        
        adj_grid = tk.Frame(adj_frame)
        adj_grid.pack(padx=10, pady=10)
        
        # Brightness
        tk.Label(adj_grid, text="Brightness:").grid(row=0, column=0, sticky='w', pady=5)
        self.brightness_var = tk.DoubleVar(value=1.0)
        brightness_scale = tk.Scale(adj_grid, from_=0.0, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                                    variable=self.brightness_var, length=300)
        brightness_scale.grid(row=0, column=1, padx=10, pady=5)
        
        # Contrast
        tk.Label(adj_grid, text="Contrast:").grid(row=1, column=0, sticky='w', pady=5)
        self.contrast_var = tk.DoubleVar(value=1.0)
        contrast_scale = tk.Scale(adj_grid, from_=0.0, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                                  variable=self.contrast_var, length=300)
        contrast_scale.grid(row=1, column=1, padx=10, pady=5)
        
        # Saturation
        tk.Label(adj_grid, text="Saturation:").grid(row=2, column=0, sticky='w', pady=5)
        self.saturation_var = tk.DoubleVar(value=1.0)
        saturation_scale = tk.Scale(adj_grid, from_=0.0, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                                    variable=self.saturation_var, length=300)
        saturation_scale.grid(row=2, column=1, padx=10, pady=5)
        
        # Filters section
        filter_frame = tk.LabelFrame(self.effects_tab, text="Filters", font=('Arial', 11, 'bold'))
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        filter_grid = tk.Frame(filter_frame)
        filter_grid.pack(padx=10, pady=10)
        
        self.grayscale_var = tk.BooleanVar(value=False)
        tk.Checkbutton(filter_grid, text="Grayscale", variable=self.grayscale_var).grid(
            row=0, column=0, sticky='w', pady=5, padx=10)
        
        self.sepia_var = tk.BooleanVar(value=False)
        tk.Checkbutton(filter_grid, text="Sepia", variable=self.sepia_var).grid(
            row=0, column=1, sticky='w', pady=5, padx=10)
        
        # Transform section
        transform_frame = tk.LabelFrame(self.effects_tab, text="Transform", font=('Arial', 11, 'bold'))
        transform_frame.pack(fill=tk.X, padx=10, pady=10)
        
        transform_grid = tk.Frame(transform_frame)
        transform_grid.pack(padx=10, pady=10)
        
        tk.Label(transform_grid, text="Rotation:").grid(row=0, column=0, sticky='w', pady=5)
        self.rotation_var = tk.IntVar(value=0)
        rotation_menu = ttk.Combobox(transform_grid, textvariable=self.rotation_var,
                                     values=[0, 90, 180, 270], state='readonly', width=10)
        rotation_menu.grid(row=0, column=1, padx=10, pady=5)
        rotation_menu.current(0)
        
        self.flip_h_var = tk.BooleanVar(value=False)
        tk.Checkbutton(transform_grid, text="Flip Horizontal", variable=self.flip_h_var).grid(
            row=1, column=0, columnspan=2, sticky='w', pady=5)
        
        self.flip_v_var = tk.BooleanVar(value=False)
        tk.Checkbutton(transform_grid, text="Flip Vertical", variable=self.flip_v_var).grid(
            row=2, column=0, columnspan=2, sticky='w', pady=5)
        
        # Reset button
        tk.Button(self.effects_tab, text="Reset All Effects", command=self.reset_effects,
                 font=('Arial', 10, 'bold')).pack(pady=20)
    
    def create_overlay_tab(self):
        """Create text and overlay tab"""
        
        # Text overlay section
        text_frame = tk.LabelFrame(self.overlay_tab, text="Add Text Overlay", font=('Arial', 11, 'bold'))
        text_frame.pack(fill=tk.X, padx=10, pady=10)
        
        text_grid = tk.Frame(text_frame)
        text_grid.pack(padx=10, pady=10)
        
        tk.Label(text_grid, text="Text:").grid(row=0, column=0, sticky='w', pady=5)
        self.text_entry = tk.Entry(text_grid, width=40)
        self.text_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky='ew')
        
        tk.Label(text_grid, text="Font Size:").grid(row=1, column=0, sticky='w', pady=5)
        self.font_size_var = tk.IntVar(value=30)
        font_size_spin = tk.Spinbox(text_grid, from_=10, to=200, textvariable=self.font_size_var, width=10)
        font_size_spin.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        tk.Label(text_grid, text="Position:").grid(row=2, column=0, sticky='w', pady=5)
        self.text_position_var = tk.StringVar(value='bottom')
        position_menu = ttk.Combobox(text_grid, textvariable=self.text_position_var,
                                     values=['top', 'center', 'bottom', 'top-left', 'top-right', 
                                            'bottom-left', 'bottom-right'], state='readonly')
        position_menu.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
        
        tk.Label(text_grid, text="Color:").grid(row=3, column=0, sticky='w', pady=5)
        self.text_color = '#FFFFFF'
        self.color_button = tk.Button(text_grid, text="Choose Color", command=self.choose_text_color,
                                      bg=self.text_color)
        self.color_button.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        
        tk.Button(text_grid, text="Add Text", command=self.add_text_overlay,
                 font=('Arial', 10, 'bold')).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Watermark section
        watermark_frame = tk.LabelFrame(self.overlay_tab, text="Watermark", font=('Arial', 11, 'bold'))
        watermark_frame.pack(fill=tk.X, padx=10, pady=10)
        
        watermark_grid = tk.Frame(watermark_frame)
        watermark_grid.pack(padx=10, pady=10)
        
        self.watermark_label = tk.Label(watermark_grid, text="No watermark selected")
        self.watermark_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        tk.Button(watermark_grid, text="Select Watermark Image", command=self.select_watermark).grid(
            row=1, column=0, padx=5, pady=5)
        tk.Button(watermark_grid, text="Clear Watermark", command=self.clear_watermark).grid(
            row=1, column=1, padx=5, pady=5)
        
        # Active overlays list
        list_frame = tk.LabelFrame(self.overlay_tab, text="Active Overlays", font=('Arial', 11, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.overlay_listbox = tk.Listbox(list_frame, height=6)
        self.overlay_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Button(list_frame, text="Remove Selected", command=self.remove_overlay).pack(pady=5)
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        
        # Frame skip section
        frame_skip_section = tk.LabelFrame(self.advanced_tab, text="Frame Sampling", 
                                          font=('Arial', 11, 'bold'))
        frame_skip_section.pack(fill=tk.X, padx=10, pady=10)
        
        skip_grid = tk.Frame(frame_skip_section)
        skip_grid.pack(padx=10, pady=10)
        
        tk.Label(skip_grid, text="Skip every N frames (1 = no skip):").grid(row=0, column=0, sticky='w', pady=5)
        self.skip_frames_var = tk.IntVar(value=1)
        skip_spin = tk.Spinbox(skip_grid, from_=1, to=10, textvariable=self.skip_frames_var, width=10)
        skip_spin.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(skip_grid, text="Use this to reduce file size for long videos", 
                font=('Arial', 9, 'italic')).grid(row=1, column=0, columnspan=2, pady=5)
        
        # Quality section
        quality_section = tk.LabelFrame(self.advanced_tab, text="Quality Settings", 
                                       font=('Arial', 11, 'bold'))
        quality_section.pack(fill=tk.X, padx=10, pady=10)
        
        quality_grid = tk.Frame(quality_section)
        quality_grid.pack(padx=10, pady=10)
        
        tk.Label(quality_grid, text="Dithering Method:").grid(row=0, column=0, sticky='w', pady=5)
        self.dither_var = tk.StringVar(value='FLOYDSTEINBERG')
        dither_menu = ttk.Combobox(quality_grid, textvariable=self.dither_var,
                                   values=['NONE', 'FLOYDSTEINBERG'], state='readonly')
        dither_menu.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        # Info section
        info_section = tk.LabelFrame(self.advanced_tab, text="Processing Info", 
                                     font=('Arial', 11, 'bold'))
        info_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.info_text = tk.Text(info_section, height=15, width=70, state='disabled', wrap=tk.WORD)
        self.info_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(info_section, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind('<Control-o>', lambda e: self.select_video())
        self.bind('<Control-t>', lambda e: self.toggle_theme())
        self.bind('<Control-e>', lambda e: self.export_gif())
        self.bind('<space>', lambda e: self.toggle_preview())
    
    def select_video(self):
        """Select video file with support for multiple formats"""
        filetypes = (
            ("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm *.flv *.wmv"),
            ("MP4 Files", "*.mp4"),
            ("All Files", "*.*")
        )
        self.video_path = filedialog.askopenfilename(title='Select Video', filetypes=filetypes)
        
        if self.video_path:
            self.process_video()
    
    def process_video(self):
        """Process video and extract information"""
        if not self.video_path:
            return
        
        try:
            # Get video info
            self.video_info = VideoProcessor.get_video_info(self.video_path)
            
            # Update UI
            info_text = f"📹 {Path(self.video_path).name} | " \
                       f"⏱ {self.video_info['duration']}s | " \
                       f"📐 {self.video_info['width']}x{self.video_info['height']} | " \
                       f"🎞 {self.video_info['total_frames']} frames @ {self.video_info['fps']:.1f} fps"
            self.video_info_label.config(text=info_text)
            
            # Update sliders
            self.start_slider.config(to=self.video_info['total_frames'])
            self.end_slider.config(to=self.video_info['total_frames'])
            self.end_slider.set(self.video_info['total_frames'])
            
            self.start_frame = 0
            self.end_frame = self.video_info['total_frames']
            
            # Load preview frames (sample every Nth frame for efficiency)
            skip = max(1, self.video_info['total_frames'] // 100)
            self.frames = VideoProcessor.extract_frames(self.video_path, skip_frames=skip)
            
            self.log_info(f"Loaded video: {Path(self.video_path).name}")
            self.log_info(f"Total frames: {self.video_info['total_frames']}, Preview frames: {len(self.frames)}")
            
            self.preview_frame_index = 0
            self.update_preview_frame()
            
            messagebox.showinfo("Success", f"Video loaded successfully!\n{len(self.frames)} preview frames loaded.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video:\n{str(e)}")
            self.log_info(f"ERROR: {str(e)}")
    
    def update_timeline(self, value=None):
        """Update timeline selection"""
        if not self.video_info:
            return
        
        self.start_frame = int(self.start_slider.get())
        self.end_frame = int(self.end_slider.get())
        
        if self.start_frame >= self.end_frame:
            self.end_frame = self.start_frame + 1
            self.end_slider.set(self.end_frame)
        
        duration = (self.end_frame - self.start_frame) / self.video_info['fps']
        frame_count = self.end_frame - self.start_frame
        
        self.timeline_label.config(
            text=f"Selection: {self.start_frame/self.video_info['fps']:.2f}s - "
                 f"{self.end_frame/self.video_info['fps']:.2f}s ({frame_count} frames, {duration:.2f}s)"
        )
        
        self.estimate_file_size()
    
    def toggle_preview(self):
        """Toggle preview playback"""
        if not self.frames:
            return
        
        self.preview_running = not self.preview_running
        
        if self.preview_running:
            self.play_button.config(text='⏸ Pause')
            self.animate_preview()
        else:
            self.play_button.config(text='▶ Play')
    
    def animate_preview(self):
        """Animate preview with effects applied"""
        if not self.preview_running or not self.frames:
            return
        
        frame = self.frames[self.preview_frame_index].copy()
        
        # Apply effects
        frame = VideoProcessor.apply_filters(
            frame,
            brightness=self.brightness_var.get(),
            contrast=self.contrast_var.get(),
            saturation=self.saturation_var.get(),
            grayscale=self.grayscale_var.get(),
            sepia=self.sepia_var.get(),
            rotation=self.rotation_var.get(),
            flip_h=self.flip_h_var.get(),
            flip_v=self.flip_v_var.get()
        )
        
        self.display_frame(frame)
        
        self.preview_frame_index = (self.preview_frame_index + 1) % len(self.frames)
        self.after(50, self.animate_preview)
    
    def update_preview_frame(self):
        """Update single preview frame"""
        if not self.frames:
            return
        
        frame = self.frames[self.preview_frame_index].copy()
        
        # Apply effects
        frame = VideoProcessor.apply_filters(
            frame,
            brightness=self.brightness_var.get(),
            contrast=self.contrast_var.get(),
            saturation=self.saturation_var.get(),
            grayscale=self.grayscale_var.get(),
            sepia=self.sepia_var.get(),
            rotation=self.rotation_var.get(),
            flip_h=self.flip_h_var.get(),
            flip_v=self.flip_v_var.get()
        )
        
        self.display_frame(frame)
    
    def display_frame(self, frame):
        """Display frame on canvas"""
        img = Image.fromarray(frame)
        
        # Apply crop if set
        if self.crop_coords:
            x1, y1, x2, y2 = self.crop_coords
            # Scale crop coords to actual frame size
            h, w = frame.shape[:2]
            canvas_w, canvas_h = 700, 400
            scale_x = w / canvas_w
            scale_y = h / canvas_h
            
            crop_box = (int(x1 * scale_x), int(y1 * scale_y), 
                       int(x2 * scale_x), int(y2 * scale_y))
            img = img.crop(crop_box)
        
        # Resize for canvas
        img.thumbnail((700, 400), Image.LANCZOS)
        
        # Apply text overlays for preview
        if self.text_overlays:
            draw = ImageDraw.Draw(img)
            for overlay in self.text_overlays:
                try:
                    font = ImageFont.truetype("arial.ttf", int(overlay['size'] * 0.5))
                except:
                    font = ImageFont.load_default()
                
                text = overlay['text']
                position = self.calculate_text_position(img.size, text, font, overlay['position'])
                
                # Draw text with outline
                x, y = position
                for adj in [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]:
                    draw.text(adj, text, font=font, fill='black')
                draw.text(position, text, font=font, fill=overlay['color'])
        
        photo = ImageTk.PhotoImage(img)
        self.canvas.delete('all')
        self.canvas.create_image(350, 200, image=photo)
        self.canvas.image = photo
        
        # Redraw crop rectangle if exists
        if self.crop_coords:
            x1, y1, x2, y2 = self.crop_coords
            self.canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=2, dash=(5, 5))
    
    def goto_first_frame(self):
        """Go to first frame"""
        if self.frames:
            self.preview_frame_index = 0
            self.update_preview_frame()
    
    def goto_last_frame(self):
        """Go to last frame"""
        if self.frames:
            self.preview_frame_index = len(self.frames) - 1
            self.update_preview_frame()
    
    def start_crop(self, event):
        """Start crop selection"""
        self.crop_start = (event.x, event.y)
    
    def draw_crop(self, event):
        """Draw crop rectangle"""
        if hasattr(self, 'crop_start'):
            self.canvas.delete('crop_rect')
            x1, y1 = self.crop_start
            self.canvas.create_rectangle(x1, y1, event.x, event.y, 
                                        outline='red', width=2, dash=(5, 5), 
                                        tags='crop_rect')
    
    def end_crop(self, event):
        """End crop selection"""
        if hasattr(self, 'crop_start'):
            x1, y1 = self.crop_start
            x2, y2 = event.x, event.y
            
            # Ensure x1 < x2 and y1 < y2
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            
            # Minimum crop size
            if abs(x2 - x1) > 20 and abs(y2 - y1) > 20:
                self.crop_coords = (x1, y1, x2, y2)
                self.log_info(f"Crop area set: {x1},{y1} to {x2},{y2}")
            
            delattr(self, 'crop_start')
    
    def reset_crop(self):
        """Reset crop selection"""
        self.crop_coords = None
        self.canvas.delete('crop_rect')
        self.update_preview_frame()
        self.log_info("Crop reset")
    
    def apply_preset(self, event=None):
        """Apply preset settings"""
        preset_name = self.preset_var.get()
        
        if preset_name in self.presets:
            preset = self.presets[preset_name]
            self.speed_entry.delete(0, tk.END)
            self.speed_entry.insert(0, str(preset['fps']))
            self.scale_entry.delete(0, tk.END)
            self.scale_entry.insert(0, str(preset['scale']))
            self.colors_entry.delete(0, tk.END)
            self.colors_entry.insert(0, str(preset['colors']))
            self.optimize_var.set(preset['optimize'])
            
            self.log_info(f"Applied preset: {preset_name}")
            self.estimate_file_size()
    
    def reset_effects(self):
        """Reset all effects to default"""
        self.brightness_var.set(1.0)
        self.contrast_var.set(1.0)
        self.saturation_var.set(1.0)
        self.grayscale_var.set(False)
        self.sepia_var.set(False)
        self.rotation_var.set(0)
        self.flip_h_var.set(False)
        self.flip_v_var.set(False)
        
        self.update_preview_frame()
        self.log_info("All effects reset")
    
    def choose_text_color(self):
        """Choose text color"""
        color = colorchooser.askcolor(initialcolor=self.text_color)
        if color[1]:
            self.text_color = color[1]
            self.color_button.config(bg=self.text_color)
    
    def add_text_overlay(self):
        """Add text overlay"""
        text = self.text_entry.get().strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text")
            return
        
        overlay = {
            'text': text,
            'size': self.font_size_var.get(),
            'position': self.text_position_var.get(),
            'color': self.text_color
        }
        
        self.text_overlays.append(overlay)
        self.overlay_listbox.insert(tk.END, f"Text: '{text}' at {overlay['position']}")
        self.update_preview_frame()
        self.log_info(f"Added text overlay: '{text}'")
    
    def select_watermark(self):
        """Select watermark image"""
        filetypes = (
            ("Image Files", "*.png *.jpg *.jpeg *.gif"),
            ("All Files", "*.*")
        )
        path = filedialog.askopenfilename(title='Select Watermark', filetypes=filetypes)
        
        if path:
            self.watermark_path = path
            self.watermark_label.config(text=f"✓ {Path(path).name}")
            self.log_info(f"Watermark selected: {Path(path).name}")
    
    def clear_watermark(self):
        """Clear watermark"""
        self.watermark_path = ''
        self.watermark_label.config(text="No watermark selected")
        self.log_info("Watermark cleared")
    
    def remove_overlay(self):
        """Remove selected overlay"""
        selection = self.overlay_listbox.curselection()
        if selection:
            index = selection[0]
            self.overlay_listbox.delete(index)
            del self.text_overlays[index]
            self.update_preview_frame()
            self.log_info("Removed overlay")
    
    def calculate_text_position(self, img_size, text, font, position):
        """Calculate text position on image"""
        try:
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            text_width, text_height = 100, 30
        
        w, h = img_size
        margin = 10
        
        positions = {
            'top': (w//2 - text_width//2, margin),
            'center': (w//2 - text_width//2, h//2 - text_height//2),
            'bottom': (w//2 - text_width//2, h - text_height - margin),
            'top-left': (margin, margin),
            'top-right': (w - text_width - margin, margin),
            'bottom-left': (margin, h - text_height - margin),
            'bottom-right': (w - text_width - margin, h - text_height - margin)
        }
        
        return positions.get(position, positions['bottom'])
    
    def estimate_file_size(self):
        """Estimate output file size"""
        if not self.video_info:
            return
        
        try:
            fps = int(self.speed_entry.get())
            scale = float(self.scale_entry.get())
            colors = int(self.colors_entry.get())
            
            frame_count = self.end_frame - self.start_frame
            frame_count = frame_count // self.skip_frames_var.get()
            
            width = int(self.video_info['width'] * scale)
            height = int(self.video_info['height'] * scale)
            
            # Rough estimation: bytes per frame = width * height * color_depth
            bytes_per_frame = width * height * (colors / 256)
            total_bytes = bytes_per_frame * frame_count
            
            if self.optimize_var.get():
                total_bytes *= 0.7  # Optimization reduces size
            
            size_mb = total_bytes / (1024 * 1024)
            self.size_label.config(text=f"Estimated size: ~{size_mb:.2f} MB")
            
        except:
            self.size_label.config(text="Estimated size: ~ MB")
    
    def export_gif(self):
        """Export GIF with all settings"""
        if not self.frames:
            messagebox.showerror("Error", "Please load a video first")
            return
        
        try:
            fps = int(self.speed_entry.get())
            scale = float(self.scale_entry.get())
            colors = int(self.colors_entry.get())
            
            if fps <= 0 or scale <= 0 or colors < 32 or colors > 256:
                messagebox.showerror("Error", "Invalid export settings")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values")
            return
        
        # Get output path
        format_ext = self.format_var.get().lower()
        if format_ext == 'apng':
            format_ext = 'png'
        
        default_ext = f'.{format_ext}'
        filetypes = [
            (f"{self.format_var.get()} Files", f"*{default_ext}"),
            ("All Files", "*.*")
        ]
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes,
            initialfile=f"{Path(self.video_path).stem}_output{default_ext}"
        )
        
        if not output_path:
            return
        
        self.progress['mode'] = 'determinate'
        self.progress['value'] = 0
        self.export_button.config(state='disabled')
        self.status_label.config(text="Exporting...")
        
        # Start export in thread
        threading.Thread(target=self._export_worker, 
                        args=(output_path, fps, scale, colors), 
                        daemon=True).start()
    
    def _export_worker(self, output_path, fps, scale, colors):
        """Worker thread for export"""
        try:
            self.log_info(f"Starting export to {Path(output_path).name}")
            self.log_info(f"Settings: {fps} fps, {scale}x scale, {colors} colors")
            
            # Extract frames from selection
            skip = self.skip_frames_var.get()
            frames = VideoProcessor.extract_frames(
                self.video_path, 
                self.start_frame, 
                self.end_frame,
                skip
            )
            
            if self.reverse_var.get():
                frames = frames[::-1]
            
            self.log_info(f"Processing {len(frames)} frames...")
            
            output_frames = []
            total = len(frames)
            
            for i, frame in enumerate(frames):
                # Apply all effects
                processed = VideoProcessor.apply_filters(
                    frame,
                    brightness=self.brightness_var.get(),
                    contrast=self.contrast_var.get(),
                    saturation=self.saturation_var.get(),
                    grayscale=self.grayscale_var.get(),
                    sepia=self.sepia_var.get(),
                    rotation=self.rotation_var.get(),
                    flip_h=self.flip_h_var.get(),
                    flip_v=self.flip_v_var.get()
                )
                
                img = Image.fromarray(processed)
                
                # Apply crop
                if self.crop_coords:
                    x1, y1, x2, y2 = self.crop_coords
                    h, w = frame.shape[:2]
                    canvas_w, canvas_h = 700, 400
                    scale_x = w / canvas_w
                    scale_y = h / canvas_h
                    crop_box = (int(x1 * scale_x), int(y1 * scale_y), 
                               int(x2 * scale_x), int(y2 * scale_y))
                    img = img.crop(crop_box)
                
                # Scale
                new_size = (int(img.width * scale), int(img.height * scale))
                img = img.resize(new_size, Image.LANCZOS)
                
                # Add text overlays
                if self.text_overlays:
                    draw = ImageDraw.Draw(img)
                    for overlay in self.text_overlays:
                        try:
                            font = ImageFont.truetype("arial.ttf", overlay['size'])
                        except:
                            font = ImageFont.load_default()
                        
                        text = overlay['text']
                        position = self.calculate_text_position(img.size, text, font, overlay['position'])
                        
                        # Text with outline
                        x, y = position
                        for adj in [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]:
                            draw.text(adj, text, font=font, fill='black')
                        draw.text(position, text, font=font, fill=overlay['color'])
                
                # Add watermark
                if self.watermark_path:
                    try:
                        watermark = Image.open(self.watermark_path).convert('RGBA')
                        wm_size = (img.width // 4, img.height // 4)
                        watermark.thumbnail(wm_size, Image.LANCZOS)
                        
                        position = (img.width - watermark.width - 10, 
                                  img.height - watermark.height - 10)
                        
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        img.paste(watermark, position, watermark)
                        img = img.convert('RGB')
                    except:
                        pass
                
                # Reduce colors
                if colors < 256:
                    img = img.convert('P', palette=Image.ADAPTIVE, colors=colors)
                    img = img.convert('RGB')
                
                output_frames.append(img)
                
                # Update progress
                progress = int((i + 1) / total * 100)
                self.after(0, lambda p=progress: self.progress.config(value=p))
                self.after(0, lambda i=i: self.status_label.config(
                    text=f"Processing frame {i+1}/{total}"))
            
            # Save
            self.log_info(f"Saving {len(output_frames)} frames...")
            self.after(0, lambda: self.status_label.config(text="Saving file..."))
            
            duration = 1000 // fps
            
            if self.format_var.get() == 'WebP':
                output_frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=output_frames[1:],
                    duration=duration,
                    loop=0,
                    lossless=False,
                    quality=85
                )
            elif self.format_var.get() == 'APNG':
                output_frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=output_frames[1:],
                    duration=duration,
                    loop=0
                )
            else:  # GIF
                dither = Image.FLOYDSTEINBERG if self.dither_var.get() == 'FLOYDSTEINBERG' else Image.NONE
                output_frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=output_frames[1:],
                    optimize=self.optimize_var.get(),
                    duration=duration,
                    loop=0,
                    dither=dither
                )
            
            file_size = Path(output_path).stat().st_size / (1024 * 1024)
            self.log_info(f"Export complete! File size: {file_size:.2f} MB")
            
            self.after(0, lambda: self.progress.config(value=100))
            self.after(0, lambda: self.status_label.config(text="Export complete!"))
            self.after(0, lambda: messagebox.showinfo(
                "Success", 
                f"GIF exported successfully!\n\nFile: {Path(output_path).name}\nSize: {file_size:.2f} MB"
            ))
            
        except Exception as e:
            self.log_info(f"ERROR during export: {str(e)}")
            self.after(0, lambda: messagebox.showerror("Error", f"Export failed:\n{str(e)}"))
        
        finally:
            self.after(0, lambda: self.export_button.config(state='normal'))
            self.after(0, lambda: self.progress.config(value=0))
    
    def batch_process(self):
        """Batch process multiple videos"""
        filetypes = (
            ("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm"),
            ("All Files", "*.*")
        )
        file_paths = filedialog.askopenfilenames(title='Select Videos', filetypes=filetypes)
        
        if not file_paths:
            return
        
        output_dir = filedialog.askdirectory(title='Select Output Directory')
        if not output_dir:
            return
        
        self.log_info(f"Batch processing {len(file_paths)} files...")
        
        messagebox.showinfo("Batch Process", 
                           f"Processing {len(file_paths)} videos.\nThis may take a while...")
        
        threading.Thread(target=self._batch_worker, 
                        args=(file_paths, output_dir), 
                        daemon=True).start()
    
    def _batch_worker(self, file_paths, output_dir):
        """Worker for batch processing"""
        successful = 0
        failed = 0
        
        for i, video_path in enumerate(file_paths):
            try:
                self.log_info(f"Processing {i+1}/{len(file_paths)}: {Path(video_path).name}")
                self.after(0, lambda i=i: self.status_label.config(
                    text=f"Batch: Processing {i+1}/{len(file_paths)}"))
                
                # Load video
                info = VideoProcessor.get_video_info(video_path)
                frames = VideoProcessor.extract_frames(video_path, skip_frames=2)
                
                # Process frames
                output_frames = []
                for frame in frames:
                    img = Image.fromarray(frame)
                    img = img.resize((int(img.width * 0.5), int(img.height * 0.5)), Image.LANCZOS)
                    output_frames.append(img)
                
                # Save
                output_name = Path(video_path).stem + '_batch.gif'
                output_path = Path(output_dir) / output_name
                
                output_frames[0].save(
                    str(output_path),
                    save_all=True,
                    append_images=output_frames[1:],
                    optimize=True,
                    duration=100,
                    loop=0
                )
                
                successful += 1
                self.log_info(f"✓ Saved: {output_name}")
                
            except Exception as e:
                failed += 1
                self.log_info(f"✗ Failed: {Path(video_path).name} - {str(e)}")
        
        self.after(0, lambda: self.status_label.config(text="Batch complete!"))
        self.after(0, lambda: messagebox.showinfo(
            "Batch Complete", 
            f"Batch processing complete!\n\nSuccessful: {successful}\nFailed: {failed}"
        ))
    
    def log_info(self, message):
        """Log information to the info text widget"""
        self.info_text.config(state='normal')
        self.info_text.insert(tk.END, f"[{self.get_timestamp()}] {message}\n")
        self.info_text.see(tk.END)
        self.info_text.config(state='disabled')
    
    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.log_info(f"Theme: {'Dark' if self.dark_mode else 'Light'}")
    
    def apply_theme(self):
        """Apply current theme"""
        theme = self.colors['dark' if self.dark_mode else 'light']
        
        self.config(bg=theme['bg'])
        
        # Update all frames and widgets
        for widget in self.winfo_children():
            self.update_widget_theme(widget, theme)
    
    def update_widget_theme(self, widget, theme):
        """Recursively update widget theme"""
        try:
            if isinstance(widget, (tk.Frame, tk.LabelFrame, tk.Label)):
                widget.config(bg=theme['bg'], fg=theme['fg'])
            elif isinstance(widget, tk.Button):
                if widget != self.export_button:  # Keep export button green
                    widget.config(bg=theme['button'], fg=theme['fg'])
            elif isinstance(widget, tk.Canvas):
                widget.config(bg=theme['canvas'])
        except:
            pass
        
        # Recurse for children
        for child in widget.winfo_children():
            self.update_widget_theme(child, theme)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """GIF Maker v2.0 - Professional Edition

A powerful video to GIF converter with advanced features:

• Multiple video format support (MP4, AVI, MOV, MKV, WebM)
• Frame selection with timeline slider
• Effects & filters (brightness, contrast, saturation, etc.)
• Text overlays and watermarks
• Batch processing
• Multiple output formats (GIF, WebP, APNG)
• Quality control and optimization
• Dark/light theme

Created with Python, OpenCV, and Pillow

Keyboard Shortcuts:
Ctrl+O - Open Video
Ctrl+E - Export
Ctrl+T - Toggle Theme
Space - Play/Pause Preview

© 2024"""
        
        messagebox.showinfo("About GIF Maker v2.0", about_text)


if __name__ == '__main__':
    app = GIFMakerV2()
    app.mainloop()