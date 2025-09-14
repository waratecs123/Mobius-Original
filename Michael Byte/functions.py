# functions.py
import numpy as np
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import platform
import os

class TextEffectFunctions:
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple."""
        if not hex_color:
            return (0, 0, 0)
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (0, 0, 0)

    @staticmethod
    def create_gradient_image(size, start_hex, end_hex, direction='horizontal'):
        """Create a gradient image."""
        w, h = size
        start = TextEffectFunctions.hex_to_rgb(start_hex)
        end = TextEffectFunctions.hex_to_rgb(end_hex)
        grad = Image.new('RGB', (w, h))
        draw = ImageDraw.Draw(grad)
        if direction == 'horizontal':
            for x in range(w):
                ratio = x / max(w - 1, 1)
                r = int(start[0] + (end[0] - start[0]) * ratio)
                g = int(start[1] + (end[1] - start[1]) * ratio)
                b = int(start[2] + (end[2] - start[2]) * ratio)
                draw.line([(x, 0), (x, h)], fill=(r, g, b))
        elif direction == 'vertical':
            for y in range(h):
                ratio = y / max(h - 1, 1)
                r = int(start[0] + (end[0] - start[0]) * ratio)
                g = int(start[1] + (end[1] - start[1]) * ratio)
                b = int(start[2] + (end[2] - start[2]) * ratio)
                draw.line([(0, y), (w, y)], fill=(r, g, b))
        else:
            for y in range(h):
                for x in range(w):
                    ratio = (x + y) / (w + h - 2) if (w + h - 2) > 0 else 0
                    r = int(start[0] + (end[0] - start[0]) * ratio)
                    g = int(start[1] + (end[1] - start[1]) * ratio)
                    b = int(start[2] + (end[2] - start[2]) * ratio)
                    draw.point((x, y), fill=(r, g, b))
        return grad

    @staticmethod
    def apply_gradient_to_text(text_mask, gradient_img):
        """Apply gradient to text mask."""
        gradient_img = gradient_img.resize(text_mask.size, Image.LANCZOS)
        result = gradient_img.convert('RGBA')
        result.putalpha(text_mask)
        return result

    @staticmethod
    def create_text_mask(size, text, font, align='center', spacing=0, stroke_width=0, rotation=0, padding=20):
        """Create a text mask with rotation support."""
        w, h = size
        mask = Image.new('L', (w, h), 0)
        draw = ImageDraw.Draw(mask)
        lines = text.splitlines() or ['']
        try:
            total_h = 0
            bbox_lines = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line or ' ', font=font, stroke_width=stroke_width)
                bbox_lines.append(bbox)
                total_h += (bbox[3] - bbox[1]) + spacing
            total_h -= spacing
            y = (h - total_h) // 2
            for idx, line in enumerate(lines):
                bbox = bbox_lines[idx]
                lw = bbox[2] - bbox[0]
                if align == 'left':
                    x = padding
                elif align == 'right':
                    x = w - lw - padding
                else:
                    x = (w - lw) // 2
                draw.text((x, y), line, fill=255, font=font, stroke_width=stroke_width)
                y += (bbox[3] - bbox[1]) + spacing
        except Exception:
            draw.text((padding, h // 2), text, fill=255, font=font)

        if rotation != 0:
            mask = mask.rotate(rotation, resample=Image.BICUBIC, expand=1)
        return mask

    @staticmethod
    def create_noise_texture(size, intensity=0.2):
        """Create a noise texture."""
        w, h = size
        intensity = float(max(0.0, min(1.0, intensity)))
        noise = np.random.randint(0, 256, (h, w), dtype=np.uint8)
        img = Image.fromarray(noise, mode='L').convert('RGBA')
        alpha = int(255 * intensity)
        data = [(px[0], px[0], px[0], alpha) for px in img.getdata()]
        img.putdata(data)
        return img

    @staticmethod
    def apply_wave_distortion(img, amplitude=0, wavelength=30):
        """Apply wave distortion effect."""
        if amplitude == 0:
            return img
        arr = np.array(img)
        h, w = arr.shape[:2]
        output = np.zeros_like(arr)
        for y in range(h):
            shift = int(amplitude * math.sin(2 * math.pi * y / max(wavelength, 1)))
            sx = np.clip(np.arange(w) + shift, 0, w - 1)
            output[y, :] = arr[y, sx]
        return Image.fromarray(output)

    @staticmethod
    def apply_perspective_like(img, strength=0):
        """Apply a perspective-like distortion."""
        if strength == 0:
            return img
        w, h = img.size
        coeff = 1 + (strength / 100.0)
        new = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        for y in range(h):
            scale = 1 + (((y - h / 2) / (h / 2)) * (coeff - 1) * 0.5)
            row = img.crop((0, y, w, y + 1)).resize((max(1, int(w * scale)), 1), Image.LANCZOS)
            xoff = (w - row.size[0]) // 2
            new.paste(row, (xoff, y))
        return new

    @staticmethod
    def apply_bevel(img, intensity=5):
        """Apply a bevel effect."""
        if intensity == 0:
            return img
        embossed = img.filter(ImageFilter.EMBOSS)
        return Image.blend(img, embossed, intensity / 100.0)

    @staticmethod
    def apply_reflection(img, opacity=50, offset=10):
        """Apply a reflection effect."""
        w, h = img.size
        refl = img.transpose(Image.FLIP_TOP_BOTTOM)
        refl.putalpha(refl.split()[3].point(lambda p: int(p * (opacity / 100.0))))
        canvas = Image.new('RGBA', (w, h + offset + h // 2), (0, 0, 0, 0))
        canvas.paste(img, (0, 0))
        canvas.paste(refl, (0, h + offset))
        return canvas

    @staticmethod
    def apply_inner_glow(mask, color, intensity=10):
        """Apply inner glow effect."""
        glow_col = TextEffectFunctions.hex_to_rgb(color)
        gmask = mask.filter(ImageFilter.GaussianBlur(radius=max(1, intensity / 3)))
        glow_layer = Image.new('RGBA', mask.size, glow_col + (160,))
        glow_layer.putalpha(gmask)
        return glow_layer

    @staticmethod
    def apply_neon_effect(img, color, intensity=10):
        """Apply neon glow effect."""
        if intensity == 0:
            return img
        neon_col = TextEffectFunctions.hex_to_rgb(color)
        blur = img.filter(ImageFilter.GaussianBlur(radius=intensity / 2))
        neon_layer = Image.new('RGBA', img.size, neon_col + (200,))
        neon_layer.putalpha(blur.split()[3])
        return Image.alpha_composite(neon_layer, img)

    @staticmethod
    def apply_3d_effect(img, depth=10, angle=45):
        """Apply 3D extrusion effect."""
        if depth == 0:
            return img
        w, h = img.size
        result = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        dx = int(math.cos(math.radians(angle)) * depth)
        dy = int(math.sin(math.radians(angle)) * depth)
        for i in range(depth):
            offset_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            offset_img.paste(img, (dx * i // depth, dy * i // depth))
            result = Image.alpha_composite(result, offset_img)
        result = Image.alpha_composite(result, img)
        return result

    @staticmethod
    def calculate_text_bbox(text, font, spacing=0, stroke_width=0, rotation=0):
        """Calculate text bounding box, accounting for rotation."""
        dummy = Image.new('L', (1, 1))
        draw = ImageDraw.Draw(dummy)
        lines = text.splitlines() or ['']
        total_w, total_h = 0, 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line or ' ', font=font, stroke_width=stroke_width)
            total_w = max(total_w, bbox[2] - bbox[0])
            total_h += (bbox[3] - bbox[1]) + spacing
        total_h -= spacing
        if rotation != 0:
            rad = math.radians(abs(rotation))
            new_w = int(abs(total_w * math.cos(rad)) + abs(total_h * math.sin(rad)))
            new_h = int(abs(total_w * math.sin(rad)) + abs(total_h * math.cos(rad)))
            return new_w, new_h
        return total_w, total_h

def load_font_prefer(name_or_family, size):
    """Load a font with Cyrillic support, with fallbacks."""
    candidates = [name_or_family] if name_or_family else []
    candidates += ["DejaVuSans.ttf", "DejaVu Sans", "LiberationSans-Regular.ttf", "Arial.ttf", "Arial"]
    if platform.system() == "Windows":
        win_fonts = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
        candidates += [os.path.join(win_fonts, fname) for fname in ["DejaVuSans.ttf", "arial.ttf", "LiberationSans-Regular.ttf"]]
    if platform.system() == "Linux":
        candidates += ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                       "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                       "/usr/share/fonts/truetype/freefont/FreeSans.ttf"]
    for c in candidates:
        try:
            return ImageFont.truetype(c, int(size))
        except Exception:
            continue
    return ImageFont.load_default()