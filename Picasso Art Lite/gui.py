import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
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
    'undo': 'Отменить'
}

class PicassoGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg='#0f0f23')
        self.master = master
        self.pack(fill='both', expand=True)
        self.original_image = None
        self.image = None
        self.preview_image = None
        self.tk_image = None
        self.preset_thumbs = {}
        self.preset_buttons = {}
        self.thumb_refs = []
        self.history = []
        self.params = {
            'brightness': 0, 'contrast': 0, 'saturation': 0, 'clarity': 0, 'exposure': 0,
            'sepia': 0, 'invert': 0, 'hue': 0, 'temperature': 0, 'tint': 0,
            'gamma': 1.0, 'highlights': 0, 'shadows': 0, 'whites': 0, 'blacks': 0,
            'vibrance': 0, 'fade': 0, 'curve': 0, 'color_balance': 0, 'selective_color': 0,
            'scale': 1.0, 'zoom': 1.0, 'rotate': 0,
            'crop_x': 0, 'crop_y': 0, 'crop_w': 0, 'crop_h': 0,
            'blur': 0, 'vignette': 0.0, 'grain': 0, 'posterize_bits': 8, 'solarize_thresh': 128,
            'emboss': 0, 'edge_enhance': 0, 'contour': 0, 'sharpen': 0,
            'mirror': False, 'flip': False,
            'find_edges': 0, 'smooth': 0, 'unsharp_radius': 0, 'unsharp_percent': 150, 'unsharp_threshold': 3,
            'median_size': 1, 'box_radius': 0, 'min_size': 1, 'max_size': 1, 'mode_size': 1,
            'rank_size': 1, 'rank': 0, 'detail': 0, 'edge_detect': 0, 'bilateral_sigma_color': 0,
            'bilateral_sigma_space': 75, 'cartoon': 0, 'oil_radius': 0, 'watercolor': 0, 'sketch': 0,
            'grayscale': 0, 'glitch_intensity': 0, 'glitch_slices': 8
        }
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.secondary_accent = "#818cf8"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#0f0f23"
        self.success_color = "#10b981"
        self.title_font = ('Arial', 24, 'bold')
        self.subtitle_font = ('Arial', 16)
        self.app_font = ('Arial', 13)
        self.button_font = ('Arial', 12, 'bold')
        self.small_font = ('Arial', 11)
        self.create_widgets()
        self.after_id = None
        self.crop_start = None
        self.canvas.bind('<Button-1>', self.start_crop)
        self.canvas.bind('<B1-Motion>', self.update_crop)
        self.canvas.bind('<ButtonRelease-1>', self.end_crop)
        self.canvas.bind('<MouseWheel>', self.zoom_canvas)
        self.canvas.bind('<Button-4>', self.zoom_canvas)
        self.canvas.bind('<Button-5>', self.zoom_canvas)

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
        ttk.Button(btn_frame, text=LABELS['apply'], command=self.apply_changes,
                   style='Accent.TButton').pack(fill='x', pady=5)
        ttk.Button(btn_frame, text=LABELS['undo'], command=self.undo_last,
                   style='Secondary.TButton').pack(fill='x', pady=5)
        notebook = ttk.Notebook(left, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, pady=15)
        color_frame = tk.Frame(notebook, bg=self.card_color)
        notebook.add(color_frame, text='Настройки цвета')
        color_canvas = tk.Canvas(color_frame, bg=self.card_color, highlightthickness=0)
        color_canvas.pack(side='left', fill='both', expand=True)
        color_scroll = tk.Scrollbar(color_frame, orient='vertical', command=color_canvas.yview,
                                    bg=self.card_color, troughcolor=self.bg_color)
        color_scroll.pack(side='right', fill='y')
        color_inner = tk.Frame(color_canvas, bg=self.card_color)
        color_canvas.create_window((0, 0), window=color_inner, anchor='nw')
        color_canvas.configure(yscrollcommand=color_scroll.set)
        color_inner.bind("<Configure>", lambda e: color_canvas.configure(scrollregion=color_canvas.bbox("all")))
        color_canvas.bind_all("<MouseWheel>", lambda e: color_canvas.yview_scroll(-1 * int(e.delta / 120), "units"))
        color_canvas.bind_all("<Button-4>", lambda e: color_canvas.yview_scroll(-1, "units"))
        color_canvas.bind_all("<Button-5>", lambda e: color_canvas.yview_scroll(1, "units"))
        self.sliders = {}
        color_slider_specs = [
            ('brightness', 'Яркость', -100, 100, 0),
            ('contrast', 'Контраст', -100, 100, 0),
            ('saturation', 'Насыщенность', -100, 100, 0),
            ('clarity', 'Чёткость', -100, 100, 0),
            ('exposure', 'Экспозиция', -100, 100, 0),
            ('sepia', 'Сепия', 0, 100, 0),
            ('invert', 'Инвертировать', 0, 100, 0),
            ('hue', 'Смещение оттенка', -180, 180, 0),
            ('temperature', 'Температура', -100, 100, 0),
            ('tint', 'Тон', -100, 100, 0),
            ('gamma', 'Гамма', 0.1, 5.0, 1.0),
            ('highlights', 'Света', -100, 100, 0),
            ('shadows', 'Тени', -100, 100, 0),
            ('whites', 'Белые', -100, 100, 0),
            ('blacks', 'Чёрные', -100, 100, 0),
            ('vibrance', 'Вибрация', -100, 100, 0),
            ('fade', 'Выцветание', 0, 100, 0),
            ('curve', 'Кривая', -100, 100, 0),
            ('color_balance', 'Баланс цвета', -100, 100, 0),
            ('selective_color', 'Выборочный цвет', -100, 100, 0),
            ('grayscale', 'Черно-белый', 0, 100, 0)
        ]
        for i, (key, label, mn, mx, default) in enumerate(color_slider_specs):
            row = tk.Frame(color_inner, bg=self.card_color)
            row.grid(row=i, column=0, sticky='ew', pady=5)
            tk.Label(row, text=label, width=20, anchor='w', bg=self.card_color,
                     fg=self.secondary_text, font=self.small_font).pack(side='left')
            res = 0.01 if key == 'gamma' else 1
            s = tk.Scale(row, from_=mn, to=mx, resolution=res, orient='horizontal',
                         length=150, command=self.on_slider(key),
                         bg=self.card_color, fg=self.text_color,
                         highlightthickness=0, troughcolor=self.bg_color,
                         activebackground=self.accent_color)
            s.set(default)
            s.pack(side='right')
            self.sliders[key] = s
            self.params[key] = default
        mirror_var = tk.BooleanVar(value=False)
        tk.Checkbutton(color_inner, text='Зеркальное отражение', variable=mirror_var,
                       command=lambda: self.set_param('mirror', mirror_var.get()),
                       bg=self.card_color, fg=self.text_color,
                       selectcolor=self.bg_color).grid(row=len(color_slider_specs), column=0, sticky='w', pady=5)
        flip_var = tk.BooleanVar(value=False)
        tk.Checkbutton(color_inner, text='Перевернуть вертикально', variable=flip_var,
                       command=lambda: self.set_param('flip', flip_var.get()),
                       bg=self.card_color, fg=self.text_color,
                       selectcolor=self.bg_color).grid(row=len(color_slider_specs)+1, column=0, sticky='w', pady=5)
        spacer = tk.Frame(color_inner, bg=self.card_color, height=20)
        spacer.grid(row=len(color_slider_specs)+2, column=0, sticky='ew')
        color_inner.grid_columnconfigure(0, weight=1)
        effects_frame = tk.Frame(notebook, bg=self.card_color)
        notebook.add(effects_frame, text='Эффекты')
        effects_canvas = tk.Canvas(effects_frame, bg=self.card_color, highlightthickness=0)
        effects_canvas.pack(side='left', fill='both', expand=True)
        effects_scroll = tk.Scrollbar(effects_frame, orient='vertical', command=effects_canvas.yview,
                                      bg=self.card_color, troughcolor=self.bg_color)
        effects_scroll.pack(side='right', fill='y')
        effects_inner = tk.Frame(effects_canvas, bg=self.card_color)
        effects_canvas.create_window((0, 0), window=effects_inner, anchor='nw')
        effects_canvas.configure(yscrollcommand=effects_scroll.set)
        effects_inner.bind("<Configure>", lambda e: effects_canvas.configure(scrollregion=effects_canvas.bbox("all")))
        effects_canvas.bind_all("<MouseWheel>", lambda e: effects_canvas.yview_scroll(-1 * int(e.delta / 120), "units"))
        effects_canvas.bind_all("<Button-4>", lambda e: effects_canvas.yview_scroll(-1, "units"))
        effects_canvas.bind_all("<Button-5>", lambda e: effects_canvas.yview_scroll(1, "units"))
        effects_slider_specs = [
            ('blur', 'Размытие', 0, 20, 0),
            ('vignette', 'Виньетка', 0, 100, 0),
            ('grain', 'Зернистость', 0, 50, 0),
            ('posterize_bits', 'Постеризация (биты)', 1, 8, 8),
            ('solarize_thresh', 'Соляризация (порог)', 0, 255, 128),
            ('emboss', 'Эмбосс', 0, 100, 0),
            ('edge_enhance', 'Усиление краёв', 0, 100, 0),
            ('contour', 'Контур', 0, 100, 0),
            ('sharpen', 'Резкость', 0, 100, 0),
            ('find_edges', 'Обнаружение краёв', 0, 100, 0),
            ('smooth', 'Сглаживание', 0, 100, 0),
            ('unsharp_radius', 'Unsharp Mask (радиус)', 0, 10, 0),
            ('median_size', 'Медианный фильтр (размер)', 1, 9, 1),
            ('box_radius', 'Box Blur (радиус)', 0, 20, 0),
            ('min_size', 'Min Filter (размер)', 1, 9, 1),
            ('max_size', 'Max Filter (размер)', 1, 9, 1),
            ('mode_size', 'Mode Filter (размер)', 1, 9, 1),
            ('rank_size', 'Rank Filter (размер)', 1, 9, 1),
            ('detail', 'Детализация', 0, 100, 0),
            ('edge_detect', 'Обнаружение краёв (усиленное)', 0, 100, 0),
            ('bilateral_sigma_color', 'Билатеральный фильтр (цвет)', 0, 150, 0),
            ('cartoon', 'Карикатура', 0, 100, 0),
            ('oil_radius', 'Масляная живопись (радиус)', 0, 10, 0),
            ('watercolor', 'Акварель', 0, 100, 0),
            ('sketch', 'Эскиз', 0, 100, 0),
            ('glitch_intensity', 'Глитч (интенсивность)', 0, 20, 0),
            ('glitch_slices', 'Глитч (срезы)', 1, 20, 8)
        ]
        for i, (key, label, mn, mx, default) in enumerate(effects_slider_specs):
            row = tk.Frame(effects_inner, bg=self.card_color)
            row.grid(row=i, column=0, sticky='ew', pady=5)
            tk.Label(row, text=label, width=20, anchor='w', bg=self.card_color,
                     fg=self.secondary_text, font=self.small_font).pack(side='left')
            res = 0.1 if 'radius' in key else 1
            s = tk.Scale(row, from_=mn, to=mx, resolution=res, orient='horizontal',
                         length=150, command=self.on_slider(key),
                         bg=self.card_color, fg=self.text_color,
                         highlightthickness=0, troughcolor=self.bg_color,
                         activebackground=self.accent_color)
            s.set(default)
            s.pack(side='right')
            self.sliders[key] = s
            self.params[key] = default
        spacer = tk.Frame(effects_inner, bg=self.card_color, height=20)
        spacer.grid(row=len(effects_slider_specs), column=0, sticky='ew')
        effects_inner.grid_columnconfigure(0, weight=1)
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

    def set_param(self, key, value):
        self.params[key] = value
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(100, self.update_preview)

    def on_slider(self, key):
        def update(value):
            self.params[key] = float(value)
            if self.after_id:
                self.after_cancel(self.after_id)
            self.after_id = self.after(100, self.update_preview)
        return update

    def start_crop(self, event):
        if self.image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение")
            return
        try:
            self.crop_start = (event.x, event.y)
            self.canvas.delete('crop_rect')
        except Exception as e:
            print(f"start_crop: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка при начале обрезки: {str(e)}")

    def update_crop(self, event):
        if self.image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение")
            return
        try:
            if self.crop_start:
                x0, y0 = self.crop_start
                x1, y1 = event.x, event.y
                self.canvas.delete('crop_rect')
                self.canvas.create_rectangle(x0, y0, x1, y1, outline=self.accent_color, width=2, tags='crop_rect')
        except Exception as e:
            print(f"update_crop: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка при обновлении обрезки: {str(e)}")

    def end_crop(self, event):
        if self.image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение")
            return
        try:
            if self.crop_start:
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
                if img_x1 > img_x0 and img_y1 > img_y0:
                    self.history.append(self.image.copy())
                    self.image = fn.crop_image(self.image, img_x0, img_y0, img_x1 - img_x0, img_y1 - img_y0)
                self.canvas.delete('crop_rect')
                self.crop_start = None
                self.update_preview()
        except Exception as e:
            print(f"end_crop: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка при завершении обрезки: {str(e)}")

    def zoom_canvas(self, event):
        if self.image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение")
            return
        try:
            delta = 0.1 if event.delta > 0 or event.num == 4 else -0.1
            new_zoom = max(0.1, min(5.0, self.params['zoom'] + delta))
            self.params['zoom'] = new_zoom
            self.update_preview()
        except Exception as e:
            print(f"zoom_canvas: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка при зумировании: {str(e)}")

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[('Изображения', '*.png;*.jpg;*.jpeg;*.bmp;*.tiff')])
        if not path:
            return
        try:
            self.original_image = Image.open(path)
            self.image = self.original_image.convert('RGB')
            self.history = [self.image.copy()]
            self.canvas.delete('crop_rect')
            self.reset_controls()
            self.update_preview()
            threading.Thread(target=self.generate_preset_thumbnails, daemon=True).start()
        except Exception as e:
            print(f"load_image: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")

    def save_image(self):
        if self.preview_image is None:
            messagebox.showerror("Ошибка", "Нет изображения для сохранения")
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
                tk.Radiobutton(size_dialog, text=label, variable=selected_size, value=label,
                               bg=self.card_color, fg=self.text_color, selectcolor=self.bg_color,
                               font=self.small_font).pack(anchor='w', padx=20)
            custom_frame = tk.Frame(size_dialog, bg=self.card_color)
            custom_frame.pack(pady=10)
            tk.Label(custom_frame, text="Ширина:", bg=self.card_color, fg=self.text_color,
                     font=self.small_font).pack(side='left')
            width_entry = tk.Entry(custom_frame, width=10, bg=self.bg_color, fg=self.text_color,
                                   insertbackground=self.text_color)
            width_entry.pack(side='left', padx=5)
            tk.Label(custom_frame, text="Высота:", bg=self.card_color, fg=self.text_color,
                     font=self.small_font).pack(side='left')
            height_entry = tk.Entry(custom_frame, width=10, bg=self.bg_color, fg=self.text_color,
                                    insertbackground=self.text_color)
            height_entry.pack(side='left', padx=5)
            preserve_aspect = tk.BooleanVar(value=True)
            tk.Checkbutton(custom_frame, text="Сохранить пропорции", variable=preserve_aspect,
                           bg=self.card_color, fg=self.text_color, selectcolor=self.bg_color,
                           font=self.small_font).pack(pady=5)
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
                            messagebox.showerror("Ошибка", "Ширина и высота должны быть больше 0.")
                            return
                    except:
                        messagebox.showerror("Ошибка", "Введите корректные числовые значения для ширины и высоты.")
                        return
                else:
                    for label, size in sizes:
                        if label == selected and size:
                            img_to_save = self.preview_image.resize(size, Image.LANCZOS)
                            break
                size_dialog.destroy()
            img_to_save = self.preview_image
            tk.Button(size_dialog, text="Подтвердить", command=confirm_size,
                      bg=self.accent_color, fg='white', font=self.button_font).pack(pady=10)
            self.master.wait_window(size_dialog)
            filetypes = [('JPEG', '*.jpg'), ('PNG', '*.png'), ('BMP', '*.bmp'), ('TIFF', '*.tiff')]
            path = filedialog.asksaveasfilename(defaultextension='.jpg', filetypes=filetypes)
            if not path:
                return
            img_to_save.save(path)
            print(f"save_image: Saved to {os.path.abspath(path)}")
        except Exception as e:
            print(f"save_image: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {str(e)}")

    def reset_controls(self):
        try:
            if self.original_image is not None:
                self.image = self.original_image.copy().convert('RGB')
                self.history = [self.image.copy()]
            for k, s in self.sliders.items():
                if k in ['scale', 'zoom', 'gamma']:
                    s.set(1.0)
                    self.params[k] = 1.0
                elif k == 'posterize_bits':
                    s.set(8)
                    self.params[k] = 8
                elif k == 'solarize_thresh':
                    s.set(128)
                    self.params[k] = 128
                elif k in ['median_size', 'min_size', 'max_size', 'mode_size', 'rank_size']:
                    s.set(1)
                    self.params[k] = 1
                elif k in ['unsharp_radius', 'box_radius', 'find_edges', 'smooth', 'detail', 'edge_detect', 'bilateral_sigma_color', 'cartoon', 'oil_radius', 'watercolor', 'sketch', 'vignette', 'blur', 'grain', 'emboss', 'edge_enhance', 'contour', 'sharpen', 'glitch_intensity', 'glitch_slices']:
                    s.set(0 if k != 'glitch_slices' else 8)
                    self.params[k] = 0 if k != 'glitch_slices' else 8
                else:
                    s.set(0)
                    self.params[k] = 0
            self.params['mirror'] = False
            self.params['flip'] = False
            self.canvas.delete('crop_rect')
            self.update_preview()
            threading.Thread(target=self.generate_preset_thumbnails, daemon=True).start()
        except Exception as e:
            print(f"reset_controls: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка при сбросе настроек: {str(e)}")

    def apply_preset(self, name):
        try:
            preset = fn.PRESETS.get(name, {})
            self.reset_controls()  # Reset before applying preset
            for k, v in preset.items():
                self.params[k] = v
                if k in self.sliders:
                    self.sliders[k].set(v)
            self.update_preview()
            threading.Thread(target=self.generate_preset_thumbnails, daemon=True).start()
        except Exception as e:
            print(f"apply_preset: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка при применении пресета: {str(e)}")

    def update_preview(self):
        if self.image is None:
            self.canvas.delete('all')
            return
        try:
            img = fn.render_preview(self.image, self.params)
            if img is None:
                print("update_preview: render_preview returned None")
                self.canvas.delete('all')
                return
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
        except Exception as e:
            print(f"update_preview: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка при обновлении превью: {str(e)}")

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

    def apply_changes(self):
        if self.preview_image is None:
            messagebox.showerror("Ошибка", "Нет изображения для применения изменений")
            return
        try:
            self.history.append(self.image.copy())
            self.image = self.preview_image.copy()
            self.canvas.delete('crop_rect')
            self.params['crop_x'] = 0
            self.params['crop_y'] = 0
            self.params['crop_w'] = 0
            self.params['crop_h'] = 0
            self.params['rotate'] = 0
            self.params['mirror'] = False
            self.params['flip'] = False
            self.update_preview()
            threading.Thread(target=self.generate_preset_thumbnails, daemon=True).start()
        except Exception as e:
            print(f"apply_changes: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка при применении изменений: {str(e)}")

    def undo_last(self):
        try:
            if len(self.history) > 0:
                self.image = self.history.pop()
                self.canvas.delete('crop_rect')
                self.params['crop_x'] = 0
                self.params['crop_y'] = 0
                self.params['crop_w'] = 0
                self.params['crop_h'] = 0
                self.params['rotate'] = 0
                self.params['mirror'] = False
                self.params['flip'] = False
                self.update_preview()
                threading.Thread(target=self.generate_preset_thumbnails, daemon=True).start()
            else:
                print("undo_last: No history to undo")
                messagebox.showinfo("Информация", "Нет изменений для отмены")
        except Exception as e:
            print(f"undo_last: Error - {traceback.format_exc()}")
            messagebox.showerror("Ошибка", f"Ошибка при отмене действия: {str(e)}")