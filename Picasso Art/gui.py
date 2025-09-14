import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
from PIL import Image, ImageTk, ImageChops, ImageFilter, ImageEnhance, ImageOps
from functions import PaintFunctions
import os


class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Picasso Art")
        self.root.geometry("1200x800")

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

        self.title_font = ('Arial', 20, 'bold')
        self.subtitle_font = ('Arial', 16, 'bold')
        self.app_font = ('Arial', 12)
        self.button_font = ('Arial', 11)
        self.mono_font = ('Arial', 10)
        self.small_font = ('Arial', 10)

        self.setup_styles()
        self.functions = PaintFunctions()
        self.status_text = tk.StringVar()
        self.zoom_text = tk.StringVar(value="100%")
        self.mouse_coords = tk.StringVar(value="X: 0, Y: 0")
        self.root.configure(bg=self.bg_color)
        self.create_widgets()
        self.bind_events()
        self.update_status()
        self.update_layers_list()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background=self.bg_color, foreground=self.text_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_color, relief="flat", borderwidth=1)
        style.configure("TLabel", background=self.card_color, foreground=self.text_color, font=self.app_font)
        style.configure("Title.TLabel", font=self.title_font)
        style.configure("Subtitle.TLabel", foreground=self.secondary_text, font=self.subtitle_font)
        style.configure("TButton", background="#2d3748", foreground=self.text_color, font=self.button_font, borderwidth=0)
        style.map("TButton", background=[('active', '#374151')], foreground=[('active', self.text_color)])
        style.configure("Accent.TButton", background=self.accent_color, foreground="#ffffff", font=self.button_font, borderwidth=0)
        style.map("Accent.TButton", background=[('active', self.accent_light)])
        style.configure("Danger.TButton", background=self.error_color, foreground="#ffffff", font=self.button_font, borderwidth=0)
        style.map("Danger.TButton", background=[('active', '#dc2626')])
        style.configure("TEntry", fieldbackground="#252525", foreground=self.text_color, borderwidth=1, bordercolor=self.border_color, insertcolor=self.accent_color, padding=5)
        style.configure("TCombobox", fieldbackground="#252525", foreground=self.text_color, selectbackground=self.accent_color, selectforeground="#ffffff", borderwidth=1, bordercolor=self.border_color, padding=5)
        style.configure("Treeview", background=self.card_color, fieldbackground=self.card_color, foreground=self.text_color, borderwidth=0)
        style.configure("Treeview.Heading", background="#252525", foreground=self.text_color, relief="flat", borderwidth=0)
        style.map("Treeview", background=[('selected', self.accent_color)], foreground=[('selected', '#ffffff')])

    def create_widgets(self):
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        header_frame = ttk.Frame(main_container, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 15))
        logo_frame = ttk.Frame(header_frame, style="TFrame")
        logo_frame.pack(side="left")
        logo_canvas = tk.Canvas(logo_frame, bg=self.bg_color, width=40, height=40, highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")
        logo_canvas.create_arc(5, 5, 35, 35, start=0, extent=180, outline=self.accent_color, width=2)
        logo_canvas.create_arc(10, 10, 30, 30, start=180, extent=180, outline=self.accent_light, width=2)
        logo_canvas.create_text(20, 20, text="φ", font=('Arial', 16, 'bold'), fill=self.accent_color)
        tk.Label(logo_frame, text="PICASSO ART", font=self.title_font, bg=self.bg_color, fg=self.text_color).pack(side="left", padx=10)
        file_menu = ttk.Frame(header_frame, style="TFrame")
        file_menu.pack(side="right")
        ttk.Button(file_menu, text="Новый", style="TButton", command=self.new_file).pack(side="left", padx=2)
        ttk.Button(file_menu, text="Открыть", style="TButton", command=self.open_file).pack(side="left", padx=2)
        ttk.Button(file_menu, text="Сохранить", style="Accent.TButton", command=self.save_file).pack(side="left", padx=2)
        ttk.Button(file_menu, text="Сохранить проект", style="TButton", command=self.save_project).pack(side="left", padx=2)
        ttk.Button(file_menu, text="Загрузить проект", style="TButton", command=self.load_project).pack(side="left", padx=2)
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(fill="both", expand=True)
        self.left_panel = ttk.Frame(content_frame, style="TFrame", width=250)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False)
        center_panel = ttk.Frame(content_frame, style="TFrame")
        center_panel.pack(side="left", fill="both", expand=True)
        right_panel = ttk.Frame(content_frame, style="TFrame", width=280)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        self.create_tools_panel(self.left_panel)
        self.create_canvas_panel(center_panel)
        self.create_layers_panel(right_panel)
        self.create_status_bar(main_container)

    def create_tools_panel(self, parent):
        tools_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        tools_card.pack(fill="x", pady=(0, 10))
        tk.Label(tools_card, text="ИНСТРУМЕНТЫ", font=self.subtitle_font, bg=self.card_color, fg=self.text_color).pack(anchor="w", pady=(0, 10))
        tools = [
            ("Карандаш", "карандаш"),
            ("Кисть", "кисть"),
            ("Ластик", "ластик"),
            ("Линия", "линия"),
            ("Прямоугольник", "прямоугольник"),
            ("Заполн. прямоугольник", "заполненный прямоугольник"),
            ("Овал", "овал"),
            ("Заполн. овал", "заполненный овал"),
            ("Многоугольник", "многоугольник"),
            ("Заполн. многоугольник", "заполненный многоугольник"),
            ("Градиент", "градиент"),
            ("Заливка", "заливка"),
            ("Текст", "текст"),
            ("Выделение", "выделение")
        ]
        for text, tool in tools:
            btn = ttk.Button(tools_card, text=text, style="TButton", command=lambda t=tool: self.set_tool(t))
            btn.pack(fill="x", pady=2)
        brush_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        brush_card.pack(fill="x", pady=(0, 10))
        tk.Label(brush_card, text="НАСТРОЙКИ КИСТИ", font=self.subtitle_font, bg=self.card_color, fg=self.text_color).pack(anchor="w", pady=(0, 10))
        tk.Label(brush_card, text="Размер:", bg=self.card_color, fg=self.text_color).pack(anchor="w")
        self.brush_size = tk.Scale(brush_card, from_=1, to=50, orient="horizontal", bg=self.card_color, fg=self.text_color, highlightthickness=0, command=self.update_brush_size)
        self.brush_size.set(self.functions.line_width)
        self.brush_size.pack(fill="x", pady=5)
        tk.Label(brush_card, text="Жесткость:", bg=self.card_color, fg=self.text_color).pack(anchor="w")
        self.brush_hardness = tk.Scale(brush_card, from_=1, to=100, orient="horizontal", bg=self.card_color, fg=self.text_color, highlightthickness=0, command=self.update_brush_hardness)
        self.brush_hardness.set(self.functions.brush_hardness)
        self.brush_hardness.pack(fill="x", pady=5)
        tk.Label(brush_card, text="Форма:", bg=self.card_color, fg=self.text_color).pack(anchor="w")
        self.brush_shape = tk.StringVar(value=self.functions.brush_shape)
        shape_combo = ttk.Combobox(brush_card, textvariable=self.brush_shape, values=["круг", "квадрат", "диагональ"], state="readonly")
        shape_combo.pack(fill="x", pady=5)
        self.brush_shape.trace("w", self.update_brush_shape)
        tk.Label(brush_card, text="Предустановки:", bg=self.card_color, fg=self.text_color).pack(anchor="w", pady=(10, 0))
        self.brush_preset = tk.StringVar()
        preset_combo = ttk.Combobox(brush_card, textvariable=self.brush_preset, values=[p["name"] for p in self.functions.brush_presets], state="readonly")
        preset_combo.pack(fill="x", pady=5)
        preset_combo.bind("<<ComboboxSelected>>", self.load_brush_preset)
        ttk.Button(brush_card, text="Сохранить пресет", style="TButton", command=self.save_brush_preset).pack(fill="x", pady=5)
        color_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        color_card.pack(fill="x", pady=(0, 10))
        tk.Label(color_card, text="ЦВЕТ", font=self.subtitle_font, bg=self.card_color, fg=self.text_color).pack(anchor="w", pady=(0, 10))
        self.color_button = tk.Button(color_card, text="Выбрать цвет", bg=self.functions.draw_color, fg="#ffffff", font=self.button_font, command=self.choose_color, relief="flat", bd=0, padx=10, pady=5)
        self.color_button.pack(fill="x")
        self.second_color_button = tk.Button(color_card, text="Второй цвет", bg=self.functions.gradient_colors[1], fg="#ffffff", font=self.button_font, command=self.choose_second_color, relief="flat", bd=0, padx=10, pady=5)
        self.second_color_button.pack(fill="x", pady=(5, 0))
        tk.Label(color_card, text="Прозрачность:", bg=self.card_color, fg=self.text_color).pack(anchor="w", pady=(10, 0))
        self.alpha_slider = tk.Scale(color_card, from_=0, to=255, orient="horizontal", bg=self.card_color, fg=self.text_color, highlightthickness=0, command=self.update_alpha)
        self.alpha_slider.set(self.functions.alpha)
        self.alpha_slider.pack(fill="x", pady=5)
        tk.Label(color_card, text="Тип градиента:", bg=self.card_color, fg=self.text_color).pack(anchor="w", pady=(10, 0))
        self.gradient_type = tk.StringVar(value=self.functions.gradient_type)
        gradient_combo = ttk.Combobox(color_card, textvariable=self.gradient_type, values=["linear", "radial"], state="readonly")
        gradient_combo.pack(fill="x", pady=5)
        self.gradient_type.trace("w", self.update_gradient_type)
        tk.Label(color_card, text="Направление:", bg=self.card_color, fg=self.text_color).pack(anchor="w", pady=(10, 0))
        self.gradient_direction = tk.StringVar(value=self.functions.gradient_direction)
        direction_combo = ttk.Combobox(color_card, textvariable=self.gradient_direction, values=["horizontal", "vertical"], state="readonly")
        direction_combo.pack(fill="x", pady=5)
        self.gradient_direction.trace("w", self.update_gradient_direction)
        filter_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        filter_card.pack(fill="x", pady=(0, 10))
        tk.Label(filter_card, text="ЭФФЕКТЫ", font=self.subtitle_font, bg=self.card_color, fg=self.text_color).pack(anchor="w", pady=(0, 10))
        self.filter_type = tk.StringVar(value="none")
        filter_combo = ttk.Combobox(filter_card, textvariable=self.filter_type, values=["none", "blur", "sharpen", "brightness", "contrast", "saturation", "grayscale", "invert", "emboss", "find_edges"], state="readonly")
        filter_combo.pack(fill="x", pady=5)
        tk.Label(filter_card, text="Сила:", bg=self.card_color, fg=self.text_color).pack(anchor="w")
        self.filter_strength = tk.Scale(filter_card, from_=0.1, to=5.0, resolution=0.1, orient="horizontal", bg=self.card_color, fg=self.text_color, highlightthickness=0)
        self.filter_strength.set(1.0)
        self.filter_strength.pack(fill="x", pady=5)
        buttons_frame = ttk.Frame(filter_card, style="Card.TFrame")
        buttons_frame.pack(fill="x", pady=5)
        ttk.Button(buttons_frame, text="Предпросмотр", style="TButton", command=self.preview_filter).pack(side="left", padx=2)
        ttk.Button(buttons_frame, text="Применить", style="Accent.TButton", command=self.apply_filter).pack(side="left", padx=2)
        ttk.Button(buttons_frame, text="Отмена", style="Danger.TButton", command=self.cancel_filter).pack(side="left", padx=2)

    def create_canvas_panel(self, parent):
        canvas_container = ttk.Frame(parent, style="Card.TFrame", padding=1)
        canvas_container.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_container, bg="#252525", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True, padx=1, pady=1)
        canvas_controls = ttk.Frame(canvas_container, style="Card.TFrame")
        canvas_controls.pack(fill="x", pady=(5, 0))
        zoom_frame = ttk.Frame(canvas_controls, style="Card.TFrame")
        zoom_frame.pack(side="right")
        ttk.Button(zoom_frame, text="−", style="TButton", width=3, command=lambda: self.zoom_canvas(-0.1)).pack(side="left", padx=2)
        ttk.Button(zoom_frame, text="+", style="TButton", width=3, command=lambda: self.zoom_canvas(0.1)).pack(side="left", padx=2)
        ttk.Button(zoom_frame, text="100%", style="TButton", width=5, command=self.reset_zoom).pack(side="left", padx=2)
        zoom_label = tk.Label(zoom_frame, textvariable=self.zoom_text, bg=self.card_color, fg=self.secondary_text, font=self.small_font)
        zoom_label.pack(side="left", padx=5)

    def create_layers_panel(self, parent):
        layers_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        layers_card.pack(fill="both", expand=True)
        layers_header = ttk.Frame(layers_card, style="Card.TFrame")
        layers_header.pack(fill="x", pady=(0, 10))
        tk.Label(layers_header, text="СЛОИ", font=self.subtitle_font, bg=self.card_color, fg=self.text_color).pack(side="left")
        layer_buttons = ttk.Frame(layers_header, style="Card.TFrame")
        layer_buttons.pack(side="right")
        ttk.Button(layer_buttons, text="+", style="Accent.TButton", width=3, command=self.add_layer).pack(side="left", padx=2)
        ttk.Button(layer_buttons, text="−", style="Danger.TButton", width=3, command=self.delete_layer).pack(side="left", padx=2)
        ttk.Button(layer_buttons, text="↑", style="TButton", width=3, command=self.move_layer_up).pack(side="left", padx=2)
        ttk.Button(layer_buttons, text="↓", style="TButton", width=3, command=self.move_layer_down).pack(side="left", padx=2)
        layers_frame = ttk.Frame(layers_card, style="Card.TFrame")
        layers_frame.pack(fill="both", expand=True)
        columns = ("visible", "name", "opacity")
        self.layers_tree = ttk.Treeview(layers_frame, columns=columns, show="tree headings", height=12)
        self.layers_tree.heading("visible", text="")
        self.layers_tree.heading("name", text="Название")
        self.layers_tree.heading("opacity", text="Непрозр.")
        self.layers_tree.column("visible", width=30, anchor="center")
        self.layers_tree.column("name", width=150, anchor="w")
        self.layers_tree.column("opacity", width=60, anchor="center")
        scrollbar = ttk.Scrollbar(layers_frame, orient="vertical", command=self.layers_tree.yview)
        self.layers_tree.configure(yscrollcommand=scrollbar.set)
        self.layers_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.layers_tree.bind("<<TreeviewSelect>>", self.on_layer_select)
        self.layers_tree.bind("<Double-1>", self.on_layer_double_click)
        props_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        props_card.pack(fill="x", pady=(10, 0))
        tk.Label(props_card, text="СВОЙСТВА СЛОЯ", font=self.subtitle_font, bg=self.card_color, fg=self.text_color).pack(anchor="w", pady=(0, 10))
        tk.Label(props_card, text="Непрозрачность:", bg=self.card_color, fg=self.text_color).pack(anchor="w")
        self.layer_opacity = tk.Scale(props_card, from_=0, to=100, orient="horizontal", bg=self.card_color, fg=self.text_color, highlightthickness=0, command=self.update_layer_opacity)
        self.layer_opacity.set(100)
        self.layer_opacity.pack(fill="x", pady=5)
        tk.Label(props_card, text="Режим наложения:", bg=self.card_color, fg=self.text_color).pack(anchor="w")
        self.blend_mode = tk.StringVar(value="normal")
        blend_combo = ttk.Combobox(props_card, textvariable=self.blend_mode, values=["normal", "multiply", "screen", "overlay", "darken", "lighten", "color_dodge", "color_burn", "soft_light", "hard_light", "difference", "exclusion"], state="readonly")
        blend_combo.pack(fill="x", pady=5)
        self.blend_mode.trace("w", self.update_blend_mode)
        check_frame = ttk.Frame(props_card, style="Card.TFrame")
        check_frame.pack(fill="x", pady=(10, 0))
        self.visible_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(check_frame, text="Видимый", variable=self.visible_var, command=self.toggle_layer_visibility).pack(anchor="w")
        self.locked_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(check_frame, text="Заблокирован", variable=self.locked_var, command=self.toggle_layer_lock).pack(anchor="w")

    def create_status_bar(self, parent):
        status_frame = ttk.Frame(parent, style="Card.TFrame", height=25)
        status_frame.pack(fill="x", pady=(10, 0))
        status_frame.pack_propagate(False)
        status_left = ttk.Frame(status_frame, style="Card.TFrame")
        status_left.pack(side="left", fill="y", padx=10)
        tk.Label(status_left, textvariable=self.status_text, bg=self.card_color, fg=self.secondary_text, font=self.small_font).pack(side="left")
        status_right = ttk.Frame(status_frame, style="Card.TFrame")
        status_right.pack(side="right", fill="y", padx=10)
        tk.Label(status_right, textvariable=self.mouse_coords, bg=self.card_color, fg=self.secondary_text, font=self.small_font).pack(side="right")

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-2>", self.on_middle_mouse_down)
        self.canvas.bind("<B2-Motion>", self.on_middle_mouse_drag)
        self.canvas.bind("<ButtonRelease-2>", self.on_middle_mouse_up)
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-plus>", lambda e: self.zoom_canvas(0.1))
        self.root.bind("<Control-minus>", lambda e: self.zoom_canvas(-0.1))
        self.root.bind("<Control-0>", lambda e: self.reset_zoom())
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

    def update_status(self):
        current_tool = self.functions.current_tool.capitalize()
        color = self.functions.draw_color
        size = self.functions.line_width
        opacity = int(self.functions.alpha / 255 * 100)
        status = f"Инструмент: {current_tool} | Цвет: {color} | Размер: {size}px | Прозрачность: {opacity}%"
        self.status_text.set(status)

    def update_layers_list(self):
        for item in self.layers_tree.get_children():
            self.layers_tree.delete(item)
        for i, layer in enumerate(reversed(self.functions.layers)):
            visible_icon = "●" if layer.visible else "○"
            item = self.layers_tree.insert("", "end", values=(visible_icon, layer.name, f"{layer.opacity}%"))
            if i == len(self.functions.layers) - 1 - self.functions.current_layer_index:
                self.layers_tree.selection_set(item)

    def on_layer_select(self, event):
        selection = self.layers_tree.selection()
        if selection:
            item = selection[0]
            index = len(self.functions.layers) - 1 - self.layers_tree.index(item)
            if 0 <= index < len(self.functions.layers):
                self.functions.current_layer_index = index
                layer = self.functions.layers[index]
                self.layer_opacity.set(layer.opacity)
                self.blend_mode.set(layer.blend_mode)
                self.visible_var.set(layer.visible)
                self.locked_var.set(layer.locked)

    def on_layer_double_click(self, event):
        item = self.layers_tree.identify_row(event.y)
        if item:
            index = len(self.functions.layers) - 1 - self.layers_tree.index(item)
            if 0 <= index < len(self.functions.layers):
                new_name = simpledialog.askstring("Переименовать слой", "Введите новое название:", initialvalue=self.functions.layers[index].name)
                if new_name:
                    self.functions.layers[index].name = new_name
                    self.update_layers_list()

    def move_layer_up(self):
        if 0 <= self.functions.current_layer_index < len(self.functions.layers) - 1:
            self.functions.reorder_layer(self.functions.current_layer_index, self.functions.current_layer_index + 1)
            self.update_layers_list()

    def move_layer_down(self):
        if 0 < self.functions.current_layer_index < len(self.functions.layers):
            self.functions.reorder_layer(self.functions.current_layer_index, self.functions.current_layer_index - 1)
            self.update_layers_list()

    def set_tool(self, tool):
        self.functions.current_tool = tool
        self.functions.clear_selection()
        self.update_status()

    def update_brush_size(self, value):
        self.functions.line_width = int(float(value))
        self.update_status()

    def update_brush_hardness(self, value):
        self.functions.brush_hardness = int(float(value))
        self.update_status()

    def update_brush_shape(self, *args):
        self.functions.brush_shape = self.brush_shape.get()
        self.update_status()

    def update_alpha(self, value):
        self.functions.alpha = int(float(value))
        self.update_status()

    def update_gradient_type(self, *args):
        self.functions.gradient_type = self.gradient_type.get()
        self.update_status()

    def update_gradient_direction(self, *args):
        self.functions.gradient_direction = self.gradient_direction.get()
        self.update_status()

    def update_layer_opacity(self, value):
        if 0 <= self.functions.current_layer_index < len(self.functions.layers):
            opacity = int(float(value))
            self.functions.set_layer_opacity(self.functions.current_layer_index, opacity)
            self.update_layers_list()

    def update_blend_mode(self, *args):
        if 0 <= self.functions.current_layer_index < len(self.functions.layers):
            self.functions.set_layer_blend_mode(self.functions.current_layer_index, self.blend_mode.get())

    def toggle_layer_visibility(self):
        if 0 <= self.functions.current_layer_index < len(self.functions.layers):
            self.functions.toggle_layer_visibility(self.functions.current_layer_index)
            self.update_layers_list()

    def toggle_layer_lock(self):
        if 0 <= self.functions.current_layer_index < len(self.functions.layers):
            layer = self.functions.layers[self.functions.current_layer_index]
            layer.locked = self.locked_var.get()

    def add_layer(self):
        name = simpledialog.askstring("Новый слой", "Введите название слоя:", initialvalue=f"Слой {len(self.functions.layers) + 1}")
        if name:
            self.functions.create_new_layer(name)
            self.update_layers_list()

    def delete_layer(self):
        if len(self.functions.layers) > 1:
            self.functions.delete_layer(self.functions.current_layer_index)
            self.update_layers_list()
        else:
            messagebox.showwarning("Предупреждение", "Нельзя удалить последний слой!")

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.functions.draw_color, title="Выберите цвет")
        if color[1]:
            self.functions.draw_color = color[1]
            self.functions.gradient_colors[0] = color[1]
            self.color_button.configure(bg=color[1])
            self.update_status()

    def choose_second_color(self):
        color = colorchooser.askcolor(initialcolor=self.functions.gradient_colors[1], title="Выберите второй цвет")
        if color[1]:
            self.functions.gradient_colors[1] = color[1]
            self.second_color_button.configure(bg=color[1])
            self.update_status()

    def save_brush_preset(self):
        name = simpledialog.askstring("Сохранить пресет", "Введите название пресета:", initialvalue="Новый пресет")
        if name:
            self.functions.save_brush_preset(name)
            self.brush_preset.set(name)
            self.update_status()

    def load_brush_preset(self, event):
        selected = self.brush_preset.get()
        for preset in self.functions.brush_presets:
            if preset["name"] == selected:
                self.functions.load_brush_preset(preset)
                self.brush_size.set(preset["size"])
                self.brush_hardness.set(preset["hardness"])
                self.brush_shape.set(preset["shape"])
                self.update_status()
                break

    def preview_filter(self):
        filter_type = self.filter_type.get()
        if filter_type == "none":
            return
        strength = float(self.filter_strength.get())
        layer = self.functions.get_current_layer()
        if not layer or layer.locked:
            return
        filtered = layer.image.copy()
        if filter_type == "blur":
            filtered = filtered.filter(ImageFilter.GaussianBlur(strength))
        elif filter_type == "sharpen":
            filtered = filtered.filter(ImageFilter.UnsharpMask(radius=strength, percent=150, threshold=3))
        elif filter_type == "brightness":
            enhancer = ImageEnhance.Brightness(filtered.convert("RGB"))
            filtered = enhancer.enhance(strength).convert("RGBA")
        elif filter_type == "contrast":
            enhancer = ImageEnhance.Contrast(filtered.convert("RGB"))
            filtered = enhancer.enhance(strength).convert("RGBA")
        elif filter_type == "saturation":
            enhancer = ImageEnhance.Color(filtered.convert("RGB"))
            filtered = enhancer.enhance(strength).convert("RGBA")
        elif filter_type == "grayscale":
            filtered = ImageOps.grayscale(filtered.convert("RGB")).convert("RGBA")
        elif filter_type == "invert":
            filtered = ImageOps.invert(filtered.convert("RGB")).convert("RGBA")
        elif filter_type == "emboss":
            filtered = filtered.filter(ImageFilter.EMBOSS)
        elif filter_type == "find_edges":
            filtered = filtered.filter(ImageFilter.FIND_EDGES)
        self.functions.preview_image = self.functions.get_display_image(filtered)
        self.update_canvas()

    def apply_filter(self):
        filter_type = self.filter_type.get()
        if filter_type == "none":
            return
        strength = float(self.filter_strength.get())
        self.functions.apply_filter(filter_type, strength)
        self.functions.preview_image = None
        self.update_canvas()
        self.filter_type.set("none")

    def cancel_filter(self):
        self.functions.preview_image = None
        self.update_canvas()
        self.filter_type.set("none")

    def on_mouse_down(self, event):
        x, y = self.functions.convert_canvas_coords(event.x, event.y)
        self.functions.start_x, self.functions.start_y = x, y
        self.functions.last_x, self.functions.last_y = x, y
        self.functions.save_state()

        if self.functions.current_tool == "заливка":
            self.functions.flood_fill(x, y)
            self.update_canvas()
        elif self.functions.current_tool == "текст":
            text = simpledialog.askstring("Текст", "Введите текст:")
            if text:
                self.functions.add_text_to_image(x, y, text)
                self.update_canvas()
        elif self.functions.current_tool == "выделение":
            self.functions.selection.points.append((x, y))
            self.functions.create_selection("polygon", self.functions.selection.points)
            self.update_canvas()
        elif self.functions.current_tool == "градиент":
            self.functions.start_drawing(x, y)
        else:
            self.functions.start_drawing(x, y)

    def on_mouse_move(self, event):
        x, y = self.functions.convert_canvas_coords(event.x, event.y)
        self.mouse_coords.set(f"X: {int(x)}, Y: {int(y)}")
        if self.functions.start_x is not None and self.functions.temp_draw is not None:
            if self.functions.current_tool == "градиент":
                self.functions.draw_shape_preview(self.functions.start_x, self.functions.start_y, x, y)
                self.update_canvas_preview()
            elif self.functions.current_tool != "выделение":
                self.functions.draw_preview(x, y)
                self.update_canvas_preview()

    def on_mouse_drag(self, event):
        x, y = self.functions.convert_canvas_coords(event.x, event.y)
        if self.functions.current_tool in ["карандаш", "кисть", "ластик"]:
            if self.functions.last_x is not None and self.functions.last_y is not None:
                self.functions.draw_on_image(self.functions.last_x, self.functions.last_y, x, y)
            self.functions.last_x, self.functions.last_y = x, y
            self.update_canvas()
        elif self.functions.current_tool in ["линия", "прямоугольник", "заполненный прямоугольник", "овал", "заполненный овал", "многоугольник", "заполненный многоугольник", "градиент"]:
            if self.functions.temp_draw is not None:
                self.functions.draw_shape_preview(self.functions.start_x, self.functions.start_y, x, y)
                self.update_canvas_preview()

    def on_mouse_up(self, event):
        x, y = self.functions.convert_canvas_coords(event.x, event.y)
        if self.functions.current_tool in ["линия", "прямоугольник", "заполненный прямоугольник", "овал", "заполненный овал", "многоугольник", "заполненный многоугольник"]:
            if self.functions.start_x is not None:
                self.functions.draw_shape_final(self.functions.start_x, self.functions.start_y, x, y)
        elif self.functions.current_tool == "градиент":
            self.functions.create_gradient(self.functions.start_x, self.functions.start_y, x, y)
        elif self.functions.current_tool == "выделение":
            self.functions.selection.points.append((x, y))
            self.functions.create_selection("polygon", self.functions.selection.points)
        elif self.functions.current_tool in ["карандаш", "кисть", "ластик"]:
            self.functions.apply_drawing()

        self.functions.start_x, self.functions.start_y = None, None
        self.functions.last_x, self.functions.last_y = None, None
        self.update_canvas()

    def on_middle_mouse_down(self, event):
        self.functions.dragging = True
        self.functions.drag_start_x = event.x
        self.functions.drag_start_y = event.y

    def on_middle_mouse_drag(self, event):
        if self.functions.dragging:
            dx = event.x - self.functions.drag_start_x
            dy = event.y - self.functions.drag_start_y
            self.functions.canvas_offset_x += dx
            self.functions.canvas_offset_y += dy
            self.functions.drag_start_x = event.x
            self.functions.drag_start_y = event.y
            self.update_canvas()

    def on_middle_mouse_up(self, event):
        self.functions.dragging = False

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom_canvas(0.1)
        else:
            self.zoom_canvas(-0.1)
        return "break"

    def zoom_canvas(self, factor):
        self.functions.scale_factor = max(0.1, min(5.0, self.functions.scale_factor + factor))
        self.zoom_text.set(f"{int(self.functions.scale_factor * 100)}%")
        self.update_canvas()

    def reset_zoom(self):
        self.functions.scale_factor = 1.0
        self.zoom_text.set("100%")
        self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        photo = self.functions.get_photo_image()
        self.canvas.create_image(self.functions.canvas_offset_x, self.functions.canvas_offset_y, anchor="nw", image=photo)
        self.canvas.image = photo
        if self.functions.has_selection:
            selection_mask = self.functions.selection.mask.convert("RGBA")
            selection_mask.putalpha(selection_mask.split()[0].point(lambda p: p * 0.3))
            selection_photo = ImageTk.PhotoImage(selection_mask.resize((int(self.functions.canvas_width * self.functions.scale_factor), int(self.functions.canvas_height * self.functions.scale_factor)), Image.LANCZOS))
            self.canvas.create_image(self.functions.canvas_offset_x, self.functions.canvas_offset_y, anchor="nw", image=selection_photo)
            self.canvas.selection_image = selection_photo

    def update_canvas_preview(self):
        self.canvas.delete("all")
        photo = self.functions.get_temp_photo_image()
        self.canvas.create_image(self.functions.canvas_offset_x, self.functions.canvas_offset_y, anchor="nw", image=photo)
        self.canvas.image = photo
        if self.functions.has_selection:
            selection_mask = self.functions.selection.mask.convert("RGBA")
            selection_mask.putalpha(selection_mask.split()[0].point(lambda p: p * 0.3))
            selection_photo = ImageTk.PhotoImage(selection_mask.resize((int(self.functions.canvas_width * self.functions.scale_factor), int(self.functions.canvas_height * self.functions.scale_factor)), Image.LANCZOS))
            self.canvas.create_image(self.functions.canvas_offset_x, self.functions.canvas_offset_y, anchor="nw", image=selection_photo)
            self.canvas.selection_image = selection_photo

    def new_file(self):
        width = simpledialog.askinteger("Новый файл", "Ширина:", initialvalue=800, minvalue=1, maxvalue=10000)
        height = simpledialog.askinteger("Новый файл", "Высота:", initialvalue=600, minvalue=1, maxvalue=10000)
        if width and height:
            bg_color = colorchooser.askcolor(title="Цвет фона", initialcolor="#ffffff")
            if bg_color[1]:
                self.functions.new_image(width, height, bg_color[1])
                self.update_canvas()
                self.update_layers_list()

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"), ("Все файлы", "*.*")])
        if file_path:
            if self.functions.open_image(file_path):
                self.update_canvas()
                self.update_layers_list()

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("BMP", "*.bmp"), ("GIF", "*.gif"), ("TIFF", "*.tiff"), ("Все файлы", "*.*")])
        if file_path:
            self.functions.save_image(file_path)
            messagebox.showinfo("Сохранено", "Изображение успешно сохранено!")

    def save_project(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".picasso", filetypes=[("Picasso Project", "*.picasso"), ("Все файлы", "*.*")])
        if file_path:
            self.functions.save_project(file_path)
            messagebox.showinfo("Сохранено", "Проект успешно сохранен!")

    def load_project(self):
        file_path = filedialog.askopenfilename(filetypes=[("Picasso Project", "*.picasso"), ("Все файлы", "*.*")])
        if file_path:
            if self.functions.load_project(file_path):
                self.update_canvas()
                self.update_layers_list()
                messagebox.showinfo("Загружено", "Проект успешно загружен!")

    def undo(self):
        if self.functions.undo():
            self.update_canvas()
            self.update_layers_list()

    def redo(self):
        if self.functions.redo():
            self.update_canvas()
            self.update_layers_list()

    def run(self):
        self.update_canvas()
        self.root.mainloop()