import tkinter as tk
from tkinter import ttk
from functions import JobsArchiveFunctions
import os
from PIL import Image, ImageTk
import time

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
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Выбор качества видео")
        self.dialog.configure(bg=self.bg_color)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        dialog_width = 800
        dialog_height = 500
        x = (self.parent.winfo_screenwidth() // 2) - (dialog_width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (dialog_height // 2)
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        frame = tk.Frame(self.dialog, bg=self.bg_color, padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=("resolution", "fps", "format", "size", "codec", "bitrate"),
                            show="headings", height=15)

        tree.heading("resolution", text="Разрешение")
        tree.heading("fps", text="FPS")
        tree.heading("format", text="Формат")
        tree.heading("size", text="Размер")
        tree.heading("codec", text="Кодек")
        tree.heading("bitrate", text="Битрейт")

        tree.column("resolution", width=120)
        tree.column("fps", width=60)
        tree.column("format", width=100)
        tree.column("size", width=100)
        tree.column("codec", width=120)
        tree.column("bitrate", width=100)

        for fmt in self.formats:
            if fmt.get('vcodec') != 'none':
                resolution = f"{fmt.get('width', 'N/A')}x{fmt.get('height', 'N/A')}"
                fps = fmt.get('fps', 'N/A')
                format_note = fmt.get('format_note', 'N/A')
                filesize = f"{fmt.get('filesize', 0) / (1024 * 1024):.1f}MB" if fmt.get('filesize') else 'N/A'
                codec = f"{fmt.get('vcodec', 'N/A')}/{fmt.get('acodec', 'N/A')}"
                bitrate = f"{fmt.get('tbr', 0) / 1000:.1f} Mbps" if fmt.get('tbr') else 'N/A'

                tree.insert("", "end", values=(resolution, fps, format_note, filesize, codec, bitrate, fmt))

        def on_select():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                self.selected_format = item['values'][-1]

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

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

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

        self.fullscreen = True
        self.root.attributes('-fullscreen', self.fullscreen)

        self.root.bind('<Escape>', lambda e: None)
        self.root.bind('<F11>', lambda e: None)

        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#2d3748"

        self.title_font = ('Arial', 24, 'bold')
        self.app_font = ('Arial', 14)
        self.button_font = ('Arial', 13)
        self.small_font = ('Arial', 12)

        os.makedirs("downloads", exist_ok=True)
        os.makedirs("history", exist_ok=True)

        self.proxy_var = tk.StringVar(value="")
        self.quality_var = tk.StringVar(value="best")
        self.fps_var = tk.StringVar(value="any")
        self.codec_var = tk.StringVar(value="any")
        self.audio_var = tk.BooleanVar(value=False)
        self.out_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))

        self.functions = JobsArchiveFunctions(self)

        self.setup_ui()
        self.setup_styles()

        self.root.after(100, self.focus_url_entry)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

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

        style.configure('TProgressbar',
                        background=self.accent_color,
                        troughcolor=self.border_color)

    def focus_url_entry(self):
        self.url_entry.focus_set()

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)

        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=40, pady=40)

        header_frame = tk.Frame(main_container, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 30))

        tk.Label(header_frame, text="JOBS ARCHIVE", bg=self.bg_color,
                 fg=self.accent_color, font=self.title_font).pack(side="left")

        content_frame = tk.Frame(main_container, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True)

        input_frame = tk.Frame(content_frame, bg=self.card_color, padx=25, pady=25)
        input_frame.pack(side="left", fill="y", padx=(0, 20), anchor="n")

        tk.Label(input_frame, text="Введите URL видео:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w", pady=(0, 15))

        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(input_frame, textvariable=self.url_var, bg="#0f0f23", fg=self.text_color,
                                  font=self.app_font, insertbackground=self.text_color,
                                  relief="flat", highlightthickness=1,
                                  highlightcolor=self.accent_color, highlightbackground=self.border_color)
        self.url_entry.pack(fill="x", pady=10, ipady=8)
        self.url_entry.bind("<Return>", lambda e: self.functions.add_to_queue(self.url_var.get()))

        self.url_entry.insert(0, "Вставьте ссылку на видео здесь...")
        self.url_entry.config(fg=self.secondary_text)

        self.enable_text_editing(self.url_entry)

        tk.Label(input_frame, text="Параметры видео:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w", pady=(15, 5))

        quality_frame = tk.Frame(input_frame, bg=self.card_color)
        quality_frame.pack(fill="x", pady=5)

        tk.Label(quality_frame, text="Качество:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(side="left", padx=(0, 10))
        quality_box = ttk.Combobox(
            quality_frame, textvariable=self.quality_var,
            values=["best", "1080p", "720p", "480p", "360p"],
            state="readonly"
        )
        quality_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        quality_box.bind("<<ComboboxSelected>>", lambda e: self.functions.save_settings())

        tk.Label(quality_frame, text="FPS:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(side="left", padx=(10, 10))
        fps_box = ttk.Combobox(
            quality_frame, textvariable=self.fps_var,
            values=["any", "24", "30", "60"],
            state="readonly"
        )
        fps_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        fps_box.bind("<<ComboboxSelected>>", lambda e: self.functions.save_settings())

        tk.Label(quality_frame, text="Кодек:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(side="left", padx=(10, 10))
        codec_box = ttk.Combobox(
            quality_frame, textvariable=self.codec_var,
            values=["any", "h264", "h265", "av1"],
            state="readonly"
        )
        codec_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        codec_box.bind("<<ComboboxSelected>>", lambda e: self.functions.save_settings())

        audio_check = tk.Checkbutton(quality_frame, text="Только аудио", variable=self.audio_var,
                                     bg=self.card_color, fg=self.text_color, selectcolor="#0f0f23",
                                     font=self.app_font, command=self.functions.save_settings)
        audio_check.pack(side="right")

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
        browse_btn.pack(side="left")

        open_folder_btn = tk.Button(dir_frame, text="Открыть папку", font=self.button_font,
                                    bg="#2d3748", fg=self.text_color, bd=0, activebackground="#374151",
                                    padx=15, pady=8, command=self.functions.open_download_folder)
        open_folder_btn.pack(side="right")

        tk.Label(input_frame, text="Прокси (если нужен):", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w", pady=(15, 5))

        self.proxy_entry = tk.Entry(input_frame, textvariable=self.proxy_var, bg="#0f0f23", fg=self.text_color,
                                    font=self.app_font, insertbackground=self.text_color,
                                    relief="flat", highlightthickness=1,
                                    highlightcolor=self.accent_color, highlightbackground=self.border_color)
        self.proxy_entry.pack(fill="x", pady=5, ipady=8)
        self.proxy_entry.bind("<KeyRelease>", lambda e: self.functions.save_settings())

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

        btn_frame = tk.Frame(input_frame, bg=self.card_color)
        btn_frame.pack(fill="x", pady=(20, 0))

        tk.Button(btn_frame, text="Вставить ссылку", font=self.button_font,
                  bg="#2d3748", fg=self.text_color, bd=0, activebackground="#374151",
                  padx=25, pady=12, command=self.functions.paste_url).pack(side="left", padx=(0, 15))

        tk.Button(btn_frame, text="Добавить в очередь", font=self.button_font,
                  bg=self.accent_color, fg="#ffffff", bd=0, activebackground="#4f46e5",
                  padx=25, pady=12, command=lambda: self.functions.add_to_queue(self.url_var.get())).pack(side="right")

        error_frame = tk.Frame(input_frame, bg=self.card_color, padx=15, pady=15)
        error_frame.pack(fill="x", pady=(10, 0))

        tk.Label(error_frame, text="Сообщения:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w")

        self.error_label = tk.Label(error_frame, text="", bg=self.card_color, fg="#ff4444",
                                    font=self.small_font, wraplength=400, justify="left", anchor="nw",
                                    height=3)
        self.error_label.pack(anchor="w", pady=5, fill="x")

        tk.Button(error_frame, text="Очистить лог", font=self.button_font,
                  bg="#2d3748", fg=self.text_color, bd=0, activebackground="#374151",
                  padx=15, pady=8, command=self.clear_log).pack(side="bottom", anchor="w", pady=5)

        right_frame = tk.Frame(content_frame, bg=self.bg_color)
        right_frame.pack(side="right", fill="both", expand=True)

        queue_frame = tk.Frame(right_frame, bg=self.card_color, padx=15, pady=15)
        queue_frame.pack(fill="x", pady=(0, 20))

        tk.Label(queue_frame, text="Очередь загрузки:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w")

        self.queue_listbox = tk.Listbox(queue_frame, bg="#0f0f23", fg=self.text_color,
                                        font=self.small_font, height=5,
                                        relief="flat", highlightthickness=1,
                                        highlightcolor=self.border_color,
                                        highlightbackground=self.border_color)
        self.queue_listbox.pack(fill="x", pady=5)
        self.queue_listbox.bind("<Button-3>", self.show_queue_context_menu)

        stats_frame = tk.Frame(right_frame, bg=self.card_color, padx=15, pady=10)
        stats_frame.pack(fill="x", pady=(0, 20))

        tk.Label(stats_frame, text="Статистика загрузок:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w")
        self.stats_label = tk.Label(stats_frame, text="Успешно: 0 | Неуспешно: 0",
                                    bg=self.card_color, fg=self.text_color, font=self.small_font)
        self.stats_label.pack(anchor="w", pady=5)

        history_frame = tk.Frame(right_frame, bg=self.card_color, padx=15, pady=15)
        history_frame.pack(fill="both", expand=True)

        tk.Label(history_frame, text="История загрузок:", bg=self.card_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w")

        self.history_tree = ttk.Treeview(history_frame, columns=("title", "timestamp", "status", "filepath"),
                                        show="headings", height=10)
        self.history_tree.heading("title", text="Название")
        self.history_tree.heading("timestamp", text="Время")
        self.history_tree.heading("status", text="Статус")
        self.history_tree.heading("filepath", text="Путь")
        self.history_tree.column("title", width=200)
        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("status", width=100)
        self.history_tree.column("filepath", width=200)
        self.history_tree.pack(fill="both", expand=True, pady=5)
        self.history_tree.bind('<Double-1>', self.on_history_double_click)
        self.history_tree.bind('<Button-3>', self.show_history_context_menu)

        history_btn_frame = tk.Frame(history_frame, bg=self.card_color)
        history_btn_frame.pack(fill="x", pady=5)

        tk.Button(history_btn_frame, text="Очистить историю", font=self.button_font,
                  bg="#2d3748", fg=self.text_color, bd=0, activebackground="#374151",
                  padx=15, pady=8, command=self.functions.clear_history).pack(side="right")

        log_frame = tk.Frame(right_frame, bg=self.bg_color)
        log_frame.pack(fill="both", expand=True)

        tk.Label(log_frame, text="Статус загрузки:", bg=self.bg_color,
                 fg=self.text_color, font=self.app_font).pack(anchor="w", pady=(0, 10))

        self.progress_bar = ttk.Progressbar(log_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(0, 10))

        self.timer_label = tk.Label(log_frame, text="Время загрузки: 00:00", bg=self.bg_color,
                                   fg=self.text_color, font=self.app_font)
        self.timer_label.pack(anchor="w", pady=(0, 10))

        self.log_text = tk.Text(log_frame, bg="#0f0f23", fg=self.text_color,
                                font=('Consolas', 11), relief="flat",
                                highlightthickness=1, highlightcolor=self.border_color,
                                highlightbackground=self.border_color, wrap="word")
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

        self.update_history_display()
        self.update_stats_display()

    def show_queue_context_menu(self, event):
        selection = self.queue_listbox.nearest(event.y)
        if selection >= 0:
            self.queue_listbox.selection_clear(0, tk.END)
            self.queue_listbox.selection_set(selection)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Удалить из очереди",
                            command=lambda: self.functions.remove_from_queue(selection))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def show_history_context_menu(self, event):
        selection = self.history_tree.selection()
        if selection:
            item = self.history_tree.item(selection[0])
            url = self.functions.load_history()[self.history_tree.index(selection[0])].get("url")
            filepath = item['values'][3]
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Открыть файл",
                            command=lambda: self.functions.open_file(filepath))
            menu.add_command(label="Повторить загрузку",
                            command=lambda: self.functions.retry_download(url))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def update_error_display(self, message):
        self.error_label.config(text=message)

    def update_queue_display(self):
        self.queue_listbox.delete(0, tk.END)
        for url in self.functions.download_queue:
            self.queue_listbox.insert(tk.END, url)

    def update_history_display(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        history = self.functions.load_history()
        for entry in history:
            title = entry.get("title", "Unknown")[:50]
            timestamp = entry.get("timestamp", "N/A")
            status = entry.get("status", "N/A")
            filepath = entry.get("filepath", "N/A")
            self.history_tree.insert("", "end", values=(title, timestamp, status, filepath))

    def update_stats_display(self):
        history = self.functions.load_history()
        successful = len([entry for entry in history if entry.get("status") == "Completed"])
        failed = len([entry for entry in history if entry.get("status", "").startswith("Failed")])
        self.stats_label.config(text=f"Успешно: {successful} | Неуспешно: {failed}")

    def on_history_double_click(self, event):
        selection = self.history_tree.selection()
        if selection:
            item = self.history_tree.item(selection[0])
            filepath = item['values'][3]
            if filepath:
                self.functions.open_file(filepath)

    def update_progress(self, percentage):
        self.progress_bar['value'] = percentage
        self.root.update_idletasks()

    def update_timer(self, elapsed_time):
        minutes, seconds = divmod(int(elapsed_time), 60)
        self.timer_label.config(text=f"Время загрузки: {minutes:02d}:{seconds:02d}")
        self.root.update_idletasks()

    def reset_progress_and_timer(self):
        self.progress_bar['value'] = 0
        self.timer_label.config(text="Время загрузки: 00:00")
        self.root.update_idletasks()

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
        self.update_error_display("Лог очищен.")

    def enable_text_editing(self, entry_widget):
        entry_widget.bind("<Control-c>", lambda e: self.copy_to_clipboard(entry_widget))
        entry_widget.bind("<Control-v>", lambda e: self.paste_from_clipboard_to_entry(entry_widget))
        entry_widget.bind("<Control-x>", lambda e: self.cut_to_clipboard(entry_widget))
        entry_widget.bind("<Control-a>", lambda e: self.select_all(entry_widget))
        entry_widget.bind("<Control-z>", lambda e: self.undo(entry_widget))
        entry_widget.bind("<Control-y>", lambda e: self.redo(entry_widget))
        entry_widget.bind("<Button-3>", lambda e: self.show_context_menu(e, entry_widget))

    def show_context_menu(self, event, entry_widget):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Копировать", command=lambda: self.copy_to_clipboard(entry_widget))
        menu.add_command(label="Вставить", command=lambda: self.paste_from_clipboard_to_entry(entry_widget))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def copy_to_clipboard(self, entry_widget):
        try:
            if entry_widget.selection_present():
                selected_text = entry_widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass
        return "break"

    def cut_to_clipboard(self, entry_widget):
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
        try:
            clipboard_text = self.root.clipboard_get()
            if clipboard_text.strip():
                if entry_widget.selection_present():
                    entry_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                entry_widget.insert(tk.INSERT, clipboard_text)
                if entry_widget == self.url_entry and entry_widget.get() == "Вставьте ссылку на видео здесь...":
                    entry_widget.delete(0, "end")
                    entry_widget.config(fg=self.text_color)
        except tk.TclError:
            pass
        return "break"

    def select_all(self, entry_widget):
        entry_widget.select_range(0, tk.END)
        return "break"

    def undo(self, entry_widget):
        try:
            entry_widget.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def redo(self, entry_widget):
        try:
            entry_widget.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def show_format_selector(self, formats):
        dialog = FormatSelectorDialog(self.root, formats, self.bg_color, self.text_color, self.accent_color)
        return dialog.show()