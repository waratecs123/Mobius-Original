import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, font, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageFilter, ImageOps
import os
import numpy as np


class TextEffectEditorGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        # Цветовая палитра в стиле Picasso Art
        self.bg_color = "#0a0a0a"
        self.card_color = "#1e1e1e"
        self.accent_color = "#8844FF"
        self.text_color = "#f0f0f0"
        self.secondary_text = "#909090"
        self.border_color = "#2a2a2a"

        # Шрифты
        self.title_font = ('Segoe UI', 16, 'bold')
        self.subtitle_font = ('Segoe UI', 12, 'bold')
        self.app_font = ('Segoe UI', 10)
        self.button_font = ('Segoe UI', 10)

        # Настройка стиля
        self.setup_styles()

        self.root.title("Michael Byte Text Editor")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.bg_color)
        self.root.minsize(1000, 700)

        # Create UI
        self.create_controls()
        self.create_preview()

    def setup_styles(self):
        """Настройка стилей элементов в стиле Picasso Art"""
        style = ttk.Style()
        style.theme_use('clam')

        # Основные стили
        style.configure(".", background=self.bg_color, foreground=self.text_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_color)
        style.configure("TLabel", background=self.card_color, foreground=self.text_color, font=self.app_font)
        style.configure("Title.TLabel", font=self.title_font)
        style.configure("Subtitle.TLabel", foreground=self.secondary_text, font=self.subtitle_font)

        # Стили кнопок
        style.configure("TButton", background=self.card_color, foreground=self.text_color,
                        font=self.button_font, borderwidth=0)
        style.map("TButton", background=[('active', '#252525')])

        # Акцентные кнопки
        style.configure("Accent.TButton", background=self.accent_color, foreground="#ffffff",
                        font=self.button_font, borderwidth=0)
        style.map("Accent.TButton", background=[('active', '#ff3a7c')])

        # Поля ввода и комбобоксы
        style.configure("TEntry", fieldbackground="#252525", foreground=self.text_color,
                        borderwidth=1, bordercolor=self.border_color, padding=5)
        style.configure("TCombobox", fieldbackground="#252525", foreground=self.text_color,
                        selectbackground=self.accent_color, selectforeground="#ffffff",
                        borderwidth=1, bordercolor=self.border_color, padding=5)

        # Слайдеры
        style.configure("Horizontal.TScale", background=self.card_color, troughcolor="#252525")

    def create_controls(self):
        # Главный контейнер
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        header_frame = ttk.Frame(main_container, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 15))

        tk.Label(header_frame, text="ТЕКСТОВЫЙ РЕДАКТОР", font=self.title_font,
                 bg=self.bg_color, fg=self.text_color).pack(side="left")

        # Основной контент
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(fill="both", expand=True)

        # Левая панель - инструменты
        left_panel = ttk.Frame(content_frame, style="TFrame", width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        left_panel.pack_propagate(False)

        # Правая панель - предпросмотр
        right_panel = ttk.Frame(content_frame, style="TFrame")
        right_panel.pack(side="right", fill="both", expand=True)

        # Создаем Notebook для вкладок
        left_notebook = ttk.Notebook(left_panel)
        left_notebook.pack(fill="both", expand=True)

        # Вкладка с основными настройками
        basic_tab = ttk.Frame(left_notebook, style="Card.TFrame", padding=15)
        left_notebook.add(basic_tab, text="Основные")

        # Вкладка с эффектами
        effects_tab = ttk.Frame(left_notebook, style="Card.TFrame", padding=15)
        left_notebook.add(effects_tab, text="Эффекты")

        # Заполняем вкладку основных настроек
        self.create_basic_tab(basic_tab)

        # Заполняем вкладку эффектов
        self.create_effects_tab(effects_tab)

        # Кнопки экспорта внизу
        export_frame = ttk.Frame(left_panel, style="Card.TFrame", padding=10)
        export_frame.pack(fill="x", pady=(15, 0))

        ttk.Button(export_frame, text="Экспорт PNG", style="Accent.TButton",
                  command=self.controller.export_png).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(export_frame, text="Экспорт JPG", style="Accent.TButton",
                  command=self.controller.export_jpg).pack(side="left", fill="x", expand=True, padx=2)

    def create_basic_tab(self, parent):
        """Создает вкладку с основными настройками"""
        tk.Label(parent, text="Основные настройки", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 15))

        # Текст
        text_frame = ttk.Frame(parent, style="Card.TFrame")
        text_frame.pack(fill="x", pady=(0, 15))

        tk.Label(text_frame, text="Текст:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.text_var = tk.StringVar(value=self.controller.text_content)
        text_entry = ttk.Entry(text_frame, textvariable=self.text_var, font=self.app_font, style="TEntry")
        text_entry.pack(fill="x", pady=5)
        text_entry.bind("<KeyRelease>", lambda e: self.controller.update_preview())

        # Шрифт
        font_frame = ttk.Frame(parent, style="Card.TFrame")
        font_frame.pack(fill="x", pady=(0, 15))

        tk.Label(font_frame, text="Шрифт:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.font_var = tk.StringVar(value=self.controller.font_name)
        fonts = ['Arial', 'Times New Roman', 'Courier New', 'Verdana',
                'Tahoma', 'Georgia', 'Impact']
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_var, values=fonts,
                                 style="TCombobox", state="readonly")
        font_combo.pack(fill="x", pady=5)
        font_combo.bind("<<ComboboxSelected>>", lambda e: self.controller.update_preview())

        # Размер шрифта
        size_frame = ttk.Frame(parent, style="Card.TFrame")
        size_frame.pack(fill="x", pady=(0, 15))

        tk.Label(size_frame, text="Размер:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.size_var = tk.IntVar(value=self.controller.font_size)
        size_scale = ttk.Scale(size_frame, from_=10, to=200, variable=self.size_var,
                              orient=tk.HORIZONTAL, style="Horizontal.TScale")
        size_scale.pack(fill="x", pady=5)
        size_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Цвет текста
        color_frame = ttk.Frame(parent, style="Card.TFrame")
        color_frame.pack(fill="x", pady=(0, 15))

        tk.Label(color_frame, text="Цвет текста:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        color_btn_frame = ttk.Frame(color_frame, style="Card.TFrame")
        color_btn_frame.pack(fill="x", pady=5)

        ttk.Button(color_btn_frame, text="Выбрать цвет", style="TButton",
                  command=lambda: self.controller.choose_color("text")).pack(side="left")

        self.controller.text_color_canvas = tk.Label(color_btn_frame, bg=self.controller.text_color,
                                                   width=3, height=1, relief="sunken", bd=1)
        self.controller.text_color_canvas.pack(side="left", padx=10)

        # Прозрачность
        alpha_frame = ttk.Frame(parent, style="Card.TFrame")
        alpha_frame.pack(fill="x", pady=(0, 15))

        tk.Label(alpha_frame, text="Прозрачность:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.opacity_var = tk.IntVar(value=self.controller.opacity)
        alpha_scale = ttk.Scale(alpha_frame, from_=0, to=100, variable=self.opacity_var,
                               orient=tk.HORIZONTAL, style="Horizontal.TScale")
        alpha_scale.pack(fill="x", pady=5)
        alpha_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Поворот
        rotation_frame = ttk.Frame(parent, style="Card.TFrame")
        rotation_frame.pack(fill="x", pady=(0, 15))

        tk.Label(rotation_frame, text="Поворот:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.rotation_var = tk.IntVar(value=self.controller.rotation)
        rotation_scale = ttk.Scale(rotation_frame, from_=-180, to=180, variable=self.rotation_var,
                                  orient=tk.HORIZONTAL, style="Horizontal.TScale")
        rotation_scale.pack(fill="x", pady=5)
        rotation_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

    def create_effects_tab(self, parent):
        """Создает вкладку с эффектами"""
        tk.Label(parent, text="Эффекты текста", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 15))

        # Обводка
        stroke_frame = ttk.Frame(parent, style="Card.TFrame")
        stroke_frame.pack(fill="x", pady=(0, 15))

        tk.Label(stroke_frame, text="Обводка:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        stroke_content_frame = ttk.Frame(stroke_frame, style="Card.TFrame")
        stroke_content_frame.pack(fill="x", pady=5)

        # Толщина обводки
        width_frame = ttk.Frame(stroke_content_frame, style="Card.TFrame")
        width_frame.pack(fill="x", pady=(0, 10))

        tk.Label(width_frame, text="Толщина:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.stroke_width_var = tk.IntVar(value=self.controller.stroke_width)
        stroke_scale = ttk.Scale(width_frame, from_=0, to=20, variable=self.stroke_width_var,
                                orient=tk.HORIZONTAL, style="Horizontal.TScale")
        stroke_scale.pack(fill="x", pady=5)
        stroke_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Цвет обводки
        color_frame = ttk.Frame(stroke_content_frame, style="Card.TFrame")
        color_frame.pack(fill="x")

        tk.Label(color_frame, text="Цвет:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        color_btn_frame = ttk.Frame(color_frame, style="Card.TFrame")
        color_btn_frame.pack(fill="x", pady=5)

        ttk.Button(color_btn_frame, text="Выбрать цвет", style="TButton",
                  command=lambda: self.controller.choose_color("stroke")).pack(side="left")

        self.controller.stroke_color_canvas = tk.Label(color_btn_frame, bg=self.controller.stroke_color,
                                                     width=3, height=1, relief="sunken", bd=1)
        self.controller.stroke_color_canvas.pack(side="left", padx=10)

        # Тень
        shadow_frame = ttk.Frame(parent, style="Card.TFrame")
        shadow_frame.pack(fill="x", pady=(0, 15))

        tk.Label(shadow_frame, text="Тень:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        shadow_content_frame = ttk.Frame(shadow_frame, style="Card.TFrame")
        shadow_content_frame.pack(fill="x", pady=5)

        # Смещение тени
        offset_frame = ttk.Frame(shadow_content_frame, style="Card.TFrame")
        offset_frame.pack(fill="x", pady=(0, 10))

        tk.Label(offset_frame, text="Смещение:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.shadow_offset_var = tk.IntVar(value=self.controller.shadow_offset)
        offset_scale = ttk.Scale(offset_frame, from_=0, to=30, variable=self.shadow_offset_var,
                                orient=tk.HORIZONTAL, style="Horizontal.TScale")
        offset_scale.pack(fill="x", pady=5)
        offset_scale.bind("<ButtonRelease-1>", lambda e: self.controller.update_preview())

        # Цвет тени
        shadow_color_frame = ttk.Frame(shadow_content_frame, style="Card.TFrame")
        shadow_color_frame.pack(fill="x")

        tk.Label(shadow_color_frame, text="Цвет тени:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        shadow_color_btn_frame = ttk.Frame(shadow_color_frame, style="Card.TFrame")
        shadow_color_btn_frame.pack(fill="x", pady=5)

        ttk.Button(shadow_color_btn_frame, text="Выбрать цвет", style="TButton",
                  command=lambda: self.controller.choose_color("shadow")).pack(side="left")

        self.controller.shadow_color_canvas = tk.Label(shadow_color_btn_frame, bg=self.controller.shadow_color,
                                                     width=3, height=1, relief="sunken", bd=1)
        self.controller.shadow_color_canvas.pack(side="left", padx=10)

    def create_preview(self):
        """Создает область предпросмотра"""
        # Правая панель из main_container
        main_container = self.root.winfo_children()[0].winfo_children()[1]
        right_panel = main_container.winfo_children()[1]

        # Холст для предпросмотра
        preview_card = ttk.Frame(right_panel, style="Card.TFrame", padding=1)
        preview_card.pack(fill="both", expand=True)

        # Контейнер для холста с прокруткой
        canvas_container = tk.Canvas(preview_card, bg=self.card_color, highlightthickness=0)
        canvas_container.pack(fill="both", expand=True)

        # Холст для отображения
        self.controller.preview_canvas = tk.Canvas(canvas_container, bg="#2c2c2c",
                                                  width=600, height=400, highlightthickness=0)
        self.controller.preview_canvas.pack(expand=True)

        # Статус бар
        status_frame = ttk.Frame(right_panel, style="Card.TFrame", padding=10)
        status_frame.pack(fill="x", pady=(15, 0))

        status_text = "Используйте колесо мыши для масштабирования"
        status_label = tk.Label(status_frame, text=status_text, font=self.app_font,
                               fg=self.secondary_text, bg=self.card_color)
        status_label.pack(fill="x")

        # Привязка событий мыши
        self.controller.preview_canvas.bind("<MouseWheel>", self.controller.on_mousewheel)

    def get_vars(self):
        return {
            'text_var': self.text_var,
            'font_var': self.font_var,
            'size_var': self.size_var,
            'opacity_var': self.opacity_var,
            'rotation_var': self.rotation_var,
            'stroke_width_var': self.stroke_width_var,
            'shadow_offset_var': self.shadow_offset_var
        }