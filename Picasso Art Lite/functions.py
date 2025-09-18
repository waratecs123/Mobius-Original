from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageChops, ImageDraw
import colorsys, random, math, io
import numpy as np
import cv2

def clamp(v, a=0, b=255):
    return max(a, min(b, int(v)))

def apply_basic_enhancements(img, params):
    if params.get('brightness', 0):
        img = ImageEnhance.Brightness(img).enhance(1 + params['brightness'] / 100.0)
    if params.get('contrast', 0):
        img = ImageEnhance.Contrast(img).enhance(1 + params['contrast'] / 100.0)
    if params.get('saturation', 0):
        img = ImageEnhance.Color(img).enhance(1 + params['saturation'] / 100.0)
    if params.get('clarity', 0):
        img = ImageEnhance.Sharpness(img).enhance(1 + params['clarity'] / 100.0)
    if params.get('exposure', 0):
        e = params['exposure'] / 100.0
        img = ImageEnhance.Brightness(img).enhance(1 + e)
        img = ImageEnhance.Contrast(img).enhance(1 + e)
    return img

def apply_sepia(img, amount=100):
    if amount <= 0:
        return img
    sepia = ImageOps.colorize(ImageOps.grayscale(img), '#704214', '#C0A080')
    return Image.blend(img.convert('RGB'), sepia.convert('RGB'), clamp(amount, 0, 100) / 100.0)

def apply_invert(img, amount=100):
    if amount <= 0:
        return img
    inverted = ImageOps.invert(img.convert('RGB'))
    return Image.blend(img.convert('RGB'), inverted, clamp(amount, 0, 100) / 100.0)

def apply_grayscale(img, amount=100):
    if amount <= 0:
        return img
    gray = ImageOps.grayscale(img).convert('RGB')
    return Image.blend(img.convert('RGB'), gray, clamp(amount, 0, 100) / 100.0)

def apply_blur(img, radius=0):
    if radius <= 0:
        return img
    return img.filter(ImageFilter.GaussianBlur(radius))

def apply_hue_rotate(img, degrees=0):
    if degrees == 0:
        return img
    src = img.convert('RGB')
    data = src.getdata()
    new = []
    shift = degrees / 360.0
    for px in data:
        r, g, b = [v / 255.0 for v in px]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        h = (h + shift) % 1.0
        r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
        new.append((int(r2 * 255), int(g2 * 255), int(b2 * 255)))
    img2 = Image.new('RGB', src.size)
    img2.putdata(new)
    return img2

def apply_temperature(img, temp=0):
    if temp == 0:
        return img
    pixels = list(img.convert('RGB').getdata())
    out = []
    delta = int(temp * 0.8)
    for (r, g, b) in pixels:
        r2 = clamp(r + delta, 0, 255)
        b2 = clamp(b - delta, 0, 255)
        out.append((r2, g, b2))
    img2 = Image.new('RGB', img.size)
    img2.putdata(out)
    return img2

def scale_image(img, scale):
    if scale == 1.0 or scale <= 0:
        return img
    try:
        w, h = img.size
        return img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    except Exception as e:
        print(f"Ошибка в scale_image: {e}")
        return img

def resize_image(img, width, height):
    if width <= 0 or height <= 0:
        return img
    return img.resize((width, height), Image.LANCZOS)

def crop_image(img, x, y, w, h):
    if w <= 0 or h <= 0:
        return img
    return img.crop((x, y, x + w, y + h))

def rotate_image(img, angle):
    if angle == 0:
        return img
    return img.rotate(angle, resample=Image.BICUBIC, expand=True)

def apply_vignette(img, strength=0.5):
    if strength <= 0:
        return img
    w, h = img.size
    vign = Image.new('L', (w, h), 255)
    draw = ImageDraw.Draw(vign)
    cx, cy = w / 2, h / 2
    maxr = math.hypot(cx, cy) * 1.2
    for x in range(w):
        for y in range(h):
            d = math.hypot(x - cx, y - cy) / maxr
            v = 255 * (1 - strength * (d ** 2))
            draw.point((x, y), fill=int(max(0, min(255, v))))
    return Image.composite(img, Image.new('RGB', img.size, (0, 0, 0)), vign)

def apply_film_grain(img, amount=10):
    if amount <= 0:
        return img
    w, h = img.size
    noise = Image.effect_noise((w, h), amount * 2.5).convert('L')
    noise = noise.point(lambda i: i // 2)
    grain = Image.merge('RGB', (noise, noise, noise))
    return ImageChops.add(img.convert('RGB'), grain, scale=1.0, offset=0)

def apply_posterize(img, bits=4):
    if bits >= 8:
        return img
    return ImageOps.posterize(img, bits)

def apply_solarize(img, thresh=128):
    return ImageOps.solarize(img, thresh)

def apply_glitch(img, intensity=8, slices=8):
    if intensity <= 0:
        return img
    w, h = img.size
    out = Image.new('RGB', (w, h))
    slice_h = max(1, h // slices)
    for i in range(slices):
        y0 = i * slice_h
        y1 = h if i == slices - 1 else (i + 1) * slice_h
        box = (0, y0, w, y1)
        part = img.crop(box)
        offset = random.randint(-intensity, intensity)
        r, g, b = part.split()
        r = ImageChops.offset(r, offset // 2, 0)
        b = ImageChops.offset(b, -offset // 2, 0)
        merged = Image.merge('RGB', (r, g, b))
        out.paste(merged, (max(0, offset), y0))
    return out

def apply_lomo(img):
    img = ImageEnhance.Color(img).enhance(1.4)
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img = apply_vignette(img, 0.6)
    return img

def apply_cyberpunk(img):
    w, h = img.size
    r, g, b = img.split()
    r = ImageEnhance.Brightness(r).enhance(0.9)
    b = ImageEnhance.Brightness(b).enhance(1.1)
    merged = Image.merge('RGB', (r, g, b))
    merged = ImageEnhance.Contrast(merged).enhance(1.15)
    return merged

def apply_inpaint(img, mask):
    img_np = np.array(img)
    mask_np = np.array(mask)
    inpainted = cv2.inpaint(img_np, mask_np, 3, cv2.INPAINT_TELEA)
    return Image.fromarray(inpainted)

def apply_background_blur(img, mask, radius=10):
    if radius <= 0:
        return img
    blurred = img.filter(ImageFilter.GaussianBlur(radius))
    mask_np = np.array(mask)
    mask_np = cv2.threshold(mask_np, 1, 255, cv2.THRESH_BINARY)[1]
    mask = Image.fromarray(mask_np)
    return Image.composite(blurred, img, mask)

def apply_background_remove(img, mask, strength=100):
    img_np = np.array(img.convert('RGB'))
    mask_np = np.array(mask)
    mask_np = cv2.threshold(mask_np, int(strength * 2.55 * 0.5), 255, cv2.THRESH_BINARY)[1]
    result = img_np.copy()
    result[mask_np > 0] = [0, 0, 0]
    return Image.fromarray(result)

PRESETS = {
    'Vintage Warm': {'brightness': 5, 'contrast': 10, 'saturation': -10, 'sepia': 30, 'clarity': 5},
    'Dramatic B&W': {'contrast': 30, 'saturation': -100, 'clarity': 30, 'grayscale': 100},
    'Soft Dream': {'brightness': 12, 'contrast': -8, 'saturation': 20, 'blur': 4, 'clarity': -6},
    'Pop Art': {'contrast': 20, 'saturation': 60, 'hue': 15},
    'Cold Steel': {'contrast': 5, 'saturation': -20, 'temperature': -25},
    'Film Grain': {'special': 'film_grain', 'grain': 12},
    'Glitch': {'special': 'glitch', 'intensity': 12, 'slices': 10},
    'Lomo': {'special': 'lomo'},
    'Cyberpunk': {'special': 'cyberpunk'},
    'Vignette Soft': {'vignette': 0.5, 'contrast': 5},
    'Posterize Pop': {'special': 'posterize', 'bits': 4},
    'Solarize Art': {'special': 'solarize', 'thresh': 120},
    'Retro Fade': {'brightness': -10, 'contrast': -15, 'saturation': -30, 'sepia': 20, 'vignette': 0.4},
    'High Contrast': {'contrast': 40, 'clarity': 20, 'saturation': 10},
    'Warm Sunset': {'temperature': 30, 'brightness': 10, 'saturation': 15, 'vignette': 0.3},
    'Cool Twilight': {'temperature': -30, 'brightness': -5, 'saturation': -10, 'blur': 2},
    'Vivid Colors': {'saturation': 50, 'contrast': 15, 'clarity': 10},
    'Noir': {'grayscale': 100, 'contrast': 25, 'brightness': -10, 'vignette': 0.6},
    'Pastel Glow': {'brightness': 15, 'saturation': -20, 'blur': 3, 'contrast': -10},
    'Neon Edge': {'contrast': 30, 'saturation': 40, 'hue': 45, 'vignette': 0.2},
    'Faded Polaroid': {'brightness': -15, 'contrast': -10, 'saturation': -25, 'sepia': 25, 'vignette': 0.5},
    'Cinematic': {'contrast': 20, 'brightness': -5, 'vignette': 0.7, 'saturation': -10},
    'Monochrome Soft': {'grayscale': 100, 'brightness': 5, 'contrast': 10, 'blur': 1},
    'Vibrant Landscape': {'saturation': 30, 'clarity': 15, 'brightness': 10, 'contrast': 10},
    'Golden Hour': {'temperature': 20, 'brightness': 15, 'saturation': 10, 'vignette': 0.4},
    'Moody Blues': {'temperature': -20, 'contrast': 15, 'saturation': -15, 'blur': 3},
    'Retro Chrome': {'sepia': 15, 'contrast': 10, 'brightness': -5, 'grain': 10},
    'Urban Grit': {'contrast': 25, 'saturation': -10, 'grain': 15, 'vignette': 0.5},
    'Dreamy Haze': {'blur': 5, 'brightness': 10, 'saturation': -20, 'vignette': 0.3},
    'Electric Pop': {'saturation': 70, 'contrast': 30, 'hue': 30},
    'Soft Sepia': {'sepia': 40, 'brightness': 5, 'contrast': -5, 'vignette': 0.2},
    'Bold Monochrome': {'grayscale': 100, 'contrast': 35, 'clarity': 25},
    'Cyber Glitch': {'special': 'glitch', 'intensity': 15, 'slices': 12},
    'Vintage Film': {'grain': 20, 'sepia': 20, 'contrast': 10, 'vignette': 0.6},
    'Solar Flare': {'special': 'solarize', 'thresh': 100, 'brightness': 10},
    'Pop Poster': {'special': 'posterize', 'bits': 3, 'saturation': 50},
    'Cool Mist': {'temperature': -15, 'blur': 2, 'brightness': -10, 'saturation': -20},
    'Warm Glow': {'temperature': 25, 'brightness': 20, 'saturation': 5},
    'Dark Fantasy': {'contrast': 20, 'brightness': -15, 'vignette': 0.8, 'saturation': -20},
    'Neon Nights': {'special': 'cyberpunk', 'saturation': 30, 'contrast': 20},
    'Old Photo': {'sepia': 50, 'grain': 15, 'brightness': -10, 'vignette': 0.5}
}

def render_preview(img, params):
    if img is None:
        print("render_preview: Input image is None")
        return None
    try:
        work = img.copy().convert('RGB')
        if params.get('rotate', 0):
            work = rotate_image(work, params['rotate'])
        work = apply_basic_enhancements(work, params)
        if params.get('grayscale', 0):
            work = apply_grayscale(work, params['grayscale'])
        if params.get('sepia', 0):
            work = apply_sepia(work, params['sepia'])
        if params.get('invert', 0):
            work = apply_invert(work, params['invert'])
        if params.get('hue', 0):
            work = apply_hue_rotate(work, params['hue'])
        if params.get('temperature', 0):
            work = apply_temperature(work, params['temperature'])
        if params.get('blur', 0):
            work = apply_blur(work, params['blur'])
        if params.get('vignette', 0):
            work = apply_vignette(work, params['vignette'])
        if params.get('grain', 0):
            work = apply_film_grain(work, params['grain'])
        if params.get('posterize_bits', 8) < 8:
            work = apply_posterize(work, int(params['posterize_bits']))
        if params.get('solarize_thresh', 128) != 128:
            work = apply_solarize(work, params['solarize_thresh'])
        if params.get('glitch_intensity', 0) > 0:
            work = apply_glitch(work, params['glitch_intensity'], params['glitch_slices'])
        if params.get('resize_width', 0) and params.get('resize_height', 0):
            work = resize_image(work, params['resize_width'], params['resize_height'])
        if params.get('crop_x', 0) or params.get('crop_y', 0) or params.get('crop_w', 0) or params.get('crop_h', 0):
            work = crop_image(work, params['crop_x'], params['crop_y'], params['crop_w'], params['crop_h'])
        special = params.get('special')
        if special == 'film_grain':
            amount = params.get('grain', 10)
            work = apply_film_grain(work, amount)
        if special == 'glitch':
            work = apply_glitch(work, params.get('intensity', 8), params.get('slices', 8))
        if special == 'lomo':
            work = apply_lomo(work)
        if special == 'cyberpunk':
            work = apply_cyberpunk(work)
        if special == 'posterize':
            work = apply_posterize(work, params.get('bits', 4))
        if special == 'solarize':
            work = apply_solarize(work, params.get('thresh', 120))
        if params.get('scale', 1.0) != 1.0 and params.get('is_thumbnail', False) == False:
            work = scale_image(work, params['scale'])
        return work
    except Exception as e:
        print(f"render_preview: Error processing image - {e}")
        return None

def make_thumbnail_for_preset(src_img, preset_params, thumb_size=(160, 120)):
    if src_img is None:
        return None
    try:
        img = src_img.copy()
        img.thumbnail(thumb_size, Image.LANCZOS)
        thumb_params = preset_params.copy()
        thumb_params['scale'] = 1.0
        thumb_params['is_thumbnail'] = True
        thumb = render_preview(img, thumb_params)
        return thumb
    except Exception as e:
        print(f"Ошибка в make_thumbnail_for_preset: {e}")
        return None