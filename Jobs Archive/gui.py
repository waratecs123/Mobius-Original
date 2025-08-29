import tkinter as tk
from tkinter import ttk, messagebox
from functions import JobsArchiveFunctions
import os
import threading


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
        dialog_width = 600
        dialog_height = 400
        x = (self.parent.winfo_screenwidth() // 2) - (dialog_width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (dialog_height // 2)
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Фрейм для Treeview
        frame = tk.Frame(self.dialog, bg=self.bg_color, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        # Создаем Treeview для отображения форматов
        tree = ttk.Treeview(frame, columns=("resolution", "fps", "format", "size"),
                            show="headings", height=15)

        tree.heading("resolution", text="Разрешение")
        tree.heading("fps", text="FPS")
        tree.heading("format", text="Формат")
        tree.heading("size", text="Размер")

        tree.column("resolution", width=120)
        tree.column("fps", width=60)
        tree.column("format", width=100)
        tree.column("size", width=100)

        # Заполняем данными
        for fmt in self.formats:
            if fmt.get('vcodec') != 'none':  # Только видео форматы
                resolution = f"{fmt.get('width', 'N/A')}x{fmt.get('height', 'N/A')}"
                fps = fmt.get('fps', 'N/A')
                format_note = fmt.get('format_note', 'N/A')
                filesize = f"{fmt.get('filesize', 0) / (1024 * 1024):.1f}MB" if fmt.get('filesize') else 'N/A'

                tree.insert("", "end", values=(resolution, fps, format_note, filesize, fmt))

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
        btn_frame = tk.Frame(self.dialog, bg=self.bg_color, pady=10)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Отмена", command=self.dialog.destroy,
                  bg="#2a2a2a", fg=self.text_color, font=('Segoe UI', 10)).pack(side="right", padx=(10, 0))

        tk.Button(btn_frame, text="Выбрать", command=on_ok,
                  bg=self.accent_color, fg="#ffffff", font=('Segoe UI', 10)).pack(side="right")

        self.dialog.wait_window()
        return self.selected_format


class JobsArchiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jobs Archive")
        self.functions = JobsArchiveFunctions(self)

        # Принудительный полноэкранный режим без возможности выхода
        self.fullscreen = True
        self.root.attributes('-fullscreen', self.fullscreen)

        # Блокируем клавиши для выхода из полноэкранного режима
        self.root.bind('<Escape>', lambda e: None)
        self.root.bind('<F11>', lambda e: None)

        # Темная цветовая палитра
        self.bg_color = "#121212"
        self.card_color = "#1e1e1e"
        self.accent_color = "#4870ff"
        self.text_color = "#e0e0e0"
        self.secondary_text = "#a0a0a0"

        # Шрифты
        self.title_font = ('Segoe UI', 18, 'bold')
        self.app_font = ('Segoe UI', 12)
        self.button_font = ('Segoe UI', 12)

        # Создаем папку для загрузок
        os.makedirs("downloads", exist_ok=True)

        self.setup_ui()

        # Устанавливаем фокус на поле ввода при запуске
        self.root.after(100, self.focus_url_entry)

    def focus_url_entry(self):
        """Устанавливает фокус на поле ввода URL"""
        self.url_entry.focus_set()

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)

        # Основной контейнер
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Заголовок
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))

        tk.Label(header_frame, text="JOBS ARCHIVE", bg=self.bg_color,
                 fg=self.accent_color, font=self.title_font).pack(side="left")

        # Поле ввода URL
        input_frame = tk.Frame(main_frame, bg=self.card_color, padx=15, pady=15)
        input_frame.pack(fill="x", pady=(0, 15))

        tk.Label(input_frame, text="Введите URL YouTube или TikTok видео:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w")

        self.url_entry = tk.Entry(input_frame, bg="#252525", fg=self.text_color,
                                  font=self.app_font, insertbackground=self.text_color,
                                  relief="flat", highlightthickness=1,
                                  highlightcolor=self.accent_color, highlightbackground="#404040")
        self.url_entry.pack(fill="x", pady=10)
        self.url_entry.bind("<Return>", lambda e: self.functions.add_to_queue())

        # Добавляем подсказку в поле ввода
        self.url_entry.insert(0, "Вставьте ссылку YouTube или TikTok здесь...")
        self.url_entry.config(fg=self.secondary_text)

        # Разрешаем вставку из буфера обмена
        self.url_entry.bind("<Control-v>", self.paste_from_clipboard)
        self.url_entry.bind("<Button-2>", self.paste_from_clipboard)  # Для Mac
        self.url_entry.bind("<Button-3>", self.paste_from_clipboard)  # Для Windows/Linux

        def on_entry_click(event):
            if self.url_entry.get() == "Вставьте ссылку YouTube или TikTok здесь...":
                self.url_entry.delete(0, "end")
                self.url_entry.config(fg=self.text_color)

        def on_focusout(event):
            if self.url_entry.get() == '':
                self.url_entry.insert(0, "Вставьте ссылку YouTube или TikTok здесь...")
                self.url_entry.config(fg=self.secondary_text)

        self.url_entry.bind('<FocusIn>', on_entry_click)
        self.url_entry.bind('<FocusOut>', on_focusout)

        # Кнопки управления
        btn_frame = tk.Frame(input_frame, bg=self.card_color)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Добавить в очередь", font=self.button_font,
                  bg=self.accent_color, fg="#ffffff", bd=0, activebackground="#3a5bd9",
                  padx=20, pady=8, command=self.functions.add_to_queue).pack(side="left")

        tk.Button(btn_frame, text="Начать загрузку", font=self.button_font,
                  bg="#2a2a2a", fg=self.text_color, bd=0, activebackground="#3a3a3a",
                  padx=20, pady=8, command=self.functions.start_downloads).pack(side="right")

        # Очередь загрузок
        queue_frame = tk.Frame(main_frame, bg=self.bg_color)
        queue_frame.pack(fill="both", expand=True)

        # Стиль для Treeview
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", background=self.card_color, fieldbackground=self.card_color,
                        foreground=self.text_color, borderwidth=0, font=self.app_font)
        style.configure("Treeview.Heading", background="#252525", foreground=self.text_color,
                        relief="flat", font=('Segoe UI', 11, 'bold'))
        style.map("Treeview", background=[('selected', '#333333')])

        # Таблица очереди
        self.queue_tree = ttk.Treeview(queue_frame,
                                       columns=("status", "progress", "size", "speed", "platform", "quality"),
                                       show="headings", height=15)

        # Настройка колонок
        self.queue_tree.heading("status", text="Статус")
        self.queue_tree.heading("progress", text="Прогресс")
        self.queue_tree.heading("size", text="Размер")
        self.queue_tree.heading("speed", text="Скорость")
        self.queue_tree.heading("platform", text="Платформа")
        self.queue_tree.heading("quality", text="Качество")

        self.queue_tree.column("status", width=120, anchor="w")
        self.queue_tree.column("progress", width=80, anchor="center")
        self.queue_tree.column("size", width=80, anchor="center")
        self.queue_tree.column("speed", width=100, anchor="center")
        self.queue_tree.column("platform", width=80, anchor="center")
        self.queue_tree.column("quality", width=120, anchor="center")

        # Скроллбары
        vsb = ttk.Scrollbar(queue_frame, orient="vertical", command=self.queue_tree.yview)
        hsb = ttk.Scrollbar(queue_frame, orient="horizontal", command=self.queue_tree.xview)
        self.queue_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Размещение элементов
        self.queue_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        queue_frame.grid_rowconfigure(0, weight=1)
        queue_frame.grid_columnconfigure(0, weight=1)

        # Кнопки управления очередью
        controls_frame = tk.Frame(queue_frame, bg=self.bg_color)
        controls_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        tk.Button(controls_frame, text="Приостановить", font=self.button_font,
                  bg="#2a2a2a", fg=self.text_color, bd=0, activebackground="#3a3a3a",
                  padx=15, pady=6, command=self.functions.pause_downloads).pack(side="left", padx=(0, 5))

        tk.Button(controls_frame, text="Удалить выбранное", font=self.button_font,
                  bg="#2a2a2a", fg=self.text_color, bd=0, activebackground="#3a3a3a",
                  padx=15, pady=6, command=self.functions.remove_selected).pack(side="left", padx=(0, 5))

        tk.Button(controls_frame, text="Очистить очередь", font=self.button_font,
                  bg="#2a2a2a", fg="#ff5555", bd=0, activebackground="#3a3a3a",
                  padx=15, pady=6, command=self.functions.clear_queue).pack(side="right")

        tk.Button(controls_frame, text="Открыть папку", font=self.button_font,
                  bg="#2a2a2a", fg=self.accent_color, bd=0, activebackground="#3a3a3a",
                  padx=15, pady=6, command=self.open_download_folder).pack(side="right", padx=(0, 10))

    def paste_from_clipboard(self, event=None):
        """Обработчик вставки из буфера обмена"""
        try:
            # Получаем текст из буфера обмена
            clipboard_text = self.root.clipboard_get()

            # Если есть текст в буфере обмена, вставляем его
            if clipboard_text.strip():
                # Очищаем поле, если там placeholder
                if self.url_entry.get() == "Вставьте ссылку YouTube или TikTok здесь...":
                    self.url_entry.delete(0, "end")
                    self.url_entry.config(fg=self.text_color)

                # Вставляем текст из буфера обмена
                self.url_entry.insert(tk.INSERT, clipboard_text)

                # Прокручиваем до конца, если текст длинный
                self.url_entry.xview_moveto(1.0)
        except tk.TclError:
            # Если в буфере обмена нет текста
            pass

        return "break"  # Предотвращаем стандартное поведение

    def show_format_selector(self, formats, is_tiktok=False):
        """Показывает диалог выбора формата видео"""
        dialog = FormatSelectorDialog(self.root, formats, self.bg_color, self.text_color, self.accent_color)
        return dialog.show()

    def show_error(self, title, message):
        """Показывает сообщение об ошибке"""
        messagebox.showerror(title, message)

    def update_queue(self, items):
        """Обновление списка загрузок"""
        self.queue_tree.delete(*self.queue_tree.get_children())
        for item in items:
            self.queue_tree.insert("", "end", values=item)

    def open_download_folder(self):
        """Открывает папку с загрузками"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile("downloads")
            elif os.name == 'posix':  # macOS or Linux
                if os.uname().sysname == 'Darwin':  # macOS
                    os.system('open downloads')
                else:  # Linux
                    os.system('xdg-open downloads')
        except Exception as e:
            self.show_error("Ошибка", f"Не удалось открыть папку: {str(e)}")