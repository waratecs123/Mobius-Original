import random
import math
import colorsys
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageEnhance
import numpy as np

pattern_map = {
    "Случайные линии": "random_lines",
    "Случайные круги": "random_circles",
    "Случайные многоугольники": "random_polygons",
    "Градиент": "gradient",
    "Спираль": "spiral",
    "Волны": "waves",
    "Точки": "dots",
    "Полосы": "stripes",
    "Шахматная доска": "checkerboard",
    "Калейдоскоп": "kaleidoscope",
    "Фрактальное дерево": "fractal_tree",
    "Множество Мандельброта": "mandelbrot",
    "Множество Джулия": "julia",
    "Перлинов шум": "perlin_noise",
    "Вороной диаграмма": "voronoi",
    "Лабиринт": "maze",
    "Звезды": "stars",
    "Соты": "honeycomb",
    "Вращающиеся квадраты": "rotated_squares",
    "Концентрические круги": "concentric_circles",
    "Радиальные линии": "radial_lines",
    "Сетка точек": "grid_dots",
    "Интерференция волн": "wave_interference",
    "Плазма": "plasma",
    "Фейерверк": "firework",
    "Мозаика": "mosaic",
    "Абстрактные формы": "abstract_shapes",
    "Текстуры": "textures",
    "Фрактальные облака": "fractal_clouds",
    "Геометрические узоры": "geometric_patterns",
    "Фрактальный ферн": "fractal_fern",
    "Снежинка Коха": "koch_snowflake",
    "Мозаика Вороного с градиентом": "voronoi_mosaic",
    "Случайные треугольники": "random_triangles",
    "Синусоидальные волны": "sine_waves",
    "Кубики": "cubes"
}

effect_map = {
    "Размытие": "blur",
    "Резкость": "sharpen",
    "Контур": "contour",
    "Эмбосс": "emboss",
    "Инверсия цветов": "invert",
    "Сепия": "sepia",
    "Черно-белый": "grayscale",
    "Поворот": "rotate",
    "Зеркальное отражение": "mirror",
    "Шум": "noise",
    "Яркость": "brightness",
    "Контраст": "contrast",
    "Насыщенность": "saturation",
    "Гамма-коррекция": "gamma",
    "Соляризация": "solarize",
    "Постеризация": "posterize",
    "Эффект края": "edge_enhance",
    "Фильтр минимума": "min_filter",
    "Фильтр максимума": "max_filter"
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

def apply_gradient(draw, shape_func, start_color, end_color, bbox, direction='vertical'):
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if direction == 'vertical':
        for y in range(height):
            ratio = y / height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            draw.line((bbox[0], bbox[1] + y, bbox[2], bbox[1] + y), fill=(r, g, b))
    else:
        for x in range(width):
            ratio = x / width
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            draw.line((bbox[0] + x, bbox[1], bbox[0] + x, bbox[3]), fill=(r, g, b))
    shape_func(outline=start_color)

def generate_single_pattern(pattern_type, colors, width, height, use_gradient=False):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    start_color = colors[1]
    end_color = colors[2] if len(colors) > 2 else colors[1]
    direction = random.choice(['vertical', 'horizontal']) if use_gradient else 'vertical'

    if pattern_type == "random_lines":
        num_lines = random.randint(50, 250)
        for _ in range(num_lines):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            color = random.choice(colors[1:]) + (random.randint(100, 255),)
            line_width = random.randint(1, 20)
            draw.line((x1, y1, x2, y2), fill=color, width=line_width)

    elif pattern_type == "random_circles":
        num_circles = random.randint(20, 200)
        for _ in range(num_circles):
            x, y = random.randint(0, width), random.randint(0, height)
            r = random.randint(5, min(width, height) // 2)
            bbox = (x - r, y - r, x + r, y + r)
            if use_gradient:
                def ellipse_outline(outline):
                    draw.ellipse(bbox, outline=outline + (255,))
                apply_gradient(draw, ellipse_outline, start_color, end_color, bbox, direction)
            else:
                color = random.choice(colors[1:]) + (random.randint(120, 255),)
                outline_color = random.choice(colors) + (255,)
                draw.ellipse(bbox, fill=color, outline=outline_color, width=random.randint(1, 8))

    elif pattern_type == "random_polygons":
        num_polygons = random.randint(10, 100)
        for _ in range(num_polygons):
            num_points = random.randint(3, 12)
            points = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_points)]
            min_x, min_y = min(p[0] for p in points), min(p[1] for p in points)
            max_x, max_y = max(p[0] for p in points), max(p[1] for p in points)
            bbox = (min_x, min_y, max_x, max_y)
            if use_gradient:
                def polygon_outline(outline):
                    draw.polygon(points, outline=outline + (255,))
                apply_gradient(draw, polygon_outline, start_color, end_color, bbox, direction)
            else:
                color = random.choice(colors[1:]) + (random.randint(100, 255),)
                outline_color = random.choice(colors) + (255,)
                draw.polygon(points, fill=color, outline=outline_color)

    elif pattern_type == "gradient":
        apply_gradient(draw, lambda outline: None, start_color, end_color, (0, 0, width, height), direction)

    elif pattern_type == "spiral":
        center_x, center_y = width // 2, height // 2
        angle = random.uniform(0, 360)
        radius = 0
        steps = random.randint(1000, 3000)
        angle_step = random.uniform(3, 20)
        radius_step = random.uniform(0.05, 2.0)
        for _ in range(steps):
            x = center_x + int(radius * math.cos(math.radians(angle)))
            y = center_y + int(radius * math.sin(math.radians(angle)))
            color = random.choice(colors[1:]) + (random.randint(150, 255),)
            dot_size = random.randint(1, 20)
            draw.ellipse((x - dot_size, y - dot_size, x + dot_size, y + dot_size), fill=color)
            angle += angle_step
            radius += radius_step

    elif pattern_type == "waves":
        wave_height = random.randint(10, 100)
        wave_length = random.randint(50, 300)
        phase_shift = random.uniform(0, 2 * math.pi)
        for y in range(0, height, max(1, wave_height // 10)):
            for x in range(width):
                offset = int(wave_height * math.sin(2 * math.pi * (x + y) / wave_length + phase_shift))
                color = random.choice(colors[1:]) + (255,)
                draw.point((x, (y + offset) % height), fill=color)

    elif pattern_type == "dots":
        num_dots = random.randint(300, 2000)
        for _ in range(num_dots):
            x, y = random.randint(0, width), random.randint(0, height)
            r = random.randint(1, 60)
            bbox = (x - r, y - r, x + r, y + r)
            if use_gradient:
                def ellipse_outline(outline):
                    draw.ellipse(bbox, outline=outline + (255,))
                apply_gradient(draw, ellipse_outline, start_color, end_color, bbox, direction)
            else:
                color = random.choice(colors[1:]) + (random.randint(128, 255),)
                draw.ellipse(bbox, fill=color)

    elif pattern_type == "stripes":
        stripe_width = random.randint(5, 200)
        vertical = random.choice([True, False])
        if vertical:
            for i in range(0, width, stripe_width * 2):
                bbox = (i, 0, min(i + stripe_width, width), height)
                if use_gradient:
                    def rect_outline(outline):
                        draw.rectangle(bbox, outline=outline + (255,))
                    apply_gradient(draw, rect_outline, colors[1], colors[2], bbox, direction)
                else:
                    draw.rectangle(bbox, fill=colors[1] + (255,))
                if i + stripe_width * 2 < width:
                    bbox = (i + stripe_width, 0, min(i + stripe_width * 2, width), height)
                    if use_gradient:
                        def rect_outline(outline):
                            draw.rectangle(bbox, outline=outline + (255,))
                        apply_gradient(draw, rect_outline, colors[2], colors[1], bbox, direction)
                    else:
                        draw.rectangle(bbox, fill=colors[2] + (255,))
        else:
            for i in range(0, height, stripe_width * 2):
                bbox = (0, i, width, min(i + stripe_width, height))
                if use_gradient:
                    def rect_outline(outline):
                        draw.rectangle(bbox, outline=outline + (255,))
                    apply_gradient(draw, rect_outline, colors[1], colors[2], bbox, direction)
                else:
                    draw.rectangle(bbox, fill=colors[1] + (255,))
                if i + stripe_width * 2 < height:
                    bbox = (0, i + stripe_width, width, min(i + stripe_width * 2, height))
                    if use_gradient:
                        def rect_outline(outline):
                            draw.rectangle(bbox, outline=outline + (255,))
                        apply_gradient(draw, rect_outline, colors[2], colors[1], bbox, direction)
                    else:
                        draw.rectangle(bbox, fill=colors[2] + (255,))

    elif pattern_type == "checkerboard":
        square_size = random.randint(10, 250)
        for y in range(0, height, square_size):
            for x in range(0, width, square_size):
                color = colors[1] if (x // square_size + y // square_size) % 2 == 0 else colors[2]
                bbox = (x, y, min(x + square_size, width), min(y + square_size, height))
                if use_gradient:
                    def rect_outline(outline):
                        draw.rectangle(bbox, outline=outline + (255,))
                    apply_gradient(draw, rect_outline, color, colors[0], bbox, direction)
                else:
                    draw.rectangle(bbox, fill=color + (255,))

    elif pattern_type == "kaleidoscope":
        sector_width, sector_height = width // 8, height // 8
        num_elements = random.randint(20, 150)
        temp_img = Image.new("RGBA", (sector_width, sector_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        for _ in range(num_elements):
            x, y = random.randint(0, sector_width), random.randint(0, sector_height)
            color = random.choice(colors[1:]) + (random.randint(120, 255),)
            r = random.randint(1, 30)
            temp_draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
        for sx in range(sector_width):
            for sy in range(sector_height):
                pixel = temp_img.getpixel((sx, sy))
                img.putpixel((sx, sy), pixel)
                img.putpixel((width - sx - 1, sy), pixel)
                img.putpixel((sx, height - sy - 1), pixel)
                img.putpixel((width - sx - 1, height - sy - 1), pixel)
                img.putpixel((sy, sx), pixel)
                img.putpixel((height - sy - 1, sx), pixel)
                img.putpixel((sy, width - sx - 1), pixel)
                img.putpixel((height - sy - 1, width - sx - 1), pixel)

    elif pattern_type == "fractal_tree":
        def draw_tree(x, y, length, angle, depth, branch_color):
            if depth == 0:
                return
            x2 = x + length * math.cos(math.radians(angle))
            y2 = y - length * math.sin(math.radians(angle))
            if use_gradient:
                steps = int(length)
                for i in range(steps):
                    ratio = i / steps
                    r = int(branch_color[0] + (colors[0][0] - branch_color[0]) * ratio)
                    g = int(branch_color[1] + (colors[0][1] - branch_color[1]) * ratio)
                    b = int(branch_color[2] + (colors[0][2] - branch_color[2]) * ratio)
                    draw.point((int(x + i * math.cos(math.radians(angle))), int(y - i * math.sin(math.radians(angle)))), (r, g, b, 255))
            else:
                draw.line((x, y, x2, y2), fill=branch_color + (255,), width=depth // 2 + 1)
            new_length = length * random.uniform(0.5, 0.9)
            left_angle = angle - random.randint(15, 45)
            right_angle = angle + random.randint(15, 45)
            draw_tree(x2, y2, new_length, left_angle, depth - 1, branch_color)
            draw_tree(x2, y2, new_length, right_angle, depth - 1, branch_color)

        tree_depth = random.randint(8, 18)
        start_length = min(width, height) // 3
        draw_tree(width // 2, height - 10, start_length, 90, tree_depth, random.choice(colors[1:]))

    elif pattern_type == "mandelbrot":
        max_iter = 150
        zoom = random.uniform(1.0, 4.0)
        offset_x, offset_y = random.uniform(-0.7, 0.7), random.uniform(-0.7, 0.7)
        for px in range(width):
            for py in range(height):
                x0 = (px / width * 3.5 - 2.5) / zoom + offset_x
                y0 = (py / height * 2 - 1) / zoom + offset_y
                x, y = 0.0, 0.0
                iteration = 0
                while x * x + y * y <= 4 and iteration < max_iter:
                    xtemp = x * x - y * y + x0
                    y = 2 * x * y + y0
                    x = xtemp
                    iteration += 1
                if iteration == max_iter:
                    img.putpixel((px, py), colors[1] + (255,))
                else:
                    shade = int(255 * (iteration / max_iter) ** 0.5)
                    img.putpixel((px, py), (shade, shade // 2, shade * 2 // 3, 255))

    elif pattern_type == "julia":
        max_iter = 150
        c_real, c_imag = random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)
        for px in range(width):
            for py in range(height):
                x = (px / width * 4 - 2)
                y = (py / height * 4 - 2)
                iteration = 0
                while x * x + y * y <= 4 and iteration < max_iter:
                    xtemp = x * x - y * y + c_real
                    y = 2 * x * y + c_imag
                    x = xtemp
                    iteration += 1
                if iteration == max_iter:
                    img.putpixel((px, py), colors[1] + (255,))
                else:
                    shade = int(255 * (iteration / max_iter) ** 0.5)
                    img.putpixel((px, py), (shade, shade // 3, shade * 3 // 4, 255))

    elif pattern_type == "perlin_noise":
        def fade(t):
            return t * t * t * (t * (t * 6 - 15) + 10)

        def lerp(a, b, x):
            return a + x * (b - a)

        def grad(hash, x, y):
            switch = hash % 4
            if switch == 0:
                return x + y
            elif switch == 1:
                return -x + y
            elif switch == 2:
                return x - y
            return -x - y

        permutation = list(range(256))
        random.shuffle(permutation)
        p = permutation * 2
        grid_size = 50
        for px in range(width):
            for py in range(height):
                x, y = px / grid_size, py / grid_size
                xi, yi = int(x), int(y)
                xf, yf = x - xi, y - yi
                u, v = fade(xf), fade(yf)
                n00 = grad(p[p[xi] + yi], xf, yf)
                n01 = grad(p[p[xi] + yi + 1], xf, yf - 1)
                n10 = grad(p[p[xi + 1] + yi], xf - 1, yf)
                n11 = grad(p[p[xi + 1] + yi + 1], xf - 1, yf - 1)
                x0 = lerp(n00, n10, u)
                x1 = lerp(n01, n11, u)
                value = lerp(x0, x1, v)
                color_val = int(128 + 127 * value)
                img.putpixel((px, py), (color_val, color_val, color_val, 255))

    elif pattern_type == "voronoi":
        num_points = random.randint(20, 100)
        points = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_points)]
        point_colors = [random.choice(colors[1:]) for _ in range(num_points)]
        for px in range(width):
            for py in range(height):
                min_dist = float('inf')
                closest = 0
                for i, (pxp, pyp) in enumerate(points):
                    dist = math.hypot(px - pxp, py - pyp)
                    if dist < min_dist:
                        min_dist = dist
                        closest = i
                img.putpixel((px, py), point_colors[closest] + (255,))

    elif pattern_type == "maze":
        cell_size = random.randint(10, 50)
        grid_width, grid_height = width // cell_size, height // cell_size
        grid = np.ones((grid_height, grid_width), dtype=bool)
        stack = [(0, 0)]
        grid[0, 0] = False
        while stack:
            x, y = stack[-1]
            neighbors = [(x + dx, y + dy) for dx, dy in [(0, 2), (0, -2), (2, 0), (-2, 0)]
                         if 0 <= x + dx < grid_width and 0 <= y + dy < grid_height and grid[y + dy, x + dx]]
            if neighbors:
                nx, ny = random.choice(neighbors)
                grid[ny, nx] = False
                grid[y + (ny - y) // 2, x + (nx - x) // 2] = False
                stack.append((nx, ny))
            else:
                stack.pop()
        for y in range(grid_height):
            for x in range(grid_width):
                if grid[y, x]:
                    draw.rectangle((x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size),
                                   fill=colors[1] + (255,))

    elif pattern_type == "stars":
        num_stars = random.randint(50, 300)
        for _ in range(num_stars):
            x, y = random.randint(0, width), random.randint(0, height)
            size = random.randint(1, 10)
            color = random.choice(colors[1:]) + (random.randint(150, 255),)
            draw.ellipse((x - size, y - size, x + size, y + size), fill=color)

    elif pattern_type == "honeycomb":
        hex_size = random.randint(10, 50)
        for y in range(-hex_size, height + hex_size, int(hex_size * 1.5)):
            for x in range(-hex_size, width + hex_size, int(hex_size * 1.732)):
                points = [(x + hex_size * math.cos(math.radians(60 * i)), y + hex_size * math.sin(math.radians(60 * i))) for i in range(6)]
                color = random.choice(colors[1:]) + (255,)
                draw.polygon(points, fill=color, outline=colors[0] + (255,))

    elif pattern_type == "rotated_squares":
        square_size = random.randint(20, 100)
        for y in range(0, height, square_size):
            for x in range(0, width, square_size):
                angle = random.randint(0, 360)
                points = [(x + square_size / 2 + square_size / 2 * math.cos(math.radians(angle + 45 * i)),
                           y + square_size / 2 + square_size / 2 * math.sin(math.radians(angle + 45 * i))) for i in range(4)]
                color = random.choice(colors[1:]) + (255,)
                draw.polygon(points, fill=color)

    elif pattern_type == "concentric_circles":
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 2
        step = random.randint(5, 20)
        for r in range(step, max_radius, step):
            color = random.choice(colors[1:]) + (255,)
            draw.ellipse((center_x - r, center_y - r, center_x + r, center_y + r), outline=color, width=random.randint(1, 5))

    elif pattern_type == "radial_lines":
        center_x, center_y = width // 2, height // 2
        num_lines = random.randint(20, 100)
        length = min(width, height) // 2
        for i in range(num_lines):
            angle = i * 360 / num_lines + random.uniform(-5, 5)
            x2 = center_x + length * math.cos(math.radians(angle))
            y2 = center_y + length * math.sin(math.radians(angle))
            color = random.choice(colors[1:]) + (255,)
            draw.line((center_x, center_y, x2, y2), fill=color, width=random.randint(1, 8))

    elif pattern_type == "grid_dots":
        dot_spacing = random.randint(10, 60)
        for x in range(0, width, dot_spacing):
            for y in range(0, height, dot_spacing):
                color = random.choice(colors[1:]) + (random.randint(128, 255),)
                r = random.randint(1, dot_spacing // 1.5)
                draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

    elif pattern_type == "wave_interference":
        num_sources = random.randint(2, 7)
        sources = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_sources)]
        wavelength = random.uniform(10, 60)
        for px in range(width):
            for py in range(height):
                intensity = sum(math.cos(2 * math.pi * math.hypot(px - sx, py - sy) / wavelength) for sx, sy in sources) / num_sources
                color_val = int(128 + 127 * intensity)
                if use_gradient:
                    h = color_val / 255
                    r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(h, 1, 1)]
                    img.putpixel((px, py), (r, g, b, 255))
                else:
                    img.putpixel((px, py), (color_val, color_val, color_val, 255))

    elif pattern_type == "plasma":
        for px in range(width):
            for py in range(height):
                value = (math.sin(px / 30) + math.sin(py / 30) + math.sin((px + py) / 40) + math.sin((px - py) / 40) + 4) / 8
                r = int(255 * math.sin(value * math.pi))
                g = int(255 * math.cos(value * math.pi))
                b = int(255 * value)
                img.putpixel((px, py), (r, g, b, 255))

    elif pattern_type == "firework":
        num_fireworks = random.randint(5, 30)
        for _ in range(num_fireworks):
            center_x, center_y = random.randint(0, width), random.randint(0, height)
            num_particles = random.randint(50, 300)
            color = random.choice(colors[1:]) + (255,)
            for p in range(num_particles):
                angle = random.uniform(0, 360)
                dist = random.uniform(10, 150)
                x = center_x + dist * math.cos(math.radians(angle))
                y = center_y + dist * math.sin(math.radians(angle))
                draw.point((x, y), fill=color)
                for trail in range(1, 6):
                    tx = center_x + (dist - trail * 5) * math.cos(math.radians(angle))
                    ty = center_y + (dist - trail * 5) * math.sin(math.radians(angle))
                    if use_gradient:
                        ratio = trail / 6
                        r = int(color[0] * (1 - ratio))
                        g = int(color[1] * (1 - ratio))
                        b = int(color[2] * (1 - ratio))
                        draw.point((tx, ty), (r, g, b, 255))
                    else:
                        draw.point((tx, ty), fill=color)

    elif pattern_type == "mosaic":
        tile_size = random.randint(10, 60)
        for ty in range(0, height, tile_size):
            for tx in range(0, width, tile_size):
                color = random.choice(colors[1:]) + (255,)
                bbox = (tx, ty, min(tx + tile_size, width), min(ty + tile_size, height))
                if use_gradient:
                    def rect_outline(outline):
                        draw.rectangle(bbox, outline=outline + (255,))
                    apply_gradient(draw, rect_outline, color[:-1], colors[0], bbox, direction)
                else:
                    draw.rectangle(bbox, fill=color)

    elif pattern_type == "abstract_shapes":
        num_shapes = random.randint(10, 70)
        for _ in range(num_shapes):
            shape_type = random.choice(["circle", "rect", "poly"])
            color = random.choice(colors[1:]) + (random.randint(100, 255),)
            if shape_type == "circle":
                x, y = random.randint(0, width), random.randint(0, height)
                r = random.randint(10, 120)
                bbox = (x - r, y - r, x + r, y + r)
                if use_gradient:
                    def shape_func(outline):
                        draw.ellipse(bbox, outline=outline + (255,))
                    apply_gradient(draw, shape_func, start_color, end_color, bbox, direction)
                else:
                    draw.ellipse(bbox, fill=color)
            elif shape_type == "rect":
                x1, y1 = random.randint(0, width), random.randint(0, height)
                x2, y2 = random.randint(x1, width), random.randint(y1, height)
                bbox = (x1, y1, x2, y2)
                if use_gradient:
                    def shape_func(outline):
                        draw.rectangle(bbox, outline=outline + (255,))
                    apply_gradient(draw, shape_func, start_color, end_color, bbox, direction)
                else:
                    draw.rectangle(bbox, fill=color)
            else:
                points = [(random.randint(0, width), random.randint(0, height)) for _ in range(random.randint(3, 8))]
                min_x, min_y = min(p[0] for p in points), min(p[1] for p in points)
                max_x, max_y = max(p[0] for p in points), max(p[1] for p in points)
                bbox = (min_x, min_y, max_x, max_y)
                if use_gradient:
                    def shape_func(outline):
                        draw.polygon(points, outline=outline + (255,))
                    apply_gradient(draw, shape_func, start_color, end_color, bbox, direction)
                else:
                    draw.polygon(points, fill=color)

    elif pattern_type == "textures":
        for px in range(width):
            for py in range(height):
                noise = random.random()
                color_val = int(255 * noise)
                img.putpixel((px, py), (color_val, color_val, color_val, 255))

    elif pattern_type == "fractal_clouds":
        scale = 0.005
        octaves = 6
        persistence = 0.5
        for px in range(width):
            for py in range(height):
                noise = 0
                amp = 1
                for octave in range(octaves):
                    n = math.sin(px * scale * (2 ** octave)) + math.cos(py * scale * (2 ** octave))
                    noise += n * amp
                    amp *= persistence
                color_val = int(128 + noise * 64)
                img.putpixel((px, py), (color_val, color_val, color_val, 255))

    elif pattern_type == "geometric_patterns":
        num_patterns = random.randint(5, 30)
        for _ in range(num_patterns):
            x, y = random.randint(0, width), random.randint(0, height)
            size = random.randint(20, 120)
            color = random.choice(colors[1:]) + (255,)
            num_sides = random.randint(3, 10)
            points = [(x + size * math.cos(2 * math.pi * i / num_sides), y + size * math.sin(2 * math.pi * i / num_sides)) for i in range(num_sides)]
            min_x, min_y = min(p[0] for p in points), min(p[1] for p in points)
            max_x, max_y = max(p[0] for p in points), max(p[1] for p in points)
            bbox = (min_x, min_y, max_x, max_y)
            if use_gradient:
                def polygon_outline(outline):
                    draw.polygon(points, outline=outline + (255,))
                apply_gradient(draw, polygon_outline, color[:-1], colors[0], bbox, direction)
            else:
                draw.polygon(points, fill=color)

    elif pattern_type == "fractal_fern":
        def fern(x, y, prob):
            if prob < 0.01:
                return 0, 0.16 * y
            elif prob < 0.86:
                return 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
            elif prob < 0.93:
                return 0.2 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
            return -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44

        num_points = 75000
        x, y = 0, 0
        for _ in range(num_points):
            prob = random.random()
            x, y = fern(x, y, prob)
            px = int(width / 2 + x * width / 10)
            py = int(height - y * height / 11)
            if 0 <= px < width and 0 <= py < height:
                color = random.choice(colors[1:]) + (255,)
                draw.point((px, py), color)

    elif pattern_type == "koch_snowflake":
        def koch_curve(start, end, depth):
            if depth == 0:
                draw.line([start, end], fill=random.choice(colors[1:]) + (255,), width=3)
                return
            dx, dy = end[0] - start[0], end[1] - start[1]
            a = (start[0] + dx / 3, start[1] + dy / 3)
            c = (start[0] + 2 * dx / 3, start[1] + 2 * dy / 3)
            b = (a[0] + math.cos(math.pi / 3) * (c[0] - a[0]) - math.sin(math.pi / 3) * (c[1] - a[1]),
                 a[1] + math.sin(math.pi / 3) * (c[0] - a[0]) + math.cos(math.pi / 3) * (c[1] - a[1]))
            koch_curve(start, a, depth - 1)
            koch_curve(a, b, depth - 1)
            koch_curve(b, c, depth - 1)
            koch_curve(c, end, depth - 1)

        side = min(width, height) * 0.8
        height_tri = side * math.sqrt(3) / 2
        p1 = (width / 2 - side / 2, height / 2 + height_tri / 3)
        p2 = (width / 2 + side / 2, height / 2 + height_tri / 3)
        p3 = (width / 2, height / 2 - 2 * height_tri / 3)
        depth = 5
        koch_curve(p1, p2, depth)
        koch_curve(p2, p3, depth)
        koch_curve(p3, p1, depth)

    elif pattern_type == "voronoi_mosaic":
        num_points = random.randint(20, 120)
        points = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_points)]
        point_colors = [random.choice(colors[1:]) for _ in range(num_points)]
        for px in range(width):
            for py in range(height):
                min_dist = float('inf')
                closest = 0
                for i, (pxp, pyp) in enumerate(points):
                    dist = math.hypot(px - pxp, py - pyp)
                    if dist < min_dist:
                        min_dist = dist
                        closest = i
                ratio = min_dist / (min(width, height) / 20)
                r = int(point_colors[closest][0] * (1 - ratio))
                g = int(point_colors[closest][1] * (1 - ratio))
                b = int(point_colors[closest][2] * (1 - ratio))
                img.putpixel((px, py), (r, g, b, 255))

    elif pattern_type == "random_triangles":
        num_triangles = random.randint(20, 150)
        for _ in range(num_triangles):
            points = [(random.randint(0, width), random.randint(0, height)) for _ in range(3)]
            color = random.choice(colors[1:]) + (random.randint(100, 255),)
            draw.polygon(points, fill=color)

    elif pattern_type == "sine_waves":
        amplitude = random.randint(20, 80)
        frequency = random.uniform(0.01, 0.06)
        phase_shift = random.uniform(0, 2 * math.pi)
        for y in range(height):
            for x in range(width):
                offset = int(amplitude * math.sin(frequency * x + phase_shift))
                color = random.choice(colors[1:]) + (255,)
                draw.point((x, (y + offset) % height), color)

    elif pattern_type == "cubes":
        cube_size = random.randint(20, 60)
        for y in range(0, height, cube_size):
            for x in range(0, width, cube_size):
                color = random.choice(colors[1:]) + (255,)
                draw.rectangle((x, y, x + cube_size, y + cube_size), fill=color)
                shadow_color = (max(0, color[0] - 50), max(0, color[1] - 50), max(0, color[2] - 50), 255)
                draw.line((x + cube_size // 2, y - cube_size // 2, x + cube_size, y, x + cube_size // 2, y + cube_size // 2), fill=shadow_color)

    return img

def combine_patterns(pattern_types, colors, width, height, use_gradient):
    bg_img = Image.new("RGB", (width, height), colors[0])
    for p_type in pattern_types:
        pattern_img = generate_single_pattern(p_type, colors, width, height, use_gradient)
        bg_img = Image.alpha_composite(bg_img.convert("RGBA"), pattern_img).convert("RGB")
    return bg_img

def apply_effects(base_img, effects):
    img = base_img.copy()
    width, height = img.size
    for effect in effects:
        if effect == "blur":
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
        elif effect == "sharpen":
            img = img.filter(ImageFilter.SHARPEN)
        elif effect == "contour":
            img = img.filter(ImageFilter.CONTOUR)
        elif effect == "emboss":
            img = img.filter(ImageFilter.EMBOSS)
        elif effect == "invert":
            img = ImageOps.invert(img)
        elif effect == "sepia":
            def sepia_filter(pixel):
                r, g, b = pixel[:3]
                new_r = min(int(r * 0.393 + g * 0.769 + b * 0.189), 255)
                new_g = min(int(r * 0.349 + g * 0.686 + b * 0.168), 255)
                new_b = min(int(r * 0.272 + g * 0.534 + b * 0.131), 255)
                return (new_r, new_g, new_b)
            img = img.point(sepia_filter)
        elif effect == "grayscale":
            img = ImageOps.grayscale(img).convert("RGB")
        elif effect == "rotate":
            angle = random.choice([90, 180, 270])
            img = img.rotate(angle, expand=True)
        elif effect == "mirror":
            img = ImageOps.mirror(img)
        elif effect == "noise":
            noise = np.random.randint(-50, 50, (height, width, 3))
            img_array = np.array(img)
            img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(img_array)
        elif effect == "brightness":
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(random.uniform(0.7, 1.3))
        elif effect == "contrast":
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(random.uniform(0.7, 1.3))
        elif effect == "saturation":
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(random.uniform(0.7, 1.3))
        elif effect == "gamma":
            gamma = random.uniform(0.5, 2.0)
            table = [int(((i / 255.0) ** (1 / gamma) * 255)) for i in range(256)]
            img = img.point(table * 3)
        elif effect == "solarize":
            threshold = random.randint(100, 200)
            img = ImageOps.solarize(img, threshold)
        elif effect == "posterize":
            bits = random.randint(1, 4)
            img = ImageOps.posterize(img, bits)
        elif effect == "edge_enhance":
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        elif effect == "min_filter":
            img = img.filter(ImageFilter.MinFilter(3))
        elif effect == "max_filter":
            img = img.filter(ImageFilter.MaxFilter(3))
    return img

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))