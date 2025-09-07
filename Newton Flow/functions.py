import numpy as np
import json
import threading
import time
from datetime import datetime
import pygame


class BeatPadFunctions:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.is_playing = False
        self.bpm = 120
        self.current_step = 0
        self.grid_size = 4
        self.beat_matrix = np.zeros((16, 16), dtype=bool)
        self.playback_thread = None
        self.loop_callback = None
        self.metronome_enabled = True
        self.playback_lock = threading.Lock()

    def toggle_playback(self):
        with self.playback_lock:
            if not self.is_playing:
                self.start_playback()
                return True
            else:
                self.stop_playback()
                return False

    def start_playback(self):
        self.is_playing = True
        self.current_step = 0
        self.playback_thread = threading.Thread(target=self.playback_loop, daemon=True)
        self.playback_thread.start()

    def stop_playback(self):
        self.is_playing = False
        self.current_step = 0
        if self.loop_callback:
            self.loop_callback(0)

    def playback_loop(self):
        step_duration = 60.0 / self.bpm / 4

        while self.is_playing:
            start_time = time.time()

            # Воспроизводим звуки для текущего шага
            for sound_idx in range(16):
                if self.beat_matrix[self.current_step, sound_idx]:
                    self.sound_manager.play_sound(sound_idx)

            # Метроном на первый удар
            if self.metronome_enabled and self.current_step % 4 == 0:
                self.sound_manager.play_metronome()

            if self.loop_callback:
                self.loop_callback(self.current_step)

            # Переходим к следующему шагу
            self.current_step = (self.current_step + 1) % 16

            # Точное время ожидания
            elapsed = time.time() - start_time
            sleep_time = max(0, step_duration - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def toggle_cell(self, row, col, state=None):
        if 0 <= row < 16 and 0 <= col < 16:
            if state is None:
                self.beat_matrix[row, col] = not self.beat_matrix[row, col]
            else:
                self.beat_matrix[row, col] = state

            if self.beat_matrix[row, col]:
                self.sound_manager.play_sound(col)
            return True
        return False

    def clear_all(self):
        self.beat_matrix = np.zeros((16, 16), dtype=bool)
        return True

    def clear_selected(self, selected_cells):
        for row, col in selected_cells:
            self.toggle_cell(row, col, False)
        return True

    def fill_selected(self, selected_cells):
        for row, col in selected_cells:
            self.toggle_cell(row, col, True)
        return True

    def change_grid_size(self, size):
        size_map = {"4x4": 4, "8x8": 8, "16x16": 16}
        if size in size_map:
            self.grid_size = size_map[size]
            return True
        return False

    def export_json(self, file_path):
        try:
            data = {
                "metadata": {
                    "bpm": self.bpm,
                    "grid_size": self.grid_size,
                    "export_date": datetime.now().isoformat(),
                    "sound_names": self.sound_manager.sound_names,
                    "sound_files": self.sound_manager.sound_files
                },
                "pattern": self.beat_matrix.tolist()
            }

            with open(file_path, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

    def import_json(self, file_path):
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                data = json.load(f)
                self.beat_matrix = np.array(data.get("pattern", []))
                metadata = data.get("metadata", {})
                self.bpm = metadata.get("bpm", 120)
                self.grid_size = metadata.get("grid_size", 4)
                return True
        except Exception as e:
            print(f"Import error: {e}")
            return False

    def export_csv(self, file_path):
        try:
            with open(file_path, "w", encoding='utf-8') as f:
                f.write("Step," + ",".join(self.sound_manager.sound_names) + "\n")
                for step in range(16):
                    row = [str(int(x)) for x in self.beat_matrix[step]]
                    f.write(f"{step + 1}," + ",".join(row) + "\n")
            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False

    def export_txt(self, file_path):
        try:
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(f"Newton Flow Beat Pattern\n")
                f.write(f"BPM: {self.bpm}\n")
                f.write(f"Grid Size: {self.grid_size}x{self.grid_size}\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                max_name_len = max(len(name) for name in self.sound_manager.sound_names)
                header = "Step".ljust(6)
                for name in self.sound_manager.sound_names:
                    header += name.ljust(max_name_len + 2)
                f.write(header + "\n")

                for step in range(16):
                    line = f"{step + 1:4}  "
                    for sound in range(16):
                        symbol = "X" if self.beat_matrix[step, sound] else "."
                        line += symbol.ljust(max_name_len + 2)
                    f.write(line + "\n")
            return True
        except Exception as e:
            print(f"TXT export error: {e}")
            return False

    def generate_random_pattern(self, density=0.3):
        self.beat_matrix = np.random.random((16, 16)) < density
        return True

    def set_loop_callback(self, callback):
        self.loop_callback = callback

    def toggle_metronome(self):
        self.metronome_enabled = not self.metronome_enabled
        return self.metronome_enabled

    def get_config(self):
        return {
            "bpm": self.bpm,
            "grid_size": self.grid_size,
            "metronome_enabled": self.metronome_enabled
        }

    def load_config(self, config):
        if "bpm" in config:
            self.bpm = config["bpm"]
        if "grid_size" in config:
            self.grid_size = config["grid_size"]
        if "metronome_enabled" in config:
            self.metronome_enabled = config["metronome_enabled"]