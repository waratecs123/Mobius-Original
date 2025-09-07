import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import math


class TextEffectFunctions:
    def __init__(self, controller):
        self.controller = controller

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def apply_gradient(self, draw, text, font, position, size):
        """Apply gradient to text"""
        x, y = position
        width, height = size

        # Create gradient image
        gradient = Image.new('RGB', (width, height), (0, 0, 0))
        grad_draw = ImageDraw.Draw(gradient)

        start_color = self.hex_to_rgb(self.controller.gradient_start)
        end_color = self.hex_to_rgb(self.controller.gradient_end)

        direction = self.controller.ui_vars['gradient_dir_var'].get()

        if direction == "horizontal":
            for i in range(width):
                r = start_color[0] + (end_color[0] - start_color[0]) * i // width
                g = start_color[1] + (end_color[1] - start_color[1]) * i // width
                b = start_color[2] + (end_color[2] - start_color[2]) * i // width
                grad_draw.line([(i, 0), (i, height)], fill=(r, g, b))
        elif direction == "vertical":
            for i in range(height):
                r = start_color[0] + (end_color[0] - start_color[0]) * i // height
                g = start_color[1] + (end_color[1] - start_color[1]) * i // height
                b = start_color[2] + (end_color[2] - start_color[2]) * i // height
                grad_draw.line([(0, i), (width, i)], fill=(r, g, b))
        else:  # diagonal
            for i in range(width):
                for j in range(height):
                    ratio = (i + j) / (width + height)
                    r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                    g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                    b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                    grad_draw.point((i, j), fill=(r, g, b))

        # Create text mask
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((0, 0), text, fill=255, font=font)

        # Apply gradient to text
        gradient.putalpha(mask)

        # Paste gradient onto main image
        draw.bitmap((x, y), gradient.convert('1'))

    def create_texture_overlay(self, width, height):
        """Create texture overlay effect"""
        intensity = self.controller.ui_vars['texture_var'].get() / 10.0

        # Create noise texture
        noise = np.random.randint(0, 255, (height, width), dtype=np.uint8)
        texture = Image.fromarray(noise, mode='L')

        # Convert to RGBA with opacity based on intensity
        texture_rgba = texture.convert('RGBA')
        alpha = int(255 * intensity)

        # Apply alpha channel
        data = [(r, g, b, alpha) for r, g, b, a in texture_rgba.getdata()]
        texture_rgba.putdata(data)

        return texture_rgba

    def apply_distortion(self, image):
        """Apply perspective and wave distortion"""
        perspective = self.controller.ui_vars['perspective_var'].get() / 10.0
        wave = self.controller.ui_vars['wave_var'].get() / 10.0

        if perspective == 0 and wave == 0:
            return image

        width, height = image.size

        # Convert to numpy array for processing
        if image.mode == 'RGBA':
            arr = np.array(image)
        else:
            arr = np.array(image.convert('RGBA'))

        # Create output array
        output = np.zeros_like(arr)

        for y in range(height):
            for x in range(width):
                # Apply perspective distortion
                px = x + int((y / height - 0.5) * perspective * 50)
                py = y + int((x / width - 0.5) * perspective * 50)

                # Apply wave distortion
                px += int(math.sin(y / 20.0) * wave * 10)
                py += int(math.cos(x / 20.0) * wave * 10)

                # Keep coordinates within bounds
                px = max(0, min(width - 1, px))
                py = max(0, min(height - 1, py))

                output[y, x] = arr[py, px]

        return Image.fromarray(output)