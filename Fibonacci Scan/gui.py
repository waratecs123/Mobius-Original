import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from functions import QRCodeFunctions


class FibonacciScanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fibonacci Scan")
        self.functions = QRCodeFunctions(self)

        # Настройка полноэкранного режима
        self.root.attributes('-fullscreen', True)

        # Современная цветовая палитра
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.secondary_accent = "#818cf8"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#0f0f23"
        self.success_color = "#10b981"
        self.warning_color = "#f59e0b"

        # Градиентные цвета для заголовка
        self.gradient_start = "#6366f1"
        self.gradient_end = "#8b5cf6"

        # Шрифты
        self.title_font = ('Arial', 24, 'bold')
        self.subtitle_font = ('Arial', 16)
        self.app_font = ('Arial', 13)
        self.button_font = ('Arial', 12, 'bold')
        self.small_font = ('Arial', 11)
        self.mono_font = ('Courier New', 10)

        # Текущие настройки
        self.current_section = "Генератор QR"

        # Настройка интерфейса
        self.setup_ui()
        self.setup_styles()

    def setup_styles(self):
        # Стили для виджетов
        style = ttk.Style()
        style.theme_use('clam')

        # Настройка стилей
        style.configure('Custom.TNotebook', background=self.card_color, borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                        background="#1a1a2e",
                        foreground=self.text_color,
                        padding=[15, 8],
                        font=self.small_font)
        style.map('Custom.TNotebook.Tab',
                  background=[('selected', self.card_color)],
                  foreground=[('selected', self.accent_color)])

        # Стиль для кнопок
        style.configure('Accent.TButton',
                        background=self.accent_color,
                        foreground='white',
                        borderwidth=0,
                        font=self.button_font,
                        padding=(15, 8))
        style.map('Accent.TButton',
                  background=[('active', '#4f46e5')])

        style.configure('Secondary.TButton',
                        background='#1a1a2e',
                        foreground=self.text_color,
                        borderwidth=0,
                        font=self.button_font,
                        padding=(15, 8))
        style.map('Secondary.TButton',
                  background=[('active', '#374151')])

        style.configure('Success.TButton',
                        background=self.success_color,
                        foreground='white',
                        borderwidth=0,
                        font=self.button_font,
                        padding=(15, 8))
        style.map('Success.TButton',
                  background=[('active', '#059669')])

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)

        # Главный контейнер с тенью
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Контентная область
        content_wrapper = tk.Frame(main_container, bg=self.bg_color)
        content_wrapper.pack(fill="both", expand=True, pady=(20, 0))

        # Сайдбар
        self.setup_sidebar(content_wrapper)

        # Основная область
        self.setup_main_area(content_wrapper)

        # Инициализация начального состояния
        self.show_section(self.current_section)

    def setup_app_header(self, parent):
        """Заголовок приложения с полным названием"""
        header_frame = tk.Frame(parent, bg=self.bg_color, height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)

        # Градиентный фон для заголовка
        gradient_canvas = tk.Canvas(header_frame, bg=self.bg_color, highlightthickness=0)
        gradient_canvas.pack(fill="both", expand=True)

        # Создаем градиент
        width = header_frame.winfo_reqwidth()
        for i in range(width):
            ratio = i / width
            r = int(int(self.gradient_start[1:3], 16) * (1 - ratio) + int(self.gradient_end[1:3], 16) * ratio)
            g = int(int(self.gradient_start[3:5], 16) * (1 - ratio) + int(self.gradient_end[3:5], 16) * ratio)
            b = int(int(self.gradient_start[5:7], 16) * (1 - ratio) + int(self.gradient_end[5:7], 16) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            gradient_canvas.create_line(i, 0, i, 80, fill=color)

        # Текст поверх градиента
        title_text = "Fibonacci Scan"
        subtitle_text = "Генератор и сканер QR-кодов"

        title_label = tk.Label(gradient_canvas, text=title_text,
                               bg=self.bg_color, fg="white",
                               font=('Arial', 28, 'bold'),
                               compound='center')
        title_label.place(relx=0.5, rely=0.4, anchor='center')

        subtitle_label = tk.Label(gradient_canvas, text=subtitle_text,
                                  bg=self.bg_color, fg=self.secondary_text,
                                  font=self.subtitle_font,
                                  compound='center')
        subtitle_label.place(relx=0.5, rely=0.7, anchor='center')

    def setup_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.card_color, width=300)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)

        # Верхняя часть сайдбара
        top_sidebar = tk.Frame(sidebar, bg=self.card_color)
        top_sidebar.pack(fill="x", pady=(20, 30), padx=20)

        # Логотип и название
        logo_frame = tk.Frame(top_sidebar, bg=self.card_color)
        logo_frame.pack(fill="x", pady=(0, 30))

        # Иконка приложения
        icon_label = tk.Label(logo_frame, text="🔷", bg=self.card_color,
                              fg=self.accent_color, font=('Arial', 32))
        icon_label.pack(side="left", padx=(0, 10))

        # Название приложения
        name_frame = tk.Frame(logo_frame, bg=self.card_color)
        name_frame.pack(side="left", fill="y")

        tk.Label(name_frame, text="FIBONACCI", bg=self.card_color,
                 fg=self.accent_color, font=('Arial', 18, 'bold')).pack(anchor="w")
        tk.Label(name_frame, text="SCAN", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 18, 'bold')).pack(anchor="w")

        # Разделитель
        separator = tk.Frame(top_sidebar, height=2, bg=self.border_color)
        separator.pack(fill="x", pady=(0, 20))

        # Меню навигации
        nav_frame = tk.Frame(top_sidebar, bg=self.card_color)
        nav_frame.pack(fill="x")

        nav_items = [
            ("Генератор QR", "", ""),
            ("Сканирование", "", "")
        ]

        self.nav_buttons = []
        for item, icon, description in nav_items:
            btn_container = tk.Frame(nav_frame, bg=self.card_color)
            btn_container.pack(fill="x", pady=8)

            btn = tk.Button(btn_container,
                            text=f"   {icon}  {item}",
                            font=self.button_font,
                            bg=self.card_color,
                            fg=self.secondary_text,
                            bd=0,
                            activebackground="#252525",
                            activeforeground=self.accent_color,
                            padx=15,
                            pady=12,
                            anchor="w",
                            highlightthickness=0,
                            command=lambda n=item: self.show_section(n))
            btn.pack(fill="x")

            # Описание пункта меню
            desc_label = tk.Label(btn_container, text=description,
                                  bg=self.card_color, fg=self.secondary_text,
                                  font=('Arial', 9), anchor="w", justify="left")
            desc_label.pack(fill="x", padx=(45, 0), pady=(2, 0))

            self.nav_buttons.append(btn)

        # Нижняя часть сайдбара
        bottom_sidebar = tk.Frame(sidebar, bg=self.card_color)
        bottom_sidebar.pack(side="bottom", fill="x", pady=20, padx=20)

        # Статистика
        stats_frame = tk.Frame(bottom_sidebar, bg=self.card_color)
        stats_frame.pack(fill="x", pady=(0, 15))

        tk.Label(stats_frame, text="Статистика", bg=self.card_color,
                 fg=self.text_color, font=self.small_font).pack(anchor="w")

        stats_text = tk.Label(stats_frame, text="Сгенерировано: 0 | Просканировано: 0",
                              bg=self.card_color, fg=self.secondary_text,
                              font=('Arial', 9))
        stats_text.pack(anchor="w", pady=(2, 0))

        # Кнопка выхода
        exit_btn = tk.Button(bottom_sidebar, text="Выход из приложения",
                             bg="#dc2626",
                             fg="white",
                             font=self.button_font,
                             bd=0,
                             command=self.root.quit,
                             padx=15,
                             pady=12)
        exit_btn.pack(fill="x")

    def setup_main_area(self, parent):
        self.main_area = tk.Frame(parent, bg=self.bg_color)
        self.main_area.pack(side="right", fill="both", expand=True)

        # Заголовок раздела
        self.header_frame = tk.Frame(self.main_area, bg=self.bg_color)
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.section_title = tk.Label(self.header_frame, text=self.current_section,
                                      bg=self.bg_color, fg=self.text_color, font=self.title_font)
        self.section_title.pack(side="left")

        # Индикатор активного раздела
        indicator = tk.Frame(self.header_frame, height=3, bg=self.accent_color, width=100)
        indicator.pack(side="left", padx=(15, 0), pady=(5, 0))

        # Область контента
        self.content_frame = tk.Frame(self.main_area, bg=self.bg_color)
        self.content_frame.pack(fill="both", expand=True)

        # Область предпросмотра/сканирования
        self.preview_frame = tk.Frame(self.content_frame, bg=self.card_color,
                                      padx=25, pady=25)
        self.preview_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))

        # Область настроек
        self.settings_frame = tk.Frame(self.content_frame, bg=self.card_color,
                                       width=400, padx=25, pady=25)
        self.settings_frame.pack(side="left", fill="y")
        self.settings_frame.pack_propagate(False)

    def setup_generator_ui(self):
        # Очищаем предыдущие виджеты
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        # Обновляем заголовок
        self.section_title.config(text="Генератор QR-кодов")

        # Настройки генератора QR
        self.setup_generator_settings()

        # Панель предпросмотра
        self.setup_preview_ui()

    def setup_generator_settings(self):
        settings_container = tk.Frame(self.settings_frame, bg=self.card_color)
        settings_container.pack(fill="both", expand=True)

        # Notebook для настроек с улучшенным стилем
        style = ttk.Style()
        style.configure("Custom.TNotebook.Tab", padding=[20, 8], font=self.small_font)

        settings_notebook = ttk.Notebook(settings_container, style="Custom.TNotebook")

        # Вкладка "Дизайн"
        design_frame = tk.Frame(settings_notebook, bg=self.card_color)
        settings_notebook.add(design_frame, text="Дизайн")

        # Цвета
        color_frame = tk.Frame(design_frame, bg=self.card_color)
        color_frame.pack(fill="x", pady=(0, 20))

        tk.Label(color_frame, text="ЦВЕТА QR-КОДА", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        color_grid = tk.Frame(color_frame, bg=self.card_color)
        color_grid.pack(fill="x")

        tk.Label(color_grid, text="Цвет кода:", bg=self.card_color, fg=self.text_color,
                 font=self.small_font).grid(row=0, column=0, sticky="w", pady=8)
        self.color_btn = tk.Button(color_grid, text="Выбрать цвет",
                                   bg=self.functions.settings["qr_fill_color"],
                                   fg="white", bd=0, font=self.small_font,
                                   command=lambda: self.functions.choose_color("fill"),
                                   padx=10, pady=5)
        self.color_btn.grid(row=0, column=1, padx=(10, 0), sticky="e", pady=8)

        tk.Label(color_grid, text="Фон:", bg=self.card_color, fg=self.text_color,
                 font=self.small_font).grid(row=1, column=0, sticky="w", pady=8)
        self.bg_color_btn = tk.Button(color_grid, text="Выбрать цвет",
                                      bg=self.functions.settings["qr_back_color"],
                                      fg="black", bd=0, font=self.small_font,
                                      command=lambda: self.functions.choose_color("back"),
                                      padx=10, pady=5)
        self.bg_color_btn.grid(row=1, column=1, padx=(10, 0), sticky="e", pady=8)

        # Логотип
        logo_frame = tk.Frame(design_frame, bg=self.card_color)
        logo_frame.pack(fill="x", pady=(0, 20))

        tk.Label(logo_frame, text="ЛОГОТИП", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        logo_btn_frame = tk.Frame(logo_frame, bg=self.card_color)
        logo_btn_frame.pack(fill="x")

        add_logo_btn = tk.Button(logo_btn_frame, text="Добавить логотип",
                                 bg="#2d3748", fg=self.text_color,
                                 font=self.small_font, bd=0,
                                 command=self.functions.add_logo,
                                 padx=15, pady=8)
        add_logo_btn.pack(side="left", fill="x", expand=True)

        remove_logo_btn = tk.Button(logo_btn_frame, text="Удалить",
                                    bg="#2d3748", fg=self.text_color,
                                    font=self.small_font, bd=0,
                                    command=self.functions.remove_logo,
                                    padx=15, pady=8)
        remove_logo_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Размер
        size_frame = tk.Frame(design_frame, bg=self.card_color)
        size_frame.pack(fill="x")

        tk.Label(size_frame, text="РАЗМЕР И ГРАНИЦА", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        size_grid = tk.Frame(size_frame, bg=self.card_color)
        size_grid.pack(fill="x")

        tk.Label(size_grid, text="Размер (px):", bg=self.card_color, fg=self.text_color,
                 font=self.small_font).grid(row=0, column=0, sticky="w", pady=8)
        self.size_entry = tk.Entry(size_grid, bg="#252525", fg=self.text_color,
                                   font=self.small_font, insertbackground=self.text_color,
                                   relief="flat", bd=1, width=10)
        self.size_entry.insert(0, str(self.functions.settings["qr_size"]))
        self.size_entry.grid(row=0, column=1, padx=(10, 0), sticky="w", pady=8)

        tk.Label(size_grid, text="Граница:", bg=self.card_color, fg=self.text_color,
                 font=self.small_font).grid(row=1, column=0, sticky="w", pady=8)
        self.border_entry = tk.Entry(size_grid, bg="#252525", fg=self.text_color,
                                     font=self.small_font, insertbackground=self.text_color,
                                     relief="flat", bd=1, width=10)
        self.border_entry.insert(0, str(self.functions.settings["qr_border"]))
        self.border_entry.grid(row=1, column=1, padx=(10, 0), sticky="w", pady=8)

        # Вкладка "Основные"
        basic_frame = tk.Frame(settings_notebook, bg=self.card_color)
        settings_notebook.add(basic_frame, text="Основные")

        # Тип содержимого
        type_frame = tk.Frame(basic_frame, bg=self.card_color)
        type_frame.pack(fill="x", pady=(0, 20))

        tk.Label(type_frame, text="ТИП СОДЕРЖИМОГО", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        self.content_type = ttk.Combobox(type_frame,
                                         values=["URL", "Текст", "vCard", "WiFi", "Email", "SMS", "Биткоин"],
                                         font=self.small_font,
                                         state="readonly")
        self.content_type.set("URL")
        self.content_type.pack(fill="x")
        self.content_type.bind("<<ComboboxSelected>>", self.functions.update_content_fields)

        # Поле ввода данных
        data_frame = tk.Frame(basic_frame, bg=self.card_color)
        data_frame.pack(fill="x", pady=(0, 20))

        tk.Label(data_frame, text="СОДЕРЖИМОЕ", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        self.data_entry = tk.Text(data_frame, height=8, bg="#2D3748", fg=self.text_color,
                                  insertbackground=self.text_color, wrap="word",
                                  font=self.small_font, bd=1, relief="flat")
        self.data_entry.pack(fill="x")
        self.data_entry.insert("1.0", self.functions.settings["qr_data"])

        # Вкладка "Дополнительно"
        advanced_frame = tk.Frame(settings_notebook, bg=self.card_color)
        settings_notebook.add(advanced_frame, text="Дополнительно")

        # Коррекция ошибок
        error_frame = tk.Frame(advanced_frame, bg=self.card_color)
        error_frame.pack(fill="x", pady=(0, 20))

        tk.Label(error_frame, text="КОРРЕКЦИЯ ОШИБОК", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        self.error_correction = ttk.Combobox(error_frame,
                                             values=["Низкая", "Средняя", "Высокая", "Максимальная"],
                                             font=self.small_font,
                                             state="readonly")
        self.error_correction.set("Высокая")
        self.error_correction.pack(fill="x")

        # Версия QR
        version_frame = tk.Frame(advanced_frame, bg=self.card_color)
        version_frame.pack(fill="x")

        tk.Label(version_frame, text="ВЕРСИЯ QR", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        self.version_entry = tk.Entry(version_frame, bg="#252525", fg=self.text_color,
                                      font=self.small_font, insertbackground=self.text_color,
                                      relief="flat", bd=1)
        self.version_entry.insert(0, str(self.functions.settings["qr_version"]))
        self.version_entry.pack(fill="x")

        settings_notebook.pack(fill="both", expand=True)

        # Кнопки действий
        action_frame = tk.Frame(settings_container, bg=self.card_color)
        action_frame.pack(fill="x", pady=(20, 0))

        generate_btn = tk.Button(action_frame, text="Сгенерировать QR-код",
                                 bg=self.accent_color, fg="white",
                                 font=self.button_font, bd=0,
                                 command=self.functions.generate_qr,
                                 padx=20, pady=12)
        generate_btn.pack(fill="x")

        random_btn = tk.Button(action_frame, text="Случайный QR",
                               bg="#2d3748", fg=self.text_color,
                               font=self.button_font, bd=0,
                               command=self.functions.generate_random_qr,
                               padx=20, pady=10)
        random_btn.pack(fill="x", pady=(10, 0))

    def setup_preview_ui(self):
        # Заголовок
        title_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        title_frame.pack(fill="x", pady=(0, 20))

        tk.Label(title_frame, text="ПРЕДПРОСМОТР", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 16, 'bold')).pack(side="left")

        # Область предпросмотра с рамкой
        preview_container = tk.Frame(self.preview_frame, bg="#1a1a2e", relief="raised", bd=1)
        preview_container.pack(fill="both", expand=True)

        # Холст для QR-кода
        self.qr_canvas = tk.Canvas(preview_container, bg="#1a1a2e", highlightthickness=0)
        self.qr_canvas.pack(fill="both", expand=True, padx=40, pady=40)

        # Информация о QR-коде
        info_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        info_frame.pack(fill="x", pady=(20, 0))

        self.qr_info = tk.Label(info_frame, text="Готов к генерации...",
                                bg=self.card_color, fg=self.secondary_text,
                                font=self.small_font, justify="left")
        self.qr_info.pack(anchor="w")

        # Кнопки экспорта
        export_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        export_frame.pack(fill="x", pady=(20, 0))

        copy_btn = tk.Button(export_frame, text="Копировать в буфер",
                             bg=self.accent_color, fg="white",
                             font=self.button_font, bd=0,
                             command=self.functions.copy_to_clipboard,
                             padx=15, pady=10)
        copy_btn.pack(side="left", fill="x", expand=True)

        export_png_btn = tk.Button(export_frame, text="Экспорт PNG",
                                   bg="#2d3748", fg=self.text_color,
                                   font=self.button_font, bd=0,
                                   command=self.functions.export_png,
                                   padx=15, pady=10)
        export_png_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))

        export_svg_btn = tk.Button(export_frame, text="Экспорт SVG",
                                   bg="#2d3748", fg=self.text_color,
                                   font=self.button_font, bd=0,
                                   command=self.functions.export_svg,
                                   padx=15, pady=10)
        export_svg_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))

    def setup_scan_ui(self):
        # Очищаем предыдущие виджеты
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        # Обновляем заголовок
        self.section_title.config(text="Сканирование QR-кодов")

        # Панель загрузки изображения
        scan_frame = tk.Frame(self.settings_frame, bg=self.card_color)
        scan_frame.pack(fill="both", expand=True)

        tk.Label(scan_frame, text="СКАНИРОВАНИЕ", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 16, 'bold')).pack(pady=(0, 20))

        load_btn = tk.Button(scan_frame, text="Загрузить изображение для сканирования",
                             bg=self.accent_color, fg="white",
                             font=self.button_font, bd=0,
                             command=self.functions.load_image_for_scan,
                             padx=20, pady=12)
        load_btn.pack(fill="x", pady=(0, 20))

        # Статус сканирования
        self.scan_status = tk.Label(scan_frame, text="Ожидание загрузки изображения...",
                                    bg=self.card_color, fg=self.secondary_text,
                                    font=self.small_font)
        self.scan_status.pack(anchor="w", pady=(0, 10))

        # Результаты сканирования
        result_frame = tk.Frame(scan_frame, bg=self.card_color)
        result_frame.pack(fill="both", expand=True)

        tk.Label(result_frame, text="РЕЗУЛЬТАТ СКАНИРОВАНИЯ:", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        result_container = tk.Frame(result_frame, bg="#1a1a2e", relief="sunken", bd=1)
        result_container.pack(fill="both", expand=True)

        self.scan_result = tk.Text(result_container, height=15, bg="#1a1a2e", fg=self.text_color,
                                   insertbackground=self.text_color, wrap="word",
                                   font=self.mono_font, bd=0, relief="flat")

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(result_container, orient="vertical", command=self.scan_result.yview)
        self.scan_result.configure(yscrollcommand=scrollbar.set)

        self.scan_result.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Панель предпросмотра загруженного изображения
        preview_title_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        preview_title_frame.pack(fill="x", pady=(0, 20))

        tk.Label(preview_title_frame, text="ПРЕДПРОСМОТР ИЗОБРАЖЕНИЯ", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 16, 'bold')).pack(side="left")

        self.scan_image_frame = tk.Frame(self.preview_frame, bg="#1a1a2e", relief="raised", bd=1)
        self.scan_image_frame.pack(fill="both", expand=True)

        self.scan_canvas = tk.Canvas(self.scan_image_frame, bg="#1a1a2e", highlightthickness=0)
        self.scan_canvas.pack(fill="both", expand=True, padx=40, pady=40)

        # Информация об изображении
        image_info_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        image_info_frame.pack(fill="x", pady=(20, 0))

        self.image_info = tk.Label(image_info_frame, text="Размер: - | Формат: -",
                                   bg=self.card_color, fg=self.secondary_text,
                                   font=self.small_font)
        self.image_info.pack(anchor="w")

    def show_section(self, section_name):
        self.current_section = section_name
        display_name = "Генератор QR-кодов" if section_name == "Генератор QR" else "Сканирование QR-кодов"
        self.section_title.config(text=display_name)

        # Обновляем состояние кнопок навигации
        for btn in self.nav_buttons:
            if section_name in btn.cget("text"):
                btn.config(fg=self.accent_color, bg="#1a1a2e")
            else:
                btn.config(fg=self.secondary_text, bg=self.card_color)

        # Показываем соответствующий раздел
        if section_name == "Генератор QR":
            self.setup_generator_ui()
        elif section_name == "Сканирование":
            self.setup_scan_ui()

    def display_qr(self, img):
        self.qr_canvas.delete("all")
        self.qr_image = ImageTk.PhotoImage(img)

        canvas_width = self.qr_canvas.winfo_width()
        canvas_height = self.qr_canvas.winfo_height()

        x = (canvas_width - self.qr_image.width()) // 2
        y = (canvas_height - self.qr_image.height()) // 2

        self.qr_canvas.create_image(x, y, image=self.qr_image, anchor="nw")

    def display_scan_image(self, img):
        self.scan_canvas.delete("all")
        img.thumbnail((400, 400))
        self.scan_img_tk = ImageTk.PhotoImage(img)

        canvas_width = self.scan_canvas.winfo_width()
        canvas_height = self.scan_canvas.winfo_height()

        x = (canvas_width - self.scan_img_tk.width()) // 2
        y = (canvas_height - self.scan_img_tk.height()) // 2

        self.scan_canvas.create_image(x, y, image=self.scan_img_tk, anchor="nw")

    def update_scan_status(self, message, is_success=True):
        """Обновляет статус сканирования"""
        color = self.success_color if is_success else self.warning_color
        self.scan_status.config(text=message, fg=color)

    def update_image_info(self, width, height, format_name):
        """Обновляет информацию об изображении"""
        self.image_info.config(text=f"Размер: {width}x{height}px | Формат: {format_name}")