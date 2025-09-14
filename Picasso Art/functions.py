import math
import collections
import numpy as np
from PIL import Image, ImageDraw, ImageTk, ImageColor, ImageFilter, ImageEnhance, ImageOps, ImageChops, ImageFont
from tkinter import messagebox
import random
import json
import os
import base64
from io import BytesIO


class Layer:
    def __init__(self, name, width, height, bg_color="transparent"):
        self.name = name
        self.visible = True
        self.opacity = 100
        self.locked = False
        self.blend_mode = "normal"
        self.image = Image.new("RGBA", (width, height), (0, 0, 0, 0) if bg_color == "transparent" else bg_color)
        self.draw = ImageDraw.Draw(self.image)
        self.thumbnail = None
        self.mask = None
        self.update_thumbnail()

    def update_thumbnail(self):
        """Создает миниатюру слоя"""
        if self.image:
            thumb_size = (64, 64)
            self.thumbnail = self.image.copy().convert("RGBA")
            self.thumbnail.thumbnail(thumb_size, Image.LANCZOS)

    def get_image_with_opacity(self):
        if self.opacity == 100:
            return self.image.copy()

        # Применяем прозрачность слоя
        result = self.image.copy()
        alpha = result.split()[3]
        alpha = alpha.point(lambda p: int(p * self.opacity / 100))
        result.putalpha(alpha)
        return result

    def apply_blend_mode(self, base, top):
        """Применяет режим наложения"""
        base = base.convert("RGBA")
        top = top.convert("RGBA")

        if self.blend_mode == "normal":
            return top
        elif self.blend_mode == "multiply":
            return ImageChops.multiply(base, top)
        elif self.blend_mode == "screen":
            return ImageChops.screen(base, top)
        elif self.blend_mode == "overlay":
            return ImageChops.overlay(base, top)
        elif self.blend_mode == "darken":
            return ImageChops.darker(base, top)
        elif self.blend_mode == "lighten":
            return ImageChops.lighter(base, top)
        elif self.blend_mode == "color_dodge":
            return self.blend_color_dodge(base, top)
        elif self.blend_mode == "color_burn":
            return self.blend_color_burn(base, top)
        elif self.blend_mode == "soft_light":
            return self.blend_soft_light(base, top)
        elif self.blend_mode == "hard_light":
            return ImageChops.hard_light(base, top)
        elif self.blend_mode == "difference":
            return ImageChops.difference(base, top)
        elif self.blend_mode == "exclusion":
            return self.blend_exclusion(base, top)
        return top

    def blend_color_dodge(self, base, top):
        """Режим наложения Color Dodge"""
        base_arr = np.array(base.convert("RGB")).astype(float)
        top_arr = np.array(top.convert("RGB")).astype(float)

        result_arr = base_arr / (1 - top_arr / 255)
        result_arr = np.clip(result_arr, 0, 255)

        return Image.fromarray(result_arr.astype('uint8'), 'RGB').convert("RGBA")

    def blend_color_burn(self, base, top):
        """Режим наложения Color Burn"""
        base_arr = np.array(base.convert("RGB")).astype(float)
        top_arr = np.array(top.convert("RGB")).astype(float)

        result_arr = 1 - (1 - base_arr / 255) / (top_arr / 255)
        result_arr = np.clip(result_arr * 255, 0, 255)

        return Image.fromarray(result_arr.astype('uint8'), 'RGB').convert("RGBA")

    def blend_soft_light(self, base, top):
        """Режим наложения Soft Light"""
        base_arr = np.array(base.convert("RGB")).astype(float) / 255
        top_arr = np.array(top.convert("RGB")).astype(float) / 255

        result_arr = np.where(top_arr <= 0.5,
                              2 * base_arr * top_arr + base_arr ** 2 * (1 - 2 * top_arr),
                              np.sqrt(base_arr) * (2 * top_arr - 1) + 2 * base_arr * (1 - top_arr))

        result_arr = np.clip(result_arr * 255, 0, 255)
        return Image.fromarray(result_arr.astype('uint8'), 'RGB').convert("RGBA")

    def blend_exclusion(self, base, top):
        """Режим наложения Exclusion"""
        base_arr = np.array(base.convert("RGB")).astype(float) / 255
        top_arr = np.array(top.convert("RGB")).astype(float) / 255

        result_arr = base_arr + top_arr - 2 * base_arr * top_arr
        result_arr = np.clip(result_arr * 255, 0, 255)
        return Image.fromarray(result_arr.astype('uint8'), 'RGB').convert("RGBA")


class Selection:
    def __init__(self, width, height):
        self.mask = Image.new("L", (width, height), 0)
        self.active = False
        self.mode = "rectangle"
        self.points = []


class PaintFunctions:
    def __init__(self):
        # Переменные для рисования
        self.draw_color = "#000000"
        self.alpha = 255
        self.bg_color = "#ffffff"
        self.line_width = 5
        self.current_tool = "карандаш"
        self.brush_shape = "круг"
        self.brush_hardness = 100
        self.start_x, self.start_y = None, None
        self.last_x, self.last_y = None, None
        self.temp_image = None
        self.temp_draw = None

        # Переменные для перемещения холста
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.scale_factor = 1.0
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Настройки холста
        self.canvas_width = 800
        self.canvas_height = 600

        # История действий для отмены/повтора
        self.history = []
        self.redo_stack = []
        self.max_history = 50

        # Система слоев
        self.layers = []
        self.current_layer_index = 0
        self.create_new_layer("Фон", self.bg_color)

        # Выделение
        self.selection = Selection(self.canvas_width, self.canvas_height)
        self.has_selection = False

        # Создание composite изображения
        self.composite_image = Image.new("RGB", (self.canvas_width, self.canvas_height), self.bg_color)
        self.composite_rgba = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        self.preview_image = None
        self.tk_image = None

        # Градиенты
        self.gradient_type = "linear"
        self.gradient_colors = ["#ff0000", "#0000ff"]
        self.gradient_direction = "horizontal"

        # Шаблоны кистей
        self.brush_presets = [
            {"name": "Мягкая круглая", "size": 10, "hardness": 50, "shape": "круг"},
            {"name": "Жесткая круглая", "size": 15, "hardness": 100, "shape": "круг"},
            {"name": "Квадратная", "size": 8, "hardness": 100, "shape": "квадрат"},
            {"name": "Текстурированная", "size": 20, "hardness": 30, "shape": "круг"}
        ]

    def create_new_layer(self, name, bg_color="transparent"):
        layer = Layer(name, self.canvas_width, self.canvas_height, bg_color)
        self.layers.append(layer)
        self.current_layer_index = len(self.layers) - 1
        self.update_composite_image()
        return layer

    def duplicate_layer(self, index):
        if 0 <= index < len(self.layers):
            original = self.layers[index]
            new_layer = Layer(f"{original.name} копия", self.canvas_width, self.canvas_height)
            new_layer.image = original.image.copy()
            new_layer.draw = ImageDraw.Draw(new_layer.image)
            new_layer.visible = original.visible
            new_layer.opacity = original.opacity
            new_layer.blend_mode = original.blend_mode
            new_layer.locked = original.locked
            self.layers.insert(index + 1, new_layer)
            self.current_layer_index = index + 1
            self.update_composite_image()

    def delete_layer(self, index):
        if 0 <= index < len(self.layers) and len(self.layers) > 1:
            del self.layers[index]
            if self.current_layer_index >= len(self.layers):
                self.current_layer_index = len(self.layers) - 1
            self.update_composite_image()

    def reorder_layer(self, index, new_index):
        """Перемещает слой на новую позицию"""
        if 0 <= index < len(self.layers) and 0 <= new_index < len(self.layers):
            layer = self.layers.pop(index)
            self.layers.insert(new_index, layer)
            self.current_layer_index = new_index
            self.update_composite_image()

    def merge_layers(self, indices):
        if len(indices) < 2:
            return

        indices.sort()
        merged = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))

        for i in indices:
            if self.layers[i].visible:
                layer_img = self.layers[i].get_image_with_opacity()
                merged = Image.alpha_composite(merged, layer_img)

        for i in sorted(indices, reverse=True):
            del self.layers[i]

        new_layer = Layer("Объединенный слой", self.canvas_width, self.canvas_height)
        new_layer.image = merged
        new_layer.draw = ImageDraw.Draw(new_layer.image)
        self.layers.append(new_layer)
        self.current_layer_index = len(self.layers) - 1
        self.update_composite_image()

    def toggle_layer_visibility(self, index):
        if 0 <= index < len(self.layers):
            self.layers[index].visible = not self.layers[index].visible
            self.update_composite_image()

    def set_layer_opacity(self, index, opacity):
        if 0 <= index < len(self.layers):
            self.layers[index].opacity = max(0, min(100, opacity))
            self.update_composite_image()

    def set_layer_blend_mode(self, index, blend_mode):
        if 0 <= index < len(self.layers):
            self.layers[index].blend_mode = blend_mode
            self.update_composite_image()

    def get_display_image(self, temp_layer_image=None):
        composite = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))

        for i, layer in enumerate(self.layers):
            if layer.visible and layer.opacity > 0:
                if temp_layer_image is not None and i == self.current_layer_index:
                    layer_img = temp_layer_image.convert("RGBA")
                    alpha = layer_img.split()[3].point(lambda p: int(p * layer.opacity / 100))
                    layer_img.putalpha(alpha)
                else:
                    layer_img = layer.get_image_with_opacity()
                if layer.blend_mode != "normal":
                    temp_composite = composite.copy()
                    composite = layer.apply_blend_mode(temp_composite, layer_img)
                else:
                    composite = Image.alpha_composite(composite, layer_img)

        display_base = Image.new("RGB", (self.canvas_width, self.canvas_height), self.bg_color)
        display_base.paste(composite, (0, 0), composite)
        return display_base

    def update_composite_image(self):
        self.composite_image = self.get_display_image()
        composite = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        for layer in self.layers:
            if layer.visible and layer.opacity > 0:
                layer_img = layer.get_image_with_opacity()
                if layer.blend_mode != "normal":
                    temp_composite = composite.copy()
                    composite = layer.apply_blend_mode(temp_composite, layer_img)
                else:
                    composite = Image.alpha_composite(composite, layer_img)
        self.composite_rgba = composite

    def get_current_layer(self):
        if self.layers and 0 <= self.current_layer_index < len(self.layers):
            return self.layers[self.current_layer_index]
        return None

    def convert_canvas_coords(self, x, y):
        canvas_x = (x - self.canvas_offset_x) / self.scale_factor
        canvas_y = (y - self.canvas_offset_y) / self.scale_factor
        return max(0, min(self.canvas_width - 1, int(canvas_x))), max(0, min(self.canvas_height - 1, int(canvas_y)))

    def get_color_with_alpha(self, base_color):
        try:
            if isinstance(base_color, str):
                rgb = ImageColor.getrgb(base_color)
            else:
                rgb = base_color
            return (*rgb[:3], self.alpha)
        except:
            return (0, 0, 0, self.alpha)

    def create_brush_texture(self, size, hardness=100):
        brush = Image.new("L", (size * 2, size * 2), 0)
        draw = ImageDraw.Draw(brush)

        center = size
        radius = size

        if hardness == 100:
            draw.ellipse([0, 0, size * 2 - 1, size * 2 - 1], fill=255)
        else:
            hardness_factor = hardness / 100.0
            for y in range(size * 2):
                for x in range(size * 2):
                    distance = math.sqrt((x - center) ** 2 + (y - center) ** 2)
                    if distance <= radius * hardness_factor:
                        alpha = 255
                    elif distance <= radius:
                        alpha = int(255 * (1 - (distance - radius * hardness_factor) / (radius * (1 - hardness_factor))))
                    else:
                        alpha = 0
                    brush.putpixel((x, y), alpha)

        return brush

    def start_drawing(self, x, y):
        layer = self.get_current_layer()
        if not layer or layer.locked:
            return False

        self.temp_image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        self.temp_draw = ImageDraw.Draw(self.temp_image)
        return True

    def draw_preview(self, x, y):
        if self.temp_draw is None:
            return

        if self.current_tool == "ластик":
            color = (0, 0, 0, 0)
        else:
            color = self.get_color_with_alpha(self.draw_color)

        brush_size = max(1, self.line_width)

        if self.brush_shape == "квадрат":
            self.temp_draw.rectangle([x - brush_size, y - brush_size, x + brush_size, y + brush_size], fill=color)
        elif self.brush_shape == "диагональ":
            self.temp_draw.line([x - brush_size, y + brush_size, x + brush_size, y - brush_size], fill=color, width=brush_size * 2)
        else:
            self.temp_draw.ellipse([x - brush_size, y - brush_size, x + brush_size, y + brush_size], fill=color)

    def apply_drawing(self):
        if self.temp_image and self.temp_draw:
            layer = self.get_current_layer()
            if layer and not layer.locked:
                layer.image = Image.alpha_composite(layer.image, self.temp_image)
                layer.draw = ImageDraw.Draw(layer.image)
                layer.update_thumbnail()

        self.temp_image = None
        self.temp_draw = None

    def draw_on_image(self, last_x, last_y, x, y):
        layer = self.get_current_layer()
        if not layer or layer.locked:
            return

        brush_size = max(1, self.line_width)

        if self.current_tool == "карандаш":
            color = self.get_color_with_alpha(self.draw_color)
            layer.draw.line([last_x, last_y, x, y], fill=color, width=brush_size)
        else:
            if self.current_tool == "ластик":
                color = (0, 0, 0, 0)
            else:
                color = self.get_color_with_alpha(self.draw_color)

            distance = math.sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
            steps = max(2, int(distance / (brush_size / 2)))

            for i in range(steps):
                t = i / steps
                cx = last_x + t * (x - last_x)
                cy = last_y + t * (y - last_y)

                if self.brush_shape == "квадрат":
                    layer.draw.rectangle([cx - brush_size, cy - brush_size, cx + brush_size, cy + brush_size], fill=color)
                elif self.brush_shape == "диагональ":
                    layer.draw.line([cx - brush_size, cy + brush_size, cx + brush_size, cy - brush_size], fill=color, width=brush_size * 2)
                else:
                    layer.draw.ellipse([cx - brush_size, cy - brush_size, cx + brush_size, cy + brush_size], fill=color)

        layer.update_thumbnail()
        self.update_composite_image()

    def draw_shape_preview(self, start_x, start_y, end_x, end_y):
        if self.temp_draw is None:
            return

        color = self.get_color_with_alpha(self.draw_color)
        self.temp_draw.rectangle([0, 0, self.canvas_width, self.canvas_height], fill=(0, 0, 0, 0))

        if self.current_tool == "линия":
            self.temp_draw.line([start_x, start_y, end_x, end_y], fill=color, width=self.line_width)
        elif self.current_tool == "прямоугольник":
            self.temp_draw.rectangle([start_x, start_y, end_x, end_y], outline=color, width=self.line_width)
        elif self.current_tool == "заполненный прямоугольник":
            self.temp_draw.rectangle([start_x, start_y, end_x, end_y], fill=color)
        elif self.current_tool == "овал":
            self.temp_draw.ellipse([start_x, start_y, end_x, end_y], outline=color, width=self.line_width)
        elif self.current_tool == "заполненный овал":
            self.temp_draw.ellipse([start_x, start_y, end_x, end_y], fill=color)
        elif self.current_tool == "многоугольник":
            if len(self.selection.points) > 1:
                self.temp_draw.polygon(self.selection.points, outline=color, width=self.line_width)
        elif self.current_tool == "заполненный многоугольник":
            if len(self.selection.points) > 1:
                self.temp_draw.polygon(self.selection.points, fill=color)

    def draw_shape_final(self, start_x, start_y, end_x, end_y):
        layer = self.get_current_layer()
        if not layer or layer.locked:
            return

        color = self.get_color_with_alpha(self.draw_color)

        if self.current_tool == "линия":
            layer.draw.line([start_x, start_y, end_x, end_y], fill=color, width=self.line_width)
        elif self.current_tool == "прямоугольник":
            layer.draw.rectangle([start_x, start_y, end_x, end_y], outline=color, width=self.line_width)
        elif self.current_tool == "заполненный прямоугольник":
            layer.draw.rectangle([start_x, start_y, end_x, end_y], fill=color)
        elif self.current_tool == "овал":
            layer.draw.ellipse([start_x, start_y, end_x, end_y], outline=color, width=self.line_width)
        elif self.current_tool == "заполненный овал":
            layer.draw.ellipse([start_x, start_y, end_x, end_y], fill=color)
        elif self.current_tool == "многоугольник":
            if len(self.selection.points) > 1:
                layer.draw.polygon(self.selection.points, outline=color, width=self.line_width)
        elif self.current_tool == "заполненный многоугольник":
            if len(self.selection.points) > 1:
                layer.draw.polygon(self.selection.points, fill=color)

        layer.update_thumbnail()
        self.update_composite_image()

    def flood_fill(self, x, y):
        layer = self.get_current_layer()
        if not layer or layer.locked:
            return

        target_color = layer.image.getpixel((x, y))
        replacement_color = self.get_color_with_alpha(self.draw_color)

        if target_color == replacement_color:
            return

        pixels = collections.deque([(x, y)])
        visited = set()

        while pixels:
            px, py = pixels.popleft()
            if (px, py) in visited or not (0 <= px < self.canvas_width and 0 <= py < self.canvas_height):
                continue
            if layer.image.getpixel((px, py)) != target_color:
                continue

            layer.image.putpixel((px, py), replacement_color)
            visited.add((px, py))

            pixels.append((px + 1, py))
            pixels.append((px - 1, py))
            pixels.append((px, py + 1))
            pixels.append((px, py - 1))

        layer.update_thumbnail()
        self.update_composite_image()

    def add_text_to_image(self, x, y, text, font_size=20, font_name="arial.ttf"):
        layer = self.get_current_layer()
        if not layer or layer.locked:
            return

        try:
            try:
                font = ImageFont.truetype(font_name, font_size)
            except:
                try:
                    font = ImageFont.truetype("Arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
        except ImportError:
            font = None

        color = self.get_color_with_alpha(self.draw_color)

        if font:
            layer.draw.text((x, y), text, fill=color, font=font)
        else:
            layer.draw.text((x, y), text, fill=color)

        layer.update_thumbnail()
        self.update_composite_image()

    def apply_filter(self, filter_type, strength=1.0):
        layer = self.get_current_layer()
        if not layer or layer.locked:
            return

        if filter_type == "blur":
            layer.image = layer.image.filter(ImageFilter.GaussianBlur(strength))
        elif filter_type == "sharpen":
            layer.image = layer.image.filter(ImageFilter.UnsharpMask(radius=strength, percent=150, threshold=3))
        elif filter_type == "brightness":
            enhancer = ImageEnhance.Brightness(layer.image.convert("RGB"))
            layer.image = enhancer.enhance(strength).convert("RGBA")
        elif filter_type == "contrast":
            enhancer = ImageEnhance.Contrast(layer.image.convert("RGB"))
            layer.image = enhancer.enhance(strength).convert("RGBA")
        elif filter_type == "saturation":
            enhancer = ImageEnhance.Color(layer.image.convert("RGB"))
            layer.image = enhancer.enhance(strength).convert("RGBA")
        elif filter_type == "grayscale":
            layer.image = ImageOps.grayscale(layer.image.convert("RGB")).convert("RGBA")
        elif filter_type == "invert":
            layer.image = ImageOps.invert(layer.image.convert("RGB")).convert("RGBA")
        elif filter_type == "emboss":
            layer.image = layer.image.filter(ImageFilter.EMBOSS)
        elif filter_type == "find_edges":
            layer.image = layer.image.filter(ImageFilter.FIND_EDGES)

        layer.draw = ImageDraw.Draw(layer.image)
        layer.update_thumbnail()
        self.update_composite_image()

    def transform_layer(self, transform_type, **kwargs):
        layer = self.get_current_layer()
        if not layer or layer.locked:
            return

        if transform_type == "rotate":
            angle = kwargs.get("angle", 0)
            layer.image = layer.image.rotate(angle, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
        elif transform_type == "flip":
            direction = kwargs.get("direction", "horizontal")
            if direction == "horizontal":
                layer.image = layer.image.transpose(Image.FLIP_LEFT_RIGHT)
            else:
                layer.image = layer.image.transpose(Image.FLIP_TOP_BOTTOM)
        elif transform_type == "scale":
            scale_x = kwargs.get("scale_x", 1.0)
            scale_y = kwargs.get("scale_y", 1.0)
            new_width = int(self.canvas_width * scale_x)
            new_height = int(self.canvas_height * scale_y)
            layer.image = layer.image.resize((new_width, new_height), Image.LANCZOS)
        elif transform_type == "crop":
            bbox = kwargs.get("bbox", (0, 0, self.canvas_width, self.canvas_height))
            layer.image = layer.image.crop(bbox)

        layer.draw = ImageDraw.Draw(layer.image)
        layer.update_thumbnail()
        self.update_composite_image()

    def create_selection(self, mode, points):
        self.selection.mode = mode
        self.selection.points = points
        self.selection.active = True

        mask = Image.new("L", (self.canvas_width, self.canvas_height), 0)
        draw = ImageDraw.Draw(mask)

        if mode == "rectangle" and len(points) == 2:
            draw.rectangle(points, fill=255)
        elif mode == "ellipse" and len(points) == 2:
            draw.ellipse(points, fill=255)
        elif mode == "lasso" and len(points) > 2:
            draw.polygon(points, fill=255)
        elif mode == "polygon" and len(points) > 2:
            draw.polygon(points, fill=255)
        elif mode == "magic_wand" and len(points) == 1:
            x, y = points[0]
            layer = self.get_current_layer()
            if layer:
                target_color = layer.image.getpixel((x, y))
                tolerance = 10
                for py in range(self.canvas_height):
                    for px in range(self.canvas_width):
                        pixel = layer.image.getpixel((px, py))
                        if all(abs(pixel[i] - target_color[i]) <= tolerance for i in range(4)):
                            mask.putpixel((px, py), 255)

        self.selection.mask = mask
        self.has_selection = True

    def clear_selection(self):
        self.selection.active = False
        self.has_selection = False
        self.selection.mask = Image.new("L", (self.canvas_width, self.canvas_height), 0)
        self.selection.points = []

    def apply_selection_mask(self):
        if not self.has_selection:
            return

        layer = self.get_current_layer()
        if layer and not layer.locked:
            alpha = layer.image.split()[3]
            alpha = ImageChops.multiply(alpha, self.selection.mask)
            layer.image.putalpha(alpha)
            layer.draw = ImageDraw.Draw(layer.image)
            layer.update_thumbnail()
            self.update_composite_image()

        self.clear_selection()

    def invert_selection(self):
        if self.has_selection:
            self.selection.mask = ImageOps.invert(self.selection.mask)

    def create_gradient(self, start_x, start_y, end_x, end_y):
        layer = self.get_current_layer()
        if not layer or layer.locked:
            return

        start_rgb = ImageColor.getrgb(self.gradient_colors[0])
        end_rgb = ImageColor.getrgb(self.gradient_colors[1])

        gradient = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)

        if self.gradient_type == "linear":
            if self.gradient_direction == "horizontal":
                for x in range(self.canvas_width):
                    ratio = x / self.canvas_width
                    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
                    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
                    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
                    a = int(self.alpha * (1 - ratio))
                    draw.line([(x, 0), (x, self.canvas_height)], fill=(r, g, b, a))
            else:
                for y in range(self.canvas_height):
                    ratio = y / self.canvas_height
                    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
                    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
                    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
                    a = int(self.alpha * (1 - ratio))
                    draw.line([(0, y), (self.canvas_width, y)], fill=(r, g, b, a))
        elif self.gradient_type == "radial":
            center_x, center_y = (start_x + end_x) / 2, (start_y + end_y) / 2
            radius = max(abs(end_x - start_x), abs(end_y - start_y)) / 2
            for y in range(self.canvas_height):
                for x in range(self.canvas_width):
                    distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                    ratio = min(distance / radius, 1.0)
                    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
                    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
                    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
                    a = int(self.alpha * (1 - ratio))
                    gradient.putpixel((x, y), (r, g, b, a))

        layer.image = Image.alpha_composite(layer.image, gradient)
        layer.draw = ImageDraw.Draw(layer.image)
        layer.update_thumbnail()
        self.update_composite_image()

    def save_state(self):
        layer_states = []
        for layer in self.layers:
            layer_states.append({
                'image': layer.image.copy(),
                'visible': layer.visible,
                'opacity': layer.opacity,
                'blend_mode': layer.blend_mode,
                'locked': layer.locked
            })

        self.history.append({
            'layers': layer_states,
            'current_index': self.current_layer_index,
            'selection': self.selection.mask.copy() if self.has_selection else None
        })

        self.redo_stack.clear()
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def undo(self):
        if self.history:
            current_states = []
            for layer in self.layers:
                current_states.append({
                    'image': layer.image.copy(),
                    'visible': layer.visible,
                    'opacity': layer.opacity,
                    'blend_mode': layer.blend_mode,
                    'locked': layer.locked
                })

            self.redo_stack.append({
                'layers': current_states,
                'current_index': self.current_layer_index,
                'selection': self.selection.mask.copy() if self.has_selection else None
            })

            if len(self.redo_stack) > self.max_history:
                self.redo_stack.pop(0)

            previous_state = self.history.pop()
            for i, layer_state in enumerate(previous_state['layers']):
                if i < len(self.layers):
                    self.layers[i].image = layer_state['image']
                    self.layers[i].visible = layer_state['visible']
                    self.layers[i].opacity = layer_state['opacity']
                    self.layers[i].blend_mode = layer_state['blend_mode']
                    self.layers[i].locked = layer_state['locked']
                    self.layers[i].draw = ImageDraw.Draw(self.layers[i].image)
                    self.layers[i].update_thumbnail()

            self.current_layer_index = previous_state['current_index']

            if previous_state['selection']:
                self.selection.mask = previous_state['selection']
                self.has_selection = True
            else:
                self.clear_selection()

            self.update_composite_image()
            return True
        return False

    def redo(self):
        if self.redo_stack:
            current_states = []
            for layer in self.layers:
                current_states.append({
                    'image': layer.image.copy(),
                    'visible': layer.visible,
                    'opacity': layer.opacity,
                    'blend_mode': layer.blend_mode,
                    'locked': layer.locked
                })

            self.history.append({
                'layers': current_states,
                'current_index': self.current_layer_index,
                'selection': self.selection.mask.copy() if self.has_selection else None
            })

            if len(self.history) > self.max_history:
                self.history.pop(0)

            redo_state = self.redo_stack.pop()
            for i, layer_state in enumerate(redo_state['layers']):
                if i < len(self.layers):
                    self.layers[i].image = layer_state['image']
                    self.layers[i].visible = layer_state['visible']
                    self.layers[i].opacity = layer_state['opacity']
                    self.layers[i].blend_mode = layer_state['blend_mode']
                    self.layers[i].locked = layer_state['locked']
                    self.layers[i].draw = ImageDraw.Draw(self.layers[i].image)
                    self.layers[i].update_thumbnail()

            self.current_layer_index = redo_state['current_index']

            if redo_state['selection']:
                self.selection.mask = redo_state['selection']
                self.has_selection = True
            else:
                self.clear_selection()

            self.update_composite_image()
            return True
        return False

    def new_image(self, width=None, height=None, bg_color=None):
        if width:
            self.canvas_width = width
        if height:
            self.canvas_height = height
        if bg_color:
            self.bg_color = bg_color

        self.layers = []
        self.current_layer_index = 0
        self.create_new_layer("Фон", self.bg_color)
        self.history.clear()
        self.redo_stack.clear()
        self.clear_selection()
        self.update_composite_image()

    def clear_canvas(self):
        layer = self.get_current_layer()
        if layer and not layer.locked:
            layer.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
            layer.draw = ImageDraw.Draw(layer.image)
            layer.update_thumbnail()
            self.update_composite_image()

    def save_image(self, file_path, format=None):
        if format is None:
            _, ext = os.path.splitext(file_path)
            ext = ext.lower().lstrip('.')
            if ext in ['jpg', 'jpeg']:
                format = 'JPEG'
            elif ext == 'png':
                format = 'PNG'
            elif ext == 'bmp':
                format = 'BMP'
            elif ext == 'gif':
                format = 'GIF'
            elif ext == 'tiff':
                format = 'TIFF'
            else:
                format = 'PNG'

        if format.upper() in ['PNG', 'TIFF']:
            self.composite_rgba.save(file_path, format=format)
        else:
            self.composite_image.save(file_path, format=format)

    def save_project(self, file_path):
        project_data = {
            'canvas_width': self.canvas_width,
            'canvas_height': self.canvas_height,
            'bg_color': self.bg_color,
            'layers': [],
            'current_layer_index': self.current_layer_index,
            'brush_presets': self.brush_presets
        }

        for layer in self.layers:
            buffer = BytesIO()
            layer.image.save(buffer, "PNG")
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

            project_data['layers'].append({
                'name': layer.name,
                'visible': layer.visible,
                'opacity': layer.opacity,
                'blend_mode': layer.blend_mode,
                'locked': layer.locked,
                'image_data': image_data
            })

        with open(file_path, 'w') as f:
            json.dump(project_data, f)

    def load_project(self, file_path):
        try:
            with open(file_path, 'r') as f:
                project_data = json.load(f)

            self.canvas_width = project_data['canvas_width']
            self.canvas_height = project_data['canvas_height']
            self.bg_color = project_data['bg_color']
            self.brush_presets = project_data.get('brush_presets', self.brush_presets)

            self.layers = []
            for layer_data in project_data['layers']:
                if 'image_data' in layer_data:
                    buffer = BytesIO(base64.b64decode(layer_data['image_data']))
                    image = Image.open(buffer).convert("RGBA")
                else:
                    image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))

                layer = Layer(layer_data['name'], self.canvas_width, self.canvas_height)
                layer.image = image
                layer.draw = ImageDraw.Draw(layer.image)
                layer.visible = layer_data['visible']
                layer.opacity = layer_data['opacity']
                layer.blend_mode = layer_data['blend_mode']
                layer.locked = layer_data['locked']
                layer.update_thumbnail()

                self.layers.append(layer)

            self.current_layer_index = project_data['current_layer_index']
            self.history.clear()
            self.redo_stack.clear()
            self.clear_selection()
            self.update_composite_image()

            return True
        except Exception as e:
            print(f"Ошибка загрузки проекта: {e}")
            return False

    def save_brush_preset(self, name):
        preset = {
            "name": name,
            "size": self.line_width,
            "hardness": self.brush_hardness,
            "shape": self.brush_shape
        }
        self.brush_presets.append(preset)

    def load_brush_preset(self, preset):
        self.line_width = preset["size"]
        self.brush_hardness = preset["hardness"]
        self.brush_shape = preset["shape"]

    def get_photo_image(self):
        scaled_width = int(self.canvas_width * self.scale_factor)
        scaled_height = int(self.canvas_height * self.scale_factor)
        if self.preview_image is not None:
            scaled = self.preview_image.resize((scaled_width, scaled_height), Image.LANCZOS)
        else:
            scaled = self.composite_image.resize((scaled_width, scaled_height), Image.LANCZOS)
        return ImageTk.PhotoImage(scaled)

    def get_temp_photo_image(self):
        if self.temp_image:
            composite = Image.alpha_composite(self.composite_rgba, self.temp_image)
            display_base = Image.new("RGB", (self.canvas_width, self.canvas_height), self.bg_color)
            display_base.paste(composite, (0, 0), composite)
            scaled_width = int(self.canvas_width * self.scale_factor)
            scaled_height = int(self.canvas_height * self.scale_factor)
            scaled = display_base.resize((scaled_width, scaled_height), Image.LANCZOS)
            return ImageTk.PhotoImage(scaled)
        return self.get_photo_image()

    def open_image(self, file_path):
        try:
            image = Image.open(file_path).convert("RGBA")
            self.canvas_width = image.width
            self.canvas_height = image.height
            self.layers = []
            layer = self.create_new_layer("Фон")
            layer.image = image
            layer.draw = ImageDraw.Draw(layer.image)
            layer.update_thumbnail()
            self.update_composite_image()
            return True
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            return False