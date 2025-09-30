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

def apply_tint(img, tint=0):
    if tint == 0:
        return img
    pixels = list(img.convert('RGB').getdata())
    out = []
    delta = int(tint * 0.8)
    for (r, g, b) in pixels:
        g2 = clamp(g + delta, 0, 255)
        out.append((r, g2, b))
    img2 = Image.new('RGB', img.size)
    img2.putdata(out)
    return img2

def apply_gamma(img, gamma=1.0):
    if gamma == 1.0:
        return img
    inv_gamma = 1.0 / gamma
    table = [((i / 255.0) ** inv_gamma) * 255 for i in range(256)]
    table = [int(round(v)) for v in table]
    return img.point(table * 3)

def apply_highlights(img, amount=0):
    if amount == 0:
        return img
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(1 + amount / 50.0)

def apply_shadows(img, amount=0):
    if amount == 0:
        return img
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(1 - amount / 50.0)

def apply_whites(img, amount=0):
    if amount == 0:
        return img
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(1 + amount / 50.0)

def apply_blacks(img, amount=0):
    if amount == 0:
        return img
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(1 - amount / 50.0)

def apply_vibrance(img, amount=0):
    if amount == 0:
        return img
    enhancer = ImageEnhance.Color(img)
    return enhancer.enhance(1 + amount / 50.0)

def apply_fade(img, amount=0):
    if amount == 0:
        return img
    return Image.blend(img, ImageOps.grayscale(img).convert('RGB'), amount / 100.0)

def apply_curve(img, amount=0):
    if amount == 0:
        return img
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(1 + amount / 100.0)

def apply_color_balance(img, amount=0):
    if amount == 0:
        return img
    r, g, b = img.split()
    r = ImageEnhance.Brightness(r).enhance(1 + amount / 100.0)
    return Image.merge('RGB', (r, g, b))

def apply_selective_color(img, amount=0):
    if amount == 0:
        return img
    enhancer = ImageEnhance.Color(img)
    return enhancer.enhance(1 + amount / 100.0)

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
    x, y, w, h = int(x), int(y), int(w), int(h)
    if x < 0 or y < 0 or x + w > img.width or y + h > img.height:
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

def apply_emboss(img, amount=100):
    if amount <= 0:
        return img
    embossed = img.filter(ImageFilter.EMBOSS)
    return Image.blend(img.convert('RGB'), embossed.convert('RGB'), clamp(amount, 0, 100) / 100.0)

def apply_edge_enhance(img, amount=100):
    if amount <= 0:
        return img
    enhanced = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return Image.blend(img.convert('RGB'), enhanced.convert('RGB'), clamp(amount, 0, 100) / 100.0)

def apply_contour(img, amount=100):
    if amount <= 0:
        return img
    contoured = img.filter(ImageFilter.CONTOUR)
    return Image.blend(img.convert('RGB'), contoured.convert('RGB'), clamp(amount, 0, 100) / 100.0)

def apply_sharpen(img, amount=100):
    if amount <= 0:
        return img
    sharpened = img.filter(ImageFilter.SHARPEN)
    return Image.blend(img.convert('RGB'), sharpened.convert('RGB'), clamp(amount, 0, 100) / 100.0)

def apply_mirror(img):
    return ImageOps.mirror(img)

def apply_flip(img):
    return ImageOps.flip(img)

def apply_find_edges(img, amount=100):
    if amount <= 0:
        return img
    edges = img.filter(ImageFilter.FIND_EDGES)
    return Image.blend(img.convert('RGB'), edges.convert('RGB'), clamp(amount, 0, 100) / 100.0)

def apply_smooth(img, amount=100):
    if amount <= 0:
        return img
    smoothed = img.filter(ImageFilter.SMOOTH_MORE)
    return Image.blend(img.convert('RGB'), smoothed.convert('RGB'), clamp(amount, 0, 100) / 100.0)

def apply_unsharp_mask(img, radius=2, percent=150, threshold=3):
    if radius <= 0:
        return img
    return img.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))

def apply_median_filter(img, size=3):
    if size <= 1:
        return img
    return img.filter(ImageFilter.MedianFilter(size=size))

def apply_box_blur(img, radius=0):
    if radius <= 0:
        return img
    return img.filter(ImageFilter.BoxBlur(radius))

def apply_min_filter(img, size=3):
    if size <= 1:
        return img
    return img.filter(ImageFilter.MinFilter(size=size))

def apply_max_filter(img, size=3):
    if size <= 1:
        return img
    return img.filter(ImageFilter.MaxFilter(size=size))

def apply_mode_filter(img, size=3):
    if size <= 1:
        return img
    return img.filter(ImageFilter.ModeFilter(size=size))

def apply_rank_filter(img, size=3, rank=0):
    if size <= 1:
        return img
    return img.filter(ImageFilter.RankFilter(size=size, rank=rank))

def apply_detail(img, amount=100):
    if amount <= 0:
        return img
    detailed = img.filter(ImageFilter.DETAIL)
    return Image.blend(img.convert('RGB'), detailed.convert('RGB'), clamp(amount, 0, 100) / 100.0)

def apply_edge_detect(img, amount=100):
    if amount <= 0:
        return img
    edges = img.filter(ImageFilter.EDGE_ENHANCE)
    return Image.blend(img.convert('RGB'), edges.convert('RGB'), clamp(amount, 0, 100) / 100.0)

def apply_bilateral_filter(img, sigma_color=75, sigma_space=75):
    if sigma_color <= 0:
        return img
    img_np = np.array(img)
    bilateral = cv2.bilateralFilter(img_np, d=9, sigmaColor=sigma_color, sigmaSpace=sigma_space)
    return Image.fromarray(bilateral)

def apply_cartoon(img, amount=100):
    if amount <= 0:
        return img
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img_np, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return Image.fromarray(cartoon)

def apply_oil_paint(img, radius=5):
    if radius <= 0:
        return img
    img_np = np.array(img)
    oil = cv2.xphoto.oilPainting(img_np, size=7, dynRatio=radius)
    return Image.fromarray(oil)

def apply_watercolor(img, amount=100):
    if amount <= 0:
        return img
    img_np = np.array(img)
    watercolor = cv2.stylization(img_np, sigma_s=60, sigma_r=amount / 100.0)
    return Image.fromarray(watercolor)

def apply_sketch(img, amount=100):
    if amount <= 0:
        return img
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    inv_blur = 255 - blur
    sketch = cv2.divide(gray, inv_blur, scale=256.0)
    return Image.fromarray(sketch).convert('RGB')

PRESETS = {
    'Vintage Warm': {'brightness': 5, 'contrast': 10, 'saturation': -10, 'sepia': 30, 'clarity': 5},
    'Dramatic B&W': {'contrast': 30, 'grayscale': 100, 'clarity': 30},
    'Soft Dream': {'brightness': 12, 'contrast': -8, 'saturation': 20, 'blur': 4, 'clarity': -6},
    'Pop Art': {'contrast': 20, 'saturation': 60, 'hue': 15},
    'Cold Steel': {'contrast': 5, 'saturation': -20, 'temperature': -25},
    'Film Grain': {'grain': 12},
    'Glitch': {'glitch_intensity': 12, 'glitch_slices': 10},
    'Lomo': {'saturation': 40, 'contrast': 20, 'vignette': 60},
    'Cyberpunk': {'brightness': -10, 'contrast': 15, 'saturation': 10},
    'Vignette Soft': {'vignette': 50, 'contrast': 5},
    'Posterize Pop': {'posterize_bits': 4, 'saturation': 50},
    'Solarize Art': {'solarize_thresh': 120, 'brightness': 10},
    'Retro Fade': {'brightness': -10, 'contrast': -15, 'saturation': -30, 'sepia': 20, 'vignette': 40},
    'High Contrast': {'contrast': 40, 'clarity': 20, 'saturation': 10},
    'Warm Sunset': {'temperature': 30, 'brightness': 10, 'saturation': 15, 'vignette': 30},
    'Cool Twilight': {'temperature': -30, 'brightness': -5, 'saturation': -10, 'blur': 2},
    'Vivid Colors': {'saturation': 50, 'clarity': 15, 'brightness': 10, 'contrast': 10},
    'Noir': {'grayscale': 100, 'contrast': 25, 'brightness': -10, 'vignette': 60},
    'Pastel Glow': {'brightness': 15, 'saturation': -20, 'blur': 3, 'contrast': -10},
    'Neon Edge': {'contrast': 30, 'saturation': 40, 'hue': 45, 'vignette': 20},
    'Faded Polaroid': {'brightness': -15, 'contrast': -10, 'saturation': -25, 'sepia': 25, 'vignette': 50},
    'Cinematic': {'contrast': 20, 'brightness': -5, 'vignette': 70, 'saturation': -10},
    'Monochrome Soft': {'grayscale': 100, 'brightness': 5, 'contrast': 10, 'blur': 1},
    'Vibrant Landscape': {'saturation': 30, 'clarity': 15, 'brightness': 10, 'contrast': 10},
    'Golden Hour': {'temperature': 20, 'brightness': 15, 'saturation': 10, 'vignette': 40},
    'Moody Blues': {'temperature': -20, 'contrast': 15, 'saturation': -15, 'blur': 3},
    'Retro Chrome': {'sepia': 15, 'contrast': 10, 'brightness': -5, 'grain': 10},
    'Urban Grit': {'contrast': 25, 'saturation': -10, 'grain': 15, 'vignette': 50},
    'Dreamy Haze': {'blur': 5, 'brightness': 10, 'saturation': -20, 'vignette': 30},
    'Electric Pop': {'saturation': 70, 'contrast': 30, 'hue': 30},
    'Soft Sepia': {'sepia': 40, 'brightness': 5, 'contrast': -5, 'vignette': 20},
    'Bold Monochrome': {'grayscale': 100, 'contrast': 35, 'clarity': 25},
    'Cyber Glitch': {'glitch_intensity': 15, 'glitch_slices': 12},
    'Vintage Film': {'grain': 20, 'sepia': 20, 'contrast': 10, 'vignette': 60},
    'Solar Flare': {'solarize_thresh': 100, 'brightness': 10},
    'Pop Poster': {'posterize_bits': 3, 'saturation': 50},
    'Cool Mist': {'temperature': -15, 'blur': 2, 'brightness': -10, 'saturation': -20},
    'Warm Glow': {'temperature': 25, 'brightness': 20, 'saturation': 5},
    'Dark Fantasy': {'contrast': 20, 'brightness': -15, 'vignette': 80, 'saturation': -20},
    'Neon Nights': {'saturation': 30, 'contrast': 20},
    'Old Photo': {'sepia': 50, 'grain': 15, 'brightness': -10, 'vignette': 50},
    'Emboss Effect': {'emboss': 100},
    'Edge Enhance': {'edge_enhance': 100},
    'Contour Art': {'contour': 100},
    'Super Sharpen': {'sharpen': 100},
    'Mirror Image': {'mirror': True},
    'Flip Image': {'flip': True},
    'Edge Detection': {'find_edges': 100},
    'Smooth Image': {'smooth': 100},
    'Unsharp Mask': {'unsharp_radius': 2, 'unsharp_percent': 150, 'unsharp_threshold': 3},
    'Median Filter': {'median_size': 3},
    'Box Blur': {'box_radius': 5},
    'Min Filter': {'min_size': 3},
    'Max Filter': {'max_size': 3},
    'Mode Filter': {'mode_size': 3},
    'Rank Filter': {'rank_size': 3, 'rank': 0},
    'Detail Enhance': {'detail': 100},
    'Edge Detect': {'edge_detect': 100},
    'Bilateral Filter': {'bilateral_sigma_color': 75, 'bilateral_sigma_space': 75},
    'Cartoon': {'cartoon': 100},
    'Oil Paint': {'oil_radius': 5},
    'Watercolor': {'watercolor': 100},
    'Sketch': {'sketch': 100}
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
        if params.get('tint', 0):
            work = apply_tint(work, params['tint'])
        if params.get('gamma', 1.0) != 1.0:
            work = apply_gamma(work, params['gamma'])
        if params.get('highlights', 0):
            work = apply_highlights(work, params['highlights'])
        if params.get('shadows', 0):
            work = apply_shadows(work, params['shadows'])
        if params.get('whites', 0):
            work = apply_whites(work, params['whites'])
        if params.get('blacks', 0):
            work = apply_blacks(work, params['blacks'])
        if params.get('vibrance', 0):
            work = apply_vibrance(work, params['vibrance'])
        if params.get('fade', 0):
            work = apply_fade(work, params['fade'])
        if params.get('curve', 0):
            work = apply_curve(work, params['curve'])
        if params.get('color_balance', 0):
            work = apply_color_balance(work, params['color_balance'])
        if params.get('selective_color', 0):
            work = apply_selective_color(work, params['selective_color'])
        if params.get('blur', 0):
            work = apply_blur(work, params['blur'])
        if params.get('vignette', 0):
            work = apply_vignette(work, params['vignette'] / 100.0)
        if params.get('grain', 0):
            work = apply_film_grain(work, params['grain'])
        if params.get('posterize_bits', 8) < 8:
            work = apply_posterize(work, int(params['posterize_bits']))
        if params.get('solarize_thresh', 128) != 128:
            work = apply_solarize(work, params['solarize_thresh'])
        if params.get('glitch_intensity', 0) > 0:
            work = apply_glitch(work, params['glitch_intensity'], params.get('glitch_slices', 8))
        if params.get('emboss', 0):
            work = apply_emboss(work, params['emboss'])
        if params.get('edge_enhance', 0):
            work = apply_edge_enhance(work, params['edge_enhance'])
        if params.get('contour', 0):
            work = apply_contour(work, params['contour'])
        if params.get('sharpen', 0):
            work = apply_sharpen(work, params['sharpen'])
        if params.get('mirror', False):
            work = apply_mirror(work)
        if params.get('flip', False):
            work = apply_flip(work)
        if params.get('find_edges', 0):
            work = apply_find_edges(work, params['find_edges'])
        if params.get('smooth', 0):
            work = apply_smooth(work, params['smooth'])
        if params.get('unsharp_radius', 0) > 0:
            work = apply_unsharp_mask(work, params['unsharp_radius'], params.get('unsharp_percent', 150), params.get('unsharp_threshold', 3))
        if params.get('median_size', 1) > 1:
            work = apply_median_filter(work, params['median_size'])
        if params.get('box_radius', 0) > 0:
            work = apply_box_blur(work, params['box_radius'])
        if params.get('min_size', 1) > 1:
            work = apply_min_filter(work, params['min_size'])
        if params.get('max_size', 1) > 1:
            work = apply_max_filter(work, params['max_size'])
        if params.get('mode_size', 1) > 1:
            work = apply_mode_filter(work, params['mode_size'])
        if params.get('rank_size', 1) > 1:
            work = apply_rank_filter(work, params['rank_size'], params.get('rank', 0))
        if params.get('detail', 0):
            work = apply_detail(work, params['detail'])
        if params.get('edge_detect', 0):
            work = apply_edge_detect(work, params['edge_detect'])
        if params.get('bilateral_sigma_color', 0) > 0:
            work = apply_bilateral_filter(work, params['bilateral_sigma_color'], params.get('bilateral_sigma_space', 75))
        if params.get('cartoon', 0):
            work = apply_cartoon(work, params['cartoon'])
        if params.get('oil_radius', 0) > 0:
            work = apply_oil_paint(work, params['oil_radius'])
        if params.get('watercolor', 0):
            work = apply_watercolor(work, params['watercolor'])
        if params.get('sketch', 0):
            work = apply_sketch(work, params['sketch'])
        if params.get('resize_width', 0) and params.get('resize_height', 0):
            work = resize_image(work, params['resize_width'], params['resize_height'])
        if params.get('crop_w', 0) > 0 and params.get('crop_h', 0) > 0:
            work = crop_image(work, params['crop_x'], params['crop_y'], params['crop_w'], params['crop_h'])
        if params.get('scale', 1.0) != 1.0 and not params.get('is_thumbnail', False):
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