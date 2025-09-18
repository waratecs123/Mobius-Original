import os
import winsound
import pygame
import numpy as np
import threading
import tempfile
from pygame import mixer


class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=16, buffer=2048)
        self.sounds = {}
        self.sound_files = [None] * 16
        self.sound_names = [
            "Kick", "Snare", "Hi-Hat", "Clap",
            "Tom 1", "Tom 2", "Cymbal", "Shaker",
            "Perc 1", "Perc 2", "FX 1", "FX 2",
            "Vox 1", "Vox 2", "Bass", "Synth"
        ]
        self.volumes = [0.7] * 16
        self.pitches = [1.0] * 16  # Pitch control
        self.panning = [0.0] * 16  # Stereo panning
        self.preview_channel = None

        # Sound categories and library with your sounds
        self.sound_categories = {
            "Трэп": [
                "Трэп - 1 басс луп", "Трэп - 1 бит луп", "Трэп - 1 лид луп",
                "Трэп - 1 пад луп", "Трэп - 1 плак луп", "Трэп - 2 басс луп",
                "Трэп - 2 лид луп", "Трэп - 2 плак луп", "Трэп - 3 басс луп",
                "Трэп - 3 лид луп", "Трэп - 3 плак луп", "Трэп - кик",
                "Трэп - клэп", "Трэп - хэт", "Трэп - хэт 2"
            ],
            "Фонк": [
                "фонк - 1 басс", "фонк - 1 вокал", "фонк - 1 кик",
                "фонк - 1 лид", "фонк - 2 басс", "фонк - 2 вокал",
                "фонк - 2 лид", "фонк - 2 хэт", "фонк - 3 басс",
                "фонк - 3 вокал", "фонк - 3 лид", "фонк - 3 снэйр",
                "фонк - 4 басс", "фонк - 4 вокал", "фонк - 4 лид",
                "фонк - перк луп", "фонк - 4 хэт2", "фонк - 5 басс",
                "фонк - 5 бит луп (1)", "фонк - 5 вокал", "фонк - 5 лид",
                "фонк - 6 басс", "фонк - 6 вокал", "фонк - 6 лид",
                "фонк - 7 басс", "фонк - 7 лид", "фонк - 8 басс",
                "фонк - 8 лид"
            ],
            "Азиатские мотивы": [
                "Азиатские мотивы - гужен 1 луп", "Азиатские мотивы - гужен 2 луп",
                "Азиатские мотивы - гужен 3 луп", "Азиатские мотивы - гужен 4 луп",
                "Азиатские мотивы - дизи 1 луп", "Азиатские мотивы - дизи 2 луп",
                "Азиатские мотивы - дизи 3 луп", "Азиатские мотивы - дизи 4 луп",
                "Азиатские мотивы - кото 1 луп", "Азиатские мотивы - кото 2 луп",
                "Азиатские мотивы - гужен 5 луп", "Азиатские мотивы - гужен 6 луп",
                "Азиатские мотивы - рииз басс 1 луп", "Азиатские мотивы - рииз басс 2 луп",
                "Азиатские мотивы - fx 1", "Азиатские мотивы - fx 2", "Азиатские мотивы - fx 3"
            ]
        }

        # Create sounds directory if it doesn't exist
        self.sounds_dir = "sounds"
        if not os.path.exists(self.sounds_dir):
            os.makedirs(self.sounds_dir)

        self.load_default_sounds()

    def get_sound_file_path(self, sound_name):
        """Get the file path for a sound name"""
        # Map sound names to file names
        sound_file_map = {
            "Трэп - 1 басс луп": "trap_bass_loop_1.easy.mp3",
            "Трэп - 1 бит луп": "trap_beat_loop_1.easy.mp3",
            "Трэп - 1 лид луп": "trap_lead_loop_1.easy.mp3",
            "Трэп - 1 пад луп": "trap_pad_loop_1.easy.mp3",
            "Трэп - 1 плак луп": "trap_pluck_loop_1.easy.mp3",
            "Трэп - 2 басс луп": "trap_bass_loop_2.easy.mp3",
            "Трэп - 2 лид луп": "trap_lead_loop_2.easy.mp3",
            "Трэп - 2 плак луп": "trap_pluck_loop_2.easy.mp3",
            "Трэп - 3 басс луп": "trap_bass_loop_3.easy.mp3",
            "Трэп - 3 лид луп": "trap_lead_loop_3.easy.mp3",
            "Трэп - 3 плак луп": "trap_pluck_loop_3.easy.mp3",
            "Трэп - кик": "trap_kick.easy.mp3",
            "Трэп - клэп": "trap_clap.easy.mp3",
            "Трэп - хэт": "trap_hat.easy.mp3",
            "Трэп - хэт 2": "trap_hat_2.easy.mp3",
            "фонк - 1 басс": "fonk_bass_1.easy.mp3",
            "фонк - 1 вокал": "fonk_vocal_1.easy.mp3",
            "фонк - 1 кик": "fonk_kick_1.easy.mp3",
            "фонк - 1 лид": "fonk_lead_1.easy.mp3",
            "фонк - 2 басс": "fonk_bass_2.easy.mp3",
            "фонк - 2 вокал": "fonk_vocal_2.easy.mp3",
            "фонк - 2 лид": "fonk_lead_2.easy.mp3",
            "фонк - 2 хэт": "fonk_hat_2.easy.mp3",
            "фонк - 3 басс": "fonk_bass_3.easy.mp3",
            "фонк - 3 вокал": "fonk_vocal_3.easy.mp3",
            "фонк - 3 лид": "fonk_lead_3.easy.mp3",
            "фонк - 3 снэйр": "fonk_snare_3.easy.mp3",
            "фонк - 4 басс": "fonk_bass_4.easy.mp3",
            "фонк - 4 вокал": "fonk_vocal_4.easy.mp3",
            "фонк - 4 лид": "fonk_lead_4.easy.mp3",
            "фонк - перк луп": "fonk_perc_loop.easy.mp3",
            "фонк - 4 хэт2": "fonk_hat2_4.easy.mp3",
            "фонк - 5 басс": "fonk_bass_5.easy.mp3",
            "фонк - 5 бит луп (1)": "fonk_beat_loop_1.easy.mp3",
            "фонк - 5 вокал": "fonk_vocal_5.easy.mp3",
            "фонк - 5 лид": "fonk_lead_5.easy.mp3",
            "фонк - 6 басс": "fonk_bass_6.easy.mp3",
            "фонк - 6 вокал": "fonk_vocal_6.easy.mp3",
            "фонк - 6 лид": "fonk_lead_6.easy.mp3",
            "фонк - 7 басс": "fonk_bass_7.easy.mp3",
            "фонк - 7 лид": "fonk_lead_7.easy.mp3",
            "фонк - 8 басс": "fonk_bass_8.easy.mp3",
            "фонк - 8 лид": "fonk_lead_8.easy.mp3",
            "Азиатские мотивы - гужен 1 луп": "asian_guzheng_1_loop.mp3",
            "Азиатские мотивы - гужен 2 луп": "asian_guzheng_2_loop.mp3",
            "Азиатские мотивы - гужен 3 луп": "asian_guzheng_3_loop.mp3",
            "Азиатские мотивы - гужен 4 луп": "asian_guzheng_4_loop.mp3",
            "Азиатские мотивы - дизи 1 луп": "asian_dizi_1_loop.mp3",
            "Азиатские мотивы - дизи 2 луп": "asian_dizi_2_loop.mp3",
            "Азиатские мотивы - дизи 3 луп": "asian_dizi_3_loop.mp3",
            "Азиатские мотивы - дизи 4 луп": "asian_dizi_4_loop.mp3",
            "Азиатские мотивы - кото 1 луп": "asian_koto_1_loop.mp3",
            "Азиатские мотивы - кото 2 луп": "asian_koto_2_loop.mp3",
            "Азиатские мотивы - гужен 5 луп": "asian_guzheng_5_loop.mp3",
            "Азиатские мотивы - гужен 6 луп": "asian_guzheng_6_loop.mp3",
            "Азиатские мотивы - рииз басс 1 луп": "asian_reese_bass_1_loop.mp3",
            "Азиатские мотивы - рииз басс 2 луп": "asian_reese_bass_2_loop.mp3",
            "Азиатские мотивы - fx 1": "asian_fx_1.mp3",
            "Азиатские мотивы - fx 2": "asian_fx_2.mp3",
            "Азиатские мотивы - fx 3": "asian_fx_3.mp3"
        }

        # Try to find the sound file using the map
        file_name = sound_file_map.get(sound_name)
        if file_name:
            file_path = os.path.join(self.sounds_dir, file_name)
            if os.path.exists(file_path):
                return file_path

        # Fallback: check if the sound is in "Азиатские мотивы" and try .mp3
        is_asian = any(sound_name in sounds for cat, sounds in self.sound_categories.items() if cat == "Азиатские мотивы")
        extensions = ['.mp3'] if is_asian else ['.easy.mp3', '.mp3']

        for ext in extensions:
            file_name = f"{sound_name}{ext}"
            file_path = os.path.join(self.sounds_dir, file_name)
            if os.path.exists(file_path):
                return file_path

        # If not found, return None
        return None

    def load_default_sounds(self):
        """Генерируем базовые синтезированные звуки"""
        for i in range(16):
            self.generate_default_sound(i)

    def generate_default_sound(self, index):
        """Генерация качественных синтезированных звуков"""
        sample_rate = 44100
        duration = 0.3

        t = np.linspace(0, duration, int(sample_rate * duration), False)

        if index == 0:  # Kick
            freq = 80 * np.exp(-15 * t)
            wave = 0.9 * np.sin(2 * np.pi * freq * t) * np.exp(-8 * t)
        elif index == 1:  # Snare
            noise = np.random.uniform(-1, 1, len(t))
            envelope = np.exp(-12 * t)
            tone = 0.3 * np.sin(2 * np.pi * 180 * t) * np.exp(-10 * t)
            wave = (noise * 0.7 + tone * 0.3) * envelope * 0.6
        elif index == 2:  # Hi-Hat
            noise = np.random.uniform(-0.7, 0.7, len(t))
            envelope = np.exp(-25 * t)
            wave = noise * envelope * 0.8
        elif index == 3:  # Clap
            # Multi-clap effect
            main_clap = np.random.uniform(-0.4, 0.4, len(t))
            delay = np.zeros_like(main_clap)
            delay[1000:1000 + len(main_clap) // 2] = main_clap[:len(main_clap) // 2] * 0.5
            wave = (main_clap + delay) * np.exp(-18 * t) * 0.7
        else:
            # Более интересные звуки для остальных слотов
            freq = 120 + index * 30
            wave = 0.6 * np.sin(2 * np.pi * freq * t) * np.exp(-3 * t)
            # Добавляем немного гармоник
            wave += 0.2 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-4 * t)
            wave += 0.1 * np.sin(2 * np.pi * freq * 3 * t) * np.exp(-5 * t)

        # Нормализуем и конвертируем
        wave = wave / np.max(np.abs(wave)) if np.max(np.abs(wave)) > 0 else wave
        sound_data = np.int16(wave * 32767 * 0.8)

        sound = pygame.mixer.Sound(buffer=sound_data.astype(np.int16))
        self.sounds[index] = sound

    def load_sound(self, index, file_path):
        """Load sound for a specific slot"""
        try:
            if file_path and os.path.exists(file_path):
                sound = pygame.mixer.Sound(file_path)
                self.sounds[index] = sound
                self.sound_files[index] = file_path
                return True
        except Exception as e:
            print(f"Error loading sound: {e}")
        return False

    def preview_sound(self, file_path):
        """Предпросмотр звука перед назначением"""
        try:
            if self.preview_channel:
                self.preview_channel.stop()

            if file_path and os.path.exists(file_path):
                sound = pygame.mixer.Sound(file_path)
                self.preview_channel = sound.play()
                return True
        except Exception as e:
            print(f"Error previewing sound: {e}")
        return False

    def stop_preview(self):
        """Остановить предпросмотр"""
        if self.preview_channel:
            self.preview_channel.stop()

    def play_sound(self, index):
        """Play sound by index"""
        try:
            if index in self.sounds and self.sounds[index]:
                channel = self.sounds[index].play()
                if channel:
                    channel.set_volume(self.volumes[index])
                    # Применяем настройки pitch и panning
                    self.apply_sound_settings(channel, index)
            else:
                # Резервный beep
                freq = 400 + index * 30
                duration = 80
                threading.Thread(target=winsound.Beep,
                                 args=(min(freq, 2000), duration), daemon=True).start()
        except Exception as e:
            print(f"Error playing sound: {e}")

    def apply_sound_settings(self, channel, index):
        """Применить настройки звука"""
        if channel:
            channel.set_volume(self.volumes[index])
            # Pitch adjustment (через изменение частоты дискретизации)
            if hasattr(channel, 'set_endevent'):
                pass  # Pitch control would need more advanced handling

    def set_volume(self, index, volume):
        if 0 <= index < len(self.volumes):
            self.volumes[index] = max(0.0, min(1.0, volume))

    def set_pitch(self, index, pitch):
        if 0 <= index < len(self.pitches):
            self.pitches[index] = max(0.5, min(2.0, pitch))

    def set_pan(self, index, pan):
        if 0 <= index < len(self.panning):
            self.panning[index] = max(-1.0, min(1.0, pan))

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

    def get_sound_categories(self):
        return self.sound_categories

    def get_sounds_in_category(self, category):
        return self.sound_categories.get(category, [])

    def stop_all(self):
        pygame.mixer.stop()
        if self.preview_channel:
            self.preview_channel.stop()

    def get_config(self):
        return {
            "sound_names": self.sound_names,
            "sound_files": self.sound_files,
            "volumes": self.volumes,
            "pitches": self.pitches,
            "panning": self.panning
        }

    def load_config(self, config):
        if "sound_names" in config:
            self.sound_names = config["sound_names"]
        if "sound_files" in config:
            self.sound_files = config["sound_files"]
        if "volumes" in config:
            self.volumes = config["volumes"]
        if "pitches" in config:
            self.pitches = config["pitches"]
        if "panning" in config:
            self.panning = config["panning"]

        # Перезагружаем звуки
        for i, file_path in enumerate(self.sound_files):
            if file_path and os.path.exists(file_path):
                self.load_sound(i, file_path)