# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime


class ConverterGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        # Цветовая палитра в стиле Möbius
        self.bg_color = "#0a0a0a"
        self.card_color = "#1e1e1e"
        self.accent_color = "#ff4d8d"
        self.text_color = "#f0f0f0"
        self.secondary_text = "#909090"
        self.border_color = "#2a2a2a"

        # Шрифты
        self.title_font = ('Segoe UI', 28, 'bold')
        self.subtitle_font = ('Segoe UI', 14, 'bold')
        self.app_font = ('Segoe UI', 11)
        self.button_font = ('Segoe UI', 12)
        self.mono_font = ('Segoe UI', 10)

        # Инициализация переменных
        self.batch_var = tk.BooleanVar(value=False)
        self.resize_var = tk.BooleanVar(value=False)
        self.aspect_var = tk.BooleanVar(value=True)

        # Устанавливаем полноэкранный режим и запрещаем выход
        self.root.attributes('-fullscreen', True)

        # Блокируем стандартные сочетания клавиш для выхода из полноэкранного режима
        self.root.bind('<Escape>', lambda e: "break")  # Блокируем Escape
        self.root.bind('<F11>', lambda e: "break")  # Блокируем F11
        self.root.bind('<Alt-Return>', lambda e: "break")  # Блокируем Alt+Enter

        self.setup_ui()
        self.setup_styles()

    def setup_styles(self):
        """Настройка стилей виджетов в стиле Möbius"""
        style = ttk.Style()
        style.theme_use('clam')

        # Основные стили
        style.configure(".",
                        background=self.bg_color,
                        foreground=self.text_color)

        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_color)

        # Стили текста
        style.configure("TLabel",
                        background=self.card_color,
                        foreground=self.text_color,
                        font=self.app_font)

        style.configure("Title.TLabel",
                        font=self.title_font)

        style.configure("Subtitle.TLabel",
                        foreground=self.secondary_text,
                        font=self.subtitle_font)

        # Стили кнопок
        style.configure("TButton",
                        background=self.card_color,
                        foreground=self.text_color,
                        font=self.button_font,
                        borderwidth=0,
                        focuscolor=self.bg_color)

        style.map("TButton",
                  background=[('active', '#252525')],
                  foreground=[('active', self.text_color)])

        # Акцентные кнопки
        style.configure("Accent.TButton",
                        background=self.accent_color,
                        foreground="#ffffff",
                        font=self.button_font,
                        borderwidth=0)

        style.map("Accent.TButton",
                  background=[('active', '#ff3a7c')])

        # Поля ввода
        style.configure("TEntry",
                        fieldbackground="#252525",
                        foreground=self.text_color,
                        borderwidth=1,
                        bordercolor=self.border_color,
                        insertcolor=self.accent_color,
                        padding=8)

        style.configure("TCombobox",
                        fieldbackground="#252525",
                        foreground=self.text_color,
                        selectbackground=self.accent_color,
                        selectforeground="#ffffff",
                        borderwidth=1,
                        bordercolor=self.border_color,
                        padding=8)

        # Прогресс-бар
        style.configure("Horizontal.TProgressbar",
                        background=self.accent_color,
                        troughcolor=self.card_color,
                        bordercolor=self.border_color,
                        thickness=6)

        # Чекбоксы
        style.configure("TCheckbutton",
                        background=self.card_color,
                        foreground=self.text_color,
                        indicatorcolor=self.card_color)

        style.map("TCheckbutton",
                  background=[('active', self.card_color)],
                  foreground=[('active', self.accent_color)])

    def setup_ui(self):
        """Настройка основного интерфейса"""
        self.root.title("Gagarin Bridge")
        self.root.configure(bg=self.bg_color)

        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=40, pady=30)

        # Заголовок
        header_frame = ttk.Frame(main_container, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 30))

        # Логотип и название
        logo_frame = ttk.Frame(header_frame, style="TFrame")
        logo_frame.pack(side="left")

        logo_canvas = tk.Canvas(logo_frame, bg=self.bg_color, width=50, height=50,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")
        logo_canvas.create_oval(5, 5, 45, 45, fill=self.accent_color, outline="")
        logo_canvas.create_text(25, 25, text="G", font=('Segoe UI', 20, 'bold'), fill="#ffffff")

        tk.Label(logo_frame, text="GAGARIN BRIDGE", font=self.title_font,
                 bg=self.bg_color, fg=self.text_color).pack(side="left", padx=15)

        # Основной контент
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(fill="both", expand=True)

        # Две колонки
        left_panel = ttk.Frame(content_frame, style="TFrame")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 20))

        right_panel = ttk.Frame(content_frame, style="TFrame")
        right_panel.pack(side="right", fill="both", expand=True)

        # Левая панель - настройки
        settings_card = ttk.Frame(left_panel, style="Card.TFrame", padding=25)
        settings_card.pack(fill="both", expand=True)

        tk.Label(settings_card, text="Настройки конвертации",
                 font=self.subtitle_font, fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 25))

        # Выбор файла
        self.setup_file_selection(settings_card)

        # Формат вывода
        self.setup_format_selection(settings_card)

        # Настройки изображения
        self.setup_image_options(settings_card)

        # Место сохранения
        self.setup_output_selection(settings_card)

        # Кнопки действий
        self.setup_action_buttons(settings_card)

        # Правая панель - предпросмотр и информация
        preview_card = ttk.Frame(right_panel, style="Card.TFrame", padding=25)
        preview_card.pack(fill="both", expand=True)

        self.setup_preview_area(preview_card)

    def setup_file_selection(self, parent):
        """Настройка выбора файла"""
        file_frame = ttk.Frame(parent, style="Card.TFrame")
        file_frame.pack(fill="x", pady=(0, 20))

        tk.Label(file_frame, text="Исходный файл",
                 font=self.app_font, fg=self.secondary_text, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        input_frame = ttk.Frame(file_frame, style="Card.TFrame")
        input_frame.pack(fill="x", pady=5)

        self.input_entry = ttk.Entry(input_frame, style="TEntry")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind('<FocusOut>', self.on_input_changed)

        btn_frame = ttk.Frame(input_frame, style="Card.TFrame")
        btn_frame.pack(side="right")

        ttk.Button(btn_frame, text="Файл", style="TButton",
                   command=self.browse_input).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Папка", style="TButton",
                   command=self.toggle_batch_mode).pack(side="left", padx=2)

    def setup_format_selection(self, parent):
        """Настройка выбора формата"""
        format_frame = ttk.Frame(parent, style="Card.TFrame")
        format_frame.pack(fill="x", pady=20)

        tk.Label(format_frame, text="Формат вывода",
                 font=self.app_font, fg=self.secondary_text, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                         style="TCombobox", state="readonly")
        self.format_combo.pack(fill="x", pady=5)

    def setup_image_options(self, parent):
        """Настройки для изображений"""
        image_frame = ttk.Frame(parent, style="Card.TFrame")
        image_frame.pack(fill="x", pady=20)

        tk.Label(image_frame, text="Настройки изображения",
                 font=self.app_font, fg=self.secondary_text, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        # Чекбокс изменения размера
        resize_frame = ttk.Frame(image_frame, style="Card.TFrame")
        resize_frame.pack(fill="x", pady=5)

        ttk.Checkbutton(resize_frame, text="Изменить размер", variable=self.resize_var,
                        command=self.toggle_resize_options, style="TCheckbutton").pack(side="left")

        # Поля для размеров
        self.size_frame = ttk.Frame(image_frame, style="Card.TFrame")

        tk.Label(self.size_frame, text="Ширина:",
                 font=self.app_font, fg=self.secondary_text, bg=self.card_color).pack(side="left", padx=(0, 5))
        self.width_var = tk.StringVar()
        width_entry = ttk.Entry(self.size_frame, textvariable=self.width_var,
                                style="TEntry", width=8)
        width_entry.pack(side="left", padx=(0, 10))

        tk.Label(self.size_frame, text="Высота:",
                 font=self.app_font, fg=self.secondary_text, bg=self.card_color).pack(side="left", padx=(0, 5))
        self.height_var = tk.StringVar()
        height_entry = ttk.Entry(self.size_frame, textvariable=self.height_var,
                                 style="TEntry", width=8)
        height_entry.pack(side="left", padx=(0, 10))

        ttk.Checkbutton(self.size_frame, text="Сохранять пропорции",
                        variable=self.aspect_var, style="TCheckbutton").pack(side="left")

        # Сначала скрываем опции
        self.size_frame.pack_forget()

    def setup_output_selection(self, parent):
        """Настройка вывода"""
        output_frame = ttk.Frame(parent, style="Card.TFrame")
        output_frame.pack(fill="x", pady=20)

        tk.Label(output_frame, text="Сохранить в",
                 font=self.app_font, fg=self.secondary_text, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        output_input_frame = ttk.Frame(output_frame, style="Card.TFrame")
        output_input_frame.pack(fill="x", pady=5)

        self.output_entry = ttk.Entry(output_input_frame, style="TEntry")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ttk.Button(output_input_frame, text="Обзор", style="TButton",
                   command=self.browse_output).pack(side="right")

    def setup_action_buttons(self, parent):
        """Настройка кнопок действий"""
        action_frame = ttk.Frame(parent, style="Card.TFrame")
        action_frame.pack(fill="x", pady=(20, 0))

        # Прогресс-бар
        self.progress = ttk.Progressbar(action_frame, orient=tk.HORIZONTAL,
                                        mode='determinate', style="Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 10))

        # Статус конвертации
        self.status_label = tk.Label(action_frame, text="Готов к работе",
                                     font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        self.status_label.pack(fill="x", pady=(0, 15))

        # Кнопки
        button_frame = ttk.Frame(action_frame, style="Card.TFrame")
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="Конвертировать", style="Accent.TButton",
                   command=self.convert).pack(side="left", expand=True, padx=5)
        ttk.Button(button_frame, text="Очистить", style="TButton",
                   command=self.clear_fields).pack(side="left", expand=True, padx=5)

    def setup_preview_area(self, parent):
        """Настройка области предпросмотра"""
        # Заголовок
        tk.Label(parent, text="Предпросмотр",
                 font=self.subtitle_font, fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 15))

        # Canvas для предпросмотра
        preview_container = ttk.Frame(parent, style="Card.TFrame")
        preview_container.pack(fill="both", expand=True, pady=(0, 20))

        self.preview_canvas = tk.Canvas(preview_container, bg=self.card_color,
                                        highlightthickness=0, relief='flat')
        self.preview_canvas.pack(fill="both", expand=True, padx=1, pady=1)
        self.preview_canvas.create_text(200, 100, text="Выберите файл для предпросмотра",
                                        fill=self.secondary_text, font=self.subtitle_font)

        # Информация о файле
        info_frame = ttk.Frame(parent, style="Card.TFrame")
        info_frame.pack(fill="x")

        tk.Label(info_frame, text="Информация о файле",
                 font=self.subtitle_font, fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        self.info_text = tk.Text(info_frame, height=6, bg=self.card_color, fg=self.text_color,
                                 font=self.mono_font, wrap=tk.WORD, relief='flat', borderwidth=0)
        self.info_text.pack(fill="x")
        self.info_text.insert(1.0, "Файл не выбран")
        self.info_text.config(state=tk.DISABLED)

    def toggle_resize_options(self):
        """Переключение видимости опций изменения размера"""
        if self.resize_var.get():
            self.size_frame.pack(fill="x", pady=5)
        else:
            self.size_frame.pack_forget()

    def on_input_changed(self, event=None):
        """Обновляет доступные форматы при изменении входного файла"""
        input_path = self.input_entry.get()
        if input_path and os.path.exists(input_path):
            file_ext = os.path.splitext(input_path)[1].upper().lstrip('.')
            if file_ext:
                try:
                    output_formats = self.controller.get_output_formats_for_input(file_ext)
                    self.format_combo['values'] = output_formats
                    if output_formats:
                        self.format_combo.current(0)
                        self.update_output_suggestion()

                    # Обновляем информацию о файле и предпросмотр
                    self.update_file_info()
                    self.update_preview()

                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось загрузить форматы: {str(e)}")

    def update_file_info(self):
        """Обновление информации о файле"""
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
        """Обновление предпросмотра изображения"""
        input_path = self.input_entry.get()
        if not input_path or not os.path.exists(input_path):
            return

        try:
            file_ext = os.path.splitext(input_path)[1].lower().lstrip('.')
            supported_formats = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp']

            if file_ext in supported_formats:
                with Image.open(input_path) as img:
                    # Масштабируем для предпросмотра
                    img.thumbnail((400, 300), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)

                    self.preview_canvas.delete("all")
                    self.preview_canvas.create_image(200, 150, image=photo)
                    self.preview_canvas.image = photo  # Сохраняем ссылку
            else:
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(200, 150, text="Предпросмотр недоступен\nдля этого типа файла",
                                                fill=self.secondary_text, font=self.subtitle_font, justify=tk.CENTER)

        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(200, 150, text="Ошибка загрузки\nпредпросмотра",
                                            fill="#ff5252", font=self.subtitle_font)

    def format_file_size(self, size_bytes):
        """Форматирует размер файла в читаемом виде"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def toggle_batch_mode(self):
        """Переключение между режимами одиночного и пакетного преобразования"""
        is_batch = self.batch_var.get()
        self.batch_var.set(not is_batch)

        if is_batch:
            self.input_entry.delete(0, tk.END)
        else:
            self.browse_input()

    def browse_input(self):
        """Выбор входного файла или папки"""
        try:
            if self.batch_var.get():
                folder = filedialog.askdirectory(title="Выберите папку для пакетной обработки")
                if folder:
                    self.input_entry.delete(0, tk.END)
                    self.input_entry.insert(0, folder)
            else:
                filetypes = [
                    ("Все файлы", "*.*"),
                    ("Изображения", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                    ("Данные", "*.csv *.json *.xlsx *.xls *.txt"),
                ]

                filename = filedialog.askopenfilename(title="Выберите файл для конвертации", filetypes=filetypes)
                if filename:
                    self.input_entry.delete(0, tk.END)
                    self.input_entry.insert(0, filename)
                    self.on_input_changed()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выбрать файл: {str(e)}")

    def browse_output(self):
        """Выбор места сохранения"""
        try:
            initial_dir = os.path.dirname(self.output_entry.get()) if self.output_entry.get() else ""
            defaultext = self.format_var.get().lower() if self.format_var.get() else ""

            filename = filedialog.asksaveasfilename(
                title="Сохранить как",
                initialdir=initial_dir,
                defaultextension=f".{defaultext}" if defaultext else ""
            )
            if filename:
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, filename)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выбрать место сохранения: {str(e)}")

    def update_output_suggestion(self):
        """Автоматическое предложение имени выходного файла"""
        try:
            input_path = self.input_entry.get()
            if not input_path or not self.format_var.get():
                return

            base, ext = os.path.splitext(input_path)
            new_ext = self.format_var.get().lower()
            if not new_ext.startswith('.'):
                new_ext = '.' + new_ext
            suggested_path = base + new_ext
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, suggested_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить предложение выходного файла: {str(e)}")

    def convert(self):
        """Запуск процесса конвертации"""
        input_path = self.input_entry.get()
        output_path = self.output_entry.get()
        output_format = self.format_var.get()

        if not input_path or not output_path or not output_format:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля")
            return

        options = {
            'batch': self.batch_var.get(),
            'resize_enabled': self.resize_var.get(),
            'width': int(self.width_var.get()) if self.width_var.get().isdigit() else None,
            'height': int(self.height_var.get()) if self.height_var.get().isdigit() else None,
            'keep_aspect': self.aspect_var.get(),
            'quality': 95  # Фиксированное качество
        }

        try:
            if self.batch_var.get():
                success = self.controller.convert_batch(
                    input_path,
                    output_path,
                    output_format,
                    options,
                    self.update_progress
                )
            else:
                success = self.controller.convert_file(
                    input_path,
                    output_path,
                    output_format,
                    options,
                    self.update_progress
                )

            if success:
                messagebox.showinfo("Успех", "Конвертация завершена успешно!")
            else:
                messagebox.showerror("Ошибка", "Не удалось выполнить конвертацию")

        except Exception as e:
            messagebox.showerror("Ошибка конвертации", f"Произошла ошибка: {str(e)}")
        finally:
            self.update_progress(0)
            self.status_label.config(text="Готов к работе")

    def update_progress(self, value):
        """Обновление прогресс-бара"""
        self.progress['value'] = value
        self.status_label.config(text=f"Прогресс: {value:.1f}%")
        self.root.update_idletasks()

    def clear_fields(self):
        """Очистка всех полей"""
        self.input_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        self.format_combo.set('')
        self.resize_var.set(False)
        self.width_var.set('')
        self.height_var.set('')
        self.toggle_resize_options()

        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Файл не выбран")
        self.info_text.config(state=tk.DISABLED)

        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(200, 150, text="Выберите файл для предпросмотра",
                                        fill=self.secondary_text, font=self.subtitle_font)

        self.status_label.config(text="Готов к работе")
        self.progress['value'] = 0