import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import json
import os
from PIL import Image, ImageTk
import numpy as np
from functions import BeatPadFunctions
from sound_manager import SoundManager
from sound_browser import SoundBrowser


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
        self.current_sound_slot = 0
        self.recording = False
        self.recorded_steps = set()

        # Храним переменные для полей имени звука
        self.sound_name_vars = [tk.StringVar() for _ in range(16)]

        # Загрузка конфигурации
        self.load_config()

        # Создание интерфейса
        self.setup_ui()
        self.bind_events()

        # Первоначальное обновление
        self.update_beat_grid()
        self.update_bpm_display()
        self.update_sound_widgets()

    def setup_theme(self):
        """Расширенная настройка темы в стиле Fibonacci Scan"""
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
        self.highlight_color = "#4f46e5"
        self.record_color = "#dc2626"

        # Шрифты
        self.title_font = ('Arial', 20, 'bold')
        self.subtitle_font = ('Arial', 14, 'bold')
        self.app_font = ('Arial', 12)
        self.button_font = ('Arial', 11)
        self.small_font = ('Arial', 10)

        self.root.configure(bg=self.bg_color)

        # Стили для ttk
        style = ttk.Style()
        style.theme_use('clam')

        # Настройка стилей
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_color)
        style.configure("TButton", background=self.card_color, foreground=self.text_color,
                        borderwidth=1, focusthickness=3, focuscolor=self.accent_color)
        style.configure("Accent.TButton", background=self.accent_color,
                        foreground="white", font=self.button_font)
        style.configure("Tool.TRadiobutton", background=self.card_color,
                        foreground=self.text_color, font=self.button_font)
        style.configure("Record.TButton", background=self.record_color,
                        foreground="white", font=self.button_font)

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
        left_panel = ttk.Frame(content_frame, style="TFrame", width=400)
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

        tk.Label(logo_frame, text="NEWTON FLOW PRO", font=self.title_font,
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

        tk.Label(tools_card, text="🎨 Инструменты", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        # Кнопки инструментов
        tools = [
            ("draw", "✏️ Рисование", "Добавление битов"),
            ("erase", "🧽 Стирание", "Удаление битов"),
            ("record", "🔴 Запись", "Запись в реальном времени")
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
        ttk.Button(extra_frame, text="🎵 Браузер звуков", command=lambda: self.open_sound_browser(),
                   style="Accent.TButton").pack(fill="x", pady=2)

    def setup_sounds_panel(self, parent):
        """Панель управления звуками с прокруткой"""
        sound_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        sound_card.pack(fill="both", expand=True)

        tk.Label(sound_card, text="🎵 Управление звуками", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        # Создаем фрейм с прокруткой
        container = ttk.Frame(sound_card)
        container.pack(fill="both", expand=True)

        # Создаем canvas и scrollbars
        canvas = tk.Canvas(container, bg=self.card_color, highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas, style="Card.TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        canvas.pack(side="top", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        # Привязываем прокрутку колесиком мыши
        canvas.bind("<MouseWheel>", self.on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", self.on_mousewheel)

        # Сохраняем ссылку на scrollable_frame
        self.sound_frame = scrollable_frame
        self.setup_sound_list(self.sound_frame)

    def setup_sound_list(self, parent):
        """Список звуков"""
        for i in range(16):
            self.create_sound_widget(parent, i)

    def create_sound_widget(self, parent, index):
        """Виджет для управления одним звуком"""
        frame = ttk.Frame(parent, style="Card.TFrame", padding=8)
        frame.pack(fill="x", pady=3)
        frame.index = index  # Сохраняем индекс для обработки событий

        # Цветной индикатор
        color_canvas = tk.Canvas(frame, width=25, height=25, bg=self.get_color_for_sound(index),
                                 highlightthickness=0, bd=0)
        color_canvas.pack(side="left", padx=(0, 10))
        color_canvas.create_text(12, 12, text=str(index + 1), fill="white",
                                 font=('Arial', 10, 'bold'))

        # Кнопка воспроизведения
        ttk.Button(frame, text="▶", width=2,
                   command=lambda idx=index: self.play_sound(idx)).pack(side="left", padx=2)

        # Поле имени
        self.sound_name_vars[index].set(self.sound_manager.get_sound_name(index))
        entry = ttk.Entry(frame, textvariable=self.sound_name_vars[index], width=15, font=self.small_font)
        entry.pack(side="left", padx=5, fill="x", expand=True)
        entry.bind("<FocusOut>", lambda e, idx=index: self.rename_sound(idx, self.sound_name_vars[idx].get()))

        # Кнопка загрузки
        ttk.Button(frame, text="📁", width=2,
                   command=lambda idx=index: self.load_sound(idx)).pack(side="left", padx=2)

        # Кнопка открытия браузера звуков
        ttk.Button(frame, text="🎵", width=2,
                   command=lambda idx=index: self.open_sound_browser(idx)).pack(side="left", padx=2)

    def setup_beat_grid_panel(self, parent):
        """Панель сетки битов"""
        grid_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        grid_card.pack(fill="both", expand=True)

        tk.Label(grid_card, text="🥁 Сетка битов", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        self.beat_canvas = tk.Canvas(grid_card, bg=self.card_color, highlightthickness=0)
        self.beat_canvas.pack(fill="both", expand=True)

        self.beat_canvas.bind("<Configure>", lambda e: self.update_beat_grid())
        self.beat_canvas.bind("<Button-1>", self.on_beat_grid_click)
        self.beat_canvas.bind("<B1-Motion>", self.on_beat_grid_drag)
        self.beat_canvas.bind("<ButtonRelease-1>", self.on_beat_grid_release)
        self.beat_canvas.bind("<Button-3>", self.on_beat_grid_right_click)
        self.beat_canvas.bind("<B3-Motion>", self.on_beat_grid_right_drag)

    def setup_control_panel(self, parent):
        """Панель управления воспроизведением"""
        control_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        control_card.pack(fill="x", pady=(15, 0))

        # BPM слайдер
        bpm_frame = ttk.Frame(control_card, style="Card.TFrame")
        bpm_frame.pack(fill="x", pady=5)

        self.bpm_label = tk.Label(bpm_frame, text=f"BPM: {self.functions.bpm}", font=self.app_font,
                                  fg=self.text_color, bg=self.card_color)
        self.bpm_label.pack(side="left")

        ttk.Scale(bpm_frame, from_=60, to=240, orient="horizontal",
                  command=self.update_bpm).pack(side="left", fill="x", expand=True, padx=10)

        # Кнопки управления
        button_frame = ttk.Frame(control_card, style="Card.TFrame")
        button_frame.pack(fill="x", pady=5)

        self.play_btn = ttk.Button(button_frame, text="▶️ Воспроизведение", command=self.toggle_playback,
                                   style="Accent.TButton")
        self.play_btn.pack(side="left", padx=5)

        self.record_btn = ttk.Button(button_frame, text="🔴 Запись", command=self.toggle_recording,
                                     style="TButton")
        self.record_btn.pack(side="left", padx=5)

        ttk.Button(button_frame, text="🗑️ Очистить", command=self.clear_all,
                   style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="💾 Экспорт", command=self.export_pattern,
                   style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="📥 Импорт", command=self.import_pattern,
                   style="TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="🎲 Случайно", command=self.generate_random_pattern,
                   style="TButton").pack(side="left", padx=5)

    def setup_status_bar(self, parent):
        """Статус бар"""
        status_frame = ttk.Frame(parent, style="Card.TFrame", padding=10)
        status_frame.pack(fill="x", pady=(15, 0))

        self.status_text = tk.StringVar(value="Готово")
        tk.Label(status_frame, textvariable=self.status_text, font=self.small_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

    def bind_events(self):
        """Привязка событий"""
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

    def set_tool(self, tool):
        """Установить текущий инструмент"""
        self.current_tool = tool
        self.status_text.set(f"Выбран инструмент: {tool}")

    def get_color_for_sound(self, index):
        """Получить цвет для звука"""
        colors = [
            "#ef4444", "#f59e0b", "#10b981", "#3b82f6",
            "#8b5cf6", "#ec4899", "#6b7280", "#f97316",
            "#14b8a6", "#0ea5e9", "#a855f7", "#f43f5e",
            "#84cc16", "#6366f1", "#d946ef", "#22d3ee"
        ]
        return colors[index % len(colors)]

    def update_beat_grid(self):
        """Обновить сетку битов"""
        self.beat_canvas.delete("all")
        width = self.beat_canvas.winfo_width()
        height = self.beat_canvas.winfo_height()

        rows = cols = self.functions.grid_size
        cell_width = width / cols
        cell_height = height / rows

        # Рисуем сетку
        for i in range(rows):
            for j in range(cols):
                x1 = j * cell_width
                y1 = i * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height

                fill_color = self.get_color_for_sound(i) if self.functions.beat_matrix[i, j] else self.bg_color
                outline_color = self.border_color
                if j == self.current_step and self.functions.is_playing:
                    outline_color = self.highlight_color

                self.beat_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=fill_color, outline=outline_color
                )

    def update_playback_position(self, step):
        """Обновить позицию воспроизведения"""
        self.current_step = step
        self.update_beat_grid()

    def on_beat_grid_click(self, event):
        """Обработка клика по сетке битов"""
        if not self.functions.is_playing:
            width = self.beat_canvas.winfo_width()
            height = self.beat_canvas.winfo_height()

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
                elif self.current_tool == "record":
                    if hasattr(self, 'record_sound_index') and self.record_sound_index is not None:
                        self.functions.toggle_cell(row, col, True)
                self.update_beat_grid()
                self.last_cell = (row, col)
                self.dragging = True

    def on_beat_grid_right_click(self, event):
        """Handle right click on beat grid - удаление"""
        if not self.functions.is_playing:
            width = self.beat_canvas.winfo_width()
            height = self.beat_canvas.winfo_height()

            rows = cols = self.functions.grid_size
            cell_width = width / cols
            cell_height = height / rows

            col = int(event.x / cell_width)
            row = int(event.y / cell_height)

            if 0 <= row < rows and 0 <= col < cols:
                self.functions.toggle_cell(row, col, False)
                self.update_beat_grid()
                self.last_cell = (row, col)
                self.dragging = True

    def on_beat_grid_right_drag(self, event):
        """Handle right drag on beat grid - удаление с перетаскиванием"""
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
                self.functions.toggle_cell(row, col, False)
                self.update_beat_grid()
                self.last_cell = (row, col)

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
                elif self.current_tool == "record":
                    if hasattr(self, 'record_sound_index') and self.record_sound_index is not None:
                        self.functions.toggle_cell(row, col, True)

                self.update_beat_grid()
                self.last_cell = (row, col)

    def on_beat_grid_release(self, event):
        """Handle mouse release on beat grid"""
        self.dragging = False
        self.last_cell = None

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

    def toggle_recording(self):
        """Toggle recording"""
        self.recording = not self.recording
        if self.recording:
            self.record_btn.config(text="⏹️ Стоп запись", style="Record.TButton")
            self.status_text.set("Запись включена - выберите звук и играйте!")
            # Если воспроизведение не запущено, запускаем его
            if not self.functions.is_playing:
                self.toggle_playback()
        else:
            self.record_btn.config(text="🔴 Запись", style="TButton")
            self.status_text.set("Запись остановлена")
            self.recorded_steps.clear()

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

    def import_pattern(self):
        """Import pattern from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            if self.functions.import_json(file_path):
                self.update_beat_grid()
                self.update_bpm_display()
                self.status_text.set(f"Паттерн импортирован: {os.path.basename(file_path)}")
            else:
                self.status_text.set("Ошибка импорта")

    def generate_random_pattern(self):
        """Generate random pattern"""
        self.functions.generate_random_pattern()
        self.update_beat_grid()
        self.status_text.set("Сгенерирован случайный паттерн")

    def play_sound(self, index):
        """Play sound by index"""
        self.sound_manager.play_sound(index)
        self.status_text.set(f"Воспроизведение: {self.sound_manager.get_sound_name(index)}")

        # Если режим записи активен, устанавливаем этот звук для записи
        if self.current_tool == "record":
            self.record_sound_index = index
            self.status_text.set(f"Выбран звук для записи: {self.sound_manager.get_sound_name(index)}")

    def rename_sound(self, index, name):
        """Rename sound"""
        self.sound_manager.set_sound_name(index, name)
        self.sound_name_vars[index].set(name)
        self.status_text.set(f"Звук переименован: {name}")

    def load_sound(self, index):
        """Load sound from file"""
        self.current_sound_slot = index
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio files", "*.wav *.mp3 *.ogg *.flac"), ("All files", "*.*")]
        )
        if file_path:
            if self.sound_manager.load_sound(index, file_path):
                sound_name = os.path.splitext(os.path.basename(file_path))[0]
                self.sound_manager.set_sound_name(index, sound_name)
                self.sound_name_vars[index].set(sound_name)
                self.status_text.set(f"Звук загружен: {os.path.basename(file_path)}")
                self.update_sound_widgets()
            else:
                self.status_text.set("Ошибка загрузки звука")

    def open_sound_browser(self, index=None):
        """Open sound browser for a specific slot"""
        def on_sound_selected(sound_name, file_path):
            if index is not None and file_path:
                if self.sound_manager.load_sound(index, file_path):
                    self.sound_manager.set_sound_name(index, sound_name)
                    self.sound_name_vars[index].set(sound_name)
                    self.status_text.set(f"Звук загружен для слота {index + 1}: {sound_name}")
                    self.update_sound_widgets()
                else:
                    self.status_text.set("Ошибка загрузки звука")

        SoundBrowser(self.root, self.sound_manager, on_sound_selected, slot_index=index)

    def update_sound_widgets(self):
        """Update sound widgets"""
        for widget in self.sound_frame.winfo_children():
            if hasattr(widget, 'index'):
                index = widget.index
                self.sound_name_vars[index].set(self.sound_manager.get_sound_name(index))

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
                if 0 <= row < self.functions.grid_size and 0 <= col < self.functions.grid_size:
                    self.functions.toggle_cell(row, col, True)
            self.update_beat_grid()
            self.status_text.set(f"Вставлено {len(self.clipboard)} ячеек")
        else:
            self.status_text.set("Буфер обмена пуст")

    def shift_right(self):
        """Shift pattern to the right"""
        self.functions.shift_right()
        self.update_beat_grid()
        self.status_text.set("Паттерн сдвинут вправо")

    def on_mousewheel(self, event):
        """Обработка прокрутки колесиком мыши"""
        if event.widget.winfo_class() == 'Canvas':
            event.widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def on_resize(self):
        """Handle window resize"""
        self.update_beat_grid()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def on_closing(self):
        """Handle window closing"""
        self.functions.stop_playback()
        self.save_config()
        self.root.destroy()

    def save_config(self):
        """Save configuration"""
        config = {
            'bpm': self.functions.bpm,
            'grid_size': self.functions.grid_size,
            'sound_names': self.sound_manager.sound_names,
            'sound_files': self.sound_manager.sound_files
        }
        try:
            with open('config.json', 'w') as f:
                json.dump(config, f)
        except:
            pass

    def load_config(self):
        """Load configuration"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    self.functions.bpm = config.get('bpm', 120)
                    self.functions.grid_size = config.get('grid_size', 16)
                    self.sound_manager.sound_names = config.get('sound_names', [f"Sound {i + 1}" for i in range(16)])
                    self.sound_manager.sound_files = config.get('sound_files', [""] * 16)
                    for i in range(16):
                        self.sound_name_vars[i].set(self.sound_manager.get_sound_name(i))
        except:
            pass

    def undo(self):
        """Undo last action"""
        messagebox.showinfo("Undo", "Функция отмены будет реализована в будущих версиях")

    def redo(self):
        """Redo last action"""
        messagebox.showinfo("Redo", "Функция повтора будет реализована в будущих версиях")


def main():
    root = tk.Tk()
    root.title("Newton Flow Pro - Beat Sequencer")
    root.geometry("1400x900")
    root.minsize(1200, 800)

    app = BeatPadGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()