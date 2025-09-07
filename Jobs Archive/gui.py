# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from functions import JobsArchiveFunctions
import os
import threading
from PIL import Image, ImageTk


class FormatSelectorDialog:
    def __init__(self, parent, formats, bg_color, text_color, accent_color):
        self.parent = parent
        self.formats = formats
        self.bg_color = bg_color
        self.text_color = text_color
        self.accent_color = accent_color
        self.selected_format = None
        self.dialog = None

    def show(self):
        """Показывает диалог выбора формата"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Выбор качества видео")
        self.dialog.configure(bg=self.bg_color)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Центрирование диалога
        dialog_width = 700
        dialog_height = 450
        x = (self.parent.winfo_screenwidth() // 2) - (dialog_width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (dialog_height // 2)
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Фрейм для Treeview
        frame = tk.Frame(self.dialog, bg=self.bg_color, padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        # Создаем Treeview для отображения форматов
        tree = ttk.Treeview(frame, columns=("resolution", "fps", "format", "size", "codec"),
                            show="headings", height=15)

        tree.heading("resolution", text="Разрешение")
        tree.heading("fps", text="FPS")
        tree.heading("format", text="Формат")
        tree.heading("size", text="Размер")
        tree.heading("codec", text="Кодек")

        tree.column("resolution", width=120)
        tree.column("fps", width=60)
        tree.column("format", width=100)
        tree.column("size", width=100)
        tree.column("codec", width=120)

        # Заполняем данными
        for fmt in self.formats:
            if fmt.get('vcodec') != 'none':  # Только видео форматы
                resolution = f"{fmt.get('width', 'N/A')}x{fmt.get('height', 'N/A')}"
                fps = fmt.get('fps', 'N/A')
                format_note = fmt.get('format_note', 'N/A')
                filesize = f"{fmt.get('filesize', 0) / (1024 * 1024):.1f}MB" if fmt.get('filesize') else 'N/A'
                codec = f"{fmt.get('vcodec', 'N/A')}/{fmt.get('acodec', 'N/A')}"

                tree.insert("", "end", values=(resolution, fps, format_note, filesize, codec, fmt))

        def on_select():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                self.selected_format = item['values'][-1]  # Сохраняем выбранный формат

        def on_double_click(event):
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                self.selected_format = item['values'][-1]
                self.dialog.destroy()

        def on_ok():
            on_select()
            self.dialog.destroy()

        tree.bind('<Double-1>', on_double_click)

        # Скроллбары
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Размещение
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Кнопки
        btn_frame = tk.Frame(self.dialog, bg=self.bg_color, pady=15)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Отмена", command=self.dialog.destroy,
                  bg="#2d3748", fg=self.text_color, font=('Arial', 11),
                  bd=0, padx=20, pady=8).pack(side="right", padx=(10, 0))

        tk.Button(btn_frame, text="Выбрать", command=on_ok,
                  bg=self.accent_color, fg="#ffffff", font=('Arial', 11),
                  bd=0, padx=20, pady=8).pack(side="right")

        self.dialog.wait_window()
        return self.selected_format


class JobsArchiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jobs Archive")

        # Полноэкранный режим
        self.fullscreen = True
        self.root.attributes('-fullscreen', self.fullscreen)

        # Блокируем клавиши для выхода из полноэкранного режима
        self.root.bind('<Escape>', lambda e: None)
        self.root.bind('<F11>', lambda e: None)

        # Темная цветовая палитра в стиле Fibonacci Scan
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#2d3748"

        # Шрифты
        self.title_font = ('Arial', 24, 'bold')
        self.app_font = ('Arial', 14)
        self.button_font = ('Arial', 13)
        self.small_font = ('Arial', 12)

        # Создаем папку для загрузок
        os.makedirs("downloads", exist_ok=True)

        # Переменные для прокси
        self.proxy_var = tk.StringVar(value="")
        self.quality_var = tk.StringVar(value="best")
        self.audio_var = tk.BooleanVar(value=False)
        self.out_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))

        # Инициализируем backend после настройки GUI
        self.functions = JobsArchiveFunctions(self)

        self.setup_ui()
        self.setup_styles()

        # Устанавливаем фокус на поле ввода при запуске
        self.root.after(100, self.focus_url_entry)

    def setup_styles(self):
        # Стили для виджетов
        style = ttk.Style()
        style.theme_use('clam')

        # Настройка стилей
        style.configure('Treeview',
                        background=self.card_color,
                        fieldbackground=self.card_color,
                        foreground=self.text_color,
                        borderwidth=0,
                        font=self.small_font)
        style.configure('Treeview.Heading',
                        background="#0f0f23",
                        foreground=self.text_color,
                        relief="flat",
                        font=('Arial', 12, 'bold'))
        style.map('Treeview',
                  background=[('selected', '#333333')])

        # Стиль для кнопок
        style.configure('Accent.TButton',
                        background=self.accent_color,
                        foreground='white',
                        borderwidth=0,
                        font=self.button_font)
        style.map('Accent.TButton',
                  background=[('active', '#4f46e5')])

        style.configure('Secondary.TButton',
                        background='#2d3748',
                        foreground=self.text_color,
                        borderwidth=0,
                        font=self.button_font)
        style.map('Secondary.TButton',
                  background=[('active', '#374151')])

    def focus_url_entry(self):
        """Устанавливает фокус на поле ввода URL"""
        self.url_entry.focus_set()

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)

        # Главный контейнер
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Заголовок
        header_frame = tk.Frame(main_container, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 30))

        tk.Label(header_frame, text="JOBS ARCHIVE", bg=self.bg_color,
                 fg=self.accent_color, font=self.title_font).pack(side="left")


        # Поле ввода URL
        input_frame = tk.Frame(main_container, bg=self.card_color, padx=25, pady=25)
        input_frame.pack(fill="x", pady=(0, 25))

        tk.Label(input_frame, text="Введите URL видео (YouTube, TikTok, VK, Rutube, Dailymotion, Bilibili, Instagram):",
                 bg=self.card_color, fg=self.text_color, font=self.app_font).pack(anchor="w", pady=(0, 15))

        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(input_frame, textvariable=self.url_var, bg="#0f0f23", fg=self.text_color,
                                  font=self.app_font, insertbackground=self.text_color,
                                  relief="flat", highlightthickness=1,
                                  highlightcolor=self.accent_color, highlightbackground=self.border_color)
        self.url_entry.pack(fill="x", pady=10, ipady=8)
        self.url_entry.bind("<Return>", lambda e: self.functions.start_download())

        # Добавляем подсказку в поле ввода
        self.url_entry.insert(0, "Вставьте ссылку на видео здесь...")
        self.url_entry.config(fg=self.secondary_text)

        # Включаем стандартные горячие клавиши для работы с текстом
        self.enable_text_editing(self.url_entry)

        # Качество
        tk.Label(input_frame, text="Качество:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w", pady=(15, 5))

        quality_frame = tk.Frame(input_frame, bg=self.card_color)
        quality_frame.pack(fill="x", pady=5)

        quality_box = ttk.Combobox(
            quality_frame, textvariable=self.quality_var,
            values=["best", "4320p", "2160p", "1440p", "1080p", "720p"],
            state="readonly"
        )
        quality_box.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Только аудио
        audio_check = tk.Checkbutton(quality_frame, text="Только аудио", variable=self.audio_var,
                                     bg=self.card_color, fg=self.text_color, selectcolor="#0f0f23",
                                     font=self.app_font)
        audio_check.pack(side="right")

        # Папка сохранения
        tk.Label(input_frame, text="Папка для сохранения:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w", pady=(15, 5))

        dir_frame = tk.Frame(input_frame, bg=self.card_color)
        dir_frame.pack(fill="x", pady=5)

        self.out_dir_entry = tk.Entry(dir_frame, textvariable=self.out_dir_var, bg="#0f0f23", fg=self.text_color,
                                      font=self.app_font, insertbackground=self.text_color,
                                      relief="flat", highlightthickness=1,
                                      highlightcolor=self.accent_color, highlightbackground=self.border_color)
        self.out_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = tk.Button(dir_frame, text="Обзор", font=self.button_font,
                               bg="#2d3748", fg=self.text_color, bd=0, activebackground="#374151",
                               padx=15, pady=8, command=self.functions.choose_dir)
        browse_btn.pack(side="right")

        # Поле для прокси
        tk.Label(input_frame, text="Прокси (если нужен, напр. http://127.0.0.1:8080):",
                 bg=self.card_color, fg=self.text_color, font=self.app_font).pack(anchor="w", pady=(15, 5))

        self.proxy_entry = tk.Entry(input_frame, textvariable=self.proxy_var, bg="#0f0f23", fg=self.text_color,
                                    font=self.app_font, insertbackground=self.text_color,
                                    relief="flat", highlightthickness=1,
                                    highlightcolor=self.accent_color, highlightbackground=self.border_color)
        self.proxy_entry.pack(fill="x", pady=5, ipady=8)

        # Включаем стандартные горячие клавиши для работы с текстом
        self.enable_text_editing(self.proxy_entry)

        def on_entry_click(event):
            if self.url_entry.get() == "Вставьте ссылку на видео здесь...":
                self.url_entry.delete(0, "end")
                self.url_entry.config(fg=self.text_color)

        def on_focusout(event):
            if self.url_entry.get() == '':
                self.url_entry.insert(0, "Вставьте ссылку на видео здесь...")
                self.url_entry.config(fg=self.secondary_text)

        self.url_entry.bind('<FocusIn>', on_entry_click)
        self.url_entry.bind('<FocusOut>', on_focusout)

        # Кнопки управления
        btn_frame = tk.Frame(input_frame, bg=self.card_color)
        btn_frame.pack(fill="x", pady=(20, 0))

        tk.Button(btn_frame, text="Вставить ссылку", font=self.button_font,
                  bg="#2d3748", fg=self.text_color, bd=0, activebackground="#374151",
                  padx=25, pady=12, command=self.functions.paste_url).pack(side="left", padx=(0, 15))

        tk.Button(btn_frame, text="Скачать", font=self.button_font,
                  bg=self.accent_color, fg="#ffffff", bd=0, activebackground="#4f46e5",
                  padx=25, pady=12, command=self.functions.start_download).pack(side="right")

        # Лог загрузки
        log_frame = tk.Frame(main_container, bg=self.bg_color)
        log_frame.pack(fill="both", expand=True)

        tk.Label(log_frame, text="Статус загрузки:", bg=self.bg_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w", pady=(0, 10))

        # Текстовое поле для логов
        self.log_text = tk.Text(log_frame, bg="#0f0f23", fg=self.text_color,
                                font=('Consolas', 11), relief="flat",
                                highlightthickness=1, highlightcolor=self.border_color,
                                highlightbackground=self.border_color, wrap="word")

        # Скроллбар для логов
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

    def enable_text_editing(self, entry_widget):
        """Включает стандартные горячие клавиши для работы с текстом"""
        # Копирование (Ctrl+C)
        entry_widget.bind("<Control-c>", lambda e: self.copy_to_clipboard(entry_widget))
        # Вставка (Ctrl+V)
        entry_widget.bind("<Control-v>", lambda e: self.paste_from_clipboard_to_entry(entry_widget))
        # Вырезание (Ctrl+X)
        entry_widget.bind("<Control-x>", lambda e: self.cut_to_clipboard(entry_widget))
        # Выделение всего (Ctrl+A)
        entry_widget.bind("<Control-a>", lambda e: self.select_all(entry_widget))
        # Отмена (Ctrl+Z)
        entry_widget.bind("<Control-z>", lambda e: self.undo(entry_widget))
        # Повтор (Ctrl+Y)
        entry_widget.bind("<Control-y>", lambda e: self.redo(entry_widget))

        # Правый клик - контекстное меню
        entry_widget.bind("<Button-3>", lambda e: self.show_context_menu(e, entry_widget))

    def show_context_menu(self, event, entry_widget):
        """Показывает контекстное меню для работы с текстом"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Копировать", command=lambda: self.copy_to_clipboard(entry_widget))
        menu.add_command(label="Вставить", command=lambda: self.paste_from_clipboard_to_entry(entry_widget))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def copy_to_clipboard(self, entry_widget):
        """Копирует выделенный текст в буфер обмена"""
        try:
            if entry_widget.selection_present():
                selected_text = entry_widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass
        return "break"

    def cut_to_clipboard(self, entry_widget):
        """Вырезает выделенный текст в буфер обмена"""
        try:
            if entry_widget.selection_present():
                selected_text = entry_widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                entry_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass
        return "break"

    def paste_from_clipboard_to_entry(self, entry_widget):
        """Вставляет текст из буфера обмена в поле ввода"""
        try:
            # Получаем текст из буфера обмена
            clipboard_text = self.root.clipboard_get()

            # Если есть текст в буфере обмена, вставляем его
            if clipboard_text.strip():
                # Удаляем выделенный текст, если есть
                if entry_widget.selection_present():
                    entry_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)

                # Вставляем текст из буфера обмена
                entry_widget.insert(tk.INSERT, clipboard_text)

                # Для поля URL убираем placeholder при вставке
                if entry_widget == self.url_entry and entry_widget.get() == "Вставьте ссылку на видео здесь...":
                    entry_widget.delete(0, "end")
                    entry_widget.config(fg=self.text_color)
        except tk.TclError:
            # Если в буфере обмена нет текста
            pass
        return "break"

    def select_all(self, entry_widget):
        """Выделяет весь текст в поле ввода"""
        entry_widget.select_range(0, tk.END)
        return "break"

    def undo(self, entry_widget):
        """Отмена действия"""
        try:
            entry_widget.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def redo(self, entry_widget):
        """Повтор действия"""
        try:
            entry_widget.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def paste_from_clipboard(self, event=None):
        """Обработчик вставки из буфера обмена (для обратной совместимости)"""
        self.paste_from_clipboard_to_entry(self.url_entry)

    def show_format_selector(self, formats, is_tiktok=False):
        """Показывает диалог выбора формата видео"""
        dialog = FormatSelectorDialog(self.root, formats, self.bg_color, self.text_color, self.accent_color)
        return dialog.show()

    def show_error(self, title, message):
        """Показывает сообщение об ошибке"""
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        """Показывает информационное сообщение"""
        messagebox.showinfo(title, message)

    def reset_url_placeholder(self):
        """Сбрасывает placeholder в поле ввода URL"""
        self.url_var.set("Вставьте ссылку на видео здесь...")
        self.url_entry.config(fg=self.secondary_text)
        self.root.after(100, self.focus_url_entry)

    def open_download_folder(self):
        """Открывает папку с загрузками"""
        try:
            path = os.path.abspath(self.out_dir_var.get())
            os.makedirs(path, exist_ok=True)
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS or Linux
                import platform
                if platform.system() == 'Darwin':  # macOS
                    os.system(f'open "{path}"')
                else:  # Linux
                    os.system(f'xdg-open "{path}"')
        except Exception as e:
            self.show_error("Ошибка", f"Не удалось открыть папку: {str(e)}")