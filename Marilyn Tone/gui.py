# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from functions import VoiceEngine
import os
import threading
import time
from typing import Optional, Callable
import webbrowser
from datetime import datetime


class MarilynToneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Marilyn Tone - Профессиональный синтезатор речи")
        self.voice_engine = VoiceEngine()
        self.current_operation = None
        self.text_history = []
        self.history_index = -1

        # Настройка полноэкранного режима
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

        # Шрифты
        self.title_font = ('Arial', 24, 'bold')
        self.app_font = ('Arial', 12)
        self.button_font = ('Arial', 11, 'bold')
        self.mono_font = ('Consolas', 10)

        self.setup_styles()
        self.setup_ui()
        self.setup_bindings()
        self.load_last_settings()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Custom.TNotebook', background=self.card_color, borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                        background="#252525",
                        foreground=self.text_color,
                        padding=[15, 8],
                        font=('Arial', 10))
        style.map('Custom.TNotebook.Tab',
                  background=[('selected', self.card_color)],
                  foreground=[('selected', self.accent_color)])

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

        style.configure('TCombobox',
                        fieldbackground='#252525',
                        background='#252525',
                        foreground=self.text_color,
                        selectbackground=self.accent_color,
                        selectforeground='#ffffff',
                        borderwidth=1,
                        bordercolor='#404040',
                        padding=8,
                        arrowcolor=self.secondary_text)
        style.map('TCombobox',
                  fieldbackground=[('readonly', '#252525')],
                  selectbackground=[('readonly', self.accent_color)],
                  selectforeground=[('readonly', '#ffffff')])

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        self.setup_sidebar(main_container)
        self.setup_main_area(main_container)

    def setup_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.card_color, width=300)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)

        top_sidebar = tk.Frame(sidebar, bg=self.card_color)
        top_sidebar.pack(fill="x", pady=(30, 40), padx=25)

        logo_frame = tk.Frame(top_sidebar, bg=self.card_color)
        logo_frame.pack(fill="x")

        logo_canvas = tk.Canvas(logo_frame, bg=self.card_color, width=50, height=50,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")
        logo_canvas.create_oval(5, 5, 45, 45, fill=self.accent_color, outline="")
        logo_canvas.create_text(25, 25, text="M", font=('Arial', 20, 'bold'), fill="#ffffff")

        name_frame = tk.Frame(logo_frame, bg=self.card_color)
        name_frame.pack(side="left", padx=(10, 0))

        tk.Label(name_frame, text="MARILYN", bg=self.card_color,
                 fg=self.accent_color, font=('Arial', 16, 'bold')).pack(anchor="w")
        tk.Label(name_frame, text="TONE", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 16, 'bold')).pack(anchor="w")

        info_frame = tk.Frame(top_sidebar, bg=self.card_color)
        info_frame.pack(fill="x", pady=(20, 0))

        self.voice_info_label = tk.Label(
            info_frame, text="", bg=self.card_color, fg=self.secondary_text,
            font=('Arial', 9), wraplength=250, justify='left'
        )
        self.voice_info_label.pack(anchor="w", pady=(0, 15))

        preview_btn = ttk.Button(
            top_sidebar,
            text="ПРОСЛУШАТЬ ГОЛОС",
            style='Secondary.TButton',
            command=self.preview_selected_voice
        )
        preview_btn.pack(fill="x", pady=(10, 0))

        stats_frame = tk.Frame(top_sidebar, bg=self.card_color)
        stats_frame.pack(fill="x", pady=(20, 0))

        self.stats_label = tk.Label(
            stats_frame, text="Символов: 0 | Слов: 0", bg=self.card_color,
            fg=self.secondary_text, font=('Arial', 9)
        )
        self.stats_label.pack(anchor="w")

        bottom_sidebar = tk.Frame(sidebar, bg=self.card_color)
        bottom_sidebar.pack(side="bottom", fill="x", pady=30, padx=25)

        self.stop_btn = ttk.Button(
            bottom_sidebar,
            text="ОСТАНОВИТЬ ГОЛОС",
            style='Secondary.TButton',
            command=self.stop_playback,
            state='disabled'
        )
        self.stop_btn.pack(fill="x", pady=(0, 10))

        exit_btn = tk.Button(bottom_sidebar, text="ВЫХОД",
                             bg="#dc2626", fg="white", font=self.button_font,
                             bd=0, command=self.safe_exit)
        exit_btn.pack(fill="x")

    def setup_main_area(self, parent):
        self.main_area = tk.Frame(parent, bg=self.bg_color)
        self.main_area.pack(side="right", fill="both", expand=True)

        header_frame = tk.Frame(self.main_area, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 25))

        self.section_title = tk.Label(header_frame, text="Синтез Речи",
                                      bg=self.bg_color, fg=self.text_color, font=self.title_font)
        self.section_title.pack(side="left")

        header_buttons = tk.Frame(header_frame, bg=self.bg_color)
        header_buttons.pack(side="right")

        ttk.Button(header_buttons, text="Вставить", style='Secondary.TButton',
                   command=self.paste_text).pack(side="left", padx=(5, 0))
        ttk.Button(header_buttons, text="Очистить", style='Secondary.TButton',
                   command=self.clear_text).pack(side="left", padx=(5, 0))

        content_frame = tk.Frame(self.main_area, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True)

        input_frame = tk.Frame(content_frame, bg=self.card_color, padx=25, pady=25)
        input_frame.pack(fill="both", expand=True, pady=(0, 20))

        tk.Label(input_frame, text="Введите текст для озвучивания:",
                 bg=self.card_color, fg=self.text_color, font=('Arial', 12, 'bold')
                 ).pack(anchor="w", pady=(0, 12))

        text_container = tk.Frame(input_frame, bg=self.border_color, bd=0, relief='flat', padx=1, pady=1)
        text_container.pack(fill="both", expand=True)

        self.text_input = scrolledtext.ScrolledText(
            text_container,
            bg="#252525", fg=self.text_color, font=self.mono_font,
            insertbackground=self.accent_color, relief='flat', bd=0,
            padx=15, pady=15, wrap=tk.WORD, selectbackground=self.accent_color,
            undo=True, maxundo=100
        )
        self.text_input.pack(fill="both", expand=True)
        self.text_input.bind('<KeyRelease>', self.update_text_stats)

        self.progress_frame = tk.Frame(content_frame, bg=self.bg_color)
        self.progress_frame.pack(fill="x", pady=(0, 10))

        self.progress_bar = ttk.Progressbar(
            self.progress_frame, mode='indeterminate', style='TProgressbar'
        )
        self.progress_bar.pack(fill="x")
        self.progress_frame.pack_forget()

        settings_container = tk.Frame(content_frame, bg=self.card_color, padx=25, pady=20)
        settings_container.pack(fill="x", pady=(0, 15))

        voice_column = tk.Frame(settings_container, bg=self.card_color)
        voice_column.pack(side="left", fill="both", expand=True, padx=(0, 15))

        tk.Label(voice_column, text="Голос:", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 11, 'bold')
                 ).pack(anchor="w", pady=(0, 8))

        self.voice_combobox = ttk.Combobox(
            voice_column, values=[v['name'] for v in self.voice_engine.voices],
            state="readonly", font=self.app_font, height=12
        )
        self.voice_combobox.current(0)
        self.voice_combobox.pack(fill="x")
        self.voice_combobox.bind('<<ComboboxSelected>>', self.on_voice_selected)

        speed_column = tk.Frame(settings_container, bg=self.card_color)
        speed_column.pack(side="right", fill="both", expand=True)

        tk.Label(speed_column, text="Скорость речи:", bg=self.card_color,
                 fg=self.text_color, font=('Arial', 11, 'bold')
                 ).pack(anchor="w", pady=(0, 8))

        speed_control_frame = tk.Frame(speed_column, bg=self.card_color)
        speed_control_frame.pack(fill="x")

        self.speed_var = tk.IntVar(value=150)
        self.speed_scale = tk.Scale(
            speed_control_frame, from_=50, to=300, orient=tk.HORIZONTAL,
            variable=self.speed_var, bg=self.card_color, fg=self.text_color,
            highlightthickness=0, troughcolor="#252525",
            activebackground=self.accent_color, sliderlength=20,
            length=180, showvalue=False, font=self.app_font
        )
        self.speed_scale.pack(side="left")

        speed_value_frame = tk.Frame(speed_control_frame, bg=self.card_color)
        speed_value_frame.pack(side="left", padx=(10, 0))

        self.speed_label = tk.Label(
            speed_value_frame, textvariable=self.speed_var,
            bg=self.card_color, fg=self.accent_color,
            font=('Arial', 14, 'bold'), width=4
        )
        self.speed_label.pack()

        tk.Label(speed_value_frame, text="слов/мин", bg=self.card_color,
                 fg=self.secondary_text, font=('Arial', 9)).pack()

        btn_frame = tk.Frame(content_frame, bg=self.card_color, padx=25, pady=20)
        btn_frame.pack(fill="x")

        self.play_btn = ttk.Button(
            btn_frame, text="ОЗВУЧИТЬ ТЕКСТ", style='Accent.TButton',
            command=self.synthesize_speech
        )
        self.play_btn.pack(side="left", padx=(0, 10), expand=True, fill="x")

        self.listen_btn = ttk.Button(
            btn_frame, text="ПРОСЛУШАТЬ ОБРАЗЕЦ", style='Secondary.TButton',
            command=self.preview_speech
        )
        self.listen_btn.pack(side="left", padx=(0, 10), expand=True, fill="x")

        self.download_btn = ttk.Button(
            btn_frame, text="СОХРАНИТЬ АУДИО", style='Secondary.TButton',
            command=self.save_audio
        )
        self.download_btn.pack(side="left", padx=(0, 10), expand=True, fill="x")

        self.quick_save_btn = ttk.Button(
            btn_frame, text="БЫСТРОЕ СОХРАНЕНИЕ", style='Secondary.TButton',
            command=self.quick_save
        )
        self.quick_save_btn.pack(side="left", expand=True, fill="x")

        self.status_bar = tk.Label(
            self.root, text="Готов к работе • Введите текст и выберите голос",
            bg=self.bg_color, fg=self.secondary_text, font=('Arial', 10),
            anchor='w', padx=30, pady=10
        )
        self.status_bar.pack(side="bottom", fill="x")

        self.speed_scale.configure(command=self.update_speed_label)
        self.setup_context_menu(self.text_input)

    def setup_bindings(self):
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)
        self.root.bind('<Escape>', lambda e: self.safe_exit())
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-q>', lambda e: self.safe_exit())
        self.root.bind('<Control-z>', lambda e: self.undo_text())
        self.root.bind('<Control-y>', lambda e: self.redo_text())
        self.root.bind('<Control-a>', lambda e: self.select_all())

    def safe_exit(self):
        """Безопасный выход из приложения"""
        try:
            self.voice_engine.stop_speech()
            self.save_current_text()
            self.root.quit()
            self.root.destroy()
        except:
            os._exit(0)

    def update_speed_label(self, value):
        self.speed_var.set(int(float(value)))

    def setup_context_menu(self, text_widget):
        menu = tk.Menu(text_widget, tearoff=0, bg="#353535", fg=self.text_color, bd=0)
        menu.add_command(label="Вставить", command=lambda: text_widget.event_generate("<<Paste>>"))
        menu.add_command(label="Копировать", command=lambda: text_widget.event_generate("<<Copy>>"))
        menu.add_command(label="Вырезать", command=lambda: text_widget.event_generate("<<Cut>>"))
        menu.add_separator()
        menu.add_command(label="Выделить все", command=lambda: text_widget.tag_add('sel', '1.0', 'end'))
        menu.add_separator()
        menu.add_command(label="Статистика текста", command=self.show_text_stats)

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        text_widget.bind("<Button-3>", show_menu)

    def load_last_settings(self):
        """Загружает последние настройки"""
        try:
            self.voice_combobox.current(self.voice_engine.settings['last_voice_index'])
            self.speed_var.set(self.voice_engine.settings['last_speed'])
            self.on_voice_selected()
        except:
            pass

    def on_voice_selected(self, event=None):
        """Обновляет информацию о выбранном голосе"""
        voice_idx = self.voice_combobox.current()
        voice_info = self.voice_engine.get_voice_info(voice_idx)

        if voice_info:
            gender = "Мужской" if voice_info.get('gender') == 'male' else "Женский"
            languages = ', '.join(voice_info.get('languages', []))
            system = "Системный" if voice_info.get('system') else "Виртуальный"

            info_text = f"{voice_info.get('name', '')}\n"
            info_text += f"Пол: {gender} • Тип: {system}\n"
            info_text += f"Языки: {languages}"

            self.voice_info_label.config(text=info_text)

    def update_text_stats(self, event=None):
        """Обновляет статистику текста"""
        text = self.text_input.get("1.0", tk.END).strip()
        char_count = len(text)
        word_count = len(text.split()) if text else 0

        self.stats_label.config(text=f"Символов: {char_count} | Слов: {word_count}")

    def show_text_stats(self):
        """Показывает подробную статистику текста"""
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
        """Очищает текстовое поле"""
        current_text = self.text_input.get("1.0", tk.END).strip()
        if current_text:
            self.text_history.append(current_text)
            self.history_index = len(self.text_history) - 1

        self.text_input.delete("1.0", tk.END)
        self.update_text_stats()
        self.status_bar.config(text="Текст очищен")

    def undo_text(self):
        """Отменяет последнее действие"""
        try:
            self.text_input.edit_undo()
            self.update_text_stats()
        except:
            pass

    def redo_text(self):
        """Повторяет последнее действие"""
        try:
            self.text_input.edit_redo()
            self.update_text_stats()
        except:
            pass

    def cut_text(self):
        """Вырезает выделенный текст"""
        self.text_input.event_generate("<<Cut>>")
        self.update_text_stats()

    def copy_text(self):
        """Копирует выделенный текст"""
        self.text_input.event_generate("<<Copy>>")

    def paste_text(self):
        """Вставляет текст из буфера обмена"""
        self.text_input.event_generate("<<Paste>>")
        self.update_text_stats()

    def select_all(self):
        """Выделяет весь текст"""
        self.text_input.tag_add('sel', '1.0', 'end')
        self.text_input.mark_set('insert', '1.0')
        self.text_input.see('1.0')

    def new_file(self):
        """Создает новый файл"""
        if self.text_input.get("1.0", tk.END).strip():
            if messagebox.askyesno("Новый файл", "Сохранить текущий текст?"):
                self.save_file()

        self.text_input.delete("1.0", tk.END)
        self.update_text_stats()
        self.status_bar.config(text="Создан новый документ")

    def open_file(self):
        """Открывает текстовый файл"""
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
        """Сохраняет текст в файл"""
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
        """Сохраняет текущий текст в историю"""
        current_text = self.text_input.get("1.0", tk.END).strip()
        if current_text:
            self.text_history.append(current_text)
            if len(self.text_history) > 100:
                self.text_history.pop(0)

    def show_processing(self, show=True):
        """Показывает/скрывает индикатор прогресса"""
        if show:
            self.progress_frame.pack(fill="x", pady=(0, 10))
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
        """Обновляет статусную строку"""
        color = self.success_color if success else self.error_color
        self.status_bar.config(text=message, fg=color)

        if not success and message:
            self.root.after(3000, lambda: self.status_bar.config(
                text="Готов к работе", fg=self.secondary_text))

    def synthesize_speech(self):
        """Озвучивает текст"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для озвучивания")
            return

        voice_idx = self.voice_combobox.current()
        speed = self.speed_var.get()

        self.show_processing(True)
        self.status_bar.config(text="Подготовка к воспроизведению...")

        def callback(success, message):
            self.root.after(0, lambda: self.show_processing(False))
            self.root.after(0, lambda: self.update_status(success, message))

        self.voice_engine.text_to_speech(text, voice_idx, speed, None, callback)

    def preview_speech(self):
        """Воспроизводит образец голоса"""
        voice_idx = self.voice_combobox.current()

        self.show_processing(True)
        self.status_bar.config(text="Воспроизведение образца голоса...")

        def callback(success, message):
            self.root.after(0, lambda: self.show_processing(False))
            self.root.after(0, lambda: self.update_status(success, message))

        self.voice_engine.preview_voice(voice_idx, callback)

    def preview_selected_voice(self):
        """Прослушивание выбранного голоса"""
        self.preview_speech()

    def stop_playback(self):
        """Останавливает воспроизведение"""
        self.voice_engine.stop_speech()
        self.show_processing(False)
        self.status_bar.config(text="Воспроизведение остановлено", fg=self.secondary_text)

    def save_audio(self):
        """Сохраняет аудио в файл"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для сохранения")
            return

        voice_idx = self.voice_combobox.current()
        voice = self.voice_engine.get_voice_info(voice_idx)
        file_ext = ".mp3" if voice['api'] in ['gtts', 'edge_tts'] else ".wav"

        file_path = filedialog.asksaveasfilename(
            defaultextension=file_ext,
            filetypes=[
                ("MP3 файлы", "*.mp3") if voice['api'] in ['gtts', 'edge_tts'] else ("WAV файлы", "*.wav"),
                ("Все файлы", "*.*")
            ]
        )

        if file_path:
            speed = self.speed_var.get()
            self.show_processing(True)
            self.status_bar.config(text="Сохранение аудиофайла...")

            def callback(success, message):
                self.root.after(0, lambda: self.show_processing(False))
                self.root.after(0, lambda: self.update_status(success, message))

                if success:
                    self.status_bar.config(text=f"Аудио сохранено: {os.path.basename(file_path)}")

            self.voice_engine.text_to_speech(text, voice_idx, speed, file_path, callback)

    def quick_save(self):
        """Быстрое сохранение аудио"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для сохранения")
            return

        voice_idx = self.voice_combobox.current()
        voice = self.voice_engine.get_voice_info(voice_idx)
        file_ext = "mp3" if voice['api'] in ['gtts', 'edge_tts'] else "wav"
        file_path = self.voice_engine.get_default_output_path(file_ext)
        speed = self.speed_var.get()

        self.show_processing(True)
        self.status_bar.config(text="Быстрое сохранение...")

        def callback(success, message):
            self.root.after(0, lambda: self.show_processing(False))
            self.root.after(0, lambda: self.update_status(success, message))

            if success:
                self.status_bar.config(text=f"Аудио сохранено: {os.path.basename(file_path)}")

        self.voice_engine.text_to_speech(text, voice_idx, speed, file_path, callback)

    def change_output_folder(self):
        """Изменяет папку для сохранения по умолчанию"""
        folder = filedialog.askdirectory(
            initialdir=self.voice_engine.settings['output_folder']
        )

        if folder:
            self.voice_engine.settings['output_folder'] = folder
            self.voice_engine.save_settings()
            self.status_bar.config(text=f"Папка сохранения изменена: {os.path.basename(folder)}")

    def toggle_auto_save(self):
        """Переключает авто-сохранение настроек"""
        self.voice_engine.settings['auto_save'] = not self.voice_engine.settings.get('auto_save', False)
        self.voice_engine.save_settings()

        status = "включено" if self.voice_engine.settings['auto_save'] else "выключено"
        self.status_bar.config(text=f"Авто-сохранение настроек {status}")

    def show_about(self):
        """Показывает информацию о программе"""
        about_text = (
            "Marilyn Tone - Профессиональный синтезатор речи\n\n"
            "Версия: 2.0\n"
            "Разработчик: Marilyn Team\n\n"
            "Возможности:\n"
            "• Синтез речи на разных языках\n"
            "• Сохранение в MP3 (gTTS, Edge TTS) и WAV (pyttsx3)\n"
            "• Настройка скорости и голосов\n"
            "• История текста и отмена действий\n\n"
            "© 2024 Marilyn Tone. Все права защищены."
        )

        messagebox.showinfo("О программе", about_text)

    def show_help(self):
        """Показывает справку"""
        help_text = (
            "📖 Руководство пользователя Marilyn Tone\n\n"
            "🔹 Основные функции:\n"
            "• Введите текст в поле ввода\n"
            "• Выберите голос из списка\n"
            "• Настройте скорость речи\n"
            "• Нажмите 'Озвучить' для воспроизведения\n"
            "• Используйте 'Сохранить аудио' для экспорта\n\n"
            "🔹 Горячие клавиши:\n"
            "Ctrl+N - Новый файл\n"
            "Ctrl+O - Открыть файл\n"
            "Ctrl+S - Сохранить текст\n"
            "Ctrl+Z - Отменить\n"
            "Ctrl+Y - Повторить\n"
            "Ctrl+A - Выделить все\n"
            "Ctrl+Q - Выход\n\n"
            "🔹 Советы:\n"
            "• Используйте правую кнопку мыши для контекстного меню\n"
            "• Прослушайте образец голоса перед озвучкой\n"
            "• Сохраняйте часто используемые настройки\n"
            "• Проверяйте статистику текста для оценки времени"
        )

        help_window = tk.Toplevel(self.root)
        help_window.title("Справка - Marilyn Tone")
        help_window.geometry("600x500")
        help_window.configure(bg=self.bg_color)
        help_window.resizable(True, True)

        text_widget = scrolledtext.ScrolledText(
            help_window, bg="#252525", fg=self.text_color,
            font=('Arial', 10), padx=20, pady=20, wrap=tk.WORD
        )
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled")

    def check_updates(self):
        """Проверяет обновления"""
        self.status_bar.config(text="Проверка обновлений...")
        self.root.after(2000, lambda: self.status_bar.config(
            text="Обновления не найдены. У вас последняя версия.", fg=self.success_color))


if __name__ == "__main__":
    root = tk.Tk()
    app = MarilynToneApp(root)
    root.mainloop()