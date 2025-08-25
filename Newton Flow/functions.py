import os
import tkinter as tk
from tkinter import filedialog
import time
import threading
import numpy as np
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Optional, Union
import sounddevice as sd
import soundfile as sf


class PadType(Enum):
    KICK = auto()
    SNARE = auto()
    HIHAT = auto()
    CUSTOM = auto()


@dataclass
class Sample:
    name: str
    path: str
    audio_data: Optional[np.ndarray] = None
    sample_rate: int = 44100


class AudioEngine:
    def __init__(self):
        self._initialize_audio_engine()
        self.latency = 'low'
        self.blocksize = 1024

    def _initialize_audio_engine(self):
        """Инициализация аудио движка с обработкой ошибок"""
        try:
            sd.check_input_settings()
            sd.check_output_settings()
        except sd.PortAudioError as e:
            print(f"Audio initialization error: {e}")
            self.fallback_mode = True
        else:
            self.fallback_mode = False

    def play_audio(self, audio_data: np.ndarray, sample_rate: int = 44100):
        """Воспроизведение аудио через sounddevice"""
        if self.fallback_mode:
            print("Audio playback not available in fallback mode")
            return

        try:
            sd.play(audio_data, sample_rate, blocksize=self.blocksize)
            sd.wait()
        except sd.PortAudioError as e:
            print(f"Playback error: {e}")


class SampleManager:
    def __init__(self):
        self.samples: Dict[str, Sample] = {}
        self.audio_engine = AudioEngine()
        self._load_default_samples()

    def _load_default_samples(self):
        """Генерация базовых синтетических сэмплов"""
        self.add_sample(
            Sample(name="Kick", path="",
                   audio_data=self._generate_kick(), sample_rate=44100)
        )
        self.add_sample(
            Sample(name="Snare", path="",
                   audio_data=self._generate_snare(), sample_rate=44100)
        )
        self.add_sample(
            Sample(name="HiHat", path="",
                   audio_data=self._generate_hihat(), sample_rate=44100)
        )

    def _generate_kick(self, duration: float = 0.3, freq: float = 60) -> np.ndarray:
        """Генерация синтетического кик-барабана"""
        t = np.linspace(0, duration, int(44100 * duration), False)
        envelope = np.exp(-5 * t)
        wave = envelope * np.sin(2 * np.pi * freq * t)
        return (wave * 32767).astype(np.int16)

    def _generate_snare(self, duration: float = 0.2) -> np.ndarray:
        """Генерация синтетического снэра"""
        t = np.linspace(0, duration, int(44100 * duration), False)
        envelope = np.exp(-8 * t)
        wave = envelope * np.random.uniform(-1, 1, len(t))
        return (wave * 32767).astype(np.int16)

    def _generate_hihat(self, duration: float = 0.1) -> np.ndarray:
        """Генерация синтетического хай-хэта"""
        t = np.linspace(0, duration, int(44100 * duration), False)
        envelope = np.exp(-50 * t)
        wave = envelope * np.random.uniform(-0.5, 0.5, len(t))
        return (wave * 32767).astype(np.int16)

    def add_sample(self, sample: Sample):
        """Добавление сэмпла в менеджер"""
        self.samples[sample.name] = sample

    def load_sample(self) -> Optional[Sample]:
        """Загрузка сэмпла через диалоговое окно"""
        file_path = filedialog.askopenfilename(
            title="Select Sample",
            filetypes=[("Audio Files", "*.wav *.flac *.ogg *.mp3")]
        )

        if not file_path:
            return None

        try:
            audio_data, sample_rate = sf.read(file_path, dtype='float32')
            sample_name = os.path.basename(file_path)
            new_sample = Sample(
                name=sample_name,
                path=file_path,
                audio_data=audio_data,
                sample_rate=sample_rate
            )
            self.add_sample(new_sample)
            return new_sample
        except Exception as e:
            print(f"Error loading sample: {e}")
            return None

    def play_sample(self, sample_name: str):
        """Воспроизведение сэмпла по имени"""
        if sample_name not in self.samples:
            print(f"Sample {sample_name} not found")
            return

        sample = self.samples[sample_name]

        if sample.audio_data is None and sample.path:
            try:
                sample.audio_data, sample.sample_rate = sf.read(sample.path)
            except Exception as e:
                print(f"Error reading sample file: {e}")
                return

        if sample.audio_data is not None:
            threading.Thread(
                target=self.audio_engine.play_audio,
                args=(sample.audio_data, sample.sample_rate)
            ).start()


class MidiController:
    def __init__(self):
        self.recording = False
        self.record_start_time = 0
        self.events = []

    def send_midi(self, note: int, velocity: int = 127, channel: int = 0):
        """Отправка MIDI сообщения (эмуляция)"""
        print(f"MIDI Event: Note={note}, Velocity={velocity}, Channel={channel}")
        if self.recording:
            timestamp = time.time() - self.record_start_time
            self.events.append((timestamp, note, velocity, channel))

    def start_recording(self):
        """Начало записи MIDI"""
        self.recording = True
        self.record_start_time = time.time()
        self.events = []
        print("MIDI recording started")

    def stop_recording(self) -> list:
        """Остановка записи и возврат событий"""
        self.recording = False
        print(f"MIDI recording stopped. {len(self.events)} events recorded")
        return self.events


class PadBank:
    def __init__(self, rows: int = 4, cols: int = 4):
        self.rows = rows
        self.cols = cols
        self.pads = np.full((rows, cols), None, dtype=object)
        self._init_default_mapping()

    def _init_default_mapping(self):
        """Инициализация стандартного маппинга пэдов"""
        default_samples = ["Kick", "Snare", "HiHat"]
        index = 0
        for i in range(self.rows):
            for j in range(self.cols):
                if index < len(default_samples):
                    self.pads[i, j] = default_samples[index]
                    index += 1

    def set_pad_sample(self, row: int, col: int, sample_name: str):
        """Назначение сэмпла на конкретный пэд"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.pads[row, col] = sample_name
        else:
            raise IndexError("Invalid pad coordinates")

    def get_pad_sample(self, row: int, col: int) -> Optional[str]:
        """Получение сэмпла назначенного на пэд"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.pads[row, col]
        return None