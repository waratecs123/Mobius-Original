import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
import pyautogui
import threading
import time
from PIL import Image, ImageTk
import os
from functions import VideoRecorder, AudioRecorder, PreviewUpdater

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
        self.entry_text_color = "#FFFFFF"  # Black text for entry fields

        # Fonts
        self.title_font = ('Inter', 22, 'bold')
        self.app_font = ('Inter', 13)
        self.button_font = ('Inter', 12)
        self.small_font = ('Inter', 11)

        # Window configuration
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Control-r>', lambda e: self.toggle_recording())
        self.root.bind('<Control-p>', lambda e: self.toggle_pause())
        self.root.bind('<Control-s>', lambda e: self.stop_recording())
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

        # Recorder objects
        self.video_recorder = None
        self.audio_recorder = None
        self.preview_updater = None

        self.setup_styles()
        self.setup_ui()
        self.start_preview()

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

        # Configure Entry style for black text
        style.configure("TEntry",
                        fieldbackground=self.card_color,
                        foreground=self.entry_text_color,
                        borderwidth=1,
                        padding=5)
        style.map("TEntry",
                  fieldbackground=[('focus', '#ffffff')],
                  foreground=[('focus', self.entry_text_color)])

        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=self.card_color,
                        foreground=self.secondary_text,
                        padding=[20, 10],
                        font=self.button_font)
        style.map("TNotebook.Tab",
                  background=[("selected", self.sidebar_color)],
                  foreground=[("selected", self.accent_color)])

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
        ttk.Button(controls_frame, text="Стоп (Ctrl+S)",
                   command=self.stop_recording, style="Secondary.TButton").pack(fill=tk.X, pady=5)
        ttk.Button(controls_frame, text="Сохранить видео",
                   command=self.save_video, style="Secondary.TButton").pack(fill=tk.X, pady=5)

        # Main content area
        self.main_area = ttk.Frame(main_container, style="TFrame")
        self.main_area.pack(side="right", fill="both", expand=True)

        # Tabs
        self.notebook = ttk.Notebook(self.main_area, style="TNotebook")
        self.notebook.pack(fill='both', expand=True)

        # Recording tab
        main_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=25)
        self.notebook.add(main_frame, text="Запись")

        # Settings panel
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки записи", padding=20, style="Card.TFrame")
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Resolution settings
        ttk.Label(settings_frame, text="Разрешение:", style="TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.resolution_var = tk.StringVar(value="1920x1080")
        resolutions = ["3840x2160", "2560x1440", "1920x1080", "1280x720", "1024x576"]
        ttk.Combobox(settings_frame, textvariable=self.resolution_var, values=resolutions,
                     width=20, state="readonly").grid(row=1, column=0, sticky="we", pady=(0, 15))

        # Custom resolution
        custom_frame = ttk.Frame(settings_frame, style="TFrame")
        custom_frame.grid(row=2, column=0, sticky="we", pady=(0, 15))
        self.custom_res_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(custom_frame, text="Пользовательское разрешение",
                        variable=self.custom_res_var, command=self.toggle_custom_resolution).grid(row=0, column=0, sticky="w")

        self.custom_width_var = tk.StringVar(value="1920")
        self.custom_height_var = tk.StringVar(value="1080")
        ttk.Entry(custom_frame, textvariable=self.custom_width_var, width=8, style="TEntry").grid(row=1, column=0, pady=(5, 0))
        ttk.Label(custom_frame, text="x").grid(row=1, column=1, padx=5)
        ttk.Entry(custom_frame, textvariable=self.custom_height_var, width=8, style="TEntry").grid(row=1, column=2)

        # Video settings
        ttk.Label(settings_frame, text="Битрейт видео (Мбит/с):", style="TLabel").grid(row=3, column=0, sticky="w",
                                                                                     pady=(15, 8))
        self.bitrate_var = tk.StringVar(value="15")
        ttk.Combobox(settings_frame, textvariable=self.bitrate_var,
                     values=["5", "10", "15", "20", "25"], width=20).grid(row=4, column=0, sticky="we", pady=(0, 15))

        ttk.Label(settings_frame, text="Частота кадров:", style="TLabel").grid(row=5, column=0, sticky="w", pady=(15, 8))
        self.fps_var = tk.StringVar(value="30")
        ttk.Combobox(settings_frame, textvariable=self.fps_var,
                     values=["60", "30", "24"], width=20).grid(row=6, column=0, sticky="we", pady=(0, 15))

        # Input sources
        ttk.Label(settings_frame, text="Источники видео:", style="TLabel").grid(row=7, column=0, sticky="w", pady=(15, 8))
        sources_frame = ttk.Frame(settings_frame, style="TFrame")
        sources_frame.grid(row=8, column=0, sticky="we")

        self.screen_var = tk.BooleanVar(value=True)
        self.camera_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sources_frame, text="Захват экрана", variable=self.screen_var,
                        command=self.toggle_screen_capture).grid(row=0, column=0, sticky="w", padx=(0, 20))
        ttk.Checkbutton(sources_frame, text="Камера", variable=self.camera_var,
                        command=self.toggle_camera).grid(row=0, column=1, sticky="w")

        # Camera settings
        ttk.Label(settings_frame, text="Устройство камеры:", style="TLabel").grid(row=9, column=0, sticky="w", pady=(15, 8))
        self.camera_index_var = tk.StringVar(value="0")
        ttk.Combobox(settings_frame, textvariable=self.camera_index_var,
                     values=["0", "1", "2", "3"], width=20).grid(row=10, column=0, sticky="we", pady=(0, 15))

        ttk.Label(settings_frame, text="Масштаб камеры:", style="TLabel").grid(row=11, column=0, sticky="w", pady=(15, 8))
        self.scale_var = tk.DoubleVar(value=1.0)
        scale_frame = ttk.Frame(settings_frame, style="TFrame")
        scale_frame.grid(row=12, column=0, sticky="we")
        ttk.Scale(scale_frame, from_=0.5, to=2.0, variable=self.scale_var,
                  orient=tk.HORIZONTAL, command=self.update_camera_scale).pack(fill=tk.X)
        self.scale_value_label = ttk.Label(scale_frame, text="1.0x", style="TLabel")
        self.scale_value_label.pack(pady=5)

        # Audio settings
        ttk.Label(settings_frame, text="Настройки аудио:", style="TLabel").grid(row=13, column=0, sticky="w",
                                                                               pady=(15, 8))
        self.audio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Записывать аудио", variable=self.audio_var,
                        command=self.toggle_audio).grid(row=14, column=0, sticky="w")

        # Preview panel
        preview_frame = ttk.LabelFrame(main_frame, text="ПРЕДПРОСМОТР ЗАПИСИ И ВЕБ-КАМЕРЫ", padding=20,
                                       style="Card.TFrame")
        preview_frame.grid(row=0, column=1, sticky="nsew")
        self.preview_canvas = tk.Canvas(preview_frame, bg=self.card_color, highlightthickness=0)
        self.preview_canvas.pack(expand=True, fill=tk.BOTH)
        self.preview_canvas.bind("<Button-1>", self.start_drag)
        self.preview_canvas.bind("<B1-Motion>", self.drag_camera)
        self.preview_canvas.bind("<ButtonRelease-1>", self.stop_drag)

        # Status bar
        status_frame = tk.Frame(main_frame, bg=self.card_color)
        status_frame.grid(row=1, column=0, columnspan=2, sticky="we", pady=20)

        self.status_var = tk.StringVar(value="Готово к записи")
        ttk.Label(status_frame, textvariable=self.status_var, style="Subtitle.TLabel").pack(side=tk.LEFT)

        self.recording_indicator = tk.Canvas(status_frame, width=20, height=20, bg=self.card_color,
                                             highlightthickness=0)
        self.recording_indicator.pack(side=tk.LEFT, padx=10)
        self.recording_circle = self.recording_indicator.create_oval(4, 4, 16, 16, fill="#4b5563", outline="")

        self.time_var = tk.StringVar(value="00:00:00")
        ttk.Label(status_frame, textvariable=self.time_var, style="Subtitle.TLabel").pack(side=tk.RIGHT)

        # Settings tab
        settings_tab = ttk.Frame(self.notebook, style="Card.TFrame", padding=25)
        self.notebook.add(settings_tab, text="⚙️ Настройки")
        self.setup_settings_tab(settings_tab)

        # Grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)
        settings_frame.columnconfigure(0, weight=1)

    def setup_settings_tab(self, parent):
        preview_frame = ttk.LabelFrame(parent, text="Настройки предпросмотра", padding=20, style="Card.TFrame")
        preview_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(preview_frame, text="Частота предпросмотра (FPS):", style="TLabel").grid(row=0, column=0, sticky="w")
        self.preview_fps_var = tk.StringVar(value="30")
        ttk.Combobox(preview_frame, textvariable=self.preview_fps_var,
                     values=["60", "30", "15"], width=15).grid(row=0, column=1, sticky="w", padx=10)

        save_frame = ttk.LabelFrame(parent, text="Настройки сохранения", padding=20, style="Card.TFrame")
        save_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(save_frame, text="Папка сохранения:", style="TLabel").grid(row=0, column=0, sticky="w")
        self.save_dir_var = tk.StringVar(value=os.path.expanduser("~/Videos"))
        ttk.Entry(save_frame, textvariable=self.save_dir_var, width=40, style="TEntry").grid(row=0, column=1, sticky="w", padx=10)
        ttk.Button(save_frame, text="Обзор", command=self.browse_save_dir,
                   style="Secondary.TButton").grid(row=0, column=2, padx=10)

        ttk.Label(save_frame, text="Формат файла:", style="TLabel").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.file_format_var = tk.StringVar(value="mp4")
        ttk.Combobox(save_frame, textvariable=self.file_format_var,
                     values=["mp4", "avi", "mov"], width=15).grid(row=1, column=1, sticky="w", padx=10, pady=(10, 0))

    def browse_save_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir_var.set(directory)

    def start_preview(self):
        self.preview_updater = PreviewUpdater(self)
        self.preview_updater.start()

    def toggle_custom_resolution(self):
        self.custom_resolution_enabled = self.custom_res_var.get()

    def toggle_screen_capture(self):
        self.screen_capture_enabled = self.screen_var.get()

    def toggle_camera(self):
        self.camera_enabled = self.camera_var.get()

    def toggle_audio(self):
        self.audio_enabled = self.audio_var.get()

    def update_camera_scale(self, value):
        self.camera_scale = float(value)
        self.scale_value_label.config(text=f"{float(value):.1f}x")

    def start_drag(self, event):
        if self.camera_enabled:
            base_width, base_height = 160, 120
            scaled_width = int(base_width * self.camera_scale)
            scaled_height = int(base_height * self.camera_scale)

            x1, y1 = self.camera_position
            x2, y2 = x1 + scaled_width, y1 + scaled_height

            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.dragging_camera = True
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                self.camera_start_x = x1
                self.camera_start_y = y1

    def drag_camera(self, event):
        if self.dragging_camera and self.camera_enabled:
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            base_width, base_height = 160, 120
            scaled_width = int(base_width * self.camera_scale)
            scaled_height = int(base_height * self.camera_scale)

            new_x = self.camera_start_x + (event.x - self.drag_start_x)
            new_y = self.camera_start_y + (event.y - self.drag_start_y)

            new_x = max(0, min(new_x, canvas_width - scaled_width))
            new_y = max(0, min(new_y, canvas_height - scaled_height))
            self.camera_position = [new_x, new_y]

    def stop_drag(self, event):
        self.dragging_camera = False

    def update_preview_gui(self, frame):
        if not self.preview_update_active:
            return

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            if canvas_width > 1 and canvas_height > 1:
                img_ratio = img.width / img.height
                canvas_ratio = canvas_width / canvas_height

                if img_ratio > canvas_ratio:
                    new_width = canvas_width
                    new_height = int(canvas_width / img_ratio)
                else:
                    new_height = canvas_height
                    new_width = int(canvas_height * img_ratio)

                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                self.preview_canvas.delete("preview")
                self.preview_canvas.create_image(canvas_width // 2, canvas_height // 2,
                                                 image=photo, anchor=tk.CENTER, tags="preview")
                self.preview_canvas.image = photo

        except Exception as e:
            print(f"Ошибка обновления предпросмотра: {e}")

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.pause_recording()

    def start_recording(self):
        try:
            # Validate resolution
            if self.custom_resolution_enabled:
                try:
                    width = int(self.custom_width_var.get())
                    height = int(self.custom_height_var.get())
                    if width <= 0 or height <= 0:
                        raise ValueError("Разрешение должно быть положительным")
                    resolution = (width, height)
                except ValueError as e:
                    messagebox.showerror("Ошибка", f"Недопустимое разрешение: {str(e)}")
                    return
            else:
                res_str = self.resolution_var.get()
                width, height = map(int, res_str.split('x'))
                resolution = (width, height)

            fps = int(self.fps_var.get())
            bitrate = int(self.bitrate_var.get()) * 1000000

            self.video_recorder = VideoRecorder(self, resolution, fps, bitrate)
            if self.audio_enabled:
                self.audio_recorder = AudioRecorder()

            self.video_recorder.start()
            if self.audio_enabled:
                self.audio_recorder.start()

            self.recording = True
            self.start_time = time.time()
            self.total_pause_time = 0
            self.update_timer()

            self.status_var.set("Идёт запись...")
            self.recording_indicator.itemconfig(self.recording_circle, fill="#ef4444")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось начать запись: {str(e)}")

    def pause_recording(self):
        self.paused = True
        self.pause_time = time.time()
        self.status_var.set("На паузе")

    def resume_recording(self):
        self.paused = False
        self.total_pause_time += time.time() - self.pause_time
        self.status_var.set("Идёт запись...")

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
                import shutil
                shutil.copy2('temp_video.avi', file_path)
                messagebox.showinfo("Успех", f"Видео сохранено как {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить видео: {str(e)}")

    def on_closing(self):
        if self.recording:
            self.stop_recording()
        self.preview_update_active = False
        if hasattr(self, 'preview_updater') and self.preview_updater:
            self.preview_updater.stop()
            self.preview_updater = None
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TarantinoCatch(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()