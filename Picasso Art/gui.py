import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
from PIL import Image, ImageTk, ImageDraw
from functions import PaintFunctions


class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Picasso Art")

        # Цветовая палитра в стиле Möbius
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
        self.mono_font = ('Segoe UI', 9)

        # Настройка стилей
        self.setup_styles()

        # Инициализируем функциональность
        self.functions = PaintFunctions()

        # Настройки интерфейса
        self.canvas_bg_color = self.bg_color
        self.status_text = tk.StringVar()

        # Устанавливаем полноэкранный режим
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.bg_color)

        # Блокируем стандартные сочетания клавиш для выхода из полноэкранного режима
        self.root.bind('<Escape>', lambda e: "break")
        self.root.bind('<F11>', lambda e: "break")
        self.root.bind('<Alt-Return>', lambda e: "break")

        # Создание элементов интерфейса
        self.create_widgets()

        # Привязка событий
        self.bind_events()

        # Обновление статуса
        self.update_status()
        self.update_layers_list()

    def setup_styles(self):
        """Настройка стилей виджетов в стиле Möbius"""
        style = ttk.Style()
        style.theme_use('clam')

        # Основные стили
        style.configure(".", background=self.bg_color, foreground=self.text_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_color)

        # Стили текста
        style.configure("TLabel", background=self.card_color, foreground=self.text_color, font=self.app_font)
        style.configure("Title.TLabel", font=self.title_font)
        style.configure("Subtitle.TLabel", foreground=self.secondary_text, font=self.subtitle_font)

        # Стили кнопок
        style.configure("TButton", background=self.card_color, foreground=self.text_color,
                        font=self.button_font, borderwidth=0, focuscolor=self.bg_color)
        style.map("TButton", background=[('active', '#252525')], foreground=[('active', self.text_color)])

        # Акцентные кнопки
        style.configure("Accent.TButton", background=self.accent_color, foreground="#ffffff",
                        font=self.button_font, borderwidth=0)
        style.map("Accent.TButton", background=[('active', '#ff3a7c')])

        # Поля ввода и комбобоксы
        style.configure("TEntry", fieldbackground="#252525", foreground=self.text_color,
                        borderwidth=1, bordercolor=self.border_color, insertcolor=self.accent_color, padding=5)
        style.configure("TCombobox", fieldbackground="#252525", foreground=self.text_color,
                        selectbackground=self.accent_color, selectforeground="#ffffff",
                        borderwidth=1, bordercolor=self.border_color, padding=5)

        # Слайдеры
        style.configure("Horizontal.TScale", background=self.card_color, troughcolor="#252525",
                        bordercolor=self.border_color)

    def create_widgets(self):
        # Главный контейнер
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        header_frame = ttk.Frame(main_container, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 15))

        # Логотип и название
        logo_frame = ttk.Frame(header_frame, style="TFrame")
        logo_frame.pack(side="left")

        logo_canvas = tk.Canvas(logo_frame, bg=self.bg_color, width=40, height=40,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")
        logo_canvas.create_oval(5, 5, 35, 35, fill=self.accent_color, outline="")
        logo_canvas.create_text(20, 20, text="P", font=('Segoe UI', 16, 'bold'), fill="#ffffff")

        tk.Label(logo_frame, text="PICASSO ART", font=self.title_font,
                 bg=self.bg_color, fg=self.text_color).pack(side="left", padx=10)

        # Основной контент
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(fill="both", expand=True)

        # Левая панель - инструменты и слои
        left_panel = ttk.Frame(content_frame, style="TFrame", width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        left_panel.pack_propagate(False)

        # Правая панель - холст
        right_panel = ttk.Frame(content_frame, style="TFrame")
        right_panel.pack(side="right", fill="both", expand=True)

        # Создаем Notebook для вкладок
        left_notebook = ttk.Notebook(left_panel)
        left_notebook.pack(fill="both", expand=True)

        # Вкладка с инструментами
        tools_tab = ttk.Frame(left_notebook, style="Card.TFrame", padding=15)
        left_notebook.add(tools_tab, text="Инструменты")

        # Вкладка со слоями
        layers_tab = ttk.Frame(left_notebook, style="Card.TFrame", padding=15)
        left_notebook.add(layers_tab, text="Слои")

        # Заполняем вкладку инструментов
        self.create_tools_tab(tools_tab)

        # Заполняем вкладку слоев
        self.create_layers_tab(layers_tab)

        # Холст для рисования
        canvas_card = ttk.Frame(right_panel, style="Card.TFrame", padding=1)
        canvas_card.pack(fill="both", expand=True)

        # Контейнер для холста с прокруткой
        self.canvas_container = tk.Canvas(canvas_card, bg=self.card_color, highlightthickness=0)
        self.canvas_container.pack(fill="both", expand=True)

        # Внутренний фрейм для перемещения
        self.inner_frame = tk.Frame(self.canvas_container, bg=self.functions.bg_color)
        self.inner_frame.pack(expand=True)

        # Холст для рисования
        self.canvas = tk.Canvas(self.inner_frame, bg=self.functions.bg_color,
                                width=self.functions.canvas_width,
                                height=self.functions.canvas_height,
                                highlightthickness=0)
        self.canvas.pack(expand=True)

        # Статус бар
        status_card = ttk.Frame(main_container, style="Card.TFrame", padding=10)
        status_card.pack(fill="x", pady=(15, 0))

        self.status_bar = tk.Label(status_card, textvariable=self.status_text,
                                   font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        self.status_bar.pack(fill="x")

    def create_tools_tab(self, parent):
        """Создает вкладку с инструментами"""
        tk.Label(parent, text="Инструменты", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 15))

        # Выбор инструмента
        tool_frame = ttk.Frame(parent, style="Card.TFrame")
        tool_frame.pack(fill="x", pady=(0, 15))

        tk.Label(tool_frame, text="Инструмент:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.tool_var = tk.StringVar(value="карандаш")
        tools = ["карандаш", "ластик", "линия", "прямоугольник", "овал", "текст", "заливка"]
        tools_combo = ttk.Combobox(tool_frame, textvariable=self.tool_var, values=tools,
                                   style="TCombobox", state="readonly")
        tools_combo.pack(fill="x", pady=5)

        # Цвет
        color_frame = ttk.Frame(parent, style="Card.TFrame")
        color_frame.pack(fill="x", pady=(0, 15))

        tk.Label(color_frame, text="Цвет:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        color_btn_frame = ttk.Frame(color_frame, style="Card.TFrame")
        color_btn_frame.pack(fill="x", pady=5)

        ttk.Button(color_btn_frame, text="Выбрать цвет", style="TButton",
                   command=self.choose_color).pack(side="left")

        self.color_display = tk.Label(color_btn_frame, bg=self.functions.draw_color,
                                      width=3, height=1, relief="sunken", bd=1)
        self.color_display.pack(side="left", padx=10)

        # Прозрачность
        alpha_frame = ttk.Frame(parent, style="Card.TFrame")
        alpha_frame.pack(fill="x", pady=(0, 15))

        tk.Label(alpha_frame, text="Прозрачность:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.alpha_var = tk.IntVar(value=100)
        self.alpha_scale = ttk.Scale(alpha_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     variable=self.alpha_var, style="Horizontal.TScale")
        self.alpha_scale.pack(fill="x", pady=5)

        # Размер кисти
        size_frame = ttk.Frame(parent, style="Card.TFrame")
        size_frame.pack(fill="x", pady=(0, 15))

        tk.Label(size_frame, text="Размер кисти:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.brush_size = ttk.Scale(size_frame, from_=1, to=50, orient=tk.HORIZONTAL,
                                    style="Horizontal.TScale")
        self.brush_size.set(self.functions.line_width)
        self.brush_size.pack(fill="x", pady=5)

        # Операции с файлами
        file_frame = ttk.Frame(parent, style="Card.TFrame")
        file_frame.pack(fill="x", pady=(0, 15))

        tk.Label(file_frame, text="Файл:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        file_btn_frame = ttk.Frame(file_frame, style="Card.TFrame")
        file_btn_frame.pack(fill="x", pady=5)

        ttk.Button(file_btn_frame, text="Новый", style="TButton",
                   command=self.new_image).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(file_btn_frame, text="Открыть", style="TButton",
                   command=self.open_image).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(file_btn_frame, text="Сохранить", style="Accent.TButton",
                   command=self.save_image).pack(side="left", fill="x", expand=True, padx=2)

        # История действий
        history_frame = ttk.Frame(parent, style="Card.TFrame")
        history_frame.pack(fill="x", pady=(0, 15))

        tk.Label(history_frame, text="История:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        history_btn_frame = ttk.Frame(history_frame, style="Card.TFrame")
        history_btn_frame.pack(fill="x", pady=5)

        ttk.Button(history_btn_frame, text="Отмена", style="TButton",
                   command=self.undo).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(history_btn_frame, text="Повтор", style="TButton",
                   command=self.redo).pack(side="left", fill="x", expand=True, padx=2)

        # Масштабирование
        zoom_frame = ttk.Frame(parent, style="Card.TFrame")
        zoom_frame.pack(fill="x", pady=(0, 15))

        tk.Label(zoom_frame, text="Масштаб:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        zoom_btn_frame = ttk.Frame(zoom_frame, style="Card.TFrame")
        zoom_btn_frame.pack(fill="x", pady=5)

        ttk.Button(zoom_btn_frame, text="+", style="TButton",
                   command=self.zoom_in).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(zoom_btn_frame, text="-", style="TButton",
                   command=self.zoom_out).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(zoom_btn_frame, text="100%", style="TButton",
                   command=self.reset_view).pack(side="left", fill="x", expand=True, padx=2)

        # Очистка
        clear_frame = ttk.Frame(parent, style="Card.TFrame")
        clear_frame.pack(fill="x")

        ttk.Button(clear_frame, text="Очистить холст", style="TButton",
                   command=self.clear_canvas).pack(fill="x")

    def create_layers_tab(self, parent):
        """Создает вкладку для управления слоями"""
        tk.Label(parent, text="Управление слоями", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 15))

        # Кнопки управления слоями
        layer_buttons_frame = ttk.Frame(parent, style="Card.TFrame")
        layer_buttons_frame.pack(fill="x", pady=(0, 15))

        ttk.Button(layer_buttons_frame, text="Новый слой", style="TButton",
                   command=self.add_new_layer).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(layer_buttons_frame, text="Удалить слой", style="TButton",
                   command=self.delete_layer).pack(side="left", fill="x", expand=True, padx=2)

        # Список слоев
        layers_list_frame = ttk.Frame(parent, style="Card.TFrame")
        layers_list_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Создаем Treeview для отображения слоев
        columns = ("visible", "name", "opacity")
        self.layers_tree = ttk.Treeview(layers_list_frame, columns=columns, show="tree headings", height=8)

        # Настраиваем колонки
        self.layers_tree.heading("visible", text="✓")
        self.layers_tree.column("visible", width=30, anchor="center")

        self.layers_tree.heading("name", text="Название")
        self.layers_tree.column("name", width=120, anchor="w")

        self.layers_tree.heading("opacity", text="Непрозр.")
        self.layers_tree.column("opacity", width=60, anchor="center")

        # Scrollbar для списка слоев
        scrollbar = ttk.Scrollbar(layers_list_frame, orient="vertical", command=self.layers_tree.yview)
        self.layers_tree.configure(yscrollcommand=scrollbar.set)

        self.layers_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем события
        self.layers_tree.bind("<Button-1>", self.on_layer_click)
        self.layers_tree.bind("<Double-1>", self.on_layer_double_click)

        # Управление прозрачностью текущего слоя
        opacity_frame = ttk.Frame(parent, style="Card.TFrame")
        opacity_frame.pack(fill="x")

        tk.Label(opacity_frame, text="Прозрачность слоя:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.layer_opacity_var = tk.IntVar(value=100)
        self.layer_opacity_scale = ttk.Scale(opacity_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                             variable=self.layer_opacity_var, style="Horizontal.TScale")
        self.layer_opacity_scale.pack(fill="x", pady=5)
        self.layer_opacity_scale.configure(command=self.on_layer_opacity_change)

    def update_layers_list(self):
        """Обновляет список слоев"""
        # Очищаем текущий список
        for item in self.layers_tree.get_children():
            self.layers_tree.delete(item)

        # Добавляем слои в обратном порядке (сверху - последний)
        for i, layer in enumerate(reversed(self.functions.layers)):
            visible_icon = "✓" if layer.visible else "✗"
            item_id = self.layers_tree.insert("", "end", values=(
                visible_icon,
                layer.name,
                f"{layer.opacity}%"
            ))

            # Выделяем текущий слой
            if i == len(self.functions.layers) - 1 - self.functions.current_layer_index:
                self.layers_tree.selection_set(item_id)
                self.layers_tree.focus(item_id)

    def on_layer_click(self, event):
        """Обработчик клика по слою"""
        item = self.layers_tree.identify_row(event.y)
        column = self.layers_tree.identify_column(event.x)

        if item and column == "#1":  # Колонка видимости
            # Получаем индекс слоя (в обратном порядке)
            all_items = self.layers_tree.get_children()
            index = all_items.index(item)
            real_index = len(self.functions.layers) - 1 - index

            # Переключаем видимость
            self.functions.toggle_layer_visibility(real_index)
            self.update_layers_list()
            self.update_canvas()

        elif item and column == "#2":  # Колонка названия
            # Выбираем слой
            all_items = self.layers_tree.get_children()
            index = all_items.index(item)
            self.functions.current_layer_index = len(self.functions.layers) - 1 - index
            self.update_layers_list()

            # Обновляем слайдер прозрачности
            current_layer = self.functions.get_current_layer()
            if current_layer:
                self.layer_opacity_var.set(current_layer.opacity)

    def on_layer_double_click(self, event):
        """Обработчик двойного клика по слою - переименование"""
        item = self.layers_tree.identify_row(event.y)
        column = self.layers_tree.identify_column(event.x)

        if item and column == "#2":  # Колонка названия
            all_items = self.layers_tree.get_children()
            index = all_items.index(item)
            real_index = len(self.functions.layers) - 1 - index

            current_name = self.functions.layers[real_index].name
            new_name = simpledialog.askstring("Переименование", "Введите новое название слоя:",
                                              initialvalue=current_name)
            if new_name:
                self.functions.layers[real_index].name = new_name
                self.update_layers_list()

    def on_layer_opacity_change(self, value):
        """Изменение прозрачности текущего слоя"""
        opacity = int(float(value))
        current_layer = self.functions.get_current_layer()
        if current_layer:
            self.functions.set_layer_opacity(self.functions.current_layer_index, opacity)
            self.update_layers_list()
            self.update_canvas()

    def add_new_layer(self):
        """Добавляет новый слой"""
        layer_name = simpledialog.askstring("Новый слой", "Введите название слоя:",
                                            initialvalue=f"Слой {len(self.functions.layers) + 1}")
        if layer_name:
            self.functions.save_state()
            self.functions.create_new_layer(layer_name, "transparent")
            self.update_layers_list()
            self.update_canvas()

    def delete_layer(self):
        """Удаляет текущий слой"""
        if len(self.functions.layers) > 1:
            self.functions.save_state()
            if self.functions.delete_current_layer():
                self.update_layers_list()
                self.update_canvas()
        else:
            messagebox.showwarning("Предупреждение", "Нельзя удалить последний слой!")

    def bind_events(self):
        # Привязка событий мыши только к холсту
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        self.canvas.bind("<Button-1>", self.start_paint)

        # Привязка событий клавиатуры
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-n>", lambda e: self.new_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-o>", lambda e: self.open_image())

        # Привязка событий для перемещения холста
        self.canvas.bind("<ButtonPress-2>", self.start_drag)  # Средняя кнопка мыши
        self.canvas.bind("<B2-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-2>", self.stop_drag)

        # Привязка событий для масштабирования колесиком мыши
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # Обновление параметров при изменении
        self.tool_var.trace_add("write", lambda *args: self.update_tool())
        self.alpha_var.trace_add("write", lambda *args: self.update_alpha())
        self.brush_size.configure(command=lambda v: self.update_brush_size())

    def update_tool(self):
        self.functions.current_tool = self.tool_var.get()

    def update_alpha(self):
        self.functions.alpha = int(self.alpha_var.get() * 2.55)

    def update_brush_size(self):
        self.functions.line_width = int(self.brush_size.get())

    def update_status(self):
        tool_names = {
            "карандаш": "Карандаш",
            "ластик": "Ластик",
            "линия": "Линия",
            "прямоугольник": "Прямоугольник",
            "овал": "Овал",
            "текст": "Текст",
            "заливка": "Заливка"
        }
        tool_name = tool_names.get(self.functions.current_tool, self.functions.current_tool)
        self.status_text.set(f"Инструмент: {tool_name} | Размер: {self.functions.line_width}px | "
                             f"Прозрачность: {self.alpha_var.get()}% | "
                             f"Масштаб: {int(self.functions.scale_factor * 100)}%")

    def update_canvas(self):
        """Обновляет отображение холста"""
        photo = self.functions.get_photo_image(self.functions.composite_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=photo, anchor="nw")
        self.canvas.image = photo  # Сохраняем ссылку

    def start_paint(self, event):
        """Начало рисования"""
        x, y = self.functions.convert_canvas_coords(event.x, event.y)
        self.functions.start_x, self.functions.start_y = x, y
        self.functions.last_x, self.functions.last_y = x, y

        if self.functions.current_tool == "текст":
            text = simpledialog.askstring("Текст", "Введите текст:")
            if text:
                self.functions.save_state()
                self.functions.add_text_to_image(x, y, text)
                self.update_canvas()

        elif self.functions.current_tool == "заливка":
            self.functions.save_state()
            self.functions.flood_fill(x, y)
            self.update_canvas()

    def paint(self, event):
        """Процесс рисования"""
        if self.functions.start_x is None:
            return

        x, y = self.functions.convert_canvas_coords(event.x, event.y)

        if self.functions.current_tool in ["карандаш", "ластик"]:
            color = "white" if self.functions.current_tool == "ластик" else self.functions.draw_color
            self.functions.draw_on_image(self.functions.last_x, self.functions.last_y, x, y, color)
            self.functions.last_x, self.functions.last_y = x, y
            self.update_canvas()

        elif self.functions.current_tool in ["линия", "прямоугольник", "овал"]:
            # Временное отображение фигуры
            self.update_canvas()
            temp_img = Image.new("RGBA", (self.functions.canvas_width, self.functions.canvas_height))
            temp_draw = ImageDraw.Draw(temp_img)

            if self.functions.current_tool == "линия":
                temp_draw.line([self.functions.start_x, self.functions.start_y, x, y],
                               fill=self.functions.get_color_with_alpha(self.functions.draw_color),
                               width=self.functions.line_width)
            elif self.functions.current_tool == "прямоугольник":
                temp_draw.rectangle([self.functions.start_x, self.functions.start_y, x, y],
                                    outline=self.functions.get_color_with_alpha(self.functions.draw_color),
                                    width=self.functions.line_width)
            elif self.functions.current_tool == "овал":
                temp_draw.ellipse([self.functions.start_x, self.functions.start_y, x, y],
                                  outline=self.functions.get_color_with_alpha(self.functions.draw_color),
                                  width=self.functions.line_width)

            photo = self.functions.get_photo_image(
                Image.alpha_composite(self.functions.composite_image.convert("RGBA"), temp_img).convert("RGB")
            )
            self.canvas.create_image(0, 0, image=photo, anchor="nw")
            self.canvas.image = photo

    def reset(self, event):
        """Завершение рисования"""
        if self.functions.start_x is None:
            return

        x, y = self.functions.convert_canvas_coords(event.x, event.y)

        if self.functions.current_tool in ["линия", "прямоугольник", "овал"]:
            self.functions.save_state()
            self.functions.draw_shape(self.functions.start_x, self.functions.start_y, x, y)
            self.update_canvas()

        self.functions.start_x, self.functions.start_y = None, None
        self.functions.last_x, self.functions.last_y = None, None

    def choose_color(self):
        """Выбор цвета"""
        color = colorchooser.askcolor(initialcolor=self.functions.draw_color)[1]
        if color:
            self.functions.draw_color = color
            self.color_display.configure(bg=color)

    def new_image(self):
        """Создание нового изображения"""
        if messagebox.askyesno("Новое изображение", "Создать новое изображение? Текущие изменения будут потеряны."):
            self.functions.new_image()
            self.update_canvas()
            self.update_layers_list()

    def open_image(self):
        """Открытие изображения"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            self.functions.save_state()
            self.functions.open_image(file_path)
            self.update_canvas()
            self.update_layers_list()

    def save_image(self):
        """Сохранение изображения"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if file_path:
            self.functions.save_image(file_path)
            messagebox.showinfo("Сохранение", "Изображение успешно сохранено!")

    def undo(self):
        """Отмена действия"""
        if self.functions.undo():
            self.update_canvas()
            self.update_layers_list()

    def redo(self):
        """Повтор действия"""
        if self.functions.redo():
            self.update_canvas()
            self.update_layers_list()

    def clear_canvas(self):
        """Очистка холста"""
        if messagebox.askyesno("Очистка", "Очистить текущий слой?"):
            self.functions.save_state()
            self.functions.clear_canvas()
            self.update_canvas()

    def start_drag(self, event):
        """Начало перемещения холста"""
        self.functions.dragging = True
        self.functions.drag_start_x = event.x
        self.functions.drag_start_y = event.y
        self.canvas.configure(cursor="fleur")

    def drag(self, event):
        """Перемещение холста"""
        if self.functions.dragging:
            dx = event.x - self.functions.drag_start_x
            dy = event.y - self.functions.drag_start_y
            self.functions.canvas_offset_x += dx
            self.functions.canvas_offset_y += dy
            self.functions.drag_start_x = event.x
            self.functions.drag_start_y = event.y

            # Обновляем позицию внутреннего фрейма
            self.inner_frame.place(x=self.functions.canvas_offset_x, y=self.functions.canvas_offset_y)

    def stop_drag(self, event):
        """Завершение перемещения холста"""
        self.functions.dragging = False
        self.canvas.configure(cursor="")

    def on_mouse_wheel(self, event):
        """Масштабирование колесиком мыши"""
        if event.state & 0x4:  # Ctrl нажат
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            return "break"

    def zoom_in(self):
        """Увеличение масштаба"""
        self.functions.scale_factor *= 1.1
        self.update_zoom()

    def zoom_out(self):
        """Уменьшение масштаба"""
        self.functions.scale_factor /= 1.1
        self.update_zoom()

    def reset_view(self):
        """Сброс масштаба и позиции"""
        self.functions.scale_factor = 1.0
        self.functions.canvas_offset_x = 0
        self.functions.canvas_offset_y = 0
        self.inner_frame.place(x=0, y=0)
        self.update_zoom()

    def update_zoom(self):
        """Обновление масштаба"""
        new_width = int(self.functions.canvas_width * self.functions.scale_factor)
        new_height = int(self.functions.canvas_height * self.functions.scale_factor)
        self.canvas.configure(width=new_width, height=new_height)
        self.update_status()
        self.update_canvas()


def main():
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()