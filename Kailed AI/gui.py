import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import ImageTk, Image
import random
import threading
from functions import pattern_map, effect_map, combine_patterns, apply_effects, hex_to_rgb, random_color

class KaleidAIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kailed AI")
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

        self.current_section = "Рандомное создание"
        self.zoom_factor = 1.0
        self.base_img = None
        self.current_img = None
        self.history = []
        self.effects_vars = {}
        self.preview_canvas = None
        self.gradient_var = None
        self.colors = None
        self.width = 800
        self.height = 600
        self.is_random = True
        self.generating_label = None
        self.dot_count = 0

        self.setup_ui()
        self.setup_styles()
        self.start_dot_animation()

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

        tk.Label(name_frame, text="KAILED", bg=self.card_color,
                 fg=self.accent_color, font=('Arial', 18, 'bold')).pack(anchor="w")
        tk.Label(name_frame, text="AI", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 18, 'bold')).pack(anchor="w")

        separator = tk.Frame(top_sidebar, height=2, bg=self.border_color)
        separator.pack(fill="x", pady=(0, 20))

        nav_frame = tk.Frame(top_sidebar, bg=self.card_color)
        nav_frame.pack(fill="x")

        nav_items = [
            ("Рандомное создание", "", ""),
            ("Пользовательское создание", "", ""),
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

    def show_section(self, section_name):
        self.current_section = section_name
        self.section_title.config(text=section_name)

        for btn in self.nav_buttons:
            if section_name in btn.cget("text"):
                btn.config(fg=self.accent_color, bg="#1a1a2e")
            else:
                btn.config(fg=self.secondary_text, bg=self.card_color)

        self.base_img = None
        self.current_img = None
        self.effects_vars = {}

        if section_name == "Рандомное создание":
            self.is_random = True
            self.setup_random_ui()
        elif section_name == "Пользовательское создание":
            self.is_random = False
            self.setup_custom_ui()
        elif section_name == "История":
            self.setup_history_ui()

    def setup_effects_panel(self, parent):
        effects_label = tk.Label(parent, text="Эффекты", bg=self.card_color, fg=self.text_color,
                                 font=('Arial', 12, 'bold'))
        effects_label.pack(anchor="w", pady=(20, 10))

        effects_canvas = tk.Canvas(parent, bg=self.card_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=effects_canvas.yview)
        effects_frame = tk.Frame(effects_canvas, bg=self.card_color)

        effects_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        effects_canvas.pack(fill="both", expand=True)
        effects_canvas.create_window((0, 0), window=effects_frame, anchor="nw")

        def update_scrollregion(event=None):
            effects_canvas.configure(scrollregion=effects_canvas.bbox("all"))

        effects_frame.bind("<Configure>", update_scrollregion)

        self.effects_vars = {}
        for effect in effect_map.keys():
            var = tk.IntVar()
            check = tk.Checkbutton(effects_frame, text=effect, variable=var, fg=self.text_color, bg=self.card_color,
                                   selectcolor=self.accent_color, font=self.small_font, anchor="w",
                                   command=self.update_preview_effects)
            check.pack(fill="x", pady=4)
            self.effects_vars[effect] = var

        def on_mouse_wheel(event):
            effects_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        effects_canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        effects_canvas.bind_all("<Button-4>", lambda e: effects_canvas.yview_scroll(-1, "units"))
        effects_canvas.bind_all("<Button-5>", lambda e: effects_canvas.yview_scroll(1, "units"))

        return effects_frame

    def setup_random_ui(self):
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        settings_container = tk.Frame(self.settings_frame, bg=self.card_color)
        settings_container.pack(fill="both", expand=True)

        tk.Label(settings_container, text="Размер изображения", bg=self.card_color, fg=self.text_color,
                 font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 10))

        size_frame = tk.Frame(settings_container, bg=self.card_color)
        size_frame.pack(fill="x")

        tk.Label(size_frame, text="Ширина:", bg=self.card_color, fg=self.text_color,
                 font=self.small_font).pack(side=tk.LEFT, padx=5)
        self.width_var = tk.StringVar(value="800")
        width_entry = tk.Entry(size_frame, textvariable=self.width_var, font=self.small_font, width=12,
                               bg=self.border_color, fg=self.text_color, insertbackground=self.text_color)
        width_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(size_frame, text="Высота:", bg=self.card_color, fg=self.text_color,
                 font=self.small_font).pack(side=tk.LEFT, padx=10)
        self.height_var = tk.StringVar(value="600")
        height_entry = tk.Entry(size_frame, textvariable=self.height_var, font=self.small_font, width=12,
                                bg=self.border_color, fg=self.text_color, insertbackground=self.text_color)
        height_entry.pack(side=tk.LEFT, padx=5)

        self.gradient_var = tk.IntVar()
        gradient_check = tk.Checkbutton(settings_container, text="Использовать градиент", variable=self.gradient_var,
                                       fg=self.text_color, bg=self.card_color, selectcolor=self.accent_color,
                                       font=self.small_font)
        gradient_check.pack(anchor="w", pady=10)

        generate_btn = ttk.Button(settings_container, text="Сгенерировать", style='Accent.TButton',
                                  command=self.start_generate_pattern)
        generate_btn.pack(fill="x", pady=20)

        self.setup_effects_panel(settings_container)

        self.preview_canvas = tk.Canvas(self.preview_frame, bg=self.card_color, highlightthickness=0)
        self.preview_canvas.pack(fill="both", expand=True, padx=50, pady=50)
        self.preview_canvas.bind("<MouseWheel>", self.zoom_preview)
        self.preview_canvas.bind("<Button-4>", lambda e: self.zoom_in())
        self.preview_canvas.bind("<Button-5>", lambda e: self.zoom_out())

        control_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        control_frame.pack(fill="x", pady=15)

        zoom_in_btn = ttk.Button(control_frame, text="Увеличить", style='Secondary.TButton', command=self.zoom_in)
        zoom_in_btn.pack(side="left", padx=5)

        zoom_out_btn = ttk.Button(control_frame, text="Уменьшить", style='Secondary.TButton', command=self.zoom_out)
        zoom_out_btn.pack(side="left", padx=5)

        save_btn = ttk.Button(control_frame, text="Сохранить", style='Success.TButton', command=self.save_image)
        save_btn.pack(side="left", padx=5)

        self.generating_label = tk.Label(self.preview_frame, text="Генерируется", bg=self.card_color,
                                         fg=self.text_color, font=self.button_font)
        self.generating_label.pack(pady=15)
        self.generating_label.pack_forget()

    def setup_custom_ui(self):
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        settings_container = tk.Frame(self.settings_frame, bg=self.card_color)
        settings_container.pack(fill="both", expand=True)

        tk.Label(settings_container, text="Узоры", bg=self.card_color, fg=self.text_color,
                 font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 10))

        scrollbar = tk.Scrollbar(settings_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.pattern_listbox = tk.Listbox(settings_container, selectmode=tk.MULTIPLE,
                                          yscrollcommand=scrollbar.set, font=self.small_font,
                                          bg=self.border_color, fg=self.text_color,
                                          selectbackground=self.accent_color, selectforeground=self.text_color,
                                          height=12)
        for pattern in pattern_map.keys():
            self.pattern_listbox.insert(tk.END, pattern)
        self.pattern_listbox.pack(fill=tk.X, pady=10)
        scrollbar.config(command=self.pattern_listbox.yview)

        color_frame = tk.Frame(settings_container, bg=self.card_color)
        color_frame.pack(fill="x", pady=15)

        tk.Label(color_frame, text="Фон:", fg=self.text_color, bg=self.card_color,
                 font=self.small_font).pack(side=tk.LEFT, padx=5)
        self.color1 = "#000000"
        color1_btn = tk.Button(color_frame, bg=self.color1, width=4, command=self.choose_color1, relief="flat")
        color1_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(color_frame, text="Цвет 1:", fg=self.text_color, bg=self.card_color,
                 font=self.small_font).pack(side=tk.LEFT, padx=10)
        self.color2 = "#FFFFFF"
        color2_btn = tk.Button(color_frame, bg=self.color2, width=4, command=self.choose_color2, relief="flat")
        color2_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(color_frame, text="Цвет 2:", fg=self.text_color, bg=self.card_color,
                 font=self.small_font).pack(side=tk.LEFT, padx=10)
        self.color3 = "#FF0000"
        color3_btn = tk.Button(color_frame, bg=self.color3, width=4, command=self.choose_color3, relief="flat")
        color3_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(settings_container, text="Размер изображения", bg=self.card_color, fg=self.text_color,
                 font=('Arial', 12, 'bold')).pack(anchor="w", pady=(15, 10))

        size_frame = tk.Frame(settings_container, bg=self.card_color)
        size_frame.pack(fill="x")

        tk.Label(size_frame, text="Ширина:", bg=self.card_color, fg=self.text_color,
                 font=self.small_font).pack(side=tk.LEFT, padx=5)
        self.width_var = tk.StringVar(value="800")
        width_entry = tk.Entry(size_frame, textvariable=self.width_var, font=self.small_font, width=12,
                               bg=self.border_color, fg=self.text_color, insertbackground=self.text_color)
        width_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(size_frame, text="Высота:", bg=self.card_color, fg=self.text_color,
                 font=self.small_font).pack(side=tk.LEFT, padx=10)
        self.height_var = tk.StringVar(value="600")
        height_entry = tk.Entry(size_frame, textvariable=self.height_var, font=self.small_font, width=12,
                                bg=self.border_color, fg=self.text_color, insertbackground=self.text_color)
        height_entry.pack(side=tk.LEFT, padx=5)

        self.gradient_var = tk.IntVar()
        gradient_check = tk.Checkbutton(settings_container, text="Использовать градиент",
                                       variable=self.gradient_var, fg=self.text_color, bg=self.card_color,
                                       selectcolor=self.accent_color, font=self.small_font)
        gradient_check.pack(anchor="w", pady=10)

        generate_btn = ttk.Button(settings_container, text="Сгенерировать", style='Accent.TButton',
                                  command=self.start_generate_pattern)
        generate_btn.pack(fill="x", pady=20)

        self.setup_effects_panel(settings_container)

        self.preview_canvas = tk.Canvas(self.preview_frame, bg=self.card_color, highlightthickness=0)
        self.preview_canvas.pack(fill="both", expand=True, padx=50, pady=50)
        self.preview_canvas.bind("<MouseWheel>", self.zoom_preview)
        self.preview_canvas.bind("<Button-4>", lambda e: self.zoom_in())
        self.preview_canvas.bind("<Button-5>", lambda e: self.zoom_out())

        control_frame = tk.Frame(self.preview_frame, bg=self.card_color)
        control_frame.pack(fill="x", pady=15)

        zoom_in_btn = ttk.Button(control_frame, text="Увеличить", style='Secondary.TButton', command=self.zoom_in)
        zoom_in_btn.pack(side="left", padx=5)

        zoom_out_btn = ttk.Button(control_frame, text="Уменьшить", style='Secondary.TButton', command=self.zoom_out)
        zoom_out_btn.pack(side="left", padx=5)

        save_btn = ttk.Button(control_frame, text="Сохранить", style='Success.TButton', command=self.save_image)
        save_btn.pack(side="left", padx=5)

        self.generating_label = tk.Label(self.preview_frame, text="Генерируется", bg=self.card_color,
                                         fg=self.text_color, font=self.button_font)
        self.generating_label.pack(pady=15)
        self.generating_label.pack_forget()

    def choose_color1(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.color1 = c
            self.update_color_buttons()

    def choose_color2(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.color2 = c
            self.update_color_buttons()

    def choose_color3(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.color3 = c
            self.update_color_buttons()

    def update_color_buttons(self):
        for widget in self.settings_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button) and child.cget("bg") in [self.color1, self.color2, self.color3]:
                        if child.cget("bg") == self.color1:
                            child.config(bg=self.color1)
                        elif child.cget("bg") == self.color2:
                            child.config(bg=self.color2)
                        elif child.cget("bg") == self.color3:
                            child.config(bg=self.color3)

    def start_dot_animation(self):
        def update_dots():
            dots = "." * self.dot_count
            self.generating_label.config(text=f"Генерируется{dots}")
            self.dot_count = (self.dot_count + 1) % 4
            self.root.after(300, update_dots)
        self.root.after(300, update_dots)

    def start_generate_pattern(self):
        self.generating_label.pack()
        self.root.update()
        threading.Thread(target=self.generate_pattern, daemon=True).start()

    def generate_pattern(self):
        try:
            self.width = int(self.width_var.get())
            self.height = int(self.height_var.get())
            if self.width <= 0 or self.height <= 0:
                raise ValueError
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", "Введите положительные числа для размера."))
            self.root.after(0, self.hide_generating_label)
            return

        if self.is_random:
            num_patterns = random.randint(1, 6)
            pattern_types = random.sample(list(pattern_map.values()), num_patterns)
            self.colors = [random_color() for _ in range(random.randint(3, 8))]
        else:
            selected_indices = self.pattern_listbox.curselection()
            if not selected_indices:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", "Выберите хотя бы один узор."))
                self.root.after(0, self.hide_generating_label)
                return
            pattern_types = [list(pattern_map.values())[i] for i in selected_indices]
            self.colors = [hex_to_rgb(self.color1), hex_to_rgb(self.color2), hex_to_rgb(self.color3)]
            if random.random() > 0.3:
                self.colors.extend([random_color() for _ in range(random.randint(1, 3))])

        use_gradient = self.gradient_var.get() or (random.random() > 0.6 if self.is_random else False)

        self.base_img = combine_patterns(pattern_types, self.colors, self.width, self.height, use_gradient)
        self.root.after(0, self.update_preview_effects)

        if len(self.history) >= 20:
            self.history.pop(0)
        self.history.append({"img": self.base_img.copy(), "patterns": pattern_types, "effects": []})
        self.root.after(0, self.hide_generating_label)

    def hide_generating_label(self):
        self.generating_label.pack_forget()

    def update_preview_effects(self):
        if self.base_img:
            selected_effects = [effect_map[effect] for effect, var in self.effects_vars.items() if var.get()]
            self.current_img = apply_effects(self.base_img, selected_effects)
            self.display_preview(self.current_img, self.preview_canvas)
            if self.history:
                self.history[-1]["effects"] = selected_effects
                self.update_history_ui()

    def setup_history_ui(self):
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        history_frame = tk.Frame(self.settings_frame, bg=self.card_color)
        history_frame.pack(fill="both", expand=True)

        tk.Label(history_frame, text="ИСТОРИЯ", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 16, 'bold')).pack(pady=(0, 20))

        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(history_frame, bg="#1a1a2e", fg=self.text_color,
                                          font=self.small_font, selectmode=tk.SINGLE)
        self.history_listbox.pack(fill="both", expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self.show_history_item)
        scrollbar.config(command=self.history_listbox.yview)

        self.update_history_ui()

        self.history_canvas = tk.Canvas(self.preview_frame, bg="#1a1a2e", highlightthickness=0)
        self.history_canvas.pack(fill="both", expand=True, padx=50, pady=50)

        self.history_info = tk.Label(self.preview_frame, text="Выберите элемент из истории",
                                     bg=self.card_color, fg=self.secondary_text,
                                     font=self.small_font, justify="left")
        self.history_info.pack(anchor="w", pady=(20, 0))

        save_btn = ttk.Button(self.preview_frame, text="Сохранить выбранное", style='Success.TButton',
                              command=self.save_selected_history)
        save_btn.pack(fill="x", pady=15)

    def update_history_ui(self):
        if hasattr(self, 'history_listbox'):
            self.history_listbox.delete(0, tk.END)
            for idx, entry in enumerate(reversed(self.history)):
                patterns = ', '.join([k for k, v in pattern_map.items() if v in entry['patterns']])
                effects = ', '.join([k for k, v in effect_map.items() if v in entry['effects']]) or "Без эффектов"
                item_text = f"Узоры: {patterns}\nЭффекты: {effects}"
                self.history_listbox.insert(tk.END, item_text)

    def show_history_item(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            entry = self.history[len(self.history) - 1 - idx]
            self.history_canvas.delete("all")
            if entry.get('img'):
                img = entry['img'].copy()
                img.thumbnail((400, 400))
                self.history_img_tk = ImageTk.PhotoImage(img)
                canvas_width = self.history_canvas.winfo_width()
                canvas_height = self.history_canvas.winfo_height()
                x = (canvas_width - self.history_img_tk.width()) // 2
                y = (canvas_height - self.history_img_tk.height()) // 2
                self.history_canvas.create_image(x, y, image=self.history_img_tk, anchor="nw")
            patterns = ', '.join([k for k, v in pattern_map.items() if v in entry['patterns']])
            effects = ', '.join([k for k, v in effect_map.items() if v in entry['effects']]) or "Без эффектов"
            self.history_info.config(text=f"Узоры: {patterns}\nЭффекты: {effects}")

    def save_selected_history(self):
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            entry = self.history[len(self.history) - 1 - idx]
            if entry.get('img'):
                self.save_image(entry['img'])

    def display_preview(self, img, canvas):
        canvas.delete("all")
        new_size = (int(img.width * self.zoom_factor), int(img.height * self.zoom_factor))
        zoomed_img = img.resize(new_size, Image.Resampling.LANCZOS)
        self.preview_img_tk = ImageTk.PhotoImage(zoomed_img)
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        x = (canvas_width - self.preview_img_tk.width()) // 2
        y = (canvas_height - self.preview_img_tk.height()) // 2
        canvas.create_image(x, y, image=self.preview_img_tk, anchor="nw")

    def zoom_preview(self, event):
        if event.delta > 0 or event.num == 4:
            self.zoom_in()
        elif event.delta < 0 or event.num == 5:
            self.zoom_out()

    def zoom_in(self):
        self.zoom_factor = min(self.zoom_factor * 1.1, 3.0)
        if self.current_img:
            self.display_preview(self.current_img, self.preview_canvas)

    def zoom_out(self):
        self.zoom_factor = max(self.zoom_factor / 1.1, 0.5)
        if self.current_img:
            self.display_preview(self.current_img, self.preview_canvas)

    def save_image(self, img=None):
        if img is None:
            img = self.current_img
        if img:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                img.save(file_path)
                messagebox.showinfo("Успех", "Изображение успешно сохранено!")