import tkinter as tk
from gui import TextEffectEditorGUI
from functions import TextEffectFunctions
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk
import os


class TextEffectEditor:
    def __init__(self, root):
        self.root = root

        # Устанавливаем полноэкранный режим
        self.root.attributes('-fullscreen', True)

        # Добавляем кнопку выхода из полноэкранного режима
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)

        # Variables
        self.text_content = "Ваш текст здесь"
        self.text_color = "#ffffff"
        self.bg_color = "#0f0f23"  # Изменен на темный фон как в Fibonacci Scan
        self.font_name = "Arial"
        self.font_size = 48
        self.shadow_color = "#000000"
        self.shadow_offset = 5
        self.shadow_blur = 2
        self.stroke_color = "#000000"
        self.stroke_width = 2
        self.glow_color = "#6366f1"  # Акцентный цвет Fibonacci Scan
        self.glow_intensity = 10
        self.rotation = 0
        self.opacity = 100

        # New effects variables
        self.gradient_start = "#ff0000"
        self.gradient_end = "#0000ff"
        self.gradient_direction = "horizontal"
        self.perspective_distortion = 0
        self.wave_distortion = 0
        self.emboss_intensity = 0
        self.texture_intensity = 0
        self.zoom_factor = 1.0

        # Canvas references
        self.text_color_canvas = None
        self.stroke_color_canvas = None
        self.shadow_color_canvas = None
        self.glow_color_canvas = None
        self.gradient_start_canvas = None
        self.gradient_end_canvas = None
        self.preview_canvas = None

        # UI variables dictionary
        self.ui_vars = {}

        # Initialize components
        self.functions = TextEffectFunctions(self)
        self.gui = TextEffectEditorGUI(root, self)

        # Get UI variables from GUI
        self.ui_vars = self.gui.get_vars()

        # Добавляем недостающие переменные
        self.ui_vars['gradient_dir_var'] = tk.StringVar(value="horizontal")
        self.ui_vars['shadow_blur_var'] = tk.IntVar(value=2)
        self.ui_vars['glow_intensity_var'] = tk.IntVar(value=10)
        self.ui_vars['emboss_var'] = tk.IntVar(value=0)
        self.ui_vars['texture_var'] = tk.IntVar(value=0)
        self.ui_vars['perspective_var'] = tk.IntVar(value=0)
        self.ui_vars['wave_var'] = tk.IntVar(value=0)
        self.ui_vars['zoom_var'] = tk.DoubleVar(value=1.0)
        self.ui_vars['bg_transparent'] = tk.BooleanVar(value=False)

        # Bind variable changes
        self.setup_variable_trace()

        # Initial update
        self.update_preview()

    def toggle_fullscreen(self, event=None):
        # Переключение полноэкранного режима
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def setup_variable_trace(self):
        """Setup tracing for all variables that should update preview"""
        variables_to_trace = [
            'text_var', 'font_var', 'size_var', 'gradient_dir_var',
            'opacity_var', 'rotation_var', 'stroke_width_var',
            'shadow_offset_var', 'shadow_blur_var', 'glow_intensity_var',
            'emboss_var', 'texture_var', 'perspective_var', 'wave_var',
            'zoom_var'
        ]

        for var_name in variables_to_trace:
            if var_name in self.ui_vars:
                var = self.ui_vars[var_name]
                if hasattr(var, 'trace_add'):
                    var.trace_add('write', lambda *args: self.update_preview())
                elif hasattr(var, 'trace'):
                    var.trace('w', lambda *args: self.update_preview())

    def on_mousewheel(self, event):
        # Zoom with mouse wheel
        if event.delta > 0 or event.num == 4:
            self.ui_vars['zoom_var'].set(min(3.0, self.ui_vars['zoom_var'].get() + 0.1))
        else:
            self.ui_vars['zoom_var'].set(max(0.5, self.ui_vars['zoom_var'].get() - 0.1))
        self.update_preview()

    def choose_color(self, color_type):
        if color_type == "text":
            current_color = self.text_color
        elif color_type == "stroke":
            current_color = self.stroke_color
        elif color_type == "shadow":
            current_color = self.shadow_color
        elif color_type == "glow":
            current_color = self.glow_color
        elif color_type == "gradient_start":
            current_color = self.gradient_start
        elif color_type == "gradient_end":
            current_color = self.gradient_end
        else:
            current_color = "#ffffff"

        color = colorchooser.askcolor(initialcolor=current_color)[1]
        if color:
            if color_type == "text":
                self.text_color = color
                self.text_color_canvas.config(bg=color)
            elif color_type == "stroke":
                self.stroke_color = color
                self.stroke_color_canvas.config(bg=color)
            elif color_type == "shadow":
                self.shadow_color = color
                self.shadow_color_canvas.config(bg=color)
            elif color_type == "glow":
                self.glow_color = color
                self.glow_color_canvas.config(bg=color)
            elif color_type == "gradient_start":
                self.gradient_start = color
                self.gradient_start_canvas.config(bg=color)
            elif color_type == "gradient_end":
                self.gradient_end = color
                self.gradient_end_canvas.config(bg=color)

            self.update_preview()

    def choose_bg_color(self):
        color = colorchooser.askcolor(initialcolor="#ffffff")[1]
        if color:
            self.bg_color = color
            self.ui_vars['bg_transparent'].set(False)
            self.update_preview()

    def update_preview(self, *args):
        if not hasattr(self, 'preview_canvas') or not self.preview_canvas:
            return

        self.preview_canvas.delete("all")

        # Get current values from UI
        text = self.ui_vars['text_var'].get()
        if not text:
            return

        font_name = self.ui_vars['font_var'].get()
        font_size = self.ui_vars['size_var'].get()
        stroke_width = self.ui_vars['stroke_width_var'].get()
        shadow_offset = self.ui_vars['shadow_offset_var'].get()
        shadow_blur = self.ui_vars['shadow_blur_var'].get()
        glow_intensity = self.ui_vars['glow_intensity_var'].get()
        rotation = self.ui_vars['rotation_var'].get()
        opacity = self.ui_vars['opacity_var'].get()
        zoom_factor = self.ui_vars['zoom_var'].get()

        # Calculate dimensions with zoom
        width, height = int(800 * zoom_factor), int(400 * zoom_factor)

        if self.ui_vars['bg_transparent'].get():
            bg_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        else:
            bg_color = self.functions.hex_to_rgb(self.bg_color)
            bg_img = Image.new('RGB', (width, height), bg_color)

        draw = ImageDraw.Draw(bg_img)

        try:
            # Try to load the font with support for Russian characters
            font_obj = ImageFont.truetype(font_name, font_size)
        except:
            try:
                # Try Arial if selected font doesn't work
                font_obj = ImageFont.truetype("Arial", font_size)
            except:
                # Fallback to default font
                font_obj = ImageFont.load_default()

        # Calculate text position (centered)
        try:
            bbox = draw.textbbox((0, 0), text, font=font_obj)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # Fallback if textbbox fails
            text_width = len(text) * font_size // 2
            text_height = font_size

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Draw glow effect
        if glow_intensity > 0:
            for i in range(glow_intensity):
                glow_size = font_size + i
                try:
                    glow_font = ImageFont.truetype(font_name, glow_size)
                except:
                    try:
                        glow_font = ImageFont.truetype("Arial", glow_size)
                    except:
                        glow_font = ImageFont.load_default()

                glow_color = self.functions.hex_to_rgb(self.glow_color) + (100,)
                try:
                    draw.text((x - i // 2, y - i // 2), text, fill=glow_color, font=glow_font)
                except:
                    pass

        # Draw shadow
        if shadow_offset > 0:
            shadow_color = self.functions.hex_to_rgb(self.shadow_color)
            for i in range(shadow_blur + 1):
                offset = shadow_offset + i
                try:
                    draw.text((x + offset, y + offset), text, fill=shadow_color, font=font_obj)
                except:
                    pass

        # Draw stroke
        if stroke_width > 0:
            stroke_color = self.functions.hex_to_rgb(self.stroke_color)
            for dx in [-stroke_width, 0, stroke_width]:
                for dy in [-stroke_width, 0, stroke_width]:
                    if dx != 0 or dy != 0:
                        try:
                            draw.text((x + dx, y + dy), text, fill=stroke_color, font=font_obj)
                        except:
                            pass

        # Apply gradient if needed
        if self.gradient_start != self.gradient_end:
            try:
                self.functions.apply_gradient(draw, text, font_obj, (x, y), (text_width, text_height))
            except:
                pass

        # Draw main text
        text_color = self.functions.hex_to_rgb(self.text_color)
        if opacity < 100:
            text_color = text_color + (int(255 * opacity / 100),)
        try:
            draw.text((x, y), text, fill=text_color, font=font_obj)
        except:
            # If text rendering fails, use a fallback
            try:
                draw.text((x, y), "Render Error", fill=text_color, font=font_obj)
            except:
                pass

        # Apply emboss effect
        emboss = self.ui_vars['emboss_var'].get()
        if emboss > 0:
            try:
                bg_img = bg_img.filter(ImageFilter.EMBOSS)
            except:
                pass

        # Apply texture effect
        texture = self.ui_vars['texture_var'].get()
        if texture > 0:
            try:
                texture_overlay = self.functions.create_texture_overlay(width, height)
                bg_img = Image.alpha_composite(bg_img.convert('RGBA'), texture_overlay)
            except:
                pass

        # Apply distortion effects
        try:
            bg_img = self.functions.apply_distortion(bg_img)
        except:
            pass

        # Apply rotation
        if rotation != 0:
            try:
                bg_img = bg_img.rotate(rotation, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
            except:
                try:
                    bg_img = bg_img.rotate(rotation, expand=True, resample=Image.BICUBIC)
                except:
                    pass

        # Convert to PhotoImage and display
        try:
            self.tk_image = ImageTk.PhotoImage(bg_img)
            self.preview_canvas.create_image(width // 2, height // 2, image=self.tk_image)

            # Update scroll region
            self.preview_canvas.config(scrollregion=(0, 0, width, height))
        except Exception as e:
            print(f"Error displaying image: {e}")

    def export_png(self):
        self.export_image("png")

    def export_jpg(self):
        self.export_image("jpg")

    def export_image(self, format):
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[(f"{format.upper()} files", f"*.{format}")]
        )

        if file_path:
            # Recreate the image for export with higher resolution
            width, height = 2400, 1200

            if self.ui_vars['bg_transparent'].get() and format == "png":
                image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            else:
                bg_color = self.functions.hex_to_rgb(self.bg_color) if not self.ui_vars['bg_transparent'].get() else (
                255, 255, 255)
                image = Image.new('RGB', (width, height), bg_color)

            draw = ImageDraw.Draw(image)

            try:
                font_obj = ImageFont.truetype(self.ui_vars['font_var'].get(), self.ui_vars['size_var'].get() * 2)
            except:
                try:
                    font_obj = ImageFont.truetype("Arial", self.ui_vars['size_var'].get() * 2)
                except:
                    font_obj = ImageFont.load_default()

            text = self.ui_vars['text_var'].get()

            try:
                bbox = draw.textbbox((0, 0), text, font=font_obj)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                text_width = len(text) * self.ui_vars['size_var'].get()
                text_height = self.ui_vars['size_var'].get() * 2

            x = (width - text_width) // 2
            y = (height - text_height) // 2

            # Draw effects
            glow_intensity = self.ui_vars['glow_intensity_var'].get()
            if glow_intensity > 0:
                for i in range(glow_intensity * 2):
                    glow_size = self.ui_vars['size_var'].get() * 2 + i
                    try:
                        glow_font = ImageFont.truetype(self.ui_vars['font_var'].get(), glow_size)
                    except:
                        try:
                            glow_font = ImageFont.truetype("Arial", glow_size)
                        except:
                            glow_font = ImageFont.load_default()

                    glow_color = self.functions.hex_to_rgb(self.glow_color) + (100,)
                    try:
                        draw.text((x - i, y - i), text, fill=glow_color, font=glow_font)
                    except:
                        pass

            shadow_offset = self.ui_vars['shadow_offset_var'].get()
            shadow_blur = self.ui_vars['shadow_blur_var'].get()
            if shadow_offset > 0:
                shadow_color = self.functions.hex_to_rgb(self.shadow_color)
                for i in range(shadow_blur + 1):
                    offset = shadow_offset * 2 + i
                    try:
                        draw.text((x + offset, y + offset), text, fill=shadow_color, font=font_obj)
                    except:
                        pass

            stroke_width = self.ui_vars['stroke_width_var'].get()
            if stroke_width > 0:
                stroke_color = self.functions.hex_to_rgb(self.stroke_color)
                for dx in [-stroke_width * 2, 0, stroke_width * 2]:
                    for dy in [-stroke_width * 2, 0, stroke_width * 2]:
                        if dx != 0 or dy != 0:
                            try:
                                draw.text((x + dx, y + dy), text, fill=stroke_color, font=font_obj)
                            except:
                                pass

            # Draw main text
            text_color = self.functions.hex_to_rgb(self.text_color)
            opacity = self.ui_vars['opacity_var'].get()
            if opacity < 100 and format == "png":
                text_color = text_color + (int(255 * opacity / 100),)
            try:
                draw.text((x, y), text, fill=text_color, font=font_obj)
            except:
                try:
                    draw.text((x, y), "Export Error", fill=text_color, font=font_obj)
                except:
                    pass

            # Apply rotation
            rotation = self.ui_vars['rotation_var'].get()
            if rotation != 0:
                try:
                    image = image.rotate(rotation, expand=True, resample=Image.BICUBIC, fillcolor=(255, 255, 255))
                except:
                    try:
                        image = image.rotate(rotation, expand=True, resample=Image.BICUBIC)
                    except:
                        pass

            # Save the image
            try:
                image.save(file_path)
                messagebox.showinfo("Успех", f"Изображение успешно экспортировано как {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TextEffectEditor(root)
    root.mainloop()