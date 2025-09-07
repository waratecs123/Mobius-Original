# [file name]: gui.py (обновленная версия)
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, font, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageFilter, ImageOps
import os
import numpy as np


class TextEffectEditorGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        # Цветовая палитра в стиле Fibonacci Scan
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#2d3748"
        self.highlight_color = "#4f46e5"

        # Шрифты
        self.title_font = ('Arial', 24, 'bold')
        self.subtitle_font = ('Arial', 16, 'bold')
        self.app_font = ('Arial', 12)
        self.button_font = ('Arial', 11, 'bold')
        self.small_font = ('Arial', 10)

        # Настройка стиля
        self.setup_styles()

        self.root.title("Michael Byte Text Editor")
        self.root.configure(bg=self.bg_color)
        self.root.minsize(1000, 700)

        # Create UI
        self.create_header()
        self.create_controls()
        self.create_preview()

    def setup_styles(self):
        """Настройка стилей элементов в стиле Fibonacci Scan"""
        style = ttk.Style()
        style.theme_use('clam')

        # Основные стили
        style.configure(".", background=self.bg_color, foreground=self.text_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_color, relief="flat", borderwidth=0)
        style.configure("TLabel", background=self.card_color, foreground=self.text_color, font=self.app_font)
        style.configure("Title.TLabel", font=self.title_font, foreground=self.accent_color)
        style.configure("Subtitle.TLabel", foreground=self.secondary_text, font=self.subtitle_font)

        # Стили кнопок
        style.configure("TButton", background=self.card_color, foreground=self.text_color,
                        font=self.button_font, borderwidth=0, focuscolor=self.card_color)
        style.map("TButton",
                  background=[('active', self.highlight_color), ('pressed', self.highlight_color)],
                  foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])

        # Акцентные кнопки
        style.configure("Accent.TButton", background=self.accent_color, foreground="#ffffff",
                        font=self.button_font, borderwidth=0)
        style.map("Accent.TButton",
                  background=[('active', self.highlight_color), ('pressed', self.highlight_color)],
                  foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])

        # Поля ввода и комбобоксы
        style.configure("TEntry", fieldbackground="#252525", foreground=self.text_color,
                        borderwidth=1, bordercolor=self.border_color, padding=8, focuscolor=self.accent_color)
        style.configure("TCombobox", fieldbackground="#252525", foreground=self.text_color,
                        selectbackground=self.accent_color, selectforeground="#ffffff",
                        borderwidth=1, bordercolor=self.border_color, padding=8)
        style.map('TCombobox', fieldbackground=[('readonly', '#252525')])
        style.map('TCombobox', selectbackground=[('readonly', self.accent_color)])

        # Слайдеры
        style.configure("Horizontal.TScale", background=self.card_color, troughcolor="#252525")

        # Notebook стили
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.card_color, foreground=self.secondary_text,
                        padding=[15, 5], font=self.button_font, borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[('selected', self.accent_color), ('active', self.highlight_color)],
                  foreground=[('selected', '#ffffff'), ('active', '#ffffff')])

    def create_header(self):
        # Header с кнопкой выхода
        header_frame = ttk.Frame(self.root, style="TFrame")
        header_frame.pack(fill="x", padx=20, pady=10)

        # Заголовок
        title_frame = ttk.Frame(header_frame, style="TFrame")
        title_frame.pack(side="left")

        tk.Label(title_frame, text="MICHAEL BYTE", font=('Arial', 28, 'bold'),
                 bg=self.bg_color, fg=self.accent_color).pack(side="left")
        tk.Label(title_frame, text="TEXT EDITOR", font=('Arial', 28, 'bold'),
                 bg=self.bg_color, fg=self.text_color).pack(side="left", padx=(5, 0))

        # Кнопка выхода из полноэкранного режима
        exit_fullscreen_btn = ttk.Button(header_frame, text="⤢", style="Accent.TButton",
                                         command=self.controller.toggle_fullscreen, width=3)
        exit_fullscreen_btn.pack(side="right", padx=(0, 10))

        # Кнопка выхода
        exit_btn = ttk.Button(header_frame, text="✕", style="Accent.TButton",
                              command=self.root.quit, width=3)
        exit_btn.pack(side="right")

    def create_controls(self):
        # Главный контейнер
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Основной контент
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(fill="both", expand=True)

        # Левая панель - инструменты
        left_panel = ttk.Frame(content_frame, style="TFrame", width=400)
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        left_panel.pack_propagate(False)

        # Правая панель - предпросмотр
        right_panel = ttk.Frame(content_frame, style="TFrame")
        right_panel.pack(side="right", fill="both", expand=True)

        # Создаем Notebook для вкладок с улучшенным стилем
        style = ttk.Style()
        style.configure("CustomNotebook.TNotebook", tabposition='n',
                        background=self.bg_color, borderwidth=0)
        style.configure("CustomNotebook.TNotebook.Tab",
                        padding=[20, 8], font=('Arial', 12, 'bold'))

        left_notebook = ttk.Notebook(left_panel, style="CustomNotebook.TNotebook")
        left_notebook.pack(fill="both", expand=True)

        # Вкладка с основными настройками
        basic_tab = ttk.Frame(left_notebook, style="Card.TFrame", padding=20)
        left_notebook.add(basic_tab, text="🎨 Основные")

        # Вкладка с эффектами
        effects_tab = ttk.Frame(left_notebook, style="Card.TFrame", padding=20)
        left_notebook.add(effects_tab, text="✨ Эффекты")

        # Вкладка с дополнительными настройками
        advanced_tab = ttk.Frame(left_notebook, style="Card.TFrame", padding=20)
        left_notebook.add(advanced_tab, text="⚙️ Дополнительно")

        # Заполняем вкладки
        self.create_basic_tab(basic_tab)
        self.create_effects_tab(effects_tab)
        self.create_advanced_tab(advanced_tab)

        # Кнопки экспорта внизу
        export_frame = ttk.Frame(left_panel, style="Card.TFrame", padding=15)
        export_frame.pack(fill="x", pady=(15, 0))

        ttk.Button(export_frame, text="📁 Экспорт PNG", style="Accent.TButton",
                   command=self.controller.export_png).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(export_frame, text="📁 Экспорт JPG", style="Accent.TButton",
                   command=self.controller.export_jpg).pack(side="left", fill="x", expand=True, padx=2)

    def create_basic_tab(self, parent):
        """Создает вкладку с основными настройками"""
        # Создаем Canvas для скроллинга
        canvas = tk.Canvas(parent, bg=self.card_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Card.TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем колесо мыши к canvas
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        tk.Label(scrollable_frame, text="Основные настройки", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 15))

        # Текст
        text_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        text_frame.pack(fill="x", pady=(0, 15))

        tk.Label(text_frame, text="Текст:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.text_var = tk.StringVar(value=self.controller.text_content)
        text_entry = ttk.Entry(text_frame, textvariable=self.text_var, font=self.app_font, style="TEntry")
        text_entry.pack(fill="x", pady=8)
        text_entry.bind("<KeyRelease>", lambda e: self.controller.update_preview())

        # Шрифт
        font_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        font_frame.pack(fill="x", pady=(0, 15))

        tk.Label(font_frame, text="Шрифт:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.font_var = tk.StringVar(value=self.controller.font_name)
        fonts = ['Arial', 'Times New Roman', 'Courier New', 'Verdana',
                 'Tahoma', 'Georgia', 'Impact', 'Comic Sans MS', 'Trebuchet MS']
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_var, values=fonts,
                                  style="TCombobox", state="readonly")
        font_combo.pack(fill="x", pady=8)
        font_combo.bind("<<ComboboxSelected>>", lambda e: self.controller.update_preview())

        # Размер шрифта
        size_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        size_frame.pack(fill="x", pady=(0, 15))

        tk.Label(size_frame, text="Размер:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.size_var = tk.IntVar(value=self.controller.font_size)
        size_scale = ttk.Scale(size_frame, from_=10, to=200, variable=self.size_var,
                               orient=tk.HORIZONTAL, style="Horizontal.TScale")
        size_scale.pack(fill="x", pady=8)
        size_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Цвет текста
        color_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        color_frame.pack(fill="x", pady=(0, 15))

        tk.Label(color_frame, text="Цвет текста:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        color_btn_frame = ttk.Frame(color_frame, style="Card.TFrame")
        color_btn_frame.pack(fill="x", pady=8)

        ttk.Button(color_btn_frame, text="Выбрать цвет", style="TButton",
                   command=lambda: self.controller.choose_color("text")).pack(side="left")

        self.controller.text_color_canvas = tk.Label(color_btn_frame, bg=self.controller.text_color,
                                                     width=3, height=1, relief="sunken", bd=1)
        self.controller.text_color_canvas.pack(side="left", padx=10)

        # Прозрачность
        alpha_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        alpha_frame.pack(fill="x", pady=(0, 15))

        tk.Label(alpha_frame, text="Прозрачность:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.opacity_var = tk.IntVar(value=self.controller.opacity)
        alpha_scale = ttk.Scale(alpha_frame, from_=0, to=100, variable=self.opacity_var,
                                orient=tk.HORIZONTAL, style="Horizontal.TScale")
        alpha_scale.pack(fill="x", pady=8)
        alpha_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Поворот
        rotation_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        rotation_frame.pack(fill="x", pady=(0, 15))

        tk.Label(rotation_frame, text="Поворот:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.rotation_var = tk.IntVar(value=self.controller.rotation)
        rotation_scale = ttk.Scale(rotation_frame, from_=-180, to=180, variable=self.rotation_var,
                                   orient=tk.HORIZONTAL, style="Horizontal.TScale")
        rotation_scale.pack(fill="x", pady=8)
        rotation_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

    def create_effects_tab(self, parent):
        """Создает вкладку с эффектами"""
        # Создаем Canvas для скроллинга
        canvas = tk.Canvas(parent, bg=self.card_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Card.TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем колесо мыши к canvas
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        tk.Label(scrollable_frame, text="Эффекты текста", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 15))

        # Обводка
        stroke_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        stroke_frame.pack(fill="x", pady=(0, 15))

        tk.Label(stroke_frame, text="Обводка:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        stroke_content_frame = ttk.Frame(stroke_frame, style="Card.TFrame")
        stroke_content_frame.pack(fill="x", pady=8)

        # Толщина обводки
        width_frame = ttk.Frame(stroke_content_frame, style="Card.TFrame")
        width_frame.pack(fill="x", pady=(0, 10))

        tk.Label(width_frame, text="Толщина:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.stroke_width_var = tk.IntVar(value=self.controller.stroke_width)
        stroke_scale = ttk.Scale(width_frame, from_=0, to=20, variable=self.stroke_width_var,
                                 orient=tk.HORIZONTAL, style="Horizontal.TScale")
        stroke_scale.pack(fill="x", pady=8)
        stroke_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Цвет обводки
        color_frame = ttk.Frame(stroke_content_frame, style="Card.TFrame")
        color_frame.pack(fill="x")

        tk.Label(color_frame, text="Цвет:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        color_btn_frame = ttk.Frame(color_frame, style="Card.TFrame")
        color_btn_frame.pack(fill="x", pady=8)

        ttk.Button(color_btn_frame, text="Выбрать цвет", style="TButton",
                   command=lambda: self.controller.choose_color("stroke")).pack(side="left")

        self.controller.stroke_color_canvas = tk.Label(color_btn_frame, bg=self.controller.stroke_color,
                                                       width=3, height=1, relief="sunken", bd=1)
        self.controller.stroke_color_canvas.pack(side="left", padx=10)

        # Тень
        shadow_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        shadow_frame.pack(fill="x", pady=(0, 15))

        tk.Label(shadow_frame, text="Тень:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        # Смещение тени
        offset_frame = ttk.Frame(shadow_frame, style="Card.TFrame")
        offset_frame.pack(fill="x", pady=(0, 10))

        tk.Label(offset_frame, text="Смещение:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.shadow_offset_var = tk.IntVar(value=self.controller.shadow_offset)
        offset_scale = ttk.Scale(offset_frame, from_=0, to=50, variable=self.shadow_offset_var,
                                 orient=tk.HORIZONTAL, style="Horizontal.TScale")
        offset_scale.pack(fill="x", pady=8)
        offset_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Размытие тени
        blur_frame = ttk.Frame(shadow_frame, style="Card.TFrame")
        blur_frame.pack(fill="x", pady=(0, 10))

        tk.Label(blur_frame, text="Размытие:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.shadow_blur_var = tk.IntVar(value=self.controller.shadow_blur)
        blur_scale = ttk.Scale(blur_frame, from_=0, to=20, variable=self.shadow_blur_var,
                               orient=tk.HORIZONTAL, style="Horizontal.TScale")
        blur_scale.pack(fill="x", pady=8)
        blur_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Цвет тени
        shadow_color_frame = ttk.Frame(shadow_frame, style="Card.TFrame")
        shadow_color_frame.pack(fill="x")

        tk.Label(shadow_color_frame, text="Цвет:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        shadow_color_btn_frame = ttk.Frame(shadow_color_frame, style="Card.TFrame")
        shadow_color_btn_frame.pack(fill="x", pady=8)

        ttk.Button(shadow_color_btn_frame, text="Выбрать цвет", style="TButton",
                   command=lambda: self.controller.choose_color("shadow")).pack(side="left")

        self.controller.shadow_color_canvas = tk.Label(shadow_color_btn_frame, bg=self.controller.shadow_color,
                                                       width=3, height=1, relief="sunken", bd=1)
        self.controller.shadow_color_canvas.pack(side="left", padx=10)

        # Свечение
        glow_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        glow_frame.pack(fill="x", pady=(0, 15))

        tk.Label(glow_frame, text="Свечение:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        # Интенсивность свечения
        intensity_frame = ttk.Frame(glow_frame, style="Card.TFrame")
        intensity_frame.pack(fill="x", pady=(0, 10))

        tk.Label(intensity_frame, text="Интенсивность:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.glow_intensity_var = tk.IntVar(value=self.controller.glow_intensity)
        intensity_scale = ttk.Scale(intensity_frame, from_=0, to=50, variable=self.glow_intensity_var,
                                    orient=tk.HORIZONTAL, style="Horizontal.TScale")
        intensity_scale.pack(fill="x", pady=8)
        intensity_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Цвет свечения
        glow_color_frame = ttk.Frame(glow_frame, style="Card.TFrame")
        glow_color_frame.pack(fill="x")

        tk.Label(glow_color_frame, text="Цвет:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        glow_color_btn_frame = ttk.Frame(glow_color_frame, style="Card.TFrame")
        glow_color_btn_frame.pack(fill="x", pady=8)

        ttk.Button(glow_color_btn_frame, text="Выбрать цвет", style="TButton",
                   command=lambda: self.controller.choose_color("glow")).pack(side="left")

        self.controller.glow_color_canvas = tk.Label(glow_color_btn_frame, bg=self.controller.glow_color,
                                                     width=3, height=1, relief="sunken", bd=1)
        self.controller.glow_color_canvas.pack(side="left", padx=10)

    def create_advanced_tab(self, parent):
        """Создает вкладку с дополнительными настройками"""
        # Создаем Canvas для скроллинга
        canvas = tk.Canvas(parent, bg=self.card_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Card.TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем колесо мыши к canvas
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        tk.Label(scrollable_frame, text="Дополнительные настройки", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 15))

        # Градиент
        gradient_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        gradient_frame.pack(fill="x", pady=(0, 15))

        tk.Label(gradient_frame, text="Градиент:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        # Начальный цвет градиента
        start_frame = ttk.Frame(gradient_frame, style="Card.TFrame")
        start_frame.pack(fill="x", pady=(0, 10))

        tk.Label(start_frame, text="Начальный цвет:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        start_color_btn_frame = ttk.Frame(start_frame, style="Card.TFrame")
        start_color_btn_frame.pack(fill="x", pady=8)

        ttk.Button(start_color_btn_frame, text="Выбрать цвет", style="TButton",
                   command=lambda: self.controller.choose_color("gradient_start")).pack(side="left")

        self.controller.gradient_start_canvas = tk.Label(start_color_btn_frame, bg=self.controller.gradient_start,
                                                         width=3, height=1, relief="sunken", bd=1)
        self.controller.gradient_start_canvas.pack(side="left", padx=10)

        # Конечный цвет градиента
        end_frame = ttk.Frame(gradient_frame, style="Card.TFrame")
        end_frame.pack(fill="x", pady=(0, 10))

        tk.Label(end_frame, text="Конечный цвет:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        end_color_btn_frame = ttk.Frame(end_frame, style="Card.TFrame")
        end_color_btn_frame.pack(fill="x", pady=8)

        ttk.Button(end_color_btn_frame, text="Выбрать цвет", style="TButton",
                   command=lambda: self.controller.choose_color("gradient_end")).pack(side="left")

        self.controller.gradient_end_canvas = tk.Label(end_color_btn_frame, bg=self.controller.gradient_end,
                                                       width=3, height=1, relief="sunken", bd=1)
        self.controller.gradient_end_canvas.pack(side="left", padx=10)

        # Направление градиента
        dir_frame = ttk.Frame(gradient_frame, style="Card.TFrame")
        dir_frame.pack(fill="x", pady=(0, 10))

        tk.Label(dir_frame, text="Направление:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.gradient_dir_var = tk.StringVar(value="horizontal")
        dir_combo = ttk.Combobox(dir_frame, textvariable=self.gradient_dir_var,
                                 values=["horizontal", "vertical", "diagonal"],
                                 style="TCombobox", state="readonly")
        dir_combo.pack(fill="x", pady=8)
        dir_combo.bind("<<ComboboxSelected>>", lambda e: self.controller.update_preview())

        # Фон
        bg_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        bg_frame.pack(fill="x", pady=(0, 15))

        tk.Label(bg_frame, text="Фон:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        bg_btn_frame = ttk.Frame(bg_frame, style="Card.TFrame")
        bg_btn_frame.pack(fill="x", pady=8)

        ttk.Button(bg_btn_frame, text="Выбрать цвет фона", style="TButton",
                   command=self.controller.choose_bg_color).pack(side="left")

        transparent_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bg_btn_frame, text="Прозрачный", variable=transparent_var,
                        style="TCheckbutton", command=lambda: self.controller.update_preview()).pack(side="left",
                                                                                                     padx=10)

        # Эффекты
        effects_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        effects_frame.pack(fill="x", pady=(0, 15))

        tk.Label(effects_frame, text="Дополнительные эффекты:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        # Эффект тиснения
        emboss_frame = ttk.Frame(effects_frame, style="Card.TFrame")
        emboss_frame.pack(fill="x", pady=(0, 10))

        tk.Label(emboss_frame, text="Тиснение:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.emboss_var = tk.IntVar(value=0)
        emboss_scale = ttk.Scale(emboss_frame, from_=0, to=10, variable=self.emboss_var,
                                 orient=tk.HORIZONTAL, style="Horizontal.TScale")
        emboss_scale.pack(fill="x", pady=8)
        emboss_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Эффект текстура
        texture_frame = ttk.Frame(effects_frame, style="Card.TFrame")
        texture_frame.pack(fill="x", pady=(0, 10))

        tk.Label(texture_frame, text="Текстура:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.texture_var = tk.IntVar(value=0)
        texture_scale = ttk.Scale(texture_frame, from_=0, to=10, variable=self.texture_var,
                                  orient=tk.HORIZONTAL, style="Horizontal.TScale")
        texture_scale.pack(fill="x", pady=8)
        texture_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Искажение перспективы
        perspective_frame = ttk.Frame(effects_frame, style="Card.TFrame")
        perspective_frame.pack(fill="x", pady=(0, 10))

        tk.Label(perspective_frame, text="Перспектива:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.perspective_var = tk.IntVar(value=0)
        perspective_scale = ttk.Scale(perspective_frame, from_=0, to=10, variable=self.perspective_var,
                                      orient=tk.HORIZONTAL, style="Horizontal.TScale")
        perspective_scale.pack(fill="x", pady=8)
        perspective_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Волновое искажение
        wave_frame = ttk.Frame(effects_frame, style="Card.TFrame")
        wave_frame.pack(fill="x", pady=(0, 10))

        tk.Label(wave_frame, text="Волна:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.wave_var = tk.IntVar(value=0)
        wave_scale = ttk.Scale(wave_frame, from_=0, to=10, variable=self.wave_var,
                               orient=tk.HORIZONTAL, style="Horizontal.TScale")
        wave_scale.pack(fill="x", pady=8)
        wave_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Масштаб
        zoom_frame = ttk.Frame(effects_frame, style="Card.TFrame")
        zoom_frame.pack(fill="x", pady=(0, 10))

        tk.Label(zoom_frame, text="Масштаб:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.zoom_var = tk.DoubleVar(value=1.0)
        zoom_scale = ttk.Scale(zoom_frame, from_=0.5, to=3.0, variable=self.zoom_var,
                               orient=tk.HORIZONTAL, style="Horizontal.TScale")
        zoom_scale.pack(fill="x", pady=8)
        zoom_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

    def create_preview(self):
        """Создает область предпросмотра"""
        preview_container = ttk.Frame(self.root, style="Card.TFrame", padding=20)
        preview_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tk.Label(preview_container, text="Предпросмотр", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 15))

        # Canvas для предпросмотра с прокруткой
        preview_canvas_frame = ttk.Frame(preview_container, style="Card.TFrame")
        preview_canvas_frame.pack(fill="both", expand=True)

        # Создаем Canvas с прокруткой
        canvas = tk.Canvas(preview_canvas_frame, bg="#252525", highlightthickness=0)
        h_scrollbar = ttk.Scrollbar(preview_canvas_frame, orient="horizontal", command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(preview_canvas_frame, orient="vertical", command=canvas.yview)

        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        # Размещаем элементы
        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        preview_canvas_frame.grid_rowconfigure(0, weight=1)
        preview_canvas_frame.grid_columnconfigure(0, weight=1)

        # Привязываем колесо мыши к canvas
        canvas.bind("<MouseWheel>", self.controller.on_mousewheel)

        # Сохраняем ссылку на canvas в контроллере
        self.controller.preview_canvas = canvas

    def get_vars(self):
        """Возвращает словарь с переменными UI"""
        return {
            'text_var': getattr(self, 'text_var', None),
            'font_var': getattr(self, 'font_var', None),
            'size_var': getattr(self, 'size_var', None),
            'opacity_var': getattr(self, 'opacity_var', None),
            'rotation_var': getattr(self, 'rotation_var', None),
            'stroke_width_var': getattr(self, 'stroke_width_var', None),
            'shadow_offset_var': getattr(self, 'shadow_offset_var', None),
            'shadow_blur_var': getattr(self, 'shadow_blur_var', None),
            'glow_intensity_var': getattr(self, 'glow_intensity_var', None),
            'gradient_dir_var': getattr(self, 'gradient_dir_var', None),
            'emboss_var': getattr(self, 'emboss_var', None),
            'texture_var': getattr(self, 'texture_var', None),
            'perspective_var': getattr(self, 'perspective_var', None),
            'wave_var': getattr(self, 'wave_var', None),
            'zoom_var': getattr(self, 'zoom_var', None)
        }