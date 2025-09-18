import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk
import json
import os
import random
import threading
import queue
import time
import math
import platform

try:
    from matplotlib import font_manager
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
from functions import TextEffectFunctions, load_font_prefer
from gui import TextEffectEditorGUI

class TextEffectEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.funcs = TextEffectFunctions()

        self.font_cache = {}
        self.fallback_fonts = ["DejaVu Sans", "Arial", "Times New Roman", "Verdana", "Helvetica", "Courier New",
                               "Liberation Sans", "Georgia"]
        self.available_fonts = self._get_available_fonts()

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
        self.gradient_dir = tk.StringVar(value="Горизонтальное")
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
        self.status_var = tk.StringVar(value="Готово")

        self.state_history = []
        self.redo_history = []

        self.image_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False

        self.presets_dir = os.path.join(os.path.expanduser("~"), ".text_effect_presets")
        os.makedirs(self.presets_dir, exist_ok=True)

        self.gui = TextEffectEditorGUI(self.root, self)

        self._preview_after_id = None
        self.update_preview_debounced()
        self._check_image_queue()
        self.update_font_preview()
        self.save_state()
        self.update_preset_previews()

    def save_state(self):
        state = {var_name: self.__dict__[var_name].get() for var_name in self.__dict__ if
                 isinstance(self.__dict__[var_name],
                            (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)) and var_name not in ['status_var',
                                                                                                        'zoom']}
        self.state_history.append(state)
        self.redo_history.clear()

    def undo(self):
        if self.state_history:
            current_state = {var_name: self.__dict__[var_name].get() for var_name in self.__dict__ if
                             isinstance(self.__dict__[var_name],
                                        (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)) and var_name not in [
                                 'status_var', 'zoom']}
            self.redo_history.append(current_state)
            prev_state = self.state_history.pop()
            for k, v in prev_state.items():
                self.__dict__[k].set(v)
            self.update_font_preview()
            self.update_preview_debounced()
            self.status_var.set("Отмена выполнена")

    def redo(self):
        if self.redo_history:
            current_state = {var_name: self.__dict__[var_name].get() for var_name in self.__dict__ if
                             isinstance(self.__dict__[var_name],
                                        (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)) and var_name not in [
                                 'status_var', 'zoom']}
            self.state_history.append(current_state)
            next_state = self.redo_history.pop()
            for k, v in next_state.items():
                self.__dict__[k].set(v)
            self.update_font_preview()
            self.update_preview_debounced()
            self.status_var.set("Повтор выполнен")

    def _get_available_fonts(self):
        if MATPLOTLIB_AVAILABLE:
            try:
                fonts = [os.path.splitext(os.path.basename(f))[0] for f in font_manager.findSystemFonts()]
                return sorted(list(set(fonts)))[:50]
            except Exception as e:
                self.status_var.set(f"Ошибка загрузки шрифтов: {str(e)}")
        return self.fallback_fonts

    def update_font_preview(self):
        try:
            font_obj = self._get_cached_font(self.font_name.get(), 20)
            img = Image.new('RGBA', (150, 40), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), "АБВ abc", fill="#ffffff", font=font_obj)
            self.font_preview_img = ImageTk.PhotoImage(img)
            self.font_preview_label.configure(image=self.font_preview_img)
            self.status_var.set(f"Предпросмотр шрифта: {self.font_name.get()}")
        except Exception as e:
            self.font_preview_label.configure(image=None)
            self.status_var.set(f"Ошибка предпросмотра шрифта: {str(e)}")

    def _get_cached_font(self, font_name, size):
        cache_key = (font_name, size)
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        try:
            font = load_font_prefer(font_name, size)
            self.font_cache[cache_key] = font
            return font
        except Exception as e:
            self.status_var.set(f"Шрифт {font_name} не загружен: {str(e)}. Пробуем резервные шрифты.")

        for fallback in self.fallback_fonts:
            try:
                font = load_font_prefer(fallback, size)
                self.font_cache[cache_key] = font
                self.font_name.set(fallback)
                self.status_var.set(f"Используется резервный шрифт: {fallback}")
                return font
            except:
                continue

        self.status_var.set("Все шрифты недоступны, используется стандартный шрифт")
        font = ImageFont.load_default()
        self.font_cache[cache_key] = font
        return font

    def save_preset(self):
        preset_name = filedialog.asksaveasfilename(
            initialdir=self.presets_dir,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if preset_name:
            settings = {
                'text': self.text_content.get(),
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
                'preview_width': self.preview_width.get(),
                'preview_height': self.preview_height.get(),
                'auto_size_canvas': self.auto_size_canvas.get(),
                'bg_color': self.bg_color.get(),
                'bg_transparent': self.bg_transparent.get()
            }
            try:
                with open(preset_name, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=4)
                self.update_preset_previews()
                self.status_var.set(f"Пресет сохранён: {os.path.basename(preset_name)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить пресет: {e}")

    def load_preset(self, preset_path=None):
        if not preset_path:
            preset_path = filedialog.askopenfilename(
                initialdir=self.presets_dir,
                filetypes=[("JSON files", "*.json")]
            )
        if preset_path:
            try:
                with open(preset_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                for key, value in settings.items():
                    if hasattr(self, key) and isinstance(self.__dict__[key], (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)):
                        self.__dict__[key].set(value)
                self.update_font_preview()
                self.save_state()
                self.update_preview_debounced()
                self.status_var.set(f"Пресет загружен: {os.path.basename(preset_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить пресет: {e}")

    def update_preset_previews(self):
        for widget in self.preset_frame.winfo_children():
            widget.destroy()
        presets = [f for f in os.listdir(self.presets_dir) if f.endswith('.json')]
        for idx, preset in enumerate(presets):
            try:
                with open(os.path.join(self.presets_dir, preset), 'r', encoding='utf-8') as f:
                    preset_data = json.load(f)
                img = self.generate_preset_preview(preset_data)
                tk_img = ImageTk.PhotoImage(img.resize((100, 100), Image.Resampling.LANCZOS))
                btn = tk.Button(self.preset_frame, image=tk_img,
                                command=lambda p=preset: self.load_preset(os.path.join(self.presets_dir, p)),
                                **self.gui.button_style)
                btn.image = tk_img
                btn.grid(row=idx // 4, column=idx % 4, padx=5, pady=5)
                tk.Label(self.preset_frame, text=preset, **self.gui.button_style).grid(row=idx // 4 + 1, column=idx % 4,
                                                                                       padx=5, pady=2)
            except:
                continue

    def generate_preset_preview(self, preset):
        font_obj = self._get_cached_font(preset.get('font_name', self.available_fonts[0]), 20)
        mask = self.funcs.create_text_mask((200, 100), preset.get('text', 'Предпросмотр'), font_obj,
                                           align=preset.get('align', 'center'), spacing=preset.get('line_spacing', 0),
                                           stroke_width=preset.get('stroke_width', 0))
        img = Image.new('RGBA', (200, 100), (0, 0, 0, 0))
        if preset.get('gradient_enabled', False):
            grad = self.funcs.create_gradient_image((200, 100), preset.get('gradient_start', '#ffffff'),
                                                    preset.get('gradient_end', '#ffffff'),
                                                    preset.get('gradient_dir', 'Горизонтальное'))
            text_img = self.funcs.apply_gradient_to_text(mask, grad)
        else:
            text_img = Image.new('RGBA', (200, 100),
                                 self.funcs.hex_to_rgb(preset.get('text_color', '#ffffff')) + (255,))
            text_img.putalpha(mask)
        return Image.alpha_composite(img, text_img)

    def open_presets_folder(self):
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
        chosen = colorchooser.askcolor(initialcolor=var.get())[1]
        if chosen:
            var.set(chosen)
            self.save_state()
            self.update_preview_debounced()

    def randomize_style(self):
        self.text_color.set('#' + ''.join(random.choice('23456789ABCDEF') for _ in range(6)))
        self.stroke_color.set('#' + ''.join(random.choice('0123456789ABCDEF') for _ in range(6)))
        self.stroke_width.set(random.randint(0, 10))
        self.opacity.set(random.randint(70, 100))
        self.font_name.set(random.choice(self.available_fonts))
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
            self.gradient_dir.set(random.choice(['Горизонтальное', 'Вертикальное', 'Диагональное']))
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
        self.update_font_preview()
        self.save_state()
        self.update_preview_debounced()
        self.status_var.set("Случайный стиль применён")

    def update_preview_debounced(self):
        if self._preview_after_id:
            self.root.after_cancel(self._preview_after_id)
        self._preview_after_id = self.root.after(300, self._update_preview)

    def _update_preview(self):
        if self.is_processing:
            return
        self.is_processing = True
        settings = {
            'text': self.text_content.get() or "Пример текста",
            'zoom': self.zoom.get(),
            'width': self.preview_width.get(),
            'height': self.preview_height.get(),
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
        self.processing_thread.start()

    def _process_image(self, settings):
        try:
            font_obj = self._get_cached_font(settings['font_name'], settings['font_size'])
            size = (settings['width'], settings['height'])

            if settings['auto_size_canvas']:
                tw, th = self.funcs.calculate_text_bbox(settings['text'], font_obj, settings['line_spacing'],
                                                        settings['stroke_width'], settings['rotation_angle'])
                size = (tw + 100, th + 100)

            canvas = Image.new('RGBA', size, (0, 0, 0, 0) if settings['bg_transparent'] else self.funcs.hex_to_rgb(
                settings['bg_color']))

            text_mask = self.funcs.create_text_mask(size, settings['text'], font_obj, align=settings['align'],
                                                    spacing=settings['line_spacing'],
                                                    stroke_width=settings['stroke_width'],
                                                    rotation=settings['rotation_angle'])

            if settings['gradient_enabled']:
                grad = self.funcs.create_gradient_image(size, settings['gradient_start'], settings['gradient_end'],
                                                        settings['gradient_dir'])
                text_img = self.funcs.apply_gradient_to_text(text_mask, grad)
            else:
                text_img = Image.new('RGBA', size, self.funcs.hex_to_rgb(settings['text_color']) + (255,))
                text_img.putalpha(text_mask)

            if settings['inner_glow_intensity'] > 0:
                inner_glow = self.funcs.apply_inner_glow(text_mask, settings['inner_glow_color'],
                                                         settings['inner_glow_intensity'])
                canvas = Image.alpha_composite(canvas, inner_glow)

            canvas = Image.alpha_composite(canvas, text_img)

            if settings['glow_intensity'] > 0:
                canvas = self.funcs.apply_neon_effect(canvas, settings['glow_color'], settings['glow_intensity'])

            if settings['neon_intensity'] > 0:
                canvas = self.funcs.apply_neon_effect(canvas, settings['neon_color'], settings['neon_intensity'])

            if settings['shadow_offset'] > 0:
                shadow_mask = self.funcs.create_text_mask(size, settings['text'], font_obj, align=settings['align'],
                                                         spacing=settings['line_spacing'],
                                                         stroke_width=settings['stroke_width'],
                                                         rotation=settings['rotation_angle'])
                shadow_img = Image.new('RGBA', size, self.funcs.hex_to_rgb(settings['shadow_color']) + (255,))
                shadow_img.putalpha(shadow_mask)
                shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=settings['shadow_blur']))
                dx = int(math.cos(math.radians(settings['shadow_angle'])) * settings['shadow_offset'])
                dy = int(math.sin(math.radians(settings['shadow_angle'])) * settings['shadow_offset'])
                shadow_canvas = Image.new('RGBA', size, (0, 0, 0, 0))
                shadow_canvas.paste(shadow_img, (dx, dy))
                canvas = Image.alpha_composite(shadow_canvas, canvas)

            if settings['threed_depth'] > 0:
                canvas = self.funcs.apply_3d_effect(canvas, settings['threed_depth'], settings['threed_angle'])

            if settings['texture_intensity'] > 0:
                texture = self.funcs.create_noise_texture(size, settings['texture_intensity'] / 100.0)
                canvas = Image.alpha_composite(canvas, texture)

            if settings['emboss_intensity'] > 0:
                canvas = self.funcs.apply_bevel(canvas, settings['emboss_intensity'])

            if settings['bevel_intensity'] > 0:
                canvas = self.funcs.apply_bevel(canvas, settings['bevel_intensity'])

            if settings['wave_amplitude'] > 0:
                canvas = self.funcs.apply_wave_distortion(canvas, settings['wave_amplitude'],
                                                         settings['wave_wavelength'])

            if settings['perspective_strength'] > 0:
                canvas = self.funcs.apply_perspective_like(canvas, settings['perspective_strength'])

            if settings['reflection_enabled']:
                canvas = self.funcs.apply_reflection(canvas, settings['reflection_opacity'],
                                                    settings['reflection_offset'])

            if settings['opacity'] < 100:
                canvas.putalpha(int(255 * (settings['opacity'] / 100.0)))

            zoomed = canvas.resize((int(size[0] * settings['zoom']), int(size[1] * settings['zoom'])),
                                  Image.Resampling.LANCZOS)
            self.image_queue.put((zoomed, size[0], size[1], settings['zoom']))
        except Exception as e:
            self.image_queue.put(('error', str(e)))
        finally:
            self.is_processing = False

    def _check_image_queue(self):
        try:
            result = self.image_queue.get_nowait()
            if isinstance(result, tuple) and len(result) == 4:
                img, w, h, zoom = result
                tk_img = ImageTk.PhotoImage(img)
                self.preview_canvas.delete("all")
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                x = (canvas_width - tk_img.width()) // 2
                y = (canvas_height - tk_img.height()) // 2
                self.preview_canvas.create_image(x, y, image=tk_img, anchor="nw")
                self.preview_canvas.image = tk_img
                self.preview_canvas.configure(scrollregion=(0, 0, tk_img.width(), tk_img.height()))
                self.status_var.set("Предпросмотр обновлён")
            elif isinstance(result, tuple) and len(result) == 2:
                self.status_var.set(f"Ошибка обработки: {result[1]}")
        except queue.Empty:
            pass
        self.root.after(100, self._check_image_queue)

    def _on_preview_mousewheel(self, event):
        if event.delta > 0 or event.num == 4:
            self.zoom.set(min(self.zoom.get() * 1.1, 5.0))
        elif event.delta < 0 or event.num == 5:
            self.zoom.set(max(self.zoom.get() / 1.1, 0.1))
        self.update_preview_debounced()
        self.status_var.set(f"Масштаб: {self.zoom.get():.2f}x")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextEffectEditorApp(root)
    root.mainloop()