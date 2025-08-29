import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
import pyautogui
import threading
import time
from PIL import Image, ImageTk
import os
import subprocess
import pyaudio
import wave
from functions import VideoRecorder, AudioRecorder, PreviewUpdater


class TarantinoCatch:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarantino Catch - Цифровой режиссёр")

        # Устанавливаем полноэкранный режим
        self.root.attributes('-fullscreen', True)
        self.fullscreen_state = True

        # Блокируем стандартные сочетания клавиш для выхода из полноэкранного режима
        self.root.bind('<Escape>', lambda e: "break")
        self.root.bind('<F11>', lambda e: "break")
        self.root.bind('<Alt-Return>', lambda e: "break")

        # Современная цветовая палитра
        self.bg_color = "#0f0f0f"
        self.sidebar_color = "#1a1a1a"
        self.card_color = "#2a2a2a"
        self.accent_color = "#ff4d4d"  # Яркий акцентный цвет
        self.text_color = "#ffffff"
        self.secondary_text = "#b0b0b0"
        self.border_color = "#404040"

        self.root.configure(bg=self.bg_color)

        # Переменные для записи
        self.recording = False
        self.paused = False
        self.camera_enabled = True
        self.screen_capture_enabled = True
        self.audio_enabled = True
        self.cap = None
        self.out = None
        self.audio_cap = None
        self.start_time = 0
        self.pause_time = 0
        self.total_pause_time = 0
        self.camera_position = [10, 10]
        self.camera_scale = 1.0  # Масштаб камеры
        self.dragging_camera = False
        self.custom_resolution_enabled = False
        self.preview_update_active = True

        # Объекты для записи
        self.video_recorder = None
        self.audio_recorder = None
        self.preview_updater = None

        self.setup_ui()
        self.start_preview()

    def setup_ui(self):
        # Стилизация
        style = ttk.Style()
        style.theme_use('clam')

        # Настройка стилей
        style.configure(".", background=self.bg_color, foreground=self.text_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("Sidebar.TFrame", background=self.sidebar_color)
        style.configure("Card.TFrame", background=self.card_color, relief="flat", borderwidth=1)
        style.configure("TLabel", background=self.card_color, foreground=self.text_color)
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground=self.accent_color)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground=self.secondary_text)
        style.configure("TButton", background=self.card_color, foreground=self.text_color,
                        borderwidth=1, focusthickness=3, focuscolor=self.accent_color)
        style.configure("Accent.TButton", background=self.accent_color, foreground="#ffffff")
        style.configure("TCombobox", fieldbackground=self.card_color, background=self.card_color,
                        foreground=self.text_color)
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.sidebar_color, foreground=self.secondary_text,
                        padding=[15, 5], font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", self.card_color)],
                  foreground=[("selected", self.text_color)])

        # Главный контейнер
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill='both', expand=True, padx=0, pady=0)

        # Сайдбар
        sidebar = ttk.Frame(main_container, width=280, style="Sidebar.TFrame")
        sidebar.pack(side="left", fill="y", padx=(0, 1))
        sidebar.pack_propagate(False)

        # Логотип и название
        logo_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        logo_frame.pack(pady=(20, 30), padx=20, fill="x")

        # Простой современный логотип
        logo_canvas = tk.Canvas(logo_frame, bg=self.sidebar_color, width=32, height=32,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")
        # Минималистичный логотип - красный квадрат
        logo_canvas.create_rectangle(4, 4, 28, 28, fill=self.accent_color, outline="")

        tk.Label(logo_frame, text="TARANTINO CATCH", font=('Segoe UI', 14, 'bold'),
                 bg=self.sidebar_color, fg=self.text_color).pack(side="left", padx=12)

        # Основная область
        self.main_area = ttk.Frame(main_container, style="TFrame")
        self.main_area.pack(side="right", fill="both", expand=True)

        # Заголовок и кнопки управления
        header_frame = ttk.Frame(self.main_area, style="TFrame")
        header_frame.pack(fill="x", padx=25, pady=(25, 15))


        # Кнопки управления записью
        control_frame = ttk.Frame(header_frame, style="TFrame")
        control_frame.pack(side="right")

        # Стилизованные кнопки
        self.record_button = tk.Button(control_frame, text="● Начать запись", font=('Segoe UI', 11),
                                       bg=self.accent_color, fg="#ffffff", bd=0,
                                       activebackground="#e03c3c", padx=20, pady=10,
                                       command=self.toggle_recording, cursor="hand2")
        self.record_button.pack(side="left", padx=(0, 8))

        self.pause_button = tk.Button(control_frame, text="⏸️ Пауза", font=('Segoe UI', 11),
                                      bg="#404040", fg="#ffffff", bd=0,
                                      activebackground="#505050", padx=20, pady=10,
                                      command=self.toggle_pause, state=tk.DISABLED, cursor="hand2")
        self.pause_button.pack(side="left", padx=(0, 8))

        self.stop_button = tk.Button(control_frame, text="⏹️ Завершить", font=('Segoe UI', 11),
                                     bg="#404040", fg="#ffffff", bd=0,
                                     activebackground="#505050", padx=20, pady=10,
                                     command=self.stop_recording, state=tk.DISABLED, cursor="hand2")
        self.stop_button.pack(side="left")

        # Новая кнопка для записи только вебкамеры
        self.camera_only_button = tk.Button(control_frame, text="📷 Только камера", font=('Segoe UI', 11),
                                            bg="#404040", fg="#ffffff", bd=0,
                                            activebackground="#505050", padx=20, pady=10,
                                            command=self.toggle_camera_only, cursor="hand2")
        self.camera_only_button.pack(side="left", padx=(8, 0))

        # Контент с вкладками
        self.notebook = ttk.Notebook(self.main_area, style="TNotebook")
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Вкладка основной записи
        main_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding="20")
        self.notebook.add(main_frame, text="Основная запись")

        # Левая панель - настройки
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки записи", padding="15", style="Card.TFrame")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))

        # Настройки разрешения
        ttk.Label(settings_frame, text="Разрешение записи:", font=("Segoe UI", 10)).grid(row=0, column=0,
                                                                                         sticky=tk.W,
                                                                                         pady=(0, 8))

        self.resolution_var = tk.StringVar(value="1920x1080")
        resolutions = [
            "3840x2160", "2560x1440", "1920x1080", "1280x720",
            "1024x576", "854x480", "640x360", "426x240"
        ]

        resolution_combo = ttk.Combobox(settings_frame, textvariable=self.resolution_var,
                                        values=resolutions, width=18, state="readonly")
        resolution_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Настройка кастомного разрешения
        custom_frame = ttk.Frame(settings_frame, style="TFrame")
        custom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        self.custom_res_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(custom_frame, text="Кастомное разрешение",
                        variable=self.custom_res_var, command=self.toggle_custom_resolution).grid(row=0, column=0,
                                                                                                  sticky=tk.W)

        ttk.Label(custom_frame, text="Ширина:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.custom_width_var = tk.StringVar(value="1920")
        ttk.Entry(custom_frame, textvariable=self.custom_width_var, width=8).grid(row=1, column=1, pady=(5, 0),
                                                                                  padx=(5, 0))

        ttk.Label(custom_frame, text="Высота:").grid(row=1, column=2, sticky=tk.W, pady=(5, 0), padx=(10, 0))
        self.custom_height_var = tk.StringVar(value="1080")
        ttk.Entry(custom_frame, textvariable=self.custom_height_var, width=8).grid(row=1, column=3, pady=(5, 0))

        # Настройки битрейта
        ttk.Label(settings_frame, text="Битрейт видео:", font=("Segoe UI", 10)).grid(row=3, column=0,
                                                                                     sticky=tk.W,
                                                                                     pady=(15, 8))

        self.bitrate_var = tk.StringVar(value="15")
        bitrate_combo = ttk.Combobox(settings_frame, textvariable=self.bitrate_var,
                                     values=["1", "2", "5", "10", "15", "20", "25", "30"], width=18)
        bitrate_combo.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Настройки FPS
        ttk.Label(settings_frame, text="Частота кадров:", font=("Segoe UI", 10)).grid(row=5, column=0,
                                                                                      sticky=tk.W,
                                                                                      pady=(15, 8))

        self.fps_var = tk.StringVar(value="30")
        fps_combo = ttk.Combobox(settings_frame, textvariable=self.fps_var,
                                 values=["120", "60", "30", "25", "24", "15"], width=18)
        fps_combo.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Настройки захвата видео
        ttk.Label(settings_frame, text="Источники видео:", font=("Segoe UI", 10)).grid(row=7, column=0,
                                                                                       sticky=tk.W,
                                                                                       pady=(15, 8))

        capture_frame = ttk.Frame(settings_frame, style="TFrame")
        capture_frame.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        self.screen_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(capture_frame, text="Захват экрана", variable=self.screen_var,
                        command=self.toggle_screen_capture).grid(row=0, column=0, sticky=tk.W)

        self.camera_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(capture_frame, text="Захват камеры", variable=self.camera_var,
                        command=self.toggle_camera).grid(row=0, column=1, sticky=tk.W)

        # Выбор камеры
        ttk.Label(settings_frame, text="Выбор камеры:").grid(row=9, column=0, sticky=tk.W, pady=(15, 8))

        self.camera_index_var = tk.StringVar(value="0")
        camera_combo = ttk.Combobox(settings_frame, textvariable=self.camera_index_var,
                                    values=["0", "1", "2", "3"], width=18)
        camera_combo.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Настройки масштаба камеры
        ttk.Label(settings_frame, text="Масштаб камеры:").grid(row=11, column=0, sticky=tk.W, pady=(15, 8))

        scale_frame = ttk.Frame(settings_frame, style="TFrame")
        scale_frame.grid(row=12, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        self.scale_var = tk.DoubleVar(value=1.0)
        scale_slider = ttk.Scale(scale_frame, from_=0.5, to=2.0, variable=self.scale_var,
                                 orient=tk.HORIZONTAL, command=self.update_camera_scale)
        scale_slider.pack(fill=tk.X)

        scale_value_label = ttk.Label(scale_frame, text="1.0x", style="TLabel")
        scale_value_label.pack()
        self.scale_value_label = scale_value_label

        # Настройки аудио
        ttk.Label(settings_frame, text="Настройки аудио:", font=("Segoe UI", 10)).grid(row=13, column=0,
                                                                                       sticky=tk.W,
                                                                                       pady=(15, 8))

        audio_frame = ttk.Frame(settings_frame, style="TFrame")
        audio_frame.grid(row=14, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        self.audio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(audio_frame, text="Запись звука", variable=self.audio_var,
                        command=self.toggle_audio).grid(row=0, column=0, sticky=tk.W)

        # Выбор аудио устройства
        ttk.Label(settings_frame, text="Аудио устройство:").grid(row=15, column=0, sticky=tk.W, pady=(15, 8))

        self.audio_device_var = tk.StringVar(value="Микрофон")
        audio_combo = ttk.Combobox(settings_frame, textvariable=self.audio_device_var,
                                   values=["Микрофон", "Системный звук", "Микрофон + Системный звук"], width=18)
        audio_combo.grid(row=16, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Битрейт аудио
        ttk.Label(settings_frame, text="Битрейт аудио:").grid(row=17, column=0, sticky=tk.W, pady=(15, 8))

        self.audio_bitrate_var = tk.StringVar(value="128")
        audio_bitrate_combo = ttk.Combobox(settings_frame, textvariable=self.audio_bitrate_var,
                                           values=["64", "96", "128", "192", "256", "320"], width=18)
        audio_bitrate_combo.grid(row=18, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Кнопки управления
        button_frame = ttk.Frame(settings_frame, style="TFrame")
        button_frame.grid(row=19, column=0, sticky=(tk.W, tk.E))

        ttk.Button(button_frame, text="Сохранить видео",
                   command=self.save_video, style="TButton").pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="Настройки предпросмотра",
                   command=self.open_preview_settings, style="TButton").pack(fill=tk.X)

        # Правая панель - предпросмотр
        preview_frame = ttk.LabelFrame(main_frame, text="Предпросмотр - Перетащите камеру для изменения позиции",
                                       padding="15", style="Card.TFrame")
        preview_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Canvas для предпросмотра
        self.preview_canvas = tk.Canvas(preview_frame, bg=self.card_color, highlightthickness=0, bd=0)
        self.preview_canvas.pack(expand=True, fill=tk.BOTH)

        # Привязка событий перетаскивания для всего canvas
        self.preview_canvas.bind("<Button-1>", self.start_drag)
        self.preview_canvas.bind("<B1-Motion>", self.drag_camera)
        self.preview_canvas.bind("<ButtonRelease-1>", self.stop_drag)

        # Статус бар
        status_frame = ttk.Frame(main_frame, style="TFrame")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))

        self.status_var = tk.StringVar(value="Готов к записи")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style="TLabel")
        status_label.pack(side=tk.LEFT)

        self.time_var = tk.StringVar(value="00:00:00")
        time_label = ttk.Label(status_frame, textvariable=self.time_var, style="TLabel")
        time_label.pack(side=tk.RIGHT)

        # Индикатор записи
        self.recording_indicator = tk.Canvas(status_frame, width=16, height=16, bg=self.bg_color, highlightthickness=0)
        self.recording_indicator.pack(side=tk.LEFT, padx=(10, 0))
        self.recording_circle = self.recording_indicator.create_oval(3, 3, 13, 13, fill="#666666", outline="")

        # Настройка весов для растягивания
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        settings_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        # Вкладка настроек
        settings_tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(settings_tab, text="Дополнительные настройки")
        self.setup_settings_tab(settings_tab)

    def setup_settings_tab(self, parent):
        # Настройки предпросмотра
        preview_frame = ttk.LabelFrame(parent, text="Настройки предпросмотра", padding="15", style="Card.TFrame")
        preview_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(preview_frame, text="FPS предпросмотра:").grid(row=0, column=0, sticky=tk.W)
        self.preview_fps_var = tk.StringVar(value="30")
        preview_fps_combo = ttk.Combobox(preview_frame, textvariable=self.preview_fps_var,
                                         values=["60", "30", "25", "20", "15", "10"], width=15)
        preview_fps_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(preview_frame, text="Качество предпросмотра:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.preview_quality_var = tk.StringVar(value="Высокое")
        preview_quality_combo = ttk.Combobox(preview_frame, textvariable=self.preview_quality_var,
                                             values=["Высокое", "Среднее", "Низкое"], width=15)
        preview_quality_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))

        # Настройки сохранения
        save_frame = ttk.LabelFrame(parent, text="Настройки сохранения", padding="15", style="Card.TFrame")
        save_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(save_frame, text="Папка для сохранения:").grid(row=0, column=0, sticky=tk.W)
        self.save_dir_var = tk.StringVar(value=os.path.expanduser("~/Videos"))
        ttk.Entry(save_frame, textvariable=self.save_dir_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Button(save_frame, text="Обзор", command=self.browse_save_dir, style="TButton").grid(row=0, column=2,
                                                                                                 padx=(10, 0))

        ttk.Label(save_frame, text="Формат файла:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.file_format_var = tk.StringVar(value="mp4")
        file_format_combo = ttk.Combobox(save_frame, textvariable=self.file_format_var,
                                         values=["mp4", "avi", "mov", "mkv"], width=15)
        file_format_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))

    def browse_save_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir_var.set(directory)

    def open_preview_settings(self):
        self.notebook.select(1)  # Переключаем на вкладку настроек

    def start_preview(self):
        """Запуск предпросмотра"""
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
        """Обновление масштаба камеры"""
        self.camera_scale = float(value)
        self.scale_value_label.config(text=f"{value}x")

    def toggle_camera_only(self):
        """Переключение режима 'только камера'"""
        if self.screen_capture_enabled:
            # Включаем режим только камеры
            self.screen_capture_enabled = False
            self.camera_enabled = True
            self.screen_var.set(False)
            self.camera_var.set(True)
            self.camera_only_button.config(bg=self.accent_color, text="📷 Только камера (вкл)")
        else:
            # Возвращаем обычный режим
            self.screen_capture_enabled = True
            self.camera_enabled = True
            self.screen_var.set(True)
            self.camera_var.set(True)
            self.camera_only_button.config(bg="#404040", text="📷 Только камера")

    def start_drag(self, event):
        """Начало перетаскивания камеры"""
        # Проверяем, что клик был в области камеры
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
        """Перетаскивание камеры"""
        if self.dragging_camera and self.camera_enabled:
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            base_width, base_height = 160, 120
            scaled_width = int(base_width * self.camera_scale)
            scaled_height = int(base_height * self.camera_scale)

            # Вычисляем новую позицию
            new_x = self.camera_start_x + (event.x - self.drag_start_x)
            new_y = self.camera_start_y + (event.y - self.drag_start_y)

            # Ограничиваем позицию, чтобы камера не выходила за границы
            new_x = max(0, min(new_x, canvas_width - scaled_width))
            new_y = max(0, min(new_y, canvas_height - scaled_height))

            self.camera_position = [new_x, new_y]

    def stop_drag(self, event):
        """Завершение перетаскивания камеры"""
        self.dragging_camera = False

    def update_preview_gui(self, frame):
        """Обновление GUI предпросмотра"""
        if not self.preview_update_active:
            return

        try:
            # Преобразование кадра для отображения
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            # Получаем размеры canvas
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()

            if canvas_width > 1 and canvas_height > 1:
                # Масштабируем изображение под размер canvas
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

                # Обновляем изображение на canvas
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
            # Получение параметров записи
            if self.custom_resolution_enabled:
                width = int(self.custom_width_var.get())
                height = int(self.custom_height_var.get())
                resolution = (width, height)
            else:
                res_str = self.resolution_var.get()
                width, height = map(int, res_str.split('x'))
                resolution = (width, height)

            fps = int(self.fps_var.get())
            bitrate = int(self.bitrate_var.get()) * 1000000

            # Создание объектов записи
            self.video_recorder = VideoRecorder(self, resolution, fps, bitrate)
            if self.audio_enabled:
                self.audio_recorder = AudioRecorder()

            # Запуск записи
            self.video_recorder.start()
            if self.audio_enabled:
                self.audio_recorder.start()

            self.recording = True
            self.start_time = time.time()
            self.total_pause_time = 0
            self.update_timer()

            # Обновление UI
            self.record_button.config(text="⏸️ Пауза", bg="#ffa500")
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.recording_indicator.itemconfig(self.recording_circle, fill="#ff4d4d")
            self.status_var.set("Идёт запись...")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось начать запись: {str(e)}")

    def pause_recording(self):
        self.paused = True
        self.pause_time = time.time()
        self.record_button.config(text="▶️ Продолжить", bg="#28a745")
        self.status_var.set("Запись на паузе")

    def resume_recording(self):
        self.paused = False
        self.total_pause_time += time.time() - self.pause_time
        self.record_button.config(text="⏸️ Пауза", bg="#ffa500")
        self.status_var.set("Идёт запись...")

    def toggle_pause(self):
        """Переключение паузы записи"""
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
        if self.audio_recorder:
            self.audio_recorder.stop()

        # Обновление UI
        self.record_button.config(text="● Начать запись", bg=self.accent_color)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.recording_indicator.itemconfig(self.recording_circle, fill="#666666")
        self.status_var.set("Запись завершена")
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
            filetypes=[
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("MOV files", "*.mov"),
                ("MKV files", "*.mkv"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                # Простое копирование файла (в реальном приложении нужно было бы кодировать)
                import shutil
                shutil.copy2('temp_video.avi', file_path)
                messagebox.showinfo("Успех", f"Видео сохранено как {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить видео: {str(e)}")

    def on_closing(self):
        if self.recording:
            self.stop_recording()
        self.preview_update_active = False
        if hasattr(self, 'preview_updater'):
            self.preview_updater.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TarantinoCatch(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()