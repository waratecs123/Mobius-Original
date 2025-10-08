# functions.py
# Core utilities, color analysis, harmony generation, and export functions for Mondrian's Grid

import os
import json
import random
from PIL import Image, ImageDraw
import numpy as np
from sklearn.cluster import KMeans
import colorsys

# --------------------------
# Utilities
# --------------------------
APP_DIR = os.path.join(os.path.expanduser("~"), ".mondrian_grid")
os.makedirs(APP_DIR, exist_ok=True)
HISTORY_PATH = os.path.join(APP_DIR, "history.json")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)

def load_json(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print("Load error:", e)
    return None

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def hex_to_rgb(hexstr):
    hexstr = hexstr.lstrip('#')
    return tuple(int(hexstr[i:i+2], 16) for i in (0, 2, 4))

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def resize_for_processing(img, max_size=800):
    w, h = img.size
    if max(w, h) <= max_size:
        return img
    scale = max_size / max(w, h)
    return img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)

def img_to_numpy(img):
    return np.array(img.convert('RGB'))

# --------------------------
# Color analysis (KMeans)
# --------------------------
def get_dominant_colors_kmeans(pil_img, n_colors=6, downsample=0.2, seed=42):
    img_small = resize_for_processing(pil_img, max_size=700)
    arr = img_to_numpy(img_small)
    if downsample and 0 < downsample < 1:
        step = max(1, int(1/downsample))
        arr = arr[::step, ::step]
    pixels = arr.reshape(-1, 3).astype(float)
    n_colors = max(2, min(10, int(n_colors)))
    kmeans = KMeans(n_clusters=n_colors, random_state=seed, n_init=10)
    labels = kmeans.fit_predict(pixels)
    centers = kmeans.cluster_centers_.round().astype(int)
    counts = np.bincount(labels, minlength=n_colors)
    total = counts.sum() if counts.sum()>0 else 1
    percentages = (counts / total * 100).round(2)
    idx = np.argsort(-percentages)
    centers_sorted = [tuple(centers[i]) for i in idx]
    pct_sorted = [float(percentages[i]) for i in idx]
    return centers_sorted, pct_sorted

def get_color_percentages_for_palette(pil_img, palette):
    arr = img_to_numpy(resize_for_processing(pil_img, max_size=800))
    pixels = arr.reshape(-1, 3).astype(int)
    pal = np.array(palette).astype(int)
    dists = ((pixels[:, None, :] - pal[None, :, :]) ** 2).sum(axis=2)
    nearest = np.argmin(dists, axis=1)
    counts = np.bincount(nearest, minlength=len(palette))
    pct = (counts / counts.sum() * 100).round(2).tolist()
    return pct

# --------------------------
# Mood classification (expanded)
# --------------------------
def rgb_to_hsv_tuple(rgb):
    r,g,b = rgb
    return colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

def classify_mood(palette_rgb, percentages):
    hs, ss, vs = [], [], []
    for c, p in zip(palette_rgb, percentages):
        h,s,v = rgb_to_hsv_tuple(c)
        hs.append(h * p)
        ss.append(s * p)
        vs.append(v * p)
    total = sum(percentages) or 1
    avg_h = sum(hs)/total
    avg_s = sum(ss)/total
    avg_v = sum(vs)/total
    hue_deg = (avg_h * 360) % 360
    if avg_s < 0.15 and 0.4 < avg_v < 0.8:
        return "Нейтральное"
    if avg_s < 0.25 and 0.35 < avg_v < 0.85:
        return "Спокойное"
    if avg_s > 0.8 and avg_v > 0.7:
        return "Вибрационное"
    if avg_s > 0.6 and avg_v > 0.6:
        return "Энергичное"
    if avg_v < 0.35:
        return "Меланхоличное"
    if avg_v > 0.85:
        return "Яркое"
    if (330 <= hue_deg <= 360) or (0 <= hue_deg <= 60):
        return "Романтичное"
    if 60 < hue_deg < 180:
        return "Натуральное"
    if 180 < hue_deg < 300:
        return "Меланхоличное"
    return "Уравновешенное"

# --------------------------
# Harmony generation (expanded)
# --------------------------
def rotate_hue(rgb, deg):
    h,s,v = rgb_to_hsv_tuple(rgb)
    h_deg = (h*360 + deg) % 360
    h2 = h_deg/360.0
    r,g,b = colorsys.hsv_to_rgb(h2, s, v)
    return (clamp(r*255), clamp(g*255), clamp(b*255))

def alter_value(rgb, factor):
    h,s,v = rgb_to_hsv_tuple(rgb)
    v2 = max(0, min(1, v * factor))
    r,g,b = colorsys.hsv_to_rgb(h, s, v2)
    return (clamp(r*255), clamp(g*255), clamp(b*255))

def random_perturb(rgb, max_shift=20):
    r,g,b = rgb
    return (clamp(r + random.randint(-max_shift, max_shift)),
            clamp(g + random.randint(-max_shift, max_shift)),
            clamp(b + random.randint(-max_shift, max_shift)))

def generate_harmonies(base_rgb):
    harmonies = {}
    harmonies['Аналогичная'] = [rotate_hue(base_rgb, -60), rotate_hue(base_rgb, -30), base_rgb, rotate_hue(base_rgb, 30), rotate_hue(base_rgb, 60)]
    harmonies['Комплементарная'] = [base_rgb, rotate_hue(base_rgb, 180), rotate_hue(base_rgb, 170), rotate_hue(base_rgb, 190), alter_value(rotate_hue(base_rgb, 180), 0.92)]
    harmonies['Триадная'] = [base_rgb, rotate_hue(base_rgb, 120), rotate_hue(base_rgb, -120), alter_value(base_rgb, 1.12), alter_value(rotate_hue(base_rgb, 120), 0.9)]
    harmonies['Монохромная'] = [alter_value(base_rgb, 0.45), alter_value(base_rgb, 0.8), base_rgb, alter_value(base_rgb, 1.2), alter_value(base_rgb, 1.6)]
    harmonies['Разделённо-комплементарная'] = [base_rgb, rotate_hue(base_rgb, 150), rotate_hue(base_rgb, 210), alter_value(base_rgb, 0.9), alter_value(rotate_hue(base_rgb, 150), 1.1)]
    harmonies['Тетрадная'] = [base_rgb, rotate_hue(base_rgb, 60), rotate_hue(base_rgb, 180), rotate_hue(base_rgb, 240), alter_value(base_rgb, 1.05)]
    harmonies['Квадратная'] = [base_rgb, rotate_hue(base_rgb, 90), rotate_hue(base_rgb, 180), rotate_hue(base_rgb, 270), alter_value(rotate_hue(base_rgb, 90), 0.95)]
    # Free: mix, perturb, pastel + accent + more
    free = []
    free.append(random_perturb(rotate_hue(base_rgb, 90), max_shift=30))
    free.append(random_perturb(rotate_hue(base_rgb, -45), max_shift=25))
    free.append(random_perturb(alter_value(rotate_hue(base_rgb, 210), 0.85), max_shift=20))
    accent = list(base_rgb)
    accent[0] = clamp(accent[0] + 50)
    free.append(tuple(accent))
    h,s,v = rgb_to_hsv_tuple(base_rgb)
    pastel = colorsys.hsv_to_rgb(h, max(0, s*0.4), min(1, v*1.2))
    free.append((clamp(pastel[0]*255), clamp(pastel[1]*255), clamp(pastel[2]*255)))
    neon = colorsys.hsv_to_rgb(h, min(1, s*1.5), min(1, v*1.3))
    free.append((clamp(neon[0]*255), clamp(neon[1]*255), clamp(neon[2]*255)))
    harmonies['Свободная'] = free
    return harmonies

# --------------------------
# Exports (expanded with PNG)
# --------------------------
def export_css(hex_list, filename):
    lines = [":root {"]
    for i,h in enumerate(hex_list, start=1):
        lines.append(f"  --color-{i}: {h};")
    lines.append("}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def export_scss(hex_list, filename):
    lines = [f"$color-{i}: {h};" for i,h in enumerate(hex_list, start=1)]
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def export_gpl(hex_list, filename, name="Mondrian Palette"):
    lines = [f"GIMP Palette\nName: {name}\nColumns: {len(hex_list)}\n#"]
    for h in hex_list:
        r,g,b = hex_to_rgb(h)
        lines.append(f"{r}\t{g}\t{b}\t{h}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def export_json_for_figma(hex_list, filename):
    data = {"palette": [{"hex": h} for h in hex_list]}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_png(hex_list, filename, swatch_size=100):
    width = len(hex_list) * swatch_size
    height = swatch_size
    im = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(im)
    for i, h in enumerate(hex_list):
        rgb = hex_to_rgb(h)
        draw.rectangle((i*swatch_size, 0, (i+1)*swatch_size, height), fill=rgb)
        draw.text((i*swatch_size + 10, height - 20), h, fill=(0,0,0) if relative_luminance(rgb) > 0.5 else (255,255,255))
    im.save(filename)

# --------------------------
# Coloristics utilities
# --------------------------
def rgb_to_hsl(rgb):
    r,g,b = [x/255.0 for x in rgb]
    h,l,s = colorsys.rgb_to_hls(r,g,b)
    return (round(h*360,2), round(s*100,2), round(l*100,2))

def hsl_to_rgb(h,s,l):
    h = (h % 360)/360.0
    s = s/100.0
    l = l/100.0
    r,g,b = colorsys.hls_to_rgb(h,l,s)
    return (clamp(r*255), clamp(g*255), clamp(b*255))

def relative_luminance(rgb):
    def channel(c):
        c = c/255.0
        if c <= 0.03928:
            return c/12.92
        return ((c+0.055)/1.055)**2.4
    r,g,b = rgb
    return 0.2126*channel(r) + 0.7152*channel(g) + 0.0722*channel(b)

def contrast_ratio(rgb1, rgb2):
    l1 = relative_luminance(rgb1)
    l2 = relative_luminance(rgb2)
    L1, L2 = max(l1,l2), min(l1,l2)
    return round((L1 + 0.05) / (L2 + 0.05), 2)