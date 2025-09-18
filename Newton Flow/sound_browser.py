import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pygame


class SoundBrowser:
    def __init__(self, parent, sound_manager, on_sound_selected, slot_index=None):
        self.parent = parent
        self.sound_manager = sound_manager
        self.on_sound_selected = on_sound_selected
        self.slot_index = slot_index
        self.selected_sound_name = None
        self.selected_file_path = None

        self.setup_ui()

    def setup_ui(self):
        """Создание интерфейса браузера звуков"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Браузер звуков - Newton Flow")
        self.window.geometry("800x600")
        self.window.configure(bg="#0f0f23")

        # Главный фрейм
        main_frame = ttk.Frame(self.window, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        header = ttk.Frame(main_frame, style="TFrame")
        header.pack(fill="x", pady=(0, 20))

        tk.Label(header, text="🎵 Браузер звуков", font=('Arial', 16, 'bold'),
                 fg="#6366f1", bg="#0f0f23").pack(side="left")

        # Поиск
        search_frame = ttk.Frame(header, style="TFrame")
        search_frame.pack(side="right")

        tk.Label(search_frame, text="Поиск:", fg="#e2e8f0", bg="#0f0f23").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self.on_search)

        # Категории и звуки
        content_frame = ttk.Frame(main_frame, style="TFrame")
        content_frame.pack(fill="both", expand=True)

        # Левая панель - категории
        category_frame = ttk.Frame(content_frame, style="Card.TFrame", width=200)
        category_frame.pack(side="left", fill="y", padx=(0, 15))
        category_frame.pack_propagate(False)

        tk.Label(category_frame, text="Категории", font=('Arial', 12, 'bold'),
                 fg="#e2e8f0", bg="#1a1a2e").pack(pady=10)

        # Добавляем прокрутку для категорий
        category_canvas = tk.Canvas(category_frame, bg="#1a1a2e", highlightthickness=0)
        category_scrollbar = ttk.Scrollbar(category_frame, orient="vertical", command=category_canvas.yview)
        category_scrollable_frame = ttk.Frame(category_canvas, style="Card.TFrame")

        category_scrollable_frame.bind(
            "<Configure>",
            lambda e: category_canvas.configure(scrollregion=category_canvas.bbox("all"))
        )

        category_canvas.create_window((0, 0), window=category_scrollable_frame, anchor="nw")
        category_canvas.configure(yscrollcommand=category_scrollbar.set)

        category_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        category_scrollbar.pack(side="right", fill="y")

        self.category_listbox = tk.Listbox(category_scrollable_frame, bg="#1a1a2e", fg="#e2e8f0",
                                           selectbackground="#6366f1", font=('Arial', 10), height=15)
        self.category_listbox.pack(fill="both", expand=True)
        self.category_listbox.bind("<<ListboxSelect>>", self.on_category_select)

        # Правая панель - звуки
        sound_frame = ttk.Frame(content_frame, style="Card.TFrame")
        sound_frame.pack(side="right", fill="both", expand=True)

        tk.Label(sound_frame, text="Звуки", font=('Arial', 12, 'bold'),
                 fg="#e2e8f0", bg="#1a1a2e").pack(pady=10)

        # Сетка звуков с прокруткой
        sound_canvas = tk.Canvas(sound_frame, bg="#1a1a2e", highlightthickness=0)
        sound_scrollbar = ttk.Scrollbar(sound_frame, orient="vertical", command=sound_canvas.yview)
        self.sound_scrollable_frame = ttk.Frame(sound_canvas, style="Card.TFrame")

        self.sound_scrollable_frame.bind(
            "<Configure>",
            lambda e: sound_canvas.configure(scrollregion=sound_canvas.bbox("all"))
        )

        sound_canvas.create_window((0, 0), window=self.sound_scrollable_frame, anchor="nw")
        sound_canvas.configure(yscrollcommand=sound_scrollbar.set)

        sound_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        sound_scrollbar.pack(side="right", fill="y")

        # Привязываем прокрутку колесиком мыши
        category_canvas.bind("<MouseWheel>", self.on_mousewheel)
        category_scrollable_frame.bind("<MouseWheel>", self.on_mousewheel)
        sound_canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.sound_scrollable_frame.bind("<MouseWheel>", self.on_mousewheel)

        # Кнопки управления
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(fill="x", pady=(20, 0))

        ttk.Button(button_frame, text="Загрузить свой звук",
                   command=self.load_custom_sound).pack(side="left", padx=5)

        ttk.Button(button_frame, text="Предпросмотр",
                   command=self.preview_selected).pack(side="left", padx=5)

        ttk.Button(button_frame, text="Выбрать",
                   command=self.select_sound, style="Accent.TButton").pack(side="right", padx=5)

        # Заполняем категории
        self.populate_categories()

    def on_mousewheel(self, event):
        """Обработка прокрутки колесиком мыши"""
        if event.widget.winfo_class() == 'Canvas':
            event.widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def populate_categories(self):
        """Заполняем список категорий"""
        self.category_listbox.delete(0, tk.END)
        categories = list(self.sound_manager.get_sound_categories().keys())
        for category in categories:
            self.category_listbox.insert(tk.END, category)

    def on_category_select(self, event):
        """Обработка выбора категории"""
        if self.category_listbox.curselection():
            category = self.category_listbox.get(self.category_listbox.curselection()[0])
            self.show_sounds_in_category(category)

    def show_sounds_in_category(self, category):
        """Показать звуки в выбранной категории"""
        # Очищаем фрейм
        for widget in self.sound_scrollable_frame.winfo_children():
            widget.destroy()

        sounds = self.sound_manager.get_sounds_in_category(category)

        # Создаем кнопки для каждого звука
        for i, sound_name in enumerate(sounds):
            frame = ttk.Frame(self.sound_scrollable_frame, style="Card.TFrame", padding=5)
            frame.pack(fill="x", pady=2, padx=5)

            # Кнопка предпросмотра
            ttk.Button(frame, text="▶", width=2,
                       command=lambda n=sound_name: self.preview_sound_by_name(n)).pack(side="left", padx=2)

            # Название звука
            label = tk.Label(frame, text=sound_name, font=('Arial', 10),
                             fg="#e2e8f0", bg="#1a1a2e", anchor="w")
            label.pack(side="left", fill="x", expand=True, padx=5)
            label.bind("<Button-1>", lambda e, n=sound_name: self.on_sound_click(n))

            # Кнопка выбора
            ttk.Button(frame, text="Выбрать", width=8,
                       command=lambda n=sound_name: self.on_sound_click(n)).pack(side="right", padx=2)

    def preview_sound_by_name(self, sound_name):
        """Предпросмотр звука по имени"""
        file_path = self.sound_manager.get_sound_file_path(sound_name)
        if file_path and os.path.exists(file_path):
            self.sound_manager.preview_sound(file_path)
        else:
            messagebox.showwarning("Файл не найден",
                                   f"Файл для звука '{sound_name}' не найден в папке sounds/")

    def on_sound_click(self, sound_name):
        """Обработка клика по звуку"""
        self.selected_sound_name = sound_name
        file_path = self.sound_manager.get_sound_file_path(sound_name)
        if file_path and os.path.exists(file_path):
            self.selected_file_path = file_path
        else:
            self.selected_file_path = None
            messagebox.showwarning("Файл не найден",
                                   f"Файл для звука '{sound_name}' не найден в папке sounds/")

    def preview_selected(self):
        """Предпросмотр выбранного звука"""
        if self.selected_sound_name and self.selected_file_path:
            self.sound_manager.preview_sound(self.selected_file_path)
        else:
            messagebox.showinfo("Предпросмотр", f"Выберите звук для предпросмотра")

    def load_custom_sound(self):
        """Загрузка пользовательского звука"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio files", "*.wav *.mp3 *.ogg *.flac"),
                       ("All files", "*.*")]
        )
        if file_path:
            self.selected_sound_name = os.path.splitext(os.path.basename(file_path))[0]
            self.selected_file_path = file_path
            messagebox.showinfo("Успех", f"Звук загружен: {self.selected_sound_name}")

    def select_sound(self):
        """Выбор звука"""
        if self.selected_sound_name and self.selected_file_path:
            self.on_sound_selected(self.selected_sound_name, self.selected_file_path)
            self.window.destroy()
        else:
            messagebox.showwarning("Ошибка", "Выберите звук перед подтверждением")

    def on_search(self, event):
        """Поиск звуков"""
        search_text = self.search_var.get().lower()
        if not search_text:
            # Если поиск пустой, показываем все категории
            self.populate_categories()
            return

        # Фильтруем категории и звуки по поисковому запросу
        categories = self.sound_manager.get_sound_categories()
        filtered_categories = {}

        for category, sounds in categories.items():
            filtered_sounds = [s for s in sounds if search_text in s.lower()]
            if filtered_sounds:
                filtered_categories[category] = filtered_sounds

        # Показываем отфильтрованные результаты
        self.category_listbox.delete(0, tk.END)
        for category in filtered_categories.keys():
            self.category_listbox.insert(tk.END, category)