import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw
from functions import *


class MondrianGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mondrian Grid")
        # default fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # generate & set icon (small mondrian-like)
        self.set_app_icon()

        # single dark theme
        self.theme = {
            'bg': "#0f1724", 'card': "#111827", 'accent': "#6366f1",
            'text': "#e6eef8", 'muted': "#9aa6c1"
        }

        # configuration (no settings UI)
        self.config = load_json(CONFIG_PATH) or {}
        self.settings = {
            'default_k': self.config.get('default_k', 6),
            'downsample_rate': self.config.get('downsample_rate', 0.2),
            'max_history': self.config.get('max_history', 200),
            'canvas_bg': self.config.get('canvas_bg', '#071223'),
            'default_export_format': self.config.get('default_export_format', 'css'),
            'auto_save_history': self.config.get('auto_save_history', True),
            'palette_preview_style': self.config.get('palette_preview_style', 'bars'),
            'zoom_sensitivity': self.config.get('zoom_sensitivity', 1.2),
            'font_size': self.config.get('font_size', 11),
            'sidebar_width': self.config.get('sidebar_width', 320)
        }

        # persistent state
        self.current_image = None
        self.current_image_path = None
        self.current_display_image = None  # resized for canvas
        self.current_scale = 1.0
        self.current_palette = []
        self.current_percentages = []
        self.current_mood = None
        self.base_color = None
        self.constructor_assignment = {'main': None, 'accent': None, 'bg': None, 'text': None}
        self.history = load_json(HISTORY_PATH) or []
        self.selected_history_index = None

        # build UI
        self.build_ui()
        self.show_masterpiece()

    def set_app_icon(self):
        try:
            size = 64
            im = Image.new('RGBA', (size, size), (240, 240, 240, 255))
            draw = ImageDraw.Draw(im)
            colors = [(228, 26, 28), (255, 214, 0), (0, 84, 159), (255, 255, 255), (0, 0, 0)]
            draw.rectangle((0, 0, 34, 34), fill=(228, 26, 28))
            draw.rectangle((34, 0, 64, 20), fill=(255, 214, 0))
            draw.rectangle((0, 34, 24, 64), fill=(0, 84, 159))
            draw.rectangle((24, 34, 64, 64), fill=(255, 255, 255))
            draw.rectangle((0, 0, 63, 63), outline=(10, 10, 10), width=3)
            tk_im = ImageTk.PhotoImage(im)
            self.root.iconphoto(False, tk_im)
            self._icon_img = tk_im
        except Exception as e:
            print("Icon set error:", e)

    def exit_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)

    def build_ui(self):
        self.root.configure(bg=self.theme['bg'])
        main = tk.Frame(self.root, bg=self.theme['bg'])
        main.pack(fill='both', expand=True)

        # Sidebar
        sidebar = tk.Frame(main, bg=self.theme['card'], width=self.settings['sidebar_width'])
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        logo = tk.Label(sidebar, text="Mondrian Grid".upper(), bg=self.theme['card'], fg=self.theme['accent'],
                        font=('Segoe UI', 18, 'bold'))
        logo.pack(anchor='w', padx=16, pady=(16, 8))

        # navigation
        nav = [
            ("Шедевр", self.show_masterpiece),
            ("Спектр", self.show_spectrum),
            ("Конструктор", self.show_constructor),
            ("Колористика", self.show_coloristics),
            ("Редактор", self.show_editor),
            ("История", self.show_history)
        ]
        for name, cmd in nav:
            b = tk.Button(sidebar, text=name, bg=self.theme['card'], fg=self.theme['text'], bd=0,
                          font=('Segoe UI', self.settings['font_size']), anchor='w', command=cmd)
            b.pack(fill='x', padx=12, pady=6)

        # quick controls
        tk.Button(sidebar, text="Загрузить изображение", bg=self.theme['accent'], fg='white', bd=0,
                  command=self.load_image).pack(fill='x', padx=12, pady=(12, 6))
        tk.Button(sidebar, text="Импорт HEX-палитры", bg="#1f2937", fg='white', bd=0,
                  command=self.import_hex_palette).pack(fill='x', padx=12, pady=6)
        tk.Button(sidebar, text="Экспорт текущей палитры", bg="#0b5fff", fg='white', bd=0,
                  command=self.export_menu).pack(fill='x', padx=12, pady=(6, 12))

        # main area
        self.main_area = tk.Frame(main, bg=self.theme['bg'])
        self.main_area.pack(side='right', fill='both', expand=True)

        header = tk.Frame(self.main_area, bg=self.theme['bg'])
        header.pack(fill='x', pady=12, padx=12)
        self.section_label = tk.Label(header, text="", bg=self.theme['bg'], fg=self.theme['text'],
                                      font=('Segoe UI', 20, 'bold'))
        self.section_label.pack(side='left')

        content = tk.Frame(self.main_area, bg=self.theme['bg'])
        content.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        self.preview_frame = tk.Frame(content, bg=self.theme['card'], padx=12, pady=12)
        self.preview_frame.pack(side='left', fill='both', expand=True)

        self.preview_canvas = tk.Canvas(self.preview_frame, bg=self.settings['canvas_bg'], highlightthickness=0)
        self.preview_canvas.pack(fill='both', expand=True)
        zframe = tk.Frame(self.preview_frame, bg=self.theme['card'])
        zframe.pack(fill='x', pady=(8, 0))
        tk.Button(zframe, text="−", width=3, command=self.zoom_out).pack(side='left', padx=4)
        tk.Button(zframe, text="+", width=3, command=self.zoom_in).pack(side='left', padx=4)
        tk.Label(zframe, text="(Колёсико мыши — зум)", bg=self.theme['card'], fg=self.theme['muted']).pack(side='left',
                                                                                                           padx=8)

        self.preview_canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.preview_canvas.bind("<Button-4>", self.on_mousewheel)
        self.preview_canvas.bind("<Button-5>", self.on_mousewheel)
        self.preview_canvas.bind("<ButtonPress-1>", self._start_pan)
        self.preview_canvas.bind("<B1-Motion>", self._do_pan)

        self.info_frame = tk.Frame(content, bg=self.theme['card'], width=420, padx=12, pady=12)
        self.info_frame.pack(side='right', fill='y')
        self.info_frame.pack_propagate(False)

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("All files", "*.*")])
        if not path:
            return
        try:
            img = Image.open(path).convert('RGB')
        except Exception as e:
            messagebox.showerror("Ошибка чтения", str(e))
            return
        self.current_image = img
        self.current_image_path = path
        self.current_scale = 1.0
        self._display_image_on_canvas(img)
        if getattr(self, 'k_var', None):
            try:
                self.analyze_image()
            except:
                pass

    def _display_image_on_canvas(self, pil_img):
        w = self.preview_canvas.winfo_width() or 800
        h = self.preview_canvas.winfo_height() or 600
        img = pil_img.copy()
        img.thumbnail((max(100, w - 40), max(100, h - 40)), Image.LANCZOS)
        self.current_display_image = img
        self._redraw_canvas_image()

    def _redraw_canvas_image(self):
        self.preview_canvas.delete("all")
        if not self.current_display_image:
            return
        width, height = self.current_display_image.size
        sw = max(1, int(width * self.current_scale))
        sh = max(1, int(height * self.current_scale))
        disp = self.current_display_image.resize((sw, sh), Image.LANCZOS)
        self._tkimg = ImageTk.PhotoImage(disp)
        self.preview_canvas.create_image(10, 10, image=self._tkimg, anchor='nw', tags="img")
        canvas_w = self.preview_canvas.winfo_width()
        canvas_h = self.preview_canvas.winfo_height()
        if sw < canvas_w and sh < canvas_h:
            x = (canvas_w - sw) // 2
            y = (canvas_h - sh) // 2
            self.preview_canvas.coords("img", x, y)
        if self.current_palette:
            if self.settings['palette_preview_style'] == 'bars':
                bar_h = 30
                x0 = 10
                y0 = canvas_h - bar_h - 10
                bar_w = (canvas_w - 20) / max(1, len(self.current_palette))
                for i, c in enumerate(self.current_palette):
                    hx = rgb_to_hex(c)
                    self.preview_canvas.create_rectangle(x0 + i * bar_w, y0, x0 + (i + 1) * bar_w, y0 + bar_h, fill=hx,
                                                         outline=hx)
            elif self.settings['palette_preview_style'] == 'grid':
                cell_size = 50
                for i, c in enumerate(self.current_palette):
                    hx = rgb_to_hex(c)
                    x = 10 + (i % 5) * cell_size
                    y = canvas_h - 60 - (i // 5) * cell_size
                    self.preview_canvas.create_rectangle(x, y, x + cell_size, y + cell_size, fill=hx, outline=hx)

    def zoom_in(self):
        self.current_scale = min(5.0, self.current_scale * self.settings['zoom_sensitivity'])
        self._redraw_canvas_image()

    def zoom_out(self):
        self.current_scale = max(0.1, self.current_scale / self.settings['zoom_sensitivity'])
        self._redraw_canvas_image()

    def on_mousewheel(self, event):
        delta = 0
        if hasattr(event, 'delta') and event.delta:
            delta = event.delta
        elif event.num == 4:
            delta = 120
        elif event.num == 5:
            delta = -120
        factor = 1.0
        try:
            if (event.state & 0x0004) != 0:
                factor = 1.5
        except Exception:
            pass
        if delta > 0:
            self.current_scale = min(5.0, self.current_scale * (self.settings['zoom_sensitivity'] * factor))
        else:
            self.current_scale = max(0.1, self.current_scale / (self.settings['zoom_sensitivity'] * factor))
        self._redraw_canvas_image()

    def _start_pan(self, event):
        self._pan_start = (event.x, event.y)
        coords = self.preview_canvas.coords("img")
        self._pan_img_pos = coords if coords else [0, 0]

    def _do_pan(self, event):
        if not hasattr(self, '_pan_start') or not hasattr(self, '_pan_img_pos'):
            return
        dx = event.x - self._pan_start[0]
        dy = event.y - self._pan_start[1]
        x0 = self._pan_img_pos[0] + dx
        y0 = self._pan_img_pos[1] + dy
        self.preview_canvas.coords("img", x0, y0)

    def _clear_info_frame(self):
        for w in self.info_frame.winfo_children():
            w.destroy()

    def show_masterpiece(self):
        self.section_label.config(text="Шедевр — анализ палитры")
        self._clear_info_frame()
        tk.Label(self.info_frame, text="Параметры анализа", bg=self.theme['card'], fg=self.theme['text'],
                 font=('Segoe UI', 13, 'bold')).pack(anchor='w', pady=(0, 8))

        # Number of colors (k) slider and entry
        tk.Label(self.info_frame, text="Число цветов (3–8):", bg=self.theme['card'], fg=self.theme['muted']).pack(
            anchor='w', pady=(8, 4))
        k_frame = tk.Frame(self.info_frame, bg=self.theme['card'])
        k_frame.pack(fill='x', pady=(0, 8))
        self.k_var = tk.IntVar(value=self.settings['default_k'])
        tk.Scale(k_frame, from_=3, to=8, orient='horizontal', variable=self.k_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0).pack(side='left', fill='x', expand=True)
        self.k_entry = tk.Entry(k_frame, textvariable=self.k_var, width=6, bg="#0b1220", fg=self.theme['text'])
        self.k_entry.pack(side='left', padx=8)

        # Downsample rate slider and entry
        tk.Label(self.info_frame, text="Степень сэмплинга (0.1–1.0):", bg=self.theme['card'],
                 fg=self.theme['muted']).pack(anchor='w', pady=(8, 4))
        ds_frame = tk.Frame(self.info_frame, bg=self.theme['card'])
        ds_frame.pack(fill='x', pady=(0, 8))
        self.ds_var = tk.DoubleVar(value=self.settings['downsample_rate'])
        tk.Scale(ds_frame, from_=0.1, to=1.0, resolution=0.1, orient='horizontal', variable=self.ds_var,
                 bg=self.theme['card'], fg=self.theme['text'], highlightthickness=0).pack(side='left', fill='x',
                                                                                          expand=True)
        self.ds_entry = tk.Entry(ds_frame, textvariable=self.ds_var, width=6, bg="#0b1220", fg=self.theme['text'])
        self.ds_entry.pack(side='left', padx=8)

        tk.Button(self.info_frame, text="Анализировать", bg=self.theme['accent'], fg='white', bd=0,
                  command=self.analyze_image).pack(fill='x', pady=(8, 12))

        tk.Label(self.info_frame, text="Результат", bg=self.theme['card'], fg=self.theme['text'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(8, 8))
        self.palette_frame = tk.Frame(self.info_frame, bg=self.theme['card'])
        self.palette_frame.pack(fill='both', expand=True, pady=(0, 8))

        tk.Label(self.info_frame, text="Настроение:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w',
                                                                                                          pady=(8, 4))
        self.mood_label = tk.Label(self.info_frame, text="—", bg=self.theme['card'], fg=self.theme['text'])
        self.mood_label.pack(anchor='w', pady=(0, 8))

        tk.Label(self.info_frame, text="Точные проценты:", bg=self.theme['card'], fg=self.theme['muted']).pack(
            anchor='w', pady=(8, 4))
        self.perc_text = tk.Text(self.info_frame, height=6, bg=self.theme['card'], fg=self.theme['text'], bd=0)
        self.perc_text.pack(fill='both', pady=(4, 0))

        if self.current_palette:
            self.render_palette_widgets()

    def analyze_image(self):
        if not self.current_image:
            messagebox.showinfo("Нет изображения", "Сначала загрузите изображение или импортируйте палитру.")
            return
        try:
            k = self.k_var.get()
            downsample = self.ds_var.get()
            if not (3 <= k <= 8):
                raise ValueError("Число цветов должно быть от 3 до 8")
            if not (0.1 <= downsample <= 1.0):
                raise ValueError("Степень сэмплинга должна быть от 0.1 до 1.0")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return
        palette_rgb, raw_pct = get_dominant_colors_kmeans(self.current_image, n_colors=k, downsample=downsample)
        pct = get_color_percentages_for_palette(self.current_image, palette_rgb)
        self.current_palette = palette_rgb
        self.current_percentages = pct
        self.current_mood = classify_mood(self.current_palette, self.current_percentages)
        self.render_palette_widgets()
        self.mood_label.config(text=self.current_mood)
        self.perc_text.delete('1.0', 'end')
        for rgb, p in zip(self.current_palette, self.current_percentages):
            self.perc_text.insert('end', f"{rgb_to_hex(rgb)} — {p:.2f}%\n")
        if self.settings['auto_save_history']:
            self.auto_save_history(trigger="analyze")

    def render_palette_widgets(self):
        for w in self.palette_frame.winfo_children():
            w.destroy()
        for i, (rgb, p) in enumerate(zip(self.current_palette, self.current_percentages)):
            hx = rgb_to_hex(rgb)
            row = tk.Frame(self.palette_frame, bg=self.theme['card'])
            row.pack(fill='x', pady=6)
            box = tk.Label(row, bg=hx, width=4, height=1, relief='sunken')
            box.pack(side='left', padx=(0, 8))
            tk.Label(row, text=f"{hx} — {p:.2f}%", bg=self.theme['card'], fg=self.theme['text']).pack(side='left')
            tk.Button(row, text="Гармонии", bg="#1f2937", fg='white', bd=0,
                      command=lambda c=rgb: self.open_spectrum_with(c)).pack(side='right', padx=4)
            tk.Button(row, text="Назначить", bg="#1f2937", fg='white', bd=0,
                      command=lambda c=rgb: self.quick_assign_dialog(c)).pack(side='right', padx=4)

    def quick_assign_dialog(self, rgb):
        hx = rgb_to_hex(rgb)
        role = simpledialog.askstring("Назначить роль", "Выберите роль (main, accent, bg, text):", initialvalue="main")
        if role in self.constructor_assignment:
            self.constructor_assignment[role] = hx
            if self.settings['auto_save_history']:
                self.auto_save_history(trigger="assign")

    def show_spectrum(self):
        self.section_label.config(text="Спектр — генератор гармоний")
        self._clear_info_frame()
        tk.Label(self.info_frame, text="Базовый цвет", bg=self.theme['card'], fg=self.theme['text'],
                 font=('Segoe UI', 13, 'bold')).pack(anchor='w', pady=(0, 8))

        # Base color sliders (HSL)
        hsl_frame = tk.Frame(self.info_frame, bg=self.theme['card'])
        hsl_frame.pack(fill='x', pady=(8, 8))
        self.hue_var = tk.DoubleVar(value=0)
        self.sat_var = tk.DoubleVar(value=50)
        self.lum_var = tk.DoubleVar(value=50)
        tk.Label(hsl_frame, text="H:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,4))
        tk.Scale(hsl_frame, from_=0, to=360, orient='horizontal', variable=self.hue_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_base_color).pack(fill='x', pady=(0,4))
        tk.Label(hsl_frame, text="S%:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,4))
        tk.Scale(hsl_frame, from_=0, to=100, orient='horizontal', variable=self.sat_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_base_color).pack(fill='x', pady=(0,4))
        tk.Label(hsl_frame, text="L%:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,4))
        tk.Scale(hsl_frame, from_=0, to=100, orient='horizontal', variable=self.lum_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_base_color).pack(fill='x', pady=(0,4))

        tk.Button(self.info_frame, text="Выбрать цвет", bg="#1f2937", fg='white', bd=0,
                  command=self.pick_base_color).pack(fill='x', pady=(8, 8))
        if self.current_palette:
            tk.Label(self.info_frame, text="Текущая палитра:", bg=self.theme['card'], fg=self.theme['muted']).pack(
                anchor='w', pady=(8, 4))
            pframe = tk.Frame(self.info_frame, bg=self.theme['card'])
            pframe.pack(fill='x', pady=(0,8))
            for c in self.current_palette:
                tk.Button(pframe, bg=rgb_to_hex(c), width=3, height=1, bd=0,
                          command=lambda c=c: self.open_spectrum_with(c)).pack(side='left', padx=4)
        tk.Label(self.info_frame, text="Гармонии", bg=self.theme['card'], fg=self.theme['text'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(12, 8))
        self.harmony_container = tk.Frame(self.info_frame, bg=self.theme['card'])
        self.harmony_container.pack(fill='both', expand=True, pady=(0,8))
        tk.Button(self.info_frame, text="Копировать список названий", bg="#1f2937", fg='white', bd=0,
                  command=self.copy_harmony_names).pack(fill='x', pady=(8, 8))
        if self.base_color:
            self.render_harmonies(None)

    def pick_base_color(self):
        c = colorchooser.askcolor(title="Выберите базовый цвет")
        if c and c[0]:
            rgb = tuple(map(int, c[0]))
            self.base_color = rgb
            hsl = rgb_to_hsl(rgb)
            self.hue_var.set(hsl[0])
            self.sat_var.set(hsl[1])
            self.lum_var.set(hsl[2])
            self.render_harmonies(None)
            if self.settings['auto_save_history']:
                self.auto_save_history(trigger="spectrum")

    def update_base_color(self, *args):
        h = self.hue_var.get()
        s = self.sat_var.get()
        l = self.lum_var.get()
        self.base_color = hsl_to_rgb(h, s, l)
        self.render_harmonies(None)
        if self.settings['auto_save_history']:
            self.auto_save_history(trigger="spectrum")

    def render_harmonies(self, *args):
        for w in self.harmony_container.winfo_children():
            w.destroy()
        if not self.base_color:
            return
        harmonies = generate_harmonies(self.base_color)
        for name, cols in harmonies.items():
            frame = tk.Frame(self.harmony_container, bg=self.theme['card'], pady=6)
            frame.pack(fill='x')
            tk.Label(frame, text=name, bg=self.theme['card'], fg=self.theme['text'],
                     font=('Segoe UI', 11, 'bold')).pack(anchor='w')
            palette_row = tk.Frame(frame, bg=self.theme['card'])
            palette_row.pack(fill='x', pady=(6, 0))
            for c in cols:
                hx = rgb_to_hex(c)
                b = tk.Button(palette_row, bg=hx, width=4, height=2, bd=0,
                              command=lambda c=c: self.preview_color_large(c))
                b.pack(side='left', padx=6)
                b.bind("<Button-3>", lambda ev, c=c: self.quick_assign_dialog(c))

    def copy_harmony_names(self):
        if not self.base_color:
            return
        harmonies = generate_harmonies(self.base_color)
        names = list(harmonies.keys())
        self.root.clipboard_clear()
        self.root.clipboard_append('\n'.join(names))
        messagebox.showinfo("Скопировано", "Список названий скопирован в буфер обмена.")

    def preview_color_large(self, rgb):
        self.preview_canvas.delete('all')
        w = self.preview_frame.winfo_width() or 800
        h = self.preview_frame.winfo_height() or 600
        hx = rgb_to_hex(rgb)
        self.preview_canvas.create_rectangle(20, 20, w - 20, h - 20, fill=hx, outline=hx)
        if self.settings['auto_save_history']:
            self.auto_save_history(trigger="preview_color", extra=[rgb])

    def open_spectrum_with(self, rgb):
        self.show_spectrum()
        hsl = rgb_to_hsl(rgb)
        self.hue_var.set(hsl[0])
        self.sat_var.set(hsl[1])
        self.lum_var.set(hsl[2])
        self.base_color = rgb
        self.render_harmonies(None)

    def show_constructor(self):
        self.section_label.config(text="Конструктор — экспорт схем")
        self._clear_info_frame()

        # Upper part with scrolling for sliders
        upper = tk.Frame(self.info_frame, bg=self.theme['card'], height=400)
        upper.pack(fill='x', expand=False)
        upper.pack_propagate(False)

        scroll = tk.Scrollbar(upper)
        scroll.pack(side='right', fill='y')
        canvas = tk.Canvas(upper, bg=self.theme['card'], yscrollcommand=scroll.set)
        canvas.pack(side='left', fill='both', expand=True)
        scroll.config(command=canvas.yview)
        constructor_frame = tk.Frame(canvas, bg=self.theme['card'])
        canvas.create_window((0, 0), window=constructor_frame, anchor='nw')
        constructor_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        tk.Label(constructor_frame, text="Назначить роли цветов", bg=self.theme['card'], fg=self.theme['text'],
                 font=('Segoe UI', 13, 'bold')).pack(anchor='w', pady=(0, 8))

        # Main color
        tk.Label(constructor_frame, text="Основной цвет:", bg=self.theme['card'], fg=self.theme['muted']).pack(
            anchor='w', pady=(8, 4))
        main_frame = tk.Frame(constructor_frame, bg=self.theme['card'])
        main_frame.pack(fill='x', pady=(4, 8))
        self.main_r_var = tk.IntVar(value=128)
        self.main_g_var = tk.IntVar(value=128)
        self.main_b_var = tk.IntVar(value=128)
        tk.Label(main_frame, text="R:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(main_frame, from_=0, to=255, orient='horizontal', variable=self.main_r_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_main_color).pack(fill='x', pady=(0,2))
        tk.Label(main_frame, text="G:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(main_frame, from_=0, to=255, orient='horizontal', variable=self.main_g_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_main_color).pack(fill='x', pady=(0,2))
        tk.Label(main_frame, text="B:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(main_frame, from_=0, to=255, orient='horizontal', variable=self.main_b_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_main_color).pack(fill='x', pady=(0,2))
        self.main_color_btn = tk.Button(main_frame, text="—", bg="#1f2937", fg='white', bd=0,
                                        command=self.pick_main_color)
        self.main_color_btn.pack(fill='x', pady=(4, 0))

        # Accent color
        tk.Label(constructor_frame, text="Акцент:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w',
                                                                                                        pady=(8, 4))
        accent_frame = tk.Frame(constructor_frame, bg=self.theme['card'])
        accent_frame.pack(fill='x', pady=(4, 8))
        self.accent_r_var = tk.IntVar(value=128)
        self.accent_g_var = tk.IntVar(value=128)
        self.accent_b_var = tk.IntVar(value=128)
        tk.Label(accent_frame, text="R:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(accent_frame, from_=0, to=255, orient='horizontal', variable=self.accent_r_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_accent_color).pack(fill='x', pady=(0,2))
        tk.Label(accent_frame, text="G:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(accent_frame, from_=0, to=255, orient='horizontal', variable=self.accent_g_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_accent_color).pack(fill='x', pady=(0,2))
        tk.Label(accent_frame, text="B:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(accent_frame, from_=0, to=255, orient='horizontal', variable=self.accent_b_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_accent_color).pack(fill='x', pady=(0,2))
        self.accent_color_btn = tk.Button(accent_frame, text="—", bg="#1f2937", fg='white', bd=0,
                                          command=self.pick_accent_color)
        self.accent_color_btn.pack(fill='x', pady=(4, 0))

        # Background color
        tk.Label(constructor_frame, text="Фон:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w',
                                                                                                     pady=(8, 4))
        bg_frame = tk.Frame(constructor_frame, bg=self.theme['card'])
        bg_frame.pack(fill='x', pady=(4, 8))
        self.bg_r_var = tk.IntVar(value=128)
        self.bg_g_var = tk.IntVar(value=128)
        self.bg_b_var = tk.IntVar(value=128)
        tk.Label(bg_frame, text="R:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(bg_frame, from_=0, to=255, orient='horizontal', variable=self.bg_r_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_bg_color).pack(fill='x', pady=(0,2))
        tk.Label(bg_frame, text="G:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(bg_frame, from_=0, to=255, orient='horizontal', variable=self.bg_g_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_bg_color).pack(fill='x', pady=(0,2))
        tk.Label(bg_frame, text="B:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(bg_frame, from_=0, to=255, orient='horizontal', variable=self.bg_b_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_bg_color).pack(fill='x', pady=(0,2))
        self.bg_color_btn = tk.Button(bg_frame, text="—", bg="#1f2937", fg='white', bd=0, command=self.pick_bg_color)
        self.bg_color_btn.pack(fill='x', pady=(4, 0))

        # Text color
        tk.Label(constructor_frame, text="Текст:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w',
                                                                                                       pady=(8, 4))
        text_frame = tk.Frame(constructor_frame, bg=self.theme['card'])
        text_frame.pack(fill='x', pady=(4, 8))
        self.text_r_var = tk.IntVar(value=128)
        self.text_g_var = tk.IntVar(value=128)
        self.text_b_var = tk.IntVar(value=128)
        tk.Label(text_frame, text="R:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(text_frame, from_=0, to=255, orient='horizontal', variable=self.text_r_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_text_color).pack(fill='x', pady=(0,2))
        tk.Label(text_frame, text="G:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(text_frame, from_=0, to=255, orient='horizontal', variable=self.text_g_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_text_color).pack(fill='x', pady=(0,2))
        tk.Label(text_frame, text="B:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(text_frame, from_=0, to=255, orient='horizontal', variable=self.text_b_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.update_text_color).pack(fill='x', pady=(0,2))
        self.text_color_btn = tk.Button(text_frame, text="—", bg="#1f2937", fg='white', bd=0,
                                        command=self.pick_text_color)
        self.text_color_btn.pack(fill='x', pady=(4, 0))

        tk.Button(constructor_frame, text="Экспорт схемы", bg=self.theme['accent'], fg='white', bd=0,
                  command=self.export_constructed_scheme).pack(fill='x', pady=(12, 8))

        # Preview below the scrolled area
        tk.Label(self.info_frame, text="Превью темы", bg=self.theme['card'], fg=self.theme['text'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(12, 6))
        self.preview_theme_frame = tk.Frame(self.info_frame, bg="#0b1220", height=180)
        self.preview_theme_frame.pack(fill='both', expand=True, pady=(6, 0))
        self.preview_theme_frame.pack_propagate(False)
        self.render_theme_preview()

    def update_main_color(self, *args):
        rgb = (self.main_r_var.get(), self.main_g_var.get(), self.main_b_var.get())
        hx = rgb_to_hex(rgb)
        self.constructor_assignment['main'] = hx
        self.main_color_btn.config(text=hx, bg=hx, fg='white' if relative_luminance(rgb) < 0.5 else 'black')
        self.render_theme_preview()
        if self.settings['auto_save_history']:
            self.auto_save_history(trigger="assign")

    def update_accent_color(self, *args):
        rgb = (self.accent_r_var.get(), self.accent_g_var.get(), self.accent_b_var.get())
        hx = rgb_to_hex(rgb)
        self.constructor_assignment['accent'] = hx
        self.accent_color_btn.config(text=hx, bg=hx, fg='white' if relative_luminance(rgb) < 0.5 else 'black')
        self.render_theme_preview()
        if self.settings['auto_save_history']:
            self.auto_save_history(trigger="assign")

    def update_bg_color(self, *args):
        rgb = (self.bg_r_var.get(), self.bg_g_var.get(), self.bg_b_var.get())
        hx = rgb_to_hex(rgb)
        self.constructor_assignment['bg'] = hx
        self.bg_color_btn.config(text=hx, bg=hx, fg='white' if relative_luminance(rgb) < 0.5 else 'black')
        self.render_theme_preview()
        if self.settings['auto_save_history']:
            self.auto_save_history(trigger="assign")

    def update_text_color(self, *args):
        rgb = (self.text_r_var.get(), self.text_g_var.get(), self.text_b_var.get())
        hx = rgb_to_hex(rgb)
        self.constructor_assignment['text'] = hx
        self.text_color_btn.config(text=hx, bg=hx, fg='white' if relative_luminance(rgb) < 0.5 else 'black')
        self.render_theme_preview()
        if self.settings['auto_save_history']:
            self.auto_save_history(trigger="assign")

    def pick_main_color(self):
        color = colorchooser.askcolor()[0]
        if color:
            hx = rgb_to_hex(color)
            self.constructor_assignment['main'] = hx
            self.main_r_var.set(color[0])
            self.main_g_var.set(color[1])
            self.main_b_var.set(color[2])
            self.main_color_btn.config(text=hx, bg=hx, fg='white' if relative_luminance(color) < 0.5 else 'black')
            self.render_theme_preview()
            if self.settings['auto_save_history']:
                self.auto_save_history(trigger="assign")

    def pick_accent_color(self):
        color = colorchooser.askcolor()[0]
        if color:
            hx = rgb_to_hex(color)
            self.constructor_assignment['accent'] = hx
            self.accent_r_var.set(color[0])
            self.accent_g_var.set(color[1])
            self.accent_b_var.set(color[2])
            self.accent_color_btn.config(text=hx, bg=hx, fg='white' if relative_luminance(color) < 0.5 else 'black')
            self.render_theme_preview()
            if self.settings['auto_save_history']:
                self.auto_save_history(trigger="assign")

    def pick_bg_color(self):
        color = colorchooser.askcolor()[0]
        if color:
            hx = rgb_to_hex(color)
            self.constructor_assignment['bg'] = hx
            self.bg_r_var.set(color[0])
            self.bg_g_var.set(color[1])
            self.bg_b_var.set(color[2])
            self.bg_color_btn.config(text=hx, bg=hx, fg='white' if relative_luminance(color) < 0.5 else 'black')
            self.render_theme_preview()
            if self.settings['auto_save_history']:
                self.auto_save_history(trigger="assign")

    def pick_text_color(self):
        color = colorchooser.askcolor()[0]
        if color:
            hx = rgb_to_hex(color)
            self.constructor_assignment['text'] = hx
            self.text_r_var.set(color[0])
            self.text_g_var.set(color[1])
            self.text_b_var.set(color[2])
            self.text_color_btn.config(text=hx, bg=hx, fg='white' if relative_luminance(color) < 0.5 else 'black')
            self.render_theme_preview()
            if self.settings['auto_save_history']:
                self.auto_save_history(trigger="assign")

    def render_theme_preview(self):
        for w in self.preview_theme_frame.winfo_children():
            w.destroy()
        bg = self.constructor_assignment.get('bg') or "#0f1724"
        main = self.constructor_assignment.get('main') or "#111827"
        accent = self.constructor_assignment.get('accent') or "#6366f1"
        text = self.constructor_assignment.get('text') or "#e6eef8"
        preview = tk.Frame(self.preview_theme_frame, bg=bg)
        preview.pack(fill='both', expand=True, padx=8, pady=8)
        header = tk.Frame(preview, bg=main, height=36)
        header.pack(fill='x', padx=12, pady=(8, 12));
        header.pack_propagate(False)
        tk.Label(header, text="Заголовок сайта", bg=main, fg=text, font=('Segoe UI', 12, 'bold')).pack(anchor='w',
                                                                                                       padx=8, pady=6)
        body = tk.Frame(preview, bg=bg)
        body.pack(fill='both', expand=True, padx=12, pady=(0, 12))
        tk.Label(body, text="Пример текста — как это будет выглядеть в интерфейсе.", bg=bg, fg=text,
                 wraplength=280).pack(anchor='w')
        tk.Button(body, text="Кнопка действия", bg=accent, fg='white', bd=0).pack(anchor='w', pady=(12, 0))

    def export_constructed_scheme(self):
        hex_list = []
        for role in ['main', 'accent', 'bg', 'text']:
            v = self.constructor_assignment.get(role)
            if v:
                hex_list.append(v)
        for rgb in getattr(self, 'current_palette', []):
            hx = rgb_to_hex(rgb)
            if hx not in hex_list:
                hex_list.append(hx)
        if not hex_list:
            messagebox.showinfo("Нет цветов", "Нет выбранных цветов для экспорта.")
            return
        folder = filedialog.askdirectory(title="Выберите папку для сохранения экспорта")
        if not folder:
            return
        base = f"mondrian_theme_{int(time.time())}"
        if self.settings['default_export_format'] == 'css':
            export_css(hex_list, os.path.join(folder, base + ".css"))
        elif self.settings['default_export_format'] == 'scss':
            export_scss(hex_list, os.path.join(folder, base + ".scss"))
        elif self.settings['default_export_format'] == 'gpl':
            export_gpl(hex_list, os.path.join(folder, base + ".gpl"), name=base)
        elif self.settings['default_export_format'] == 'json':
            export_json_for_figma(hex_list, os.path.join(folder, base + ".json"))
        elif self.settings['default_export_format'] == 'png':
            export_png(hex_list, os.path.join(folder, base + ".png"))
        messagebox.showinfo("Экспорт", f"Экспортировано в {folder}")

    def show_coloristics(self):
        self.section_label.config(text="Колористика — конвертеры и контраст")
        self._clear_info_frame()
        tk.Label(self.info_frame, text="HEX ↔ RGB ↔ HSL", bg=self.theme['card'], fg=self.theme['text'],
                 font=('Segoe UI', 13, 'bold')).pack(anchor='w', pady=(0,8))
        frm = tk.Frame(self.info_frame, bg=self.theme['card'])
        frm.pack(fill='x', pady=(8, 8))

        # HEX input
        tk.Label(frm, text="HEX:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,4))
        self.hex_entry = tk.Entry(frm, bg="#0b1220", fg=self.theme['text'])
        self.hex_entry.pack(fill='x', pady=(0, 4))
        self.hex_entry.bind("<KeyRelease>", self.hex_to_others)

        # RGB sliders
        rgb_frame = tk.Frame(frm, bg=self.theme['card'])
        rgb_frame.pack(fill='x', pady=(4,4))
        self.rgb_r_var = tk.IntVar(value=128)
        self.rgb_g_var = tk.IntVar(value=128)
        self.rgb_b_var = tk.IntVar(value=128)
        tk.Label(rgb_frame, text="R:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(rgb_frame, from_=0, to=255, orient='horizontal', variable=self.rgb_r_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.rgb_to_others).pack(fill='x', pady=(0,2))
        tk.Label(rgb_frame, text="G:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(rgb_frame, from_=0, to=255, orient='horizontal', variable=self.rgb_g_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.rgb_to_others).pack(fill='x', pady=(0,2))
        tk.Label(rgb_frame, text="B:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(rgb_frame, from_=0, to=255, orient='horizontal', variable=self.rgb_b_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.rgb_to_others).pack(fill='x', pady=(0,2))
        self.rgb_entry = tk.Entry(frm, bg="#0b1220", fg=self.theme['text'])
        self.rgb_entry.pack(fill='x', pady=(4, 4))

        # HSL sliders
        hsl_frame = tk.Frame(frm, bg=self.theme['card'])
        hsl_frame.pack(fill='x', pady=(4,4))
        self.hsl_h_var = tk.DoubleVar(value=0)
        self.hsl_s_var = tk.DoubleVar(value=50)
        self.hsl_l_var = tk.DoubleVar(value=50)
        tk.Label(hsl_frame, text="H:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(hsl_frame, from_=0, to=360, orient='horizontal', variable=self.hsl_h_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.hsl_to_others).pack(fill='x', pady=(0,2))
        tk.Label(hsl_frame, text="S%:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(hsl_frame, from_=0, to=100, orient='horizontal', variable=self.hsl_s_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.hsl_to_others).pack(fill='x', pady=(0,2))
        tk.Label(hsl_frame, text="L%:", bg=self.theme['card'], fg=self.theme['muted']).pack(anchor='w', pady=(0,2))
        tk.Scale(hsl_frame, from_=0, to=100, orient='horizontal', variable=self.hsl_l_var, bg=self.theme['card'],
                 fg=self.theme['text'], highlightthickness=0, command=self.hsl_to_others).pack(fill='x', pady=(0,2))
        self.hsl_entry = tk.Entry(frm, bg="#0b1220", fg=self.theme['text'])
        self.hsl_entry.pack(fill='x', pady=(4, 4))

        tk.Label(self.info_frame, text="Проверка контраста (WCAG)", bg=self.theme['card'], fg=self.theme['text'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(12, 6))
        contrast_fr = tk.Frame(self.info_frame, bg=self.theme['card'])
        contrast_fr.pack(fill='x', pady=(0,8))
        tk.Label(contrast_fr, text="Цвет 1 (HEX):", bg=self.theme['card'], fg=self.theme['muted']).grid(row=0, column=0,
                                                                                                        sticky='w', pady=4)
        self.c1 = tk.Entry(contrast_fr, bg="#0b1220", fg=self.theme['text'])
        self.c1.grid(row=0, column=1, padx=8, sticky='ew', pady=4)
        tk.Label(contrast_fr, text="Цвет 2 (HEX):", bg=self.theme['card'], fg=self.theme['muted']).grid(row=1, column=0,
                                                                                                        sticky='w', pady=4)
        self.c2 = tk.Entry(contrast_fr, bg="#0b1220", fg=self.theme['text'])
        self.c2.grid(row=1, column=1, padx=8, sticky='ew', pady=4)
        contrast_fr.columnconfigure(1, weight=1)
        tk.Button(self.info_frame, text="Проверить контраст", bg=self.theme['accent'], fg='white', bd=0,
                  command=self.check_contrast).pack(fill='x', pady=(8, 4))
        self.contrast_result = tk.Label(self.info_frame, text="", bg=self.theme['card'], fg=self.theme['text'])
        self.contrast_result.pack(anchor='w', pady=(0,8))

    def hex_to_others(self, *args):
        txt = self.hex_entry.get().strip()
        if not txt:
            return
        if not txt.startswith('#'): txt = '#' + txt
        try:
            rgb = hex_to_rgb(txt)
            hsl = rgb_to_hsl(rgb)
            self.rgb_r_var.set(rgb[0])
            self.rgb_g_var.set(rgb[1])
            self.rgb_b_var.set(rgb[2])
            self.rgb_entry.delete(0, 'end');
            self.rgb_entry.insert(0, f"{rgb[0]}, {rgb[1]}, {rgb[2]}")
            self.hsl_h_var.set(hsl[0])
            self.hsl_s_var.set(hsl[1])
            self.hsl_l_var.set(hsl[2])
            self.hsl_entry.delete(0, 'end');
            self.hsl_entry.insert(0, f"{hsl[0]:.1f}, {hsl[1]:.1f}, {hsl[2]:.1f}")
        except Exception:
            pass  # Silent error for live update

    def rgb_to_others(self, *args):
        rgb = (self.rgb_r_var.get(), self.rgb_g_var.get(), self.rgb_b_var.get())
        try:
            hx = rgb_to_hex(rgb)
            hsl = rgb_to_hsl(rgb)
            self.hex_entry.delete(0, 'end');
            self.hex_entry.insert(0, hx)
            self.hsl_h_var.set(hsl[0])
            self.hsl_s_var.set(hsl[1])
            self.hsl_l_var.set(hsl[2])
            self.hsl_entry.delete(0, 'end');
            self.hsl_entry.insert(0, f"{hsl[0]:.1f}, {hsl[1]:.1f}, {hsl[2]:.1f}")
            self.rgb_entry.delete(0, 'end');
            self.rgb_entry.insert(0, f"{rgb[0]}, {rgb[1]}, {rgb[2]}")
        except Exception:
            pass

    def hsl_to_others(self, *args):
        h, s, l = self.hsl_h_var.get(), self.hsl_s_var.get(), self.hsl_l_var.get()
        try:
            rgb = hsl_to_rgb(h, s, l)
            hx = rgb_to_hex(rgb)
            self.rgb_r_var.set(rgb[0])
            self.rgb_g_var.set(rgb[1])
            self.rgb_b_var.set(rgb[2])
            self.rgb_entry.delete(0, 'end');
            self.rgb_entry.insert(0, f"{rgb[0]}, {rgb[1]}, {rgb[2]}")
            self.hex_entry.delete(0, 'end');
            self.hex_entry.insert(0, hx)
            self.hsl_entry.delete(0, 'end');
            self.hsl_entry.insert(0, f"{h:.1f}, {s:.1f}, {l:.1f}")
        except Exception:
            pass

    def check_contrast(self):
        a = self.c1.get().strip()
        b = self.c2.get().strip()
        if a and not a.startswith('#'): a = '#' + a
        if b and not b.startswith('#'): b = '#' + b
        try:
            rgb1 = hex_to_rgb(a);
            rgb2 = hex_to_rgb(b)
            cr = contrast_ratio(rgb1, rgb2)
            ok_large = cr >= 7.0
            ok_small = cr >= 4.5
            txt = f"Контраст: {cr:.2f}:1 — WCAG AA (большой текст): {'Да' if ok_small else 'Нет'}, WCAG AAA: {'Да' if ok_large else 'Нет'}"
            self.contrast_result.config(text=txt)
        except Exception:
            messagebox.showinfo("Ошибка", "Введите корректные HEX-коды для сравнения")

    def show_editor(self):
        self.section_label.config(text="Редактор — редактирование палитры")
        self._clear_info_frame()
        if not self.current_palette:
            tk.Label(self.info_frame, text="Нет палитры для редактирования.", bg=self.theme['card'],
                     fg=self.theme['text']).pack(pady=12)
            return
        tk.Label(self.info_frame, text="Редактировать цвета", bg=self.theme['card'], fg=self.theme['text'],
                 font=('Segoe UI', 13, 'bold')).pack(anchor='w', pady=(0,8))
        self.editor_frame = tk.Frame(self.info_frame, bg=self.theme['card'])
        self.editor_frame.pack(fill='both', expand=True, pady=(0,8))
        self.color_vars = []
        for i, rgb in enumerate(self.current_palette):
            hx = rgb_to_hex(rgb)
            row = tk.Frame(self.editor_frame, bg=self.theme['card'])
            row.pack(fill='x', pady=6)
            box = tk.Label(row, bg=hx, width=4, height=1, relief='sunken')
            box.pack(side='left', padx=(0, 8))
            r_var = tk.IntVar(value=rgb[0])
            g_var = tk.IntVar(value=rgb[1])
            b_var = tk.IntVar(value=rgb[2])
            self.color_vars.append((r_var, g_var, b_var))
            tk.Label(row, text="R:", bg=self.theme['card'], fg=self.theme['muted']).pack(side='left', padx=4)
            tk.Scale(row, from_=0, to=255, orient='horizontal', variable=r_var, bg=self.theme['card'],
                     fg=self.theme['text'], highlightthickness=0, command=lambda v, idx=i: self.update_color(idx)).pack(
                side='left', fill='x', expand=True, padx=4)
            tk.Label(row, text="G:", bg=self.theme['card'], fg=self.theme['muted']).pack(side='left', padx=4)
            tk.Scale(row, from_=0, to=255, orient='horizontal', variable=g_var, bg=self.theme['card'],
                     fg=self.theme['text'], highlightthickness=0, command=lambda v, idx=i: self.update_color(idx)).pack(
                side='left', fill='x', expand=True, padx=4)
            tk.Label(row, text="B:", bg=self.theme['card'], fg=self.theme['muted']).pack(side='left', padx=4)
            tk.Scale(row, from_=0, to=255, orient='horizontal', variable=b_var, bg=self.theme['card'],
                     fg=self.theme['text'], highlightthickness=0, command=lambda v, idx=i: self.update_color(idx)).pack(
                side='left', fill='x', expand=True, padx=4)
            tk.Button(row, text="Удалить", bg="#1f2937", fg='white', bd=0,
                      command=lambda idx=i: self.remove_color(idx)).pack(side='right', padx=8)
        tk.Button(self.info_frame, text="Добавить цвет", bg=self.theme['accent'], fg='white', bd=0,
                  command=self.add_color).pack(fill='x', pady=12)

    def update_color(self, idx):
        rgb = (self.color_vars[idx][0].get(), self.color_vars[idx][1].get(), self.color_vars[idx][2].get())
        self.current_palette[idx] = rgb
        self.current_percentages = [round(100 / len(self.current_palette), 2)] * len(
            self.current_palette) if self.current_palette else []
        self.show_editor()
        self._redraw_canvas_image()
        if self.settings['auto_save_history']:
            self.auto_save_history(trigger="editor")

    def remove_color(self, idx):
        del self.current_palette[idx]
        del self.color_vars[idx]
        self.current_percentages = [round(100 / len(self.current_palette), 2)] * len(
            self.current_palette) if self.current_palette else []
        self.show_editor()
        self._redraw_canvas_image()
        if self.settings['auto_save_history']:
            self.auto_save_history(trigger="editor")

    def add_color(self):
        color = colorchooser.askcolor()[0]
        if color:
            self.current_palette.append(tuple(map(int, color)))
            self.current_percentages = [round(100 / len(self.current_palette), 2)] * len(self.current_palette)
            self.color_vars.append((tk.IntVar(value=color[0]), tk.IntVar(value=color[1]), tk.IntVar(value=color[2])))
            self.show_editor()
            self._redraw_canvas_image()
            if self.settings['auto_save_history']:
                self.auto_save_history(trigger="editor")

    def show_history(self):
        self.section_label.config(text="История палитр")
        self._clear_info_frame()
        tk.Label(self.info_frame, text="Сохранённые палитры", bg=self.theme['card'], fg=self.theme['text'],
                 font=('Segoe UI', 13, 'bold')).pack(anchor='w', pady=(0,8))

        history_container = tk.Frame(self.info_frame, bg=self.theme['card'])
        history_container.pack(fill='both', expand=True)

        self.history_listbox = tk.Listbox(history_container, bg=self.theme['card'], fg=self.theme['text'], bd=0, highlightthickness=0,
                                          font=('Segoe UI', 11), activestyle='dotbox')
        self.history_listbox.pack(fill='both', expand=True, pady=(0,8))
        self.load_history()
        self.render_history_listbox()

        buttons_frame = tk.Frame(history_container, bg=self.theme['card'])
        buttons_frame.pack(fill='x', pady=8)
        tk.Button(buttons_frame, text="Загрузить", bg="#1f2937", fg='white', bd=0,
                  command=self.load_selected_history).pack(side='left', padx=8, pady=4)
        tk.Button(buttons_frame, text="Экспорт", bg="#1f2937", fg='white', bd=0,
                  command=self.export_selected_history).pack(side='left', padx=8, pady=4)
        tk.Button(buttons_frame, text="Скопировать HEX", bg="#1f2937", fg='white', bd=0,
                  command=self.copy_selected_hex).pack(side='left', padx=8, pady=4)
        tk.Button(buttons_frame, text="Скачать PNG", bg="#1f2937", fg='white', bd=0,
                  command=self.download_selected_png).pack(side='left', padx=8, pady=4)

    def load_history(self):
        self.history = load_json(HISTORY_PATH) or []

    def render_history_listbox(self):
        self.history_listbox.delete(0, tk.END)
        if not self.history:
            self.history_listbox.insert(tk.END, "Пусто — генерируйте или импортируйте палитры.")
            return
        for entry in self.history:
            display = f"{entry['name']} · {entry.get('mood', '—')} · {entry['timestamp'][:19]}"
            self.history_listbox.insert(tk.END, display)

    def get_selected_history_entry(self):
        sel = self.history_listbox.curselection()
        if not sel:
            messagebox.showinfo("Нет выбора", "Выберите запись из списка.")
            return None
        return self.history[sel[0]]

    def load_selected_history(self):
        entry = self.get_selected_history_entry()
        if entry:
            self.load_history_entry(entry)

    def export_selected_history(self):
        entry = self.get_selected_history_entry()
        if entry:
            self.export_history_entry(entry)

    def copy_selected_hex(self):
        entry = self.get_selected_history_entry()
        if entry:
            self.copy_hex_codes(entry)

    def download_selected_png(self):
        entry = self.get_selected_history_entry()
        if entry:
            self.download_png(entry)

    def auto_save_history(self, trigger="auto", extra=None):
        entry = None
        timestamp = datetime.now().isoformat()
        if trigger == "analyze":
            if not self.current_palette:
                return
            entry = {
                'name': f"Palette {len(self.history) + 1}",
                'timestamp': timestamp,
                'palette_hex': [rgb_to_hex(r) for r in self.current_palette],
                'percentages': self.current_percentages,
                'mood': self.current_mood,
                'source': self.current_image_path
            }
        elif trigger == "spectrum":
            if not self.base_color:
                return
            harmonies = generate_harmonies(self.base_color)
            flat = [rgb_to_hex(self.base_color)]
            for k, v in harmonies.items():
                flat.extend([rgb_to_hex(x) for x in v[:2]])
            entry = {
                'name': f"Harmony {len(self.history) + 1}",
                'timestamp': timestamp,
                'palette_hex': flat[:8],
                'percentages': [],
                'mood': classify_mood([hex_to_rgb(h) for h in flat[:5]], [20] * 5),
                'source': None
            }
        elif trigger == "preview_color":
            if not extra:
                return
            flat = [rgb_to_hex(extra[0])]
            entry = {
                'name': f"Color {len(self.history) + 1}",
                'timestamp': timestamp,
                'palette_hex': flat,
                'percentages': [],
                'mood': None,
                'source': None
            }
        elif trigger == "assign":
            pal = [v for v in self.constructor_assignment.values() if v]
            if not pal:
                return
            entry = {
                'name': f"Theme {len(self.history) + 1}",
                'timestamp': timestamp,
                'palette_hex': pal,
                'percentages': [],
                'mood': None,
                'source': None
            }
        elif trigger == "import":
            if not self.current_palette:
                return
            entry = {
                'name': f"Imported {len(self.history) + 1}",
                'timestamp': timestamp,
                'palette_hex': [rgb_to_hex(r) for r in self.current_palette],
                'percentages': self.current_percentages,
                'mood': classify_mood(self.current_palette, self.current_percentages),
                'source': None
            }
        elif trigger == "editor":
            if not self.current_palette:
                return
            entry = {
                'name': f"Edited Palette {len(self.history) + 1}",
                'timestamp': timestamp,
                'palette_hex': [rgb_to_hex(r) for r in self.current_palette],
                'percentages': self.current_percentages,
                'mood': classify_mood(self.current_palette, self.current_percentages),
                'source': None
            }
        else:
            return
        if entry:
            self.history.insert(0, entry)
            self.history = self.history[:self.settings['max_history']]
            save_json(HISTORY_PATH, self.history)
            if hasattr(self, 'history_listbox'):
                self.render_history_listbox()

    def load_history_entry(self, entry):
        self.current_palette = [hex_to_rgb(h) for h in entry['palette_hex']]
        self.current_percentages = entry.get('percentages', [round(100 / max(1, len(self.current_palette)), 2)] * len(
            self.current_palette))
        self.current_mood = entry.get('mood')
        self.current_image = None
        self.current_image_path = entry.get('source')
        self.show_masterpiece()
        self.render_palette_widgets()
        self.mood_label.config(text=self.current_mood or "—")
        self.perc_text.delete('1.0', 'end')
        for hx, p in zip(entry['palette_hex'], self.current_percentages):
            self.perc_text.insert('end', f"{hx} — {p:.2f}%\n")
        self.preview_canvas.delete('all')
        canvas_w = self.preview_canvas.winfo_width() or 800
        canvas_h = self.preview_canvas.winfo_height() or 600
        if self.settings['palette_preview_style'] == 'bars':
            bar_h = canvas_h // max(1, len(self.current_palette))
            for i, rgb in enumerate(self.current_palette):
                hx = rgb_to_hex(rgb)
                self.preview_canvas.create_rectangle(0, i * bar_h, canvas_w, (i + 1) * bar_h, fill=hx, outline=hx)
        elif self.settings['palette_preview_style'] == 'grid':
            cell_size = 50
            for i, rgb in enumerate(self.current_palette):
                hx = rgb_to_hex(rgb)
                x = 10 + (i % 5) * cell_size
                y = canvas_h - 60 - (i // 5) * cell_size
                self.preview_canvas.create_rectangle(x, y, x + cell_size, y + cell_size, fill=hx, outline=hx)

    def export_history_entry(self, entry):
        hex_list = entry['palette_hex']
        folder = filedialog.askdirectory(title="Выберите папку для экспорта")
        if not folder:
            return
        base = f"mondrian_history_{entry['name'].replace(' ', '_')}_{int(time.time())}"
        export_css(hex_list, os.path.join(folder, base + ".css"))
        export_scss(hex_list, os.path.join(folder, base + ".scss"))
        export_gpl(hex_list, os.path.join(folder, base + ".gpl"), name=base)
        export_json_for_figma(hex_list, os.path.join(folder, base + ".json"))
        export_png(hex_list, os.path.join(folder, base + ".png"))
        messagebox.showinfo("Экспорт", f"Экспортировано в {folder}")

    def copy_hex_codes(self, entry):
        hex_list = entry['palette_hex']
        self.root.clipboard_clear()
        self.root.clipboard_append(', '.join(hex_list))
        messagebox.showinfo("Скопировано", "HEX-коды скопированы в буфер обмена.")

    def download_png(self, entry):
        hex_list = entry['palette_hex']
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG file", "*.png"), ("All files", "*.*")],
                                            initialfile="palette.png")
        if not path:
            return
        export_png(hex_list, path)
        messagebox.showinfo("Скачано", f"Палитра сохранена как {path}")

    def import_hex_palette(self):
        txt = simpledialog.askstring("Импорт палитры",
                                     "Вставьте HEX-коды через запятую (например: #ff0000,#00ff00,#0000ff):")
        if not txt:
            return
        parts = [p.strip() for p in txt.replace(';', ',').split(',') if p.strip()]
        pal = []
        for p in parts:
            if not p.startswith('#'):
                p = '#' + p
            try:
                pal.append(hex_to_rgb(p))
            except:
                continue
        if not pal:
            messagebox.showinfo("Ошибка", "Не удалось распознать HEX-коды.")
            return
        self.current_palette = pal
        self.current_percentages = [round(100 / len(pal), 2)] * len(pal)
        self.current_mood = classify_mood(self.current_palette, self.current_percentages)
        self.show_masterpiece()
        self.render_palette_widgets()
        self.mood_label.config(text=self.current_mood)
        self.perc_text.delete('1.0', 'end')
        for rgb, p in zip(self.current_palette, self.current_percentages):
            self.perc_text.insert('end', f"{rgb_to_hex(rgb)} — {p:.2f}%\n")
        if self.settings['auto_save_history']:
            self.auto_save_history(trigger="import")

    def export_menu(self):
        if not self.current_palette:
            messagebox.showinfo("Нет палитры", "Сначала проанализируйте изображение или импортируйте палитру.")
            return
        hex_list = [rgb_to_hex(rgb) for rgb in self.current_palette]
        path = filedialog.asksaveasfilename(
            defaultextension=f".{self.settings['default_export_format']}",
            filetypes=[(f"{self.settings['default_export_format'].upper()} file",
                        f"*.{self.settings['default_export_format']}"), ("All files", "*.*")],
            initialfile=f"palette.{self.settings['default_export_format']}"
        )
        if not path:
            return
        folder = os.path.dirname(path)
        base = os.path.splitext(os.path.basename(path))[0]
        if self.settings['default_export_format'] == 'css':
            export_css(hex_list, os.path.join(folder, base + ".css"))
        elif self.settings['default_export_format'] == 'scss':
            export_scss(hex_list, os.path.join(folder, base + ".scss"))
        elif self.settings['default_export_format'] == 'gpl':
            export_gpl(hex_list, os.path.join(folder, base + ".gpl"), name=base)
        elif self.settings['default_export_format'] == 'json':
            export_json_for_figma(hex_list, os.path.join(folder, base + ".json"))
        elif self.settings['default_export_format'] == 'png':
            export_png(hex_list, os.path.join(folder, base + ".png"))
        messagebox.showinfo("Экспорт", f"Экспортировано в {folder}")