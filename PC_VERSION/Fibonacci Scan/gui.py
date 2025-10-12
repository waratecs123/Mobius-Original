import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from functions import QRCodeFunctions

class FibonacciScanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fibonacci Scan")
        self.functions = QRCodeFunctions(self)

        self.root.attributes('-fullscreen', True)

        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.secondary_accent = "#818cf8"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#0f0f23"
        self.success_color = "#10b981"
        self.warning_color = "#f59e0b"

        self.gradient_start = "#6366f1"
        self.gradient_end = "#8b5cf6"

        self.title_font = ('Arial', 24, 'bold')
        self.subtitle_font = ('Arial', 16)
        self.app_font = ('Arial', 13)
        self.button_font = ('Arial', 12, 'bold')
        self.small_font = ('Arial', 11)
        self.mono_font = ('Courier New', 10)

        self.current_section = "Генератор QR"
        self.zoom_factor = 1.0

        self.setup_ui()
        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Custom.TNotebook', background=self.card_color, borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                        background="#1a1a2e",
                        foreground=self.text_color,
                        padding=[15, 8],
                        font=self.small_font)
        style.map('Custom.TNotebook.Tab',
                  background=[('selected', self.card_color)],
                  foreground=[('selected', self.accent_color)])

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

        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        content_wrapper = tk.Frame(main_container, bg=self.bg_color)
        content_wrapper.pack(fill="both", expand=True, pady=(20, 0))

        self.setup_sidebar(content_wrapper)
        self.setup_main_area(content_wrapper)
        self.show_section(self.current_section)

    def setup_app_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.bg_color, height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)

        gradient_canvas = tk.Canvas(header_frame, bg=self.bg_color, highlightthickness=0)
        gradient_canvas.pack(fill="both", expand=True)

        width = header_frame.winfo_reqwidth()
        for i in range(width):
            ratio = i / width
            r = int(int(self.gradient_start[1:3], 16) * (1 - ratio) + int(self.gradient_end[1:3], 16) * ratio)
            g = int(int(self.gradient_start[3:5], 16) * (1 - ratio) + int(self.gradient_end[3:5], 16) * ratio)
            b = int(int(self.gradient_start[5:7], 16) * (1 - ratio) + int(self.gradient_end[5:7], 16) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            gradient_canvas.create_line(i, 0, i, 80, fill=color)

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

        top_sidebar = tk.Frame(sidebar, bg=self.card_color)
        top_sidebar.pack(fill="x", pady=(20, 30), padx=20)

        logo_frame = tk.Frame(top_sidebar, bg=self.card_color)
        logo_frame.pack(fill="x", pady=(0, 30))

        icon_label = tk.Label(logo_frame, text="🔷", bg=self.card_color,
                              fg=self.accent_color, font=('Arial', 32))
        icon_label.pack(side="left", padx=(0, 10))

        name_frame = tk.Frame(logo_frame, bg=self.card_color)
        name_frame.pack(side="left", fill="y")

        tk.Label(name_frame, text="FIBONACCI", bg=self.card_color,
                 fg=self.accent_color, font=('Arial', 18, 'bold')).pack(anchor="w")
        tk.Label(name_frame, text="SCAN", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 18, 'bold')).pack(anchor="w")

        separator = tk.Frame(top_sidebar, height=2, bg=self.border_color)
        separator.pack(fill="x", pady=(0, 20))

        nav_frame = tk.Frame(top_sidebar, bg=self.card_color)
        nav_frame.pack(fill="x")

        nav_items = [
            ("Генератор QR", "", ""),
            ("Сканирование", "", ""),
            ("История", "", "")
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

            desc_label = tk.Label(btn_container, text=description,
                                  bg=self.card_color, fg=self.secondary_text,
                                  font=('Arial', 9), anchor="w", justify="left")
            desc_label.pack(fill="x", padx=(45, 0), pady=(2, 0))

            self.nav_buttons.append(btn)

        bottom_sidebar = tk.Frame(sidebar, bg=self.card_color)
        bottom_sidebar.pack(side="bottom", fill="x", pady=20, padx=20)

        stats_frame = tk.Frame(bottom_sidebar, bg=self.card_color)
        stats_frame.pack(fill="x", pady=(0, 15))

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

        self.header_frame = tk.Frame(self.main_area, bg=self.bg_color)
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.section_title = tk.Label(self.header_frame, text=self.current_section,
                                      bg=self.bg_color, fg=self.text_color, font=self.title_font)
        self.section_title.pack(side="left")

        indicator = tk.Frame(self.header_frame, height=3, bg=self.accent_color, width=100)
        indicator.pack(side="left", padx=(15, 0), pady=(5, 0))

        self.content_frame = tk.Frame(self.main_area, bg=self.bg_color)
        self.content_frame.pack(fill="both", expand=True)

        self.preview_frame = tk.Frame(self.content_frame, bg=self.card_color,
                                      padx=25, pady=25)
        self.preview_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))

        self.settings_frame = tk.Frame(self.content_frame, bg=self.card_color,
                                       width=400, padx=25, pady=25)
        self.settings_frame.pack(side="left", fill="y")
        self.settings_frame.pack_propagate(False)

    def setup_generator_ui(self):
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        self.section_title.config(text="Генератор QR-кодов")
        self.setup_generator_settings()
        self.setup_preview_ui()

    def setup_generator_settings(self):
        settings_container = tk.Frame(self.settings_frame, bg=self.card_color)
        settings_container.pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure("Custom.TNotebook.Tab", padding=[20, 8], font=self.small_font)

        settings_notebook = ttk.Notebook(settings_container, style="Custom.TNotebook")

        design_frame = tk.Frame(settings_notebook, bg=self.card_color)
        settings_notebook.add(design_frame, text="Дизайн")

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

        basic_frame = tk.Frame(settings_notebook, bg=self.card_color)
        settings_notebook.add(basic_frame, text="Основные")

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

        data_frame = tk.Frame(basic_frame, bg=self.card_color)
        data_frame.pack(fill="x", pady=(0, 20))

        tk.Label(data_frame, text="СОДЕРЖИМОЕ", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        self.data_entry = tk.Text(data_frame, height=8, bg="#2D3748", fg=self.text_color,
                                  insertbackground=self.text_color, wrap="word",
                                  font=self.small_font, bd=1, relief="flat")
        self.data_entry.pack(fill="x")
        self.data_entry.insert("1.0", self.functions.settings["qr_data"])

        advanced_frame = tk.Frame(settings_notebook, bg=self.card_color)
        settings_notebook.add(advanced_frame, text="Дополнительно")

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
        title_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        title_frame.pack(fill="x", pady=(0, 20))

        tk.Label(title_frame, text="ПРЕДПРОСМОТР", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 16, 'bold')).pack(side="left")

        preview_container = tk.Frame(self.preview_frame, bg="#1a1a2e", relief="raised", bd=1)
        preview_container.pack(fill="both", expand=True)

        self.qr_canvas = tk.Canvas(preview_container, bg="#1a1a2e", highlightthickness=0)
        self.qr_canvas.pack(fill="both", expand=True, padx=40, pady=40)

        self.qr_canvas.bind("<MouseWheel>", self.zoom_qr)

        info_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        info_frame.pack(fill="x", pady=(20, 0))

        self.qr_info = tk.Label(info_frame, text="Готов к генерации...",
                                bg=self.card_color, fg=self.secondary_text,
                                font=self.small_font, justify="left")
        self.qr_info.pack(anchor="w")

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
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        self.section_title.config(text="Сканирование QR-кодов")

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

        self.webcam_btn = tk.Button(scan_frame, text="Сканировать с веб-камеры",
                                    bg=self.secondary_accent, fg="white",
                                    font=self.button_font, bd=0,
                                    command=self.functions.scan_from_webcam,
                                    padx=20, pady=12)
        self.webcam_btn.pack(fill="x", pady=(0, 20))

        self.scan_status = tk.Label(scan_frame, text="Ожидание загрузки изображения...",
                                    bg=self.card_color, fg=self.secondary_text,
                                    font=self.small_font)
        self.scan_status.pack(anchor="w", pady=(0, 10))

        result_frame = tk.Frame(scan_frame, bg=self.card_color)
        result_frame.pack(fill="both", expand=True)

        tk.Label(result_frame, text="РЕЗУЛЬТАТ СКАНИРОВАНИЯ:", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))

        result_container = tk.Frame(result_frame, bg="#1a1a2e", relief="sunken", bd=1)
        result_container.pack(fill="both", expand=True)

        self.scan_result = tk.Text(result_container, height=15, bg="#1a1a2e", fg=self.text_color,
                                   insertbackground=self.text_color, wrap="word",
                                   font=self.mono_font, bd=0, relief="flat")

        scrollbar = ttk.Scrollbar(result_container, orient="vertical", command=self.scan_result.yview)
        self.scan_result.configure(yscrollcommand=scrollbar.set)

        self.scan_result.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        preview_title_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        preview_title_frame.pack(fill="x", pady=(0, 20))

        tk.Label(preview_title_frame, text="ПРЕДПРОСМОТР ИЗОБРАЖЕНИЯ", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 16, 'bold')).pack(side="left")

        self.scan_image_frame = tk.Frame(self.preview_frame, bg="#1a1a2e", relief="raised", bd=1)
        self.scan_image_frame.pack(fill="x", expand=False)

        self.scan_canvas = tk.Canvas(self.scan_image_frame, bg="#1a1a2e", highlightthickness=0, height=300)
        self.scan_canvas.pack(fill="x", padx=40, pady=20)

        self.qr_detected_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        self.qr_detected_frame.pack(fill="x", pady=(10, 0))

        tk.Label(self.qr_detected_frame, text="ОТСКАНИРОВАННЫЙ QR-КОД", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 10))

        self.qr_detected_canvas = tk.Canvas(self.qr_detected_frame, bg="#1a1a2e", highlightthickness=0, height=200)
        self.qr_detected_canvas.pack(fill="x", padx=40)

        image_info_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        image_info_frame.pack(fill="x", pady=(20, 0))

        self.image_info = tk.Label(image_info_frame, text="Размер: - | Формат: -",
                                   bg=self.card_color, fg=self.secondary_text,
                                   font=self.small_font)
        self.image_info.pack(anchor="w")

    def setup_history_ui(self):
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        self.section_title.config(text="История (последние 15)")

        history_frame = tk.Frame(self.settings_frame, bg=self.card_color)
        history_frame.pack(fill="both", expand=True)

        tk.Label(history_frame, text="ИСТОРИЯ", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 16, 'bold')).pack(pady=(0, 20))

        self.history_listbox = tk.Listbox(history_frame, bg="#1a1a2e", fg=self.text_color,
                                          font=self.small_font, selectmode=tk.SINGLE)
        self.history_listbox.pack(fill="both", expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self.show_history_item)

        preview_title_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        preview_title_frame.pack(fill="x", pady=(0, 20))

        tk.Label(preview_title_frame, text="ПРЕДПРОСМОТР ИСТОРИИ", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 16, 'bold')).pack(side="left")

        self.history_canvas = tk.Canvas(self.preview_frame, bg="#1a1a2e", highlightthickness=0)
        self.history_canvas.pack(fill="both", expand=True, padx=40, pady=40)

        self.history_info = tk.Label(self.preview_frame, text="Выберите элемент из истории",
                                     bg=self.card_color, fg=self.secondary_text,
                                     font=self.small_font, justify="left")
        self.history_info.pack(anchor="w", pady=(20, 0))

        self.update_history_ui()

    def update_history_ui(self):
        if hasattr(self, 'history_listbox'):
            self.history_listbox.delete(0, tk.END)
            for idx, entry in enumerate(reversed(self.functions.history)):
                item_text = f"{entry['type'].capitalize()}: {entry['data'][:30]}..."
                self.history_listbox.insert(tk.END, item_text)

    def show_history_item(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            entry = self.functions.history[len(self.functions.history) - 1 - idx]
            self.history_canvas.delete("all")
            if entry.get('img'):
                img = entry['img'].copy()
                img.thumbnail((300, 300))
                self.history_img_tk = ImageTk.PhotoImage(img)
                canvas_width = self.history_canvas.winfo_width()
                canvas_height = self.history_canvas.winfo_height()
                x = (canvas_width - self.history_img_tk.width()) // 2
                y = (canvas_height - self.history_img_tk.height()) // 2
                self.history_canvas.create_image(x, y, image=self.history_img_tk, anchor="nw")
            self.history_info.config(text=f"Тип: {entry['type']} | Данные: {entry['data'][:50]}...")

    def show_section(self, section_name):
        if self.functions.webcam_active:
            self.functions.stop_webcam()
        self.current_section = section_name
        display_name = {
            "Генератор QR": "Генератор QR-кодов",
            "Сканирование": "Сканирование QR-кодов",
            "История": "История"
        }.get(section_name, section_name)
        self.section_title.config(text=display_name)

        for btn in self.nav_buttons:
            if section_name in btn.cget("text"):
                btn.config(fg=self.accent_color, bg="#1a1a2e")
            else:
                btn.config(fg=self.secondary_text, bg=self.card_color)

        if section_name == "Генератор QR":
            self.setup_generator_ui()
        elif section_name == "Сканирование":
            self.setup_scan_ui()
        elif section_name == "История":
            self.setup_history_ui()

    def display_qr(self, img):
        self.qr_canvas.delete("all")
        new_size = (int(img.width * self.zoom_factor), int(img.height * self.zoom_factor))
        zoomed_img = img.resize(new_size, Image.LANCZOS)
        self.qr_image = ImageTk.PhotoImage(zoomed_img)

        canvas_width = self.qr_canvas.winfo_width()
        canvas_height = self.qr_canvas.winfo_height()

        x = (canvas_width - self.qr_image.width()) // 2
        y = (canvas_height - self.qr_image.height()) // 2

        self.qr_canvas.create_image(x, y, image=self.qr_image, anchor="nw")

    def zoom_qr(self, event):
        if event.delta > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
        self.zoom_factor = max(0.5, min(self.zoom_factor, 3.0))
        if self.functions.current_qr:
            self.display_qr(self.functions.current_qr)

    def display_scan_image(self, img):
        self.scan_canvas.delete("all")
        img.thumbnail((400, 400))
        self.scan_img_tk = ImageTk.PhotoImage(img)

        canvas_width = self.scan_canvas.winfo_width()
        canvas_height = self.scan_canvas.winfo_height()

        x = (canvas_width - self.scan_img_tk.width()) // 2
        y = (canvas_height - self.scan_img_tk.height()) // 2

        self.scan_canvas.create_image(x, y, image=self.scan_img_tk, anchor="nw")

    def display_webcam_feed(self, img):
        self.scan_canvas.delete("all")
        img.thumbnail((400, 400))
        self.webcam_img_tk = ImageTk.PhotoImage(img)

        canvas_width = self.scan_canvas.winfo_width()
        canvas_height = self.scan_canvas.winfo_height()

        x = (canvas_width - self.webcam_img_tk.width()) // 2
        y = (canvas_height - self.webcam_img_tk.height()) // 2

        self.scan_canvas.create_image(x, y, image=self.webcam_img_tk, anchor="nw")

    def clear_webcam_feed(self):
        self.scan_canvas.delete("all")
        self.qr_detected_canvas.delete("all")

    def display_detected_qr(self, img):
        self.qr_detected_canvas.delete("all")
        img.thumbnail((200, 200))
        self.qr_detected_img_tk = ImageTk.PhotoImage(img)

        canvas_width = self.qr_detected_canvas.winfo_width()
        canvas_height = self.qr_detected_canvas.winfo_height()

        x = (canvas_width - self.qr_detected_img_tk.width()) // 2
        y = (canvas_height - self.qr_detected_img_tk.height()) // 2

        self.qr_detected_canvas.create_image(x, y, image=self.qr_detected_img_tk, anchor="nw")

    def update_scan_status(self, message, is_success=True):
        color = self.success_color if is_success else self.warning_color
        self.scan_status.config(text=message, fg=color)

    def update_image_info(self, width, height, format_name):
        self.image_info.config(text=f"Размер: {width}x{height}px | Формат: {format_name}")