import os
import winsound
import pygame
import numpy as np
import threading


class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        self.sounds = {}
        self.sound_files = [None] * 16
        self.sound_names = [
            "Kick", "Snare", "Hi-Hat", "Clap",
            "Tom 1", "Tom 2", "Cymbal", "Shaker",
            "Perc 1", "Perc 2", "FX 1", "FX 2",
            "Vox 1", "Vox 2", "Bass", "Synth"
        ]
        self.volumes = [0.7] * 16
        self.load_default_sounds()

    def load_default_sounds(self):
        """Генерируем базовые синтезированные звуки"""
        for i in range(16):
            self.generate_default_sound(i)

    def generate_default_sound(self, index):
        """Генерация простых синтезированных звуков"""
        sample_rate = 44100
        duration = 0.2

        t = np.linspace(0, duration, int(sample_rate * duration), False)

        if index == 0:  # Kick
            freq = 60 * np.exp(-12 * t)
            wave = 0.8 * np.sin(2 * np.pi * freq * t) * np.exp(-6 * t)
        elif index == 1:  # Snare
            noise = np.random.uniform(-1, 1, len(t))
            envelope = np.exp(-10 * t)
            wave = noise * envelope * 0.6
        elif index == 2:  # Hi-Hat
            noise = np.random.uniform(-0.5, 0.5, len(t))
            envelope = np.exp(-20 * t)
            wave = noise * envelope * 0.7
        elif index == 3:  # Clap
            noise = np.random.uniform(-0.3, 0.3, len(t))
            envelope = np.exp(-15 * t)
            wave = noise * envelope * 0.8
        else:
            # Простой тон для остальных звуков
            freq = 150 + index * 40
            wave = 0.5 * np.sin(2 * np.pi * freq * t) * np.exp(-4 * t)

        # Конвертируем в pygame sound
        sound_data = np.int16(wave * 32767)
        sound = pygame.mixer.Sound(buffer=sound_data.astype(np.int16))
        self.sounds[index] = sound

    def load_sound(self, index, file_path):
        try:
            if file_path and os.path.exists(file_path):
                sound = pygame.mixer.Sound(file_path)
                self.sounds[index] = sound
                self.sound_files[index] = file_path
                return True
        except Exception as e:
            print(f"Error loading sound: {e}")
        return False

    def play_sound(self, index):
        try:
            if index in self.sounds and self.sounds[index]:
                channel = self.sounds[index].play()
                if channel:
                    channel.set_volume(self.volumes[index])
            else:
                # Резервный beep
                freq = 300 + index * 50
                duration = 100
                threading.Thread(target=winsound.Beep, args=(min(freq, 2000), duration), daemon=True).start()
        except Exception as e:
            print(f"Error playing sound: {e}")

    def play_metronome(self):
        """Простой метроном"""
        try:
            winsound.Beep(800, 30)
        except:
            pass

    def get_sound_name(self, index):
        if 0 <= index < len(self.sound_names):
            return self.sound_names[index]
        return f"Sound {index + 1}"

    def set_sound_name(self, index, name):
        if 0 <= index < len(self.sound_names):
            self.sound_names[index] = name

    def get_sound_file_name(self, index):
        if 0 <= index < len(self.sound_files) and self.sound_files[index]:
            return os.path.basename(self.sound_files[index])
        return "Synthesized"

    def set_volume(self, index, volume):
        if 0 <= index < len(self.volumes):
            self.volumes[index] = max(0.0, min(1.0, volume))

    def stop_all(self):
        pygame.mixer.stop()

    def get_config(self):
        return {
            "sound_names": self.sound_names,
            "sound_files": self.sound_files,
            "volumes": self.volumes
        }

    def load_config(self, config):
        if "sound_names" in config:
            self.sound_names = config["sound_names"]
        if "sound_files" in config:
            self.sound_files = config["sound_files"]
        if "volumes" in config:
            self.volumes = config["volumes"]

        # Перезагружаем звуки
        for i, file_path in enumerate(self.sound_files):
            if file_path:
                self.load_sound(i, file_path)