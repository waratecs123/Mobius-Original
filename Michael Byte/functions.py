import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import math


class TextEffectFunctions:
    def __init__(self, controller):
        self.controller = controller

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def apply_gradient(self, draw, text, font, position, size):
        x, y = position
        width, height = size

        if self.controller.gradient_start == self.controller.gradient_end:
            return

        start_color = self.hex_to_rgb(self.controller.gradient_start)
        end_color = self.hex_to_rgb(self.controller.gradient_end)

        direction = self.controller.gradient_direction

        if direction == "horizontal":
            for i in range(width):
                ratio = i / width
                r = int(start_color[0] + ratio * (end_color[0] - start_color[0]))
                g = int(start_color[1] + ratio * (end_color[1] - start_color[1]))
                b = int(start_color[2] + ratio * (end_color[2] - start_color[2]))
                color = (r, g, b)

                # Draw vertical slice of text
                mask = Image.new('L', (1, height), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.text((-x - i, -y), text, fill=255, font=font)

                # Apply color to this slice
                slice_img = Image.new('RGB', (1, height), color)
                draw.bitmap((x + i, y), mask, fill=color)

        elif direction == "vertical":
            for i in range(height):
                ratio = i / height
                r = int(start_color[0] + ratio * (end_color[0] - start_color[0]))
                g = int(start_color[1] + ratio * (end_color[1] - start_color[1]))
                b = int(start_color[2] + ratio * (end_color[2] - start_color[2]))
                color = (r, g, b)

                # Draw horizontal slice of text
                mask = Image.new('L', (width, 1), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.text((-x, -y - i), text, fill=255, font=font)

                # Apply color to this slice
                draw.bitmap((x, y + i), mask, fill=color)

        else:  # diagonal
            for i in range(width):
                for j in range(height):
                    ratio = (i + j) / (width + height)
                    r = int(start_color[0] + ratio * (end_color[0] - start_color[0]))
                    g = int(start_color[1] + ratio * (end_color[1] - start_color[1]))
                    b = int(start_color[2] + ratio * (end_color[2] - start_color[2]))
                    color = (r, g, b)

                    # Check if this pixel is part of the text
                    mask = Image.new('L', (1, 1), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.text((-x - i, -y - j), text, fill=255, font=font)

                    if mask.getpixel((0, 0)) > 0:
                        draw.point((x + i, y + j), fill=color)

    def apply_distortion(self, image):
        # Get distortion parameters
        perspective = self.controller.ui_vars['perspective_var'].get() / 100.0
        wave = self.controller.ui_vars['wave_var'].get()

        if perspective == 0 and wave == 0:
            return image

        width, height = image.size
        pixels = image.load()

        # Create new image
        new_image = Image.new(image.mode, (width, height), (0, 0, 0, 0))
        new_pixels = new_image.load()

        # Apply perspective distortion
        if perspective > 0:
            for y in range(height):
                for x in range(width):
                    # Simple perspective effect
                    new_x = int(x + perspective * (x - width / 2) * (y / height))
                    new_y = y

                    if 0 <= new_x < width and 0 <= new_y < height:
                        new_pixels[x, y] = pixels[new_x, new_y]

            pixels = new_pixels

        # Apply wave distortion
        if wave > 0:
            for y in range(height):
                wave_offset = int(wave * math.sin(2 * math.pi * y / 50))
                for x in range(width):
                    new_x = (x + wave_offset) % width
                    new_pixels[x, y] = pixels[new_x, y]

        return new_image

    def create_texture_overlay(self, width, height):
        texture = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(texture)

        intensity = self.controller.ui_vars['texture_var'].get()

        if intensity > 0:
            for i in range(intensity * 100):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                size = np.random.randint(1, intensity + 1)
                alpha = np.random.randint(50, 150)
                draw.ellipse([x, y, x + size, y + size], fill=(255, 255, 255, alpha))

        return texture