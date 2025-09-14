import tkinter as tk
from tkinter import ttk, colorchooser
from tkinter import font as tkfont
from PIL import Image, ImageTk

def setup_styles(app):
    """Настройка современных и красивых стилей интерфейса (только тёмная тема)."""
    app.bg = "#1a1b26"  # Фон приложения
    app.card = "#24283b"  # Фон карточек
    app.accent = "#7aa2f7"  # Акцентный цвет
    app.accent_hover = "#89b4fa"  # Акцентный цвет при наведении
    app.text = "#c0caf5"  # Цвет текста
    app.sub = "#a9b1d6"  # Цвет подтекста

    app.style.configure("TFrame", background=app.bg)
    app.style.configure("Card.TFrame", background=app.card, relief="flat")
    app.style.configure("TLabel", background=app.card, foreground=app.text, font=("Inter", 12))
    app.style.configure("Title.TLabel", font=("Inter", 24, "bold"), foreground=app.accent, background=app.bg)
    app.style.configure("Small.TLabel", font=("Inter", 10), foreground=app.sub, background=app.card)
    app.style.configure("Accent.TButton", font=("Inter", 12, "bold"), background=app.accent, foreground="#fff",
                        padding=8, borderwidth=0)
    app.style.map("Accent.TButton", background=[('active', app.accent_hover), ('pressed', '#555bff')],
                  foreground=[('active', '#fff')])
    app.style.configure("TButton", background=app.card, foreground=app.text, font=("Inter", 12), padding=6,
                        borderwidth=1, relief="flat")
    app.style.map("TButton", background=[('active', '#2a2e52')],
                  foreground=[('active', app.text)])
    app.style.configure("TCheckbutton", background=app.card, foreground=app.text, font=("Inter", 12), padding=4)
    app.style.map("TCheckbutton", background=[('active', app.card)], foreground=[('active', app.accent)])
    app.style.configure("TScale", background=app.card, troughcolor="#2a2e52",
                        sliderrelief="flat", sliderlength=20, sliderthickness=12)
    app.style.map("TScale", background=[('active', app.card)],
                  troughcolor=[('active', '#3a3e72')])
    app.style.configure("TCombobox", fieldbackground="#2a2e52",
                        background=app.card, foreground=app.text, font=("Inter", 12), arrowsize=14)
    app.style.map("TCombobox", fieldbackground=[('readonly', '#2a2e52')],
                  selectbackground=[('readonly', '#2a2e52')],
                  selectforeground=[('readonly', app.text)])
    app.style.configure("TNotebook", background=app.card, tabmargins=0)
    app.style.configure("TNotebook.Tab", background="#2a2e52",
                        foreground=app.text, font=("Inter", 12, "bold"), padding=(12, 8), borderwidth=0)
    app.style.map("TNotebook.Tab",
                  background=[('selected', app.card), ('active', '#3a3e72')],
                  foreground=[('selected', app.accent), ('active', app.accent)])

    app.button_style = {'bg': '#2a2e52', 'fg': app.text, 'font': ('Inter', 12),
                        'activebackground': '#3a3e72',
                        'activeforeground': app.text, 'relief': 'flat', 'bd': 0, 'highlightthickness': 0}
    app.accent_button_style = {'bg': app.accent, 'fg': '#fff', 'font': ('Inter', 12, 'bold'),
                               'activebackground': app.accent_hover, 'activeforeground': '#fff', 'relief': 'flat',
                               'bd': 0, 'highlightthickness': 0}
    app.entry_style = {'bg': '#2a2e52', 'fg': app.text,
                       'insertbackground': app.accent, 'font': ('Inter', 12), 'relief': 'flat', 'bd': 1,
                       'highlightthickness': 1, 'highlightcolor': app.accent}
    app.text_style = {'bg': '#2a2e52', 'fg': app.text,
                      'insertbackground': app.accent, 'font': ('Inter', 12), 'relief': 'flat', 'bd': 1,
                      'highlightthickness': 1, 'highlightcolor': app.accent}

def build_ui(app):
    """Создание интерфейса с улучшенными виджетами и компактными вкладками."""
    app.root.title("MICHAEL BYTE — Редактор текстовых эффектов")
    app.root.configure(bg=app.bg)
    try:
        app.style.theme_use('clam')
    except:
        pass
    setup_styles(app)

    # Верхняя панель
    topbar = ttk.Frame(app.root, style="TFrame")
    topbar.pack(side="top", fill="x", padx=20, pady=10)
    ttk.Label(topbar, text="MICHAEL BYTE", style="Title.TLabel").pack(side="left", padx=(10, 20))
    tk.Button(topbar, text="Случайный стиль", command=app.randomize_style, **app.button_style).pack(side="right", padx=10)
    tk.Button(topbar, text="Отмена", command=app.undo, **app.button_style).pack(side="right", padx=10)
    tk.Button(topbar, text="Повтор", command=app.redo, **app.button_style).pack(side="right", padx=10)

    # Основная область
    main = ttk.Frame(app.root, style="TFrame")
    main.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    # Настройки (вкладки) с уменьшенной высотой
    settings = ttk.Frame(main, style="TFrame")
    settings.pack(side="top", fill="x", pady=(0, 10))
    settings.configure(height=150)  # Уменьшена высота настроек

    notebook = ttk.Notebook(settings)
    notebook.pack(fill="both", expand=False)

    # Вкладки
    text_presets_tab = ttk.Frame(notebook, style="Card.TFrame")
    effects_advanced_tab = ttk.Frame(notebook, style="Card.TFrame")

    notebook.add(text_presets_tab, text="Текст и Пресеты")
    notebook.add(effects_advanced_tab, text="Эффекты и Продвинутые")

    # Создание содержимого вкладки "Текст и Пресеты"
    text_subframe = ttk.Frame(text_presets_tab, style="Card.TFrame", padding=12)
    text_subframe.pack(side="top", fill="x")
    build_text_controls(app, text_subframe)
    presets_subframe = ttk.Frame(text_presets_tab, style="Card.TFrame", padding=12)
    presets_subframe.pack(side="top", fill="both", expand=True)
    build_preset_controls(app, presets_subframe)

    # Создание содержимого вкладки "Эффекты и Продвинутые" с вертикальным разделением
    paned = ttk.PanedWindow(effects_advanced_tab, orient="vertical", style="Card.TFrame")
    paned.pack(fill="both", expand=True, padx=12, pady=12)

    effects_subframe = ttk.Frame(paned, style="Card.TFrame", padding=12)
    paned.add(effects_subframe, weight=1)
    build_effects_controls(app, effects_subframe)

    advanced_subframe = ttk.Frame(paned, style="Card.TFrame", padding=12)
    paned.add(advanced_subframe, weight=1)
    build_advanced_controls(app, advanced_subframe)

    # Область предпросмотра (увеличена за счёт уменьшения высоты настроек)
    preview_frame = ttk.Frame(main, style="Card.TFrame")
    preview_frame.pack(side="bottom", fill="both", expand=True, pady=(0, 10))

    preview_top = ttk.Frame(preview_frame, style="Card.TFrame")
    preview_top.pack(fill="x", padx=15, pady=(8, 6))
    ttk.Label(preview_top, text="Предпросмотр", style="Small.TLabel").pack(side="left")
    ttk.Label(preview_top, textvariable=app.font_name, style="Small.TLabel").pack(side="right")
    app.font_preview_label = ttk.Label(preview_top, style="Small.TLabel")
    app.font_preview_label.pack(side="right", padx=5)

    preview_area = ttk.Frame(preview_frame, style="Card.TFrame")
    preview_area.pack(fill="both", expand=True, padx=15, pady=(0, 10))
    app.preview_canvas = tk.Canvas(preview_area, bg=app.card, highlightthickness=0)
    hbar = ttk.Scrollbar(preview_area, orient="horizontal", command=app.preview_canvas.xview)
    vbar = ttk.Scrollbar(preview_area, orient="vertical", command=app.preview_canvas.yview)
    app.preview_canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    app.preview_canvas.grid(row=0, column=0, sticky="nsew")
    vbar.grid(row=0, column=1, sticky="ns")
    hbar.grid(row=1, column=0, sticky="ew")
    preview_area.grid_rowconfigure(0, weight=1)
    preview_area.grid_columnconfigure(0, weight=1)

    # Привязка колеса мыши
    app.preview_canvas.bind("<MouseWheel>", app._on_preview_mousewheel)
    app.preview_canvas.bind("<Button-4>", app._on_preview_mousewheel)
    app.preview_canvas.bind("<Button-5>", app._on_preview_mousewheel)

    # Нижняя строка состояния
    bottom = ttk.Frame(app.root, style="TFrame")
    bottom.pack(fill="x", padx=20, pady=(0, 10))
    app.status_var = tk.StringVar(value="Готово")
    ttk.Label(bottom, textvariable=app.status_var, style="Small.TLabel").pack(side="left")

def build_text_controls(app, parent):
    """Создание вкладки управления текстом с улучшенными виджетами."""
    tk.Label(parent, text="Текст:", **app.button_style).grid(row=0, column=0, sticky="w", pady=2)
    txt = tk.Text(parent, height=5, wrap="word", **app.text_style)
    txt.insert("1.0", app.text_content.get())
    txt.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(5, 8))

    def on_text_change(evt=None):
        app.text_content.set(txt.get("1.0", "end").rstrip("\n"))
        app.save_state()
        app.update_preview_debounced()

    txt.bind("<<Modified>>", lambda e: (txt.edit_modified(False), on_text_change()))

    fframe = ttk.Frame(parent)
    fframe.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(6, 0))
    ttk.Label(fframe, text="Шрифт:").pack(side="left")
    fonts = sorted(set(tkfont.families()))
    common = ["DejaVu Sans", "Arial", "Liberation Sans", "Times New Roman", "Verdana"]
    fonts_sorted = [f for f in common if f in fonts] + [f for f in fonts if f not in common]
    app.font_combo = ttk.Combobox(fframe, values=fonts_sorted, textvariable=app.font_name, state="readonly", width=22)
    app.font_combo.pack(side="left", padx=8)

    def on_font_change(e):
        app.update_font_preview()
        app.save_state()
        app.update_preview_debounced()

    app.font_combo.bind("<<ComboboxSelected>>", on_font_change)

    ttk.Label(fframe, text="Размер:").pack(side="left", padx=(12, 0))
    tk.Spinbox(fframe, from_=8, to=400, textvariable=app.font_size, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=8)

    spacing_frame = ttk.Frame(parent)
    spacing_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(6, 0))
    ttk.Label(spacing_frame, text="Выравнивание:").pack(side="left")
    ttk.Radiobutton(spacing_frame, text="Слева", variable=app.align, value="left",
                    command=lambda: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4)
    ttk.Radiobutton(spacing_frame, text="Центр", variable=app.align, value="center",
                    command=lambda: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4)
    ttk.Radiobutton(spacing_frame, text="Справа", variable=app.align, value="right",
                    command=lambda: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4)
    ttk.Label(spacing_frame, text="Интервал (строки):").pack(side="left", padx=(12, 0))
    tk.Spinbox(spacing_frame, from_=-20, to=80, textvariable=app.line_spacing, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Label(spacing_frame, text="Буквы:").pack(side="left", padx=(12, 0))
    tk.Spinbox(spacing_frame, from_=-10, to=50, textvariable=app.letter_spacing, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    parent.columnconfigure(0, weight=1)

def build_effects_controls(app, parent):
    """Создание вкладки управления эффектами с ползунками и улучшенными виджетами."""
    row = ttk.Frame(parent)
    row.pack(fill="x", pady=6)
    ttk.Label(row, text="Цвет текста:").pack(side="left")
    tk.Button(row, text="Выбрать", command=lambda: app._choose_color(app.text_color), **app.button_style).pack(
        side="left", padx=8)
    ttk.Label(row, textvariable=app.text_color, style="Small.TLabel").pack(side="left", padx=8)

    row2 = ttk.Frame(parent)
    row2.pack(fill="x", pady=6)
    ttk.Label(row2, text="Обводка:").pack(side="left")
    tk.Button(row2, text="Цвет", command=lambda: app._choose_color(app.stroke_color), **app.button_style).pack(
        side="left", padx=8)
    ttk.Label(row2, textvariable=app.stroke_color, style="Small.TLabel").pack(side="left", padx=8)
    ttk.Label(row2, text="Толщина:").pack(side="left", padx=(12, 0))
    tk.Spinbox(row2, from_=0, to=100, textvariable=app.stroke_width, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(row2, from_=0, to=100, variable=app.stroke_width,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)

    row3 = ttk.Frame(parent)
    row3.pack(fill="x", pady=6)
    ttk.Label(row3, text="Прозрачность:").pack(side="left")
    tk.Spinbox(row3, from_=0, to=100, textvariable=app.opacity, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(row3, from_=0, to=100, variable=app.opacity,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)

    glowf = ttk.Frame(parent)
    glowf.pack(fill="x", pady=6)
    ttk.Label(glowf, text="Свечение:").pack(side="left")
    tk.Button(glowf, text="Цвет", command=lambda: app._choose_color(app.glow_color), **app.button_style).pack(
        side="left", padx=8)
    ttk.Label(glowf, textvariable=app.glow_color, style="Small.TLabel").pack(side="left", padx=8)
    ttk.Label(glowf, text="Интенсивность:").pack(side="left", padx=(12, 0))
    tk.Spinbox(glowf, from_=0, to=80, textvariable=app.glow_intensity, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(glowf, from_=0, to=80, variable=app.glow_intensity,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)

    igf = ttk.Frame(parent)
    igf.pack(fill="x", pady=6)
    ttk.Label(igf, text="Внутреннее свечение:").pack(side="left")
    tk.Button(igf, text="Цвет", command=lambda: app._choose_color(app.inner_glow_color), **app.button_style).pack(
        side="left", padx=8)
    ttk.Label(igf, textvariable=app.inner_glow_color, style="Small.TLabel").pack(side="left", padx=8)
    ttk.Label(igf, text="Интенсивность:").pack(side="left", padx=(12, 0))
    tk.Spinbox(igf, from_=0, to=80, textvariable=app.inner_glow_intensity, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(igf, from_=0, to=80, variable=app.inner_glow_intensity,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)

    neonf = ttk.Frame(parent)
    neonf.pack(fill="x", pady=6)
    ttk.Label(neonf, text="Неоновое свечение:").pack(side="left")
    tk.Button(neonf, text="Цвет", command=lambda: app._choose_color(app.neon_color), **app.button_style).pack(
        side="left", padx=8)
    ttk.Label(neonf, textvariable=app.neon_color, style="Small.TLabel").pack(side="left", padx=8)
    ttk.Label(neonf, text="Интенсивность:").pack(side="left", padx=(12, 0))
    tk.Spinbox(neonf, from_=0, to=80, textvariable=app.neon_intensity, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(neonf, from_=0, to=80, variable=app.neon_intensity,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)

    shadowf = ttk.Frame(parent)
    shadowf.pack(fill="x", pady=6)
    ttk.Label(shadowf, text="Тень:").pack(side="left")
    tk.Button(shadowf, text="Цвет", command=lambda: app._choose_color(app.shadow_color), **app.button_style).pack(
        side="left", padx=8)
    ttk.Label(shadowf, textvariable=app.shadow_color, style="Small.TLabel").pack(side="left", padx=8)
    ttk.Label(shadowf, text="Смещение:").pack(side="left", padx=(12, 0))
    tk.Spinbox(shadowf, from_=0, to=200, textvariable=app.shadow_offset, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(shadowf, from_=0, to=200, variable=app.shadow_offset,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)
    ttk.Label(shadowf, text="Угол:").pack(side="left", padx=(12, 0))
    tk.Spinbox(shadowf, from_=0, to=359, textvariable=app.shadow_angle, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(shadowf, from_=0, to=359, variable=app.shadow_angle,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)
    ttk.Label(shadowf, text="Размытие:").pack(side="left", padx=(12, 0))
    tk.Spinbox(shadowf, from_=0, to=80, textvariable=app.shadow_blur, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(shadowf, from_=0, to=80, variable=app.shadow_blur,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)

    threedf = ttk.Frame(parent)
    threedf.pack(fill="x", pady=6)
    ttk.Label(threedf, text="3D эффект:").pack(side="left")
    ttk.Label(threedf, text="Глубина:").pack(side="left", padx=(12, 0))
    tk.Spinbox(threedf, from_=0, to=50, textvariable=app.threed_depth, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(threedf, from_=0, to=50, variable=app.threed_depth,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)
    ttk.Label(threedf, text="Угол:").pack(side="left", padx=(12, 0))
    tk.Spinbox(threedf, from_=0, to=359, textvariable=app.threed_angle, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(threedf, from_=0, to=359, variable=app.threed_angle,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)

def build_advanced_controls(app, parent):
    """Создание вкладки продвинутых настроек с улучшенными виджетами."""
    grad = ttk.Frame(parent)
    grad.pack(fill="x", pady=6)
    ttk.Checkbutton(grad, text="Включить градиент", variable=app.gradient_enabled,
                    command=lambda: (app.save_state(), app.update_preview_debounced())).pack(side="left")
    tk.Button(grad, text="Начало", command=lambda: app._choose_color(app.gradient_start), **app.button_style).pack(
        side="left", padx=8)
    ttk.Label(grad, textvariable=app.gradient_start, style="Small.TLabel").pack(side="left", padx=(0, 8))
    tk.Button(grad, text="Конец", command=lambda: app._choose_color(app.gradient_end), **app.button_style).pack(
        side="left")
    ttk.Label(grad, textvariable=app.gradient_end, style="Small.TLabel").pack(side="left", padx=(8, 0))
    ttk.Label(grad, text="Направление:").pack(side="left", padx=(12, 0))
    ttk.Combobox(grad, values=["Горизонтальное", "Вертикальное", "Диагональное"], textvariable=app.gradient_dir, state="readonly",
                 width=15).pack(side="left", padx=4)

    trow = ttk.Frame(parent)
    trow.pack(fill="x", pady=6)
    ttk.Label(trow, text="Текстура:").pack(side="left")
    tk.Spinbox(trow, from_=0, to=100, textvariable=app.texture_intensity, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(trow, from_=0, to=100, variable=app.texture_intensity,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)
    ttk.Label(trow, text="Тиснение:").pack(side="left", padx=(12, 0))
    tk.Spinbox(trow, from_=0, to=100, textvariable=app.emboss_intensity, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Label(trow, text="Скос:").pack(side="left", padx=(12, 0))
    tk.Spinbox(trow, from_=0, to=100, textvariable=app.bevel_intensity, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)

    w1 = ttk.Frame(parent)
    w1.pack(fill="x", pady=6)
    ttk.Label(w1, text="Волна (амплитуда):").pack(side="left")
    tk.Spinbox(w1, from_=0, to=150, textvariable=app.wave_amplitude, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(w1, from_=0, to=150, variable=app.wave_amplitude,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)
    ttk.Label(w1, text="Длина волны:").pack(side="left", padx=(12, 0))
    tk.Spinbox(w1, from_=5, to=300, textvariable=app.wave_wavelength, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)

    w2 = ttk.Frame(parent)
    w2.pack(fill="x", pady=6)
    ttk.Label(w2, text="Перспектива:").pack(side="left")
    tk.Spinbox(w2, from_=0, to=100, textvariable=app.perspective_strength, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Label(w2, text="Поворот (градусы):").pack(side="left", padx=(12, 0))
    tk.Spinbox(w2, from_=-180, to=180, textvariable=app.rotation_angle, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)

    refl = ttk.Frame(parent)
    refl.pack(fill="x", pady=6)
    ttk.Checkbutton(refl, text="Включить отражение", variable=app.reflection_enabled,
                    command=lambda: (app.save_state(), app.update_preview_debounced())).pack(side="left")
    ttk.Label(refl, text="Прозрачность:").pack(side="left", padx=(12, 0))
    tk.Spinbox(refl, from_=0, to=100, textvariable=app.reflection_opacity, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(refl, from_=0, to=100, variable=app.reflection_opacity,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)
    ttk.Label(refl, text="Смещение:").pack(side="left", padx=(12, 0))
    tk.Spinbox(refl, from_=0, to=100, textvariable=app.reflection_offset, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Scale(refl, from_=0, to=100, variable=app.reflection_offset,
              command=lambda e: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=4, fill="x",
                                                                                         expand=True)

    canvasf = ttk.Frame(parent)
    canvasf.pack(fill="x", pady=6)
    ttk.Label(canvasf, text="Ширина холста:").pack(side="left")
    tk.Spinbox(canvasf, from_=200, to=4000, textvariable=app.preview_width, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Label(canvasf, text="Высота:").pack(side="left", padx=(12, 0))
    tk.Spinbox(canvasf, from_=200, to=4000, textvariable=app.preview_height, width=5,
               command=lambda: (app.save_state(), app.update_preview_debounced()), **app.entry_style).pack(side="left",
                                                                                                           padx=4)
    ttk.Checkbutton(canvasf, text="Автоматический размер", variable=app.auto_size_canvas,
                    command=lambda: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=12)

    bgf = ttk.Frame(parent)
    bgf.pack(fill="x", pady=6)
    ttk.Label(bgf, text="Фон:").pack(side="left")
    tk.Button(bgf, text="Цвет фона", command=lambda: app._choose_color(app.bg_color), **app.button_style).pack(
        side="left", padx=8)
    ttk.Label(bgf, textvariable=app.bg_color, style="Small.TLabel").pack(side="left", padx=8)
    ttk.Checkbutton(bgf, text="Прозрачный (PNG)", variable=app.bg_transparent,
                    command=lambda: (app.save_state(), app.update_preview_debounced())).pack(side="left", padx=12)

def build_preset_controls(app, parent):
    """Создание вкладки управления пресетами с улучшенными виджетами."""
    tk.Button(parent, text="Сохранить пресет", command=app.save_preset, **app.accent_button_style).pack(anchor="w",
                                                                                                       pady=6)
    tk.Button(parent, text="Загрузить пресет", command=app.load_preset, **app.accent_button_style).pack(anchor="w",
                                                                                                       pady=6)
    tk.Button(parent, text="Открыть папку пресетов", command=app.open_presets_folder, **app.accent_button_style).pack(
        anchor="w", pady=6)

    # Область предпросмотра пресетов
    app.preset_frame = ttk.Frame(parent, style="Card.TFrame")
    app.preset_frame.pack(fill="both", expand=True, pady=10)
    app.update_preset_previews()