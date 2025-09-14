# main.py
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk
import json
import os
from datetime import datetime
import platform
import random
import threading
import queue
import time
import math
try:
    from matplotlib import font_manager
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
from functions import TextEffectFunctions, load_font_prefer
from gui import setup_styles, build_ui, build_text_controls, build_effects_controls, build_advanced_controls, build_preset_controls

class TextEffectEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.style = ttk.Style(self.root)
        self.funcs = TextEffectFunctions()

        # Font cache and available fonts
        self.font_cache = {}
        self.fallback_fonts = ["DejaVu Sans", "Arial", "Times New Roman", "Verdana", "Helvetica", "Courier New", "sans-serif"]
        self.available_fonts = self._get_available_fonts()

        # State variables
        self.text_content = tk.StringVar(value="Привет, мир!\nЭто пример текста")
        self.font_name = tk.StringVar(value=self.available_fonts[0] if self.available_fonts else "DejaVu Sans")
        self.font_size = tk.IntVar(value=72)
        self.letter_spacing = tk.IntVar(value=0)
        self.line_spacing = tk.IntVar(value=10)
        self.align = tk.StringVar(value="center")
        self.text_color = tk.StringVar(value="#ffffff")
        self.stroke_color = tk.StringVar(value="#000000")
        self.stroke_width = tk.IntVar(value=2)
        self.opacity = tk.IntVar(value=100)
        self.shadow_color = tk.StringVar(value="#000000")
        self.shadow_offset = tk.IntVar(value=8)
        self.shadow_angle = tk.IntVar(value=45)
        self.shadow_blur = tk.IntVar(value=6)
        self.glow_color = tk.StringVar(value="#5a5ff7")
        self.glow_intensity = tk.IntVar(value=10)
        self.inner_glow_color = tk.StringVar(value="#ffffff")
        self.inner_glow_intensity = tk.IntVar(value=0)
        self.neon_color = tk.StringVar(value="#ff00ff")
        self.neon_intensity = tk.IntVar(value=0)
        self.threed_depth = tk.IntVar(value=0)
        self.threed_angle = tk.IntVar(value=45)
        self.gradient_enabled = tk.BooleanVar(value=False)
        self.gradient_start = tk.StringVar(value="#ff5f6d")
        self.gradient_end = tk.StringVar(value="#ffc371")
        self.gradient_dir = tk.StringVar(value="horizontal")
        self.texture_intensity = tk.IntVar(value=0)
        self.emboss_intensity = tk.IntVar(value=0)
        self.bevel_intensity = tk.IntVar(value=0)
        self.wave_amplitude = tk.IntVar(value=0)
        self.wave_wavelength = tk.IntVar(value=30)
        self.perspective_strength = tk.IntVar(value=0)
        self.rotation_angle = tk.IntVar(value=0)
        self.reflection_enabled = tk.BooleanVar(value=False)
        self.reflection_opacity = tk.IntVar(value=50)
        self.reflection_offset = tk.IntVar(value=10)
        self.zoom = tk.DoubleVar(value=1.0)
        self.preview_width = tk.IntVar(value=1280)
        self.preview_height = tk.IntVar(value=720)
        self.auto_size_canvas = tk.BooleanVar(value=True)
        self.bg_color = tk.StringVar(value="#0a0d1e")
        self.bg_transparent = tk.BooleanVar(value=False)
        self.dark_mode = tk.BooleanVar(value=True)

        # Undo/Redo history
        self.state_history = []
        self.redo_history = []

        # Multithreading
        self.image_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False

        # Presets directory
        self.presets_dir = os.path.join(os.path.expanduser("~"), ".text_effect_presets")
        os.makedirs(self.presets_dir, exist_ok=True)

        # Initialize styles before building UI
        setup_styles(self)

        # UI
        build_ui(self)

        # Debounce
        self._preview_after_id = None
        self.update_preview_debounced()
        self._check_image_queue()
        self.update_font_preview()
        self.save_state()  # Initial state

    def save_state(self):
        state = {var_name: self.__dict__[var_name].get() for var_name in self.__dict__ if isinstance(self.__dict__[var_name], (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)) and var_name not in ['status_var', 'zoom']}
        self.state_history.append(state)
        self.redo_history.clear()

    def undo(self):
        if self.state_history:
            current_state = {var_name: self.__dict__[var_name].get() for var_name in self.__dict__ if isinstance(self.__dict__[var_name], (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)) and var_name not in ['status_var', 'zoom']}
            self.redo_history.append(current_state)
            prev_state = self.state_history.pop()
            for k, v in prev_state.items():
                self.__dict__[k].set(v)
            self.update_font_preview()
            self.update_preview_debounced()
            self.status_var.set("Отмена выполнена")

    def redo(self):
        if self.redo_history:
            current_state = {var_name: self.__dict__[var_name].get() for var_name in self.__dict__ if isinstance(self.__dict__[var_name], (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)) and var_name not in ['status_var', 'zoom']}
            self.state_history.append(current_state)
            next_state = self.redo_history.pop()
            for k, v in next_state.items():
                self.__dict__[k].set(v)
            self.update_font_preview()
            self.update_preview_debounced()
            self.status_var.set("Повтор выполнен")

    def _get_available_fonts(self):
        """Получить список доступных системных шрифтов."""
        if MATPLOTLIB_AVAILABLE:
            try:
                fonts = [os.path.splitext(os.path.basename(f))[0] for f in font_manager.findSystemFonts()]
                return sorted(list(set(fonts)))[:50]  # Ограничим 50 шрифтами для скорости
            except Exception as e:
                self.status_var.set(f"Ошибка загрузки шрифтов: {str(e)}")
        return self.fallback_fonts

    def update_font_preview(self):
        """Обновить предварительный просмотр шрифта."""
        try:
            font_obj = self._get_cached_font(self.font_name.get(), 20)
            img = Image.new('RGBA', (150, 40), (0, 0, 0, 0))  # Увеличен размер для лучшей видимости
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), "АБВ abc", fill="#ffffff", font=font_obj)  # Добавлен латинский текст для проверки
            self.font_preview_img = ImageTk.PhotoImage(img)
            self.font_preview_label.configure(image=self.font_preview_img)
            self.status_var.set(f"Предпросмотр шрифта: {self.font_name.get()}")
        except Exception as e:
            self.font_preview_label.configure(image=None)
            self.status_var.set(f"Ошибка предпросмотра шрифта: {str(e)}")

    def _get_cached_font(self, font_name, size):
        """Получить шрифт из кэша или загрузить новый, с резервными шрифтами."""
        cache_key = (font_name, size)
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        try:
            font = load_font_prefer(font_name, size)
            self.font_cache[cache_key] = font
            return font
        except Exception as e:
            self.status_var.set(f"Шрифт {font_name} не загружен: {str(e)}. Пробуем резервные шрифты.")

        for fallback in self.available_fonts:
            try:
                font = load_font_prefer(fallback, size)
                self.font_cache[cache_key] = font
                self.font_name.set(fallback)
                self.status_var.set(f"Используется резервный шрифт: {fallback}")
                return font
            except:
                continue

        self.status_var.set(f"Все шрифты недоступны, используется стандартный шрифт")
        font = ImageFont.load_default()
        self.font_cache[cache_key] = font
        return font

    def update_preset_previews(self):
        """Обновить миниатюры предпросмотра пресетов."""
        for widget in self.preset_frame.winfo_children():
            widget.destroy()
        presets = [f for f in os.listdir(self.presets_dir) if f.endswith('.json')]
        for idx, preset in enumerate(presets):
            try:
                with open(os.path.join(self.presets_dir, preset), 'r', encoding='utf-8') as f:
                    preset_data = json.load(f)
                img = self.generate_preset_preview(preset_data)
                tk_img = ImageTk.PhotoImage(img.resize((100, 100), Image.Resampling.LANCZOS))
                btn = tk.Button(self.preset_frame, image=tk_img, command=lambda p=preset: self.load_preset(os.path.join(self.presets_dir, p)), **self.button_style)
                btn.image = tk_img
                btn.grid(row=idx // 4, column=idx % 4, padx=5, pady=5)
                tk.Label(self.preset_frame, text=preset, **self.button_style).grid(row=idx // 4 + 1, column=idx % 4, padx=5, pady=2)
            except:
                continue

    def generate_preset_preview(self, preset):
        """Сгенерировать миниатюру предпросмотра для пресета."""
        font_obj = self._get_cached_font(preset.get('font_name', self.available_fonts[0]), 20)
        mask = self.funcs.create_text_mask((200, 100), preset.get('text', 'Предпросмотр'), font_obj, align=preset.get('align', 'center'), spacing=preset.get('line_spacing', 0), stroke_width=preset.get('stroke_width', 0))
        img = Image.new('RGBA', (200, 100), (0, 0, 0, 0))
        if preset.get('gradient_enabled', False):
            grad = self.funcs.create_gradient_image((200, 100), preset.get('gradient_start', '#ffffff'), preset.get('gradient_end', '#ffffff'), preset.get('gradient_dir', 'horizontal'))
            text_img = self.funcs.apply_gradient_to_text(mask, grad)
        else:
            text_img = Image.new('RGBA', (200, 100), self.funcs.hex_to_rgb(preset.get('text_color', '#ffffff')) + (255,))
            text_img.putalpha(mask)
        return Image.alpha_composite(img, text_img)

    def open_presets_folder(self):
        """Открыть папку с пресетами."""
        try:
            if platform.system() == "Windows":
                os.startfile(self.presets_dir)
            elif platform.system() == "Darwin":
                os.system(f'open "{self.presets_dir}"')
            else:
                os.system(f'xdg-open "{self.presets_dir}"')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")

    def _choose_color(self, var):
        """Выбрать цвет и обновить предпросмотр."""
        chosen = colorchooser.askcolor(initialcolor=var.get())[1]
        if chosen:
            var.set(chosen)
            self.update_preview_debounced()

    def randomize_style(self):
        """Случайно изменить настройки стиля для создания уникального дизайна."""
        self.text_color.set('#' + ''.join(random.choice('23456789ABCDEF') for _ in range(6)))
        self.stroke_color.set('#' + ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        self.stroke_width.set(random.randint(0, 10))
        self.opacity.set(random.randint(70, 100))

        self.font_name.set(random.choice(self.available_fonts))  # Выбор из доступных шрифтов
        self.font_size.set(random.randint(36, 100))
        self.align.set(random.choice(["left", "center", "right"]))
        self.line_spacing.set(random.randint(-5, 20))
        self.letter_spacing.set(random.randint(-3, 10))

        self.shadow_color.set('#' + ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        self.shadow_offset.set(random.randint(0, 20))
        self.shadow_angle.set(random.randint(0, 359))
        self.shadow_blur.set(random.randint(0, 15))

        self.glow_color.set('#' + ''.join(random.choice('23456789ABCDEF') for _ in range(6)))
        self.glow_intensity.set(random.randint(0, 30))
        self.inner_glow_color.set('#' + ''.join(random.choice('23456789ABCDEF') for _ in range(6)))
        self.inner_glow_intensity.set(random.randint(0, 30))
        self.neon_color.set('#' + ''.join(random.choice('23456789ABCDEF') for _ in range(6)))
        self.neon_intensity.set(random.randint(0, 30))

        self.threed_depth.set(random.randint(0, 15))
        self.threed_angle.set(random.randint(0, 359))

        self.gradient_enabled.set(random.choice([True, False]))
        if self.gradient_enabled.get():
            self.gradient_start.set('#' + ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
            self.gradient_end.set('#' + ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
            self.gradient_dir.set(random.choice(['horizontal', 'vertical', 'diagonal']))

        self.texture_intensity.set(random.randint(0, 50))
        self.emboss_intensity.set(random.randint(0, 50))
        self.bevel_intensity.set(random.randint(0, 50))

        self.wave_amplitude.set(random.randint(0, 30))
        self.wave_wavelength.set(random.randint(10, 100))
        self.perspective_strength.set(random.randint(0, 20))
        self.rotation_angle.set(random.randint(-30, 30))

        self.reflection_enabled.set(random.choice([True, False]))
        if self.reflection_enabled.get():
            self.reflection_opacity.set(random.randint(20, 80))
            self.reflection_offset.set(random.randint(5, 20))

        self.bg_color.set('#' + ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        self.bg_transparent.set(random.choice([True, False]))

        self.update_font_preview()
        self.update_preview_debounced(delay=200)
        self.status_var.set(f"Случайный стиль применён, шрифт: {self.font_name.get()}")

    def update_preview_debounced(self, delay=100):
        """Отложить обновление предпросмотра."""
        if self._preview_after_id:
            self.root.after_cancel(self._preview_after_id)
        self._preview_after_id = self.root.after(delay, self.update_preview)

    def update_preview(self):
        """Инициировать обработку изображения в отдельном потоке."""
        if self.is_processing:
            return
        self.is_processing = True
        self.status_var.set("Обработка изображения...")

        settings = {
            'text': self.text_content.get() or "Пример текста",
            'zoom': float(self.zoom.get()),
            'width': int(self.preview_width.get() * self.zoom.get()),
            'height': int(self.preview_height.get() * self.zoom.get()),
            'font_name': self.font_name.get(),
            'font_size': max(6, int(self.font_size.get() * self.zoom.get())),
            'align': self.align.get(),
            'line_spacing': self.line_spacing.get(),
            'stroke_width': self.stroke_width.get(),
            'rotation_angle': self.rotation_angle.get(),
            'bg_transparent': self.bg_transparent.get(),
            'bg_color': self.bg_color.get(),
            'auto_size_canvas': self.auto_size_canvas.get(),
            'stroke_color': self.stroke_color.get(),
            'text_color': self.text_color.get(),
            'gradient_enabled': self.gradient_enabled.get(),
            'gradient_start': self.gradient_start.get(),
            'gradient_end': self.gradient_end.get(),
            'gradient_dir': self.gradient_dir.get(),
            'inner_glow_intensity': int(self.inner_glow_intensity.get()),
            'inner_glow_color': self.inner_glow_color.get(),
            'glow_intensity': int(self.glow_intensity.get()),
            'glow_color': self.glow_color.get(),
            'neon_intensity': int(self.neon_intensity.get()),
            'neon_color': self.neon_color.get(),
            'shadow_offset': int(self.shadow_offset.get()),
            'shadow_angle': self.shadow_angle.get(),
            'shadow_blur': self.shadow_blur.get(),
            'shadow_color': self.shadow_color.get(),
            'threed_depth': int(self.threed_depth.get()),
            'threed_angle': self.threed_angle.get(),
            'texture_intensity': int(self.texture_intensity.get()),
            'emboss_intensity': int(self.emboss_intensity.get()),
            'bevel_intensity': int(self.bevel_intensity.get()),
            'wave_amplitude': int(self.wave_amplitude.get()),
            'wave_wavelength': max(5, int(self.wave_wavelength.get())),
            'perspective_strength': int(self.perspective_strength.get()),
            'reflection_enabled': self.reflection_enabled.get(),
            'reflection_opacity': self.reflection_opacity.get(),
            'reflection_offset': self.reflection_offset.get(),
            'opacity': int(self.opacity.get())
        }

        self.processing_thread = threading.Thread(target=self._process_image, args=(settings,))
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def _process_image(self, settings):
        """Обработать изображение в отдельном потоке."""
        try:
            font_obj = self._get_cached_font(settings['font_name'], settings['font_size'])

            if settings['auto_size_canvas']:
                tw, th = self.funcs.calculate_text_bbox(settings['text'], font_obj, settings['line_spacing'], settings['stroke_width'], settings['rotation_angle'])
                padding = max(100, settings['stroke_width'] * 2 + settings['glow_intensity'] + settings['shadow_offset'] + settings['reflection_offset']) * settings['zoom']
                settings['width'] = max(settings['width'], int(tw + padding * 2))
                settings['height'] = max(settings['height'], int(th + padding * 2 + (settings['reflection_offset'] if settings['reflection_enabled'] else 0)))
                self.preview_width.set(int(settings['width'] / settings['zoom']))
                self.preview_height.set(int(settings['height'] / settings['zoom']))

            if settings['bg_transparent']:
                base_mode = 'RGBA'
                bg_color = (0, 0, 0, 0)
            else:
                base_mode = 'RGB'
                bg_color = self.funcs.hex_to_rgb(settings['bg_color'])

            max_preview_size = 1500
            scale_factor = min(1.0, max_preview_size / max(settings['width'], settings['height']))
            render_width = int(settings['width'] * scale_factor)
            render_height = int(settings['height'] * scale_factor)

            if render_width <= 0 or render_height <= 0:
                raise ValueError(f"Недопустимые размеры рендера: {render_width}x{render_height}")

            mask = self.funcs.create_text_mask((render_width, render_height), settings['text'], font_obj,
                                               align=settings['align'], spacing=settings['line_spacing'],
                                               stroke_width=settings['stroke_width'], rotation=settings['rotation_angle'], padding=50 * settings['zoom'])

            base = Image.new(base_mode, (render_width, render_height), bg_color)
            text_img = Image.new('RGBA', (render_width, render_height), (0, 0, 0, 0))

            stroke_w = settings['stroke_width']
            if stroke_w > 0:
                stroke_col = self.funcs.hex_to_rgb(settings['stroke_color'])
                sd = mask.filter(ImageFilter.MaxFilter(size=max(3, int(stroke_w * scale_factor * 2 + 1))))
                stroke_layer = Image.new('RGBA', (render_width, render_height), stroke_col + (255,))
                stroke_layer.putalpha(sd)
                if stroke_layer.size != text_img.size:
                    stroke_layer = stroke_layer.resize(text_img.size, Image.Resampling.LANCZOS)
                text_img = Image.alpha_composite(text_img, stroke_layer)

            if settings['inner_glow_intensity'] > 0:
                inner_glow = self.funcs.apply_inner_glow(mask, settings['inner_glow_color'], settings['inner_glow_intensity'] * scale_factor)
                if inner_glow.size != text_img.size:
                    inner_glow = inner_glow.resize(text_img.size, Image.Resampling.LANCZOS)
                text_img = Image.alpha_composite(text_img, inner_glow)

            if settings['gradient_enabled']:
                grad = self.funcs.create_gradient_image((render_width, render_height), settings['gradient_start'], settings['gradient_end'], settings['gradient_dir'])
                text_img = self.funcs.apply_gradient_to_text(mask, grad)
            else:
                fill_col = self.funcs.hex_to_rgb(settings['text_color'])
                fill_layer = Image.new('RGBA', (render_width, render_height), fill_col + (255,))
                fill_layer.putalpha(mask)
                text_img = Image.alpha_composite(text_img, fill_layer)

            if settings['glow_intensity'] > 0:
                glow_mask = mask.filter(ImageFilter.GaussianBlur(radius=settings['glow_intensity'] * scale_factor / 2))
                glow_col = self.funcs.hex_to_rgb(settings['glow_color'])
                glow_layer = Image.new('RGBA', (render_width, render_height), glow_col + (200,))
                glow_layer.putalpha(glow_mask)
                text_img = Image.alpha_composite(glow_layer, text_img)

            if settings['neon_intensity'] > 0:
                text_img = self.funcs.apply_neon_effect(text_img, settings['neon_color'], int(settings['neon_intensity'] * scale_factor))

            if settings['shadow_offset'] > 0:
                angle = math.radians(settings['shadow_angle'])
                dx = int(math.cos(angle) * settings['shadow_offset'] * scale_factor)
                dy = int(math.sin(angle) * settings['shadow_offset'] * scale_factor)
                shmask = mask.filter(ImageFilter.GaussianBlur(radius=max(0, settings['shadow_blur'] * scale_factor / 2)))
                shcol = self.funcs.hex_to_rgb(settings['shadow_color'])
                shadow_layer = Image.new('RGBA', (render_width, render_height), shcol + (200,))
                shadow_layer.putalpha(shmask)
                base = Image.new('RGBA', (render_width, render_height), (0, 0, 0, 0))
                base.paste(shadow_layer, (dx, dy), shmask)

            if settings['threed_depth'] > 0:
                text_img = self.funcs.apply_3d_effect(text_img, int(settings['threed_depth'] * scale_factor), settings['threed_angle'])
                if text_img.size != base.size:
                    text_img = text_img.resize(base.size, Image.Resampling.LANCZOS)

            if text_img.size != base.size:
                text_img = text_img.resize(base.size, Image.Resampling.LANCZOS)
            base = Image.alpha_composite(base, text_img)

            if settings['texture_intensity'] > 0:
                texture = self.funcs.create_noise_texture((render_width, render_height), intensity=settings['texture_intensity'] / 100.0)
                if texture.size != base.size:
                    texture = texture.resize(base.size, Image.Resampling.LANCZOS)
                base = Image.alpha_composite(base, texture)

            if settings['emboss_intensity'] > 0:
                base = base.filter(ImageFilter.EMBOSS)

            if settings['bevel_intensity'] > 0:
                base = self.funcs.apply_bevel(base, settings['bevel_intensity'])

            if settings['wave_amplitude'] > 0:
                base = self.funcs.apply_wave_distortion(base, amplitude=int(settings['wave_amplitude'] * scale_factor), wavelength=settings['wave_wavelength'])
                if base.size != (render_width, render_height):
                    base = base.resize((render_width, render_height), Image.Resampling.LANCZOS)

            if settings['perspective_strength'] > 0:
                base = self.funcs.apply_perspective_like(base, settings['perspective_strength'])
                if base.size != (render_width, render_height):
                    base = base.resize((render_width, render_height), Image.Resampling.LANCZOS)

            if settings['reflection_enabled']:
                base = self.funcs.apply_reflection(base, settings['reflection_opacity'], int(settings['reflection_offset'] * scale_factor))
                if base.size != (render_width, render_height):
                    base = base.resize((render_width, render_height), Image.Resampling.LANCZOS)

            if settings['opacity'] < 100:
                alpha = base.split()[3].point(lambda a: int(a * (settings['opacity'] / 100.0)))
                base.putalpha(alpha)

            display_img = base.resize((settings['width'], settings['height']), Image.Resampling.LANCZOS)

            self.image_queue.put((display_img, settings['width'], settings['height'], settings['zoom']))
        except Exception as e:
            self.image_queue.put(('error', str(e)))

    def _check_image_queue(self):
        """Проверить очередь изображений для обработанных изображений."""
        try:
            result = self.image_queue.get_nowait()
            if isinstance(result, tuple) and len(result) == 4:
                display_img, width, height, zoom = result
                self.tk_preview_img = ImageTk.PhotoImage(display_img)
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(0, 0, image=self.tk_preview_img, anchor="nw")
                self.preview_canvas.config(scrollregion=(0, 0, width, height))
                self.status_var.set(f"Предпросмотр обновлён — {width}×{height} (масштаб {zoom:.2f}×)")
            elif isinstance(result, tuple) and result[0] == 'error':
                self.status_var.set(f"Ошибка предпросмотра: {result[1]}")
        except queue.Empty:
            pass
        finally:
            self.is_processing = False
        self.root.after(50, self._check_image_queue)

    def open_export_dialog(self):
        """Открыть диалог экспорта с улучшенными виджетами."""
        export_win = tk.Toplevel(self.root)
        export_win.title("Экспорт изображения")
        export_win.geometry("400x300")
        export_win.configure(bg=self.bg)
        ttk.Label(export_win, text="Параметры экспорта", style="Title.TLabel").pack(pady=12)

        fmt_var = tk.StringVar(value="png")
        ttk.Radiobutton(export_win, text="PNG (с прозрачностью)", variable=fmt_var, value="png").pack(anchor="w", padx=20, pady=4)
        ttk.Radiobutton(export_win, text="JPEG", variable=fmt_var, value="jpeg").pack(anchor="w", padx=20, pady=4)

        quality_frame = ttk.Frame(export_win)
        quality_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(quality_frame, text="Качество (JPEG):").pack(side="left")
        quality_var = tk.IntVar(value=90)
        tk.Spinbox(quality_frame, from_=10, to=100, textvariable=quality_var, width=5, **self.entry_style).pack(side="left", padx=5)

        size_frame = ttk.Frame(export_win)
        size_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(size_frame, text="Ширина:").pack(side="left")
        width_var = tk.IntVar(value=self.preview_width.get())
        tk.Spinbox(size_frame, from_=100, to=4000, textvariable=width_var, width=5, **self.entry_style).pack(side="left", padx=5)
        ttk.Label(size_frame, text="Высота:").pack(side="left", padx=10)
        height_var = tk.IntVar(value=self.preview_height.get())
        tk.Spinbox(size_frame, from_=100, to=4000, textvariable=height_var, width=5, **self.entry_style).pack(side="left", padx=5)

        def export():
            filename = filedialog.asksaveasfilename(defaultextension=f".{fmt_var.get()}", filetypes=[(f"{fmt_var.get().upper()} файлы", f"*.{fmt_var.get()}"), ("Все файлы", "*.*")])
            if not filename:
                return
            settings = {
                'text': self.text_content.get() or "Пример текста",
                'zoom': 1.0,
                'width': width_var.get(),
                'height': height_var.get(),
                'font_name': self.font_name.get(),
                'font_size': max(6, int(self.font_size.get())),
                'align': self.align.get(),
                'line_spacing': self.line_spacing.get(),
                'stroke_width': self.stroke_width.get(),
                'rotation_angle': self.rotation_angle.get(),
                'bg_transparent': self.bg_transparent.get(),
                'bg_color': self.bg_color.get(),
                'auto_size_canvas': self.auto_size_canvas.get(),
                'stroke_color': self.stroke_color.get(),
                'text_color': self.text_color.get(),
                'gradient_enabled': self.gradient_enabled.get(),
                'gradient_start': self.gradient_start.get(),
                'gradient_end': self.gradient_end.get(),
                'gradient_dir': self.gradient_dir.get(),
                'inner_glow_intensity': int(self.inner_glow_intensity.get()),
                'inner_glow_color': self.inner_glow_color.get(),
                'glow_intensity': int(self.glow_intensity.get()),
                'glow_color': self.glow_color.get(),
                'neon_intensity': int(self.neon_intensity.get()),
                'neon_color': self.neon_color.get(),
                'shadow_offset': int(self.shadow_offset.get()),
                'shadow_angle': self.shadow_angle.get(),
                'shadow_blur': self.shadow_blur.get(),
                'shadow_color': self.shadow_color.get(),
                'threed_depth': int(self.threed_depth.get()),
                'threed_angle': self.threed_angle.get(),
                'texture_intensity': int(self.texture_intensity.get()),
                'emboss_intensity': int(self.emboss_intensity.get()),
                'bevel_intensity': int(self.bevel_intensity.get()),
                'wave_amplitude': int(self.wave_amplitude.get()),
                'wave_wavelength': max(5, int(self.wave_wavelength.get())),
                'perspective_strength': int(self.perspective_strength.get()),
                'reflection_enabled': self.reflection_enabled.get(),
                'reflection_opacity': self.reflection_opacity.get(),
                'reflection_offset': self.reflection_offset.get(),
                'opacity': int(self.opacity.get())
            }
            self._process_image(settings)
            try:
                result = self.image_queue.get(timeout=10)
                if isinstance(result, tuple) and len(result) == 4:
                    img, _, _, _ = result
                    if fmt_var.get() == "jpeg":
                        img = img.convert('RGB')
                        img.save(filename, quality=quality_var.get())
                    else:
                        img.save(filename)
                    self.status_var.set(f"Изображение сохранено: {filename}")
                    export_win.destroy()
                else:
                    messagebox.showerror("Ошибка", f"Не удалось экспортировать: {result[1]}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

        ttk.Button(export_win, text="Экспорт", command=export, style="Accent.TButton").pack(pady=20)

    def save_preset(self):
        """Сохранить текущие настройки как пресет."""
        preset_name = filedialog.asksaveasfilename(initialdir=self.presets_dir, defaultextension=".json", filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")])
        if preset_name:
            settings = {
                'text_content': self.text_content.get(),
                'font_name': self.font_name.get(),
                'font_size': self.font_size.get(),
                'letter_spacing': self.letter_spacing.get(),
                'line_spacing': self.line_spacing.get(),
                'align': self.align.get(),
                'text_color': self.text_color.get(),
                'stroke_color': self.stroke_color.get(),
                'stroke_width': self.stroke_width.get(),
                'opacity': self.opacity.get(),
                'shadow_color': self.shadow_color.get(),
                'shadow_offset': self.shadow_offset.get(),
                'shadow_angle': self.shadow_angle.get(),
                'shadow_blur': self.shadow_blur.get(),
                'glow_color': self.glow_color.get(),
                'glow_intensity': self.glow_intensity.get(),
                'inner_glow_color': self.inner_glow_color.get(),
                'inner_glow_intensity': self.inner_glow_intensity.get(),
                'neon_color': self.neon_color.get(),
                'neon_intensity': self.neon_intensity.get(),
                'threed_depth': self.threed_depth.get(),
                'threed_angle': self.threed_angle.get(),
                'gradient_enabled': self.gradient_enabled.get(),
                'gradient_start': self.gradient_start.get(),
                'gradient_end': self.gradient_end.get(),
                'gradient_dir': self.gradient_dir.get(),
                'texture_intensity': self.texture_intensity.get(),
                'emboss_intensity': self.emboss_intensity.get(),
                'bevel_intensity': self.bevel_intensity.get(),
                'wave_amplitude': self.wave_amplitude.get(),
                'wave_wavelength': self.wave_wavelength.get(),
                'perspective_strength': self.perspective_strength.get(),
                'rotation_angle': self.rotation_angle.get(),
                'reflection_enabled': self.reflection_enabled.get(),
                'reflection_opacity': self.reflection_opacity.get(),
                'reflection_offset': self.reflection_offset.get(),
                'bg_color': self.bg_color.get(),
                'bg_transparent': self.bg_transparent.get(),
                'preview_width': self.preview_width.get(),
                'preview_height': self.preview_height.get(),
                'auto_size_canvas': self.auto_size_canvas.get()
            }
            settings['text'] = self.text_content.get()
            try:
                with open(preset_name, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
                self.update_preset_previews()
                self.status_var.set(f"Пресет сохранён: {preset_name}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить пресет: {e}")

    def load_preset(self, filename=None):
        """Загрузить пресет из файла."""
        if not filename:
            filename = filedialog.askopenfilename(initialdir=self.presets_dir, filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    preset = json.load(f)
                self.text_content.set(preset.get('text_content', self.text_content.get()))
                self.font_name.set(preset.get('font_name', self.font_name.get()))
                self.font_size.set(preset.get('font_size', self.font_size.get()))
                self.letter_spacing.set(preset.get('letter_spacing', self.letter_spacing.get()))
                self.line_spacing.set(preset.get('line_spacing', self.line_spacing.get()))
                self.align.set(preset.get('align', self.align.get()))
                self.text_color.set(preset.get('text_color', self.text_color.get()))
                self.stroke_color.set(preset.get('stroke_color', self.stroke_color.get()))
                self.stroke_width.set(preset.get('stroke_width', self.stroke_width.get()))
                self.opacity.set(preset.get('opacity', self.opacity.get()))
                self.shadow_color.set(preset.get('shadow_color', self.shadow_color.get()))
                self.shadow_offset.set(preset.get('shadow_offset', self.shadow_offset.get()))
                self.shadow_angle.set(preset.get('shadow_angle', self.shadow_angle.get()))
                self.shadow_blur.set(preset.get('shadow_blur', self.shadow_blur.get()))
                self.glow_color.set(preset.get('glow_color', self.glow_color.get()))
                self.glow_intensity.set(preset.get('glow_intensity', self.glow_intensity.get()))
                self.inner_glow_color.set(preset.get('inner_glow_color', self.inner_glow_color.get()))
                self.inner_glow_intensity.set(preset.get('inner_glow_intensity', self.inner_glow_intensity.get()))
                self.neon_color.set(preset.get('neon_color', self.neon_color.get()))
                self.neon_intensity.set(preset.get('neon_intensity', self.neon_intensity.get()))
                self.threed_depth.set(preset.get('threed_depth', self.threed_depth.get()))
                self.threed_angle.set(preset.get('threed_angle', self.threed_angle.get()))
                self.gradient_enabled.set(preset.get('gradient_enabled', self.gradient_enabled.get()))
                self.gradient_start.set(preset.get('gradient_start', self.gradient_start.get()))
                self.gradient_end.set(preset.get('gradient_end', self.gradient_end.get()))
                self.gradient_dir.set(preset.get('gradient_dir', self.gradient_dir.get()))
                self.texture_intensity.set(preset.get('texture_intensity', self.texture_intensity.get()))
                self.emboss_intensity.set(preset.get('emboss_intensity', self.emboss_intensity.get()))
                self.bevel_intensity.set(preset.get('bevel_intensity', self.bevel_intensity.get()))
                self.wave_amplitude.set(preset.get('wave_amplitude', self.wave_amplitude.get()))
                self.wave_wavelength.set(preset.get('wave_wavelength', self.wave_wavelength.get()))
                self.perspective_strength.set(preset.get('perspective_strength', self.perspective_strength.get()))
                self.rotation_angle.set(preset.get('rotation_angle', self.rotation_angle.get()))
                self.reflection_enabled.set(preset.get('reflection_enabled', self.reflection_enabled.get()))
                self.reflection_opacity.set(preset.get('reflection_opacity', self.reflection_opacity.get()))
                self.reflection_offset.set(preset.get('reflection_offset', self.reflection_offset.get()))
                self.bg_color.set(preset.get('bg_color', self.bg_color.get()))
                self.bg_transparent.set(preset.get('bg_transparent', self.bg_transparent.get()))
                self.preview_width.set(preset.get('preview_width', self.preview_width.get()))
                self.preview_height.set(preset.get('preview_height', self.preview_height.get()))
                self.auto_size_canvas.set(preset.get('auto_size_canvas', self.auto_size_canvas.get()))
                self.update_font_preview()
                self.update_preview_debounced()
                self.status_var.set(f"Пресет загружен: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить пресет: {e}")

    def _on_preview_mousewheel(self, event):
        """Обработать колесо мыши для изменения масштаба."""
        if event.delta > 0 or event.num == 4:
            self.zoom.set(min(self.zoom.get() * 1.1, 3.0))
        elif event.delta < 0 or event.num == 5:
            self.zoom.set(max(self.zoom.get() / 1.1, 0.1))
        self.update_preview_debounced()
        self.status_var.set(f"Масштаб: {self.zoom.get():.2f}×")

def main():
    root = tk.Tk()
    app = TextEffectEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()