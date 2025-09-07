# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime
import threading
import time
import cv2


class ConverterGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        # Современная цветовая палитра
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.accent_hover = "#4f46e5"
        self.text_color = "#ffffff"  # Белый текст
        self.secondary_text = "#cbd5e1"
        self.border_color = "#334155"
        self.success_color = "#10b981"
        self.error_color = "#ef4444"

        # Шрифты
        self.title_font = ('Segoe UI', 24, 'bold')
        self.subtitle_font = ('Segoe UI', 16, 'bold')
        self.app_font = ('Segoe UI', 12)
        self.button_font = ('Segoe UI', 11, 'bold')
        self.mono_font = ('Consolas', 10)

        # Переменные
        self.batch_var = tk.BooleanVar(value=False)
        self.resize_var = tk.BooleanVar(value=False)
        self.aspect_var = tk.BooleanVar(value=True)
        self.video_playing = False
        self.video_thread = None

        # Полноэкранный режим
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.bg_color)

        self.setup_ui()
        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Базовые стили
        style.configure(".",
                        background=self.bg_color,
                        foreground=self.text_color,
                        font=self.app_font)

        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame",
                        background=self.card_color,
                        relief='flat',
                        borderwidth=0)

        style.configure("TLabel",
                        background=self.card_color,
                        foreground=self.text_color,
                        font=self.app_font)

        style.configure("Title.TLabel",
                        font=self.title_font,
                        foreground=self.text_color)

        style.configure("Subtitle.TLabel",
                        foreground=self.secondary_text,
                        font=self.subtitle_font)

        # Кнопки
        style.configure("TButton",
                        background=self.card_color,
                        foreground=self.text_color,
                        font=self.button_font,
                        borderwidth=0,
                        focuscolor='none')

        style.map("TButton",
                  background=[('active', self.accent_hover)],
                  foreground=[('active', '#ffffff')])

        style.configure("Accent.TButton",
                        background=self.accent_color,
                        foreground="#ffffff",
                        font=self.button_font,
                        borderwidth=0)

        style.map("Accent.TButton",
                  background=[('active', self.accent_hover)],
                  foreground=[('active', '#ffffff')])

        # Поля ввода
        style.configure("TEntry",
                        fieldbackground="#2d3748",
                        foreground=self.text_color,
                        borderwidth=1,
                        insertcolor=self.accent_color,
                        padding=8,
                        bordercolor=self.border_color)

        style.configure("TCombobox",
                        fieldbackground="#2d3748",
                        foreground=self.text_color,
                        selectbackground=self.accent_color,
                        selectforeground="#ffffff",
                        borderwidth=1,
                        bordercolor=self.border_color)

        # Прогресс-бар
        style.configure("Horizontal.TProgressbar",
                        background=self.accent_color,
                        troughcolor=self.card_color,
                        thickness=8,
                        borderwidth=0)

        # Чекбоксы
        style.configure("TCheckbutton",
                        background=self.card_color,
                        foreground=self.text_color,
                        indicatorcolor=self.accent_color)

        style.map("TCheckbutton",
                  background=[('active', self.card_color)],
                  indicatorcolor=[('selected', self.accent_color)])

    def setup_ui(self):
        self.root.title("Gagarin Bridge")

        # Главный контейнер
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Хедер
        header_frame = ttk.Frame(main_container, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 30))

        # Логотип
        logo_frame = ttk.Frame(header_frame, style="TFrame")
        logo_frame.pack(side="left")

        # Создаем современный логотип
        logo_canvas = tk.Canvas(logo_frame, bg=self.bg_color, width=60, height=60,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")

        # Градиентный круг для логотипа
        logo_canvas.create_oval(5, 5, 55, 55, fill=self.accent_color, outline="")
        logo_canvas.create_text(30, 30, text="GB", font=('Segoe UI', 16, 'bold'),
                                fill="#ffffff")

        # Заголовок
        title_label = tk.Label(logo_frame, text="GAGARIN BRIDGE",
                               font=self.title_font, bg=self.bg_color, fg=self.text_color)
        title_label.pack(side="left", padx=15)

        # Основное содержимое
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(fill="both", expand=True)

        # Левая панель (настройки)
        left_panel = ttk.Frame(content_frame, style="TFrame")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 20))

        # Правая панель (превью)
        right_panel = ttk.Frame(content_frame, style="TFrame")
        right_panel.pack(side="right", fill="both", expand=True)

        # Карточка настроек
        settings_card = ttk.Frame(left_panel, style="Card.TFrame", padding=30)
        settings_card.pack(fill="both", expand=True)

        # Заголовок настроек
        settings_title = tk.Label(settings_card, text="Настройки конвертации",
                                  font=self.subtitle_font, bg=self.card_color, fg=self.text_color)
        settings_title.pack(anchor="w", pady=(0, 25))

        # Элементы интерфейса
        self.setup_file_selection(settings_card)
        self.setup_format_selection(settings_card)
        self.setup_image_options(settings_card)
        self.setup_output_selection(settings_card)
        self.setup_action_buttons(settings_card)

        # Карточка превью
        preview_card = ttk.Frame(right_panel, style="Card.TFrame", padding=30)
        preview_card.pack(fill="both", expand=True)

        self.setup_preview_area(preview_card)

    def setup_file_selection(self, parent):
        file_frame = ttk.Frame(parent, style="Card.TFrame")
        file_frame.pack(fill="x", pady=(0, 20))

        # Заголовок
        file_label = tk.Label(file_frame, text="Исходный файл",
                              font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        file_label.pack(anchor="w", pady=(0, 12))

        # Фрейм для ввода и кнопок
        input_frame = ttk.Frame(file_frame, style="Card.TFrame")
        input_frame.pack(fill="x", pady=8)

        # Поле ввода
        self.input_entry = ttk.Entry(input_frame, style="TEntry")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind('<FocusOut>', self.on_input_changed)

        # Фрейм для кнопок
        btn_frame = ttk.Frame(input_frame, style="Card.TFrame")
        btn_frame.pack(side="right")

        # Кнопки
        file_btn = ttk.Button(btn_frame, text="Файл", style="TButton",
                              command=self.browse_input)
        file_btn.pack(side="left", padx=3)

        folder_btn = ttk.Button(btn_frame, text="Папка", style="TButton",
                                command=self.toggle_batch_mode)
        folder_btn.pack(side="left", padx=3)

    def setup_format_selection(self, parent):
        format_frame = ttk.Frame(parent, style="Card.TFrame")
        format_frame.pack(fill="x", pady=20)

        format_label = tk.Label(format_frame, text="Формат вывода",
                                font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        format_label.pack(anchor="w", pady=(0, 12))

        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                         style="TCombobox", state="readonly")
        self.format_combo.pack(fill="x", pady=8)
        self.format_combo.bind('<<ComboboxSelected>>', self.update_output_suggestion)

    def setup_image_options(self, parent):
        image_frame = ttk.Frame(parent, style="Card.TFrame")
        image_frame.pack(fill="x", pady=20)

        image_label = tk.Label(image_frame, text="Настройки изображения",
                               font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        image_label.pack(anchor="w", pady=(0, 12))

        # Чекбокс изменения размера
        resize_frame = ttk.Frame(image_frame, style="Card.TFrame")
        resize_frame.pack(fill="x", pady=8)

        resize_cb = ttk.Checkbutton(resize_frame, text="Изменить размер",
                                    variable=self.resize_var, command=self.toggle_resize_options)
        resize_cb.pack(side="left")

        # Фрейм для настроек размера
        self.size_frame = ttk.Frame(image_frame, style="Card.TFrame")

        # Ширина
        width_frame = ttk.Frame(self.size_frame, style="Card.TFrame")
        width_frame.pack(side="left", padx=(0, 15))

        tk.Label(width_frame, text="Ширина:", bg=self.card_color, fg=self.text_color).pack(side="left", padx=(0, 5))
        self.width_var = tk.StringVar()
        width_entry = ttk.Entry(width_frame, textvariable=self.width_var, width=8, style="TEntry")
        width_entry.pack(side="left")

        # Высота
        height_frame = ttk.Frame(self.size_frame, style="Card.TFrame")
        height_frame.pack(side="left", padx=(0, 15))

        tk.Label(height_frame, text="Высота:", bg=self.card_color, fg=self.text_color).pack(side="left", padx=(0, 5))
        self.height_var = tk.StringVar()
        height_entry = ttk.Entry(height_frame, textvariable=self.height_var, width=8, style="TEntry")
        height_entry.pack(side="left")

        # Сохранение пропорций
        aspect_cb = ttk.Checkbutton(self.size_frame, text="Сохранять пропорции",
                                    variable=self.aspect_var)
        aspect_cb.pack(side="left")

        self.size_frame.pack_forget()

    def setup_output_selection(self, parent):
        output_frame = ttk.Frame(parent, style="Card.TFrame")
        output_frame.pack(fill="x", pady=20)

        output_label = tk.Label(output_frame, text="Сохранить в",
                                font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        output_label.pack(anchor="w", pady=(0, 12))

        output_input_frame = ttk.Frame(output_frame, style="Card.TFrame")
        output_input_frame.pack(fill="x", pady=8)

        self.output_entry = ttk.Entry(output_input_frame, style="TEntry")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = ttk.Button(output_input_frame, text="Обзор", style="TButton",
                                command=self.browse_output)
        browse_btn.pack(side="right")

    def setup_action_buttons(self, parent):
        action_frame = ttk.Frame(parent, style="Card.TFrame")
        action_frame.pack(fill="x", pady=(20, 0))

        # Прогресс-бар
        self.progress = ttk.Progressbar(action_frame, orient=tk.HORIZONTAL,
                                        mode='determinate', style="Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 12))

        # Статус
        self.status_label = tk.Label(action_frame, text="Готов к работе",
                                     font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        self.status_label.pack(fill="x", pady=(0, 15))

        # Кнопки действий
        button_frame = ttk.Frame(action_frame, style="Card.TFrame")
        button_frame.pack(fill="x")

        convert_btn = ttk.Button(button_frame, text="Конвертировать", style="Accent.TButton",
                                 command=self.convert)
        convert_btn.pack(side="left", expand=True, padx=5)

        clear_btn = ttk.Button(button_frame, text="Очистить", style="TButton",
                               command=self.clear_fields)
        clear_btn.pack(side="left", expand=True, padx=5)

    def setup_preview_area(self, parent):
        preview_title = tk.Label(parent, text="Предпросмотр",
                                 font=self.subtitle_font, bg=self.card_color, fg=self.text_color)
        preview_title.pack(anchor="w", pady=(0, 20))

        # Контейнер для превью
        preview_container = ttk.Frame(parent, style="Card.TFrame")
        preview_container.pack(fill="both", expand=True, pady=(0, 20))

        # Canvas для превью
        self.preview_canvas = tk.Canvas(preview_container, bg=self.card_color,
                                        highlightthickness=0, relief='flat')
        self.preview_canvas.pack(fill="both", expand=True)

        # Начальный текст
        self.preview_canvas.create_text(200, 100, text="Выберите файл для предпросмотра",
                                        fill=self.secondary_text, font=self.subtitle_font)

        # Кнопки управления видео
        self.video_controls_frame = ttk.Frame(preview_container, style="Card.TFrame")
        self.video_controls_frame.pack(fill="x", pady=(10, 0))
        self.video_controls_frame.pack_forget()

        self.play_btn = ttk.Button(self.video_controls_frame, text="Пауза", style="TButton",
                                   command=self.toggle_video_playback)
        self.play_btn.pack(side="left", padx=5)

        # Информация о файле
        info_frame = ttk.Frame(parent, style="Card.TFrame")
        info_frame.pack(fill="x")

        info_title = tk.Label(info_frame, text="Информация о файле",
                              font=self.subtitle_font, bg=self.card_color, fg=self.text_color)
        info_title.pack(anchor="w", pady=(0, 15))

        # Текстовое поле для информации
        self.info_text = tk.Text(info_frame, height=8, bg="#2d3748", fg=self.text_color,
                                 font=self.mono_font, wrap=tk.WORD, relief='flat',
                                 borderwidth=1, padx=10, pady=10)
        self.info_text.pack(fill="x")
        self.info_text.insert(1.0, "Файл не выбран")
        self.info_text.config(state=tk.DISABLED)

    def toggle_resize_options(self):
        if self.resize_var.get():
            self.size_frame.pack(fill="x", pady=8)
        else:
            self.size_frame.pack_forget()

    def on_input_changed(self, event=None):
        input_path = self.input_entry.get()
        if input_path and os.path.exists(input_path):
            ext = os.path.splitext(input_path)[1].upper().lstrip('.')
            try:
                output_formats = self.controller.get_output_formats_for_input(ext)
                self.format_combo['values'] = output_formats
                if output_formats:
                    self.format_combo.current(0)
                    self.update_output_suggestion()
                self.update_file_info()
                self.update_preview()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить форматы: {str(e)}")

    def update_file_info(self):
        input_path = self.input_entry.get()
        if not input_path or not os.path.exists(input_path):
            return

        try:
            file_info = self.controller.get_file_info(input_path)
            if not file_info:
                return

            info_text = f"Имя: {file_info['name']}\n"
            info_text += f"Размер: {self.format_file_size(file_info['size'])}\n"
            info_text += f"Формат: {file_info['format']}\n"
            info_text += f"Создан: {datetime.fromtimestamp(file_info['created']).strftime('%Y-%m-%d %H:%M:%S')}\n"

            if 'width' in file_info and 'height' in file_info:
                info_text += f"Размер: {file_info['width']}x{file_info['height']} px\n"
            if 'mode' in file_info:
                info_text += f"Цветовой режим: {file_info['mode']}\n"
            if 'duration' in file_info:
                info_text += f"Длительность: {file_info['duration']:.2f} сек\n"
            if 'channels' in file_info:
                info_text += f"Каналы: {file_info['channels']}\n"
            if 'sample_rate' in file_info:
                info_text += f"Частота: {file_info['sample_rate']} Hz\n"

            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            self.info_text.config(state=tk.DISABLED)

        except Exception as e:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, f"Ошибка: {str(e)}")
            self.info_text.config(state=tk.DISABLED)

    def update_preview(self):
        input_path = self.input_entry.get()
        if not input_path or not os.path.exists(input_path):
            return

        try:
            ext = os.path.splitext(input_path)[1].lower().lstrip('.')
            image_formats = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp']
            video_formats = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm']

            self.preview_canvas.delete("all")
            self.video_controls_frame.pack_forget()

            # Останавливаем предыдущее видео
            self.stop_video_playback()

            if ext in image_formats:
                with Image.open(input_path) as img:
                    img.thumbnail((400, 300), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.preview_canvas.create_image(200, 150, image=photo)
                    self.preview_canvas.image = photo

            elif ext in video_formats:
                try:
                    # Запускаем проигрывание видео в отдельном потоке
                    self.start_video_playback(input_path)
                    self.video_controls_frame.pack(fill="x", pady=(10, 0))

                except Exception as e:
                    self.preview_canvas.create_text(200, 150,
                                                    text=f"Ошибка предпросмотра видео:\n{str(e)}",
                                                    fill=self.error_color, font=self.app_font,
                                                    justify=tk.CENTER)
            else:
                self.preview_canvas.create_text(200, 150,
                                                text="Предпросмотр недоступен\nдля этого типа файла",
                                                fill=self.secondary_text, font=self.subtitle_font,
                                                justify=tk.CENTER)

        except Exception as e:
            self.preview_canvas.create_text(200, 150, text=f"Ошибка предпросмотра:\n{str(e)}",
                                            fill=self.error_color, font=self.app_font,
                                            justify=tk.CENTER)

    def start_video_playback(self, video_path):
        """Запуск проигрывания видео в отдельном потоке"""
        self.stop_video_playback()
        self.video_playing = True
        self.video_thread = threading.Thread(target=self._video_playback_loop,
                                             args=(video_path,), daemon=True)
        self.video_thread.start()

    def stop_video_playback(self):
        """Остановка проигрывания видео"""
        self.video_playing = False
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=1.0)

    def toggle_video_playback(self):
        """Переключение паузы/воспроизведения видео"""
        self.video_playing = not self.video_playing
        if self.video_playing:
            self.play_btn.config(text="Пауза")
        else:
            self.play_btn.config(text="Воспроизвести")

    def _video_playback_loop(self, video_path):
        """Цикл проигрывания видео"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 25

        frame_time = 1.0 / fps
        current_frame = 0

        while self.video_playing and cap.isOpened():
            start_time = time.time()

            # Ждем, если видео на паузе
            while not self.video_playing:
                time.sleep(0.1)
                if not self.video_playing:
                    break

            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            try:
                # Конвертируем кадр для отображения
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.thumbnail((400, 300), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                # Обновляем canvas в основном потоке
                self.root.after(0, self._update_video_frame, photo)

            except Exception as e:
                print(f"Ошибка обновления кадра: {e}")
                break

            # Регулируем скорость проигрывания
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)

            current_frame += 1

        cap.release()

    def _update_video_frame(self, photo):
        """Обновление кадра видео в основном потоке"""
        if hasattr(self, 'preview_canvas'):
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(200, 150, image=photo)
            self.preview_canvas.image = photo

    def format_file_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def update_output_suggestion(self, event=None):
        input_path = self.input_entry.get()
        output_format = self.format_var.get().lower()
        if input_path and output_format:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_dir = os.path.dirname(input_path)
            output_path = os.path.join(output_dir, f"{base_name}_converted.{output_format}")
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_path)

    def browse_input(self):
        file_types = [
            ("Все файлы", "*.*"),
            ("Изображения", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
            ("Документы", "*.pdf *.doc *.docx *.txt *.rtf"),
            ("Данные", "*.csv *.json *.xlsx *.xls"),
            ("Аудио", "*.mp3 *.wav *.ogg *.flac *.m4a *.wma"),
            ("Видео", "*.mp4 *.avi *.mov *.wmv *.flv *.mkv *.webm")
        ]

        if self.batch_var.get():
            folder = filedialog.askdirectory(title="Выберите папку")
            if folder:
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, folder)
                self.on_input_changed()
        else:
            file_path = filedialog.askopenfilename(title="Выберите файл", filetypes=file_types)
            if file_path:
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, file_path)
                self.on_input_changed()

    def toggle_batch_mode(self):
        self.batch_var.set(not self.batch_var.get())
        self.on_input_changed()

    def browse_output(self):
        if self.batch_var.get():
            folder = filedialog.askdirectory(title="Выберите папку для сохранения")
            if folder:
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, folder)
        else:
            output_format = self.format_var.get().lower()
            if not output_format:
                messagebox.showwarning("Предупреждение", "Сначала выберите формат")
                return
            file_types = [(f"{output_format.upper()} файлы", f"*.{output_format}")]
            file_path = filedialog.asksaveasfilename(
                title="Сохранить как",
                defaultextension=f".{output_format}",
                filetypes=file_types
            )
            if file_path:
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, file_path)

    def convert(self):
        """Запуск конвертации"""
        try:
            input_path = self.input_entry.get().strip()
            output_path = self.output_entry.get().strip()
            output_format = self.format_var.get().lower().strip()

            if not input_path or not os.path.exists(input_path):
                messagebox.showerror("Ошибка", "Исходный файл/папка не существует")
                return

            # Останавливаем видео перед конвертацией
            self.stop_video_playback()

            # Опции
            options = {
                'resize_enabled': self.resize_var.get(),
                'width': int(self.width_var.get()) if self.width_var.get().isdigit() else None,
                'height': int(self.height_var.get()) if self.height_var.get().isdigit() else None,
                'keep_aspect': self.aspect_var.get(),
                'quality': 95
            }

            # Статус
            self.status_label.config(text="Конвертация...", fg=self.accent_color)
            self.progress['value'] = 0
            self.root.update()

            # Конвертация
            if not output_format:
                result = self.controller.auto_convert_file(
                    input_path, os.path.dirname(output_path) if output_path else None,
                    options=options, progress_callback=self.update_progress
                )
                success = bool(result)
            else:
                if self.batch_var.get():
                    success = self.controller.convert_batch(
                        input_path, output_path, output_format, options, self.update_progress
                    )
                else:
                    success = self.controller.convert_file(
                        input_path, output_path, output_format, options, self.update_progress
                    )

            if success:
                self.status_label.config(text="Готово", fg=self.success_color)
                messagebox.showinfo("Успех", "Конвертация завершена успешно!")
            else:
                self.status_label.config(text="Ошибка", fg=self.error_color)
                messagebox.showerror("Ошибка", "Ошибка при конвертации")

        except Exception as e:
            self.status_label.config(text="Ошибка", fg=self.error_color)
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def update_progress(self, value):
        """Обновление прогресс-бара"""
        self.progress['value'] = value
        self.root.update_idletasks()

    def clear_fields(self):
        """Очистка всех полей"""
        # Останавливаем видео
        self.stop_video_playback()

        self.input_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        self.format_combo.set('')
        self.resize_var.set(False)
        self.width_var.set('')
        self.height_var.set('')
        self.aspect_var.set(True)
        self.progress['value'] = 0
        self.status_label.config(text="Готов к работе", fg=self.secondary_text)
        self.toggle_resize_options()
        self.video_controls_frame.pack_forget()

        # Очистка предпросмотра
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(200, 100, text="Выберите файл для предпросмотра",
                                        fill=self.secondary_text, font=self.subtitle_font)
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Файл не выбран")
        self.info_text.config(state=tk.DISABLED)