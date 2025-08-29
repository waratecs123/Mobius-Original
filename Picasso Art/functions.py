import math
import collections
from PIL import Image, ImageDraw, ImageTk, ImageColor
from tkinter import messagebox, filedialog


class Layer:
    def __init__(self, name, width, height, bg_color="transparent"):
        self.name = name
        self.visible = True
        self.opacity = 100
        self.image = Image.new("RGBA", (width, height), (0, 0, 0, 0) if bg_color == "transparent" else bg_color)
        self.draw = ImageDraw.Draw(self.image)

    def get_image_with_opacity(self):
        if self.opacity == 100:
            return self.image
        # Применяем прозрачность слоя
        opacity_img = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
        alpha = self.image.split()[3]
        alpha = alpha.point(lambda p: p * self.opacity / 100)
        opacity_img.putalpha(alpha)
        return Image.composite(self.image, opacity_img, self.image)


class PaintFunctions:
    def __init__(self):
        # Переменные для рисования
        self.draw_color = "black"
        self.alpha = 255
        self.bg_color = "white"
        self.line_width = 5
        self.current_tool = "карандаш"
        self.start_x, self.start_y = None, None
        self.last_x, self.last_y = None, None

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
        self.max_history = 20

        # Система слоев
        self.layers = []
        self.current_layer_index = 0
        self.create_new_layer("Слой 1", self.bg_color)

        # Создание composite изображения
        self.composite_image = Image.new("RGB", (self.canvas_width, self.canvas_height), self.bg_color)

    def create_new_layer(self, name, bg_color="transparent"):
        """Создает новый слой"""
        layer = Layer(name, self.canvas_width, self.canvas_height, bg_color)
        self.layers.append(layer)
        self.current_layer_index = len(self.layers) - 1
        self.update_composite_image()
        return layer

    def delete_current_layer(self):
        """Удаляет текущий слой"""
        if len(self.layers) > 1:
            del self.layers[self.current_layer_index]
            if self.current_layer_index >= len(self.layers):
                self.current_layer_index = len(self.layers) - 1
            self.update_composite_image()
            return True
        return False

    def toggle_layer_visibility(self, index):
        """Переключает видимость слоя"""
        if 0 <= index < len(self.layers):
            self.layers[index].visible = not self.layers[index].visible
            self.update_composite_image()

    def set_layer_opacity(self, index, opacity):
        """Устанавливает прозрачность слоя"""
        if 0 <= index < len(self.layers):
            self.layers[index].opacity = max(0, min(100, opacity))
            self.update_composite_image()

    def update_composite_image(self):
        """Обновляет composite изображение из всех видимых слоев"""
        # Создаем прозрачное изображение для композиции
        composite = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))

        # Накладываем все видимые слои
        for layer in self.layers:
            if layer.visible:
                layer_img = layer.get_image_with_opacity()
                composite = Image.alpha_composite(composite, layer_img)

        # Конвертируем в RGB для отображения
        self.composite_image = composite.convert("RGB")
        self.image = self.composite_image  # Для обратной совместимости

    def get_current_layer(self):
        """Возвращает текущий активный слой"""
        if self.layers:
            return self.layers[self.current_layer_index]
        return None

    def convert_canvas_coords(self, x, y):
        """Преобразует координаты холста с учетом масштаба"""
        if self.scale_factor != 1.0:
            return int(x / self.scale_factor), int(y / self.scale_factor)
        return x, y

    def get_color_with_alpha(self, base_color):
        """Возвращает цвет с учетом прозрачности"""
        try:
            if isinstance(base_color, str):
                rgb = ImageColor.getrgb(base_color)
            else:
                rgb = base_color
            return (*rgb, self.alpha)
        except:
            return (0, 0, 0, self.alpha)

    def draw_on_image(self, last_x, last_y, x, y, color):
        """Рисует на текущем слое с интерполяцией"""
        layer = self.get_current_layer()
        if not layer:
            return

        steps = max(2, int(math.sqrt((x - last_x) ** 2 + (y - last_y) ** 2) / 2))
        for i in range(steps):
            t = i / steps
            cx = last_x + t * (x - last_x)
            cy = last_y + t * (y - last_y)

            temp_img = Image.new("RGBA", (self.line_width * 2, self.line_width * 2))
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.ellipse([0, 0, self.line_width * 2 - 1, self.line_width * 2 - 1],
                              fill=self.get_color_with_alpha(color))

            layer.image.paste(temp_img,
                              (int(cx - self.line_width), int(cy - self.line_width)),
                              temp_img)

        self.update_composite_image()

    def draw_shape(self, start_x, start_y, end_x, end_y):
        """Рисует фигуру на текущем слое"""
        layer = self.get_current_layer()
        if not layer:
            return

        temp_img = Image.new("RGBA", (self.canvas_width, self.canvas_height))
        temp_draw = ImageDraw.Draw(temp_img)

        if self.current_tool == "линия":
            temp_draw.line([start_x, start_y, end_x, end_y],
                           fill=self.get_color_with_alpha(self.draw_color), width=self.line_width)
        elif self.current_tool == "прямоугольник":
            temp_draw.rectangle([start_x, start_y, end_x, end_y],
                                outline=self.get_color_with_alpha(self.draw_color), width=self.line_width)
        elif self.current_tool == "овал":
            temp_draw.ellipse([start_x, start_y, end_x, end_y],
                              outline=self.get_color_with_alpha(self.draw_color), width=self.line_width)

        layer.image.paste(temp_img, (0, 0), temp_img)
        layer.draw = ImageDraw.Draw(layer.image)
        self.update_composite_image()

    def flood_fill(self, x, y):
        """Заливка области на текущем слое"""
        layer = self.get_current_layer()
        if not layer:
            return

        target_color = layer.image.getpixel((x, y))
        fill_color = self.get_color_with_alpha(self.draw_color)

        if target_color == fill_color[:3]:
            return

        queue = collections.deque([(x, y)])
        visited = set([(x, y)])

        while queue:
            cx, cy = queue.popleft()

            if 0 <= cx < self.canvas_width and 0 <= cy < self.canvas_height:
                if layer.image.getpixel((cx, cy)) == target_color:
                    layer.image.putpixel((cx, cy), fill_color[:3])

                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        nx, ny = cx + dx, cy + dy
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny))

        layer.draw = ImageDraw.Draw(layer.image)
        self.update_composite_image()

    def add_text_to_image(self, x, y, text):
        """Добавляет текст на текущий слой"""
        layer = self.get_current_layer()
        if not layer:
            return

        temp_img = Image.new("RGBA", (self.canvas_width, self.canvas_height))
        temp_draw = ImageDraw.Draw(temp_img)
        text_color = self.get_color_with_alpha(self.draw_color)
        temp_draw.text((x, y), text, fill=text_color)
        layer.image.paste(temp_img, (0, 0), temp_img)
        layer.draw = ImageDraw.Draw(layer.image)
        self.update_composite_image()

    def save_state(self):
        """Сохраняет текущее состояние всех слоев для отмены"""
        layer_states = []
        for layer in self.layers:
            layer_states.append({
                'image': layer.image.copy(),
                'visible': layer.visible,
                'opacity': layer.opacity
            })

        self.history.append({
            'layers': layer_states,
            'current_index': self.current_layer_index
        })

        self.redo_stack.clear()
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def undo(self):
        if self.history:
            # Сохраняем текущее состояние для redo
            current_states = []
            for layer in self.layers:
                current_states.append({
                    'image': layer.image.copy(),
                    'visible': layer.visible,
                    'opacity': layer.opacity
                })

            self.redo_stack.append({
                'layers': current_states,
                'current_index': self.current_layer_index
            })

            if len(self.redo_stack) > self.max_history:
                self.redo_stack.pop(0)

            # Восстанавливаем предыдущее состояние
            previous_state = self.history.pop()
            for i, layer_state in enumerate(previous_state['layers']):
                if i < len(self.layers):
                    self.layers[i].image = layer_state['image']
                    self.layers[i].visible = layer_state['visible']
                    self.layers[i].opacity = layer_state['opacity']
                    self.layers[i].draw = ImageDraw.Draw(self.layers[i].image)

            self.current_layer_index = previous_state['current_index']
            self.update_composite_image()
            return True
        return False

    def redo(self):
        if self.redo_stack:
            # Сохраняем текущее состояние для истории
            current_states = []
            for layer in self.layers:
                current_states.append({
                    'image': layer.image.copy(),
                    'visible': layer.visible,
                    'opacity': layer.opacity
                })

            self.history.append({
                'layers': current_states,
                'current_index': self.current_layer_index
            })

            if len(self.history) > self.max_history:
                self.history.pop(0)

            # Восстанавливаем состояние из redo
            redo_state = self.redo_stack.pop()
            for i, layer_state in enumerate(redo_state['layers']):
                if i < len(self.layers):
                    self.layers[i].image = layer_state['image']
                    self.layers[i].visible = layer_state['visible']
                    self.layers[i].opacity = layer_state['opacity']
                    self.layers[i].draw = ImageDraw.Draw(self.layers[i].image)

            self.current_layer_index = redo_state['current_index']
            self.update_composite_image()
            return True
        return False

    def new_image(self):
        """Создает новое изображение со слоем по умолчанию"""
        self.layers = []
        self.current_layer_index = 0
        self.create_new_layer("Слой 1", self.bg_color)

    def clear_canvas(self):
        """Очищает текущий слой"""
        layer = self.get_current_layer()
        if layer:
            layer.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
            layer.draw = ImageDraw.Draw(layer.image)
            self.update_composite_image()

    def save_image(self, file_path):
        """Сохраняет composite изображение"""
        self.composite_image.save(file_path)

    def open_image(self, file_path):
        """Открывает изображение как новый слой"""
        img = Image.open(file_path).convert("RGBA")
        self.canvas_width, self.canvas_height = img.size

        # Создаем новый слой с открытым изображением
        self.create_new_layer("Импортированный слой", "transparent")
        self.get_current_layer().image = img
        self.get_current_layer().draw = ImageDraw.Draw(self.get_current_layer().image)
        self.update_composite_image()

    def get_photo_image(self, image):
        """Конвертирует PIL Image в PhotoImage"""
        return ImageTk.PhotoImage(image)