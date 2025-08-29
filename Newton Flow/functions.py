import numpy as np
import json
import threading
import time
from datetime import datetime


class BeatPadFunctions:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.is_playing = False
        self.bpm = 120
        self.current_step = 0
        self.grid_size = 4
        self.beat_matrix = np.zeros((16, 16), dtype=bool)
        self.playback_thread = None

    def toggle_playback(self):
        if not self.is_playing:
            self.start_playback()
            return True
        else:
            self.stop_playback()
            return False

    def start_playback(self):
        self.is_playing = True
        self.playback_thread = threading.Thread(target=self.playback_loop)
        self.playback_thread.daemon = True
        self.playback_thread.start()

    def stop_playback(self):
        self.is_playing = False
        self.current_step = 0

    def playback_loop(self):
        step_duration = 60.0 / self.bpm / 4  # 16th notes

        while self.is_playing:
            start_time = time.time()

            # Воспроизводим звуки для текущего шага
            for sound_idx in range(16):
                if self.beat_matrix[self.current_step, sound_idx]:
                    self.sound_manager.play_sound(sound_idx)

            # Переходим к следующему шагу
            self.current_step = (self.current_step + 1) % 16

            # Ждем до следующего шага
            elapsed = time.time() - start_time
            sleep_time = max(0, step_duration - elapsed)
            time.sleep(sleep_time)

    def toggle_cell(self, row, col):
        if 0 <= row < 16 and 0 <= col < 16:
            self.beat_matrix[row, col] = not self.beat_matrix[row, col]
            if self.beat_matrix[row, col]:
                self.sound_manager.play_sound(col)
            return True
        return False

    def clear_all(self):
        self.beat_matrix = np.zeros((16, 16), dtype=bool)

    def change_grid_size(self, size):
        size_map = {"4x4": 4, "8x8": 8, "16x16": 16}
        self.grid_size = size_map.get(size, 4)

    def export_json(self, file_path):
        data = {
            "metadata": {
                "bpm": self.bpm,
                "grid_size": self.grid_size,
                "export_date": datetime.now().isoformat(),
                "sound_names": self.sound_manager.sound_names
            },
            "pattern": self.beat_matrix.tolist()
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def export_csv(self, file_path):
        with open(file_path, "w") as f:
            f.write("Step," + ",".join(self.sound_manager.sound_names) + "\n")
            for step in range(16):
                row = [str(int(x)) for x in self.beat_matrix[step]]
                f.write(f"{step + 1}," + ",".join(row) + "\n")

    def export_txt(self, file_path):
        with open(file_path, "w") as f:
            f.write(f"Beat Pattern Export\n")
            f.write(f"BPM: {self.bpm}\n")
            f.write(f"Grid Size: {self.grid_size}x{self.grid_size}\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            max_name_len = max(len(name) for name in self.sound_manager.sound_names)
            header = "Step".ljust(5)
            for name in self.sound_manager.sound_names:
                header += name.ljust(max_name_len + 1)
            f.write(header + "\n")

            for step in range(16):
                line = f"{step + 1:4} "
                for sound in range(16):
                    symbol = "X" if self.beat_matrix[step, sound] else "."
                    line += symbol.ljust(max_name_len + 1)
                f.write(line + "\n")

    def load_config(self, config):
        if "sound_names" in config:
            self.sound_manager.sound_names = config["sound_names"]
        if "sound_files" in config:
            self.sound_manager.sound_files = config["sound_files"]
            for i, file_path in enumerate(self.sound_manager.sound_files):
                if file_path:
                    self.sound_manager.load_sound(i, file_path)

    def get_config(self):
        return {
            "sound_names": self.sound_manager.sound_names,
            "sound_files": self.sound_manager.sound_files
        }