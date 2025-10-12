import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime
import threading
import time
import cv2
import queue

class ConverterGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.accent_hover = "#4f46e5"
        self.text_color = "#ffffff"
        self.secondary_text = "#cbd5e1"
        self.border_color = "#334155"
        self.success_color = "#10b981"
        self.error_color = "#ef4444"

        self.title_font = ('Segoe UI', 24, 'bold')
        self.subtitle_font = ('Segoe UI', 16, 'bold')
        self.app_font = ('Segoe UI', 12)
        self.button_font = ('Segoe UI', 11, 'bold')
        self.mono_font = ('Consolas', 10)

        self.batch_var = tk.BooleanVar(value=False)
        self.resize_var = tk.BooleanVar(value=False)
        self.aspect_var = tk.BooleanVar(value=True)
        self.download_queue = queue.Queue()
        self.queue_running = False
        self.queue_thread = None

        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.bg_color)

        self.setup_ui()
        self.setup_styles()
        self.start_queue_processing()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure(".", background=self.bg_color, foreground=self.text_color, font=self.app_font)
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_color, relief='flat', borderwidth=0)
        style.configure("TLabel", background=self.card_color, foreground=self.text_color, font=self.app_font)
        style.configure("Title.TLabel", font=self.title_font, foreground=self.text_color)
        style.configure("Subtitle.TLabel", foreground=self.secondary_text, font=self.subtitle_font)
        style.configure("TButton", background=self.card_color, foreground=self.text_color,
                        font=self.button_font, borderwidth=0, focuscolor='none')
        style.map("TButton", background=[('active', self.accent_hover)], foreground=[('active', '#ffffff')])
        style.configure("Accent.TButton", background=self.accent_color, foreground="#ffffff",
                        font=self.button_font, borderwidth=0)
        style.map("Accent.TButton", background=[('active', self.accent_hover)], foreground=[('active', '#ffffff')])
        style.configure("TEntry", fieldbackground="#2d3748", foreground=self.text_color, borderwidth=1,
                        insertcolor=self.accent_color, padding=8, bordercolor=self.border_color)
        style.configure("TCombobox", fieldbackground="#2d3748", foreground=self.text_color,
                        selectbackground=self.accent_color, selectforeground="#ffffff",
                        borderwidth=1, bordercolor=self.border_color)
        style.configure("Horizontal.TProgressbar", background=self.accent_color, troughcolor=self.card_color,
                        thickness=8, borderwidth=0)
        style.configure("TCheckbutton", background=self.card_color, foreground=self.text_color,
                        indicatorcolor=self.accent_color)
        style.map("TCheckbutton", background=[('active', self.card_color)],
                  indicatorcolor=[('selected', self.accent_color)])
        style.configure("Horizontal.TScale", background=self.card_color, troughcolor="#2d3748",
                        sliderlength=20, borderwidth=0)

    def setup_ui(self):
        self.root.title("Gagarin Bridge")

        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        header_frame = ttk.Frame(main_container, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 20))

        logo_frame = ttk.Frame(header_frame, style="TFrame")
        logo_frame.pack(side="left")

        logo_canvas = tk.Canvas(logo_frame, bg=self.bg_color, width=60, height=60,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")

        logo_canvas.create_oval(5, 5, 55, 55, fill=self.accent_color, outline="")
        logo_canvas.create_text(30, 30, text="GB", font=('Segoe UI', 16, 'bold'),
                                fill="#ffffff")

        title_label = tk.Label(logo_frame, text="GAGARIN BRIDGE",
                               font=self.title_font, bg=self.bg_color, fg=self.text_color)
        title_label.pack(side="left", padx=15)

        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(fill="both", expand=True)

        left_panel = ttk.Frame(content_frame, style="TFrame")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))

        right_panel = ttk.Frame(content_frame, style="TFrame")
        right_panel.pack(side="right", fill="both", expand=True)

        settings_card = ttk.Frame(left_panel, style="Card.TFrame", padding=20)
        settings_card.pack(fill="x", pady=(0, 15))

        settings_title = tk.Label(settings_card, text="Настройки конвертации",
                                  font=self.subtitle_font, bg=self.card_color, fg=self.text_color)
        settings_title.pack(anchor="w", pady=(0, 15))

        self.setup_file_selection(settings_card)
        self.setup_format_selection(settings_card)
        self.setup_image_options(settings_card)
        self.setup_output_selection(settings_card)
        self.setup_action_buttons(settings_card)

        queue_card = ttk.Frame(left_panel, style="Card.TFrame", padding=20)
        queue_card.pack(fill="both", expand=True, pady=(15, 0))

        queue_title = tk.Label(queue_card, text="Очередь конвертаций",
                               font=self.subtitle_font, bg=self.card_color, fg=self.text_color)
        queue_title.pack(anchor="w", pady=(0, 10))

        self.queue_text = tk.Text(queue_card, height=15, bg="#2d3748", fg=self.text_color,
                                  font=self.mono_font, wrap=tk.WORD, relief='flat',
                                  borderwidth=1, padx=10, pady=10)
        self.queue_text.pack(fill="both", expand=True, pady=(0, 10))
        self.queue_text.config(state=tk.DISABLED)

        clear_queue_btn = ttk.Button(queue_card, text="Очистить очередь", style="TButton",
                                     command=self.clear_queue)
        clear_queue_btn.pack(anchor="w")

        preview_card = ttk.Frame(right_panel, style="Card.TFrame", padding=20)
        preview_card.pack(fill="both", expand=True)

        self.setup_preview_area(preview_card)
        self.setup_info_area(preview_card)

    def setup_file_selection(self, parent):
        file_frame = ttk.Frame(parent, style="Card.TFrame")
        file_frame.pack(fill="x", pady=(0, 15))

        file_label = tk.Label(file_frame, text="Исходный файл",
                              font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        file_label.pack(anchor="w", pady=(0, 10))

        input_frame = ttk.Frame(file_frame, style="Card.TFrame")
        input_frame.pack(fill="x", pady=5)

        self.input_entry = ttk.Entry(input_frame, style="TEntry")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind('<FocusOut>', self.on_input_changed)

        btn_frame = ttk.Frame(input_frame, style="Card.TFrame")
        btn_frame.pack(side="right")

        file_btn = ttk.Button(btn_frame, text="Файл", style="TButton",
                              command=self.browse_input)
        file_btn.pack(side="left", padx=3)

        folder_btn = ttk.Button(btn_frame, text="Папка", style="TButton",
                                command=self.toggle_batch_mode)
        folder_btn.pack(side="left", padx=3)

    def setup_format_selection(self, parent):
        format_frame = ttk.Frame(parent, style="Card.TFrame")
        format_frame.pack(fill="x", pady=15)

        format_label = tk.Label(format_frame, text="Формат вывода",
                                font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        format_label.pack(anchor="w", pady=(0, 10))

        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                         style="TCombobox", state="readonly")
        self.format_combo.pack(fill="x", pady=5)
        self.format_combo.bind('<<ComboboxSelected>>', self.update_output_suggestion)

    def setup_image_options(self, parent):
        image_frame = ttk.Frame(parent, style="Card.TFrame")
        image_frame.pack(fill="x", pady=15)

        image_label = tk.Label(image_frame, text="Настройки изображения",
                               font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        image_label.pack(anchor="w", pady=(0, 10))

        resize_frame = ttk.Frame(image_frame, style="Card.TFrame")
        resize_frame.pack(fill="x", pady=5)

        resize_cb = ttk.Checkbutton(resize_frame, text="Изменить размер",
                                    variable=self.resize_var, command=self.toggle_resize_options)
        resize_cb.pack(side="left")

        self.size_frame = ttk.Frame(image_frame, style="Card.TFrame")

        width_frame = ttk.Frame(self.size_frame, style="Card.TFrame")
        width_frame.pack(side="left", padx=(0, 10))

        tk.Label(width_frame, text="Ширина:", bg=self.card_color, fg=self.text_color).pack(side="left", padx=(0, 5))
        self.width_var = tk.StringVar()
        width_entry = ttk.Entry(width_frame, textvariable=self.width_var, width=8, style="TEntry")
        width_entry.pack(side="left")

        height_frame = ttk.Frame(self.size_frame, style="Card.TFrame")
        height_frame.pack(side="left", padx=(0, 10))

        tk.Label(height_frame, text="Высота:", bg=self.card_color, fg=self.text_color).pack(side="left", padx=(0, 5))
        self.height_var = tk.StringVar()
        height_entry = ttk.Entry(height_frame, textvariable=self.height_var, width=8, style="TEntry")
        height_entry.pack(side="left")

        aspect_cb = ttk.Checkbutton(self.size_frame, text="Сохранять пропорции",
                                    variable=self.aspect_var)
        aspect_cb.pack(side="left")

        self.size_frame.pack_forget()

    def setup_output_selection(self, parent):
        output_frame = ttk.Frame(parent, style="Card.TFrame")
        output_frame.pack(fill="x", pady=15)

        output_label = tk.Label(output_frame, text="Сохранить в",
                                font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        output_label.pack(anchor="w", pady=(0, 10))

        output_input_frame = ttk.Frame(output_frame, style="Card.TFrame")
        output_input_frame.pack(fill="x", pady=5)

        self.output_entry = ttk.Entry(output_input_frame, style="TEntry")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = ttk.Button(output_input_frame, text="Обзор", style="TButton",
                                command=self.browse_output)
        browse_btn.pack(side="right")

    def setup_action_buttons(self, parent):
        action_frame = ttk.Frame(parent, style="Card.TFrame")
        action_frame.pack(fill="x", pady=(15, 0))

        self.progress = ttk.Progressbar(action_frame, orient=tk.HORIZONTAL,
                                        mode='determinate', style="Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 10))

        self.status_label = tk.Label(action_frame, text="Готов к работе",
                                     font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        self.status_label.pack(anchor="w", pady=(0, 10))

        button_frame = ttk.Frame(action_frame, style="Card.TFrame")
        button_frame.pack(fill="x")

        convert_btn = ttk.Button(button_frame, text="Добавить в очередь", style="Accent.TButton",
                                 command=self.queue_conversion)
        convert_btn.pack(side="left", expand=True, padx=5)

        clear_btn = ttk.Button(button_frame, text="Очистить", style="TButton",
                               command=self.clear_fields)
        clear_btn.pack(side="left", expand=True, padx=5)

    def setup_preview_area(self, parent):
        preview_title = tk.Label(parent, text="Предпросмотр",
                                 font=self.subtitle_font, bg=self.card_color, fg=self.text_color)
        preview_title.pack(anchor="w", pady=(0, 15))

        self.preview_container = ttk.Frame(parent, style="Card.TFrame")
        self.preview_container.pack(fill="both", expand=True)

        self.preview_canvas = tk.Canvas(self.preview_container, bg=self.card_color,
                                        highlightthickness=0, relief='flat', width=800, height=600)
        self.preview_canvas.pack(fill="both", expand=True)

        self.preview_canvas.create_text(400, 300, text="Выберите файл для предпросмотра",
                                        fill=self.secondary_text, font=self.subtitle_font)

    def setup_info_area(self, parent):
        info_card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        info_card.pack(fill="x", pady=(15, 0))

        info_title = tk.Label(info_card, text="Информация о файле",
                              font=self.subtitle_font, bg=self.card_color, fg=self.text_color)
        info_title.pack(anchor="w", pady=(0, 10))

        self.info_text = tk.Text(info_card, height=8, bg="#2d3748", fg=self.text_color,
                                 font=self.mono_font, wrap=tk.WORD, relief='flat',
                                 borderwidth=1, padx=10, pady=10)
        self.info_text.pack(fill="both", expand=True)
        self.info_text.config(state=tk.DISABLED)
        self.info_text.insert(1.0, "Файл не выбран")

    def update_queue_display(self):
        try:
            queue_items = []
            temp_queue = queue.Queue()
            while not self.download_queue.empty():
                try:
                    item = self.download_queue.get_nowait()
                    queue_items.append(item)
                    temp_queue.put(item)
                except queue.Empty:
                    break
            self.download_queue.queue.clear()
            while not temp_queue.empty():
                self.download_queue.put(temp_queue.get_nowait())

            text = "Текущая очередь:\n"
            for i, item in enumerate(queue_items, 1):
                status = item.get('status', 'Ожидание')
                file_name = os.path.basename(item['input_path'])
                text += f"{i}. {file_name} ({status})\n"

            self.queue_text.config(state=tk.NORMAL)
            self.queue_text.delete(1.0, tk.END)
            self.queue_text.insert(1.0, text if queue_items else "Очередь пуста")
            self.queue_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error updating queue display: {e}")

    def toggle_resize_options(self):
        if self.resize_var.get():
            self.size_frame.pack(fill="x", pady=5)
        else:
            self.size_frame.pack_forget()

    def on_input_changed(self, event=None):
        input_path = self.input_entry.get().strip()
        if input_path and os.path.exists(input_path):
            ext = os.path.splitext(input_path)[1].lower().lstrip('.')
            try:
                output_formats = self.controller.get_output_formats_for_input(ext)
                self.format_combo['values'] = output_formats
                if output_formats:
                    self.format_combo.set(output_formats[0])
                    self.update_output_suggestion()
                self.update_file_info()
                self.update_preview()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить форматы: {str(e)}")

    def update_file_info(self):
        input_path = self.input_entry.get().strip()
        if not input_path or not os.path.exists(input_path):
            return

        if os.path.isdir(input_path):
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, "Папка выбрана")
            self.info_text.config(state=tk.DISABLED)
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
        input_path = self.input_entry.get().strip()
        if not input_path or not os.path.exists(input_path):
            return

        if os.path.isdir(input_path):
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(400, 300, text="Папка выбрана\nПредпросмотр недоступен",
                                            fill=self.secondary_text, font=self.subtitle_font, justify=tk.CENTER)
            return

        ext = os.path.splitext(input_path)[1].lower().lstrip('.')

        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(400, 300, text="Загрузка предпросмотра...",
                                        fill=self.secondary_text, font=self.app_font)

        thread = threading.Thread(target=self._load_preview, args=(input_path, ext))
        thread.daemon = True
        thread.start()

    def _load_preview(self, input_path, ext):
        try:
            image_formats = self.controller.supported_formats['images']
            video_formats = self.controller.supported_formats['video']
            document_formats = self.controller.supported_formats['documents']

            if ext in image_formats:
                img = Image.open(input_path)
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            elif ext in video_formats:
                frame = self.controller.get_video_preview(input_path, frame_time=0.0)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            elif ext in document_formats:
                img = self.controller.get_document_preview_image(input_path)
                if img:
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                else:
                    img = None
            else:
                img = None

            self.root.after(0, self._update_preview_canvas, img)
        except Exception as e:
            self.root.after(0, self._update_preview_canvas, None, str(e))

    def _update_preview_canvas(self, img, error=None):
        self.preview_canvas.delete("all")
        if error:
            self.preview_canvas.create_text(400, 300, text=f"Ошибка предпросмотра:\n{error}",
                                            fill=self.error_color, font=self.app_font, justify=tk.CENTER)
        elif img:
            photo = ImageTk.PhotoImage(img)
            self.preview_canvas.create_image(400, 300, image=photo)
            self.preview_canvas.image = photo
        else:
            self.preview_canvas.create_text(400, 300, text="Предпросмотр недоступен\nдля этого типа файла",
                                            fill=self.secondary_text, font=self.subtitle_font, justify=tk.CENTER)

    def format_file_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def update_output_suggestion(self, event=None):
        input_path = self.input_entry.get().strip()
        output_format = self.format_var.get().lower()
        if input_path and output_format:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_dir = os.path.dirname(input_path) if os.path.dirname(input_path) else "."
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
        if self.batch_var.get():
            self.format_combo.config(state="normal")
        else:
            self.format_combo.config(state="readonly")

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

    def start_queue_processing(self):
        self.queue_running = True
        self.queue_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.queue_thread.start()

    def _process_queue(self):
        while self.queue_running:
            try:
                task = self.download_queue.get(timeout=1.0)
                if task:
                    task['status'] = 'В процессе'
                    self.root.after(0, self.update_queue_display)
                    self.convert_task(task)
                    task['status'] = 'Завершено' if task.get('success', False) else 'Ошибка'
                    self.root.after(0, self.update_queue_display)
                self.download_queue.task_done()
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                print(f"Ошибка обработки очереди: {e}")
                if 'task' in locals():
                    task['status'] = 'Ошибка'
                    self.root.after(0, self.update_queue_display)
                self.download_queue.task_done()

    def queue_conversion(self):
        try:
            input_path = self.input_entry.get().strip()
            output_path = self.output_entry.get().strip()
            output_format = self.format_var.get().lower().strip()

            if not input_path or not os.path.exists(input_path):
                messagebox.showerror("Ошибка", "Исходный файл/папка не существует")
                return

            options = {
                'resize_enabled': self.resize_var.get(),
                'width': int(self.width_var.get()) if self.width_var.get().isdigit() else None,
                'height': int(self.height_var.get()) if self.height_var.get().isdigit() else None,
                'keep_aspect': self.aspect_var.get(),
                'quality': 95
            }

            task = {
                'input_path': input_path,
                'output_path': output_path,
                'output_format': output_format,
                'options': options,
                'batch': self.batch_var.get(),
                'status': 'Ожидание',
                'success': False
            }

            self.download_queue.put(task)
            self.root.after(0, self.update_queue_display)
            messagebox.showinfo("Успех", "Задача добавлена в очередь")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении задачи: {str(e)}")

    def convert_task(self, task):
        try:
            self.root.after(0, lambda: self.status_label.config(
                text=f"Конвертация: {os.path.basename(task['input_path'])}",
                fg=self.accent_color))
            self.root.after(0, lambda: setattr(self.progress, 'value', 0))

            if not task['output_format']:
                result = self.controller.auto_convert_file(
                    task['input_path'],
                    os.path.dirname(task['output_path']) if task['output_path'] else None,
                    options=task['options'],
                    progress_callback=self.update_progress
                )
                task['success'] = bool(result)
            else:
                if task['batch']:
                    task['success'] = self.controller.convert_batch(
                        task['input_path'], task['output_path'], task['output_format'],
                        task['options'], self.update_progress
                    )
                else:
                    task['success'] = self.controller.convert_file(
                        task['input_path'], task['output_path'], task['output_format'],
                        task['options'], self.update_progress
                    )

            self.root.after(0, lambda: self.status_label.config(
                text="Готово" if task['success'] else "Ошибка",
                fg=self.success_color if task['success'] else self.error_color))

        except Exception as e:
            task['success'] = False
            print(f"Conversion error: {e}")
            self.root.after(0, lambda: self.status_label.config(text="Ошибка", fg=self.error_color))

    def clear_queue(self):
        try:
            self.queue_running = False
            with self.download_queue.mutex:
                self.download_queue.queue.clear()
            self.queue_running = True
            self.root.after(0, self.update_queue_display)
            messagebox.showinfo("Успех", "Очередь очищена")
        except Exception as e:
            print(f"Error clearing queue: {e}")

    def update_progress(self, value):
        try:
            self.root.after(0, lambda: setattr(self.progress, 'value', value))
        except:
            pass

    def clear_fields(self):
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

        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(400, 300, text="Выберите файл для предпросмотра",
                                        fill=self.secondary_text, font=self.subtitle_font)
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Файл не выбран")
        self.info_text.config(state=tk.DISABLED)

    def run(self):
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            print(f"Application error: {e}")

    def on_closing(self):
        self.queue_running = False
        self.root.destroy()