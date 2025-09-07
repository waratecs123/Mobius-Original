# functions.py
import pyttsx3
from typing import Optional, List, Callable
import os
from pydub import AudioSegment
import tempfile
import threading
import time
import json
from pathlib import Path


class VoiceEngine:
    def __init__(self):
        self.engine = None
        self.init_engine()
        self.voices = self.load_voices()
        self.is_speaking = False
        self.stop_requested = False
        self.settings_file = "voice_settings.json"
        self.load_settings()

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
        # Обработчики событий
        self.engine.connect('started-utterance', self.on_start)
        self.engine.connect('finished-utterance', self.on_finish)

    def load_voices(self) -> List[dict]:
        """Возвращает список доступных голосов с параметрами."""
        voices = [
            # Русские голоса
            {'id': 'russian_male', 'name': 'Русский (Мужской)', 'gender': 'male', 'languages': ['ru'], 'system': False},
            {'id': 'russian_female', 'name': 'Русский (Женский)', 'gender': 'female', 'languages': ['ru'],
             'system': False},

            # Английские голоса
            {'id': 'english_us_male', 'name': 'English (US Male)', 'gender': 'male', 'languages': ['en-US'],
             'system': False},
            {'id': 'english_us_female', 'name': 'English (US Female)', 'gender': 'female', 'languages': ['en-US'],
             'system': False},
            {'id': 'english_uk_male', 'name': 'English (UK Male)', 'gender': 'male', 'languages': ['en-GB'],
             'system': False},
            {'id': 'english_uk_female', 'name': 'English (UK Female)', 'gender': 'female', 'languages': ['en-GB'],
             'system': False},

            # Другие языки
            {'id': 'german_male', 'name': 'Deutsch (Männlich)', 'gender': 'male', 'languages': ['de'], 'system': False},
            {'id': 'german_female', 'name': 'Deutsch (Weiblich)', 'gender': 'female', 'languages': ['de'],
             'system': False},
            {'id': 'french_male', 'name': 'Français (Homme)', 'gender': 'male', 'languages': ['fr'], 'system': False},
            {'id': 'french_female', 'name': 'Français (Femme)', 'gender': 'female', 'languages': ['fr'],
             'system': False},
            {'id': 'spanish_male', 'name': 'Español (Hombre)', 'gender': 'male', 'languages': ['es'], 'system': False},
            {'id': 'spanish_female', 'name': 'Español (Mujer)', 'gender': 'female', 'languages': ['es'],
             'system': False},
        ]

        # Добавляем системные голоса
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
            'output_folder': str(Path.home() / "Documents" / "MarilynTone"),
            'auto_save': False
        }

        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = {**self.default_settings, **json.load(f)}
            else:
                self.settings = self.default_settings

            # Создаем папку для сохранения, если не существует
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
        if self.is_speaking:
            self.stop_requested = True
            try:
                self.engine.stop()
            except:
                pass
            self.init_engine()

    def text_to_speech(self, text: str, voice_idx: int, speed: int = 150,
                       save_path: Optional[str] = None, callback: Optional[Callable] = None):
        """Озвучивает текст с возможностью сохранения в файл."""
        try:
            if voice_idx >= len(self.voices):
                raise Exception("Неверный индекс голоса")

            voice = self.voices[voice_idx]
            self.init_engine()

            # Сохраняем последние настройки
            self.settings['last_voice_index'] = voice_idx
            self.settings['last_speed'] = speed
            self.save_settings()

            # Настройка голоса
            if voice['system']:
                # Системные голоса
                self.engine.setProperty('voice', voice['id'])
                self.engine.setProperty('rate', speed)
                self.engine.setProperty('pitch', 1.0)
            else:
                # Виртуальные голоса
                available_voices = self.engine.getProperty('voices')
                if available_voices:
                    self.engine.setProperty('voice', available_voices[0].id)

                self.engine.setProperty('rate', speed)

                # Настройка pitch для разных голосов
                if 'male' in voice['id']:
                    self.engine.setProperty('pitch', 0.7)
                else:
                    self.engine.setProperty('pitch', 1.3)

            if save_path:
                # Создание директории если не существует
                os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

                if save_path.endswith('.mp3'):
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                        temp_wav_path = temp_wav.name

                    self.engine.save_to_file(text, temp_wav_path)
                    self.engine.runAndWait()

                    if os.path.exists(temp_wav_path):
                        try:
                            sound = AudioSegment.from_wav(temp_wav_path)
                            sound.export(save_path, format="mp3", bitrate="192k")
                        finally:
                            os.remove(temp_wav_path)

                elif save_path.endswith('.ogg'):
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                        temp_wav_path = temp_wav.name

                    self.engine.save_to_file(text, temp_wav_path)
                    self.engine.runAndWait()

                    if os.path.exists(temp_wav_path):
                        try:
                            sound = AudioSegment.from_wav(temp_wav_path)
                            sound.export(save_path, format="ogg")
                        finally:
                            os.remove(temp_wav_path)
                else:
                    self.engine.save_to_file(text, save_path)
                    self.engine.runAndWait()

                if callback:
                    callback(True, "Аудио успешно сохранено")

            else:
                # Воспроизведение
                def speak():
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                        if callback and not self.stop_requested:
                            callback(True, "Воспроизведение завершено")
                    except Exception as e:
                        if callback:
                            callback(False, f"Ошибка воспроизведения: {str(e)}")

                # Запуск в отдельном потоке
                thread = threading.Thread(target=speak)
                thread.daemon = True
                thread.start()

        except Exception as e:
            if callback:
                callback(False, f"Ошибка: {str(e)}")
            else:
                raise Exception(f"Ошибка: {str(e)}")

    def preview_voice(self, voice_idx: int, callback: Optional[Callable] = None):
        """Воспроизводит образец голоса"""
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

        self.text_to_speech(text, voice_idx, 150, None, callback)

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