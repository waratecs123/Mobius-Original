import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk
from functions import TextEffectFunctions, load_font_prefer

class TextEffectEditorGUI:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.functions = TextEffectFunctions()

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

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Custom.TNotebook', background=self.card_color, borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                        background=self.card_color,
                        foreground=self.text_color,
                        padding=[15, 8],
                        font=self.small_font)
        style.map('Custom.TNotebook.Tab',
                  background=[('selected', self.card_color), ('active', '#252525')],
                  foreground=[('selected', self.accent_color), ('active', self.secondary_accent)])

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

        style.configure('TLabel', background=self.card_color, foreground=self.text_color, font=self.app_font)
        style.configure('Title.TLabel', font=self.title_font, foreground='white', background=self.bg_color)
        style.configure('Small.TLabel', font=self.small_font, foreground=self.secondary_text,
                        background=self.card_color)
        style.configure('TCheckbutton', background=self.card_color, foreground=self.text_color, font=self.app_font)
        style.map('TCheckbutton', background=[('active', self.card_color)], foreground=[('active', self.accent_color)])
        style.configure('TScale', background=self.card_color, troughcolor='#252525',
                        sliderrelief='flat', sliderlength=20, sliderthickness=12)
        style.map('TScale', background=[('active', self.card_color)], troughcolor=[('active', '#374151')])
        style.configure('TCombobox', fieldbackground='#252525', background=self.card_color, foreground=self.text_color,
                        font=self.app_font, arrowsize=14)
        style.map('TCombobox', fieldbackground=[('readonly', '#252525')],
                  selectbackground=[('readonly', '#252525')],
                  selectforeground=[('readonly', self.text_color)])

        self.button_style = {
            'bg': '#1a1a2e', 'fg': self.text_color, 'font': self.button_font,
            'activebackground': '#374151', 'activeforeground': self.text_color,
            'relief': 'flat', 'bd': 0, 'highlightthickness': 0
        }
        self.accent_button_style = {
            'bg': self.accent_color, 'fg': 'white', 'font': self.button_font,
            'activebackground': '#4f46e5', 'activeforeground': 'white',
            'relief': 'flat', 'bd': 0, 'highlightthickness': 0
        }
        self.entry_style = {
            'bg': '#252525', 'fg': self.text_color, 'insertbackground': self.accent_color,
            'font': self.app_font, 'relief': 'flat', 'bd': 1,
            'highlightthickness': 1, 'highlightcolor': self.accent_color
        }
        self.text_style = {
            'bg': '#252525', 'fg': self.text_color, 'insertbackground': self.accent_color,
            'font': self.app_font, 'relief': 'flat', 'bd': 1,
            'highlightthickness': 1, 'highlightcolor': self.accent_color
        }

    def setup_ui(self):
        self.root.title("MICHAEL BYTE — Редактор эффектов текста")
        self.root.configure(bg=self.bg_color)

        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        content_wrapper = tk.Frame(main_container, bg=self.bg_color)
        content_wrapper.pack(fill="both", expand=True, pady=(20, 0))

        self.setup_app_header(content_wrapper)

        content_frame = tk.Frame(content_wrapper, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True)

        self.settings_frame = tk.Frame(content_frame, bg=self.card_color, width=400, padx=25, pady=25)
        self.settings_frame.pack(side="left", fill="y")
        self.settings_frame.pack_propagate(False)

        self.preview_frame = tk.Frame(content_frame, bg=self.card_color, padx=25, pady=25)
        self.preview_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))

        self.setup_settings_ui()
        self.setup_preview_ui()

    def setup_app_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.bg_color, height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)

        title_text = "MICHAEL BYTE"
        title_label = tk.Label(header_frame, text=title_text, bg=self.bg_color, fg="white",
                               font=self.title_font, compound='center')
        title_label.place(relx=0.5, rely=0.4, anchor='center')

    def setup_settings_ui(self):
        settings_container = tk.Frame(self.settings_frame, bg=self.card_color)
        settings_container.pack(fill="both", expand=True)

        settings_notebook = ttk.Notebook(settings_container, style="Custom.TNotebook")
        settings_notebook.pack(fill="both", expand=True)

        text_presets_tab = tk.Frame(settings_notebook, bg=self.card_color)
        effects_advanced_tab = tk.Frame(settings_notebook, bg=self.card_color)
        settings_notebook.add(text_presets_tab, text="Текст и пресеты")
        settings_notebook.add(effects_advanced_tab, text="Эффекты и расширенные")

        text_subframe = tk.Frame(text_presets_tab, bg=self.card_color, padx=12, pady=12)
        text_subframe.pack(side="top", fill="x")
        self.build_text_controls(text_subframe)

        presets_subframe = tk.Frame(text_presets_tab, bg=self.card_color, padx=12, pady=12)
        presets_subframe.pack(side="top", fill="both", expand=True)
        self.build_preset_controls(presets_subframe)

        effects_subframe = tk.Frame(effects_advanced_tab, bg=self.card_color, padx=12, pady=12)
        effects_subframe.pack(side="top", fill="both", expand=True)
        self.build_effects_controls(effects_subframe)

        advanced_subframe = tk.Frame(effects_advanced_tab, bg=self.card_color, padx=12, pady=12)
        advanced_subframe.pack(side="top", fill="both", expand=True)
        self.build_advanced_controls(advanced_subframe)

    def setup_preview_ui(self):
        title_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        title_frame.pack(fill="x", pady=(0, 20))
        tk.Label(title_frame, text="ПРЕДПРОСМОТР", bg=self.card_color, fg=self.text_color,
                 font=('Arial', 16, 'bold')).pack(side="left")
        self.app.font_preview_label = tk.Label(title_frame, bg=self.card_color, fg=self.secondary_text,
                                              font=self.small_font)
        self.app.font_preview_label.pack(side="right", padx=5)
        tk.Label(title_frame, textvariable=self.app.font_name, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="right")

        preview_container = tk.Frame(self.preview_frame, bg="#1a1a2e", relief="raised", bd=1)
        preview_container.pack(fill="both", expand=True)

        self.app.preview_canvas = tk.Canvas(preview_container, bg="#1a1a2e", highlightthickness=0)
        hbar = ttk.Scrollbar(preview_container, orient="horizontal", command=self.app.preview_canvas.xview)
        vbar = ttk.Scrollbar(preview_container, orient="vertical", command=self.app.preview_canvas.yview)
        self.app.preview_canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.app.preview_canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)

        self.app.preview_canvas.bind("<MouseWheel>", self.app._on_preview_mousewheel)
        self.app.preview_canvas.bind("<Button-4>", self.app._on_preview_mousewheel)
        self.app.preview_canvas.bind("<Button-5>", self.app._on_preview_mousewheel)

        bottom = tk.Frame(self.preview_frame, bg=self.card_color)
        bottom.pack(fill="x", pady=(20, 0))
        tk.Label(bottom, textvariable=self.app.status_var, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="left")

    def build_text_controls(self, parent):
        tk.Label(parent, text="ТЕКСТ", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))
        txt = tk.Text(parent, height=5, wrap="word", **self.text_style)
        txt.insert("1.0", self.app.text_content.get())
        txt.pack(fill="x", pady=(5, 8))

        def on_text_change(evt=None):
            self.app.text_content.set(txt.get("1.0", "end").rstrip("\n"))
            self.app.save_state()
            self.app.update_preview_debounced()

        txt.bind("<KeyRelease>", on_text_change)

        fframe = tk.Frame(parent, bg=self.card_color)
        fframe.pack(fill="x", pady=(6, 0))
        tk.Label(fframe, text="Шрифт:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(side="left")
        fonts = sorted(set(self.app.available_fonts))
        common = ["DejaVu Sans", "Arial", "Times New Roman", "Verdana", "Helvetica", "Courier New"]
        fonts_sorted = [f for f in common if f in fonts] + [f for f in fonts if f not in common]
        self.app.font_combo = ttk.Combobox(fframe, values=fonts_sorted, textvariable=self.app.font_name,
                                           state="readonly", width=22)
        self.app.font_combo.pack(side="left", padx=8)

        def on_font_change(e):
            self.app.update_font_preview()
            self.app.save_state()
            self.app.update_preview_debounced()

        self.app.font_combo.bind("<<ComboboxSelected>>", on_font_change)

        tk.Label(fframe, text="Размер:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(side="left",
                                                                                                        padx=(12, 0))
        tk.Spinbox(fframe, from_=8, to=400, textvariable=self.app.font_size, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=8)

        spacing_frame = tk.Frame(parent, bg=self.card_color)
        spacing_frame.pack(fill="x", pady=(6, 0))
        tk.Label(spacing_frame, text="Выравнивание:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left")
        ttk.Radiobutton(spacing_frame, text="Слева", variable=self.app.align, value="left",
                        command=lambda: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                          padx=4)
        ttk.Radiobutton(spacing_frame, text="По центру", variable=self.app.align, value="center",
                        command=lambda: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                          padx=4)
        ttk.Radiobutton(spacing_frame, text="Справа", variable=self.app.align, value="right",
                        command=lambda: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                          padx=4)
        tk.Label(spacing_frame, text="Межстрочный интервал:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).pack(side="left", padx=(12, 0))
        tk.Spinbox(spacing_frame, from_=-20, to=80, textvariable=self.app.line_spacing, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        tk.Label(spacing_frame, text="Межбуквенный интервал:", bg=self.card_color, fg=self.text_color,
                 font=self.app_font).pack(side="left", padx=(12, 0))
        tk.Spinbox(spacing_frame, from_=-10, to=50, textvariable=self.app.letter_spacing, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)

    def build_effects_controls(self, parent):
        row = tk.Frame(parent, bg=self.card_color)
        row.pack(fill="x", pady=6)
        tk.Label(row, text="ЦВЕТ ТЕКСТА", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))
        tk.Button(row, text="Выбрать", command=lambda: self.app._choose_color(self.app.text_color),
                  **self.button_style).pack(side="left", padx=8)
        tk.Label(row, textvariable=self.app.text_color, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="left", padx=8)

        row2 = tk.Frame(parent, bg=self.card_color)
        row2.pack(fill="x", pady=6)
        tk.Label(row2, text="Цвет обводки:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left")
        tk.Button(row2, text="Выбрать", command=lambda: self.app._choose_color(self.app.stroke_color),
                  **self.button_style).pack(side="left", padx=8)
        tk.Label(row2, textvariable=self.app.stroke_color, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="left", padx=8)
        tk.Label(row2, text="Толщина:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(side="left",
                                                                                                        padx=(12, 0))
        tk.Spinbox(row2, from_=0, to=20, textvariable=self.app.stroke_width, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(row2, from_=0, to=20, variable=self.app.stroke_width,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)

        row3 = tk.Frame(parent, bg=self.card_color)
        row3.pack(fill="x", pady=6)
        tk.Label(row3, text="Непрозрачность:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left")
        tk.Spinbox(row3, from_=0, to=100, textvariable=self.app.opacity, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(row3, from_=0, to=100, variable=self.app.opacity,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)

        glowf = tk.Frame(parent, bg=self.card_color)
        glowf.pack(fill="x", pady=6)
        tk.Label(glowf, text="СВЕЧЕНИЕ", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))
        tk.Button(glowf, text="Цвет свечения", command=lambda: self.app._choose_color(self.app.glow_color),
                  **self.button_style).pack(side="left", padx=8)
        tk.Label(glowf, textvariable=self.app.glow_color, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="left", padx=8)
        tk.Label(glowf, text="Интенсивность:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(glowf, from_=0, to=50, textvariable=self.app.glow_intensity, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(glowf, from_=0, to=50, variable=self.app.glow_intensity,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)

        innerglowf = tk.Frame(parent, bg=self.card_color)
        innerglowf.pack(fill="x", pady=6)
        tk.Label(innerglowf, text="ВНУТРЕННЕЕ СВЕЧЕНИЕ", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))
        tk.Button(innerglowf, text="Цвет", command=lambda: self.app._choose_color(self.app.inner_glow_color),
                  **self.button_style).pack(side="left", padx=8)
        tk.Label(innerglowf, textvariable=self.app.inner_glow_color, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="left", padx=8)
        tk.Label(innerglowf, text="Интенсивность:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(innerglowf, from_=0, to=50, textvariable=self.app.inner_glow_intensity, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(innerglowf, from_=0, to=50, variable=self.app.inner_glow_intensity,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)

        neonf = tk.Frame(parent, bg=self.card_color)
        neonf.pack(fill="x", pady=6)
        tk.Label(neonf, text="НЕОНОВЫЙ ЭФФЕКТ", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))
        tk.Button(neonf, text="Цвет", command=lambda: self.app._choose_color(self.app.neon_color),
                  **self.button_style).pack(side="left", padx=8)
        tk.Label(neonf, textvariable=self.app.neon_color, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="left", padx=8)
        tk.Label(neonf, text="Интенсивность:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(neonf, from_=0, to=50, textvariable=self.app.neon_intensity, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(neonf, from_=0, to=50, variable=self.app.neon_intensity,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)

        shadowf = tk.Frame(parent, bg=self.card_color)
        shadowf.pack(fill="x", pady=6)
        tk.Label(shadowf, text="ТЕНЬ", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))
        tk.Button(shadowf, text="Цвет тени", command=lambda: self.app._choose_color(self.app.shadow_color),
                  **self.button_style).pack(side="left", padx=8)
        tk.Label(shadowf, textvariable=self.app.shadow_color, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="left", padx=8)
        tk.Label(shadowf, text="Смещение:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(shadowf, from_=0, to=200, textvariable=self.app.shadow_offset, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(shadowf, from_=0, to=200, variable=self.app.shadow_offset,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)
        tk.Label(shadowf, text="Угол:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(shadowf, from_=0, to=359, textvariable=self.app.shadow_angle, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(shadowf, from_=0, to=359, variable=self.app.shadow_angle,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)
        tk.Label(shadowf, text="Размытие:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(shadowf, from_=0, to=80, textvariable=self.app.shadow_blur, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(shadowf, from_=0, to=80, variable=self.app.shadow_blur,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)

        threedf = tk.Frame(parent, bg=self.card_color)
        threedf.pack(fill="x", pady=6)
        tk.Label(threedf, text="3D ЭФФЕКТ", bg=self.card_color, fg=self.secondary_text,
                 font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 10))
        tk.Label(threedf, text="Глубина:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(threedf, from_=0, to=50, textvariable=self.app.threed_depth, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(threedf, from_=0, to=50, variable=self.app.threed_depth,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)
        tk.Label(threedf, text="Угол:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(threedf, from_=0, to=359, textvariable=self.app.threed_angle, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(threedf, from_=0, to=359, variable=self.app.threed_angle,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)

    def build_advanced_controls(self, parent):
        grad = tk.Frame(parent, bg=self.card_color)
        grad.pack(fill="x", pady=6)
        ttk.Checkbutton(grad, text="Включить градиент", variable=self.app.gradient_enabled,
                        command=lambda: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left")
        tk.Button(grad, text="Начальный цвет", command=lambda: self.app._choose_color(self.app.gradient_start),
                  **self.button_style).pack(side="left", padx=8)
        tk.Label(grad, textvariable=self.app.gradient_start, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="left", padx=(0, 8))
        tk.Button(grad, text="Конечный цвет", command=lambda: self.app._choose_color(self.app.gradient_end),
                  **self.button_style).pack(side="left")
        tk.Label(grad, textvariable=self.app.gradient_end, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="left", padx=(8, 0))
        tk.Label(grad, text="Направление:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        ttk.Combobox(grad, values=["Горизонтальное", "Вертикальное", "Диагональное"], textvariable=self.app.gradient_dir,
                     state="readonly", width=15).pack(side="left", padx=4)

        trow = tk.Frame(parent, bg=self.card_color)
        trow.pack(fill="x", pady=6)
        tk.Label(trow, text="Интенсивность текстуры:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left")
        tk.Spinbox(trow, from_=0, to=100, textvariable=self.app.texture_intensity, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(trow, from_=0, to=100, variable=self.app.texture_intensity,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)
        tk.Label(trow, text="Рельеф:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(trow, from_=0, to=100, textvariable=self.app.emboss_intensity, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        tk.Label(trow, text="Фаска:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(trow, from_=0, to=100, textvariable=self.app.bevel_intensity, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)

        w1 = tk.Frame(parent, bg=self.card_color)
        w1.pack(fill="x", pady=6)
        tk.Label(w1, text="Амплитуда волны:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left")
        tk.Spinbox(w1, from_=0, to=150, textvariable=self.app.wave_amplitude, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(w1, from_=0, to=150, variable=self.app.wave_amplitude,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)
        tk.Label(w1, text="Длина волны:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(w1, from_=5, to=300, textvariable=self.app.wave_wavelength, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)

        w2 = tk.Frame(parent, bg=self.card_color)
        w2.pack(fill="x", pady=6)
        tk.Label(w2, text="Перспектива:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(side="left")
        tk.Spinbox(w2, from_=0, to=100, textvariable=self.app.perspective_strength, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        tk.Label(w2, text="Поворот (градусы):", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(w2, from_=-180, to=180, textvariable=self.app.rotation_angle, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)

        refl = tk.Frame(parent, bg=self.card_color)
        refl.pack(fill="x", pady=6)
        ttk.Checkbutton(refl, text="Включить отражение", variable=self.app.reflection_enabled,
                        command=lambda: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left")
        tk.Label(refl, text="Непрозрачность:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(refl, from_=0, to=100, textvariable=self.app.reflection_opacity, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(refl, from_=0, to=100, variable=self.app.reflection_opacity,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)
        tk.Label(refl, text="Смещение:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(refl, from_=0, to=100, textvariable=self.app.reflection_offset, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Scale(refl, from_=0, to=100, variable=self.app.reflection_offset,
                  command=lambda e: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                      padx=4, fill="x",
                                                                                                      expand=True)

        canvasf = tk.Frame(parent, bg=self.card_color)
        canvasf.pack(fill="x", pady=6)
        tk.Label(canvasf, text="Ширина холста:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left")
        tk.Spinbox(canvasf, from_=200, to=4000, textvariable=self.app.preview_width, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        tk.Label(canvasf, text="Высота:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(
            side="left", padx=(12, 0))
        tk.Spinbox(canvasf, from_=200, to=4000, textvariable=self.app.preview_height, width=5,
                   command=lambda: (self.app.save_state(), self.app.update_preview_debounced()),
                   **self.entry_style).pack(side="left", padx=4)
        ttk.Checkbutton(canvasf, text="Автоматический размер", variable=self.app.auto_size_canvas,
                        command=lambda: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                          padx=12)

        bgf = tk.Frame(parent, bg=self.card_color)
        bgf.pack(fill="x", pady=6)
        tk.Label(bgf, text="Фон:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(side="left")
        tk.Button(bgf, text="Цвет фона", command=lambda: self.app._choose_color(self.app.bg_color),
                  **self.button_style).pack(side="left", padx=8)
        tk.Label(bgf, textvariable=self.app.bg_color, bg=self.card_color, fg=self.secondary_text,
                 font=self.small_font).pack(side="left", padx=8)
        ttk.Checkbutton(bgf, text="Прозрачный (PNG)", variable=self.app.bg_transparent,
                        command=lambda: (self.app.save_state(), self.app.update_preview_debounced())).pack(side="left",
                                                                                                          padx=12)

    def build_preset_controls(self, parent):
        tk.Button(parent, text="Сохранить пресет", command=self.app.save_preset,
                  **self.accent_button_style).pack(anchor="w", pady=6)
        tk.Button(parent, text="Загрузить пресет", command=self.app.load_preset,
                  **self.accent_button_style).pack(anchor="w", pady=6)
        tk.Button(parent, text="Открыть папку пресетов", command=self.app.open_presets_folder,
                  **self.accent_button_style).pack(anchor="w", pady=6)
        tk.Button(parent, text="Случайный стиль", command=self.app.randomize_style,
                  **self.accent_button_style).pack(anchor="w", pady=6)
        tk.Button(parent, text="Отменить", command=self.app.undo,
                  **self.button_style).pack(anchor="w", pady=6)
        tk.Button(parent, text="Повторить", command=self.app.redo,
                  **self.button_style).pack(anchor="w", pady=6)

        self.app.preset_frame = tk.Frame(parent, bg=self.card_color)
        self.app.preset_frame.pack(fill="both", expand=True, pady=10)