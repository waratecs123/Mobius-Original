# functions.py
import pyttsx3
from typing import Optional, List
import os
from pydub import AudioSegment
import tempfile


class VoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.voices = self.load_voices()

    def load_voices(self) -> List[dict]:
        """Возвращает список доступных голосов с параметрами."""
        voices = [
            # Русские голоса
            {'id': 'russian_male', 'name': 'Русский (Мужской)', 'gender': 'male', 'languages': ['ru']},
            {'id': 'russian_female', 'name': 'Русский (Женский)', 'gender': 'female', 'languages': ['ru']},

            # Английские голоса
            {'id': 'english_us_male', 'name': 'English (US Male)', 'gender': 'male', 'languages': ['en-US']},
            {'id': 'english_us_female', 'name': 'English (US Female)', 'gender': 'female', 'languages': ['en-US']},
            {'id': 'english_uk_male', 'name': 'English (UK Male)', 'gender': 'male', 'languages': ['en-GB']},
            {'id': 'english_uk_female', 'name': 'English (UK Female)', 'gender': 'female', 'languages': ['en-GB']},

            # Другие языки
            {'id': 'german_male', 'name': 'Deutsch (Männlich)', 'gender': 'male', 'languages': ['de']},
            {'id': 'german_female', 'name': 'Deutsch (Weiblich)', 'gender': 'female', 'languages': ['de']},
            {'id': 'french_male', 'name': 'Français (Homme)', 'gender': 'male', 'languages': ['fr']},
            {'id': 'french_female', 'name': 'Français (Femme)', 'gender': 'female', 'languages': ['fr']},
            {'id': 'spanish_male', 'name': 'Español (Hombre)', 'gender': 'male', 'languages': ['es']},
            {'id': 'spanish_female', 'name': 'Español (Mujer)', 'gender': 'female', 'languages': ['es']},
            {'id': 'italian_male', 'name': 'Italiano (Uomo)', 'gender': 'male', 'languages': ['it']},
            {'id': 'italian_female', 'name': 'Italiano (Donna)', 'gender': 'female', 'languages': ['it']},
            {'id': 'japanese_male', 'name': '日本語 (男性)', 'gender': 'male', 'languages': ['ja']},
            {'id': 'japanese_female', 'name': '日本語 (女性)', 'gender': 'female', 'languages': ['ja']},
            {'id': 'chinese_male', 'name': '中文 (男性)', 'gender': 'male', 'languages': ['zh']},
            {'id': 'chinese_female', 'name': '中文 (女性)', 'gender': 'female', 'languages': ['zh']},
            {'id': 'korean_male', 'name': '한국어 (남성)', 'gender': 'male', 'languages': ['ko']},
            {'id': 'korean_female', 'name': '한국어 (여성)', 'gender': 'female', 'languages': ['ko']}
        ]

        # Добавляем системные голоса
        for voice in self.engine.getProperty('voices'):
            voice_info = {
                'id': voice.id,
                'name': voice.name,
                'gender': 'male' if 'male' in voice.name.lower() else 'female',
                'languages': voice.languages
            }
            voices.append(voice_info)

        return voices

    def text_to_speech(self, text: str, voice_idx: int, speed: int = 150, save_path: Optional[str] = None):
        """Озвучивает текст с возможностью сохранения в файл."""
        try:
            # Для виртуальных голосов используем настройки pitch и rate
            if voice_idx < len(self.voices):
                voice = self.voices[voice_idx]
                if voice['id'].startswith(('russian', 'english', 'german', 'french', 'spanish', 'italian', 'japanese',
                                           'chinese', 'korean')):
                    # Виртуальные голоса - настраиваем параметры
                    self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)  # Базовый голос
                    self.engine.setProperty('rate', speed)

                    # Настройка pitch для разных голосов
                    if 'male' in voice['id']:
                        self.engine.setProperty('pitch', 0.8)  # Более низкий голос
                    else:
                        self.engine.setProperty('pitch', 1.2)  # Более высокий голос
                else:
                    # Системные голоса
                    self.engine.setProperty('voice', voice['id'])
                    self.engine.setProperty('rate', speed)
                    self.engine.setProperty('pitch', 1.0)  # Нормальный pitch
            else:
                raise Exception("Неверный индекс голоса")

            if save_path:
                # Поддержка разных форматов
                if save_path.endswith('.mp3'):
                    temp_wav = os.path.join(tempfile.gettempdir(), 'temp_tts.wav')
                    self.engine.save_to_file(text, temp_wav)
                    self.engine.runAndWait()

                    # Конвертируем в MP3
                    sound = AudioSegment.from_wav(temp_wav)
                    sound.export(save_path, format="mp3")
                    os.remove(temp_wav)
                elif save_path.endswith('.ogg'):
                    temp_wav = os.path.join(tempfile.gettempdir(), 'temp_tts.wav')
                    self.engine.save_to_file(text, temp_wav)
                    self.engine.runAndWait()

                    # Конвертируем в OGG
                    sound = AudioSegment.from_wav(temp_wav)
                    sound.export(save_path, format="ogg")
                    os.remove(temp_wav)
                else:
                    self.engine.save_to_file(text, save_path)
                    self.engine.runAndWait()
            else:
                # Создаем новый движок для каждого воспроизведения
                temp_engine = pyttsx3.init()
                temp_engine.setProperty('voice', self.engine.getProperty('voice'))
                temp_engine.setProperty('rate', self.engine.getProperty('rate'))
                temp_engine.setProperty('pitch', self.engine.getProperty('pitch'))
                temp_engine.say(text)
                temp_engine.runAndWait()
                temp_engine.stop()

        except Exception as e:
            raise Exception(f"Ошибка: {e}")