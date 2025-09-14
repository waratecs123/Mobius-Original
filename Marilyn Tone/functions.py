# functions.py
import pyttsx3
from typing import Optional, List, Callable
import os
import pygame  # Для воспроизведения аудио
import tempfile
import threading
import time
import json
from pathlib import Path
from gtts import gTTS  # Google Text-to-Speech API
import edge_tts  # Microsoft Edge TTS API
import asyncio


class VoiceEngine:
    def __init__(self):
        self.engine = None
        self.current_api = None
        self.init_engine()
        self.voices = self.load_voices()
        self.is_speaking = False
        self.stop_requested = False
        self.settings_file = "voice_settings.json"
        self.load_settings()
        pygame.mixer.init()  # Инициализация pygame для воспроизведения

    def init_engine(self):
        """Инициализирует движок pyttsx3 TTS."""
        if self.engine:
            try:
                self.engine.stop()
                self.engine = None
            except:
                pass

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.connect('started-utterance', self.on_start)
        self.engine.connect('finished-utterance', self.on_finish)

    def load_voices(self) -> List[dict]:
        """Возвращает список доступных голосов с параметрами, включая gTTS и Edge TTS."""
        voices = [
            # Виртуальные голоса pyttsx3
            {'id': 'russian_male', 'name': 'Русский (Мужской)', 'gender': 'male', 'languages': ['ru'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'russian_female', 'name': 'Русский (Женский)', 'gender': 'female', 'languages': ['ru'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'english_us_male', 'name': 'English (US Male)', 'gender': 'male', 'languages': ['en-US'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'english_us_female', 'name': 'English (US Female)', 'gender': 'female', 'languages': ['en-US'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'english_uk_male', 'name': 'English (UK Male)', 'gender': 'male', 'languages': ['en-GB'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'english_uk_female', 'name': 'English (UK Female)', 'gender': 'female', 'languages': ['en-GB'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'german_male', 'name': 'Deutsch (Männlich)', 'gender': 'male', 'languages': ['de'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'german_female', 'name': 'Deutsch (Weiblich)', 'gender': 'female', 'languages': ['de'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'french_male', 'name': 'Français (Homme)', 'gender': 'male', 'languages': ['fr'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'french_female', 'name': 'Français (Femme)', 'gender': 'female', 'languages': ['fr'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'spanish_male', 'name': 'Español (Hombre)', 'gender': 'male', 'languages': ['es'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'spanish_female', 'name': 'Español (Mujer)', 'gender': 'female', 'languages': ['es'], 'system': False, 'api': 'pyttsx3'},

            # Голоса gTTS с разными акцентами (tld)
            {'id': 'gtts_russian', 'name': 'Google Русский', 'gender': 'female', 'languages': ['ru'], 'api': 'gtts', 'tld': 'ru'},
            {'id': 'gtts_english_us', 'name': 'Google English (US)', 'gender': 'female', 'languages': ['en'], 'api': 'gtts', 'tld': 'us'},
            {'id': 'gtts_english_uk', 'name': 'Google English (UK)', 'gender': 'female', 'languages': ['en'], 'api': 'gtts', 'tld': 'co.uk'},
            {'id': 'gtts_english_au', 'name': 'Google English (AU)', 'gender': 'female', 'languages': ['en'], 'api': 'gtts', 'tld': 'com.au'},
            {'id': 'gtts_english_ca', 'name': 'Google English (CA)', 'gender': 'female', 'languages': ['en'], 'api': 'gtts', 'tld': 'ca'},
            {'id': 'gtts_english_in', 'name': 'Google English (IN)', 'gender': 'female', 'languages': ['en'], 'api': 'gtts', 'tld': 'co.in'},
            {'id': 'gtts_german', 'name': 'Google Deutsch', 'gender': 'female', 'languages': ['de'], 'api': 'gtts', 'tld': 'de'},
            {'id': 'gtts_french_fr', 'name': 'Google Français (FR)', 'gender': 'female', 'languages': ['fr'], 'api': 'gtts', 'tld': 'fr'},
            {'id': 'gtts_french_ca', 'name': 'Google Français (CA)', 'gender': 'female', 'languages': ['fr'], 'api': 'gtts', 'tld': 'ca'},
            {'id': 'gtts_spanish_es', 'name': 'Google Español (ES)', 'gender': 'female', 'languages': ['es'], 'api': 'gtts', 'tld': 'es'},
            {'id': 'gtts_spanish_mx', 'name': 'Google Español (MX)', 'gender': 'female', 'languages': ['es'], 'api': 'gtts', 'tld': 'com.mx'},
            {'id': 'gtts_portuguese_br', 'name': 'Google Português (BR)', 'gender': 'female', 'languages': ['pt'], 'api': 'gtts', 'tld': 'com.br'},
            {'id': 'gtts_portuguese_pt', 'name': 'Google Português (PT)', 'gender': 'female', 'languages': ['pt'], 'api': 'gtts', 'tld': 'pt'},

            # Голоса Edge TTS (выборка для разнообразия)
            {'id': 'en-US-GuyNeural', 'name': 'Edge English US Guy (Neural)', 'gender': 'male', 'languages': ['en-US'], 'api': 'edge_tts'},
            {'id': 'en-US-AnaNeural', 'name': 'Edge English US Ana (Neural)', 'gender': 'female', 'languages': ['en-US'], 'api': 'edge_tts'},
            {'id': 'en-GB-RyanNeural', 'name': 'Edge English GB Ryan (Neural)', 'gender': 'male', 'languages': ['en-GB'], 'api': 'edge_tts'},
            {'id': 'en-GB-SoniaNeural', 'name': 'Edge English GB Sonia (Neural)', 'gender': 'female', 'languages': ['en-GB'], 'api': 'edge_tts'},
            {'id': 'ru-RU-DmitryNeural', 'name': 'Edge Russian Dmitry (Neural)', 'gender': 'male', 'languages': ['ru-RU'], 'api': 'edge_tts'},
            {'id': 'ru-RU-SvetlanaNeural', 'name': 'Edge Russian Svetlana (Neural)', 'gender': 'female', 'languages': ['ru-RU'], 'api': 'edge_tts'},
            {'id': 'de-DE-ConradNeural', 'name': 'Edge German Conrad (Neural)', 'gender': 'male', 'languages': ['de-DE'], 'api': 'edge_tts'},
            {'id': 'de-DE-KatjaNeural', 'name': 'Edge German Katja (Neural)', 'gender': 'female', 'languages': ['de-DE'], 'api': 'edge_tts'},
            {'id': 'fr-FR-AlainNeural', 'name': 'Edge French Alain (Neural)', 'gender': 'male', 'languages': ['fr-FR'], 'api': 'edge_tts'},
            {'id': 'fr-FR-DeniseNeural', 'name': 'Edge French Denise (Neural)', 'gender': 'female', 'languages': ['fr-FR'], 'api': 'edge_tts'},
            {'id': 'es-ES-AlvaroNeural', 'name': 'Edge Spanish Alvaro (Neural)', 'gender': 'male', 'languages': ['es-ES'], 'api': 'edge_tts'},
            {'id': 'es-ES-ElviraNeural', 'name': 'Edge Spanish Elvira (Neural)', 'gender': 'female', 'languages': ['es-ES'], 'api': 'edge_tts'},
            {'id': 'pt-BR-AntonioNeural', 'name': 'Edge Portuguese BR Antonio (Neural)', 'gender': 'male', 'languages': ['pt-BR'], 'api': 'edge_tts'},
            {'id': 'pt-BR-FranciscaNeural', 'name': 'Edge Portuguese BR Francisca (Neural)', 'gender': 'female', 'languages': ['pt-BR'], 'api': 'edge_tts'},
        ]

        try:
            temp_engine = pyttsx3.init()
            for voice in temp_engine.getProperty('voices'):
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'gender': 'male' if 'male' in voice.name.lower() else 'female',
                    'languages': voice.languages,
                    'system': True,
                    'api': 'pyttsx3'
                }
                voices.append(voice_info)
            temp_engine.stop()
        except:
            pass

        return voices

    def load_settings(self):
        """Загружает настройки из файла."""
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

            os.makedirs(self.settings['output_folder'], exist_ok=True)

        except:
            self.settings = self.default_settings

    def save_settings(self):
        """Сохраняет настройки в файл."""
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
        """Останавливает текущее воспроизведение."""
        if self.is_speaking:
            self.stop_requested = True
            if self.current_api == 'pyttsx3':
                try:
                    self.engine.stop()
                except:
                    pass
                self.init_engine()
            else:
                pygame.mixer.music.stop()

    async def _edge_tts_synthesize(self, text: str, voice_id: str, rate_str: str, save_path: Optional[str] = None):
        """Вспомогательный метод для асинхронного синтеза edge_tts."""
        communicate = edge_tts.Communicate(text, voice_id, rate=rate_str)
        if save_path:
            await communicate.save(save_path)
        else:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
                temp_mp3_path = temp_mp3.name
            await communicate.save(temp_mp3_path)
            return temp_mp3_path

    def text_to_speech(self, text: str, voice_idx: int, speed: int = 150,
                       save_path: Optional[str] = None, callback: Optional[Callable] = None):
        """Синтезирует текст в речь с возможностью сохранения в файл, поддерживает pyttsx3, gTTS и edge_tts."""
        try:
            if voice_idx >= len(self.voices):
                raise Exception("Неверный индекс голоса")

            voice = self.voices[voice_idx]
            self.current_api = voice['api']
            self.init_engine()

            self.settings['last_voice_index'] = voice_idx
            self.settings['last_speed'] = speed
            self.save_settings()

            if voice['api'] == 'gtts':
                lang = voice['languages'][0][:2] if len(voice['languages'][0]) > 2 else voice['languages'][0]
                tld = voice.get('tld', 'com')
                slow = speed < 100
                tts = gTTS(text=text, lang=lang, tld=tld, slow=slow)

                if save_path:
                    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                    tts.save(save_path)
                    if callback:
                        callback(True, "Аудио успешно сохранено")
                else:
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
                        temp_mp3_path = temp_mp3.name
                    tts.save(temp_mp3_path)

                    def play_audio():
                        try:
                            pygame.mixer.music.load(temp_mp3_path)
                            pygame.mixer.music.play()
                            while pygame.mixer.music.get_busy() and not self.stop_requested:
                                pygame.time.wait(100)
                            if callback and not self.stop_requested:
                                callback(True, "Воспроизведение завершено")
                        except Exception as e:
                            if callback:
                                callback(False, f"Ошибка воспроизведения: {str(e)}")
                        finally:
                            try:
                                os.remove(temp_mp3_path)
                            except:
                                pass

                    thread = threading.Thread(target=play_audio)
                    thread.daemon = True
                    thread.start()

            elif voice['api'] == 'edge_tts':
                rate = (speed - 150) * (100 / 150)
                rate_str = f"+{int(rate)}%" if rate >= 0 else f"{int(rate)}%"

                def run_edge_tts():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        if save_path:
                            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                            loop.run_until_complete(self._edge_tts_synthesize(text, voice['id'], rate_str, save_path))
                            if callback:
                                callback(True, "Аудио успешно сохранено")
                        else:
                            temp_mp3_path = loop.run_until_complete(self._edge_tts_synthesize(text, voice['id'], rate_str))
                            try:
                                pygame.mixer.music.load(temp_mp3_path)
                                pygame.mixer.music.play()
                                while pygame.mixer.music.get_busy() and not self.stop_requested:
                                    pygame.time.wait(100)
                                if callback and not self.stop_requested:
                                    callback(True, "Воспроизведение завершено")
                            except Exception as e:
                                if callback:
                                    callback(False, f"Ошибка воспроизведения: {str(e)}")
                            finally:
                                try:
                                    os.remove(temp_mp3_path)
                                except:
                                    pass
                        loop.close()
                    except Exception as e:
                        if callback:
                            callback(False, f"Ошибка: {str(e)}")

                thread = threading.Thread(target=run_edge_tts)
                thread.daemon = True
                thread.start()

            else:  # pyttsx3
                if voice['system']:
                    self.engine.setProperty('voice', voice['id'])
                    self.engine.setProperty('rate', speed)
                    self.engine.setProperty('pitch', 1.0)
                else:
                    available_voices = self.engine.getProperty('voices')
                    if available_voices:
                        self.engine.setProperty('voice', available_voices[0].id)
                    self.engine.setProperty('rate', speed)
                    if 'male' in voice['id']:
                        self.engine.setProperty('pitch', 0.7)
                    else:
                        self.engine.setProperty('pitch', 1.3)

                if save_path:
                    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                    if not save_path.endswith('.wav'):
                        raise Exception("Для pyttsx3 поддерживается только сохранение в WAV")
                    self.engine.save_to_file(text, save_path)
                    self.engine.runAndWait()
                    if callback:
                        callback(True, "Аудио успешно сохранено")
                else:
                    def play_audio():
                        try:
                            self.engine.say(text)
                            self.engine.runAndWait()
                            if callback and not self.stop_requested:
                                callback(True, "Воспроизведение завершено")
                        except Exception as e:
                            if callback:
                                callback(False, f"Ошибка воспроизведения: {str(e)}")

                    thread = threading.Thread(target=play_audio)
                    thread.daemon = True
                    thread.start()

        except Exception as e:
            if callback:
                callback(False, f"Ошибка: {str(e)}")
            else:
                raise Exception(f"Ошибка: {str(e)}")

    def preview_voice(self, voice_idx: int, callback: Optional[Callable] = None):
        """Воспроизводит образец выбранного голоса."""
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
        """Возвращает путь сохранения по умолчанию."""
        if format not in ["mp3", "wav"]:
            format = "mp3" if self.current_api in ['gtts', 'edge_tts'] else "wav"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"marilyntone_{timestamp}.{format}"
        return os.path.join(self.settings['output_folder'], filename)

    def get_voice_info(self, voice_idx: int) -> dict:
        """Возвращает информацию о голосе по индексу."""
        if 0 <= voice_idx < len(self.voices):
            return self.voices[voice_idx]
        return {}