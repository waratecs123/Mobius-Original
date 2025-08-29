import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import json
import os
from functions import BeatPadFunctions
from sound_manager import SoundManager


class BeatPadGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Newton Flow Beat Pad")

        # Устанавливаем полноэкранный режим
        self.root.attributes('-fullscreen', True)

        # Добавляем кнопку выхода из полноэкранного режима (F11 или ESC)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # Устанавливаем минимальный размер окна
        self.root.minsize(1000, 700)

        # Стиль Newton Flow (тёмная тема с акцентами)
        self.bg_color = "#0a0a0a"
        self.card_color = "#1e1e1e"
        self.accent_color = "#8844FF"
        self.text_color = "#f0f0f0"
        self.secondary_text = "#909090"
        self.border_color = "#2a2a2a"

        # Устанавливаем цвет фона корневого окна
        self.root.configure(bg=self.bg_color)

        # Шрифты
        self.title_font = ('Segoe UI', 18, 'bold')
        self.subtitle_font = ('Segoe UI', 12, 'bold')
        self.app_font = ('Segoe UI', 10)
        self.button_font = ('Segoe UI', 10)

        # Настройка стилей
        self.setup_styles()

        # Инициализация компонентов
        self.sound_manager = SoundManager()
        self.functions = BeatPadFunctions(self.sound_manager)

        # Загрузка конфигурации
        self.load_config()

        # Переменные интерфейса
        self.cell_size = 50
        self.dragging = False
        self.last_cell = None
        self.fullscreen = True

        # Создание интерфейса
        self.setup_ui()

        # Привязка событий
        self.bind_events()

        # Обновление интерфейса
        self.update_beat_grid()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        return "break"

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes('-fullscreen', False)
        return "break"

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Основные стили с явным указанием фона
        style.configure(".",
                        background=self.bg_color,
                        foreground=self.text_color,
                        fieldbackground=self.card_color)

        style.configure("TFrame",
                        background=self.bg_color)

        style.configure("Card.TFrame",
                        background=self.card_color,
                        relief="flat")

        # Стили текста
        style.configure("TLabel",
                        background=self.card_color,
                        foreground=self.text_color,
                        font=self.app_font)

        style.configure("Title.TLabel",
                        font=self.title_font)

        style.configure("Subtitle.TLabel",
                        foreground=self.secondary_text,
                        font=self.subtitle_font)

        # Стили кнопок
        style.configure("TButton",
                        background=self.card_color,
                        foreground=self.text_color,
                        font=self.button_font,
                        borderwidth=0,
                        focuscolor=self.bg_color)

        style.map("TButton",
                  background=[('active', '#252525')],
                  foreground=[('active', self.text_color)])

        # Акцентные кнопки
        style.configure("Accent.TButton",
                        background=self.accent_color,
                        foreground="#ffffff",
                        font=self.button_font,
                        borderwidth=0)

        style.map("Accent.TButton",
                  background=[('active', '#aa66ff')])

        # Поля ввода и комбобоксы
        style.configure("TEntry",
                        fieldbackground="#252525",
                        foreground=self.text_color,
                        borderwidth=1,
                        bordercolor=self.border_color,
                        insertcolor=self.accent_color,
                        padding=5)

        style.configure("TCombobox",
                        fieldbackground="#252525",
                        foreground=self.text_color,
                        selectbackground=self.accent_color,
                        selectforeground="#ffffff",
                        borderwidth=1,
                        bordercolor=self.border_color,
                        padding=5)

        # Слайдеры
        style.configure("Horizontal.TScale",
                        background=self.card_color,
                        troughcolor="#252525",
                        bordercolor=self.border_color)

        # Стиль для Scrollbar
        style.configure("Vertical.TScrollbar",
                        background=self.card_color,
                        troughcolor=self.bg_color,
                        bordercolor=self.border_color)

    def setup_ui(self):
        # Главный контейнер
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        header_frame = ttk.Frame(main_container, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 15))

        # Логотип и название
        logo_frame = ttk.Frame(header_frame, style="TFrame")
        logo_frame.pack(side="left")

        logo_canvas = tk.Canvas(logo_frame, bg=self.bg_color, width=40, height=40,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")
        logo_canvas.create_oval(5, 5, 35, 35, fill=self.accent_color, outline="")
        logo_canvas.create_text(20, 20, text="N", font=('Segoe UI', 16, 'bold'), fill="#ffffff")

        tk.Label(logo_frame, text="NEWTON FLOW", font=self.title_font,
                 bg=self.bg_color, fg=self.text_color).pack(side="left", padx=10)

        # Кнопка выхода из полноэкранного режима
        exit_fullscreen_btn = ttk.Button(header_frame, text="⛶",
                                         command=self.exit_fullscreen,
                                         style="TButton", width=3)
        exit_fullscreen_btn.pack(side="right")

        # Основной контент
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(fill="both", expand=True)

        # Левая панель - управление
        left_panel = ttk.Frame(content_frame, style="TFrame", width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        left_panel.pack_propagate(False)

        # Правая панель - beat grid
        right_panel = ttk.Frame(content_frame, style="TFrame")
        right_panel.pack(side="right", fill="both", expand=True)

        # Заполняем левую панель
        self.setup_control_panel(left_panel)

        # Заполняем правую панель
        self.setup_beat_grid_panel(right_panel)

        # Нижняя панель - статус
        status_frame = ttk.Frame(main_container, style="Card.TFrame", padding=10)
        status_frame.pack(fill="x", pady=(15, 0))

        self.status_text = tk.StringVar(value="Готов к созданию битов! Кликайте по сетке чтобы добавить/удалить звуки")
        status_label = tk.Label(status_frame, textvariable=self.status_text,
                                font=self.app_font, fg=self.secondary_text, bg=self.card_color)
        status_label.pack(fill="x")

    def setup_control_panel(self, parent):
        # Управление воспроизведением
        control_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        control_card.pack(fill="x", pady=(0, 15))

        tk.Label(control_card, text="Управление", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        # Кнопки управления
        btn_frame = ttk.Frame(control_card, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=5)

        self.play_btn = ttk.Button(btn_frame, text="▶️ Воспроизведение", style="Accent.TButton",
                                   command=self.toggle_playback)
        self.play_btn.pack(fill="x", pady=2)

        ttk.Button(btn_frame, text="🗑️ Очистить всё", style="TButton",
                   command=self.clear_all).pack(fill="x", pady=2)

        ttk.Button(btn_frame, text="💾 Экспорт", style="TButton",
                   command=self.export_pattern).pack(fill="x", pady=2)

        # Настройки BPM
        bpm_frame = ttk.Frame(control_card, style="Card.TFrame")
        bpm_frame.pack(fill="x", pady=(10, 0))

        tk.Label(bpm_frame, text="BPM:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.bpm_var = tk.IntVar(value=self.functions.bpm)
        bpm_scale = ttk.Scale(bpm_frame, from_=60, to=240, orient=tk.HORIZONTAL,
                              variable=self.bpm_var, style="Horizontal.TScale")
        bpm_scale.pack(fill="x", pady=5)
        bpm_scale.bind("<Motion>", lambda e: self.update_bpm())

        bpm_value = tk.Label(bpm_frame, textvariable=self.bpm_var, font=self.app_font,
                             fg=self.text_color, bg=self.card_color)
        bpm_value.pack(anchor="e")

        # Настройки сетки
        grid_frame = ttk.Frame(control_card, style="Card.TFrame")
        grid_frame.pack(fill="x", pady=(10, 0))

        tk.Label(grid_frame, text="Размер сетки:", font=self.app_font,
                 fg=self.secondary_text, bg=self.card_color).pack(anchor="w")

        self.grid_var = tk.StringVar(value="4x4")
        grid_combo = ttk.Combobox(grid_frame, textvariable=self.grid_var,
                                  values=["4x4", "8x8", "16x16"], state="readonly")
        grid_combo.pack(fill="x", pady=5)
        grid_combo.bind("<<ComboboxSelected>>", self.change_grid_size)

        # Панель управления звуками
        sound_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        sound_card.pack(fill="both", expand=True, pady=(0, 15))

        tk.Label(sound_card, text="Управление звуками", font=self.subtitle_font,
                 fg=self.text_color, bg=self.card_color).pack(anchor="w", pady=(0, 10))

        # Контейнер для списка звуков с прокруткой
        sound_container = ttk.Frame(sound_card, style="Card.TFrame")
        sound_container.pack(fill="both", expand=True)

        # Canvas для прокрутки
        self.sound_canvas = tk.Canvas(sound_container, bg=self.card_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(sound_container, orient="vertical", command=self.sound_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.sound_canvas, style="Card.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.sound_canvas.configure(scrollregion=self.sound_canvas.bbox("all"))
        )

        self.sound_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.sound_canvas.configure(yscrollcommand=scrollbar.set)

        self.sound_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Заполняем список звуков
        self.setup_sound_list()

    def setup_sound_list(self):
        # Очищаем текущий список
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Добавляем элементы управления для каждого звука
        for i in range(16):
            sound_frame = ttk.Frame(self.scrollable_frame, style="Card.TFrame", padding=5)
            sound_frame.pack(fill="x", pady=2)

            # Цветной индикатор
            color_indicator = tk.Canvas(sound_frame, width=20, height=20,
                                        bg=self.get_color_for_sound(i), highlightthickness=0)
            color_indicator.pack(side="left", padx=(0, 10))
            color_indicator.create_text(10, 10, text=str(i + 1), fill="white",
                                        font=('Arial', 10, 'bold'))

            # Кнопка воспроизведения
            play_btn = ttk.Button(sound_frame, text="▶", width=2,
                                  command=lambda idx=i: self.play_sound(idx))
            play_btn.pack(side="left", padx=2)

            # Поле для имени звука
            name_var = tk.StringVar(value=self.sound_manager.get_sound_name(i))
            name_entry = ttk.Entry(sound_frame, textvariable=name_var, width=15)
            name_entry.pack(side="left", padx=5, fill="x", expand=True)
            name_entry.bind("<FocusOut>", lambda e, idx=i, var=name_var: self.rename_sound(idx, var.get()))

            # Кнопка загрузки звука
            load_btn = ttk.Button(sound_frame, text="📁", width=2,
                                  command=lambda idx=i: self.load_sound(idx))
            load_btn.pack(side="left", padx=2)

            # Метка имени файла
            file_name = self.sound_manager.get_sound_file_name(i)
            file_label = tk.Label(sound_frame, text=file_name, font=('Arial', 8),
                                  fg=self.secondary_text, bg=self.card_color, width=15)
            file_label.pack(side="left", padx=5)

            # Привязываем правый клик для перезаписи звука
            sound_frame.bind("<Button-3>", lambda e, idx=i: self.load_sound(idx))
            for child in sound_frame.winfo_children():
                child.bind("<Button-3>", lambda e, idx=i: self.load_sound(idx))

    def setup_beat_grid_panel(self, parent):
        beat_card = ttk.Frame(parent, style="Card.TFrame", padding=1)
        beat_card.pack(fill="both", expand=True)

        # Создаем canvas для beat grid
        self.beat_canvas = tk.Canvas(beat_card, bg=self.card_color, highlightthickness=0)
        self.beat_canvas.pack(fill="both", expand=True)

        # Привязываем события мыши
        self.beat_canvas.bind("<Button-1>", self.on_beat_grid_click)
        self.beat_canvas.bind("<B1-Motion>", self.on_beat_grid_drag)
        self.beat_canvas.bind("<ButtonRelease-1>", self.on_beat_grid_release)
        self.beat_canvas.bind("<Button-3>", self.on_beat_grid_right_click)

    def bind_events(self):
        # Глобальные горячие клавиши
        self.root.bind("<space>", lambda e: self.toggle_playback())
        self.root.bind("<Delete>", lambda e: self.clear_all())
        self.root.bind("<Control-s>", lambda e: self.export_pattern())

        # Обработка изменения размера окна
        self.root.bind("<Configure>", self.on_resize)

    def update_beat_grid(self):
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
            self.beat_canvas.create_line(0, y, width, y, fill=self.border_color)

        for j in range(cols + 1):
            x = j * cell_width
            self.beat_canvas.create_line(x, 0, x, height, fill=self.border_color)

        # Рисуем активные ячейки
        for i in range(rows):
            for j in range(cols):
                if self.functions.beat_matrix[i, j]:
                    x1 = j * cell_width
                    y1 = i * cell_height
                    x2 = x1 + cell_width
                    y2 = y1 + cell_height

                    color = self.get_color_for_sound(j)
                    self.beat_canvas.create_rectangle(x1, y1, x2, y2,
                                                      fill=color, outline="")

                    # Номер звука
                    self.beat_canvas.create_text(x1 + cell_width / 2, y1 + cell_height / 2,
                                                 text=str(j + 1), fill="white",
                                                 font=('Arial', 8, 'bold'))

        # Рисуем текущий шаг
        if self.functions.is_playing:
            step_width = width / 16
            x1 = self.functions.current_step * step_width
            x2 = x1 + step_width
            self.beat_canvas.create_rectangle(x1, 0, x2, height,
                                              fill="yellow", stipple="gray25",
                                              outline="red", width=2)

    def get_color_for_sound(self, sound_index):
        colors = [
            '#e74c3c', '#3498db', '#2ecc71', '#f39c12',
            '#9b59b6', '#1abc9c', '#d35400', '#27ae60',
            '#8e44ad', '#f1c40f', '#e67e22', '#16a085',
            '#c0392b', '#2980b9', '#27ae60', '#d35400'
        ]
        return colors[sound_index % len(colors)]

    def on_beat_grid_click(self, event):
        x, y = event.x, event.y
        width = self.beat_canvas.winfo_width()
        height = self.beat_canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        col = int(x / width * self.functions.grid_size)
        row = int(y / height * self.functions.grid_size)

        self.functions.toggle_cell(row, col)
        self.last_cell = (row, col)
        self.update_beat_grid()

    def on_beat_grid_drag(self, event):
        x, y = event.x, event.y
        width = self.beat_canvas.winfo_width()
        height = self.beat_canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        col = int(x / width * self.functions.grid_size)
        row = int(y / height * self.functions.grid_size)

        if (row, col) != self.last_cell:
            self.functions.toggle_cell(row, col)
            self.last_cell = (row, col)
            self.update_beat_grid()

    def on_beat_grid_release(self, event):
        self.last_cell = None

    def on_beat_grid_right_click(self, event):
        # Правый клик для быстрой загрузки звука
        x, y = event.x, event.y
        width = self.beat_canvas.winfo_width()
        height = self.beat_canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        col = int(x / width * self.functions.grid_size)
        self.load_sound(col)

    def on_resize(self, event):
        if event.widget == self.root:
            self.update_beat_grid()

    def toggle_playback(self):
        if self.functions.toggle_playback():
            self.play_btn.config(text="⏸️ Пауза")
            self.status_text.set("Воспроизведение...")
        else:
            self.play_btn.config(text="▶️ Воспроизведение")
            self.status_text.set("Остановлено")
        self.update_beat_grid()

    def clear_all(self):
        self.functions.clear_all()
        self.update_beat_grid()
        self.status_text.set("Все биты очищены!")

    def update_bpm(self):
        self.functions.bpm = self.bpm_var.get()

    def change_grid_size(self, event):
        self.functions.change_grid_size(self.grid_var.get())
        self.update_beat_grid()

    def play_sound(self, index):
        self.sound_manager.play_sound(index)

    def load_sound(self, index):
        file_path = filedialog.askopenfilename(
            title="Выберите звуковой файл",
            filetypes=[("Audio files", "*.wav *.mp3 *.ogg"), ("All files", "*.*")]
        )

        if file_path:
            if self.sound_manager.load_sound(index, file_path):
                self.setup_sound_list()  # Обновляем список звуков
                self.status_text.set(f"Звук {index + 1} загружен: {os.path.basename(file_path)}")
                self.save_config()
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить звуковой файл")

    def rename_sound(self, index, name):
        self.sound_manager.set_sound_name(index, name)
        self.save_config()
        self.status_text.set(f"Звук {index + 1} переименован в: {name}")

    def export_pattern(self):
        export_window = tk.Toplevel(self.root)
        export_window.title("Экспорт паттерна")
        export_window.geometry("300x200")
        export_window.resizable(False, False)
        export_window.transient(self.root)
        export_window.grab_set()

        # Устанавливаем темную тему для дочернего окна
        export_window.configure(bg=self.bg_color)

        ttk.Label(export_window, text="Выберите формат экспорта:").pack(pady=10)

        format_var = tk.StringVar(value="JSON")

        format_frame = ttk.Frame(export_window)
        format_frame.pack(pady=10)

        ttk.Radiobutton(format_frame, text="JSON", variable=format_var, value="JSON").pack(anchor=tk.W)
        ttk.Radiobutton(format_frame, text="CSV", variable=format_var, value="CSV").pack(anchor=tk.W)
        ttk.Radiobutton(format_frame, text="TXT", variable=format_var, value="TXT").pack(anchor=tk.W)

        def do_export():
            format_type = format_var.get()
            file_path = filedialog.asksaveasfilename(
                defaultextension=f".{format_type.lower()}",
                filetypes=[(f"{format_type} files", f"*.{format_type.lower()}")]
            )

            if file_path:
                try:
                    if format_type == "JSON":
                        self.functions.export_json(file_path)
                    elif format_type == "CSV":
                        self.functions.export_csv(file_path)
                    else:
                        self.functions.export_txt(file_path)

                    messagebox.showinfo("Успех", f"Паттерн экспортирован в {file_path}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось экспортировать: {str(e)}")

            export_window.destroy()

        ttk.Button(export_window, text="Экспорт", command=do_export).pack(pady=10)

    def load_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    self.functions.load_config(config)
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        try:
            with open("config.json", "w") as f:
                json.dump(self.functions.get_config(), f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def on_closing(self):
        self.save_config()
        self.root.destroy()


# Для запуска приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = BeatPadGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()