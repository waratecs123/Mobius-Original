import math
import collections
import numpy as np
from PIL import Image, ImageDraw, ImageTk, ImageColor, ImageFilter, ImageEnhance, ImageOps, ImageChops, ImageFont
from tkinter import messagebox, simpledialog
import random
import json
import os
import base64
from io import BytesIO
import colorsys

class Layer:
    def __init__(self, name, width, height, bg_color="transparent", is_adjustment=False, adjustment_type=None):
        self.name = name
        self.visible = True
        self.opacity = 100
        self.locked = False
        self.blend_mode = "normal"
        self.is_adjustment = is_adjustment
        self.adjustment_type = adjustment_type
        self.adjustment_params = {}
        self.image = Image.new("RGBA", (width, height), (0, 0, 0, 0) if bg_color == "transparent" else bg_color)
        self.draw = ImageDraw.Draw(self.image)
        self.thumbnail = None
        self.mask = None
        self.transform_mode = False  # For transform mode
        self.rotation = 0  # Rotation angle (90, 180, 270 degrees)
        self.scale = 1.0  # Scale factor
        self.position = (0, 0)  # Position offset
        self.update_thumbnail()

    def update_thumbnail(self):
        if self.image:
            thumb_size = (64, 64)
            self.thumbnail = self.image.copy().convert("RGBA")
            self.thumbnail.thumbnail(thumb_size, Image.LANCZOS)

    def get_image_with_opacity(self):
        if self.opacity == 100:
            return self.image.copy()
        result = self.image.copy()
        alpha = result.split()[3]
        alpha = alpha.point(lambda p: int(p * self.opacity / 100))
        result.putalpha(alpha)
        return result

    def apply_transform(self):
        if self.transform_mode:
            img = self.image.copy()
            # Apply rotation
            if self.rotation != 0:
                img = img.rotate(self.rotation, resample=Image.BICUBIC, expand=False)
            # Apply scale
            if self.scale != 1.0:
                new_size = (int(img.width * self.scale), int(img.height * self.scale))
                img = img.resize(new_size, Image.LANCZOS)
            # Apply position
            if self.position != (0, 0):
                new_img = Image.new("RGBA", (self.image.width, self.image.height), (0, 0, 0, 0))
                new_img.paste(img, self.position)
                img = new_img
            return img
        return self.image.copy()

    def apply_blend_mode(self, base, top):
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
        base_arr = np.array(base.convert("RGB")).astype(float)
        top_arr = np.array(top.convert("RGB")).astype(float)
        result_arr = np.clip(base_arr / (1 - top_arr / 255 + 1e-10), 0, 255)
        return Image.fromarray(result_arr.astype('uint8'), 'RGB').convert("RGBA")

    def blend_color_burn(self, base, top):
        base_arr = np.array(base.convert("RGB")).astype(float)
        top_arr = np.array(top.convert("RGB")).astype(float)
        result_arr = np.clip(1 - (1 - base_arr / 255) / (top_arr / 255 + 1e-10) * 255, 0, 255)
        return Image.fromarray(result_arr.astype('uint8'), 'RGB').convert("RGBA")

    def blend_soft_light(self, base, top):
        base_arr = np.array(base.convert("RGB")).astype(float) / 255
        top_arr = np.array(top.convert("RGB")).astype(float) / 255
        result_arr = np.where(top_arr <= 0.5,
                              2 * base_arr * top_arr + base_arr ** 2 * (1 - 2 * top_arr),
                              np.sqrt(base_arr) * (2 * top_arr - 1) + 2 * base_arr * (1 - top_arr))
        result_arr = np.clip(result_arr * 255, 0, 255)
        return Image.fromarray(result_arr.astype('uint8'), 'RGB').convert("RGBA")

    def blend_exclusion(self, base, top):
        base_arr = np.array(base.convert("RGB")).astype(float) / 255
        top_arr = np.array(top.convert("RGB")).astype(float) / 255
        result_arr = base_arr + top_arr - 2 * base_arr * top_arr
        result_arr = np.clip(result_arr * 255, 0, 255)
        return Image.fromarray(result_arr.astype('uint8'), 'RGB').convert("RGBA")

    def apply_adjustment(self, image):
        if not self.is_adjustment:
            return image
        img = image.convert("RGB")
        if self.adjustment_type == "brightness":
            enhancer = ImageEnhance.Brightness(img)
            return enhancer.enhance(self.adjustment_params.get("strength", 1.0)).convert("RGBA")
        elif self.adjustment_type == "contrast":
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(self.adjustment_params.get("strength", 1.0)).convert("RGBA")
        elif self.adjustment_type == "hue":
            hsv = np.array(img.convert("HSV")).astype(float)
            hsv[:, :, 0] = (hsv[:, :, 0] + self.adjustment_params.get("hue", 0)) % 360
            return Image.fromarray(hsv.astype('uint8'), 'HSV').convert("RGBA")
        elif self.adjustment_type == "saturation":
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(self.adjustment_params.get("strength", 1.0)).convert("RGBA")
        return image

class Selection:
    def __init__(self, width, height):
        self.mask = Image.new("L", (width, height), 0)
        self.active = False
        self.mode = "rectangle"
        self.points = []

class Path:
    def __init__(self, name):
        self.name = name
        self.points = []
        self.closed = False

class PaintFunctions:
    def __init__(self):
        self.draw_color = "#000000"
        self.alpha = 255
        self.bg_color = "#ffffff"
        self.line_width = 5
        self.current_tool = "pencil"
        self.brush_shape = "circle"
        self.brush_hardness = 100
        self.start_x, self.start_y = None, None
        self.last_x, self.last_y = None, None
        self.temp_image = None
        self.temp_draw = None
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.scale_factor = 1.0
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.canvas_width = 800
        self.canvas_height = 600
        self.color_mode = "RGB"
        self.cmyk_values = [0, 0, 0, 0]
        self.lab_values = [50, 0, 0]
        self.hsb_values = [0, 0, 100]
        self.history = []
        self.redo_stack = []
        self.actions = []
        self.current_action = None
        self.max_history = 50
        self.layers = []
        self.current_layer_index = 0
        self.selection = Selection(self.canvas_width, self.canvas_height)
        self.has_selection = False
        self.create_new_layer("Фон", self.bg_color)
        self.paths = []
        self.current_path = None
        self.composite_image = Image.new("RGB", (self.canvas_width, self.canvas_height), self.bg_color)
        self.composite_rgba = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        self.preview_image = None
        self.tk_image = None
        self.gradient_type = "linear"
        self.gradient_colors = ["#ff0000", "#0000ff"]
        self.gradient_direction = "horizontal"
        self.swatches = []
        self.brush_presets = [
            {"name": "Мягкая круглая", "size": 10, "hardness": 50, "shape": "circle"},
            {"name": "Жесткая круглая", "size": 15, "hardness": 100, "shape": "circle"},
            {"name": "Квадратная", "size": 8, "hardness": 100, "shape": "square"},
            {"name": "Текстурированная", "size": 20, "hardness": 30, "shape": "circle"},
            {"name": "Разброс", "size": 25, "hardness": 20, "shape": "scatter"}
        ]
        self.filter_presets = [
            {"name": "Мягкое размытие", "type": "blur", "strength": 2.0},
            {"name": "Резкость", "type": "sharpen", "strength": 1.5},
            {"name": "Сепия", "type": "sepia", "strength": 1.0},
            {"name": "Винтаж", "type": "sepia", "strength": 0.7},
            {"name": "Ч/Б", "type": "grayscale", "strength": 1.0},
            {"name": "Контрастный", "type": "contrast", "strength": 1.5},
            {"name": "Яркий", "type": "brightness", "strength": 1.3}
        ]
        try:
            self.font = ImageFont.truetype("arial.ttf", 16)
        except:
            self.font = ImageFont.load_default()

    def create_new_layer(self, name, bg_color="transparent"):
        layer = Layer(name, self.canvas_width, self.canvas_height, bg_color)
        self.layers.append(layer)
        self.current_layer_index = len(self.layers) - 1
        self.update_composite_image()
        self.save_state(action="Создание слоя")
        return layer

    def create_adjustment_layer(self, name, adjustment_type):
        layer = Layer(name, self.canvas_width, self.canvas_height, is_adjustment=True, adjustment_type=adjustment_type)
        layer.adjustment_params = {"strength": 1.0}
        if adjustment_type == "hue":
            layer.adjustment_params["hue"] = 0
        self.layers.append(layer)
        self.current_layer_index = len(self.layers) - 1
        self.update_composite_image()
        self.save_state(action="Создание корректирующего слоя")

    def duplicate_layer(self, index):
        if 0 <= index < len(self.layers):
            original = self.layers[index]
            new_layer = Layer(f"{original.name} копия", self.canvas_width, self.canvas_height, is_adjustment=original.is_adjustment, adjustment_type=original.adjustment_type)
            new_layer.image = original.image.copy()
            new_layer.draw = ImageDraw.Draw(new_layer.image)
            new_layer.visible = original.visible
            new_layer.opacity = original.opacity
            new_layer.blend_mode = original.blend_mode
            new_layer.locked = original.locked
            new_layer.adjustment_params = original.adjustment_params.copy()
            new_layer.rotation = original.rotation
            new_layer.scale = original.scale
            new_layer.position = original.position
            self.layers.insert(index + 1, new_layer)
            self.current_layer_index = index + 1
            self.update_composite_image()
            self.save_state(action="Дублирование слоя")

    def delete_layer(self, index):
        if 0 <= index < len(self.layers) and len(self.layers) > 1:
            del self.layers[index]
            if self.current_layer_index >= len(self.layers):
                self.current_layer_index = len(self.layers) - 1
            self.update_composite_image()
            self.save_state(action="Удаление слоя")

    def reorder_layer(self, index, new_index):
        if 0 <= index < len(self.layers) and 0 <= new_index < len(self.layers):
            layer = self.layers.pop(index)
            self.layers.insert(new_index, layer)
            self.current_layer_index = new_index
            self.update_composite_image()
            self.save_state(action="Перемещение слоя")

    def merge_layers(self, indices):
        if len(indices) < 2:
            return
        indices.sort()
        merged = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        for i in indices:
            if self.layers[i].visible:
                layer_img = self.layers[i].apply_transform()
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
        self.save_state(action="Объединение слоев")

    def toggle_layer_visibility(self, index):
        if 0 <= index < len(self.layers):
            self.layers[index].visible = not self.layers[index].visible
            self.update_composite_image()
            self.save_state(action="Переключение видимости слоя")

    def set_layer_opacity(self, index, opacity):
        if 0 <= index < len(self.layers):
            self.layers[index].opacity = max(0, min(100, opacity))
            self.update_composite_image()
            self.save_state(action="Изменение прозрачности слоя")

    def set_layer_blend_mode(self, index, blend_mode):
        if 0 <= index < len(self.layers):
            self.layers[index].blend_mode = blend_mode
            self.update_composite_image()
            self.save_state(action="Изменение режима наложения")

    def toggle_transform_mode(self, index):
        if 0 <= index < len(self.layers):
            self.layers[index].transform_mode = not self.layers[index].transform_mode
            self.update_composite_image()
            self.save_state(action="Переключение режима трансформации")

    def get_display_image(self, temp_layer_image=None):
        composite = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
        for i, layer in enumerate(self.layers):
            if layer.visible and layer.opacity > 0:
                layer_img = layer.apply_transform() if layer.transform_mode else layer.get_image_with_opacity()
                if temp_layer_image is not None and i == self.current_layer_index and not layer.is_adjustment:
                    layer_img = temp_layer_image.convert("RGBA")
                    alpha = layer_img.split()[3].point(lambda p: int(p * layer.opacity / 100))
                    layer_img.putalpha(alpha)
                if layer.is_adjustment:
                    layer_img = layer.apply_adjustment(composite)
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
                layer_img = layer.apply_transform() if layer.transform_mode else layer.get_image_with_opacity()
                if layer.is_adjustment:
                    layer_img = layer.apply_adjustment(composite)
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
            if self.color_mode == "CMYK":
                rgb = self.cmyk_to_rgb(self.cmyk_values)
            elif self.color_mode == "LAB":
                rgb = self.lab_to_rgb(self.lab_values)
            elif self.color_mode == "HSB":
                rgb = self.hsb_to_rgb(self.hsb_values)
            return (*rgb[:3], self.alpha)
        except:
            return (0, 0, 0, self.alpha)

    def cmyk_to_rgb(self, cmyk):
        c, m, y, k = [x / 100 for x in cmyk]
        r = 255 * (1 - c) * (1 - k)
        g = 255 * (1 - m) * (1 - k)
        b = 255 * (1 - y) * (1 - k)
        return (int(r), int(g), int(b))

    def rgb_to_cmyk(self, rgb):
        r, g, b = [x / 255.0 for x in rgb]
        k = 1 - max(r, g, b)
        if k == 1:
            c = m = y = 0
        else:
            c = (1 - r - k) / (1 - k)
            m = (1 - g - k) / (1 - k)
            y = (1 - b - k) / (1 - k)
        return [c * 100, m * 100, y * 100, k * 100]

    def lab_to_rgb(self, lab):
        from skimage.color import lab2rgb
        l, a, b = lab
        lab_array = np.array([[[l, a, b]]], dtype=float)
        lab_array[0, 0, 0] /= 100.0
        lab_array[0, 0, 1:] /= 128.0
        rgb_array = lab2rgb(lab_array) * 255
        return tuple(int(x) for x in rgb_array[0, 0])

    def rgb_to_lab(self, rgb):
        from skimage.color import rgb2lab
        r, g, b = [x / 255.0 for x in rgb]
        rgb_array = np.array([[[r, g, b]]])
        lab_array = rgb2lab(rgb_array)
        return [lab_array[0, 0, 0], lab_array[0, 0, 1], lab_array[0, 0, 2]]

    def hsb_to_rgb(self, hsb):
        h, s, b = [x / 100 for x in hsb]
        rgb = colorsys.hsv_to_rgb(h / 360.0, s, b)
        return tuple(int(x * 255) for x in rgb)

    def rgb_to_hsb(self, rgb):
        r, g, b = [x / 255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return [h * 360, s * 100, v * 100]

    def set_color_mode(self, mode):
        self.color_mode = mode
        if isinstance(self.draw_color, str):
            rgb = ImageColor.getrgb(self.draw_color)
            if mode == "CMYK":
                self.cmyk_values = self.rgb_to_cmyk(rgb)
            elif mode == "LAB":
                self.lab_values = self.rgb_to_lab(rgb)
            elif mode == "HSB":
                self.hsb_values = self.rgb_to_hsb(rgb)

    def apply_filter_preview(self, filter_type, strength, image):
        if filter_type == "blur":
            return image.filter(ImageFilter.GaussianBlur(radius=strength))
        elif filter_type == "sharpen":
            return image.filter(ImageFilter.UnsharpMask(radius=2, percent=int(strength * 100), threshold=3)).convert("RGBA")
        elif filter_type == "brightness":
            enhancer = ImageEnhance.Brightness(image.convert("RGB"))
            return enhancer.enhance(strength).convert("RGBA")
        elif filter_type == "contrast":
            enhancer = ImageEnhance.Contrast(image.convert("RGB"))
            return enhancer.enhance(strength).convert("RGBA")
        elif filter_type == "saturation":
            enhancer = ImageEnhance.Color(image.convert("RGB"))
            return enhancer.enhance(strength).convert("RGBA")
        elif filter_type == "grayscale":
            return ImageOps.grayscale(image).convert("RGBA")
        elif filter_type == "invert":
            return ImageOps.invert(image.convert("RGB")).convert("RGBA")
        elif filter_type == "emboss":
            return image.filter(ImageFilter.EMBOSS).convert("RGBA")
        elif filter_type == "find_edges":
            return image.filter(ImageFilter.FIND_EDGES).convert("RGBA")
        elif filter_type == "posterize":
            return ImageOps.posterize(image.convert("RGB"), bits=int(8 - strength * 4)).convert("RGBA")
        elif filter_type == "solarize":
            return ImageOps.solarize(image.convert("RGB"), threshold=int(256 - strength * 50)).convert("RGBA")
        elif filter_type == "sepia":
            img = ImageOps.grayscale(image).convert("RGB")
            sepia_matrix = (
                0.393 + 0.607 * (1 - strength), 0.769 - 0.769 * (1 - strength), 0.189 - 0.189 * (1 - strength),
                0.349 - 0.349 * (1 - strength), 0.686 + 0.314 * (1 - strength), 0.168 - 0.168 * (1 - strength),
                0.272 - 0.272 * (1 - strength), 0.534 - 0.534 * (1 - strength), 0.131 + 0.869 * (1 - strength)
            )
            return img.convert("RGB", sepia_matrix).convert("RGBA")
        return image

    def apply_filter(self, filter_type, strength):
        layer = self.get_current_layer()
        if not layer or layer.locked or layer.is_adjustment:
            return
        if self.has_selection:
            mask = self.selection.mask
            filtered = self.apply_filter_preview(filter_type, strength, layer.image)
            temp = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
            temp.paste(filtered, (0, 0), mask)
            layer.image = Image.alpha_composite(layer.image, temp)
        else:
            layer.image = self.apply_filter_preview(filter_type, strength, layer.image)
        layer.draw = ImageDraw.Draw(layer.image)
        layer.update_thumbnail()
        self.update_composite_image()
        self.save_state(action=f"Фильтр: {filter_type}")

    def apply_filter_preset(self, preset):
        layer = self.get_current_layer()
        if not layer or layer.locked or layer.is_adjustment:
            return
        filter_type = preset["type"]
        strength = preset["strength"]
        if self.has_selection:
            mask = self.selection.mask
            filtered = self.apply_filter_preview(filter_type, strength, layer.image)
            temp = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
            temp.paste(filtered, (0, 0), mask)
            layer.image = Image.alpha_composite(layer.image, temp)
        else:
            layer.image = self.apply_filter_preview(filter_type, strength, layer.image)
        layer.draw = ImageDraw.Draw(layer.image)
        layer.update_thumbnail()
        self.update_composite_image()
        self.save_state(action=f"Пресет фильтра: {preset['name']}")

    def new_image(self, width, height, bg_color):
        self.canvas_width = width
        self.canvas_height = height
        self.bg_color = bg_color
        self.layers = []
        self.current_layer_index = 0
        self.selection = Selection(width, height)
        self.has_selection = False
        self.create_new_layer("Фон", bg_color)
        self.paths = []
        self.current_path = None
        self.composite_image = Image.new("RGB", (width, height), bg_color)
        self.composite_rgba = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        self.save_state(action="Создание нового изображения")

    def open_image(self, file_path):
        try:
            img = Image.open(file_path).convert("RGBA")
            self.canvas_width, self.canvas_height = img.size
            self.bg_color = "#ffffff"
            self.layers = []
            self.current_layer_index = 0
            layer = Layer("Фон", self.canvas_width, self.canvas_height, bg_color=(0, 0, 0, 0))
            layer.image = img
            layer.draw = ImageDraw.Draw(layer.image)
            layer.update_thumbnail()
            self.layers.append(layer)
            self.selection = Selection(self.canvas_width, self.canvas_height)
            self.has_selection = False
            self.paths = []
            self.current_path = None
            self.update_composite_image()
            self.save_state(action="Открытие изображения")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть изображение: {str(e)}")
            return False

    def save_image(self, file_path, width=None, height=None, rotation=0):
        try:
            img = self.composite_image.copy()
            if rotation != 0:
                img = img.rotate(rotation, resample=Image.BICUBIC, expand=False)
            if width and height:
                img = img.resize((width, height), Image.LANCZOS)
            img.save(file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {str(e)}")

    def save_project(self, file_path):
        project = {
            "width": self.canvas_width,
            "height": self.canvas_height,
            "bg_color": self.bg_color,
            "layers": [],
            "current_layer_index": self.current_layer_index,
            "swatches": self.swatches,
            "brush_presets": self.brush_presets,
            "filter_presets": self.filter_presets,
            "actions": self.actions
        }
        for layer in self.layers:
            layer_data = {
                "name": layer.name,
                "visible": layer.visible,
                "opacity": layer.opacity,
                "locked": layer.locked,
                "blend_mode": layer.blend_mode,
                "is_adjustment": layer.is_adjustment,
                "adjustment_type": layer.adjustment_type,
                "adjustment_params": layer.adjustment_params,
                "image": None,
                "rotation": layer.rotation,
                "scale": layer.scale,
                "position": layer.position
            }
            if not layer.is_adjustment:
                buffered = BytesIO()
                layer.image.save(buffered, format="PNG")
                layer_data["image"] = base64.b64encode(buffered.getvalue()).decode('utf-8')
            project["layers"].append(layer_data)
        with open(file_path, 'w') as f:
            json.dump(project, f, indent=2)

    def load_project(self, file_path):
        try:
            with open(file_path, 'r') as f:
                project = json.load(f)
            self.canvas_width = project["width"]
            self.canvas_height = project["height"]
            self.bg_color = project["bg_color"]
            self.current_layer_index = project["current_layer_index"]
            self.swatches = project.get("swatches", [])
            self.brush_presets = project.get("brush_presets", self.brush_presets)
            self.filter_presets = project.get("filter_presets", self.filter_presets)
            self.actions = project.get("actions", [])
            self.layers = []
            for layer_data in project["layers"]:
                layer = Layer(
                    name=layer_data["name"],
                    width=self.canvas_width,
                    height=self.canvas_height,
                    is_adjustment=layer_data["is_adjustment"],
                    adjustment_type=layer_data["adjustment_type"]
                )
                layer.visible = layer_data["visible"]
                layer.opacity = layer_data["opacity"]
                layer.locked = layer_data["locked"]
                layer.blend_mode = layer_data["blend_mode"]
                layer.adjustment_params = layer_data.get("adjustment_params", {})
                layer.rotation = layer_data.get("rotation", 0)
                layer.scale = layer_data.get("scale", 1.0)
                layer.position = layer_data.get("position", (0, 0))
                if layer_data["image"]:
                    img_data = base64.b64decode(layer_data["image"])
                    layer.image = Image.open(BytesIO(img_data)).convert("RGBA")
                    layer.draw = ImageDraw.Draw(layer.image)
                layer.update_thumbnail()
                self.layers.append(layer)
            self.selection = Selection(self.canvas_width, self.canvas_height)
            self.has_selection = False
            self.paths = []
            self.current_path = None
            self.update_composite_image()
            self.save_state(action="Загрузка проекта")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить проект: {str(e)}")
            return False

    def apply_drawing(self):
        layer = self.get_current_layer()
        if layer and not layer.locked and not layer.is_adjustment:
            if self.current_tool == "eraser":
                # Ensure eraser works on photos by using transparent color
                color = (0, 0, 0, 0)
            else:
                color = self.get_color_with_alpha(self.draw_color)
            if self.temp_image:
                layer.image = self.temp_image.copy()
                layer.draw = ImageDraw.Draw(layer.image)
                self.temp_image = None
                self.temp_draw = None
                layer.update_thumbnail()
                self.update_composite_image()
                self.save_state(action="Рисование")

    def start_drawing(self, x, y):
        layer = self.get_current_layer()
        if layer and not layer.locked and not layer.is_adjustment:
            self.temp_image = layer.image.copy()
            self.temp_draw = ImageDraw.Draw(self.temp_image)
            self.last_x, self.last_y = x, y

    def draw_on_image(self, last_x, last_y, x, y):
        layer = self.get_current_layer()
        if layer and not layer.locked and not layer.is_adjustment and self.temp_draw:
            color = (0, 0, 0, 0) if self.current_tool == "eraser" else self.get_color_with_alpha(self.draw_color)
            if self.brush_shape == "circle":
                self.temp_draw.line((last_x, last_y, x, y), fill=color, width=self.line_width)
            elif self.brush_shape == "square":
                dx = (x - last_x) / 2
                dy = (y - last_y) / 2
                points = [(last_x - dx, last_y - dy), (last_x + dx, last_y + dy),
                          (x + dx, y + dy), (x - dx, y - dy)]
                self.temp_draw.polygon(points, fill=color)
            self.update_composite_image()

    def draw_shape_final(self, start_x, start_y, end_x, end_y):
        layer = self.get_current_layer()
        if layer and not layer.locked and not layer.is_adjustment:
            color = self.get_color_with_alpha(self.draw_color)
            self.temp_image = layer.image.copy()
            self.temp_draw = ImageDraw.Draw(self.temp_image)
            if self.current_tool == "line":
                self.temp_draw.line((start_x, start_y, end_x, end_y), fill=color, width=self.line_width)
            elif self.current_tool == "rectangle":
                self.temp_draw.rectangle((start_x, start_y, end_x, end_y), outline=color, width=self.line_width)
            elif self.current_tool == "filled_rectangle":
                self.temp_draw.rectangle((start_x, start_y, end_x, end_y), fill=color)
            elif self.current_tool == "ellipse":
                self.temp_draw.ellipse((start_x, start_y, end_x, end_y), outline=color, width=self.line_width)
            elif self.current_tool == "filled_ellipse":
                self.temp_draw.ellipse((start_x, start_y, end_x, end_y), fill=color)
            elif self.current_tool in ["polygon", "filled_polygon"]:
                points = self.selection.points if self.selection.points else [(start_x, start_y), (end_x, end_y)]
                if self.current_tool == "polygon":
                    self.temp_draw.polygon(points, outline=color, width=self.line_width)
                else:
                    self.temp_draw.polygon(points, fill=color)
            layer.image = self.temp_image.copy()
            layer.draw = ImageDraw.Draw(layer.image)
            self.temp_image = None
            self.temp_draw = None
            layer.update_thumbnail()
            self.update_composite_image()
            self.save_state(action=f"Рисование фигуры: {self.current_tool}")

    def create_gradient(self, start_x, start_y, end_x, end_y):
        layer = self.get_current_layer()
        if layer and not layer.locked and not layer.is_adjustment:
            self.temp_image = layer.image.copy()
            self.temp_draw = ImageDraw.Draw(self.temp_image)
            start_color = ImageColor.getrgb(self.gradient_colors[0])
            end_color = ImageColor.getrgb(self.gradient_colors[1])
            width, height = self.canvas_width, self.canvas_height
            gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(gradient)
            if self.gradient_type == "linear":
                for i in range(width if self.gradient_direction == "horizontal" else height):
                    ratio = i / (width if self.gradient_direction == "horizontal" else height)
                    r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                    g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                    b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                    if self.gradient_direction == "horizontal":
                        draw.line((i, 0, i, height), fill=(r, g, b, self.alpha))
                    else:
                        draw.line((0, i, width, i), fill=(r, g, b, self.alpha))
            layer.image = Image.alpha_composite(self.temp_image, gradient)
            layer.draw = ImageDraw.Draw(layer.image)
            self.temp_image = None
            self.temp_draw = None
            layer.update_thumbnail()
            self.update_composite_image()
            self.save_state(action="Создание градиента")

    def flood_fill(self, x, y):
        layer = self.get_current_layer()
        if layer and not layer.locked and not layer.is_adjustment:
            color = self.get_color_with_alpha(self.draw_color)
            ImageDraw.floodfill(layer.image, (int(x), int(y)), color)
            layer.draw = ImageDraw.Draw(layer.image)
            layer.update_thumbnail()
            self.update_composite_image()
            self.save_state(action="Заливка")

    def add_text_to_image(self, x, y, text):
        layer = self.get_current_layer()
        if layer and not layer.locked and not layer.is_adjustment:
            color = self.get_color_with_alpha(self.draw_color)
            layer.draw.text((x, y), text, font=self.font, fill=color)
            layer.update_thumbnail()
            self.update_composite_image()
            self.save_state(action="Добавление текста")

    def create_selection(self, mode, points):
        self.selection.mode = mode
        self.selection.points = points
        self.selection.mask = Image.new("L", (self.canvas_width, self.canvas_height), 0)
        draw = ImageDraw.Draw(self.selection.mask)
        if mode == "rectangle" and len(points) >= 2:
            draw.rectangle((points[0], points[-1]), fill=255)
        elif mode == "polygon":
            draw.polygon(points, fill=255)
        elif mode == "lasso":
            draw.polygon(points, fill=255)
        elif mode == "magic_wand" and points:
            x, y = points[0]
            ImageDraw.floodfill(self.selection.mask, (int(x), int(y)), 255)
        self.has_selection = bool(self.selection.mask.getbbox())
        self.update_composite_image()

    def start_tool_action(self, tool, x, y):
        if tool == "move" and self.has_selection:
            self.selection_start = (x, y)

    def update_tool_action(self, tool, x, y):
        if tool == "move" and self.has_selection and self.selection_start:
            dx = x - self.selection_start[0]
            dy = y - self.selection_start[1]
            self.get_current_layer().position = (dx, dy)
            self.update_composite_image()

    def end_tool_action(self, tool, x, y):
        if tool == "move":
            self.selection_start = None
            self.save_state(action="Перемещение")

    def rotate_layer(self, index, angle):
        if 0 <= index < len(self.layers):
            layer = self.layers[index]
            layer.rotation = (layer.rotation + angle) % 360
            self.update_composite_image()
            self.save_state(action=f"Поворот слоя на {angle} градусов")

    def scale_layer(self, index, scale):
        if 0 <= index < len(self.layers):
            layer = self.layers[index]
            layer.scale = max(0.1, min(5.0, scale))
            self.update_composite_image()
            self.save_state(action="Масштабирование слоя")

    def move_layer(self, index, dx, dy):
        if 0 <= index < len(self.layers):
            layer = self.layers[index]
            layer.position = (layer.position[0] + dx, layer.position[1] + dy)
            self.update_composite_image()
            self.save_state(action="Перемещение слоя")

    def add_swatch(self, color):
        self.swatches.append(color)
        self.save_state(action="Добавление сюжета")

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

    def start_action_recording(self, name):
        self.current_action = {"name": name, "steps": []}

    def play_action(self, index):
        if 0 <= index < len(self.actions):
            action = self.actions[index]
            for step in action["steps"]:
                if step["type"] == "draw":
                    self.current_tool = step["tool"]
                    self.draw_color = step["color"]
                    self.line_width = step["size"]
                    self.brush_shape = step["shape"]
                    self.brush_hardness = step["hardness"]
                    self.alpha = step["alpha"]
                    self.draw_on_image(step["last_x"], step["last_y"], step["x"], step["y"])
                elif step["type"] == "shape":
                    self.current_tool = step["tool"]
                    self.draw_color = step["color"]
                    self.line_width = step["size"]
                    self.alpha = step["alpha"]
                    self.draw_shape_final(step["start_x"], step["start_y"], step["end_x"], step["end_y"])
                elif step["type"] == "filter":
                    self.apply_filter(step["filter_type"], step["strength"])
                elif step["type"] == "layer":
                    if step["action"] == "create":
                        self.create_new_layer(step["name"], step["bg_color"])
                    elif step["action"] == "delete":
                        self.delete_layer(step["index"])
                    elif step["action"] == "opacity":
                        self.set_layer_opacity(step["index"], step["opacity"])
                    elif step["action"] == "blend":
                        self.set_layer_blend_mode(step["index"], step["blend_mode"])
            self.save_state(action=f"Воспроизведение действия: {action['name']}")

    def save_state(self, action="Изменение"):
        if self.current_action:
            self.current_action["steps"].append({
                "type": "draw" if self.current_tool in ["pencil", "brush", "eraser"] else
                        "shape" if self.current_tool in ["line", "rectangle", "filled_rectangle", "ellipse", "filled_ellipse", "polygon", "filled_polygon"] else
                        "filter" if self.current_tool == "filter" else "layer",
                "tool": self.current_tool,
                "color": self.draw_color,
                "size": self.line_width,
                "shape": self.brush_shape,
                "hardness": self.brush_hardness,
                "alpha": self.alpha,
                "last_x": self.last_x,
                "last_y": self.last_y,
                "x": self.last_x,
                "y": self.last_y,
                "start_x": self.start_x,
                "start_y": self.start_y,
                "end_x": self.last_x,
                "end_y": self.last_y,
                "filter_type": getattr(self, "filter_type", "none"),
                "strength": getattr(self, "filter_strength", 1.0),
                "action": action,
                "index": self.current_layer_index,
                "name": action,
                "bg_color": self.bg_color,
                "opacity": self.get_current_layer().opacity if self.get_current_layer() else 100,
                "blend_mode": self.get_current_layer().blend_mode if self.get_current_layer() else "normal"
            })
        state = {
            "action": action,
            "layers": [
                {
                    "name": layer.name,
                    "visible": layer.visible,
                    "opacity": layer.opacity,
                    "locked": layer.locked,
                    "blend_mode": layer.blend_mode,
                    "is_adjustment": layer.is_adjustment,
                    "adjustment_type": layer.adjustment_type,
                    "adjustment_params": layer.adjustment_params,
                    "image": layer.image.copy() if not layer.is_adjustment else None,
                    "rotation": layer.rotation,
                    "scale": layer.scale,
                    "position": layer.position
                } for layer in self.layers
            ],
            "current_layer_index": self.current_layer_index,
            "selection": {
                "mask": self.selection.mask.copy(),
                "points": self.selection.points[:],
                "mode": self.selection.mode
            }
        }
        self.history.append(state)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        self.redo_stack = []

    def undo(self):
        if self.history:
            self.redo_stack.append(self.get_current_state())
            state = self.history.pop()
            self.restore_state_from_data(state)
            return True
        return False

    def redo(self):
        if self.redo_stack:
            self.history.append(self.get_current_state())
            state = self.redo_stack.pop()
            self.restore_state_from_data(state)
            return True
        return False

    def restore_state_from_data(self, state):
        self.layers = []
        for layer_data in state["layers"]:
            layer = Layer(
                name=layer_data["name"],
                width=self.canvas_width,
                height=self.canvas_height,
                is_adjustment=layer_data["is_adjustment"],
                adjustment_type=layer_data["adjustment_type"]
            )
            layer.visible = layer_data["visible"]
            layer.opacity = layer_data["opacity"]
            layer.locked = layer_data["locked"]
            layer.blend_mode = layer_data["blend_mode"]
            layer.adjustment_params = layer_data.get("adjustment_params", {})
            layer.rotation = layer_data.get("rotation", 0)
            layer.scale = layer_data.get("scale", 1.0)
            layer.position = layer_data.get("position", (0, 0))
            if layer_data["image"]:
                layer.image = layer_data["image"].copy()
                layer.draw = ImageDraw.Draw(layer.image)
            layer.update_thumbnail()
            self.layers.append(layer)
        self.current_layer_index = state["current_layer_index"]
        self.selection.mask = state["selection"]["mask"].copy()
        self.selection.points = state["selection"]["points"][:]
        self.selection.mode = state["selection"]["mode"]
        self.has_selection = bool(self.selection.points or self.selection.mask.getbbox())
        self.update_composite_image()

    def get_current_state(self):
        return {
            "action": "Текущее состояние",
            "layers": [
                {
                    "name": layer.name,
                    "visible": layer.visible,
                    "opacity": layer.opacity,
                    "locked": layer.locked,
                    "blend_mode": layer.blend_mode,
                    "is_adjustment": layer.is_adjustment,
                    "adjustment_type": layer.adjustment_type,
                    "adjustment_params": layer.adjustment_params,
                    "image": layer.image.copy() if not layer.is_adjustment else None,
                    "rotation": layer.rotation,
                    "scale": layer.scale,
                    "position": layer.position
                } for layer in self.layers
            ],
            "current_layer_index": self.current_layer_index,
            "selection": {
                "mask": self.selection.mask.copy(),
                "points": self.selection.points[:],
                "mode": self.selection.mode
            }
        }

    def rotate_canvas(self, angle):
        for layer in self.layers:
            if not layer.locked and not layer.is_adjustment:
                layer.rotation = (layer.rotation + angle) % 360
                layer.update_thumbnail()
        self.selection.mask = self.selection.mask.rotate(angle, resample=Image.BICUBIC, expand=False)
        self.update_composite_image()
        self.save_state(action=f"Поворот холста на {angle} градусов")

    def get_photo_image(self):
        display_image = self.preview_image if self.preview_image else self.composite_image
        resized = display_image.resize((int(self.canvas_width * self.scale_factor), int(self.canvas_height * self.scale_factor)), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized)
        return self.tk_image

    def get_temp_photo_image(self):
        temp_image = self.get_display_image(self.temp_image)
        resized = temp_image.resize((int(self.canvas_width * self.scale_factor), int(self.canvas_height * self.scale_factor)), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized)
        return self.tk_image