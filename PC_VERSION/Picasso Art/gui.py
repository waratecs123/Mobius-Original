import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
from PIL import Image, ImageTk
from functions import PaintFunctions
import os

class NewCanvasDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Новый холст")
        self.geometry("300x200")
        self.callback = callback
        self.configure(bg="#0f0f23")

        ttk.Label(self, text="Ширина:", style="TLabel").pack(pady=5)
        self.width_entry = ttk.Entry(self)
        self.width_entry.insert(0, "800")
        self.width_entry.pack(pady=5)

        ttk.Label(self, text="Высота:", style="TLabel").pack(pady=5)
        self.height_entry = ttk.Entry(self)
        self.height_entry.insert(0, "600")
        self.height_entry.pack(pady=5)

        ttk.Label(self, text="Цвет фона:", style="TLabel").pack(pady=5)
        self.bg_color = "#ffffff"
        self.color_button = tk.Button(self, text="Выбрать цвет", bg=self.bg_color, fg="#000000",
                                      command=self.choose_bg_color)
        self.color_button.pack(pady=5)

        ttk.Button(self, text="Создать", style="Accent.TButton", command=self.create).pack(pady=10)

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Цвет фона", initialcolor=self.bg_color)
        if color[1]:
            self.bg_color = color[1]
            self.color_button.configure(bg=color[1])

    def create(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            if width > 0 and height > 0:
                self.callback(width, height, self.bg_color)
                self.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения!")

class ExportDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Экспорт изображения")
        self.geometry("300x300")
        self.callback = callback
        self.configure(bg="#0f0f23")

        ttk.Label(self, text="Ширина:", style="TLabel").pack(pady=5)
        self.width_entry = ttk.Entry(self)
        self.width_entry.insert(0, str(parent.functions.canvas_width))
        self.width_entry.pack(pady=5)

        ttk.Label(self, text="Высота:", style="TLabel").pack(pady=5)
        self.height_entry = ttk.Entry(self)
        self.height_entry.insert(0, str(parent.functions.canvas_height))
        self.height_entry.pack(pady=5)

        ttk.Label(self, text="Поворот:", style="TLabel").pack(pady=5)
        self.rotation_var = tk.StringVar(value="0")
        rotation_combo = ttk.Combobox(self, textvariable=self.rotation_var, values=["0", "90", "180", "270"], state="readonly")
        rotation_combo.pack(pady=5)

        ttk.Button(self, text="Экспортировать", style="Accent.TButton", command=self.export).pack(pady=10)

    def export(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            rotation = int(self.rotation_var.get())
            if width > 0 and height > 0:
                self.callback(width, height, rotation)
                self.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения!")

class TransformDialog(tk.Toplevel):
    def __init__(self, parent, layer_index):
        super().__init__(parent)
        self.title("Трансформация слоя")
        self.geometry("300x300")
        self.functions = parent.functions
        self.layer_index = layer_index
        self.configure(bg="#0f0f23")

        ttk.Label(self, text="Поворот:", style="TLabel").pack(pady=5)
        self.rotation_var = tk.StringVar(value=str(self.functions.layers[layer_index].rotation))
        rotation_combo = ttk.Combobox(self, textvariable=self.rotation_var, values=["0", "90", "180", "270"], state="readonly")
        rotation_combo.pack(pady=5)

        ttk.Label(self, text="Масштаб:", style="TLabel").pack(pady=5)
        self.scale_var = tk.DoubleVar(value=self.functions.layers[layer_index].scale)
        scale_slider = tk.Scale(self, from_=0.1, to=5.0, resolution=0.1, orient="horizontal", variable=self.scale_var,
                                bg="#0f0f23", fg="#e2e8f0", highlightthickness=0)
        scale_slider.pack(pady=5)

        ttk.Label(self, text="Перемещение X:", style="TLabel").pack(pady=5)
        self.pos_x_var = tk.IntVar(value=self.functions.layers[layer_index].position[0])
        pos_x_entry = ttk.Entry(self, textvariable=self.pos_x_var)
        pos_x_entry.pack(pady=5)

        ttk.Label(self, text="Перемещение Y:", style="TLabel").pack(pady=5)
        self.pos_y_var = tk.IntVar(value=self.functions.layers[layer_index].position[1])
        pos_y_entry = ttk.Entry(self, textvariable=self.pos_y_var)
        pos_y_entry.pack(pady=5)

        ttk.Button(self, text="Применить", style="Accent.TButton", command=self.apply).pack(pady=10)

    def apply(self):
        try:
            rotation = int(self.rotation_var.get())
            scale = float(self.scale_var.get())
            pos_x = int(self.pos_x_var.get())
            pos_y = int(self.pos_y_var.get())
            self.functions.rotate_layer(self.layer_index, rotation - self.functions.layers[self.layer_index].rotation)
            self.functions.scale_layer(self.layer_index, scale)
            self.functions.move_layer(self.layer_index, pos_x - self.functions.layers[self.layer_index].position[0],
                                     pos_y - self.functions.layers[self.layer_index].position[1])
            self.functions.toggle_transform_mode(self.layer_index)
            self.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные значения!")

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Picasso Art")
        self.root.geometry("1400x900")
        self.root.state('zoomed')

        # Color scheme (dark theme only)
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.accent_light = "#818cf8"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#2d3748"
        self.success_color = "#10b981"
        self.warning_color = "#f59e0b"
        self.error_color = "#ef4444"

        # Fonts
        self.title_font = ('Arial', 20, 'bold')
        self.subtitle_font = ('Arial', 16, 'bold')
        self.app_font = ('Arial', 12)
        self.button_font = ('Arial', 11)
        self.mono_font = ('Courier New', 10)
        self.small_font = ('Arial', 9)

        # State variables
        self.status_text = tk.StringVar()
        self.zoom_text = tk.StringVar(value="100%")
        self.mouse_coords = tk.StringVar(value="X: 0, Y: 0")
        self.color_mode = tk.StringVar(value="RGB")
        self.root.configure(bg=self.bg_color)

        self.functions = PaintFunctions()
        self.setup_styles()
        self.create_widgets()
        self.bind_events()
        self.update_status()
        self.update_layers_list()
        self.update_history_list()
        self.update_actions_list()
        self.show_channels = False
        self.show_paths = False
        self.show_properties = False
        self.show_history = False
        self.show_actions = False

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background=self.bg_color, foreground=self.text_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_color, relief="flat", borderwidth=1)
        style.configure("TLabel", background=self.card_color, foreground=self.text_color, font=self.app_font)
        style.configure("Title.TLabel", font=self.title_font, background=self.bg_color, foreground=self.text_color)
        style.configure("Subtitle.TLabel", foreground=self.secondary_text, font=self.subtitle_font, background=self.card_color)
        style.configure("TButton", background="#2d3748", foreground=self.text_color, font=self.button_font,
                        borderwidth=0)
        style.map("TButton", background=[('active', '#374151')], foreground=[('active', self.text_color)])
        style.configure("Accent.TButton", background=self.accent_color, foreground="#ffffff", font=self.button_font,
                        borderwidth=0)
        style.map("Accent.TButton", background=[('active', self.accent_light)])
        style.configure("Danger.TButton", background=self.error_color, foreground="#ffffff", font=self.button_font,
                        borderwidth=0)
        style.map("Danger.TButton", background=[('active', '#dc2626')])
        style.configure("TEntry", fieldbackground="#252525", foreground=self.text_color, borderwidth=1,
                        bordercolor=self.border_color, insertcolor=self.accent_color, padding=5)
        style.configure("TCombobox", fieldbackground="#252525", foreground=self.text_color,
                        selectbackground=self.accent_color, selectforeground="#ffffff", borderwidth=1,
                        bordercolor=self.border_color, padding=5)
        style.configure("Treeview", background=self.card_color, fieldbackground=self.card_color,
                        foreground=self.text_color, borderwidth=0)
        style.configure("Treeview.Heading", background="#252525", foreground=self.text_color, relief="flat",
                        borderwidth=0)
        style.map("Treeview", background=[('selected', self.accent_color)], foreground=[('selected', '#ffffff')])
        style.configure("Progressbar", background=self.accent_color, troughcolor=self.card_color, borderwidth=0)

    def create_widgets(self):
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_header(main_container)
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(fill="both", expand=True)

        left_container = ttk.Frame(content_frame, style="TFrame", width=300)
        left_container.pack(side="left", fill="y", padx=(0, 10))
        left_container.pack_propagate(False)

        self.create_tools_panel(left_container)
        self.create_color_panel(left_container)
        self.create_options_panel(left_container)
        self.create_filters_panel(left_container)

        center_panel = ttk.Frame(content_frame, style="TFrame")
        center_panel.pack(side="left", fill="both", expand=True)
        self.create_canvas_panel(center_panel)

        right_container = ttk.Frame(content_frame, style="TFrame", width=350)
        right_container.pack(side="right", fill="y", padx=(10, 0))
        right_container.pack_propagate(False)

        self.create_layers_panel(right_container)
        self.create_history_panel(right_container)
        self.create_actions_panel(right_container)
        self.create_channels_panel(right_container)
        self.create_paths_panel(right_container)
        self.create_properties_panel(right_container)
        self.create_status_bar(main_container)

    def create_header(self, parent):
        header_frame = ttk.Frame(parent, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 15))

        logo_frame = ttk.Frame(header_frame, style="TFrame")
        logo_frame.pack(side="left")
        logo_canvas = tk.Canvas(logo_frame, bg=self.bg_color, width=50, height=50, highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")
        logo_canvas.create_arc(5, 5, 45, 45, start=0, extent=180, outline=self.accent_color, width=3)
        logo_canvas.create_arc(10, 10, 40, 40, start=180, extent=180, outline=self.accent_light, width=3)
        logo_canvas.create_text(25, 25, text="φ", font=('Arial', 20, 'bold'), fill=self.accent_color)
        ttk.Label(logo_frame, text="PICASSO ART", style="Title.TLabel").pack(side="left", padx=10)

        file_menu = ttk.Frame(header_frame, style="TFrame")
        file_menu.pack(side="right")
        ttk.Button(file_menu, text="Новый", style="TButton", command=self.new_file).pack(side="left", padx=2)
        ttk.Button(file_menu, text="Открыть", style="TButton", command=self.open_file).pack(side="left", padx=2)
        ttk.Button(file_menu, text="Экспортировать", style="Accent.TButton", command=self.export_file).pack(side="left", padx=2)
        ttk.Button(file_menu, text="Сохранить проект", style="TButton", command=self.save_project).pack(side="left", padx=2)
        ttk.Button(file_menu, text="Загрузить проект", style="TButton", command=self.load_project).pack(side="left", padx=2)

        view_menu = ttk.Frame(header_frame, style="TFrame")
        view_menu.pack(side="right", padx=(10, 0))
        ttk.Button(view_menu, text="История", style="TButton", command=self.toggle_history).pack(side="left", padx=2)
        ttk.Button(view_menu, text="Действия", style="TButton", command=self.toggle_actions).pack(side="left", padx=2)
        ttk.Button(view_menu, text="Каналы", style="TButton", command=self.toggle_channels).pack(side="left", padx=2)
        ttk.Button(view_menu, text="Пути", style="TButton", command=self.toggle_paths).pack(side="left", padx=2)
        ttk.Button(view_menu, text="Характеристики", style="TButton", command=self.toggle_properties).pack(side="left", padx=2)

    def create_tools_panel(self, parent):
        tools_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        tools_card.pack(fill="x", pady=(0, 10))
        ttk.Label(tools_card, text="ИНСТРУМЕНТЫ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))

        tools = [
            ("Перемещение", "move"),
            ("Карандаш", "pencil"),
            ("Кисть", "brush"),
            ("Ластик", "eraser"),
            ("Линия", "line"),
            ("Прямоугольник", "rectangle"),
            ("Заполн. прямоугольник", "filled_rectangle"),
            ("Овал", "ellipse"),
            ("Заполн. овал", "filled_ellipse"),
            ("Многоугольник", "polygon"),
            ("Заполн. многоугольник", "filled_polygon"),
            ("Градиент", "gradient"),
            ("Заливка", "fill"),
            ("Текст", "text"),
            ("Выделение", "selection"),
            ("Волшебная палочка", "magic_wand"),
            ("Лассо", "lasso")
        ]
        for text, tool in tools:
            btn = ttk.Button(tools_card, text=text, style="TButton", command=lambda t=tool: self.set_tool(t))
            btn.pack(fill="x", pady=1)

    def create_color_panel(self, parent):
        color_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        color_card.pack(fill="x", pady=(0, 10))
        ttk.Label(color_card, text="ЦВЕТА И МОДЕЛИ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))

        self.color_button = tk.Button(color_card, text="Основной цвет", bg=self.functions.draw_color, fg="#ffffff",
                                      font=self.button_font, command=self.choose_color, relief="flat", bd=0, padx=10,
                                      pady=5)
        self.color_button.pack(fill="x")
        self.second_color_button = tk.Button(color_card, text="Дополнительный цвет",
                                             bg=self.functions.gradient_colors[1], fg="#ffffff", font=self.button_font,
                                             command=self.choose_second_color, relief="flat", bd=0, padx=10, pady=5)
        self.second_color_button.pack(fill="x", pady=(5, 0))

        ttk.Label(color_card, text="Модель цвета:", style="TLabel").pack(anchor="w", pady=(10, 0))
        color_mode_combo = ttk.Combobox(color_card, textvariable=self.color_mode, values=["RGB", "CMYK", "LAB", "HSB"],
                                        state="readonly")
        color_mode_combo.pack(fill="x", pady=5)
        color_mode_combo.bind("<<ComboboxSelected>>", self.change_color_mode)

        self.cmyk_frame = ttk.Frame(color_card, style="Card.TFrame")
        self.cmyk_frame.pack(fill="x", pady=5)
        ttk.Label(self.cmyk_frame, text="CMYK:", style="TLabel").pack(anchor="w")
        self.cmyk_vars = {"C": tk.DoubleVar(value=0), "M": tk.DoubleVar(value=0), "Y": tk.DoubleVar(value=0),
                          "K": tk.DoubleVar(value=0)}
        for key, var in self.cmyk_vars.items():
            scale = tk.Scale(self.cmyk_frame, from_=0, to=100, orient="horizontal", variable=var, bg=self.card_color,
                             fg=self.text_color, highlightthickness=0, command=self.update_cmyk)
            scale.pack(fill="x", pady=1)

        self.lab_frame = ttk.Frame(color_card, style="Card.TFrame")
        self.lab_frame.pack(fill="x", pady=5)
        ttk.Label(self.lab_frame, text="LAB:", style="TLabel").pack(anchor="w")
        self.lab_vars = {"L": tk.DoubleVar(value=50), "A": tk.DoubleVar(value=0), "B": tk.DoubleVar(value=0)}
        for key, var in self.lab_vars.items():
            scale = tk.Scale(self.lab_frame, from_=0 if key == "L" else -128, to=100 if key == "L" else 128,
                             orient="horizontal", variable=var, bg=self.card_color, fg=self.text_color,
                             highlightthickness=0, command=self.update_lab)
            scale.pack(fill="x", pady=1)

        self.hsb_frame = ttk.Frame(color_card, style="Card.TFrame")
        self.hsb_frame.pack(fill="x", pady=5)
        ttk.Label(self.hsb_frame, text="HSB:", style="TLabel").pack(anchor="w")
        self.hsb_vars = {"H": tk.DoubleVar(value=0), "S": tk.DoubleVar(value=0), "B": tk.DoubleVar(value=100)}
        for key, var in self.hsb_vars.items():
            scale = tk.Scale(self.hsb_frame, from_=0, to=360 if key == "H" else 100, orient="horizontal", variable=var,
                             bg=self.card_color, fg=self.text_color, highlightthickness=0, command=self.update_hsb)
            scale.pack(fill="x", pady=1)

        swatches_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        swatches_card.pack(fill="x", pady=(0, 10))
        ttk.Label(swatches_card, text="СЮЖЕТЫ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.swatches_listbox = tk.Listbox(swatches_card, bg=self.card_color, fg=self.text_color,
                                           selectbackground=self.accent_color, height=8)
        self.swatches_listbox.pack(fill="x")
        ttk.Button(swatches_card, text="Добавить сюжет", style="TButton", command=self.add_swatch).pack(fill="x", pady=5)
        self.load_swatches()

    def create_options_panel(self, parent):
        options_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        options_card.pack(fill="x", pady=(0, 10))
        ttk.Label(options_card, text="ОПЦИИ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))

        ttk.Label(options_card, text="Размер кисти:", style="TLabel").pack(anchor="w")
        self.brush_size = tk.Scale(options_card, from_=1, to=200, orient="horizontal", bg=self.card_color,
                                   fg=self.text_color, highlightthickness=0, command=self.update_brush_size)
        self.brush_size.set(self.functions.line_width)
        self.brush_size.pack(fill="x", pady=5)

        ttk.Label(options_card, text="Жесткость:", style="TLabel").pack(anchor="w")
        self.brush_hardness = tk.Scale(options_card, from_=1, to=100, orient="horizontal", bg=self.card_color,
                                       fg=self.text_color, highlightthickness=0, command=self.update_brush_hardness)
        self.brush_hardness.set(self.functions.brush_hardness)
        self.brush_hardness.pack(fill="x", pady=5)

        ttk.Label(options_card, text="Форма:", style="TLabel").pack(anchor="w")
        self.brush_shape = tk.StringVar(value=self.functions.brush_shape)
        shape_combo = ttk.Combobox(options_card, textvariable=self.brush_shape,
                                   values=["circle", "square", "diagonal", "scatter", "texture"], state="readonly")
        shape_combo.pack(fill="x", pady=5)
        self.brush_shape.trace("w", self.update_brush_shape)

        ttk.Label(options_card, text="Предустановки:", style="TLabel").pack(anchor="w", pady=(10, 0))
        self.brush_preset = tk.StringVar()
        preset_combo = ttk.Combobox(options_card, textvariable=self.brush_preset,
                                    values=[p["name"] for p in self.functions.brush_presets], state="readonly")
        preset_combo.pack(fill="x", pady=5)
        preset_combo.bind("<<ComboboxSelected>>", self.load_brush_preset)
        ttk.Button(options_card, text="Сохранить пресет", style="TButton", command=self.save_brush_preset).pack(fill="x", pady=5)

        ttk.Label(options_card, text="Тип градиента:", style="TLabel").pack(anchor="w", pady=(10, 0))
        self.gradient_type = tk.StringVar(value=self.functions.gradient_type)
        gradient_combo = ttk.Combobox(options_card, textvariable=self.gradient_type,
                                      values=["linear", "radial", "angular", "reflected", "diamond"], state="readonly")
        gradient_combo.pack(fill="x", pady=5)
        self.gradient_type.trace("w", self.update_gradient_type)

        ttk.Label(options_card, text="Направление:", style="TLabel").pack(anchor="w")
        self.gradient_direction = tk.StringVar(value=self.functions.gradient_direction)
        direction_combo = ttk.Combobox(options_card, textvariable=self.gradient_direction,
                                       values=["horizontal", "vertical", "diagonal", "custom"], state="readonly")
        direction_combo.pack(fill="x", pady=5)
        self.gradient_direction.trace("w", self.update_gradient_direction)

        ttk.Label(options_card, text="Прозрачность:", style="TLabel").pack(anchor="w", pady=(10, 0))
        self.alpha_slider = tk.Scale(options_card, from_=0, to=255, orient="horizontal", bg=self.card_color,
                                     fg=self.text_color, highlightthickness=0, command=self.update_alpha)
        self.alpha_slider.set(self.functions.alpha)
        self.alpha_slider.pack(fill="x", pady=5)

    def create_filters_panel(self, parent):
        filter_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        filter_card.pack(fill="x", pady=(0, 10))
        ttk.Label(filter_card, text="ЭФФЕКТЫ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.filter_type = tk.StringVar(value="none")
        filter_combo = ttk.Combobox(filter_card, textvariable=self.filter_type,
                                    values=["none", "blur", "sharpen", "brightness", "contrast", "saturation",
                                            "grayscale", "invert", "emboss", "find_edges", "posterize", "solarize", "sepia"],
                                    state="readonly")
        filter_combo.pack(fill="x", pady=5)
        filter_combo.bind("<<ComboboxSelected>>", self.preview_filter)

        ttk.Label(filter_card, text="Сила эффекта:", style="TLabel").pack(anchor="w")
        self.filter_strength = tk.DoubleVar(value=1.0)
        filter_strength_slider = tk.Scale(filter_card, from_=0.1, to=5.0, resolution=0.1, orient="horizontal",
                                         variable=self.filter_strength, bg=self.card_color, fg=self.text_color,
                                         highlightthickness=0, command=self.preview_filter)
        filter_strength_slider.pack(fill="x", pady=5)

        ttk.Label(filter_card, text="Пресеты:", style="TLabel").pack(anchor="w", pady=(10, 0))
        self.filter_preset = tk.StringVar()
        preset_combo = ttk.Combobox(filter_card, textvariable=self.filter_preset,
                                    values=[p["name"] for p in self.functions.filter_presets], state="readonly")
        preset_combo.pack(fill="x", pady=5)
        preset_combo.bind("<<ComboboxSelected>>", self.load_filter_preset)

        ttk.Button(filter_card, text="Применить эффект", style="Accent.TButton", command=self.apply_filter).pack(fill="x", pady=5)

    def create_canvas_panel(self, parent):
        canvas_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        canvas_card.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_card, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas_image = self.canvas.create_image(0, 0, anchor="nw", image=self.functions.get_photo_image())

    def create_layers_panel(self, parent):
        layers_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        layers_card.pack(fill="x", pady=(0, 10))
        ttk.Label(layers_card, text="СЛОИ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.layers_listbox = ttk.Treeview(layers_card, columns=("name", "visible"), show="tree headings", selectmode="browse", height=8)
        self.layers_listbox.heading("name", text="Имя")
        self.layers_listbox.heading("visible", text="Видимость")
        self.layers_listbox.column("name", width=200)
        self.layers_listbox.column("visible", width=80)
        self.layers_listbox.pack(fill="x")
        self.layers_listbox.bind("<<TreeviewSelect>>", self.select_layer)

        layers_buttons = ttk.Frame(layers_card, style="Card.TFrame")
        layers_buttons.pack(fill="x", pady=5)
        ttk.Button(layers_buttons, text="Новый", style="TButton", command=self.new_layer).pack(side="left", padx=2)
        ttk.Button(layers_buttons, text="Дублировать", style="TButton", command=self.duplicate_layer).pack(side="left", padx=2)
        ttk.Button(layers_buttons, text="Удалить", style="Danger.TButton", command=self.delete_layer).pack(side="left", padx=2)
        ttk.Button(layers_buttons, text="Трансформация", style="TButton", command=self.transform_layer).pack(side="left", padx=2)

        ttk.Label(layers_card, text="Прозрачность:", style="TLabel").pack(anchor="w", pady=(5, 0))
        self.opacity_slider = tk.Scale(layers_card, from_=0, to=100, orient="horizontal", bg=self.card_color,
                                      fg=self.text_color, highlightthickness=0, command=self.update_opacity)
        self.opacity_slider.pack(fill="x", pady=5)

        ttk.Label(layers_card, text="Режим наложения:", style="TLabel").pack(anchor="w", pady=(5, 0))
        self.blend_mode = tk.StringVar(value="normal")
        blend_combo = ttk.Combobox(layers_card, textvariable=self.blend_mode,
                                   values=["normal", "multiply", "screen", "overlay", "darken", "lighten", "color_dodge",
                                           "color_burn", "soft_light", "hard_light", "difference", "exclusion"],
                                   state="readonly")
        blend_combo.pack(fill="x", pady=5)
        blend_combo.bind("<<ComboboxSelected>>", self.update_blend_mode)

        ttk.Label(layers_card, text="Корректирующий слой:", style="TLabel").pack(anchor="w", pady=(5, 0))
        adjustment_combo = ttk.Combobox(layers_card, values=["none", "brightness", "contrast", "hue", "saturation"], state="readonly")
        adjustment_combo.pack(fill="x", pady=5)
        adjustment_combo.bind("<<ComboboxSelected>>", self.create_adjustment_layer)

    def create_history_panel(self, parent):
        self.history_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        ttk.Label(self.history_card, text="ИСТОРИЯ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.history_listbox = ttk.Treeview(self.history_card, columns=("action",), show="tree headings", selectmode="browse", height=8)
        self.history_listbox.heading("action", text="Действие")
        self.history_listbox.column("action", width=300)
        self.history_listbox.pack(fill="x")
        history_buttons = ttk.Frame(self.history_card, style="Card.TFrame")
        history_buttons.pack(fill="x", pady=5)
        ttk.Button(history_buttons, text="Отменить", style="TButton", command=self.undo).pack(side="left", padx=2)
        ttk.Button(history_buttons, text="Повторить", style="TButton", command=self.redo).pack(side="left", padx=2)

    def create_actions_panel(self, parent):
        self.actions_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        ttk.Label(self.actions_card, text="ДЕЙСТВИЯ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.actions_listbox = ttk.Treeview(self.actions_card, columns=("action",), show="tree headings", selectmode="browse", height=8)
        self.actions_listbox.heading("action", text="Действие")
        self.actions_listbox.column("action", width=300)
        self.actions_listbox.pack(fill="x")
        actions_buttons = ttk.Frame(self.actions_card, style="Card.TFrame")
        actions_buttons.pack(fill="x", pady=5)
        ttk.Button(actions_buttons, text="Записать", style="TButton", command=self.start_action_recording).pack(side="left", padx=2)
        ttk.Button(actions_buttons, text="Воспроизвести", style="TButton", command=self.play_action).pack(side="left", padx=2)

    def create_channels_panel(self, parent):
        self.channels_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        ttk.Label(self.channels_card, text="КАНАЛЫ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.channels_listbox = ttk.Treeview(self.channels_card, columns=("channel",), show="tree headings", selectmode="browse", height=4)
        self.channels_listbox.heading("channel", text="Канал")
        self.channels_listbox.column("channel", width=300)
        self.channels_listbox.pack(fill="x")
        for channel in ["RGB", "Red", "Green", "Blue", "Alpha"]:
            self.channels_listbox.insert("", "end", values=(channel,))

    def create_paths_panel(self, parent):
        self.paths_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        ttk.Label(self.paths_card, text="ПУТИ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.paths_listbox = ttk.Treeview(self.paths_card, columns=("path",), show="tree headings", selectmode="browse", height=4)
        self.paths_listbox.heading("path", text="Путь")
        self.paths_listbox.column("path", width=300)
        self.paths_listbox.pack(fill="x")
        ttk.Button(self.paths_card, text="Создать путь", style="TButton", command=self.create_path).pack(fill="x", pady=5)

    def create_properties_panel(self, parent):
        self.properties_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        ttk.Label(self.properties_card, text="ХАРАКТЕРИСТИКИ", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.properties_listbox = ttk.Treeview(self.properties_card, columns=("property", "value"), show="tree headings", selectmode="browse", height=4)
        self.properties_listbox.heading("property", text="Свойство")
        self.properties_listbox.heading("value", text="Значение")
        self.properties_listbox.column("property", width=150)
        self.properties_listbox.column("value", width=150)
        self.properties_listbox.pack(fill="x")
        self.update_properties()

    def create_status_bar(self, parent):
        status_bar = ttk.Frame(parent, style="TFrame")
        status_bar.pack(fill="x", pady=(10, 0))
        ttk.Label(status_bar, textvariable=self.status_text, style="TLabel").pack(side="left")
        ttk.Label(status_bar, textvariable=self.zoom_text, style="TLabel").pack(side="right", padx=10)
        ttk.Label(status_bar, textvariable=self.mouse_coords, style="TLabel").pack(side="right")

    def bind_events(self):
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonPress-1>", self.canvas_click)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)
        self.canvas.bind("<Motion>", self.update_mouse_coords)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-4>", self.zoom)
        self.canvas.bind("<Button-5>", self.zoom)
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)
        self.root.bind("<Control-n>", self.new_file)
        self.root.bind("<Control-o>", self.open_file)
        self.root.bind("<Control-s>", self.save_file)

    def set_tool(self, tool):
        self.functions.current_tool = tool
        self.update_status()

    def choose_color(self):
        color = colorchooser.askcolor(title="Выберите цвет", initialcolor=self.functions.draw_color)
        if color[1]:
            self.functions.draw_color = color[1]
            self.color_button.configure(bg=color[1])
            if self.color_mode.get() == "CMYK":
                self.functions.cmyk_values = self.functions.rgb_to_cmyk(color[0])
                for key, value in zip(self.cmyk_vars.keys(), self.functions.cmyk_values):
                    self.cmyk_vars[key].set(value)
            elif self.color_mode.get() == "LAB":
                self.functions.lab_values = self.functions.rgb_to_lab(color[0])
                for key, value in zip(self.lab_vars.keys(), self.functions.lab_values):
                    self.lab_vars[key].set(value)
            elif self.color_mode.get() == "HSB":
                self.functions.hsb_values = self.functions.rgb_to_hsb(color[0])
                for key, value in zip(self.hsb_vars.keys(), self.functions.hsb_values):
                    self.hsb_vars[key].set(value)

    def choose_second_color(self):
        color = colorchooser.askcolor(title="Выберите дополнительный цвет", initialcolor=self.functions.gradient_colors[1])
        if color[1]:
            self.functions.gradient_colors[1] = color[1]
            self.second_color_button.configure(bg=color[1])

    def change_color_mode(self, event):
        mode = self.color_mode.get()
        self.functions.set_color_mode(mode)
        self.cmyk_frame.pack_forget()
        self.lab_frame.pack_forget()
        self.hsb_frame.pack_forget()
        if mode == "CMYK":
            self.cmyk_frame.pack(fill="x", pady=5)
        elif mode == "LAB":
            self.lab_frame.pack(fill="x", pady=5)
        elif mode == "HSB":
            self.hsb_frame.pack(fill="x", pady=5)

    def update_cmyk(self, event=None):
        self.functions.cmyk_values = [self.cmyk_vars[key].get() for key in self.cmyk_vars]
        if self.color_mode.get() == "CMYK":
            rgb = self.functions.cmyk_to_rgb(self.functions.cmyk_values)
            self.functions.draw_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            self.color_button.configure(bg=self.functions.draw_color)

    def update_lab(self, event=None):
        self.functions.lab_values = [self.lab_vars[key].get() for key in self.lab_vars]
        if self.color_mode.get() == "LAB":
            rgb = self.functions.lab_to_rgb(self.functions.lab_values)
            self.functions.draw_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            self.color_button.configure(bg=self.functions.draw_color)

    def update_hsb(self, event=None):
        self.functions.hsb_values = [self.hsb_vars[key].get() for key in self.hsb_vars]
        if self.color_mode.get() == "HSB":
            rgb = self.functions.hsb_to_rgb(self.functions.hsb_values)
            self.functions.draw_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            self.color_button.configure(bg=self.functions.draw_color)

    def add_swatch(self):
        self.functions.add_swatch(self.functions.draw_color)
        self.load_swatches()

    def load_swatches(self):
        self.swatches_listbox.delete(0, tk.END)
        for color in self.functions.swatches:
            self.swatches_listbox.insert(tk.END, color)
            self.swatches_listbox.itemconfig(tk.END, {'bg': color, 'fg': '#ffffff' if self.is_dark_color(color) else '#000000'})

    def is_dark_color(self, color):
        r, g, b = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        return luminance < 128

    def update_brush_size(self, value):
        self.functions.line_width = int(float(value))
        self.update_status()

    def update_brush_hardness(self, value):
        self.functions.brush_hardness = int(float(value))
        self.update_status()

    def update_brush_shape(self, *args):
        self.functions.brush_shape = self.brush_shape.get()
        self.update_status()

    def update_gradient_type(self, *args):
        self.functions.gradient_type = self.gradient_type.get()
        self.update_status()

    def update_gradient_direction(self, *args):
        self.functions.gradient_direction = self.gradient_direction.get()
        self.update_status()

    def update_alpha(self, value):
        self.functions.alpha = int(float(value))
        self.update_status()

    def preview_filter(self, event=None):
        filter_type = self.filter_type.get()
        if filter_type == "none":
            self.functions.preview_image = None
        else:
            self.functions.preview_image = self.functions.apply_filter_preview(filter_type, self.filter_strength.get(),
                                                                             self.functions.get_current_layer().image)
        self.update_canvas()

    def apply_filter(self):
        filter_type = self.filter_type.get()
        if filter_type != "none":
            self.functions.apply_filter(filter_type, self.filter_strength.get())
            self.functions.preview_image = None
            self.update_canvas()

    def load_filter_preset(self, event):
        preset_name = self.filter_preset.get()
        for preset in self.functions.filter_presets:
            if preset["name"] == preset_name:
                self.filter_type.set(preset["type"])
                self.filter_strength.set(preset["strength"])
                self.preview_filter()
                break

    def save_brush_preset(self):
        name = simpledialog.askstring("Название пресета", "Введите название пресета:", parent=self.root)
        if name:
            self.functions.save_brush_preset(name)
            self.update_brush_presets()

    def load_brush_preset(self, event):
        preset_name = self.brush_preset.get()
        for preset in self.functions.brush_presets:
            if preset["name"] == preset_name:
                self.functions.load_brush_preset(preset)
                self.brush_size.set(preset["size"])
                self.brush_hardness.set(preset["hardness"])
                self.brush_shape.set(preset["shape"])
                self.update_status()
                break

    def update_brush_presets(self):
        self.brush_preset.set("")
        # Find the Combobox widget in the options panel
        for widget in self.options_card.winfo_children():
            if isinstance(widget, ttk.Combobox) and widget.cget("textvariable") == self.brush_preset:
                widget['values'] = [p["name"] for p in self.functions.brush_presets]
                break

    def new_file(self, event=None):
        dialog = NewCanvasDialog(self.root, self.functions.new_image)
        dialog.grab_set()

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("All files", "*.*")])
        if file_path:
            if self.functions.open_image(file_path):
                self.update_canvas()
                self.update_layers_list()
                self.update_properties()

    def save_file(self, event=None):
        self.export_file()

    def export_file(self):
        dialog = ExportDialog(self.root, self.save_file_with_params)
        dialog.grab_set()

    def save_file_with_params(self, width, height, rotation):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All files", "*.*")])
        if file_path:
            self.functions.save_image(file_path, width, height, rotation)
            messagebox.showinfo("Успех", "Изображение успешно сохранено!")

    def save_project(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".paint", filetypes=[("Paint Project", "*.paint"), ("All files", "*.*")])
        if file_path:
            self.functions.save_project(file_path)
            messagebox.showinfo("Успех", "Проект успешно сохранен!")

    def load_project(self):
        file_path = filedialog.askopenfilename(filetypes=[("Paint Project", "*.paint"), ("All files", "*.*")])
        if file_path:
            if self.functions.load_project(file_path):
                self.update_canvas()
                self.update_layers_list()
                self.update_history_list()
                self.update_actions_list()
                self.update_properties()

    def toggle_history(self):
        if self.show_history:
            self.history_card.pack_forget()
        else:
            self.history_card.pack(fill="x", pady=(0, 10))
        self.show_history = not self.show_history

    def toggle_actions(self):
        if self.show_actions:
            self.actions_card.pack_forget()
        else:
            self.actions_card.pack(fill="x", pady=(0, 10))
        self.show_actions = not self.show_actions

    def toggle_channels(self):
        if self.show_channels:
            self.channels_card.pack_forget()
        else:
            self.channels_card.pack(fill="x", pady=(0, 10))
        self.show_channels = not self.show_channels

    def toggle_paths(self):
        if self.show_paths:
            self.paths_card.pack_forget()
        else:
            self.paths_card.pack(fill="x", pady=(0, 10))
        self.show_paths = not self.show_paths

    def toggle_properties(self):
        if self.show_properties:
            self.properties_card.pack_forget()
        else:
            self.properties_card.pack(fill="x", pady=(0, 10))
        self.show_properties = not self.show_properties

    def new_layer(self):
        name = simpledialog.askstring("Новый слой", "Введите имя слоя:", parent=self.root)
        if name:
            self.functions.create_new_layer(name)
            self.update_layers_list()
            self.update_canvas()

    def duplicate_layer(self):
        selection = self.layers_listbox.selection()
        if selection:
            index = int(self.layers_listbox.index(selection[0]))
            self.functions.duplicate_layer(index)
            self.update_layers_list()
            self.update_canvas()

    def delete_layer(self):
        selection = self.layers_listbox.selection()
        if selection:
            index = int(self.layers_listbox.index(selection[0]))
            self.functions.delete_layer(index)
            self.update_layers_list()
            self.update_canvas()

    def transform_layer(self):
        selection = self.layers_listbox.selection()
        if selection:
            index = int(self.layers_listbox.index(selection[0]))
            self.functions.toggle_transform_mode(index)
            dialog = TransformDialog(self.root, index)
            dialog.grab_set()

    def select_layer(self, event):
        selection = self.layers_listbox.selection()
        if selection:
            index = int(self.layers_listbox.index(selection[0]))
            self.functions.current_layer_index = index
            self.opacity_slider.set(self.functions.layers[index].opacity)
            self.blend_mode.set(self.functions.layers[index].blend_mode)
            self.update_canvas()
            self.update_properties()

    def update_opacity(self, value):
        selection = self.layers_listbox.selection()
        if selection:
            index = int(self.layers_listbox.index(selection[0]))
            self.functions.set_layer_opacity(index, int(float(value)))
            self.update_canvas()

    def update_blend_mode(self, event):
        selection = self.layers_listbox.selection()
        if selection:
            index = int(self.layers_listbox.index(selection[0]))
            self.functions.set_layer_blend_mode(index, self.blend_mode.get())
            self.update_canvas()

    def create_adjustment_layer(self, event):
        adjustment_type = event.widget.get()
        if adjustment_type != "none":
            name = f"Корректировка: {adjustment_type}"
            self.functions.create_adjustment_layer(name, adjustment_type)
            self.update_layers_list()
            self.update_canvas()

    def create_path(self):
        name = simpledialog.askstring("Новый путь", "Введите имя пути:", parent=self.root)
        if name:
            self.functions.paths.append(self.functions.Path(name))
            self.update_paths_list()

    def update_paths_list(self):
        self.paths_listbox.delete(*self.paths_listbox.get_children())
        for path in self.functions.paths:
            self.paths_listbox.insert("", "end", values=(path.name,))

    def update_properties(self):
        self.properties_listbox.delete(*self.properties_listbox.get_children())
        selection = self.layers_listbox.selection()
        if selection:
            index = int(self.layers_listbox.index(selection[0]))
            layer = self.functions.layers[index]
            properties = [
                ("Имя", layer.name),
                ("Видимость", "Да" if layer.visible else "Нет"),
                ("Прозрачность", f"{layer.opacity}%"),
                ("Режим наложения", layer.blend_mode),
                ("Поворот", f"{layer.rotation}°"),
                ("Масштаб", f"{layer.scale:.1f}x"),
                ("Позиция X", f"{layer.position[0]}"),
                ("Позиция Y", f"{layer.position[1]}")
            ]
            for prop, value in properties:
                self.properties_listbox.insert("", "end", values=(prop, value))

    def canvas_click(self, event):
        x, y = self.functions.convert_canvas_coords(event.x, event.y)
        self.functions.start_x, self.functions.start_y = x, y
        if self.functions.current_tool in ["pencil", "brush", "eraser"]:
            self.functions.start_drawing(x, y)
        elif self.functions.current_tool in ["line", "rectangle", "filled_rectangle", "ellipse", "filled_ellipse", "polygon", "filled_polygon", "gradient", "selection", "lasso"]:
            self.functions.selection.points = [(x, y)]
        elif self.functions.current_tool == "fill":
            self.functions.flood_fill(x, y)
            self.update_canvas()
        elif self.functions.current_tool == "text":
            text = simpledialog.askstring("Текст", "Введите текст:", parent=self.root)
            if text:
                self.functions.add_text_to_image(x, y, text)
                self.update_canvas()
        elif self.functions.current_tool in ["magic_wand"]:
            self.functions.create_selection(self.functions.current_tool, [(x, y)])
            self.update_canvas()
        elif self.functions.current_tool == "move":
            self.functions.start_tool_action("move", x, y)

    def canvas_drag(self, event):
        x, y = self.functions.convert_canvas_coords(event.x, event.y)
        if self.functions.current_tool in ["pencil", "brush", "eraser"]:
            self.functions.draw_on_image(self.functions.last_x, self.functions.last_y, x, y)
            self.functions.last_x, self.functions.last_y = x, y
            self.canvas.itemconfig(self.canvas_image, image=self.functions.get_temp_photo_image())
        elif self.functions.current_tool in ["line", "rectangle", "filled_rectangle", "ellipse", "filled_ellipse", "polygon", "filled_polygon", "gradient", "selection", "lasso"]:
            self.functions.selection.points.append((x, y))
            self.functions.create_selection(self.functions.current_tool, self.functions.selection.points)
            self.update_canvas()
        elif self.functions.current_tool == "move":
            self.functions.update_tool_action("move", x, y)
            self.update_canvas()

    def canvas_release(self, event):
        x, y = self.functions.convert_canvas_coords(event.x, event.y)
        if self.functions.current_tool in ["pencil", "brush", "eraser"]:
            self.functions.apply_drawing()
            self.update_canvas()
        elif self.functions.current_tool in ["line", "rectangle", "filled_rectangle", "ellipse", "filled_ellipse", "polygon", "filled_polygon"]:
            self.functions.draw_shape_final(self.functions.start_x, self.functions.start_y, x, y)
            self.functions.selection.points = []
            self.functions.has_selection = False
            self.update_canvas()
        elif self.functions.current_tool == "gradient":
            self.functions.create_gradient(self.functions.start_x, self.functions.start_y, x, y)
            self.functions.selection.points = []
            self.functions.has_selection = False
            self.update_canvas()
        elif self.functions.current_tool in ["selection", "lasso"]:
            self.functions.create_selection(self.functions.current_tool, self.functions.selection.points)
            self.update_canvas()
        elif self.functions.current_tool == "move":
            self.functions.end_tool_action("move", x, y)
            self.update_canvas()

    def update_mouse_coords(self, event):
        x, y = self.functions.convert_canvas_coords(event.x, event.y)
        self.mouse_coords.set(f"X: {int(x)}, Y: {int(y)}")

    def zoom(self, event):
        factor = 1.1 if event.delta > 0 or event.num == 4 else 0.9
        self.functions.scale_factor *= factor
        self.functions.scale_factor = max(0.1, min(self.functions.scale_factor, 5.0))
        self.zoom_text.set(f"{int(self.functions.scale_factor * 100)}%")
        self.update_canvas()

    def undo(self, event=None):
        if self.functions.undo():
            self.update_canvas()
            self.update_layers_list()
            self.update_history_list()

    def redo(self, event=None):
        if self.functions.redo():
            self.update_canvas()
            self.update_layers_list()
            self.update_history_list()

    def start_action_recording(self):
        name = simpledialog.askstring("Запись действия", "Введите имя действия:", parent=self.root)
        if name:
            self.functions.start_action_recording(name)
            self.update_status()

    def play_action(self):
        selection = self.actions_listbox.selection()
        if selection:
            index = int(self.actions_listbox.index(selection[0]))
            self.functions.play_action(index)
            self.update_canvas()
            self.update_layers_list()

    def update_canvas(self):
        self.canvas.itemconfig(self.canvas_image, image=self.functions.get_photo_image())

    def update_layers_list(self):
        self.layers_listbox.delete(*self.layers_listbox.get_children())
        for i, layer in enumerate(self.functions.layers):
            visible = "✓" if layer.visible else " "
            self.layers_listbox.insert("", "end", values=(layer.name, visible))
        if self.functions.layers:
            self.layers_listbox.selection_set(self.layers_listbox.get_children()[self.functions.current_layer_index])

    def update_history_list(self):
        self.history_listbox.delete(*self.history_listbox.get_children())
        for state in self.functions.history:
            self.history_listbox.insert("", "end", values=(state["action"],))

    def update_actions_list(self):
        self.actions_listbox.delete(*self.actions_listbox.get_children())
        for action in self.functions.actions:
            self.actions_listbox.insert("", "end", values=(action["name"],))

    def update_status(self):
        tool = self.functions.current_tool
        size = self.functions.line_width
        hardness = self.functions.brush_hardness
        shape = self.functions.brush_shape
        self.status_text.set(f"Инструмент: {tool}, Размер: {size}, Жесткость: {hardness}%, Форма: {shape}")

    def run(self):
        self.root.mainloop()