# functions.py
import pyttsx3
from typing import Optional, List, Callable, Dict
import os
from pydub import AudioSegment
import tempfile
import threading
import time
import json
from pathlib import Path
import subprocess


class VoiceEngine:
    def __init__(self):
        self.engine = None
        self.init_engine()
        self.voices = self.load_voices()
        self.is_speaking = False
        self.stop_requested = False
        self.settings_file = "voice_settings.json"
        self.load_settings()
        self.current_player = None

    def init_engine(self):
        """Инициализирует движок TTS"""
        if self.engine:
            try:
                self.engine.stop()
                self.engine = None
            except:
                pass

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        self.engine.connect('started-utterance', self.on_start)
        self.engine.connect('finished-utterance', self.on_finish)

    def load_voices(self) -> List[dict]:
        """Возвращает список доступных голосов с параметрами."""
        voices = [
            {'id': 'russian_male', 'name': 'Русский (Мужской)', 'gender': 'male', 'languages': ['ru'], 'system': False},
            {'id': 'russian_female', 'name': 'Русский (Женский)', 'gender': 'female', 'languages': ['ru'], 'system': False},
            {'id': 'english_us_male', 'name': 'English (US Male)', 'gender': 'male', 'languages': ['en-US'], 'system': False},
            {'id': 'english_us_female', 'name': 'English (US Female)', 'gender': 'female', 'languages': ['en-US'], 'system': False},
            {'id': 'english_uk_male', 'name': 'English (UK Male)', 'gender': 'male', 'languages': ['en-GB'], 'system': False},
            {'id': 'english_uk_female', 'name': 'English (UK Female)', 'gender': 'female', 'languages': ['en-GB'], 'system': False},
            {'id': 'german_male', 'name': 'Deutsch (Männlich)', 'gender': 'male', 'languages': ['de'], 'system': False},
            {'id': 'german_female', 'name': 'Deutsch (Weiblich)', 'gender': 'female', 'languages': ['de'], 'system': False},
            {'id': 'french_male', 'name': 'Français (Homme)', 'gender': 'male', 'languages': ['fr'], 'system': False},
            {'id': 'french_female', 'name': 'Français (Femme)', 'gender': 'female', 'languages': ['fr'], 'system': False},
            {'id': 'spanish_male', 'name': 'Español (Hombre)', 'gender': 'male', 'languages': ['es'], 'system': False},
            {'id': 'spanish_female', 'name': 'Español (Mujer)', 'gender': 'female', 'languages': ['es'], 'system': False},
        ]

        try:
            temp_engine = pyttsx3.init()
            for voice in temp_engine.getProperty('voices'):
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'gender': 'male' if 'male' in voice.name.lower() else 'female',
                    'languages': voice.languages,
                    'system': True
                }
                voices.append(voice_info)
            temp_engine.stop()
        except:
            pass

        return voices

    def load_settings(self):
        """Загружает настройки из файла"""
        self.default_settings = {
            'last_voice_index': 0,
            'last_speed': 150,
            'last_volume': 1.0,
            'last_pitch': 0,
            'last_echo': False,
            'last_reverb_intensity': 0,
            'last_volume_db': 0,
            'output_folder': str(Path.home() / "Documents" / "MarilynTone"),
            'auto_save': False
        }

        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = {**self.default_settings, **json.load(f)}
            else:
                self.settings = self.default_settings
            os.makedirs(self.settings['output_folder'], exist_ok=True)
        except:
            self.settings = self.default_settings

    def save_settings(self):
        """Сохраняет настройки в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except:
            pass

    def on_start(self, name):
        self.is_speaking = True
        self.stop_requested = False

    def on_finish(self, name, completed):
        self.is_speaking = False

    def stop_speech(self):
        """Останавливает текущее воспроизведение"""
        self.stop_requested = True
        try:
            self.engine.stop()
        except:
            pass
        if self.current_player:
            self.current_player.kill()
            self.current_player = None
        self.init_engine()

    def text_to_speech(self, text: str, voice_idx: int, speed: int = 150, volume: float = 1.0,
                       save_path: Optional[str] = None, callback: Optional[Callable] = None,
                       effects: Optional[Dict] = None):
        """Озвучивает текст с возможностью сохранения в файл и применения эффектов."""
        if effects is None:
            effects = {}
        try:
            if voice_idx >= len(self.voices):
                raise Exception("Неверный индекс голоса")

            voice = self.voices[voice_idx]
            self.init_engine()

            # Сохраняем последние настройки
            self.settings['last_voice_index'] = voice_idx
            self.settings['last_speed'] = speed
            self.settings['last_volume'] = volume
            self.settings['last_pitch'] = effects.get('pitch', 0)
            self.settings['last_echo'] = effects.get('echo', False)
            self.settings['last_reverb_intensity'] = effects.get('reverb_intensity', 0)
            self.settings['last_volume_db'] = effects.get('volume_db', 0)
            self.save_settings()

            # Настройка голоса
            if voice['system']:
                self.engine.setProperty('voice', voice['id'])
                self.engine.setProperty('rate', speed)
                self.engine.setProperty('volume', volume)
            else:
                available_voices = self.engine.getProperty('voices')
                if available_voices:
                    self.engine.setProperty('voice', available_voices[0].id)
                self.engine.setProperty('rate', speed)
                self.engine.setProperty('volume', volume)
                if 'male' in voice['id']:
                    self.engine.setProperty('pitch', 0.7)
                else:
                    self.engine.setProperty('pitch', 1.3)

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_wav_path = temp_wav.name

            self.engine.save_to_file(text, temp_wav_path)
            self.engine.runAndWait()

            if os.path.exists(temp_wav_path):
                sound = AudioSegment.from_wav(temp_wav_path)
                os.remove(temp_wav_path)

                # Применение эффектов
                if 'pitch' in effects and effects['pitch'] != 0:
                    octaves = effects['pitch'] / 12.0
                    new_rate = int(sound.frame_rate * (2.0 ** octaves))
                    sound = sound._spawn(sound.raw_data, overrides={"frame_rate": new_rate})
                    sound = sound.set_frame_rate(44100)

                if 'echo' in effects and effects['echo']:
                    echo_sound = sound - 20
                    sound = sound.overlay(echo_sound, position=400)

                if 'reverb_intensity' in effects and effects['reverb_intensity'] > 0:
                    reverb_sound = sound - (20 - effects['reverb_intensity'] / 5)
                    for i in range(1, 4):
                        delay = 100 * i
                        attenuated = sound - (20 + i * 10 - effects['reverb_intensity'] / 5)
                        sound = sound.overlay(attenuated, position=delay)

                if 'volume_db' in effects and effects['volume_db'] != 0:
                    sound = sound + effects['volume_db']

                if 'normalize' in effects and effects['normalize']:
                    sound = sound.normalize()

                if save_path:
                    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                    ext = os.path.splitext(save_path)[1].lower()[1:]
                    if ext == 'mp3':
                        sound.export(save_path, format="mp3", bitrate="192k")
                    elif ext == 'ogg':
                        sound.export(save_path, format="ogg")
                    else:
                        sound.export(save_path, format=ext)
                    if callback:
                        callback(True, "Аудио успешно сохранено")
                else:
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
                        temp_mp3_path = temp_mp3.name
                    sound.export(temp_mp3_path, format="mp3")

                    def play_func():
                        self.on_start(None)
                        self.current_player = subprocess.Popen(
                            ["ffplay", "-nodisp", "-autoexit", temp_mp3_path],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        self.current_player.wait()
                        os.remove(temp_mp3_path)
                        self.current_player = None
                        self.on_finish(None, True)
                        if callback and not self.stop_requested:
                            callback(True, "Воспроизведение завершено")

                    thread = threading.Thread(target=play_func)
                    thread.daemon = True
                    thread.start()

        except Exception as e:
            if callback:
                callback(False, f"Ошибка: {str(e)}")
            else:
                raise Exception(f"Ошибка: {str(e)}")

    def preview_voice(self, voice_idx: int, callback: Optional[Callable] = None, effects: Optional[Dict] = None):
        """Воспроизводит образец голоса"""
        if effects is None:
            effects = {}
        sample_texts = {
            'ru': 'Привет, это пример голоса. Данный голос предназначен для русского языка.',
            'en': 'Hello, this is a voice sample. This voice is designed for English language.',
            'de': 'Hallo, dies ist eine Sprachprobe. Diese Stimme ist für die deutsche Sprache ausgelegt.',
            'fr': 'Bonjour, ceci est un échantillon vocal. Cette voix est conçue pour la langue française.',
            'es': 'Hola, esta es una muestra de voz. Esta voz está diseñada para el idioma español.',
            'it': 'Ciao, questo è un campione vocale. Questa voce è progettata per la lingua italiana.',
            'pt': 'Olá, esta é uma amostra de voz. Esta voz é projetada para a língua portuguesa.'
        }

        voice = self.voices[voice_idx]
        lang = voice['languages'][0][:2] if voice['languages'] else 'en'
        text = sample_texts.get(lang, sample_texts['en'])

        self.text_to_speech(text, voice_idx, 150, self.settings['last_volume'], None, callback, effects)

    def get_default_output_path(self, format: str = "mp3") -> str:
        """Возвращает путь для сохранения по умолчанию"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"marilyntone_{timestamp}.{format}"
        return os.path.join(self.settings['output_folder'], filename)

    def get_voice_info(self, voice_idx: int) -> dict:
        """Возвращает информацию о голосе по индексу"""
        if 0 <= voice_idx < len(self.voices):
            return self.voices[voice_idx]
        return {}