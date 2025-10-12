import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import threading
import time
import json
from functions import VideoRecorder, AudioRecorder, PreviewUpdater
import subprocess  # For merging in save_video

class TarantinoCatch:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarantino Catch")

        # Color scheme
        self.bg_color = "#0a0a1a"
        self.sidebar_color = "#141429"
        self.card_color = "#141429"
        self.accent_color = "#7c3aed"
        self.text_color = "#f1f5f9"
        self.secondary_text = "#a1a1aa"
        self.border_color = "#27272a"
        self.success_color = "#22c55e"
        self.warning_color = "#f97316"
        self.entry_text_color = "#000000"

        # Fonts
        self.title_font = ('Inter', 22, 'bold')
        self.app_font = ('Inter', 13)
        self.button_font = ('Inter', 12)
        self.small_font = ('Inter', 11)

        # Window configuration
        self.root.attributes('-fullscreen', True)
        self.hotkeys = {
            'start_recording': '<Control-r>',
            'pause_recording': '<Control-p>',
            'stop_recording': '<Control-s>'
        }
        self.bind_hotkeys()
        self.root.configure(bg=self.bg_color)

        # Recording variables
        self.recording = False
        self.paused = False
        self.camera_enabled = True
        self.screen_capture_enabled = True
        self.audio_enabled = True
        self.camera_position = [20, 20]
        self.camera_scale = 1.0
        self.dragging_camera = False
        self.custom_resolution_enabled = False
        self.preview_update_active = True
        self.last_screenshot = None
        self.last_screenshot_time = 0
        self.screenshot_cache_duration = 0.5
        self.transition_type = 'cut'
        self.transition_duration = 1.0
        self.audio_filters = {'noise_suppression': False}
        self.output_profile = {'resolution': '1920x1080', 'fps': 30, 'bitrate': 15}
        self.save_dir_var = tk.StringVar(value=os.path.expanduser("~"))
        self.file_format_var = tk.StringVar(value="mp4")
        self.camera_index_var = tk.StringVar(value="0")
        self.preview_fps_var = tk.StringVar(value="30")
        self.mic_volume_var = tk.DoubleVar(value=1.0)
        self.system_volume_var = tk.DoubleVar(value=1.0)
        self.noise_suppression_var = tk.BooleanVar(value=False)
        self.audio_gain_var = tk.DoubleVar(value=0.0)  # New: Audio gain (dB)
        self.audio_compression_var = tk.DoubleVar(value=1.0)  # New: Compression ratio
        self.brightness_var = tk.DoubleVar(value=0)
        self.contrast_var = tk.DoubleVar(value=1.0)
        self.blur_var = tk.DoubleVar(value=0)
        self.hue_var = tk.DoubleVar(value=0)
        self.saturation_var = tk.DoubleVar(value=1.0)
        self.sharpness_var = tk.DoubleVar(value=0)
        self.gamma_var = tk.DoubleVar(value=1.0)
        self.temperature_var = tk.DoubleVar(value=0)
        self.tint_var = tk.DoubleVar(value=0)
        self.vignette_var = tk.DoubleVar(value=0)
        self.noise_var = tk.DoubleVar(value=0)
        self.sepia_var = tk.DoubleVar(value=0)
        self.grayscale_var = tk.DoubleVar(value=0)
        self.invert_var = tk.DoubleVar(value=0)
        self.edge_var = tk.DoubleVar(value=0)
        self.emboss_var = tk.DoubleVar(value=0)
        self.posterize_var = tk.DoubleVar(value=0)
        self.solarize_var = tk.DoubleVar(value=0)
        self.transition_duration_var = tk.DoubleVar(value=1.0)
        self.only_camera_var = tk.BooleanVar(value=False)

        # Recorder objects
        self.video_recorder = None
        self.audio_recorder = None
        self.preview_updater = None

        self.setup_styles()
        self.setup_ui()
        self.start_preview()
        self.load_settings()

    def bind_hotkeys(self):
        self.root.bind(self.hotkeys['start_recording'], lambda e: self.toggle_recording())
        self.root.bind(self.hotkeys['pause_recording'], lambda e: self.toggle_pause())
        self.root.bind(self.hotkeys['stop_recording'], lambda e: self.stop_recording())

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background=self.bg_color, foreground=self.text_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("Sidebar.TFrame", background=self.sidebar_color)
        style.configure("Card.TFrame", background=self.card_color, relief="flat", borderwidth=0)
        style.configure("TLabel", background=self.card_color, foreground=self.text_color, font=self.small_font)
        style.configure("Title.TLabel", font=self.title_font, foreground=self.accent_color)
        style.configure("Subtitle.TLabel", font=self.small_font, foreground=self.secondary_text)

        style.configure('Accent.TButton',
                        background=self.accent_color,
                        foreground='white',
                        borderwidth=0,
                        font=self.button_font,
                        padding=10)
        style.map('Accent.TButton',
                  background=[('active', '#6d28d9')],
                  foreground=[('active', 'white')])

        style.configure('Secondary.TButton',
                        background=self.border_color,
                        foreground=self.text_color,
                        borderwidth=0,
                        font=self.button_font,
                        padding=10)
        style.map('Secondary.TButton',
                  background=[('active', '#3f3f46')],
                  foreground=[('active', 'white')])

        style.configure("TCombobox",
                        fieldbackground=self.card_color,
                        background=self.card_color,
                        foreground=self.text_color,
                        borderwidth=0,
                        arrowsize=14)
        style.map("TCombobox",
                  fieldbackground=[('readonly', self.card_color)],
                  selectbackground=[('readonly', self.card_color)])

        style.configure("TEntry", fieldbackground=self.card_color, foreground=self.entry_text_color, borderwidth=1, padding=5)
        style.map("TEntry", fieldbackground=[('focus', '#ffffff')], foreground=[('focus', self.entry_text_color)])

        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.card_color, foreground=self.secondary_text, padding=[20, 10], font=self.button_font)
        style.map("TNotebook.Tab", background=[("selected", self.sidebar_color)], foreground=[("selected", self.accent_color)])

    def setup_ui(self):
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill='both', expand=True, padx=40, pady=40)

        # Sidebar
        sidebar = ttk.Frame(main_container, width=360, style="Sidebar.TFrame")
        sidebar.pack(side="left", fill="y", padx=(0, 30))
        sidebar.pack_propagate(False)

        # Sidebar header
        header_frame = tk.Frame(sidebar, bg=self.sidebar_color)
        header_frame.pack(fill="x", pady=(40, 50), padx=30)
        logo_frame = tk.Frame(header_frame, bg=self.sidebar_color)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="TARANTINO CATCH", bg=self.sidebar_color,
                 fg=self.accent_color, font=('Inter', 24, 'bold')).pack(side="left")

        # Sidebar controls
        controls_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        controls_frame.pack(fill="x", padx=30, pady=20)
        ttk.Button(controls_frame, text="Начать запись (Ctrl+R)",
                   command=self.toggle_recording, style="Accent.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(controls_frame, text="Пауза (Ctrl+P)",
                   command=self.toggle_pause, style="Secondary.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(controls_frame, text="Остановить (Ctrl+S)",
                   command=self.stop_recording, style="Secondary.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(controls_frame, text="Сохранить видео",
                   command=self.save_video, style="Secondary.TButton").pack(fill=tk.X, pady=5)

        # Status and timer
        status_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        status_frame.pack(fill="x", padx=30, pady=20)
        self.status_var = tk.StringVar(value="Готово")
        ttk.Label(status_frame, textvariable=self.status_var, style="TLabel").pack()
        self.time_var = tk.StringVar(value="00:00:00")
        ttk.Label(status_frame, textvariable=self.time_var, font=('Inter', 16, 'bold'), foreground=self.text_color).pack(pady=5)
        self.recording_indicator = tk.Canvas(status_frame, width=20, height=20, bg=self.sidebar_color, highlightthickness=0)
        self.recording_circle = self.recording_indicator.create_oval(5, 5, 15, 15, fill="#4b5563")
        self.recording_indicator.pack()

        # Main content area
        self.main_area = ttk.Frame(main_container, style="TFrame")
        self.main_area.pack(side="right", fill="both", expand=True)

        # Tabs
        self.notebook = ttk.Notebook(self.main_area, style="TNotebook")
        self.notebook.pack(fill='both', expand=True)

        # Recording tab
        main_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=25)
        self.notebook.add(main_frame, text="Запись")

        # Preview canvas for recording tab
        preview_frame_rec = ttk.Frame(main_frame, style="Card.TFrame")
        preview_frame_rec.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        self.preview_canvas_rec = tk.Canvas(preview_frame_rec, bg="black", highlightthickness=0, width=960, height=540)
        self.preview_canvas_rec.pack(fill="both", expand=True)
        self.preview_canvas_rec.bind("<Button-1>", self.start_drag_rec)
        self.preview_canvas_rec.bind("<B1-Motion>", self.drag_camera_rec)
        self.preview_canvas_rec.bind("<ButtonRelease-1>", self.stop_drag_rec)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Settings panel
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки записи", padding=20, style="Card.TFrame")
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Toggles for sources
        self.screen_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Захват экрана", variable=self.screen_var, command=self.toggle_screen).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.camera_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Камера", variable=self.camera_var, command=self.toggle_camera).grid(row=1, column=0, sticky="w", pady=(0, 10))
        self.audio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Аудио", variable=self.audio_var, command=self.toggle_audio).grid(row=2, column=0, sticky="w", pady=(0, 10))
        ttk.Checkbutton(settings_frame, text="Только веб-камера", variable=self.only_camera_var, command=self.toggle_only_camera).grid(row=3, column=0, sticky="w", pady=(0, 15))

        # Camera settings
        ttk.Label(settings_frame, text="Индекс камеры:", style="TLabel").grid(row=4, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(settings_frame, textvariable=self.camera_index_var, width=10).grid(row=5, column=0, sticky="we", pady=(0, 15))

        # Resolution settings
        ttk.Label(settings_frame, text="Профиль вывода:", style="TLabel").grid(row=6, column=0, sticky="w", pady=(0, 8))
        self.profile_var = tk.StringVar(value="По умолчанию")
        ttk.Combobox(settings_frame, textvariable=self.profile_var, values=["По умолчанию", "Высокое качество"],
                     width=20, state="readonly").grid(row=7, column=0, sticky="we", pady=(0, 15))
        self.profile_var.trace('w', self.load_profile)

        ttk.Label(settings_frame, text="Разрешение:", style="TLabel").grid(row=8, column=0, sticky="w", pady=(0, 8))
        self.resolution_var = tk.StringVar(value="1920x1080")
        resolutions = ["3840x2160", "2560x1440", "1920x1080", "1280x720", "1024x576"]
        ttk.Combobox(settings_frame, textvariable=self.resolution_var, values=resolutions,
                     width=20, state="readonly").grid(row=9, column=0, sticky="we", pady=(0, 15))
        self.resolution_var.trace('w', self.on_resolution_change)

        # FPS and Bitrate
        ttk.Label(settings_frame, text="FPS:", style="TLabel").grid(row=10, column=0, sticky="w", pady=(0, 8))
        self.fps_var = tk.StringVar(value="30")
        ttk.Entry(settings_frame, textvariable=self.fps_var, width=10).grid(row=11, column=0, sticky="we", pady=(0, 15))
        self.fps_var.trace('w', self.on_fps_change)

        ttk.Label(settings_frame, text="Битрейт (Mbps):", style="TLabel").grid(row=12, column=0, sticky="w", pady=(0, 8))
        self.bitrate_var = tk.StringVar(value="15")
        ttk.Entry(settings_frame, textvariable=self.bitrate_var, width=10).grid(row=13, column=0, sticky="we", pady=(0, 15))

        # Audio settings
        ttk.Label(settings_frame, text="Настройки аудио:", style="TLabel").grid(row=14, column=0, sticky="w", pady=(15, 8))
        ttk.Label(settings_frame, text="Громкость микрофона:", style="TLabel").grid(row=15, column=0, sticky="w", pady=(0, 5))
        ttk.Scale(settings_frame, from_=0.0, to=2.0, variable=self.mic_volume_var, orient=tk.HORIZONTAL, length=150).grid(row=16, column=0, sticky="we", pady=(0, 10))
        ttk.Label(settings_frame, text="Громкость системы:", style="TLabel").grid(row=17, column=0, sticky="w", pady=(0, 5))
        ttk.Scale(settings_frame, from_=0.0, to=2.0, variable=self.system_volume_var, orient=tk.HORIZONTAL, length=150).grid(row=18, column=0, sticky="we", pady=(0, 10))
        ttk.Label(settings_frame, text="Усиление (dB):", style="TLabel").grid(row=19, column=0, sticky="w", pady=(0, 5))
        ttk.Scale(settings_frame, from_=-20.0, to=20.0, variable=self.audio_gain_var, orient=tk.HORIZONTAL, length=150).grid(row=20, column=0, sticky="we", pady=(0, 10))
        ttk.Label(settings_frame, text="Компрессия:", style="TLabel").grid(row=21, column=0, sticky="w", pady=(0, 5))
        ttk.Scale(settings_frame, from_=0.1, to=10.0, variable=self.audio_compression_var, orient=tk.HORIZONTAL, length=150).grid(row=22, column=0, sticky="we", pady=(0, 15))
        ttk.Checkbutton(settings_frame, text="Подавление шума", variable=self.noise_suppression_var, command=self.toggle_noise_suppression).grid(row=23, column=0, sticky="w", pady=(0, 15))

        settings_frame.columnconfigure(0, weight=1)

        # Effects tab
        effects_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=25)
        self.notebook.add(effects_frame, text="Эффекты")

        # Duplicate preview for effects tab
        preview_frame_eff = ttk.Frame(effects_frame, style="Card.TFrame")
        preview_frame_eff.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        self.preview_canvas_eff = tk.Canvas(preview_frame_eff, bg="black", highlightthickness=0, width=960, height=540)
        self.preview_canvas_eff.pack(fill="both", expand=True)
        self.preview_canvas_eff.bind("<Button-1>", self.start_drag_eff)
        self.preview_canvas_eff.bind("<B1-Motion>", self.drag_camera_eff)
        self.preview_canvas_eff.bind("<ButtonRelease-1>", self.stop_drag_eff)
        effects_frame.columnconfigure(1, weight=1)
        effects_frame.rowconfigure(0, weight=1)

        # Scrollable effects panel
        scroll_container = tk.Frame(effects_frame, bg=self.card_color)
        scroll_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        self.effects_canvas = tk.Canvas(scroll_container, bg=self.card_color, highlightthickness=0, width=250)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.effects_canvas.yview)
        self.scrollable_effects_frame = ttk.Frame(self.effects_canvas, style="Card.TFrame", padding=20)

        self.scrollable_effects_frame.bind(
            "<Configure>",
            lambda e: self.effects_canvas.configure(scrollregion=self.effects_canvas.bbox("all"))
        )

        self.effects_canvas.create_window((0, 0), window=self.scrollable_effects_frame, anchor="nw")
        self.effects_canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mousewheel
        def on_mousewheel(event):
            self.effects_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.effects_canvas.bind("<MouseWheel>", on_mousewheel)
        self.scrollable_effects_frame.bind("<MouseWheel>", on_mousewheel)  # Also bind to frame for better UX

        # Pack scrollbar and canvas
        self.effects_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Effect sliders with shorter length
        effects = [
            ("Яркость", self.brightness_var, -100, 100),
            ("Контраст", self.contrast_var, 0.0, 3.0),
            ("Размытие", self.blur_var, 0, 10),
            ("Оттенок", self.hue_var, -180, 180),
            ("Насыщенность", self.saturation_var, 0.0, 2.0),
            ("Резкость", self.sharpness_var, 0, 1.0),
            ("Гамма", self.gamma_var, 0.1, 3.0),
            ("Температура цвета", self.temperature_var, -100, 100),
            ("Тон", self.tint_var, -100, 100),
            ("Виньетирование", self.vignette_var, 0, 1.0),
            ("Шум", self.noise_var, 0, 1.0),
            ("Сепия", self.sepia_var, 0, 1.0),
            ("Оттенки серого", self.grayscale_var, 0, 1.0),
            ("Инверсия", self.invert_var, 0, 1.0),
            ("Усиление краев", self.edge_var, 0, 1.0),
            ("Эмбосс", self.emboss_var, 0, 1.0),
            ("Постеризация", self.posterize_var, 0, 1.0),
            ("Соляризация", self.solarize_var, 0, 1.0)
        ]

        for i, (label, var, from_, to) in enumerate(effects):
            ttk.Label(self.scrollable_effects_frame, text=f"{label}:", style="TLabel").grid(row=i*2, column=0, sticky="w", pady=(0, 5))
            ttk.Scale(self.scrollable_effects_frame, from_=from_, to=to, variable=var, orient=tk.HORIZONTAL, length=120).grid(row=i*2+1, column=0, sticky="we", pady=(0, 10))

        self.scrollable_effects_frame.columnconfigure(0, weight=1)

    def on_resolution_change(self, *args):
        # Trigger preview update on resolution change
        if hasattr(self, 'preview_updater') and self.preview_updater:
            self.preview_updater.restart_preview()

    def on_fps_change(self, *args):
        # Update preview FPS on FPS change
        if hasattr(self, 'preview_fps_var'):
            self.preview_fps_var.set(self.fps_var.get())

    # Drag methods for recording preview
    def start_drag_rec(self, event):
        self.start_drag(event, self.preview_canvas_rec)

    def drag_camera_rec(self, event):
        self.drag_camera(event, self.preview_canvas_rec)

    def stop_drag_rec(self, event):
        self.stop_drag()

    # Drag methods for effects preview
    def start_drag_eff(self, event):
        self.start_drag(event, self.preview_canvas_eff)

    def drag_camera_eff(self, event):
        self.drag_camera(event, self.preview_canvas_eff)

    def stop_drag_eff(self, event):
        self.stop_drag()

    def start_drag(self, event, canvas):
        if not self.camera_enabled or self.only_camera_var.get() or not self.preview_updater:
            return
        try:
            pw, ph = self.preview_updater.preview_resolution
            canvas_w = canvas.winfo_width()
            canvas_h = canvas.winfo_height()
            if canvas_w <= 1 or canvas_h <= 1:
                return
            # Calculate scaling to fit preview in canvas
            scale = min(canvas_w / pw, canvas_h / ph)
            new_w = int(pw * scale)
            new_h = int(ph * scale)
            offset_x = (canvas_w - new_w) // 2
            offset_y = (canvas_h - new_h) // 2
            # Convert mouse coordinates to preview coordinates
            preview_x = (event.x - offset_x) / scale
            preview_y = (event.y - offset_y) / scale
            # Webcam size in preview resolution
            cam_w = int(160 * self.camera_scale)
            cam_h = int(120 * self.camera_scale)
            x1, y1 = self.camera_position
            x2 = x1 + cam_w
            y2 = y1 + cam_h
            # Check if click is within webcam bounds
            if x1 <= preview_x <= x2 and y1 <= preview_y <= y2:
                self.dragging_camera = True
                self.drag_start_px = preview_x
                self.drag_start_py = preview_y
                self.camera_start_x = x1
                self.camera_start_y = y1
                self.drag_scale = scale
                self.drag_offset_x = offset_x
                self.drag_offset_y = offset_y
                self.drag_pw = pw
                self.drag_ph = ph
                self.drag_cam_w = cam_w
                self.drag_cam_h = cam_h
        except Exception as e:
            print(f"Error in start_drag: {e}")

    def drag_camera(self, event, canvas):
        if self.dragging_camera and self.camera_enabled and not self.only_camera_var.get():
            try:
                canvas_w = canvas.winfo_width()
                canvas_h = canvas.winfo_height()
                if canvas_w <= 1 or canvas_h <= 1:
                    return
                # Convert mouse coordinates to preview coordinates
                preview_x = (event.x - self.drag_offset_x) / self.drag_scale
                preview_y = (event.y - self.drag_offset_y) / self.drag_scale
                # Calculate new webcam position
                new_x = self.camera_start_x + (preview_x - self.drag_start_px)
                new_y = self.camera_start_y + (preview_y - self.drag_start_py)
                # Ensure webcam stays within preview bounds
                new_x = max(0, min(new_x, self.drag_pw - self.drag_cam_w))
                new_y = max(0, min(new_y, self.drag_ph - self.drag_cam_h))
                self.camera_position = [int(new_x), int(new_y)]
            except Exception as e:
                print(f"Error in drag_camera: {e}")

    def stop_drag(self, event=None):
        self.dragging_camera = False

    def toggle_screen(self):
        self.screen_capture_enabled = self.screen_var.get()

    def toggle_camera(self):
        self.camera_enabled = self.camera_var.get()

    def toggle_audio(self):
        self.audio_enabled = self.audio_var.get()

    def toggle_noise_suppression(self):
        self.audio_filters['noise_suppression'] = self.noise_suppression_var.get()

    def toggle_only_camera(self):
        pass  # Handled in VideoRecorder and PreviewUpdater

    def start_preview(self):
        self.preview_updater = PreviewUpdater(self)
        self.preview_updater.start()

    def update_preview_gui(self, frame):
        if not self.preview_update_active:
            return
        try:
            # Update both canvases
            self.update_single_canvas(self.preview_canvas_rec, frame)
            self.update_single_canvas(self.preview_canvas_eff, frame)
        except Exception as e:
            print(f"Ошибка обновления предпросмотра: {e}")

    def update_single_canvas(self, canvas, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            return
        # Calculate scaling to fit image in canvas while preserving aspect ratio
        img_ratio = img.width / img.height
        canvas_ratio = canvas_width / canvas_height
        if img_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / img_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * img_ratio)
        # Resize image with high-quality interpolation
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        canvas.delete("preview")
        canvas.create_image(canvas_width // 2, canvas_height // 2,
                            image=photo, anchor=tk.CENTER, tags="preview")
        canvas.image = photo

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.toggle_pause()

    def start_recording(self):
        try:
            if self.custom_resolution_enabled:
                try:
                    width = int(self.custom_width_var.get())
                    height = int(self.custom_height_var.get())
                    if width <= 0 or height <= 0:
                        raise ValueError("Разрешение должно быть положительным")
                    resolution = (width, height)
                except ValueError as e:
                    messagebox.showerror("Ошибка", f"Неверное разрешение: {str(e)}")
                    return
            else:
                res_str = self.resolution_var.get()
                width, height = map(int, res_str.split('x'))
                resolution = (width, height)

            fps = int(self.fps_var.get())
            bitrate = int(self.bitrate_var.get()) * 1000000

            self.video_recorder = VideoRecorder(self, resolution, fps, bitrate)
            if self.audio_enabled:
                self.audio_recorder = AudioRecorder(
                    mic_volume=self.mic_volume_var.get(),
                    system_volume=self.system_volume_var.get(),
                    noise_suppression=self.audio_filters['noise_suppression'],
                    gain=self.audio_gain_var.get(),
                    compression=self.audio_compression_var.get()
                )
            self.video_recorder.start()
            if self.audio_enabled:
                self.audio_recorder.start()
            self.recording = True
            self.start_time = time.time()
            self.total_pause_time = 0
            self.update_timer()
            self.status_var.set("Запись...")
            self.recording_indicator.itemconfig(self.recording_circle, fill="#ef4444")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось начать запись: {str(e)}")

    def pause_recording(self):
        self.paused = True
        self.pause_time = time.time()
        self.status_var.set("Пауза")

    def resume_recording(self):
        self.paused = False
        self.total_pause_time += time.time() - self.pause_time
        self.status_var.set("Запись...")

    def toggle_pause(self):
        if not self.recording:
            return
        if self.paused:
            self.resume_recording()
        else:
            self.pause_recording()

    def stop_recording(self):
        self.recording = False
        self.paused = False
        if self.video_recorder:
            self.video_recorder.stop()
            self.video_recorder = None
        if self.audio_recorder:
            self.audio_recorder.stop()
            self.audio_recorder = None
        self.status_var.set("Запись остановлена")
        self.recording_indicator.itemconfig(self.recording_circle, fill="#4b5563")
        self.time_var.set("00:00:00")

    def update_timer(self):
        if self.recording and not self.paused:
            elapsed = time.time() - self.start_time - self.total_pause_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.time_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)

    def save_video(self):
        if not os.path.exists('temp_video.avi'):
            messagebox.showwarning("Предупреждение", "Нет записанного видео для сохранения")
            return
        file_path = filedialog.asksaveasfilename(
            initialdir=self.save_dir_var.get(),
            defaultextension=f".{self.file_format_var.get()}",
            filetypes=[("Видео файлы", "*.mp4 *.avi *.mov"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                if self.audio_enabled and os.path.exists('temp_audio.wav'):
                    subprocess.run(['ffmpeg', '-y', '-i', 'temp_video.avi', '-i', 'temp_audio.wav', '-c:v', 'copy', '-c:a', 'aac', '-shortest', file_path], check=True)
                    os.remove('temp_audio.wav')
                else:
                    import shutil
                    shutil.copy2('temp_video.avi', file_path)
                os.remove('temp_video.avi')
                messagebox.showinfo("Успех", f"Видео сохранено как {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить видео: {str(e)}")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            self.hotkeys.update(settings.get('hotkeys', {}))
            self.bind_hotkeys()
        except FileNotFoundError:
            pass

    def save_settings(self):
        settings = {'hotkeys': self.hotkeys}
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_profile(self, *args):
        profile = self.profile_var.get()
        profiles = {
            'По умолчанию': {'resolution': '1920x1080', 'fps': 30, 'bitrate': 15},
            'Высокое качество': {'resolution': '3840x2160', 'fps': 60, 'bitrate': 25}
        }
        self.output_profile = profiles.get(profile, profiles['По умолчанию'])
        self.resolution_var.set(self.output_profile['resolution'])
        self.fps_var.set(str(self.output_profile['fps']))
        self.bitrate_var.set(str(self.output_profile['bitrate']))
        # Trigger preview updates
        self.on_resolution_change()
        self.on_fps_change()

    def on_closing(self):
        if self.recording:
            self.stop_recording()
        self.preview_update_active = False
        if hasattr(self, 'preview_updater') and self.preview_updater:
            self.preview_updater.stop()
            self.preview_updater = None
        self.save_settings()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TarantinoCatch(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()