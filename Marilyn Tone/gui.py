# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from functions import VoiceEngine
import os


class MarilynToneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Marilyn Tone - Text to Speech")
        self.voice_engine = VoiceEngine()

        # Устанавливаем полноэкранный режим и запрещаем выход
        self.root.attributes('-fullscreen', True)
        self.fullscreen_state = True
        # Убираем привязки клавиш для выхода из полноэкранного режима
        self.root.bind("<F11>", lambda e: "break")  # Блокируем F11
        self.root.bind("<Escape>", lambda e: "break")  # Блокируем Escape

        # Цветовая палитра в стиле Möbius
        self.bg_color = "#0a0a0a"
        self.card_color = "#1e1e1e"
        self.accent_color = "#ff4df0"  # Розовый акцент Marilyn Tone
        self.secondary_color = "#a29bfe"
        self.text_color = "#f0f0f0"
        self.secondary_text = "#909090"
        self.disabled_color = "#404040"

        # Шрифты
        self.title_font = ('Segoe UI', 24, 'bold')
        self.app_font = ('Segoe UI', 11)
        self.button_font = ('Segoe UI', 12, 'bold')
        self.mono_font = ('Consolas', 10)

        self.setup_ui()

    def toggle_fullscreen(self, event=None):
        # Запрещаем переключение полноэкранного режима
        return "break"

    def exit_fullscreen(self, event=None):
        # Запрещаем выход из полноэкранного режима
        return "break"

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)

        # Основной контейнер
        main_container = tk.Frame(self.root, bg=self.bg_color, bd=0)
        main_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Заголовок (убираем кнопку выхода)
        header_frame = tk.Frame(main_container, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = tk.Label(
            header_frame,
            text="MARILYN TONE",
            bg=self.bg_color,
            fg=self.accent_color,
            font=('Segoe UI', 32, 'bold'),
            pady=10
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame,
            text="Text to Speech Converter • Полноэкранный режим",
            bg=self.bg_color,
            fg=self.secondary_text,
            font=('Segoe UI', 12),
            pady=5
        )
        subtitle_label.pack()

        # Основная карточка
        card = tk.Frame(
            main_container,
            bg=self.card_color,
            bd=0,
            relief='flat',
            highlightthickness=0
        )
        card.pack(fill="both", expand=True)

        # Ввод текста
        input_frame = tk.Frame(card, bg=self.card_color, padx=30, pady=30)
        input_frame.pack(fill="both", expand=True, pady=(0, 20))

        tk.Label(
            input_frame,
            text="Введите текст:",
            bg=self.card_color,
            fg=self.text_color,
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor="w", pady=(0, 15))

        # Стилизованное текстовое поле
        text_container = tk.Frame(input_frame, bg="#252525", bd=0, relief='flat', padx=2, pady=2)
        text_container.pack(fill="both", expand=True)

        self.text_input = scrolledtext.ScrolledText(
            text_container,
            bg="#2d2d2d",
            fg=self.text_color,
            font=self.mono_font,
            insertbackground=self.accent_color,
            relief='flat',
            bd=0,
            padx=20,
            pady=20,
            wrap=tk.WORD,
            selectbackground=self.accent_color
        )
        self.text_input.pack(fill="both", expand=True, padx=1, pady=1)

        # Настройки в три колонки
        settings_container = tk.Frame(card, bg=self.card_color, padx=30, pady=20)
        settings_container.pack(fill="x", pady=(0, 20))

        # Колонка 1 - Выбор языка
        lang_column = tk.Frame(settings_container, bg=self.card_color)
        lang_column.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(
            lang_column,
            text="Язык:",
            bg=self.card_color,
            fg=self.text_color,
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor="w", pady=(0, 8))

        self.language_var = tk.StringVar(value="Все языки")
        languages = ["Все языки", "Русский", "Английский", "Немецкий", "Французский",
                     "Испанский", "Итальянский", "Японский", "Китайский", "Корейский"]

        language_combobox = ttk.Combobox(
            lang_column,
            textvariable=self.language_var,
            values=languages,
            state="readonly",
            font=self.app_font,
            width=20
        )
        language_combobox.current(0)
        language_combobox.pack(fill="x")
        language_combobox.bind('<<ComboboxSelected>>', self.filter_voices)

        # Колонка 2 - Выбор пола голоса
        gender_column = tk.Frame(settings_container, bg=self.card_color)
        gender_column.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(
            gender_column,
            text="Пол голоса:",
            bg=self.card_color,
            fg=self.text_color,
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor="w", pady=(0, 8))

        self.gender_var = tk.StringVar(value="Любой")
        genders = ["Любой", "Мужской", "Женский"]

        gender_combobox = ttk.Combobox(
            gender_column,
            textvariable=self.gender_var,
            values=genders,
            state="readonly",
            font=self.app_font,
            width=15
        )
        gender_combobox.current(0)
        gender_combobox.pack(fill="x")
        gender_combobox.bind('<<ComboboxSelected>>', self.filter_voices)

        # Колонка 3 - Выбор голоса
        voice_column = tk.Frame(settings_container, bg=self.card_color)
        voice_column.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(
            voice_column,
            text="Голос:",
            bg=self.card_color,
            fg=self.text_color,
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor="w", pady=(0, 8))

        self.voice_combobox = ttk.Combobox(
            voice_column,
            values=[v['name'] for v in self.voice_engine.voices],
            state="readonly",
            font=self.app_font,
            width=25
        )
        self.voice_combobox.current(0)
        self.voice_combobox.pack(fill="x")

        # Колонка 4 - Настройки скорости
        speed_column = tk.Frame(settings_container, bg=self.card_color)
        speed_column.pack(side="right", fill="both", expand=True)

        speed_frame = tk.Frame(speed_column, bg=self.card_color)
        speed_frame.pack(fill="x")

        tk.Label(
            speed_frame,
            text="Скорость речи:",
            bg=self.card_color,
            fg=self.text_color,
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor="w", pady=(0, 8))

        speed_control_frame = tk.Frame(speed_frame, bg=self.card_color)
        speed_control_frame.pack(fill="x")

        self.speed_var = tk.IntVar(value=150)
        self.speed_scale = tk.Scale(
            speed_control_frame,
            from_=50,
            to=300,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            bg=self.card_color,
            fg=self.text_color,
            highlightthickness=0,
            troughcolor="#252525",
            activebackground=self.accent_color,
            sliderlength=20,
            length=200,
            showvalue=False,
            font=self.app_font
        )
        self.speed_scale.pack(side="left")

        # Отображение значения скорости
        speed_value_frame = tk.Frame(speed_control_frame, bg=self.card_color)
        speed_value_frame.pack(side="left", padx=(15, 0))

        self.speed_label = tk.Label(
            speed_value_frame,
            textvariable=self.speed_var,
            bg=self.card_color,
            fg=self.accent_color,
            font=('Segoe UI', 14, 'bold'),
            width=4
        )
        self.speed_label.pack()

        tk.Label(
            speed_value_frame,
            text="слов/мин",
            bg=self.card_color,
            fg=self.secondary_text,
            font=('Segoe UI', 9)
        ).pack()

        # Кнопки управления
        btn_frame = tk.Frame(card, bg=self.card_color, padx=30, pady=25)
        btn_frame.pack(fill="x")

        # Создаем стили для кнопок с лучшей читаемостью
        style = ttk.Style()

        # Стиль для акцентных кнопок (белый текст на розовом фоне)
        style.configure('Accent.TButton',
                        background=self.accent_color,
                        foreground="#ffffff",  # Белый текст для лучшей читаемости
                        font=self.button_font,
                        borderwidth=0,
                        padding=(20, 12),
                        focuscolor=self.accent_color)
        style.map('Accent.TButton',
                  background=[('active', '#e03cd9'), ('pressed', '#c132bb'), ('!disabled', self.accent_color)],
                  foreground=[('!disabled', '#ffffff')])  # Всегда белый текст

        # Стиль для второстепенных кнопок (белый текст на темном фоне)
        style.configure('Secondary.TButton',
                        background="#353535",
                        foreground="#ffffff",  # Белый текст для лучшей читаемости
                        font=self.button_font,
                        borderwidth=0,
                        padding=(20, 12),
                        focuscolor="#454545")
        style.map('Secondary.TButton',
                  background=[('active', '#454545'), ('pressed', '#555555'), ('!disabled', '#353535')],
                  foreground=[('!disabled', '#ffffff')])  # Всегда белый текст

        # Кнопка озвучить
        self.play_btn = ttk.Button(
            btn_frame,
            text="🔊 ОЗВУЧИТЬ",
            style='Accent.TButton',
            command=self.synthesize_speech
        )
        self.play_btn.pack(side="left", padx=(0, 15), expand=True, fill="x")

        # Кнопка прослушать
        self.listen_btn = ttk.Button(
            btn_frame,
            text="▶️ ПРОСЛУШАТЬ",
            style='Secondary.TButton',
            command=self.preview_speech
        )
        self.listen_btn.pack(side="left", padx=(0, 15), expand=True, fill="x")

        # Кнопка скачать
        self.download_btn = ttk.Button(
            btn_frame,
            text="💾 СКАЧАТЬ",
            style='Secondary.TButton',
            command=self.save_audio
        )
        self.download_btn.pack(side="left", padx=(0, 15), expand=True, fill="x")

        # Кнопка очистки
        self.clear_btn = ttk.Button(
            btn_frame,
            text="🗑️ ОЧИСТИТЬ",
            style='Secondary.TButton',
            command=self.clear_text
        )
        self.clear_btn.pack(side="left", expand=True, fill="x")

        # Статус бар
        self.status_bar = tk.Label(
            self.root,
            text="Готов к работе • Выберите текст и настройки • Полноэкранный режим",
            bg=self.bg_color,
            fg=self.secondary_text,
            font=('Segoe UI', 10),
            anchor='w',
            padx=30,
            pady=10
        )
        self.status_bar.pack(side="bottom", fill="x")

        # Привязка событий
        self.speed_scale.configure(command=self.update_speed_label)
        self.setup_context_menu(self.text_input)

    def filter_voices(self, event=None):
        """Фильтрует голоса по выбранному языку и полу"""
        selected_language = self.language_var.get()
        selected_gender = self.gender_var.get()
        voices = self.voice_engine.voices

        # Фильтрация по языку
        if selected_language != "Все языки":
            lang_map = {
                "Русский": "ru",
                "Английский": "en",
                "Немецкий": "de",
                "Французский": "fr",
                "Испанский": "es",
                "Итальянский": "it",
                "Японский": "ja",
                "Китайский": "zh",
                "Корейский": "ko"
            }

            target_lang = lang_map.get(selected_language, "")
            filtered_voices = [v for v in voices if any(target_lang in lang for lang in v['languages'])]
        else:
            filtered_voices = voices

        # Фильтрация по полу
        if selected_gender != "Любой":
            gender_map = {
                "Мужской": "male",
                "Женский": "female"
            }
            target_gender = gender_map.get(selected_gender, "")
            filtered_voices = [v for v in filtered_voices if v.get('gender') == target_gender]

        self.voice_combobox['values'] = [v['name'] for v in filtered_voices]
        if filtered_voices:
            self.voice_combobox.current(0)
        else:
            self.voice_combobox.set('')
            self.status_bar.config(text="Нет доступных голосов для выбранных параметров")

    def update_speed_label(self, value):
        self.speed_var.set(int(float(value)))

    def setup_context_menu(self, text_widget):
        """Добавляет контекстное меню для текстового поля"""
        menu = tk.Menu(text_widget, tearoff=0, bg="#353535", fg=self.text_color, bd=0)
        menu.add_command(label="Вставить", command=lambda: text_widget.event_generate("<<Paste>>"))
        menu.add_command(label="Копировать", command=lambda: text_widget.event_generate("<<Copy>>"))
        menu.add_command(label="Вырезать", command=lambda: text_widget.event_generate("<<Cut>>"))
        menu.add_separator()
        menu.add_command(label="Выделить все", command=lambda: text_widget.tag_add('sel', '1.0', 'end'))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        text_widget.bind("<Button-3>", show_menu)

    def clear_text(self):
        """Очищает текстовое поле"""
        self.text_input.delete("1.0", tk.END)
        self.status_bar.config(text="Текст очищен")

    def synthesize_speech(self):
        """Озвучивает текст"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Ошибка", "Введите текст для озвучивания!")
            return

        voice_idx = self.voice_combobox.current()
        speed = self.speed_var.get()

        try:
            self.status_bar.config(text="Озвучивание...")
            self.root.update()

            # Создаем новый экземпляр движка для каждого воспроизведения
            temp_engine = VoiceEngine()
            temp_engine.text_to_speech(text, voice_idx, speed)
            self.status_bar.config(text="Озвучивание завершено ✓")

        except Exception as e:
            self.status_bar.config(text="Ошибка при озвучивании")
            messagebox.showerror("Ошибка", f"Не удалось воспроизвести текст:\n{str(e)}")

    def preview_speech(self):
        """Прослушивание предварительного варианта"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Ошибка", "Введите текст для прослушивания!")
            return

        # Берем только первые 100 символов для предпросмотра
        preview_text = text[:100] + "..." if len(text) > 100 else text

        voice_idx = self.voice_combobox.current()
        speed = self.speed_var.get()

        try:
            self.status_bar.config(text="Прослушивание...")
            self.root.update()

            # Создаем новый экземпляр движка для каждого воспроизведения
            temp_engine = VoiceEngine()
            temp_engine.text_to_speech(preview_text, voice_idx, speed)
            self.status_bar.config(text="Прослушивание завершено ✓")

        except Exception as e:
            self.status_bar.config(text="Ошибка при прослушивании")
            messagebox.showerror("Ошибка", f"Не удалось воспроизвести текст:\n{str(e)}")

    def save_audio(self):
        """Сохраняет аудио в файл"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Ошибка", "Введите текст для сохранения!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[
                ("MP3 файлы", "*.mp3"),
                ("WAV файлы", "*.wav"),
                ("OGG файлы", "*.ogg"),
                ("FLAC файлы", "*.flac")
            ],
            title="Сохранить аудиофайл"
        )

        if file_path:
            try:
                self.status_bar.config(text="Сохранение аудио...")
                self.root.update()

                # Создаем новый экземпляр движка для каждого сохранения
                temp_engine = VoiceEngine()
                temp_engine.text_to_speech(
                    text,
                    self.voice_combobox.current(),
                    self.speed_var.get(),
                    file_path
                )

                self.status_bar.config(text=f"Аудио сохранено: {os.path.basename(file_path)} ✓")
                messagebox.showinfo("Успех", f"Аудиофайл успешно сохранен!\n{file_path}")

            except Exception as e:
                self.status_bar.config(text="Ошибка при сохранении")
                messagebox.showerror("Ошибка", f"Не удалось сохранить аудио:\n{str(e)}")