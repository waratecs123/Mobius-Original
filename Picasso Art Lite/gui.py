import tkinter as tk
from tkinter import filedialog, ttk, simpledialog
from PIL import Image, ImageTk, ImageDraw
import os, threading, time
import functions as fn
import traceback

LABELS = {
    'load': 'Загрузить изображение',
    'save': 'Сохранить как...',
    'reset': 'Сбросить',
    'controls': 'Настройки',
    'presets': 'Пресеты',
    'preview': 'Предпросмотр',
    'apply': 'Применить',
    'about': 'О программе',
    'resize': 'Изменить размер',
    'crop': 'Обрезать',
    'zoom': 'Зум',
    'rotate': 'Поворот',
    'brush': 'Кисть (удаление объектов)',
    'bg_blur': 'Кисть (размытие фона)',
    'bg_remove': 'Кисть (удаление фона)',
}

class PicassoGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='#0f0f23')
        self.master = master
        self.pack(fill='both', expand=True)
        self.image = None
        self.preview_image = None
        self.tk_image = None
        self.preset_thumbs = {}
        self.preset_buttons = {}
        self.thumb_refs = []
        self.brush_mask = None
        self.brush_mode = None
        self.brush_points = []
        self.last_cursor_pos = None
        self.brush_cursor_image = None
        self.params = {
            'brightness': 0, 'contrast': 0, 'saturation': 0, 'clarity': 0, 'exposure': 0,
            'sepia': 0, 'invert': 0, 'hue': 0, 'temperature': 0, 'blur': 0,
            'scale': 1.0, 'vignette': 0.0, 'zoom': 1.0, 'rotate': 0,
            'brush_size': 20, 'brush_strength': 100, 'bg_blur_radius': 10, 'bg_remove_strength': 100,
            'crop_x': 0, 'crop_y': 0, 'crop_w': 0, 'crop_h': 0,
            'grain': 0, 'posterize_bits': 8, 'solarize_thresh': 128
        }
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.secondary_accent = "#818cf8"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#0f0f23"
        self.success_color = "#10b981"
        self.gradient_start = "#6366f1"
        self.gradient_end = "#8b5cf6"
        self.title_font = ('Arial', 24, 'bold')
        self.subtitle_font = ('Arial', 16)
        self.app_font = ('Arial', 13)
        self.button_font = ('Arial', 12, 'bold')
        self.small_font = ('Arial', 11)
        self.create_widgets()
        self.after_id = None
        self.crop_start = None
        self.canvas.bind('<Button-1>', self.start_crop_or_brush)
        self.canvas.bind('<B1-Motion>', self.update_crop_or_brush)
        self.canvas.bind('<ButtonRelease-1>', self.end_crop_or_brush)
        self.canvas.bind('<MouseWheel>', self.zoom_canvas)
        self.canvas.bind('<Button-4>', self.zoom_canvas)
        self.canvas.bind('<Button-5>', self.zoom_canvas)
        self.canvas.bind('<Motion>', self.update_brush_cursor)

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
                  background=[('selected', self.accent_color), ('active', self.secondary_accent)],
                  foreground=[('selected', '#FFFFFF'), ('!selected', self.secondary_text)])
        style.configure('Accent.TButton',
                        background=self.accent_color,
                        foreground='white',
                        borderwidth=0,
                        font=self.button_font,
                        padding=(15, 8))
        style.map('Accent.TButton',
                  background=[('active', '#4f46e5')])
        style.configure('Secondary.TButton',
                        background=self.card_color,
                        foreground=self.text_color,
                        borderwidth=0,
                        font=self.button_font,
                        padding=(15, 8))
        style.map('Secondary.TButton',
                  background=[('active', '#374151')])

    def create_widgets(self):
        self.setup_styles()
        w = self.master.winfo_screenwidth()
        left_w = 400
        right_w = w - left_w
        main_container = tk.Frame(self, bg=self.bg_color, padx=20, pady=20)
        main_container.pack(fill='both', expand=True)
        left = tk.Frame(main_container, width=left_w, bg=self.card_color, padx=15, pady=15)
        left.pack(side='left', fill='y')
        left.pack_propagate(False)
        right = tk.Frame(main_container, bg=self.bg_color)
        right.pack(side='right', fill='both', expand=True)
        title_label = tk.Label(left, text='Picasso Art Lite',
                               bg=self.card_color, fg='white',
                               font=self.title_font)
        title_label.pack(fill='x', pady=(0, 20))
        btn_frame = tk.Frame(left, bg=self.card_color)
        btn_frame.pack(fill='x', pady=10)
        ttk.Button(btn_frame, text=LABELS['load'], command=self.load_image,
                   style='Accent.TButton').pack(fill='x', pady=5)
        ttk.Button(btn_frame, text=LABELS['save'], command=self.save_image,
                   style='Accent.TButton').pack(fill='x', pady=5)
        ttk.Button(btn_frame, text=LABELS['reset'], command=self.reset_controls,
                   style='Secondary.TButton').pack(fill='x', pady=5)
        notebook = ttk.Notebook(left, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, pady=15)
        adj_frame = tk.Frame(notebook, bg=self.card_color)
        notebook.add(adj_frame, text='Настройки')
        controls_canvas = tk.Canvas(adj_frame, bg=self.card_color, highlightthickness=0)
        controls_canvas.pack(side='top', fill='both', expand=True)
        controls_inner = tk.Frame(controls_canvas, bg=self.card_color)
        controls_canvas.create_window((0, 0), window=controls_inner, anchor='nw')
        controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))
        controls_inner.bind("<Configure>", lambda e: controls_canvas.configure(scrollregion=controls_canvas.bbox("all")))
        controls_canvas.bind_all("<MouseWheel>", lambda e: controls_canvas.yview_scroll(-1 * int(e.delta / 120), "units"))
        controls_canvas.bind_all("<Button-4>", lambda e: controls_canvas.yview_scroll(-1, "units"))
        controls_canvas.bind_all("<Button-5>", lambda e: controls_canvas.yview_scroll(1, "units"))
        self.sliders = {}
        slider_specs = [
            ('brightness', 'Яркость', -100, 100, 0),
            ('contrast', 'Контраст', -100, 100, 0),
            ('saturation', 'Насыщенность', -100, 100, 0),
            ('clarity', 'Чёткость', -100, 100, 0),
            ('exposure', 'Экспозиция', -100, 100, 0),
            ('sepia', 'Сепия', 0, 100, 0),
            ('invert', 'Инвертировать', 0, 100, 0),
            ('hue', 'Смещение оттенка', -180, 180, 0),
            ('temperature', 'Температура', -100, 100, 0),
            ('blur', 'Размытие', 0, 20, 0),
            ('vignette', 'Виньетка', 0, 100, 0),
            ('grain', 'Зернистость', 0, 50, 0),
            ('posterize_bits', 'Постеризация (биты)', 1, 8, 8),
            ('solarize_thresh', 'Соляризация (порог)', 0, 255, 128),
            ('scale', 'Масштаб (превью)', 0.1, 3.0, 1.0),
            ('zoom', 'Зум', 0.1, 5.0, 1.0),
            ('rotate', 'Поворот (°)', 0, 360, 0),
        ]
        for i, (key, label, mn, mx, default) in enumerate(slider_specs):
            row = tk.Frame(controls_inner, bg=self.card_color)
            row.grid(row=i, column=0, sticky='ew', pady=5)
            tk.Label(row, text=label, width=20, anchor='w', bg=self.card_color,
                     fg=self.secondary_text, font=self.small_font).pack(side='left')
            res = 0.01 if key in ['scale', 'zoom'] else 1
            s = tk.Scale(row, from_=mn, to=mx, resolution=res, orient='horizontal',
                         length=150, command=self.on_slider(key),
                         bg=self.card_color, fg=self.text_color,
                         highlightthickness=0, troughcolor=self.bg_color,
                         activebackground=self.accent_color)
            s.set(default)
            s.pack(side='right')
            self.sliders[key] = s
            self.params[key] = default
        spacer = tk.Frame(controls_inner, bg=self.card_color, height=20)
        spacer.grid(row=len(slider_specs), column=0, sticky='ew')
        controls_inner.grid_columnconfigure(0, weight=1)
        brush_frame = tk.Frame(notebook, bg=self.card_color)
        notebook.add(brush_frame, text='Кисти')
        brush_btn_frame = tk.Frame(brush_frame, bg=self.card_color)
        brush_btn_frame.pack(fill='x', pady=10)
        ttk.Button(brush_btn_frame, text=LABELS['brush'], command=lambda: self.toggle_brush('inpaint'),
                   style='Accent.TButton').pack(fill='x', pady=5)
        ttk.Button(brush_btn_frame, text=LABELS['bg_blur'], command=lambda: self.toggle_brush('bg_blur'),
                   style='Accent.TButton').pack(fill='x', pady=5)
        ttk.Button(brush_btn_frame, text=LABELS['bg_remove'], command=lambda: self.toggle_brush('bg_remove'),
                   style='Accent.TButton').pack(fill='x', pady=5)
        brush_controls = tk.Frame(brush_frame, bg=self.card_color)
        brush_controls.pack(fill='x', pady=10)
        brush_slider_specs = [
            ('brush_size', 'Размер кисти', 1, 100, 20),
            ('brush_strength', 'Сила кисти', 0, 100, 100),
            ('bg_blur_radius', 'Радиус размытия фона', 0, 50, 10),
            ('bg_remove_strength', 'Сила удаления фона', 0, 100, 100),
        ]
        for key, label, mn, mx, default in brush_slider_specs:
            row = tk.Frame(brush_controls, bg=self.card_color)
            row.pack(fill='x', pady=5)
            tk.Label(row, text=label, width=20, anchor='w', bg=self.card_color,
                     fg=self.secondary_text, font=self.small_font).pack(side='left')
            res = 1
            s = tk.Scale(row, from_=mn, to=mx, resolution=res, orient='horizontal',
                         length=150, command=self.on_slider(key),
                         bg=self.card_color, fg=self.text_color,
                         highlightthickness=0, troughcolor=self.bg_color,
                         activebackground=self.accent_color)
            s.set(default)
            s.pack(side='right')
            self.sliders[key] = s
            self.params[key] = default
        preset_frame = tk.Frame(notebook, bg=self.card_color)
        notebook.add(preset_frame, text='Пресеты')
        preset_canvas = tk.Canvas(preset_frame, bg=self.card_color, highlightthickness=0)
        preset_canvas.pack(side='left', fill='both', expand=True)
        preset_scroll = tk.Scrollbar(preset_frame, orient='vertical', command=preset_canvas.yview,
                                     bg=self.card_color, troughcolor=self.bg_color)
        preset_scroll.pack(side='right', fill='y')
        preset_inner = tk.Frame(preset_canvas, bg=self.card_color)
        preset_canvas.create_window((0, 0), window=preset_inner, anchor='nw')
        preset_canvas.configure(yscrollcommand=preset_scroll.set)
        preset_inner.grid_columnconfigure(0, weight=1)
        preset_inner.grid_columnconfigure(1, weight=1)
        for i, name in enumerate(fn.PRESETS.keys()):
            btn = ttk.Button(preset_inner, text=name, command=lambda n=name: self.apply_preset(n),
                             style='Secondary.TButton')
            btn.grid(row=i // 2, column=i % 2, sticky='ew', padx=5, pady=5)
            self.preset_buttons[name] = btn
        preset_inner.bind("<Configure>", lambda e: preset_canvas.configure(scrollregion=preset_canvas.bbox("all")))
        preset_canvas.bind_all("<MouseWheel>", lambda e: preset_canvas.yview_scroll(-1 * int(e.delta / 120), "units"))
        preset_canvas.bind_all("<Button-4>", lambda e: preset_canvas.yview_scroll(-1, "units"))
        preset_canvas.bind_all("<Button-5>", lambda e: preset_canvas.yview_scroll(1, "units"))
        self.canvas = tk.Canvas(right, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

    def on_slider(self, key):
        def update(value):
            self.params[key] = float(value)
            if self.after_id:
                self.after_cancel(self.after_id)
            self.after_id = self.after(100, self.update_preview)
        return update

    def toggle_brush(self, mode):
        if self.image is None:
            print("toggle_brush: No image loaded")
            return
        try:
            if self.brush_mode == mode:
                self.brush_mode = None
                self.brush_mask = None
                self.canvas.delete('brush_cursor')
                self.brush_cursor_image = None
            else:
                self.brush_mode = mode
                self.brush_mask = Image.new('L', self.image.size, 0)
                self.brush_points = []
            self.update_preview()
        except Exception as e:
            print(f"toggle_brush: Error - {traceback.format_exc()}")

    def start_crop_or_brush(self, event):
        if self.image is None:
            print("start_crop_or_brush: No image loaded")
            return
        try:
            if self.brush_mode:
                self.brush_points.append((event.x, event.y))
                self.last_cursor_pos = (event.x, event.y)
                self.update_brush_mask(event)
            else:
                self.crop_start = (event.x, event.y)
                self.canvas.delete('crop_rect')
        except Exception as e:
            print(f"start_crop_or_brush: Error - {traceback.format_exc()}")

    def update_crop_or_brush(self, event):
        if self.image is None:
            print("update_crop_or_brush: No image loaded")
            return
        try:
            if self.brush_mode:
                self.brush_points.append((event.x, event.y))
                self.last_cursor_pos = (event.x, event.y)
                self.update_brush_mask(event)
            elif self.crop_start:
                x0, y0 = self.crop_start
                x1, y1 = event.x, event.y
                self.canvas.delete('crop_rect')
                self.canvas.create_rectangle(x0, y0, x1, y1, outline=self.accent_color, width=2, tags='crop_rect')
        except Exception as e:
            print(f"update_crop_or_brush: Error - {traceback.format_exc()}")

    def end_crop_or_brush(self, event):
        if self.image is None:
            print("end_crop_or_brush: No image loaded")
            return
        try:
            if self.brush_mode:
                self.apply_brush()
            elif self.crop_start:
                x0, y0 = self.crop_start
                x1, y1 = event.x, event.y
                cw = max(1, self.canvas.winfo_width() or 800)
                ch = max(1, self.canvas.winfo_height() or 600)
                iw, ih = self.image.size
                scale = min(max(0.05, min(cw / iw, ch / ih)), 5.0) * self.params['zoom']
                offset_x = (cw - iw * scale) / 2
                offset_y = (ch - ih * scale) / 2
                img_x0 = int((min(x0, x1) - offset_x) / scale)
                img_y0 = int((min(y0, y1) - offset_y) / scale)
                img_x1 = int((max(x0, x1) - offset_x) / scale)
                img_y1 = int((max(y0, y1) - offset_y) / scale)
                img_x0 = max(0, min(iw - 1, img_x0))
                img_y0 = max(0, min(ih - 1, img_y0))
                img_x1 = max(0, min(iw - 1, img_x1))
                img_y1 = max(0, min(ih - 1, img_y1))
                self.params['crop_x'] = img_x0
                self.params['crop_y'] = img_y0
                self.params['crop_w'] = img_x1 - img_x0
                self.params['crop_h'] = img_y1 - img_y0
                self.canvas.delete('crop_rect')
                self.crop_start = None
                self.update_preview()
        except Exception as e:
            print(f"end_crop_or_brush: Error - {traceback.format_exc()}")

    def update_brush_cursor(self, event=None, x=None, y=None):
        if self.image is None or not self.brush_mode:
            self.canvas.delete('brush_cursor')
            return
        try:
            x = x or event.x
            y = y or event.y
            brush_size = max(1, int(self.params['brush_size'] / self.params['zoom']))
            cursor = Image.new('RGBA', (brush_size * 2, brush_size * 2), (0, 0, 0, 0))
            draw = ImageDraw.Draw(cursor)
            draw.ellipse((0, 0, brush_size * 2, brush_size * 2), outline=self.accent_color, width=2)
            self.brush_cursor_image = ImageTk.PhotoImage(cursor)
            self.canvas.delete('brush_cursor')
            self.canvas.create_image(x, y, image=self.brush_cursor_image, tags='brush_cursor')
        except Exception as e:
            print(f"update_brush_cursor: Error - {traceback.format_exc()}")

    def update_brush_mask(self, event):
        if not self.brush_points or not self.brush_mode or not self.image:
            print("update_brush_mask: Invalid state (no points, mode, or image)")
            return
        try:
            draw = ImageDraw.Draw(self.brush_mask)
            brush_size = max(1, int(self.params['brush_size'] / self.params['zoom']))
            brush_strength = int(self.params['brush_strength'] * 2.55)
            cw = max(1, self.canvas.winfo_width() or 800)
            ch = max(1, self.canvas.winfo_height() or 600)
            iw, ih = self.image.size
            scale = min(max(0.05, min(cw / iw, ch / ih)), 5.0) * self.params['zoom']
            offset_x = (cw - iw * scale) / 2
            offset_y = (ch - ih * scale) / 2
            def canvas_to_image(x, y):
                img_x = int((x - offset_x) / scale)
                img_y = int((y - offset_y) / scale)
                img_x = max(0, min(iw - 1, img_x))
                img_y = max(0, min(ih - 1, img_y))
                return img_x, img_y
            for i in range(len(self.brush_points) - 1):
                x0, y0 = self.brush_points[i]
                x1, y1 = self.brush_points[i + 1]
                x0_img, y0_img = canvas_to_image(x0, y0)
                x1_img, y1_img = canvas_to_image(x1, y1)
                draw.line((x0_img, y0_img, x1_img, y1_img), fill=brush_strength, width=brush_size)
                draw.ellipse((x0_img - brush_size // 2, y0_img - brush_size // 2,
                              x0_img + brush_size // 2, y0_img + brush_size // 2),
                             fill=brush_strength)
                draw.ellipse((x1_img - brush_size // 2, y1_img - brush_size // 2,
                              x1_img + brush_size // 2, y1_img + brush_size // 2),
                             fill=brush_strength)
            self.update_preview()
        except Exception as e:
            print(f"update_brush_mask: Error - {traceback.format_exc()}")

    def apply_brush(self):
        if self.image is None or self.brush_mask is None:
            print("apply_brush: No image or mask available")
            return
        try:
            if self.brush_mode == 'inpaint':
                self.image = fn.apply_inpaint(self.image, self.brush_mask)
            elif self.brush_mode == 'bg_blur':
                self.image = fn.apply_background_blur(self.image, self.brush_mask, self.params['bg_blur_radius'])
            elif self.brush_mode == 'bg_remove':
                self.image = fn.apply_background_remove(self.image, self.brush_mask, self.params['bg_remove_strength'])
            self.brush_mask = Image.new('L', self.image.size, 0)
            self.brush_points = []
            self.update_preview()
        except Exception as e:
            print(f"apply_brush: Error - {traceback.format_exc()}")

    def zoom_canvas(self, event):
        if self.image is None:
            print("zoom_canvas: No image loaded")
            return
        try:
            delta = 0.1 if event.delta > 0 or event.num == 4 else -0.1
            new_zoom = max(0.1, min(5.0, self.params['zoom'] + delta))
            self.params['zoom'] = new_zoom
            self.sliders['zoom'].set(new_zoom)
            self.update_preview()
        except Exception as e:
            print(f"zoom_canvas: Error - {traceback.format_exc()}")

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[('Изображения', '*.png;*.jpg;*.jpeg;*.bmp;*.tiff')])
        if not path:
            return
        try:
            img = Image.open(path)
            self.image = img.convert('RGB')
            self.brush_mask = None
            self.brush_mode = None
            self.canvas.delete('brush_cursor')
            self.brush_cursor_image = None
            self.reset_controls()
            self.update_preview()
            threading.Thread(target=self.generate_preset_thumbnails, daemon=True).start()
        except Exception as e:
            print(f"load_image: Error - {traceback.format_exc()}")

    def save_image(self):
        if self.preview_image is None:
            print("save_image: No preview image available")
            return
        try:
            size_dialog = tk.Toplevel(self.master)
            size_dialog.title("Выберите размер изображения")
            size_dialog.geometry("300x300")
            size_dialog.configure(bg=self.card_color)
            size_dialog.transient(self.master)
            size_dialog.grab_set()
            tk.Label(size_dialog, text="Выберите размер:", bg=self.card_color, fg=self.text_color, font=self.app_font).pack(pady=10)
            sizes = [
                ("Оригинальный размер", None),
                ("1920x1080 (Full HD)", (1920, 1080)),
                ("1280x720 (HD)", (1280, 720)),
                ("800x600", (800, 600)),
                ("Пользовательский", "custom")
            ]
            selected_size = tk.StringVar(value="Оригинальный размер")
            for label, _ in sizes:
                tk.Radiobutton(size_dialog, text=label, variable=selected_size, value=label, bg=self.card_color, fg=self.text_color, selectcolor=self.bg_color, font=self.small_font).pack(anchor='w', padx=20)
            custom_frame = tk.Frame(size_dialog, bg=self.card_color)
            custom_frame.pack(pady=10)
            tk.Label(custom_frame, text="Ширина:", bg=self.card_color, fg=self.text_color, font=self.small_font).pack(side='left')
            width_entry = tk.Entry(custom_frame, width=10, bg=self.bg_color, fg=self.text_color, insertbackground=self.text_color)
            width_entry.pack(side='left', padx=5)
            tk.Label(custom_frame, text="Высота:", bg=self.card_color, fg=self.text_color, font=self.small_font).pack(side='left')
            height_entry = tk.Entry(custom_frame, width=10, bg=self.bg_color, fg=self.text_color, insertbackground=self.text_color)
            height_entry.pack(side='left', padx=5)
            preserve_aspect = tk.BooleanVar(value=True)
            tk.Checkbutton(custom_frame, text="Сохранить пропорции", variable=preserve_aspect, bg=self.card_color, fg=self.text_color, selectcolor=self.bg_color, font=self.small_font).pack(pady=5)
            def update_height(*args):
                if preserve_aspect.get() and width_entry.get().isdigit():
                    orig_w, orig_h = self.preview_image.size
                    try:
                        new_width = int(width_entry.get())
                        new_height = int(new_width * orig_h / orig_w)
                        height_entry.delete(0, tk.END)
                        height_entry.insert(0, str(new_height))
                    except:
                        pass
            def update_width(*args):
                if preserve_aspect.get() and height_entry.get().isdigit():
                    orig_w, orig_h = self.preview_image.size
                    try:
                        new_height = int(height_entry.get())
                        new_width = int(new_height * orig_w / orig_h)
                        width_entry.delete(0, tk.END)
                        width_entry.insert(0, str(new_width))
                    except:
                        pass
            width_entry.bind("<KeyRelease>", update_height)
            height_entry.bind("<KeyRelease>", update_width)
            def confirm_size():
                nonlocal img_to_save
                selected = selected_size.get()
                if selected == "Оригинальный размер":
                    img_to_save = self.preview_image
                elif selected == "Пользовательский":
                    try:
                        width = int(width_entry.get())
                        height = int(height_entry.get())
                        if width > 0 and height > 0:
                            img_to_save = self.preview_image.resize((width, height), Image.LANCZOS)
                        else:
                            tk.messagebox.showerror("Ошибка", "Ширина и высота должны быть больше 0.")
                            return
                    except:
                        tk.messagebox.showerror("Ошибка", "Введите корректные числовые значения для ширины и высоты.")
                        return
                else:
                    for label, size in sizes:
                        if label == selected and size:
                            img_to_save = self.preview_image.resize(size, Image.LANCZOS)
                            break
                size_dialog.destroy()
            img_to_save = self.preview_image
            tk.Button(size_dialog, text="Подтвердить", command=confirm_size, bg=self.accent_color, fg='white', font=self.button_font).pack(pady=10)
            self.master.wait_window(size_dialog)
            filetypes = [('JPEG', '*.jpg'), ('PNG', '*.png'), ('BMP', '*.bmp'), ('TIFF', '*.tiff')]
            path = filedialog.asksaveasfilename(defaultextension='.jpg', filetypes=filetypes)
            if not path:
                return
            img_to_save.save(path)
            print(f"save_image: Saved to {os.path.abspath(path)}")
        except Exception as e:
            print(f"save_image: Error - {traceback.format_exc()}")

    def reset_controls(self):
        try:
            for k, s in self.sliders.items():
                if k in ['scale', 'zoom']:
                    s.set(1.0)
                    self.params[k] = 1.0
                elif k == 'brush_size':
                    s.set(20)
                    self.params[k] = 20
                elif k == 'brush_strength':
                    s.set(100)
                    self.params[k] = 100
                elif k == 'bg_blur_radius':
                    s.set(10)
                    self.params[k] = 10
                elif k == 'bg_remove_strength':
                    s.set(100)
                    self.params[k] = 100
                elif k == 'posterize_bits':
                    s.set(8)
                    self.params[k] = 8
                elif k == 'solarize_thresh':
                    s.set(128)
                    self.params[k] = 128
                else:
                    s.set(0)
                    self.params[k] = 0
            self.brush_mode = None
            self.brush_mask = None
            self.canvas.delete('brush_cursor')
            self.brush_cursor_image = None
            self.update_preview()
        except Exception as e:
            print(f"reset_controls: Error - {traceback.format_exc()}")

    def apply_preset(self, name):
        try:
            preset = fn.PRESETS.get(name, {})
            for k in list(self.params.keys()):
                if k in preset and not preset.get('special'):
                    self.params[k] = preset[k]
                    if k in self.sliders:
                        self.sliders[k].set(preset[k])
            self.params.update(preset)
            self.update_preview()
        except Exception as e:
            print(f"apply_preset: Error - {traceback.format_exc()}")

    def update_preview(self):
        if self.image is None:
            print("update_preview: No image loaded")
            self.canvas.delete('all')
            return
        try:
            img = fn.render_preview(self.image, self.params)
            if img is None:
                print("update_preview: render_preview returned None")
                self.canvas.delete('all')
                return
            if self.brush_mode and self.brush_mask:
                if self.brush_mode == 'inpaint':
                    img = fn.apply_inpaint(img, self.brush_mask)
                elif self.brush_mode == 'bg_blur':
                    img = fn.apply_background_blur(img, self.brush_mask, self.params['bg_blur_radius'])
                elif self.brush_mode == 'bg_remove':
                    img = fn.apply_background_remove(img, self.brush_mask, self.params['bg_remove_strength'])
            cw = max(1, self.canvas.winfo_width() or 800)
            ch = max(1, self.canvas.winfo_height() or 600)
            iw, ih = img.size
            scale = min(max(0.05, min(cw / iw, ch / ih)), 5.0) * self.params['zoom']
            disp = img.resize((max(1, int(iw * scale)), max(1, int(ih * scale))), Image.LANCZOS)
            self.preview_image = img
            self.tk_image = ImageTk.PhotoImage(disp)
            self.canvas.delete('all')
            self.canvas.create_image(cw // 2, ch // 2, image=self.tk_image)
            self.canvas.create_text(12, 12, anchor='nw', text=f'{img.size[0]}×{img.size[1]}',
                                    fill=self.secondary_text, font=self.small_font)
            if self.brush_mode and self.last_cursor_pos:
                self.update_brush_cursor(x=self.last_cursor_pos[0], y=self.last_cursor_pos[1])
        except Exception as e:
            print(f"update_preview: Error - {traceback.format_exc()}")

    def generate_preset_thumbnails(self):
        if self.image is None:
            print("generate_preset_thumbnails: No image loaded")
            return
        for name, preset in fn.PRESETS.items():
            try:
                thumb = fn.make_thumbnail_for_preset(self.image, preset, thumb_size=(160, 120))
                if thumb is None:
                    print(f"generate_preset_thumbnails: Failed to create thumbnail for {name}")
                    continue
                tk_thumb = ImageTk.PhotoImage(thumb)
                self.master.after(0, lambda: self._set_preset_thumbnail(name, tk_thumb))
                self.thumb_refs.append(tk_thumb)
                time.sleep(0.06)
            except Exception as e:
                print(f"generate_preset_thumbnails: Error for {name} - {traceback.format_exc()}")

    def _set_preset_thumbnail(self, name, tk_thumb):
        try:
            btn = self.preset_buttons.get(name)
            if btn:
                btn.configure(image=tk_thumb, compound='top', text=name)
                self.preset_thumbs[name] = tk_thumb
        except Exception as e:
            print(f"_set_preset_thumbnail: Error for {name} - {traceback.format_exc()}")

    def apply_and_save_dialog(self):
        if self.image is None:
            print("apply_and_save_dialog: No image loaded")
            return
        try:
            res = fn.render_preview(self.image, self.params)
            if self.brush_mode and self.brush_mask:
                if self.brush_mode == 'inpaint':
                    res = fn.apply_inpaint(res, self.brush_mask)
                elif self.brush_mode == 'bg_blur':
                    res = fn.apply_background_blur(res, self.brush_mask, self.params['bg_blur_radius'])
                elif self.brush_mode == 'bg_remove':
                    res = fn.apply_background_remove(res, self.brush_mask, self.params['bg_remove_strength'])
            filetypes = [('JPEG', '*.jpg'), ('PNG', '*.png'), ('BMP', '*.bmp'), ('TIFF', '*.tiff')]
            path = filedialog.asksaveasfilename(defaultextension='.jpg', filetypes=filetypes)
            if not path:
                return
            res.save(path)
            self.image = res
            self.brush_mask = None
            self.brush_mode = None
            self.canvas.delete('brush_cursor')
            self.brush_cursor_image = None
            print(f"apply_and_save_dialog: Saved to {path}")
            self.update_preview()
        except Exception as e:
            print(f"apply_and_save_dialog: Error - {traceback.format_exc()}")