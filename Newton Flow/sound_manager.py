import os
import winsound
from pygame import mixer
import numpy as np


class SoundManager:
    def __init__(self):
        mixer.init()
        self.sounds = {}
        self.sound_files = [None] * 16
        self.sound_names = [
            "Kick", "Snare", "Hi-Hat", "Clap",
            "Tom 1", "Tom 2", "Cymbal", "Shaker",
            "Perc 1", "Perc 2", "FX 1", "FX 2",
            "Vox 1", "Vox 2", "Bass", "Synth"
        ]

    def load_sound(self, index, file_path):
        try:
            if file_path and os.path.exists(file_path):
                self.sounds[index] = mixer.Sound(file_path)
                self.sound_files[index] = file_path
                return True
        except Exception as e:
            print(f"Error loading sound: {e}")
        return False

    def play_sound(self, index):
        try:
            if index in self.sounds:
                self.sounds[index].play()
            else:
                # Генерируем тональный звук по умолчанию
                freq = 440 + index * 50
                winsound.Beep(freq, 50)
        except Exception as e:
            print(f"Error playing sound: {e}")

    def get_sound_name(self, index):
        return self.sound_names[index] if index < len(self.sound_names) else f"Sound {index + 1}"

    def set_sound_name(self, index, name):
        if index < len(self.sound_names):
            self.sound_names[index] = name

    def get_sound_file_name(self, index):
        if self.sound_files[index]:
            return os.path.basename(self.sound_files[index])
        return "Default"