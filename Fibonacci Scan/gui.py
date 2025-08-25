import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from functions import QRCodeFunctions


class FibonacciScanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fibonacci Scan")
        self.functions = QRCodeFunctions(self)

        # Настройка полноэкранного режима (без возможности выхода)
        self.root.attributes('-fullscreen', True)

        # Темная цветовая палитра
        self.bg_color = "#121212"
        self.card_color = "#1e1e1e"
        self.accent_color = "#4870ff"
        self.text_color = "#e0e0e0"
        self.secondary_text = "#a0a0a0"

        # Шрифты
        self.title_font = ('Segoe UI', 18, 'bold')
        self.app_font = ('Segoe UI', 12)
        self.button_font = ('Segoe UI', 12)
        self.small_font = ('Segoe UI', 11)

        # Текущие настройки
        self.current_section = "Генератор QR"
        self.current_settings_tab = "Дизайн"

        # Настройка интерфейса
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)

        # Главный контейнер
        main_container = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main_container.pack(fill="both", expand=True)

        # Сайдбар
        self.setup_sidebar(main_container)

        # Основная область
        self.setup_main_area(main_container)

        # Инициализация начального состояния
        self.show_section(self.current_section)
        self.show_settings_tab(self.current_settings_tab)

    def setup_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.card_color, width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Верхняя часть сайдбара с логотипом
        top_sidebar = tk.Frame(sidebar, bg=self.card_color)
        top_sidebar.pack(fill="x", pady=(20, 30), padx=20)

        logo_frame = tk.Frame(top_sidebar, bg=self.card_color)
        logo_frame.pack(fill="x")

        tk.Label(logo_frame, text="FIBONACCI SCAN", bg=self.card_color,
                 fg=self.accent_color, font=self.title_font).pack(side="left")

        # Меню навигации
        nav_frame = tk.Frame(top_sidebar, bg=self.card_color)
        nav_frame.pack(fill="x")

        nav_items = [
            ("Генератор QR", self.accent_color),
            ("Сканирование", self.accent_color)
        ]

        self.nav_buttons = []
        for item, color in nav_items:
            btn = tk.Button(nav_frame,
                            text=item,
                            font=self.app_font,
                            bg=self.card_color,
                            fg=self.text_color,
                            bd=0,
                            activebackground="#252525",
                            activeforeground=self.accent_color,
                            padx=20,
                            pady=12,
                            anchor="w",
                            highlightthickness=0,
                            command=lambda n=item: self.show_section(n))
            btn.pack(fill="x", pady=2)

            self.nav_buttons.append(btn)

    def setup_main_area(self, parent):
        self.main_area = tk.Frame(parent, bg=self.bg_color)
        self.main_area.pack(side="right", fill="both", expand=True)

        # Заголовок
        self.header_frame = tk.Frame(self.main_area, bg=self.bg_color)
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.section_title = tk.Label(self.header_frame, text=self.current_section,
                                      bg=self.bg_color, fg=self.text_color, font=self.title_font)
        self.section_title.pack(side="left")

        # Область контента
        self.content_frame = tk.Frame(self.main_area, bg=self.bg_color)
        self.content_frame.pack(fill="both", expand=True)

        # Область предпросмотра/сканирования
        self.preview_frame = tk.Frame(self.content_frame, bg=self.card_color, padx=15, pady=15)
        self.preview_frame.pack(side="right", fill="both", expand=True)

        # Область настроек
        self.settings_frame = tk.Frame(self.content_frame, bg=self.card_color, width=350, padx=15, pady=15)
        self.settings_frame.pack(side="left", fill="y")
        self.settings_frame.pack_propagate(False)

    def setup_generator_ui(self):
        # Очищаем предыдущие виджеты
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        # Обновляем заголовок
        self.section_title.config(text="Генератор QR")

        # Настройки генератора QR
        self.setup_generator_settings()

        # Панель предпросмотра
        self.setup_preview_ui()

    def setup_generator_settings(self):
        # Главный контейнер настроек
        settings_container = tk.Frame(self.settings_frame, bg=self.card_color)
        settings_container.pack(fill="both", expand=True)

        # Кнопка генерации QR
        generate_btn = tk.Button(settings_container, text="Сгенерировать QR", bg=self.accent_color, fg="#ffffff",
                                 font=self.button_font, bd=0, command=self.functions.generate_qr)
        generate_btn.pack(fill="x", pady=(0, 15))

        # Notebook для разных категорий настроек
        settings_notebook = ttk.Notebook(settings_container, style="Custom.TNotebook")

        # Стиль для Notebook
        style = ttk.Style()
        style.configure("Custom.TNotebook", background=self.card_color, borderwidth=0)
        style.configure("Custom.TNotebook.Tab", background="#252525", foreground=self.text_color,
                        padding=[10, 5], font=self.small_font)
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", self.card_color)],
                  foreground=[("selected", self.accent_color)])

        # Вкладка "Дизайн"
        design_frame = tk.Frame(settings_notebook, bg=self.card_color)
        settings_notebook.add(design_frame, text="Дизайн")

        # Цвета
        tk.Label(design_frame, text="Цвета:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).pack(pady=(10, 5), anchor="w")

        color_frame = tk.Frame(design_frame, bg=self.card_color)
        color_frame.pack(fill="x", pady=(0, 10))

        tk.Label(color_frame, text="Цвет кода:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).grid(row=0, column=0, sticky="w")
        self.color_btn = tk.Button(color_frame, text="Выбрать", bg=self.functions.settings["qr_fill_color"],
                                   fg="#ffffff", bd=0, font=self.small_font,
                                   command=lambda: self.functions.choose_color("fill"))
        self.color_btn.grid(row=0, column=1, padx=5, sticky="e")

        tk.Label(color_frame, text="Фон:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.bg_color_btn = tk.Button(color_frame, text="Выбрать", bg=self.functions.settings["qr_back_color"],
                                      fg="#000000", bd=0, font=self.small_font,
                                      command=lambda: self.functions.choose_color("back"))
        self.bg_color_btn.grid(row=1, column=1, padx=5, pady=(10, 0), sticky="e")

        # Логотип
        tk.Label(design_frame, text="Логотип:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).pack(pady=(15, 5), anchor="w")

        logo_btn_frame = tk.Frame(design_frame, bg=self.card_color)
        logo_btn_frame.pack(fill="x", pady=(0, 10))

        add_logo_btn = tk.Button(logo_btn_frame, text="Добавить лого", bg="#252525", fg=self.text_color,
                                 bd=0, font=self.small_font, command=self.functions.add_logo)
        add_logo_btn.pack(side="left", fill="x", expand=True)

        remove_logo_btn = tk.Button(logo_btn_frame, text="Удалить", bg="#252525", fg=self.text_color,
                                    bd=0, font=self.small_font, command=self.functions.remove_logo)
        remove_logo_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Размер и границы
        tk.Label(design_frame, text="Размер:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).pack(pady=(15, 5), anchor="w")

        size_frame = tk.Frame(design_frame, bg=self.card_color)
        size_frame.pack(fill="x", pady=(0, 10))

        tk.Label(size_frame, text="Размер (px):", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).grid(row=0, column=0, sticky="w")
        self.size_entry = tk.Entry(size_frame, bg="#252525", fg=self.text_color,
                                   font=self.app_font, insertbackground=self.text_color,
                                   relief="flat", highlightthickness=1,
                                   highlightcolor=self.accent_color, highlightbackground="#404040")
        self.size_entry.insert(0, str(self.functions.settings["qr_size"]))
        self.size_entry.grid(row=0, column=1, padx=5, sticky="e")

        tk.Label(size_frame, text="Граница:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.border_entry = tk.Entry(size_frame, bg="#252525", fg=self.text_color,
                                     font=self.app_font, insertbackground=self.text_color,
                                     relief="flat", highlightthickness=1,
                                     highlightcolor=self.accent_color, highlightbackground="#404040")
        self.border_entry.insert(0, str(self.functions.settings["qr_border"]))
        self.border_entry.grid(row=1, column=1, padx=5, pady=(10, 0), sticky="e")

        # Вкладка "Основные"
        basic_frame = tk.Frame(settings_notebook, bg=self.card_color)
        settings_notebook.add(basic_frame, text="Основные")

        # Тип содержимого
        tk.Label(basic_frame, text="Тип содержимого:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).pack(pady=(10, 5), anchor="w")

        self.content_type = ttk.Combobox(basic_frame,
                                         values=["URL", "Текст", "vCard", "WiFi", "Email", "SMS", "Биткоин"],
                                         font=self.app_font)
        self.content_type.set("URL")
        self.content_type.pack(fill="x", pady=(0, 15))
        self.content_type.bind("<<ComboboxSelected>>", self.functions.update_content_fields)

        # Поле ввода данных
        self.data_frame = tk.Frame(basic_frame, bg=self.card_color)
        self.data_frame.pack(fill="x", pady=(0, 15))

        tk.Label(self.data_frame, text="Содержимое:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).pack(anchor="w")
        self.data_entry = tk.Text(self.data_frame, height=4, bg="#252525", fg=self.text_color,
                                  insertbackground=self.text_color, wrap="word",
                                  font=self.small_font, bd=0, highlightthickness=1,
                                  highlightbackground="#404040", highlightcolor=self.accent_color)
        self.data_entry.pack(fill="x", pady=(5, 0))
        self.data_entry.insert("1.0", self.functions.settings["qr_data"])

        # Кнопка случайного QR
        random_btn = tk.Button(basic_frame, text="Случайный QR", bg="#252525", fg=self.text_color,
                               font=self.button_font, bd=0, command=self.functions.generate_random_qr)
        random_btn.pack(fill="x", pady=(0, 15))

        # Вкладка "Дополнительно"
        advanced_frame = tk.Frame(settings_notebook, bg=self.card_color)
        settings_notebook.add(advanced_frame, text="Дополнительно")

        # Коррекция ошибок
        tk.Label(advanced_frame, text="Коррекция ошибок:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).pack(pady=(10, 5), anchor="w")

        self.error_correction = ttk.Combobox(advanced_frame,
                                             values=["Низкая", "Средняя", "Высокая", "Максимальная"],
                                             font=self.app_font)
        self.error_correction.set("Высокая")
        self.error_correction.pack(fill="x", pady=(0, 15))

        # Версия QR
        tk.Label(advanced_frame, text="Версия QR (1-40):", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).pack(pady=(10, 5), anchor="w")

        self.version_entry = tk.Entry(advanced_frame, bg="#252525", fg=self.text_color,
                                      font=self.app_font, insertbackground=self.text_color,
                                      relief="flat", highlightthickness=1,
                                      highlightcolor=self.accent_color, highlightbackground="#404040")
        self.version_entry.insert(0, str(self.functions.settings["qr_version"]))
        self.version_entry.pack(fill="x", pady=(0, 15))

        settings_notebook.pack(fill="both", expand=True)

    def setup_preview_ui(self):
        # Заголовок
        tk.Label(self.preview_frame, text="Предпросмотр QR-кода", bg=self.card_color,
                 fg=self.text_color, font=self.title_font).pack(pady=(0, 15), anchor="w")

        # Область предпросмотра
        preview_container = tk.Frame(self.preview_frame, bg="#252525")
        preview_container.pack(fill="both", expand=True)

        # Холст для QR-кода
        self.qr_canvas = tk.Canvas(preview_container, bg="#252525", highlightthickness=0)
        self.qr_canvas.pack(fill="both", expand=True, padx=40, pady=40)

        # Информация о QR-коде
        info_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        info_frame.pack(fill="x", pady=(15, 0))

        self.qr_info = tk.Label(info_frame, text="Размер: - | Тип: - | Данные: -",
                                bg=self.card_color, fg=self.secondary_text, font=self.small_font)
        self.qr_info.pack(anchor="w")

        # Кнопки экспорта
        export_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        export_frame.pack(fill="x", pady=(15, 0))

        copy_btn = tk.Button(export_frame, text="Копировать", bg=self.accent_color, fg="#ffffff",
                             font=self.button_font, bd=0, command=self.functions.copy_to_clipboard)
        copy_btn.pack(side="left", fill="x", expand=True)

        export_btn = tk.Button(export_frame, text="Экспорт PNG", bg="#252525", fg=self.text_color,
                               font=self.button_font, bd=0, command=self.functions.export_png)
        export_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))

        export_svg_btn = tk.Button(export_frame, text="Экспорт SVG", bg="#252525", fg=self.text_color,
                                   font=self.button_font, bd=0, command=self.functions.export_svg)
        export_svg_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))

    def setup_scan_ui(self):
        # Очищаем предыдущие виджеты
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        # Обновляем заголовок
        self.section_title.config(text="Сканирование")

        # Панель загрузки изображения
        scan_frame = tk.Frame(self.settings_frame, bg=self.card_color, padx=15, pady=15)
        scan_frame.pack(fill="both", expand=True)

        tk.Label(scan_frame, text="Сканирование QR-кода", bg=self.card_color,
                 fg=self.text_color, font=self.title_font).pack(pady=(0, 20))

        load_btn = tk.Button(scan_frame, text="Загрузить изображение", bg=self.accent_color, fg="#ffffff",
                             font=self.button_font, bd=0, command=self.functions.load_image_for_scan)
        load_btn.pack(fill="x", pady=(0, 20))

        # Результаты сканирования
        tk.Label(scan_frame, text="Результат:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).pack(anchor="w", pady=(10, 5))

        self.scan_result = tk.Text(scan_frame, height=10, bg="#252525", fg=self.text_color,
                                   insertbackground=self.text_color, wrap="word",
                                   font=self.small_font, bd=0, highlightthickness=1,
                                   highlightbackground="#404040", highlightcolor=self.accent_color)
        self.scan_result.pack(fill="x")

        # Панель предпросмотра загруженного изображения
        tk.Label(self.preview_frame, text="Изображение для сканирования", bg=self.card_color,
                 fg=self.text_color, font=self.title_font).pack(pady=(0, 15), anchor="w")

        self.scan_image_frame = tk.Frame(self.preview_frame, bg="#252525")
        self.scan_image_frame.pack(fill="both", expand=True)

        self.scan_canvas = tk.Canvas(self.scan_image_frame, bg="#252525", highlightthickness=0)
        self.scan_canvas.pack(fill="both", expand=True, padx=40, pady=40)

    def show_section(self, section_name):
        self.current_section = section_name
        self.section_title.config(text=section_name)

        # Обновляем состояние кнопок навигации
        for btn in self.nav_buttons:
            if btn.cget("text") == section_name:
                btn.config(fg=self.accent_color)
            else:
                btn.config(fg=self.text_color)

        # Показываем соответствующий раздел
        if section_name == "Генератор QR":
            self.setup_generator_ui()
        elif section_name == "Сканирование":
            self.setup_scan_ui()

    def show_settings_tab(self, tab_name):
        self.current_settings_tab = tab_name

    def display_qr(self, img):
        # Очищаем холст
        self.qr_canvas.delete("all")

        # Конвертируем PIL Image в PhotoImage
        self.qr_image = ImageTk.PhotoImage(img)

        # Получаем размеры холста
        canvas_width = self.qr_canvas.winfo_width()
        canvas_height = self.qr_canvas.winfo_height()

        # Рассчитываем позицию для центрирования
        x = (canvas_width - self.qr_image.width()) // 2
        y = (canvas_height - self.qr_image.height()) // 2

        # Отображаем изображение
        self.qr_canvas.create_image(x, y, image=self.qr_image, anchor="nw")

    def display_scan_image(self, img):
        self.scan_canvas.delete("all")

        # Масштабируем изображение для отображения
        img.thumbnail((400, 400))
        self.scan_img_tk = ImageTk.PhotoImage(img)

        # Получаем размеры холста
        canvas_width = self.scan_canvas.winfo_width()
        canvas_height = self.scan_canvas.winfo_height()

        # Рассчитываем позицию для центрирования
        x = (canvas_width - self.scan_img_tk.width()) // 2
        y = (canvas_height - self.scan_img_tk.height()) // 2

        # Отображаем изображение
        self.scan_canvas.create_image(x, y, image=self.scan_img_tk, anchor="nw")