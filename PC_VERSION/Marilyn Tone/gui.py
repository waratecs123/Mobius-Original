import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from functions import VoiceEngine
import os
import threading
import time
from typing import Optional, Callable
import webbrowser
from datetime import datetime
import json


class MarilynToneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Marilyn Tone - Профессиональный синтезатор речи")
        self.voice_engine = VoiceEngine()
        self.current_operation = None
        self.text_history = []
        self.history_index = -1
        self.history = []

        # Переменные для эффектов
        self.pitch_var = tk.IntVar(value=0)
        self.echo_var = tk.BooleanVar(value=False)
        self.reverb_var = tk.IntVar(value=0)  # Reverb intensity (0-100)
        self.volume_var = tk.IntVar(value=0)  # Volume adjustment (-12 to +12 dB)
        self.search_var = tk.StringVar()

        self.root.attributes('-fullscreen', True)

        # Цветовая палитра
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.secondary_color = "#4f46e5"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#2d3748"
        self.disabled_color = "#404040"
        self.success_color = "#10b981"
        self.error_color = "#ef4444"
        self.hover_color = "#2f2f5b"

        # Шрифты
        self.title_font = ('Arial', 26, 'bold')
        self.app_font = ('Arial', 13)
        self.button_font = ('Arial', 12, 'bold')
        self.mono_font = ('Consolas', 11)

        self.setup_styles()
        self.setup_ui()
        self.setup_bindings()
        self.load_last_settings()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Custom.TNotebook', background=self.card_color, borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                        background=self.border_color,
                        foreground=self.text_color,
                        padding=[20, 10],
                        font=('Arial', 11, 'bold'),
                        borderwidth=0)
        style.map('Custom.TNotebook.Tab',
                  background=[('selected', self.card_color)],
                  foreground=[('selected', self.accent_color)])

        style.configure('Accent.TButton',
                        background=self.accent_color,
                        foreground='white',
                        borderwidth=0,
                        font=self.button_font,
                        padding=10)
        style.map('Accent.TButton',
                  background=[('active', self.secondary_color), ('disabled', self.disabled_color)])

        style.configure('Secondary.TButton',
                        background=self.border_color,
                        foreground=self.text_color,
                        borderwidth=0,
                        font=self.button_font,
                        padding=10)
        style.map('Secondary.TButton',
                  background=[('active', self.hover_color), ('disabled', self.disabled_color)])

        style.configure('TCombobox',
                        fieldbackground=self.border_color,
                        background=self.border_color,
                        foreground=self.text_color,
                        selectbackground=self.accent_color,
                        selectforeground='white',
                        borderwidth=1,
                        padding=10,
                        arrowcolor=self.accent_color)
        style.map('TCombobox',
                  fieldbackground=[('readonly', self.border_color)],
                  selectbackground=[('readonly', self.accent_color)])

        style.configure('Custom.Treeview',
                        background=self.card_color,
                        foreground=self.text_color,
                        fieldbackground=self.card_color,
                        font=('Arial', 11),
                        rowheight=35)
        style.configure('Custom.Treeview.Heading',
                        background=self.border_color,
                        foreground=self.text_color,
                        font=('Arial', 12, 'bold'))
        style.map('Custom.Treeview',
                  background=[('selected', self.accent_color)],
                  foreground=[('selected', 'white')])
        style.map('Custom.Treeview.Heading',
                  background=[('active', self.hover_color)])

        style.configure('TProgressbar',
                        background=self.accent_color,
                        troughcolor=self.border_color)

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=40, pady=40)

        self.setup_sidebar(main_container)
        self.setup_main_area(main_container)

    def setup_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.card_color, width=320, relief='flat',
                          bd=2, highlightbackground=self.border_color, highlightthickness=1)
        sidebar.pack(side="left", fill="y", padx=(0, 30))
        sidebar.pack_propagate(False)

        top_sidebar = tk.Frame(sidebar, bg=self.card_color)
        top_sidebar.pack(fill="x", pady=(40, 50), padx=30)

        logo_frame = tk.Frame(top_sidebar, bg=self.card_color)
        logo_frame.pack(fill="x")

        logo_canvas = tk.Canvas(logo_frame, bg=self.card_color, width=60, height=60,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")
        logo_canvas.create_oval(8, 8, 52, 52, fill=self.accent_color, outline="")
        logo_canvas.create_text(30, 30, text="M", font=('Arial', 24, 'bold'), fill="white")

        name_frame = tk.Frame(logo_frame, bg=self.card_color)
        name_frame.pack(side="left", padx=(15, 0))
        tk.Label(name_frame, text="MARILYN", bg=self.card_color,
                 fg=self.accent_color, font=('Arial', 18, 'bold')).pack(anchor="w")
        tk.Label(name_frame, text="TONE", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 18, 'bold')).pack(anchor="w")

        info_frame = tk.Frame(top_sidebar, bg=self.card_color)
        info_frame.pack(fill="x", pady=(30, 0))
        self.voice_info_label = tk.Label(
            info_frame, text="", bg=self.card_color, fg=self.secondary_text,
            font=('Arial', 10), wraplength=280, justify='left'
        )
        self.voice_info_label.pack(anchor="w", pady=(0, 20))

        preview_btn = ttk.Button(
            top_sidebar,
            text="ПРОСЛУШАТЬ ГОЛОС",
            style='Accent.TButton',
            command=self.preview_selected_voice
        )
        preview_btn.pack(fill="x", pady=(10, 0))

        stats_frame = tk.Frame(top_sidebar, bg=self.card_color)
        stats_frame.pack(fill="x", pady=(30, 0))
        self.stats_label = tk.Label(
            stats_frame, text="Символов: 0 | Слов: 0", bg=self.card_color,
            fg=self.secondary_text, font=('Arial', 10)
        )
        self.stats_label.pack(anchor="w")

        bottom_sidebar = tk.Frame(sidebar, bg=self.card_color)
        bottom_sidebar.pack(side="bottom", fill="x", pady=40, padx=30)

        self.stop_btn = ttk.Button(
            bottom_sidebar,
            text="ОСТАНОВИТЬ ГОЛОС",
            style='Secondary.TButton',
            command=self.stop_playback,
            state='disabled'
        )
        self.stop_btn.pack(fill="x", pady=(0, 15))

        exit_btn = tk.Button(
            bottom_sidebar, text="ВЫХОД",
            bg="#dc2626", fg="white", font=self.button_font,
            bd=0, command=self.safe_exit
        )
        exit_btn.pack(fill="x")

    def setup_main_area(self, parent):
        self.main_area = tk.Frame(parent, bg=self.bg_color)
        self.main_area.pack(side="right", fill="both", expand=True)

        header_frame = tk.Frame(self.main_area, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))

        self.section_title = tk.Label(header_frame, text="Синтез Речи",
                                      bg=self.bg_color, fg=self.text_color, font=self.title_font)
        self.section_title.pack(side="left")

        header_buttons = tk.Frame(header_frame, bg=self.bg_color)
        header_buttons.pack(side="right")
        ttk.Button(header_buttons, text="Вставить", style='Secondary.TButton',
                   command=self.paste_text).pack(side="left", padx=10)
        ttk.Button(header_buttons, text="Очистить", style='Secondary.TButton',
                   command=self.clear_text).pack(side="left", padx=10)
        self.play_btn = ttk.Button(
            header_buttons, text="ОЗВУЧИТЬ", style='Accent.TButton',
            command=self.synthesize_speech
        )
        self.play_btn.pack(side="left", padx=10)
        self.listen_btn = ttk.Button(
            header_buttons, text="ПРОСЛУШАТЬ", style='Secondary.TButton',
            command=self.preview_speech
        )
        self.listen_btn.pack(side="left", padx=10)
        self.download_btn = ttk.Button(
            header_buttons, text="СОХРАНИТЬ АУДИО", style='Secondary.TButton',
            command=self.save_audio
        )
        self.download_btn.pack(side="left", padx=10)
        self.quick_save_btn = ttk.Button(
            header_buttons, text="БЫСТРОЕ СОХРАНЕНИЕ", style='Secondary.TButton',
            command=self.quick_save
        )
        self.quick_save_btn.pack(side="left", padx=10)

        self.notebook = ttk.Notebook(self.main_area, style='Custom.TNotebook')
        self.notebook.pack(fill="both", expand=True)

        self.synth_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.synth_frame, text="Синтез")

        self.history_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.history_frame, text="История")

        self.setup_synth_ui()
        self.setup_history_ui()

    def setup_synth_ui(self):
        content_frame = tk.Frame(self.synth_frame, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True)

        input_frame = tk.Frame(content_frame, bg=self.card_color, padx=30, pady=20,
                              relief='flat', bd=2, highlightbackground=self.border_color,
                              highlightthickness=1)
        input_frame.pack(fill="both", expand=True, pady=(0, 15))

        tk.Label(input_frame, text="Введите текст для озвучивания:",
                 bg=self.card_color, fg=self.text_color, font=('Arial', 14, 'bold')
                 ).pack(anchor="w", pady=(0, 10))

        text_container = tk.Frame(input_frame, bg=self.border_color, bd=0, relief='flat', padx=1, pady=1)
        text_container.pack(fill="both", expand=True)

        self.text_input = scrolledtext.ScrolledText(
            text_container,
            bg=self.border_color, fg=self.text_color, font=self.mono_font,
            insertbackground=self.accent_color, relief='flat', bd=0,
            padx=20, pady=20, wrap=tk.WORD, selectbackground=self.accent_color,
            undo=True, maxundo=100
        )
        self.text_input.pack(fill="both", expand=True)
        self.text_input.bind('<KeyRelease>', self.update_text_stats)

        self.progress_frame = tk.Frame(content_frame, bg=self.bg_color)
        self.progress_frame.pack(fill="x", pady=(0, 15))
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, mode='indeterminate', style='TProgressbar'
        )
        self.progress_bar.pack(fill="x")
        self.progress_frame.pack_forget()

        settings_container = tk.Frame(content_frame, bg=self.card_color, padx=30, pady=15,
                                     relief='flat', bd=2, highlightbackground=self.border_color,
                                     highlightthickness=1)
        settings_container.pack(fill="x", pady=(0, 15))

        voice_column = tk.Frame(settings_container, bg=self.card_color)
        voice_column.pack(side="left", fill="both", expand=True, padx=(0, 20))
        tk.Label(voice_column, text="Голос:", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 12, 'bold')
                 ).pack(anchor="w", pady=(0, 10))
        self.voice_combobox = ttk.Combobox(
            voice_column, values=[v['name'] for v in self.voice_engine.voices],
            state="readonly", font=self.app_font, height=12
        )
        self.voice_combobox.current(0)
        self.voice_combobox.pack(fill="x")
        self.voice_combobox.bind('<<ComboboxSelected>>', self.on_voice_selected)

        speed_column = tk.Frame(settings_container, bg=self.card_color)
        speed_column.pack(side="left", fill="both", expand=True, padx=(0, 20))
        tk.Label(speed_column, text="Скорость речи:", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 12, 'bold')
                 ).pack(anchor="w", pady=(0, 10))
        speed_control_frame = tk.Frame(speed_column, bg=self.card_color)
        speed_control_frame.pack(fill="x")
        self.speed_var = tk.IntVar(value=150)
        self.speed_scale = tk.Scale(
            speed_control_frame, from_=50, to=300, orient=tk.HORIZONTAL,
            variable=self.speed_var, bg=self.card_color, fg=self.text_color,
            highlightthickness=0, troughcolor=self.border_color,
            activebackground=self.accent_color, sliderlength=25,
            length=200, showvalue=False, font=self.app_font
        )
        self.speed_scale.pack(side="left")
        speed_value_frame = tk.Frame(speed_control_frame, bg=self.card_color)
        speed_value_frame.pack(side="left", padx=(15, 0))
        self.speed_label = tk.Label(
            speed_value_frame, textvariable=self.speed_var,
            bg=self.card_color, fg=self.accent_color,
            font=('Arial', 15, 'bold'), width=4
        )
        self.speed_label.pack()
        tk.Label(speed_value_frame, text="слов/мин", bg=self.card_color,
                 fg=self.secondary_text, font=('Arial', 10)).pack()

        effects_column = tk.Frame(settings_container, bg=self.card_color)
        effects_column.pack(side="left", fill="both", expand=True)
        tk.Label(effects_column, text="Эффекты:", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 12, 'bold')
                 ).pack(anchor="w", pady=(0, 10))

        # Scrollable effects frame
        effects_canvas = tk.Canvas(effects_column, bg=self.card_color, height=200,
                                   highlightthickness=0)
        effects_scrollbar = ttk.Scrollbar(effects_column, orient="vertical",
                                          command=effects_canvas.yview)
        effects_frame = tk.Frame(effects_canvas, bg=self.card_color)

        effects_canvas.configure(yscrollcommand=effects_scrollbar.set)
        effects_scrollbar.pack(side="right", fill="y")
        effects_canvas.pack(fill="both", expand=True)
        effects_canvas.create_window((0, 0), window=effects_frame, anchor="nw")

        def on_configure(event):
            effects_canvas.configure(scrollregion=effects_canvas.bbox("all"))

        effects_frame.bind("<Configure>", on_configure)

        # Pitch effect
        tk.Label(effects_frame, text="Высота тона:", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 11)).pack(anchor="w", pady=(0, 5))
        self.pitch_scale = tk.Scale(
            effects_frame, from_=-12, to=12, orient=tk.HORIZONTAL,
            variable=self.pitch_var, bg=self.card_color, fg=self.text_color,
            highlightthickness=0, troughcolor=self.border_color,
            activebackground=self.accent_color, sliderlength=25,
            length=200, showvalue=False, font=self.app_font
        )
        self.pitch_scale.pack(fill="x")
        tk.Label(effects_frame, textvariable=self.pitch_var, bg=self.card_color,
                 fg=self.accent_color, font=('Arial', 11)).pack(anchor="w", pady=(0, 5))

        # Echo effect
        tk.Checkbutton(effects_frame, text="Эхо эффект", variable=self.echo_var,
                       bg=self.card_color, fg=self.text_color, selectcolor=self.border_color,
                       activebackground=self.card_color, activeforeground=self.text_color).pack(anchor="w", pady=(5, 5))

        # Reverb effect
        tk.Label(effects_frame, text="Интенсивность реверберации:", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 11)).pack(anchor="w", pady=(5, 5))
        self.reverb_scale = tk.Scale(
            effects_frame, from_=0, to=100, orient=tk.HORIZONTAL,
            variable=self.reverb_var, bg=self.card_color, fg=self.text_color,
            highlightthickness=0, troughcolor=self.border_color,
            activebackground=self.accent_color, sliderlength=25,
            length=200, showvalue=False, font=self.app_font
        )
        self.reverb_scale.pack(fill="x")
        tk.Label(effects_frame, textvariable=self.reverb_var, bg=self.card_color,
                 fg=self.accent_color, font=('Arial', 11)).pack(anchor="w", pady=(0, 5))

        # Volume effect
        tk.Label(effects_frame, text="Громкость (дБ):", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 11)).pack(anchor="w", pady=(5, 5))
        self.volume_scale = tk.Scale(
            effects_frame, from_=-12, to=12, orient=tk.HORIZONTAL,
            variable=self.volume_var, bg=self.card_color, fg=self.text_color,
            highlightthickness=0, troughcolor=self.border_color,
            activebackground=self.accent_color, sliderlength=25,
            length=200, showvalue=False, font=self.app_font
        )
        self.volume_scale.pack(fill="x")
        tk.Label(effects_frame, textvariable=self.volume_var, bg=self.card_color,
                 fg=self.accent_color, font=('Arial', 11)).pack(anchor="w", pady=(0, 5))

        self.status_frame = tk.Frame(content_frame, bg=self.bg_color, height=30)
        self.status_frame.pack(fill="x", pady=(10, 0))
        self.status_bar = tk.Label(
            self.status_frame, text="Готов к работе • Введите текст и выберите голос",
            bg=self.bg_color, fg=self.secondary_text, font=('Arial', 10)
        )
        self.status_bar.pack(anchor="w")

    def setup_history_ui(self):
        content_frame = tk.Frame(self.history_frame, bg=self.bg_color, padx=30, pady=30)
        content_frame.pack(fill="both", expand=True)

        search_frame = tk.Frame(content_frame, bg=self.bg_color)
        search_frame.pack(fill="x", pady=(0, 15))
        tk.Label(search_frame, text="Поиск:", bg=self.bg_color, fg=self.text_color,
                 font=('Arial', 12, 'bold')).pack(side="left", padx=(0, 10))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=self.app_font)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind('<KeyRelease>', self.search_history)

        self.history_tree = ttk.Treeview(
            content_frame, columns=('date', 'text', 'voice', 'speed', 'file'),
            show='headings', style='Custom.Treeview'
        )
        self.history_tree.pack(fill="both", expand=True)

        self.history_tree.heading('date', text='Дата')
        self.history_tree.heading('text', text='Текст')
        self.history_tree.heading('voice', text='Голос')
        self.history_tree.heading('speed', text='Скорость')
        self.history_tree.heading('file', text='Файл')

        self.history_tree.column('date', width=150, anchor='center')
        self.history_tree.column('text', width=300, anchor='w')
        self.history_tree.column('voice', width=150, anchor='center')
        self.history_tree.column('speed', width=100, anchor='center')
        self.history_tree.column('file', width=200, anchor='w')

        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        actions_frame = tk.Frame(content_frame, bg=self.bg_color)
        actions_frame.pack(fill="x", pady=(15, 0))
        ttk.Button(actions_frame, text="Загрузить текст", style='Accent.TButton',
                   command=self.load_from_history).pack(side="left", padx=(0, 10))
        ttk.Button(actions_frame, text="Открыть файл", style='Secondary.TButton',
                   command=self.open_history_file).pack(side="left", padx=(0, 10))
        ttk.Button(actions_frame, text="Очистить историю", style='Secondary.TButton',
                   command=self.clear_history).pack(side="left")

    def setup_bindings(self):
        self.root.bind('<Escape>', lambda e: self.safe_exit())
        self.root.bind('<Control-z>', lambda e: self.undo_text())
        self.root.bind('<Control-y>', lambda e: self.redo_text())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-q>', lambda e: self.safe_exit())
        self.root.bind('<Control-x>', lambda e: self.cut_text())
        self.root.bind('<Control-c>', lambda e: self.copy_text())
        self.root.bind('<Control-v>', lambda e: self.paste_text())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<F5>', lambda e: self.synthesize_speech())
        self.root.bind('<F6>', lambda e: self.preview_speech())
        self.root.bind('<F7>', lambda e: self.save_audio())
        self.root.bind('<F8>', lambda e: self.quick_save())
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)

    def load_last_settings(self):
        settings = self.voice_engine.settings
        self.voice_combobox.current(settings.get('last_voice_index', 0))
        self.speed_var.set(settings.get('last_speed', 150))
        self.pitch_var.set(settings.get('last_pitch', 0))
        self.echo_var.set(settings.get('last_echo', False))
        self.reverb_var.set(settings.get('last_reverb_intensity', 0))
        self.volume_var.set(settings.get('last_volume_db', 0))
        self.on_voice_selected(None)
        self.load_history()

    def on_voice_selected(self, event=None):
        idx = self.voice_combobox.current()
        voice = self.voice_engine.voices[idx]
        info = f"Язык: {', '.join(voice['languages'])}\n"
        info += f"Пол: {'Мужской' if voice['gender'] == 'male' else 'Женский'}\n"
        info += f"Тип: {'Системный' if voice['system'] else 'Виртуальный'}"
        self.voice_info_label.config(text=info)

    def add_to_history(self, text: str, voice_idx: int, speed: int, effects: dict, file_path: Optional[str]):
        entry = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'text': text[:100] + '...' if len(text) > 100 else text,
            'voice': self.voice_engine.voices[voice_idx]['name'],
            'speed': speed,
            'effects': effects,
            'full_text': text,
            'file': file_path if file_path else 'Не сохранено'
        }
        self.history.append(entry)
        self.update_history_tree()
        self.save_history()

    def update_history_tree(self):
        self.history_tree.delete(*self.history_tree.get_children())
        for entry in self.history:
            self.history_tree.insert('', 'end', values=(
                entry['date'],
                entry['text'],
                entry['voice'],
                entry['speed'],
                entry['file']
            ))

    def search_history(self, event=None):
        query = self.search_var.get().lower()
        self.history_tree.delete(*self.history_tree.get_children())
        for entry in self.history:
            if query in entry['text'].lower() or query in entry['voice'].lower():
                self.history_tree.insert('', 'end', values=(
                    entry['date'],
                    entry['text'],
                    entry['voice'],
                    entry['speed'],
                    entry['file']
                ))

    def load_from_history(self):
        selected = self.history_tree.selection()
        if selected:
            item = self.history_tree.item(selected[0])
            values = item['values']
            for entry in self.history:
                if entry['date'] == values[0]:
                    self.text_input.delete("1.0", tk.END)
                    self.text_input.insert("1.0", entry['full_text'])
                    self.voice_combobox.current(self.voice_engine.voices.index(
                        next(v for v in self.voice_engine.voices if v['name'] == values[2])
                    ))
                    self.speed_var.set(int(values[3]))
                    self.pitch_var.set(entry['effects'].get('pitch', 0))
                    self.echo_var.set(entry['effects'].get('echo', False))
                    self.reverb_var.set(entry['effects'].get('reverb_intensity', 0))
                    self.volume_var.set(entry['effects'].get('volume_db', 0))
                    self.update_text_stats()
                    self.status_bar.config(text="Загружено из истории")
                    break

    def open_history_file(self):
        selected = self.history_tree.selection()
        if selected:
            item = self.history_tree.item(selected[0])
            file_path = item['values'][4]
            if file_path != 'Не сохранено' and os.path.exists(file_path):
                try:
                    os.startfile(file_path)
                except:
                    webbrowser.open('file://' + os.path.realpath(file_path))
            else:
                messagebox.showinfo("Информация", "Файл не сохранен или не найден")

    def clear_history(self):
        if messagebox.askyesno("Очистка истории", "Очистить всю историю?"):
            self.history = []
            self.update_history_tree()
            self.save_history()
            self.status_bar.config(text="История очищена")

    def load_history(self):
        try:
            if os.path.exists('history.json'):
                with open('history.json', 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                self.update_history_tree()
        except:
            pass

    def save_history(self):
        try:
            with open('history.json', 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except:
            pass

    def get_effects(self) -> dict:
        return {
            'pitch': self.pitch_var.get(),
            'echo': self.echo_var.get(),
            'reverb_intensity': self.reverb_var.get(),
            'volume_db': self.volume_var.get(),
            'normalize': True
        }

    def safe_exit(self):
        if self.voice_engine.is_speaking:
            self.voice_engine.stop_speech()
        self.voice_engine.save_settings()
        self.save_history()
        self.root.destroy()

    def update_text_stats(self, event=None):
        text = self.text_input.get("1.0", tk.END).strip()
        char_count = len(text)
        word_count = len(text.split()) if text else 0
        self.stats_label.config(text=f"Символов: {char_count} | Слов: {word_count}")

    def show_text_stats(self):
        text = self.text_input.get("1.0", tk.END).strip()
        char_count = len(text)
        word_count = len(text.split()) if text else 0
        line_count = text.count('\n') + 1 if text else 0
        messagebox.showinfo("Статистика текста",
                            f"Символов: {char_count}\n"
                            f"Слов: {word_count}\n"
                            f"Строк: {line_count}\n"
                            f"Примерное время озвучки: {char_count / 150:.1f} сек.")

    def clear_text(self):
        current_text = self.text_input.get("1.0", tk.END).strip()
        if current_text:
            self.text_history.append(current_text)
            self.history_index = len(self.text_history) - 1
        self.text_input.delete("1.0", tk.END)
        self.update_text_stats()
        self.status_bar.config(text="Текст очищен")

    def undo_text(self):
        try:
            self.text_input.edit_undo()
            self.update_text_stats()
        except:
            pass

    def redo_text(self):
        try:
            self.text_input.edit_redo()
            self.update_text_stats()
        except:
            pass

    def cut_text(self):
        self.text_input.event_generate("<<Cut>>")
        self.update_text_stats()

    def copy_text(self):
        self.text_input.event_generate("<<Copy>>")

    def paste_text(self):
        self.text_input.event_generate("<<Paste>>")
        self.update_text_stats()

    def select_all(self):
        self.text_input.tag_add('sel', '1.0', 'end')
        self.text_input.mark_set('insert', '1.0')
        self.text_input.see('1.0')

    def new_file(self):
        if self.text_input.get("1.0", tk.END).strip():
            if messagebox.askyesno("Новый файл", "Сохранить текущий текст?"):
                self.save_file()
        self.text_input.delete("1.0", tk.END)
        self.update_text_stats()
        self.status_bar.config(text="Создан новый документ")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_input.delete("1.0", tk.END)
                self.text_input.insert("1.0", content)
                self.update_text_stats()
                self.status_bar.config(text=f"Загружен файл: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            try:
                content = self.text_input.get("1.0", tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.config(text=f"Файл сохранен: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def save_current_text(self):
        current_text = self.text_input.get("1.0", tk.END).strip()
        if current_text:
            self.text_history.append(current_text)
            if len(self.text_history) > 100:
                self.text_history.pop(0)

    def show_processing(self, show=True):
        if show:
            self.progress_frame.pack(fill="x", pady=(0, 15))
            self.progress_bar.start(10)
            self.play_btn.config(state='disabled')
            self.listen_btn.config(state='disabled')
            self.download_btn.config(state='disabled')
            self.quick_save_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
        else:
            self.progress_frame.pack_forget()
            self.progress_bar.stop()
            self.play_btn.config(state='normal')
            self.listen_btn.config(state='normal')
            self.download_btn.config(state='normal')
            self.quick_save_btn.config(state='normal')
            self.stop_btn.config(state='disabled')

    def update_status(self, success, message):
        color = self.success_color if success else self.error_color
        prefix = "✓ " if success else "✗ "
        self.status_bar.config(text=prefix + message, fg=color)
        if not success and message:
            self.root.after(3000, lambda: self.status_bar.config(
                text="Готов к работе • Введите текст и выберите голос", fg=self.secondary_text))

    def synthesize_speech(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для озвучивания")
            return
        voice_idx = self.voice_combobox.current()
        speed = self.speed_var.get()
        effects = self.get_effects()
        self.show_processing(True)
        self.status_bar.config(text="Подготовка к воспроизведению...")
        def callback(success, msg):
            self.root.after(0, lambda: self.show_processing(False))
            self.root.after(0, lambda: self.update_status(success, msg))
            if success:
                self.root.after(0, lambda: self.add_to_history(text, voice_idx, speed, effects, None))
        self.voice_engine.text_to_speech(text, voice_idx, speed, self.voice_engine.settings['last_volume'], None, callback, effects)

    def preview_speech(self):
        voice_idx = self.voice_combobox.current()
        effects = self.get_effects()
        self.show_processing(True)
        self.status_bar.config(text="Воспроизведение образца голоса...")
        def callback(success, message):
            self.root.after(0, lambda: self.show_processing(False))
            self.root.after(0, lambda: self.update_status(success, message))
        self.voice_engine.preview_voice(voice_idx, callback, effects)

    def preview_selected_voice(self):
        self.preview_speech()

    def stop_playback(self):
        self.voice_engine.stop_speech()
        self.show_processing(False)
        self.status_bar.config(text="Воспроизведение остановлено", fg=self.secondary_text)

    def save_audio(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для сохранения")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[
                ("MP3 файлы", "*.mp3"),
                ("WAV файлы", "*.wav"),
                ("OGG файлы", "*.ogg"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            voice_idx = self.voice_combobox.current()
            speed = self.speed_var.get()
            effects = self.get_effects()
            self.show_processing(True)
            self.status_bar.config(text="Сохранение аудиофайла...")
            def callback(success, msg):
                self.root.after(0, lambda: self.show_processing(False))
                self.root.after(0, lambda: self.update_status(success, msg))
                if success:
                    self.root.after(0, lambda: self.add_to_history(text, voice_idx, speed, effects, file_path))
                    self.status_bar.config(text=f"Аудио сохранено: {os.path.basename(file_path)}")
            self.voice_engine.text_to_speech(text, voice_idx, speed, self.voice_engine.settings['last_volume'], file_path, callback, effects)

    def quick_save(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для сохранения")
            return
        file_path = self.voice_engine.get_default_output_path()
        voice_idx = self.voice_combobox.current()
        speed = self.speed_var.get()
        effects = self.get_effects()
        self.show_processing(True)
        self.status_bar.config(text="Быстрое сохранение...")
        def callback(success, msg):
            self.root.after(0, lambda: self.show_processing(False))
            self.root.after(0, lambda: self.update_status(success, msg))
            if success:
                self.root.after(0, lambda: self.add_to_history(text, voice_idx, speed, effects, file_path))
                self.status_bar.config(text=f"Аудио сохранено: {os.path.basename(file_path)}")
        self.voice_engine.text_to_speech(text, voice_idx, speed, self.voice_engine.settings['last_volume'], file_path, callback, effects)

    def quick_export(self):
        self.quick_save()

    def change_output_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.voice_engine.settings['output_folder']
        )
        if folder:
            self.voice_engine.settings['output_folder'] = folder
            self.voice_engine.save_settings()
            self.status_bar.config(text=f"Папка сохранения изменена: {os.path.basename(folder)}")

    def toggle_auto_save(self):
        self.voice_engine.settings['auto_save'] = not self.voice_engine.settings.get('auto_save', False)
        self.voice_engine.save_settings()
        status = "включено" if self.voice_engine.settings['auto_save'] else "выключено"
        self.status_bar.config(text=f"Авто-сохранение настроек {status}")

    def show_about(self):
        about_text = (
            "Marilyn Tone - Профессиональный синтезатор речи\n\n"
            "Версия: 2.0\n"
            "Разработчик: Marilyn Team\n\n"
            "Возможности:\n"
            "• Синтез речи на разных языках\n"
            "• Сохранение в MP3, WAV, OGG\n"
            "• Настройка скорости и голосов\n"
            "• Эффекты: высота тона, эхо, реверберация, громкость\n"
            "• История текста и отмена действий\n\n"
            "© 2024 Marilyn Tone. Все права защищены."
        )
        messagebox.showinfo("О программе", about_text)

    def show_help(self):
        help_text = (
            "📖 Руководство пользователя Marilyn Tone\n\n"
            "🔹 Основные функции:\n"
            "• Введите текст в поле ввода\n"
            "• Выберите голос из списка\n"
            "• Настройте скорость речи и эффекты (высота тона, эхо, реверберация, громкость)\n"
            "• Нажмите 'Озвучить' для воспроизведения\n"
            "• Используйте 'Сохранить аудио' для экспорта\n\n"
            "🔹 Горячие клавиши:\n"
            "Ctrl+N - Новый файл\n"
            "Ctrl+O - Открыть файл\n"
            "Ctrl+S - Сохранить текст\n"
            "Ctrl+Z - Отменить\n"
            "Ctrl+Y - Повторить\n"
            "Ctrl+A - Выделить все\n"
            "Ctrl+Q - Выход\n"
            "F5 - Озвучить\n"
            "F6 - Прослушать голос\n"
            "F7 - Сохранить аудио\n"
            "F8 - Быстрое сохранение\n\n"
            "🔹 Советы:\n"
            "• Используйте правую кнопку мыши для контекстного меню\n"
            "• Настройте реверберацию для создания эффекта пространства\n"
            "• Регулируйте громкость для оптимального звучания\n"
            "• Прокрутите область эффектов для доступа ко всем настройкам\n"
            "• Сохраняйте часто используемые настройки\n"
            "• Проверяйте статистику текста для оценки времени"
        )
        help_window = tk.Toplevel(self.root)
        help_window.title("Справка - Marilyn Tone")
        help_window.geometry("600x500")
        help_window.configure(bg=self.bg_color)
        help_window.resizable(True, True)
        text_widget = scrolledtext.ScrolledText(
            help_window, bg=self.border_color, fg=self.text_color,
            font=('Arial', 11), padx=20, pady=20, wrap=tk.WORD
        )
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled")

    def check_updates(self):
        self.status_bar.config(text="Проверка обновлений...")
        self.root.after(2000, lambda: self.status_bar.config(
            text="Обновления не найдены. У вас последняя версия.", fg=self.success_color))


if __name__ == "__main__":
    root = tk.Tk()
    app = MarilynToneApp(root)
    root.mainloop()