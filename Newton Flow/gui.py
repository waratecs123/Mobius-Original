import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import json
import os
from PIL import Image, ImageTk
import numpy as np
from functions import BeatPadFunctions
from sound_manager import SoundManager


class BeatPadGUI:
    def __init__(self, root):
        self.root = root
        self.setup_theme()

        # Инициализация компонентов
        self.sound_manager = SoundManager()
        self.functions = BeatPadFunctions(self.sound_manager)
        self.functions.set_loop_callback(self.update_playback_position)

        # Переменные интерфейса
        self.current_tool = "draw"
        self.selected_cells = set()
        self.clipboard = None
        self.dragging = False
        self.last_cell = None
        self.current_step = 0

        # Загрузка конфигурации
        self.load_config()

        # Создание интерфейса
        self.setup_ui()
        self.bind_events()

        # Первоначальное обновление
        self.update_beat_grid()
        self.update_bpm_display()

    def setup_theme(self):
        """Настройка темы в стиле Fibonacci Scan"""
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.secondary_accent = "#818cf8"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#2d3748"
        self.success_color = "#10b981"
        self.warning_color = "#f59e0b"
        self.error_color = "#ef4444"

        # Шрифты
        self.title_font = ('Arial', 20, 'bold')
        self.subtitle_font = ('Arial', 14, 'bold')
        self.app_font = ('Arial', 12)
        self.button_font = ('Arial', 11)
        self.small_font = ('Arial', 10)

        self.root.configure(bg=self.bg_color)

    def setup_ui(self):
        """Создание основного интерфейса"""
        # Главный контейнер
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        self.setup_header(main_container)

        # Основной контент
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(fill="both", expand=True, pady=(20, 0))

        # Левая панель
        left_panel = ttk.Frame(content_frame, style="TFrame", width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        left_panel.pack_propagate(False)

        # Правая панель
        right_panel = ttk.Frame(content_frame, style="TFrame")
        right_panel.pack(side="right", fill="both", expand=True)

        # Заполнение панелей
        self.setup_tools_panel(left_panel)
        self.setup_sounds_panel(left_panel)
        self.setup_beat_grid_panel(right_panel)
        self.setup_control_panel(right_panel)

        # Статус бар
        self.setup_status_bar(main_container)

    def setup_header(self, parent):
        """Заголовок приложения"""
        header_frame = ttk.Frame(parent, style="TFrame")
        header_frame.pack(fill="x")

        # Логотип и название
        logo_frame = ttk.Frame(header_frame, style="TFrame")
        logo_frame.pack(side="left")

        logo_canvas = tk.Canvas(logo_frame, bg=self.bg_color, width=50, height=50,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")
        logo_canvas.create_oval(5, 5, 45, 45, fill=self.accent_color, outline="")
        logo_canvas.create_text(25, 25, text="NF", font=('Arial', 16, 'bold'),
                                fill="#ffffff", tags="logo")

        tk.Label(logo_frame, text="NEWTON FLOW", font=self.title_font,
                 bg=self.bg_color, fg=self.accent_color).pack(side="left", padx=10)

        # Кнопки управления окном
        control_frame = ttk.Frame(header_frame, style="TFrame")
        control_frame.pack(side="right")

        ttk.Button(control_frame, text="⛶", command=self.toggle_fullscreen,
                   style="TButton", width=3).pack(side="left", padx=5)
        ttk.Button(control_frame, text="🗕", command=self.root.iconify,
                   style="TButton", width=3).pack(side="left", padx=5)
        ttk.Button(control_frame, text="✕", command=self.on_closing,
                   style="TButton", width=3).pack(side="left", padx=5)

    def setup_tools_panel(self, parent):
        """Панель инструментов"""
        tools_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        tools_card.pack(fill="x", pady=(0, 15))

        tk.Label(tools_card, text="Инструменты", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        # Кнопки инструментов
        tools = [
            ("draw", "✏️ Рисование", "Добавление битов"),
            ("erase", "🧽 Стирание", "Удаление битов"),
            ("select", "🔍 Выделение", "Выделение области")
        ]

        self.tool_var = tk.StringVar(value="draw")

        for tool, text, desc in tools:
            frame = ttk.Frame(tools_card, style="Card.TFrame")
            frame.pack(fill="x", pady=2)

            btn = ttk.Radiobutton(frame, text=text, value=tool, variable=self.tool_var,
                                  command=lambda t=tool: self.set_tool(t), style="Tool.TRadiobutton")
            btn.pack(anchor="w")

            tk.Label(frame, text=desc, font=self.small_font, fg=self.secondary_text,
                     bg=self.card_color).pack(anchor="w", padx=25, pady=(0, 5))

        # Дополнительные инструменты
        extra_frame = ttk.Frame(tools_card, style="Card.TFrame")
        extra_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(extra_frame, text="📋 Копировать", command=self.copy_selection,
                   style="TButton").pack(fill="x", pady=2)
        ttk.Button(extra_frame, text="📄 Вставить", command=self.paste_selection,
                   style="TButton").pack(fill="x", pady=2)
        ttk.Button(extra_frame, text="🔄 Сдвиг вправо", command=self.shift_right,
                   style="TButton").pack(fill="x", pady=2)

    def setup_sounds_panel(self, parent):
        """Панель управления звуками"""
        sound_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        sound_card.pack(fill="both", expand=True)

        tk.Label(sound_card, text="Управление звуками", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        # Контейнер с прокруткой
        container = ttk.Frame(sound_card, style="Card.TFrame")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=self.card_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Card.TFrame")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.setup_sound_list(scroll_frame)

    def setup_sound_list(self, parent):
        """Список звуков"""
        for i in range(16):
            self.create_sound_widget(parent, i)

    def create_sound_widget(self, parent, index):
        """Виджет для управления одним звуком"""
        frame = ttk.Frame(parent, style="Card.TFrame", padding=5)
        frame.pack(fill="x", pady=2)

        # Цветной индикатор
        color_canvas = tk.Canvas(frame, width=20, height=20, bg=self.get_color_for_sound(index),
                                 highlightthickness=0, bd=0)
        color_canvas.pack(side="left", padx=(0, 10))
        color_canvas.create_text(10, 10, text=str(index + 1), fill="white",
                                 font=('Arial', 10, 'bold'))

        # Кнопка воспроизведения
        ttk.Button(frame, text="▶", width=2, command=lambda: self.play_sound(index)).pack(side="left", padx=2)

        # Поле имени
        name_var = tk.StringVar(value=self.sound_manager.get_sound_name(index))
        entry = ttk.Entry(frame, textvariable=name_var, width=15, font=self.small_font)
        entry.pack(side="left", padx=5, fill="x", expand=True)
        entry.bind("<FocusOut>", lambda e: self.rename_sound(index, name_var.get()))

        # Кнопка загрузки
        ttk.Button(frame, text="📁", width=2, command=lambda: self.load_sound(index)).pack(side="left", padx=2)

        # Информация о файле
        file_label = tk.Label(frame, text=self.sound_manager.get_sound_file_name(index),
                              font=self.small_font, fg=self.secondary_text, bg=self.card_color)
        file_label.pack(side="left", padx=5)

    def setup_beat_grid_panel(self, parent):
        """Панель с beat grid"""
        beat_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        beat_card.pack(fill="both", expand=True)

        # Заголовок
        header = ttk.Frame(beat_card, style="Card.TFrame")
        header.pack(fill="x", pady=(0, 10))

        tk.Label(header, text="Beat Grid", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(side="left")

        self.bpm_label = tk.Label(header, text=f"BPM: {self.functions.bpm}",
                                  font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        self.bpm_label.pack(side="right")

        # Canvas для сетки
        grid_frame = ttk.Frame(beat_card, style="Card.TFrame")
        grid_frame.pack(fill="both", expand=True)

        self.beat_canvas = tk.Canvas(grid_frame, bg=self.card_color, highlightthickness=0)
        self.beat_canvas.pack(fill="both", expand=True, padx=2, pady=2)

    def setup_control_panel(self, parent):
        """Панель управления"""
        control_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        control_card.pack(fill="x", pady=(15, 0))

        # Основные кнопки
        btn_frame = ttk.Frame(control_card, style="Card.TFrame")
        btn_frame.pack(fill="x")

        self.play_btn = ttk.Button(btn_frame, text="▶️ Воспроизведение",
                                   style="Accent.TButton", command=self.toggle_playback)
        self.play_btn.pack(side="left", fill="x", expand=True, padx=2)

        ttk.Button(btn_frame, text="🗑️ Очистить", style="TButton",
                   command=self.clear_all).pack(side="left", fill="x", expand=True, padx=2)

        ttk.Button(btn_frame, text="💾 Экспорт", style="TButton",
                   command=self.export_pattern).pack(side="left", fill="x", expand=True, padx=2)

        ttk.Button(btn_frame, text="🎵 Пресеты", style="TButton",
                   command=self.show_presets).pack(side="left", fill="x", expand=True, padx=2)

        # Слайдер BPM
        bpm_frame = ttk.Frame(control_card, style="Card.TFrame")
        bpm_frame.pack(fill="x", pady=(10, 0))

        tk.Label(bpm_frame, text="Скорость (BPM):", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.bpm_var = tk.IntVar(value=self.functions.bpm)
        bpm_scale = ttk.Scale(bpm_frame, from_=60, to=240, orient=tk.HORIZONTAL,
                              variable=self.bpm_var, command=self.update_bpm)
        bpm_scale.pack(fill="x", pady=5)

    def setup_status_bar(self, parent):
        """Статус бар"""
        status_frame = ttk.Frame(parent, style="Card.TFrame", padding=10)
        status_frame.pack(fill="x", pady=(15, 0))

        self.status_text = tk.StringVar(value="Готов к созданию битов! Выберите инструмент и начинайте творить.")
        status_label = tk.Label(status_frame, textvariable=self.status_text,
                                font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        status_label.pack(side="left")

        self.step_label = tk.Label(status_frame, text="Шаг: 0",
                                   font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        self.step_label.pack(side="right")

    def bind_events(self):
        """Привязка событий"""
        self.beat_canvas.bind("<Button-1>", self.on_beat_grid_click)
        self.beat_canvas.bind("<B1-Motion>", self.on_beat_grid_drag)
        self.beat_canvas.bind("<ButtonRelease-1>", self.on_beat_grid_release)
        self.beat_canvas.bind("<Button-3>", self.on_beat_grid_right_click)

        # Глобальные горячие клавиши
        self.root.bind("<space>", lambda e: self.toggle_playback())
        self.root.bind("<Delete>", lambda e: self.clear_all())
        self.root.bind("<Control-s>", lambda e: self.export_pattern())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

        # Обработка изменения размера
        self.root.bind("<Configure>", lambda e: self.on_resize())

    def update_playback_position(self, step):
        """Update the playback position display"""
        self.current_step = step
        self.step_label.config(text=f"Шаг: {step + 1}")

        # Redraw the grid to show the current playing position
        self.update_beat_grid()

        # Update status text
        if self.functions.is_playing:
            self.status_text.set(f"Воспроизведение... Шаг {step + 1}/16")

    def update_beat_grid(self):
        """Обновление отображения сетки"""
        self.beat_canvas.delete("all")
        width = self.beat_canvas.winfo_width()
        height = self.beat_canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        rows = cols = self.functions.grid_size
        cell_width = width / cols
        cell_height = height / rows

        # Рисуем сетку
        for i in range(rows + 1):
            y = i * cell_height
            width = 2 if i % 4 == 0 else 1
            self.beat_canvas.create_line(0, y, width, y, fill=self.border_color, width=width)

        for j in range(cols + 1):
            x = j * cell_width
            width = 2 if j % 4 == 0 else 1
            self.beat_canvas.create_line(x, 0, x, height, fill=self.border_color, width=width)

        # Рисуем активные ячейки
        for i in range(rows):
            for j in range(cols):
                if self.functions.beat_matrix[i, j]:
                    x1 = j * cell_width + 2
                    y1 = i * cell_height + 2
                    x2 = x1 + cell_width - 4
                    y2 = y1 + cell_height - 4

                    color = self.get_color_for_sound(j)
                    self.beat_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                    # Номер звука
                    self.beat_canvas.create_text(x1 + cell_width / 2 - 2, y1 + cell_height / 2 - 2,
                                                 text=str(j + 1), fill="white", font=('Arial', 8, 'bold'))

        # Подсветка текущего шага
        if self.functions.is_playing:
            step_width = width / 16
            x1 = self.functions.current_step * step_width
            x2 = x1 + step_width
            self.beat_canvas.create_rectangle(x1, 0, x2, height, fill=self.accent_color,
                                              stipple="gray50", outline="", alpha=0.3)

    def get_color_for_sound(self, index):
        """Цвет для звука"""
        colors = [
            '#e74c3c', '#3498db', '#2ecc71', '#f39c12',
            '#9b59b6', '#1abc9c', '#d35400', '#27ae60',
            '#8e44ad', '#f1c40f', '#e67e22', '#16a085',
            '#c0392b', '#2980b9', '#27ae60', '#d35400'
        ]
        return colors[index % len(colors)]

    def set_tool(self, tool):
        """Set the current tool"""
        self.current_tool = tool
        tool_names = {
            "draw": "Рисование",
            "erase": "Стирание",
            "select": "Выделение"
        }
        self.status_text.set(f"Инструмент: {tool_names.get(tool, tool)}")

    def on_beat_grid_click(self, event):
        """Handle click on beat grid"""
        if not self.functions.is_playing:
            width = self.beat_canvas.winfo_width()
            height = self.beat_canvas.winfo_height()

            if width <= 1 or height <= 1:
                return

            rows = cols = self.functions.grid_size
            cell_width = width / cols
            cell_height = height / rows

            col = int(event.x / cell_width)
            row = int(event.y / cell_height)

            if 0 <= row < rows and 0 <= col < cols:
                if self.current_tool == "draw":
                    self.functions.toggle_cell(row, col, True)
                elif self.current_tool == "erase":
                    self.functions.toggle_cell(row, col, False)
                elif self.current_tool == "select":
                    # Handle selection logic
                    self.selected_cells = {(row, col)}

                self.update_beat_grid()
                self.last_cell = (row, col)
                self.dragging = True

    def on_beat_grid_drag(self, event):
        """Handle drag on beat grid"""
        if self.dragging and self.last_cell and not self.functions.is_playing:
            width = self.beat_canvas.winfo_width()
            height = self.beat_canvas.winfo_height()

            rows = cols = self.functions.grid_size
            cell_width = width / cols
            cell_height = height / rows

            col = int(event.x / cell_width)
            row = int(event.y / cell_height)

            if (0 <= row < rows and 0 <= col < cols and
                    (row, col) != self.last_cell):

                if self.current_tool == "draw":
                    self.functions.toggle_cell(row, col, True)
                elif self.current_tool == "erase":
                    self.functions.toggle_cell(row, col, False)
                elif self.current_tool == "select":
                    self.selected_cells.add((row, col))

                self.update_beat_grid()
                self.last_cell = (row, col)

    def on_beat_grid_release(self, event):
        """Handle mouse release on beat grid"""
        self.dragging = False
        self.last_cell = None

    def on_beat_grid_right_click(self, event):
        """Handle right click on beat grid"""
        pass

    def toggle_playback(self):
        """Toggle playback"""
        is_playing = self.functions.toggle_playback()
        if is_playing:
            self.play_btn.config(text="⏸️ Пауза")
            self.status_text.set("Воспроизведение...")
        else:
            self.play_btn.config(text="▶️ Воспроизведение")
            self.status_text.set("Пауза")
        self.update_beat_grid()

    def update_bpm(self, value):
        """Update BPM from slider"""
        self.functions.bpm = int(float(value))
        self.update_bpm_display()

    def update_bpm_display(self):
        """Update BPM label"""
        self.bpm_label.config(text=f"BPM: {self.functions.bpm}")

    def clear_all(self):
        """Clear all beats"""
        self.functions.clear_all()
        self.update_beat_grid()
        self.status_text.set("Все биты очищены")

    def export_pattern(self):
        """Export pattern to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            if self.functions.export_json(file_path):
                self.status_text.set(f"Паттерн экспортирован: {os.path.basename(file_path)}")
            else:
                self.status_text.set("Ошибка экспорта")

    def show_presets(self):
        """Show presets dialog"""
        messagebox.showinfo("Пресеты", "Функция пресетов будет реализована в будущих версиях")

    def play_sound(self, index):
        """Play sound by index"""
        self.sound_manager.play_sound(index)
        self.status_text.set(f"Воспроизведение: {self.sound_manager.get_sound_name(index)}")

    def rename_sound(self, index, name):
        """Rename sound"""
        self.sound_manager.set_sound_name(index, name)
        self.status_text.set(f"Звук переименован: {name}")

    def load_sound(self, index):
        """Load sound from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio files", "*.wav *.mp3 *.ogg"), ("All files", "*.*")]
        )
        if file_path:
            if self.sound_manager.load_sound(index, file_path):
                self.status_text.set(f"Звук загружен: {os.path.basename(file_path)}")
                # Обновляем виджет звука
                self.update_sound_widgets()
            else:
                self.status_text.set("Ошибка загрузки звука")

    def update_sound_widgets(self):
        """Update sound widgets"""
        # Эта функция будет обновлять все виджеты звуков
        pass

    def copy_selection(self):
        """Copy selected cells"""
        if self.selected_cells:
            self.clipboard = list(self.selected_cells)
            self.status_text.set(f"Скопировано {len(self.selected_cells)} ячеек")
        else:
            self.status_text.set("Нет выделенных ячеек для копирования")

    def paste_selection(self):
        """Paste copied cells"""
        if self.clipboard:
            for row, col in self.clipboard:
                if 0 <= row < 16 and 0 <= col < 16:
                    self.functions.toggle_cell(row, col, True)
            self.update_beat_grid()
            self.status_text.set(f"Вставлено {len(self.clipboard)} ячеек")
        else:
            self.status_text.set("Буфер обмена пуст")

    def shift_right(self):
        """Shift pattern to the right"""
        # Простой сдвиг всех битов вправо
        new_matrix = np.roll(self.functions.beat_matrix, 1, axis=1)
        self.functions.beat_matrix = new_matrix
        self.update_beat_grid()
        self.status_text.set("Паттерн сдвинут вправо")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def on_resize(self):
        """Handle window resize"""
        self.update_beat_grid()

    def undo(self):
        """Undo last action"""
        self.status_text.set("Функция отмены будет реализована в будущих версиях")

    def redo(self):
        """Redo last action"""
        self.status_text.set("Функция повтора будет реализована в будущих версиях")

    def load_config(self):
        """Load configuration"""
        config_path = "newton_flow_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                if "sound_config" in config:
                    self.sound_manager.load_config(config["sound_config"])
                if "functions_config" in config:
                    self.functions.load_config(config["functions_config"])
            except:
                pass

    def save_config(self):
        """Save configuration"""
        config = {
            "sound_config": self.sound_manager.get_config(),
            "functions_config": self.functions.get_config()
        }
        try:
            with open("newton_flow_config.json", 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass

    def on_closing(self):
        """Обработка закрытия приложения"""
        self.save_config()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BeatPadGUI(root)
    root.mainloop()