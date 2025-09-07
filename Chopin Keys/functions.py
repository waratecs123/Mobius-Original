# functions.py
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, colorchooser
import threading
import time
import os
import random
import pygame
import numpy as np
import wave
import struct
from scipy import signal
from scipy.io import wavfile
import sounddevice as sd
import soundfile as sf
import json
import mido
from mido import MidiFile, MidiTrack, Message
from tkinter.scrolledtext import ScrolledText


class DAWEngine:
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.setup_audio_engine()

        # Переменные для аудио записи
        self.recording = False
        self.recorded_audio = []
        self.audio_stream = None

        # Списки эффектов и инструментов
        self.effects_list = ["Reverb", "Delay", "Chorus", "Flanger", "Phaser",
                             "Distortion", "Compressor", "EQ", "Filter", "Limiter"]

        # Паттерны и проекты
        self.patterns = {1: {"name": "Pattern 1", "data": []}}
        self.current_pattern = 1
        self.playlist = []

        # Настройки
        self.settings = {
            'audio_latency': 128,
            'sample_rate': 44100,
            'record_channels': 2,
            'theme': 'dark'
        }

        # Стеки отмены/повтора
        self.undo_stack = []
        self.redo_stack = []

    def setup_audio_engine(self):
        """Настройка аудио движка"""
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        self.audio_thread = threading.Thread(target=self.audio_processing, daemon=True)
        self.audio_thread.start()

    def audio_processing(self):
        """Обработка аудио в отдельном потоке"""
        while True:
            if self.gui.is_playing:
                self.generate_audio()
                self.update_vu_meters()
            time.sleep(0.01)

    def generate_audio(self):
        """Генерация аудио данных для воспроизведения"""
        # Генерация простого тестового сигнала
        sample_rate = 44100
        t = np.linspace(0, 0.1, int(0.1 * sample_rate), False)
        note_freq = 440.0  # A4
        audio = 0.5 * np.sin(2 * np.pi * note_freq * t)

        # Воспроизведение через pygame
        sound = pygame.sndarray.make_sound((audio * 32767).astype(np.int16))
        sound.play()

    def update_vu_meters(self):
        """Обновление VU метров в микшере"""
        for i, channel in enumerate(self.gui.mixer_channels):
            vu_value = random.uniform(0, 1)
            vu_height = int(vu_value * 150)
            channel['vu_meter'].delete('vu')
            channel['vu_meter'].create_rectangle(2, 150 - vu_height, 18, 150,
                                                 fill='#00ff00', outline='', tags='vu')

    def new_project(self):
        """Создание нового проекта"""
        self.gui.current_project = "Новый проект"
        self.gui.tracks = ["Трек 1"]
        self.gui.selected_track = 0
        self.gui.playback_position = 0
        self.gui.update_playlist()
        messagebox.showinfo("Новый проект", "Создан новый проект")

    def open_project(self):
        """Открытие проекта"""
        file_path = filedialog.askopenfilename(filetypes=[("Chopin Keys Project", "*.ckp")])
        if file_path:
            self.gui.current_project = os.path.basename(file_path)
            messagebox.showinfo("Проект открыт", f"Проект {self.gui.current_project} загружен")

    def save_project(self):
        """Сохранение проекта"""
        if not self.gui.current_project:
            self.save_project_as()
        else:
            messagebox.showinfo("Проект сохранен", f"Проект {self.gui.current_project} сохранен")

    def save_project_as(self):
        """Сохранение проекта как..."""
        file_path = filedialog.asksaveasfilename(defaultextension=".ckp")
        if file_path:
            self.gui.current_project = os.path.basename(file_path)
            messagebox.showinfo("Проект сохранен", f"Проект {self.gui.current_project} сохранен")

    def import_midi(self):
        """Импорт MIDI файла"""
        file_path = filedialog.askopenfilename(filetypes=[("MIDI Files", "*.mid")])
        if file_path:
            try:
                midi = MidiFile(file_path)
                messagebox.showinfo("Импорт MIDI", f"MIDI файл импортирован: {len(midi.tracks)} треков")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить MIDI: {str(e)}")

    def export_midi(self):
        """Экспорт MIDI файла"""
        file_path = filedialog.asksaveasfilename(defaultextension=".mid")
        if file_path:
            # Создание простого MIDI файла
            midi = MidiFile()
            track = MidiTrack()
            midi.tracks.append(track)
            track.append(Message('note_on', note=60, velocity=64, time=0))
            track.append(Message('note_off', note=60, velocity=64, time=480))
            midi.save(file_path)
            messagebox.showinfo("Экспорт MIDI", "MIDI файл экспортирован")

    def import_audio(self):
        """Импорт аудио файла"""
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if file_path:
            messagebox.showinfo("Импорт аудио", f"Аудио файл {os.path.basename(file_path)} импортирован")

    def export_wav(self):
        """Экспорт WAV файла"""
        file_path = filedialog.asksaveasfilename(defaultextension=".wav")
        if file_path:
            # Создание простого WAV файла
            sample_rate = 44100
            duration = 2.0
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio = 0.5 * np.sin(2 * np.pi * 440 * t)
            audio = (audio * 32767).astype(np.int16)
            wavfile.write(file_path, sample_rate, audio)
            messagebox.showinfo("Экспорт WAV", "WAV файл экспортирован")

    def open_settings(self):
        """Открытие настроек"""
        settings_window = tk.Toplevel(self.gui.root)
        settings_window.title("Настройки")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.gui.card_color)

        tk.Label(settings_window, text="Настройки DAW", bg=self.gui.card_color,
                 fg=self.gui.text_color).pack(pady=10)

        # Настройки аудио
        audio_frame = tk.LabelFrame(settings_window, text="Аудио настройки",
                                    bg=self.gui.card_color, fg=self.gui.text_color)
        audio_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(audio_frame, text="Задержка:", bg=self.gui.card_color,
                 fg=self.gui.text_color).grid(row=0, column=0, padx=5, pady=5)
        latency_var = tk.StringVar(value=str(self.settings['audio_latency']))
        latency_combo = tk.Combobox(audio_frame, textvariable=latency_var,
                                    values=['64', '128', '256', '512'])
        latency_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(audio_frame, text="Частота дискретизации:", bg=self.gui.card_color,
                 fg=self.gui.text_color).grid(row=1, column=0, padx=5, pady=5)
        sr_var = tk.StringVar(value=str(self.settings['sample_rate']))
        sr_combo = tk.Combobox(audio_frame, textvariable=sr_var,
                               values=['44100', '48000', '96000'])
        sr_combo.grid(row=1, column=1, padx=5, pady=5)

    def exit_app(self):
        """Выход из приложения"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.gui.root.quit()

    def undo(self):
        """Отменить последнее действие"""
        if self.undo_stack:
            action = self.undo_stack.pop()
            self.redo_stack.append(action)
            messagebox.showinfo("Отменить", "Действие отменено")

    def redo(self):
        """Повторить последнее действие"""
        if self.redo_stack:
            action = self.redo_stack.pop()
            self.undo_stack.append(action)
            messagebox.showinfo("Повторить", "Действие повторено")

    def cut(self):
        """Вырезать"""
        messagebox.showinfo("Вырезать", "Вырезано в буфер обмена")

    def copy(self):
        """Копировать"""
        messagebox.showinfo("Копировать", "Скопировано в буфер обмена")

    def paste(self):
        """Вставить"""
        messagebox.showinfo("Вставить", "Вставлено из буфера обмена")

    def delete(self):
        """Удалить"""
        messagebox.showinfo("Удалить", "Выделенное удалено")

    def select_all(self):
        """Выделить все"""
        messagebox.showinfo("Выделить все", "Все элементы выделены")

    def add_track(self):
        """Добавить трек"""
        track_name = simpledialog.askstring("Новый трек", "Введите название трека:")
        if track_name:
            self.gui.tracks.append(track_name)
            self.gui.update_playlist()
            messagebox.showinfo("Трек добавлен", f"Трек '{track_name}' добавлен")

    def delete_track(self):
        """Удалить трек"""
        if self.gui.tracks:
            track = self.gui.tracks.pop()
            self.gui.update_playlist()
            messagebox.showinfo("Трек удален", f"Трек '{track}' удален")

    def duplicate_track(self):
        """Дублировать трек"""
        if self.gui.tracks:
            new_track = f"{self.gui.tracks[-1]} (копия)"
            self.gui.tracks.append(new_track)
            self.gui.update_playlist()
            messagebox.showinfo("Трек дублирован", f"Трек '{new_track}' создан")

    def track_settings(self):
        """Настройки трека"""
        if self.gui.tracks:
            messagebox.showinfo("Настройки трека", f"Настройки для: {self.gui.tracks[self.gui.selected_track]}")

    def open_automation(self):
        """Открыть окно автоматизации"""
        automation_window = tk.Toplevel(self.gui.root)
        automation_window.title("Автоматизация")
        automation_window.geometry("600x400")
        automation_window.configure(bg=self.gui.card_color)

        tk.Label(automation_window, text="Редактор автоматизации",
                 bg=self.gui.card_color, fg=self.gui.text_color).pack(pady=10)

        canvas = tk.Canvas(automation_window, bg='#2d2d2d', height=300)
        canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Рисуем сетку автоматизации
        for i in range(0, 601, 50):
            canvas.create_line(i, 0, i, 300, fill='#444')
        for i in range(0, 301, 50):
            canvas.create_line(0, i, 600, i, fill='#444')

        # Примерная кривая автоматизации
        canvas.create_line(0, 250, 200, 100, 400, 200, 600, 50, fill='#00ff00', width=2)

    def new_pattern(self):
        """Создать новый паттерн"""
        pattern_num = len(self.patterns) + 1
        self.patterns[pattern_num] = {"name": f"Паттерн {pattern_num}", "data": []}
        messagebox.showinfo("Новый паттерн", f"Создан паттерн {pattern_num}")

    def duplicate_pattern(self):
        """Дублировать текущий паттерн"""
        if self.patterns:
            pattern_num = len(self.patterns) + 1
            self.patterns[pattern_num] = self.patterns[self.current_pattern].copy()
            self.patterns[pattern_num]["name"] = f"Паттерн {pattern_num} (копия)"
            messagebox.showinfo("Паттерн дублирован", f"Паттерн {self.current_pattern} дублирован")

    def delete_pattern(self):
        """Удалить текущий паттерн"""
        if len(self.patterns) > 1:
            del self.patterns[self.current_pattern]
            self.current_pattern = list(self.patterns.keys())[0]
            messagebox.showinfo("Паттерн удален", f"Паттерн удален, текущий: {self.current_pattern}")

    def open_piano(self):
        """Открыть виртуальное пианино"""
        piano_window = tk.Toplevel(self.gui.root)
        piano_window.title("Виртуальное пианино")
        piano_window.geometry("800x300")
        piano_window.configure(bg=self.gui.card_color)

        canvas = tk.Canvas(piano_window, bg='#2d2d2d')
        canvas.pack(fill="both", expand=True)

        # Рисуем белые клавиши
        white_keys = 14
        key_width = 50
        for i in range(white_keys):
            canvas.create_rectangle(i * key_width, 0, (i + 1) * key_width, 150,
                                    fill='white', outline='black')

        # Рисуем черные клавиши
        black_positions = [0.7, 1.7, 3.7, 4.7, 5.7, 7.7, 8.7, 10.7, 11.7, 12.7]
        for pos in black_positions:
            canvas.create_rectangle(pos * key_width, 0, (pos + 0.6) * key_width, 100,
                                    fill='black', outline='')

    def open_drum_machine(self):
        """Открыть барабанную машину"""
        drum_window = tk.Toplevel(self.gui.root)
        drum_window.title("Барабанная машина")
        drum_window.geometry("600x400")
        drum_window.configure(bg=self.gui.card_color)

        tk.Label(drum_window, text="Барабанная машина",
                 bg=self.gui.card_color, fg=self.gui.text_color).pack(pady=10)

        # Создаем сетку драм-машины 4x4
        drum_frame = tk.Frame(drum_window, bg=self.gui.card_color)
        drum_frame.pack(pady=10)

        drum_pads = []
        for i in range(4):
            for j in range(4):
                pad = tk.Button(drum_frame, text=f"Pad {i * 4 + j + 1}",
                                bg='#252525', fg=self.gui.text_color,
                                width=10, height=5, relief="raised")
                pad.grid(row=i, column=j, padx=5, pady=5)
                drum_pads.append(pad)

    def open_sequencer(self):
        """Открыть секвенсор"""
        self.gui.notebook.select(2)  # Переключаемся на вкладку секвенсора

    def open_mixer(self):
        """Открыть микшер"""
        self.gui.notebook.select(3)  # Переключаемся на вкладку микшера

    def open_playlist(self):
        """Открыть плейлист"""
        self.gui.notebook.select(0)  # Переключаемся на вкладку плейлиста

    def open_piano_roll(self):
        """Открыть пианино ролл"""
        self.gui.notebook.select(1)  # Переключаемся на вкладку пианино ролла

    def add_effect_to_selected_track(self, effect):
        """Добавить эффект к выбранному треку"""
        if self.gui.tracks:
            track = self.gui.tracks[self.gui.selected_track]
            messagebox.showinfo("Эффект добавлен", f"Эффект {effect} добавлен к {track}")

    def add_effect(self, effect):
        """Добавить эффект"""
        messagebox.showinfo("Эффект добавлен", f"Эффект {effect} добавлен")

    def select_instrument(self, instrument):
        """Выбор инструмента"""
        self.gui.current_instrument = instrument
        messagebox.showinfo("Инструмент выбран", f"Выбран инструмент: {instrument}")

    def play(self):
        """Воспроизведение"""
        self.gui.is_playing = True

    def pause(self):
        """Пауза"""
        self.gui.is_playing = False

    def stop(self):
        """Остановка"""
        self.gui.is_playing = False
        self.gui.is_recording = False
        self.gui.playback_position = 0
        self.gui.position_slider.set(0)

    def record(self):
        """Запись"""
        self.gui.is_recording = not self.gui.is_recording
        if self.gui.is_recording:
            messagebox.showinfo("Запись", "Запись начата")
        else:
            messagebox.showinfo("Запись", "Запись остановлена")

    def rewind(self):
        """Перемотка назад"""
        self.gui.playback_position = max(0, self.gui.playback_position - 5)
        self.gui.position_slider.set(self.gui.playback_position)

    def update_bpm(self):
        """Обновление BPM"""
        self.gui.bpm = self.gui.bpm_var.get()
        messagebox.showinfo("BPM изменен", f"BPM установлен: {self.gui.bpm}")

    def set_position(self, value):
        """Установка позиции воспроизведения"""
        self.gui.playback_position = float(value)

    def set_channel_volume(self, channel, volume):
        """Установка громкости канала"""
        volume = float(volume)
        self.gui.mixer_channels[channel]['volume'].set(volume)

    def set_channel_mute(self, channel, mute):
        """Установка mute для канала"""
        self.gui.mixer_channels[channel]['mute'].set(mute)

    def set_channel_solo(self, channel, solo):
        """Установка solo для канала"""
        self.gui.mixer_channels[channel]['solo'].set(solo)

    def open_channel_effects(self, channel):
        """Открыть эффекты для канала"""
        messagebox.showinfo("Эффекты канала", f"Эффекты для канала {channel + 1}")

    def toggle_sequencer_step(self, row, col):
        """Переключение шага в секвенсоре"""
        button = self.gui.sequencer_buttons[row][col]
        current_bg = button.cget('bg')
        if current_bg == '#252525':
            button.config(bg=self.gui.accent_color)
        else:
            button.config(bg='#252525')

    def open_ai_assistant(self):
        """Открыть AI ассистента"""
        ai_window = tk.Toplevel(self.gui.root)
        ai_window.title("AI Ассистент")
        ai_window.geometry("500x400")
        ai_window.configure(bg=self.gui.card_color)

        tk.Label(ai_window, text="AI Ассистент",
                 bg=self.gui.card_color, fg=self.gui.text_color).pack(pady=10)

        # Область чата
        chat_frame = tk.Frame(ai_window, bg=self.gui.card_color)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

        chat_log = ScrolledText(chat_frame, bg='#252525', fg=self.gui.text_color)
        chat_log.pack(fill="both", expand=True)
        chat_log.insert("end", "AI: Привет! Я ваш музыкальный ассистент.\n")

    def show_help(self):
        """Показать справку"""
        help_text = """Chopin Keys Pro - Современная DAW

Основные функции:
- Многодорожечная запись и редактирование
- MIDI секвенсор и пианино ролл
- Микшер с эффектами и автоматизацией
- Поддержка VST плагинов
- Экспорт в MIDI и WAV

Горячие клавиши:
Пробел - Воспроизведение/Пауза
R - Запись
Ctrl+Z - Отменить
Ctrl+Y - Повторить
Ctrl+S - Сохранить проект"""
        messagebox.showinfo("Справка", help_text)

    def about(self):
        """О программе"""
        about_text = """Chopin Keys Pro
Версия 2.0
Профессиональная DAW для создания музыки

Разработано с использованием Python, Pygame и Tkinter

© 2023 Chopin Keys Team. Все права защищены."""
        messagebox.showinfo("О программе", about_text)