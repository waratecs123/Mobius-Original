import tkinter as tk
import customtkinter as ctk
from typing import Dict, Optional
from dataclasses import dataclass
from functions import SampleManager, MidiController, PadBank, AudioEngine
import numpy as np
import json
import os


@dataclass
class AppConfig:
    grid_size: tuple = (4, 4)
    theme: str = "dark"
    default_samples: Dict[str, str] = None
    midi_enabled: bool = False
    last_used_path: str = ""


class NewtonFlowApp:
    def __init__(self):
        # Инициализация конфигурации
        self.config = self._load_config()

        # Инициализация основных компонентов
        self.sample_manager = SampleManager()
        self.midi_controller = MidiController()
        self.pad_bank = PadBank(*self.config.grid_size)
        self.audio_engine = AudioEngine()

        # Создание GUI
        self.root = ctk.CTk()
        self._setup_gui()

        # Настройка темы
        ctk.set_appearance_mode(self.config.theme)
        ctk.set_default_color_theme("blue")

        # Загрузка сохраненных сэмплов
        self._load_saved_samples()

    def _setup_gui(self):
        """Настройка графического интерфейса"""
        self.root.title("Newton Flow BeatPad Pro")
        self.root.geometry("1000x700")

        # Основные фреймы
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Панель пэдов
        self._setup_pad_grid()

        # Панель управления
        self._setup_control_panel()

        # Статус бар
        self.status_bar = ctk.CTkLabel(self.root, text="Ready", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=10, pady=5)

    def _setup_pad_grid(self):
        """Настройка сетки пэдов"""
        self.pad_frame = ctk.CTkFrame(self.main_frame)
        self.pad_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.pad_buttons = []
        for i in range(self.pad_bank.rows):
            row_buttons = []
            for j in range(self.pad_bank.cols):
                btn = ctk.CTkButton(
                    self.pad_frame,
                    text=f"{i * self.pad_bank.cols + j + 1}",
                    width=100,
                    height=100,
                    corner_radius=15,
                    command=lambda r=i, c=j: self._on_pad_press(r, c)
                )
                btn.grid(row=i, column=j, padx=5, pady=5)
                row_buttons.append(btn)
            self.pad_buttons.append(row_buttons)

    def _setup_control_panel(self):
        """Настройка панели управления"""
        control_frame = ctk.CTkFrame(self.main_frame, width=250)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        # Настройки сетки
        grid_label = ctk.CTkLabel(control_frame, text="Grid Size:")
        grid_label.pack(pady=(10, 0))

        self.grid_size_var = ctk.StringVar(value=f"{self.pad_bank.rows}x{self.pad_bank.cols}")
        grid_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["4x4", "8x8", "Custom"],
            variable=self.grid_size_var,
            command=self._change_grid_size
        )
        grid_menu.pack(pady=5)

        # Управление сэмплами
        sample_frame = ctk.CTkFrame(control_frame)
        sample_frame.pack(pady=10, fill=tk.X)

        ctk.CTkLabel(sample_frame, text="Sample Management").pack()

        load_btn = ctk.CTkButton(
            sample_frame,
            text="Load Sample",
            command=self._load_sample
        )
        load_btn.pack(pady=5, fill=tk.X)

        # MIDI контроль
        midi_frame = ctk.CTkFrame(control_frame)
        midi_frame.pack(pady=10, fill=tk.X)

        ctk.CTkLabel(midi_frame, text="MIDI Control").pack()

        self.midi_toggle = ctk.CTkSwitch(
            midi_frame,
            text="Enable MIDI",
            command=self._toggle_midi
        )
        self.midi_toggle.pack(pady=5)
        self.midi_toggle.select() if self.config.midi_enabled else self.midi_toggle.deselect()

        # Запись
        record_btn = ctk.CTkButton(
            control_frame,
            text="Record Jam",
            command=self._record_jam
        )
        record_btn.pack(pady=10, fill=tk.X)

        # Настройки
        settings_btn = ctk.CTkButton(
            control_frame,
            text="Settings",
            command=self._open_settings
        )
        settings_btn.pack(pady=10, fill=tk.X)

    def _on_pad_press(self, row: int, col: int):
        """Обработка нажатия на пэд"""
        sample_name = self.pad_bank.get_pad_sample(row, col)
        if sample_name:
            # Визуальная обратная связь
            self._highlight_pad(row, col)

            # Воспроизведение сэмпла
            self.sample_manager.play_sample(sample_name)

            # Отправка MIDI
            if self.config.midi_enabled:
                note = 36 + row * self.pad_bank.cols + col  # MIDI ноты для ударных
                self.midi_controller.send_midi(note)

    def _highlight_pad(self, row: int, col: int):
        """Подсветка нажатого пэда"""
        btn = self.pad_buttons[row][col]
        original_color = btn.cget("fg_color")
        btn.configure(fg_color="#3A7EBF")
        self.root.after(200, lambda: btn.configure(fg_color=original_color))

    def _load_sample(self):
        """Загрузка нового сэмпла"""
        sample = self.sample_manager.load_sample()
        if sample:
            self._update_status(f"Loaded: {sample.name}")
            self._save_config()

    def _change_grid_size(self, choice: str):
        """Изменение размера сетки пэдов"""
        if choice == "4x4":
            self.pad_bank = PadBank(4, 4)
        elif choice == "8x8":
            self.pad_bank = PadBank(8, 8)
        else:
            # Кастомный размер можно реализовать через диалоговое окно
            pass

        self.config.grid_size = (self.pad_bank.rows, self.pad_bank.cols)
        self._save_config()
        self._setup_pad_grid()

    def _toggle_midi(self):
        """Включение/выключение MIDI"""
        self.config.midi_enabled = not self.config.midi_enabled
        self._save_config()
        status = "enabled" if self.config.midi_enabled else "disabled"
        self._update_status(f"MIDI {status}")

    def _record_jam(self):
        """Запись джэма"""
        self._update_status("Recording...")
        self.midi_controller.start_recording()

        # Эмуляция записи (в реальном приложении было бы окно с кнопкой остановки)
        self.root.after(5000, self._stop_recording)

    def _stop_recording(self):
        """Остановка записи"""
        events = self.midi_controller.stop_recording()
        self._update_status(f"Recorded {len(events)} events")

        # Сохранение записи
        self._save_recording(events)

    def _open_settings(self):
        """Открытие окна настроек"""
        settings = ctk.CTkToplevel(self.root)
        settings.title("Settings")
        settings.geometry("400x300")

        # Здесь можно добавить настройки аудио, MIDI и т.д.

    def _update_status(self, message: str):
        """Обновление статус бара"""
        self.status_bar.configure(text=message)

    def _load_config(self) -> AppConfig:
        """Загрузка конфигурации из файла"""
        config_path = "newton_flow_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    return AppConfig(
                        grid_size=tuple(data.get("grid_size", (4, 4))),
                        theme=data.get("theme", "dark"),
                        midi_enabled=data.get("midi_enabled", False),
                        last_used_path=data.get("last_used_path", "")
                    )
            except Exception as e:
                print(f"Error loading config: {e}")

        return AppConfig()

    def _save_config(self):
        """Сохранение конфигурации в файл"""
        config_path = "newton_flow_config.json"
        data = {
            "grid_size": self.config.grid_size,
            "theme": self.config.theme,
            "midi_enabled": self.config.midi_enabled,
            "last_used_path": self.config.last_used_path
        }

        try:
            with open(config_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _load_saved_samples(self):
        """Загрузка сохраненных сэмплов"""
        # В реальном приложении можно загружать из конфига
        pass

    def _save_recording(self, events):
        """Сохранение записи в файл"""
        # В реальном приложении можно сохранять как MIDI или аудио
        pass

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


if __name__ == "__main__":
    app = NewtonFlowApp()
    app.run()