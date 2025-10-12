# gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import random
from functions import DAWEngine


class ModernChopinKeysGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chopin Keys")

        # Полноэкранный режим
        self.root.attributes('-fullscreen', True)


        # Цветовая палитра Fibonacci
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#2d3748"

        self.root.configure(bg=self.bg_color)

        # Инициализация движка DAW
        self.daw = DAWEngine(self)

        # Переменные состояния
        self.current_project = None
        self.tracks = []
        self.selected_track = 0
        self.is_playing = False
        self.is_recording = False
        self.playback_position = 0
        self.total_length = 300
        self.bpm = 120
        self.current_instrument = "Piano"
        self.mixer_channels = []

        # Создание интерфейса
        self.setup_styles()
        self.setup_ui()
        self.load_demo_project()
        self.update_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Dark.TFrame', background=self.card_color)
        style.configure('Dark.TLabel', background=self.card_color, foreground=self.text_color)
        style.configure('Dark.TButton', background='#2d3748', foreground=self.text_color)
        style.configure('Accent.TButton', background=self.accent_color, foreground='white')
        style.configure('Play.TButton', background='#10b981', foreground='white')
        style.configure('Stop.TButton', background='#ef4444', foreground='white')
        style.configure('Record.TButton', background='#dc2626', foreground='white')

    def setup_ui(self):
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Верхняя панель
        self.create_top_bar(main_container)

        # Основная рабочая область
        self.create_workspace(main_container)

        # Нижняя панель транспорта
        self.create_transport_bar(main_container)

        # Боковая панель
        self.create_sidebar(main_container)

        # Создание главного меню
        self.create_main_menu()

    def create_main_menu(self):
        menubar = tk.Menu(self.root, bg=self.card_color, fg=self.text_color)
        self.root.config(menu=menubar)

        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый проект", command=self.daw.new_project)
        file_menu.add_command(label="Открыть...", command=self.daw.open_project)
        file_menu.add_command(label="Сохранить", command=self.daw.save_project)
        file_menu.add_command(label="Сохранить как...", command=self.daw.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Импорт MIDI", command=self.daw.import_midi)
        file_menu.add_command(label="Импорт Аудио", command=self.daw.import_audio)
        file_menu.add_command(label="Экспорт MIDI", command=self.daw.export_midi)
        file_menu.add_command(label="Экспорт WAV", command=self.daw.export_wav)
        file_menu.add_separator()
        file_menu.add_command(label="Настройки", command=self.daw.open_settings)
        file_menu.add_command(label="Выход", command=self.daw.exit_app)

        # Меню Правка
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Отменить", command=self.daw.undo)
        edit_menu.add_command(label="Повторить", command=self.daw.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.daw.cut)
        edit_menu.add_command(label="Копировать", command=self.daw.copy)
        edit_menu.add_command(label="Вставить", command=self.daw.paste)
        edit_menu.add_command(label="Удалить", command=self.daw.delete)
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить все", command=self.daw.select_all)

        # Меню Трек
        track_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color)
        menubar.add_cascade(label="Трек", menu=track_menu)
        track_menu.add_command(label="Добавить трек", command=self.daw.add_track)
        track_menu.add_command(label="Удалить трек", command=self.daw.delete_track)
        track_menu.add_command(label="Дублировать трек", command=self.daw.duplicate_track)
        track_menu.add_separator()
        track_menu.add_command(label="Настройки трека", command=self.daw.track_settings)
        track_menu.add_command(label="Автоматизация", command=self.daw.open_automation)

        # Меню Паттерны
        pattern_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color)
        menubar.add_cascade(label="Паттерны", menu=pattern_menu)
        pattern_menu.add_command(label="Новый паттерн", command=self.daw.new_pattern)
        pattern_menu.add_command(label="Дублировать паттерн", command=self.daw.duplicate_pattern)
        pattern_menu.add_command(label="Удалить паттерн", command=self.daw.delete_pattern)

        # Меню Инструменты
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Пианино", command=self.daw.open_piano)
        tools_menu.add_command(label="Барабанная машина", command=self.daw.open_drum_machine)
        tools_menu.add_command(label="Секвенсор", command=self.daw.open_sequencer)
        tools_menu.add_command(label="Микшер", command=self.daw.open_mixer)
        tools_menu.add_command(label="Плейлист", command=self.daw.open_playlist)
        tools_menu.add_command(label="Пианино ролл", command=self.daw.open_piano_roll)

        # Меню Эффекты
        effects_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color)
        menubar.add_cascade(label="Эффекты", menu=effects_menu)
        for effect in self.daw.effects_list:
            effects_menu.add_command(label=effect, command=lambda e=effect: self.daw.add_effect_to_selected_track(e))

        # Меню Помощь
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.card_color, fg=self.text_color)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="Справка", command=self.daw.show_help)
        help_menu.add_command(label="О программе", command=self.daw.about)

    def create_top_bar(self, parent):
        top_bar = tk.Frame(parent, bg=self.card_color, height=60)
        top_bar.pack(fill="x", pady=(0, 10))
        top_bar.pack_propagate(False)

        # Логотип
        logo_frame = tk.Frame(top_bar, bg=self.card_color)
        logo_frame.pack(side="left", padx=20)

        tk.Label(logo_frame, text="🎹", bg=self.card_color, fg=self.accent_color,
                 font=('Arial', 24)).pack(side="left")
        tk.Label(logo_frame, text="Chopin Keys", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 16, 'bold')).pack(side="left", padx=(10, 0))

        # Кнопки быстрого доступа
        toolbar = tk.Frame(top_bar, bg=self.card_color)
        toolbar.pack(side="right", padx=20)

        buttons = [
            ("📄", self.daw.new_project, 'Dark.TButton'),
            ("📂", self.daw.open_project, 'Dark.TButton'),
            ("💾", self.daw.save_project, 'Dark.TButton'),
            ("🔍", self.daw.open_ai_assistant, 'Dark.TButton'),
            ("⚙️", self.daw.open_settings, 'Dark.TButton')
        ]

        for icon, command, style in buttons:
            btn = ttk.Button(toolbar, text=icon, command=command, style=style, width=3)
            btn.pack(side="left", padx=2)

    def create_workspace(self, parent):
        workspace = tk.Frame(parent, bg=self.bg_color)
        workspace.pack(fill="both", expand=True)

        # Создание вкладок
        self.notebook = ttk.Notebook(workspace)
        self.notebook.pack(fill="both", expand=True)

        # Вкладка плейлиста
        self.setup_playlist_tab()

        # Вкладка пианино ролла
        self.setup_piano_roll_tab()

        # Вкладка секвенсора
        self.setup_sequencer_tab()

        # Вкладка микшера
        self.setup_mixer_tab()

        # Вкладка браузера
        self.setup_browser_tab()

    def setup_playlist_tab(self):
        playlist_frame = tk.Frame(self.notebook, bg=self.card_color)
        self.notebook.add(playlist_frame, text="🎵 Плейлист")

        # Холст плейлиста
        canvas_frame = tk.Frame(playlist_frame, bg=self.card_color)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.playlist_canvas = tk.Canvas(canvas_frame, bg='#252525', scrollregion=(0, 0, 2000, 1000))

        v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.playlist_canvas.yview)
        h_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.playlist_canvas.xview)

        self.playlist_canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.playlist_canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.draw_playlist()

    def setup_piano_roll_tab(self):
        piano_frame = tk.Frame(self.notebook, bg=self.card_color)
        self.notebook.add(piano_frame, text="🎹 Пианино ролл")

        # Сетка пианино ролла
        grid_frame = tk.Frame(piano_frame, bg=self.card_color)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Вертикальная линейка с нотами
        note_frame = tk.Frame(grid_frame, bg='#252525', width=60)
        note_frame.pack(side="left", fill="y")
        note_frame.pack_propagate(False)

        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        for i in range(36, 84):
            note_index = i % 12
            octave = i // 12
            lbl = tk.Label(note_frame, text=f"{notes[note_index]}{octave}",
                           bg='#252525', fg=self.text_color, font=('Arial', 8))
            lbl.pack(anchor="w", padx=5, pady=1)

        # Основная область с сеткой
        main_area = tk.Frame(grid_frame, bg=self.card_color)
        main_area.pack(side="right", fill="both", expand=True)

        self.piano_canvas = tk.Canvas(main_area, bg='#252525')
        self.piano_canvas.pack(fill="both", expand=True)

        self.draw_piano_roll()

    def setup_sequencer_tab(self):
        seq_frame = tk.Frame(self.notebook, bg=self.card_color)
        self.notebook.add(seq_frame, text="🎚️ Секвенсор")

        # Создаем сетку секвенсора 16x16
        grid_frame = tk.Frame(seq_frame, bg=self.card_color)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.sequencer_buttons = []
        for i in range(16):
            row = []
            for j in range(16):
                btn = tk.Button(grid_frame, text="", bg='#252525', fg=self.text_color,
                                width=2, height=1, relief="raised",
                                command=lambda r=i, c=j: self.daw.toggle_sequencer_step(r, c))
                btn.grid(row=i, column=j, padx=1, pady=1)
                row.append(btn)
            self.sequencer_buttons.append(row)

    def setup_mixer_tab(self):
        mixer_frame = tk.Frame(self.notebook, bg=self.card_color)
        self.notebook.add(mixer_frame, text="🎚️ Микшер")

        # Создаем каналы микшера
        channels_frame = tk.Frame(mixer_frame, bg=self.card_color)
        channels_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.mixer_channels = []
        for i in range(8):
            channel = self.create_mixer_channel(channels_frame, i)
            channel['frame'].grid(row=0, column=i, padx=5)
            self.mixer_channels.append(channel)

    def create_mixer_channel(self, parent, channel_num):
        channel_frame = tk.Frame(parent, bg=self.card_color, width=80)
        channel_frame.pack_propagate(False)

        # Заголовок канала
        tk.Label(channel_frame, text=f"Ch {channel_num + 1}", bg=self.card_color,
                 fg=self.text_color).pack(pady=(5, 10))

        # VU метр
        vu_frame = tk.Frame(channel_frame, bg='#252525', height=150, width=20)
        vu_frame.pack_propagate(False)
        vu_frame.pack(pady=5)

        vu_meter = tk.Canvas(vu_frame, bg='#252525', highlightthickness=0)
        vu_meter.pack(fill="both", expand=True)

        # Ползунок громкости
        volume = tk.DoubleVar(value=0.8)
        volume_scale = tk.Scale(channel_frame, variable=volume, from_=0, to=1,
                                resolution=0.01, orient="vertical", length=150,
                                bg=self.card_color, fg=self.text_color,
                                troughcolor='#252525')
        volume_scale.pack(pady=5)

        # Кнопки Mute/Solo
        btn_frame = tk.Frame(channel_frame, bg=self.card_color)
        btn_frame.pack(pady=5)

        mute_var = tk.BooleanVar()
        solo_var = tk.BooleanVar()

        mute_btn = tk.Checkbutton(btn_frame, text="M", variable=mute_var,
                                  bg=self.card_color, fg=self.text_color,
                                  selectcolor='#dc2626')
        mute_btn.grid(row=0, column=0, padx=2)

        solo_btn = tk.Checkbutton(btn_frame, text="S", variable=solo_var,
                                  bg=self.card_color, fg=self.text_color,
                                  selectcolor='#10b981')
        solo_btn.grid(row=0, column=1, padx=2)

        # Кнопка эффектов
        effects_btn = tk.Button(channel_frame, text="FX", bg='#252525',
                                fg=self.text_color, width=6,
                                command=lambda: self.daw.open_channel_effects(channel_num))
        effects_btn.pack(pady=5)

        return {
            'frame': channel_frame,
            'volume': volume,
            'mute': mute_var,
            'solo': solo_var,
            'vu_meter': vu_meter
        }

    def setup_browser_tab(self):
        browser_frame = tk.Frame(self.notebook, bg=self.card_color)
        self.notebook.add(browser_frame, text="📁 Браузер")

        # Браузер файлов и инструментов
        tree_frame = tk.Frame(browser_frame, bg=self.card_color)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree = ttk.Treeview(tree_frame)
        tree.pack(fill="both", expand=True)

        # Добавляем примерные элементы
        tree.insert("", "end", text="Инструменты", values=("folder",))
        tree.insert("", "end", text="Сэмплы", values=("folder",))
        tree.insert("", "end", text="Эффекты", values=("folder",))
        tree.insert("", "end", text="Проекты", values=("folder",))

    def create_transport_bar(self, parent):
        transport = tk.Frame(parent, bg=self.card_color, height=80)
        transport.pack(fill="x", pady=(10, 0))
        transport.pack_propagate(False)

        # Левая часть - BPM и позиция
        left_frame = tk.Frame(transport, bg=self.card_color)
        left_frame.pack(side="left", padx=20)

        # BPM контрол
        bpm_frame = tk.Frame(left_frame, bg=self.card_color)
        bpm_frame.pack()

        tk.Label(bpm_frame, text="BPM:", bg=self.card_color,
                 fg=self.text_color).pack(side="left")

        self.bpm_var = tk.IntVar(value=self.bpm)
        bpm_spin = tk.Spinbox(bpm_frame, from_=30, to=240, width=5,
                              textvariable=self.bpm_var, bg='#252525',
                              fg=self.text_color, insertbackground=self.text_color)
        bpm_spin.pack(side="left", padx=5)
        bpm_spin.bind('<Return>', lambda e: self.daw.update_bpm())

        # Позиция воспроизведения
        pos_frame = tk.Frame(left_frame, bg=self.card_color)
        pos_frame.pack(pady=(10, 0))

        self.position_slider = tk.Scale(pos_frame, from_=0, to=self.total_length,
                                        orient="horizontal", length=300,
                                        bg=self.card_color, fg=self.text_color,
                                        troughcolor='#252525')
        self.position_slider.pack()

        # Центральная часть - кнопки транспорта
        center_frame = tk.Frame(transport, bg=self.card_color)
        center_frame.pack(side="left", expand=True)

        transport_buttons = [
            ("⏮️", self.daw.rewind, 'Dark.TButton'),
            ("▶️", self.daw.play, 'Play.TButton'),
            ("⏸️", self.daw.pause, 'Dark.TButton'),
            ("⏹️", self.daw.stop, 'Stop.TButton'),
            ("⏺️", self.daw.record, 'Record.TButton')
        ]

        for icon, command, style in transport_buttons:
            btn = ttk.Button(center_frame, text=icon, command=command, style=style, width=4)
            btn.pack(side="left", padx=5)

        # Правая часть - индикаторы
        right_frame = tk.Frame(transport, bg=self.card_color)
        right_frame.pack(side="right", padx=20)

        # Индикатор записи
        self.record_indicator = tk.Label(right_frame, text="● REC", fg='#dc2626',
                                         bg=self.card_color, font=('Arial', 12, 'bold'))
        self.record_indicator.pack()

        # Индикатор воспроизведения
        self.play_indicator = tk.Label(right_frame, text="▶ PLAY", fg='#10b981',
                                       bg=self.card_color, font=('Arial', 12, 'bold'))
        self.play_indicator.pack()

    def create_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.card_color, width=250)
        sidebar.pack(side="right", fill="y", padx=(10, 0))
        sidebar.pack_propagate(False)

        # Инструменты
        tk.Label(sidebar, text="🎵 Инструменты", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 12, 'bold')).pack(pady=(20, 10))

        instruments = ["Piano", "Guitar", "Bass", "Drums", "Strings", "Synth"]
        for instr in instruments:
            btn = tk.Button(sidebar, text=instr, bg='#252525', fg=self.text_color,
                            width=20, height=2, relief="flat",
                            command=lambda i=instr: self.daw.select_instrument(i))
            btn.pack(pady=2)

        # Эффекты
        tk.Label(sidebar, text="🎛️ Эффекты", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 12, 'bold')).pack(pady=(20, 10))

        for effect in self.daw.effects_list[:5]:  # Показываем первые 5 эффектов
            btn = tk.Button(sidebar, text=effect, bg='#252525', fg=self.text_color,
                            width=20, height=1, relief="flat",
                            command=lambda e=effect: self.daw.add_effect(e))
            btn.pack(pady=1)

    def draw_playlist(self):
        self.playlist_canvas.delete("all")

        # Рисуем временную линейку
        for i in range(0, self.total_length + 1, 10):
            x = i * 10
            self.playlist_canvas.create_line(x, 0, x, 30, fill=self.border_color)
            self.playlist_canvas.create_text(x + 5, 15, text=str(i), fill=self.text_color, font=('Arial', 8))

        # Рисуем дорожки
        for i, track in enumerate(self.tracks):
            y = 40 + i * 60
            # Заголовок дорожки
            self.playlist_canvas.create_rectangle(0, y, 2000, y + 40, fill='#252525', outline=self.border_color)
            self.playlist_canvas.create_text(50, y + 20, text=track, fill=self.text_color, font=('Arial', 10, 'bold'))

            # Клипы на дорожке
            clip_start = random.randint(0, self.total_length - 20)
            clip_end = clip_start + random.randint(10, 50)

            # Красивый клип с закругленными углами (симулируем)
            self.playlist_canvas.create_rectangle(clip_start * 10, y + 5, clip_end * 10, y + 35,
                                                  fill=self.accent_color, outline='', width=0)

            # Добавляем текст названия клипа
            self.playlist_canvas.create_text((clip_start * 10 + clip_end * 10) // 2, y + 20,
                                             text=f"{track} Clip", fill='white', font=('Arial', 8))

    def draw_piano_roll(self):
        self.piano_canvas.delete("all")

        # Рисуем сетку
        for i in range(0, 2000, 50):
            self.piano_canvas.create_line(i, 0, i, 1000, fill='#444')
        for i in range(0, 1000, 20):
            self.piano_canvas.create_line(0, i, 2000, i, fill='#444')

        # Рисуем MIDI ноты
        for _ in range(20):
            start_x = random.randint(0, 1900)
            start_y = random.randint(0, 900)
            length = random.randint(50, 200)
            note_height = 15

            # Красивые ноты с градиентом (симулируем)
            self.piano_canvas.create_rectangle(start_x, start_y, start_x + length, start_y + note_height,
                                               fill=self.accent_color, outline='', width=0)

    def update_playlist(self):
        self.draw_playlist()

    def load_demo_project(self):
        self.current_project = "Демо проект"
        self.tracks = ["Бас", "Барабаны", "Пианино", "Синтезатор", "Вокал"]
        self.update_playlist()

    def update_ui(self):
        # Обновляем индикаторы
        if self.is_recording:
            self.record_indicator.config(fg='#dc2626')
        else:
            self.record_indicator.config(fg='#666')

        if self.is_playing:
            self.play_indicator.config(fg='#10b981')
        else:
            self.play_indicator.config(fg='#666')

        # Обновляем позицию
        if self.is_playing:
            self.playback_position += 0.1
            if self.playback_position > self.total_length:
                self.playback_position = 0
            self.position_slider.set(self.playback_position)

        # Планируем следующее обновление
        self.root.after(100, self.update_ui)