import asyncio
import json
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional, List, Callable
import pygame
import pyttsx3
from gtts import gTTS
import edge_tts
import librosa
import numpy as np
import soundfile as sf
import logging
import requests
import re
from docx import Document
import pyth
import PyPDF2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VoiceEngine:
    def __init__(self):
        self.engine = None
        self.current_api = None
        self.preview_cache = {}  # Cache for preview audio
        self.init_engine()
        self.voices = self.load_voices()
        self.is_speaking = False
        self.stop_requested = False
        self.settings_file = "voice_settings.json"
        self.load_settings()
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            logging.info("Pygame mixer initialized successfully")
        except Exception as e:
            logging.error(f"Pygame mixer initialization failed: {e}")

    def init_engine(self):
        """Initializes the pyttsx3 TTS engine."""
        if self.engine:
            try:
                self.engine.stop()
                self.engine = None
            except:
                pass
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.connect('started-utterance', self.on_start)
            self.engine.connect('finished-utterance', self.on_finish)
            logging.info("pyttsx3 engine initialized")
        except Exception as e:
            logging.error(f"pyttsx3 initialization failed: {e}")

    def check_internet(self):
        """Checks if internet connection is available."""
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except requests.ConnectionError:
            logging.error("No internet connection available")
            return False

    def load_voices(self) -> List[dict]:
        """Returns a list of available voices with parameters."""
        voices = [
            {'id': 'russian_male', 'name': 'Русский (Мужской)', 'gender': 'male', 'languages': ['ru'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'russian_female', 'name': 'Русский (Женский)', 'gender': 'female', 'languages': ['ru'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'english_us_male', 'name': 'English (US Male)', 'gender': 'male', 'languages': ['en-US'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'english_us_female', 'name': 'English (US Female)', 'gender': 'female', 'languages': ['en-US'], 'system': False, 'api': 'pyttsx3'},
            {'id': 'gtts_russian', 'name': 'Google Русский (RU)', 'gender': 'female', 'languages': ['ru'], 'api': 'gtts', 'tld': 'ru'},
            {'id': 'gtts_english_us', 'name': 'Google English (US)', 'gender': 'female', 'languages': ['en'], 'api': 'gtts', 'tld': 'us'},
            {'id': 'gtts_english_uk', 'name': 'Google English (UK)', 'gender': 'female', 'languages': ['en'], 'api': 'gtts', 'tld': 'co.uk'},
            {'id': 'gtts_french', 'name': 'Google French', 'gender': 'female', 'languages': ['fr'], 'api': 'gtts', 'tld': 'fr'},
            {'id': 'gtts_spanish', 'name': 'Google Spanish', 'gender': 'female', 'languages': ['es'], 'api': 'gtts', 'tld': 'es'},
            {'id': 'en-US-GuyNeural', 'name': 'Edge English US Guy (Neural)', 'gender': 'male', 'languages': ['en-US'], 'api': 'edge_tts'},
            {'id': 'en-US-JennyNeural', 'name': 'Edge English US Jenny (Neural)', 'gender': 'female', 'languages': ['en-US'], 'api': 'edge_tts'},
            {'id': 'ru-RU-DmitryNeural', 'name': 'Edge Russian Dmitry (Neural)', 'gender': 'male', 'languages': ['ru-RU'], 'api': 'edge_tts'},
            {'id': 'ru-RU-SvetlanaNeural', 'name': 'Edge Russian Svetlana (Neural)', 'gender': 'female', 'languages': ['ru-RU'], 'api': 'edge_tts'},
            {'id': 'fr-FR-DeniseNeural', 'name': 'Edge French Denise (Neural)', 'gender': 'female', 'languages': ['fr-FR'], 'api': 'edge_tts'},
            {'id': 'es-ES-AlvaroNeural', 'name': 'Edge Spanish Alvaro (Neural)', 'gender': 'male', 'languages': ['es-ES'], 'api': 'edge_tts'},
            {'id': 'de-DE-ConradNeural', 'name': 'Edge German Conrad (Neural)', 'gender': 'male', 'languages': ['de-DE'], 'api': 'edge_tts'},
            {'id': 'it-IT-IsabellaNeural', 'name': 'Edge Italian Isabella (Neural)', 'gender': 'female', 'languages': ['it-IT'], 'api': 'edge_tts'},
        ]
        try:
            temp_engine = pyttsx3.init()
            for voice in temp_engine.getProperty('voices'):
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'gender': 'male' if 'male' in voice.name.lower() else 'female',
                    'languages': [lang for lang in voice.languages] if voice.languages else ['en-US'],
                    'system': True,
                    'api': 'pyttsx3'
                }
                voices.append(voice_info)
            temp_engine.stop()
        except Exception as e:
            logging.error(f"Failed to load pyttsx3 voices: {e}")
        return voices

    def load_settings(self):
        """Loads settings from a file or sets defaults."""
        self.default_settings = {
            'last_voice_index': 0,
            'last_speed': 150,
            'output_folder': str(Path.home() / "Documents" / "MarilynTone"),
            'auto_save': False,
            'effects': {
                'pitch_shift': {'enabled': False, 'semitones': 0},
                'volume_adjust': {'enabled': False, 'db': 0},
                'reverb': {'enabled': False, 'room_scale': 0},
                'emotion': {'enabled': False, 'type': 'neutral'},
                'bg_music': {'enabled': False, 'type': 'none', 'volume': 0.3, 'custom_path': ''}
            }
        }
        try:
            if Path(self.settings_file).exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings = self.default_settings.copy()
                    self.settings.update(loaded_settings)
                    self.settings['effects'] = self.default_settings['effects'].copy()
                    self.settings['effects'].update(loaded_settings.get('effects', {}))
            else:
                self.settings = self.default_settings.copy()
            Path(self.settings['output_folder']).mkdir(parents=True, exist_ok=True)
            logging.info("Settings loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")
            self.settings = self.default_settings.copy()

    def save_settings(self):
        """Saves settings to a file with debouncing."""
        if not hasattr(self, '_last_save_time'):
            self._last_save_time = 0
        current_time = time.time()
        if current_time - self._last_save_time >= 1:
            try:
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, ensure_ascii=False, indent=2)
                self._last_save_time = current_time
                logging.info("Settings saved successfully")
            except Exception as e:
                logging.error(f"Failed to save settings: {e}")

    def on_start(self, name):
        self.is_speaking = True
        self.stop_requested = False
        logging.info(f"Speech started: {name}")

    def on_finish(self, name, completed):
        self.is_speaking = False
        logging.info(f"Speech finished: {name}, completed: {completed}")

    def stop_speech(self):
        """Stops the current playback."""
        if self.is_speaking:
            self.stop_requested = True
            if self.current_api == 'pyttsx3':
                try:
                    self.engine.stop()
                    logging.info("pyttsx3 speech stopped")
                except Exception as e:
                    logging.error(f"Failed to stop pyttsx3 speech: {e}")
                self.init_engine()
            else:
                try:
                    pygame.mixer.music.stop()
                    logging.info("Pygame mixer music stopped")
                except Exception as e:
                    logging.error(f"Failed to stop pygame music: {e}")

    async def _edge_tts_synthesize(self, text: str, voice_id: str, rate_str: str, save_path: Optional[str] = None, emotion: str = 'neutral'):
        """Helper method for asynchronous edge_tts synthesis with emotion."""
        try:
            prosody = f'<prosody expressiveness="{emotion}">' if emotion != 'neutral' else ''
            text = f'<mstts:express-as style="{emotion}">{text}</mstts:express-as>' if emotion != 'neutral' else text
            communicate = edge_tts.Communicate(text, voice_id, rate=rate_str, prosody=prosody)
            if save_path:
                await communicate.save(save_path)
                logging.info(f"Edge TTS saved to {save_path}")
            else:
                temp_mp3 = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                temp_mp3_path = temp_mp3.name
                temp_mp3.close()
                await communicate.save(temp_mp3_path)
                logging.info(f"Edge TTS saved to temporary file {temp_mp3_path}")
                return temp_mp3_path
        except Exception as e:
            logging.error(f"Edge TTS synthesis failed: {e}")
            raise

    def apply_effects(self, audio: np.ndarray, sr: int) -> tuple[np.ndarray, int]:
        """Applies enabled audio effects to the audio array."""
        effects = self.settings.get('effects', {})
        original_dtype = audio.dtype
        audio = audio.astype(np.float32)
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0:
            audio = audio / max_amplitude
            logging.info("Audio normalized before effects")

        if effects.get('pitch_shift', {}).get('enabled', False):
            semitones = float(effects['pitch_shift'].get('semitones', 0))
            if semitones != 0:
                try:
                    audio = librosa.effects.pitch_shift(y=audio, sr=sr, n_steps=semitones)
                    logging.info(f"Applied pitch shift: {semitones} semitones")
                except Exception as e:
                    logging.error(f"Pitch shift error: {e}")

        if effects.get('volume_adjust', {}).get('enabled', False):
            db = float(effects['volume_adjust'].get('db', 0))
            if db != 0:
                try:
                    gain = 10 ** (db / 20.0)
                    audio = audio * gain
                    logging.info(f"Applied volume adjustment: {db} dB")
                except Exception as e:
                    logging.error(f"Volume adjustment error: {e}")

        if effects.get('reverb', {}).get('enabled', False):
            room_scale = float(effects['reverb'].get('room_scale', 0))
            if room_scale > 0:
                try:
                    reverb_length = int(0.7 * sr)
                    decay = np.exp(-6.0 * np.arange(reverb_length) / (room_scale * sr / 100.0))
                    impulse_response = decay * np.random.randn(reverb_length)
                    impulse_response[0] = 1.0
                    impulse_response *= (room_scale / 100.0)
                    audio = np.convolve(audio, impulse_response, mode='full')[:len(audio)]
                    logging.info(f"Applied reverb: room scale {room_scale}")
                except Exception as e:
                    logging.error(f"Reverb error: {e}")

        if effects.get('bg_music', {}).get('enabled', False) and effects['bg_music'].get('type') != 'none':
            try:
                bg_music_files = {
                    'calm_piano': 'assets/audio/calm_piano.mp3',
                    'epic_orchestral': 'assets/audio/epic_orchestral.mp3',
                    'ambient_lofi': 'assets/audio/ambient_lofi.mp3'
                }
                bg_music_path = effects['bg_music'].get('custom_path') if effects['bg_music']['type'] == 'custom' else bg_music_files.get(effects['bg_music']['type'])
                if bg_music_path and Path(bg_music_path).exists():
                    bg_audio, bg_sr = librosa.load(bg_music_path, sr=sr)
                    if len(bg_audio) < len(audio):
                        bg_audio = np.tile(bg_audio, int(np.ceil(len(audio) / len(bg_audio))))[:len(audio)]
                    elif len(bg_audio) > len(audio):
                        bg_audio = bg_audio[:len(audio)]
                    volume = effects['bg_music'].get('volume', 0.3)
                    audio = audio * (1.0 - volume) + bg_audio * volume
                    logging.info(f"Applied background music: {effects['bg_music']['type']}, volume {volume}")
                else:
                    logging.warning(f"Background music file not found: {bg_music_path}")
            except Exception as e:
                logging.error(f"Background music error: {e}")

        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0:
            audio = audio / max_amplitude
            logging.info("Audio normalized after effects")
        audio = np.clip(audio, -1.0, 1.0)
        if original_dtype == np.int16:
            audio = (audio * 32767).astype(np.int16)
        else:
            audio = audio.astype(np.float32)
        return audio, sr

    def process_pauses(self, text: str) -> List[tuple[str, float]]:
        """Parses text for <пауза: X сек> tags and returns segments with pause durations."""
        pause_pattern = re.compile(r'<пауза:\s*(\d*\.?\d+)\s*сек>')
        segments = []
        last_pos = 0
        for match in pause_pattern.finditer(text):
            start, end = match.span()
            pause_duration = float(match.group(1))
            text_segment = text[last_pos:start].strip()
            if text_segment:
                segments.append((text_segment, 0.0))
            segments.append(("", pause_duration))
            last_pos = end
        final_segment = text[last_pos:].strip()
        if final_segment:
            segments.append((final_segment, 0.0))
        return segments if segments else [(text, 0.0)]

    def text_to_speech(self, text: str, voice_idx: int, speed: int = 150,
                       save_path: Optional[str] = None, callback: Optional[Callable] = None):
        """Synthesizes text to speech with support for pauses."""
        if not text or voice_idx < 0 or voice_idx >= len(self.voices):
            if callback:
                callback(False, "Ошибка: Неверный текст или индекс голоса")
            return
        voice = self.voices[voice_idx]
        self.current_api = voice['api']
        self.stop_requested = False
        self.settings['last_voice_index'] = voice_idx
        self.settings['last_speed'] = speed
        if self.settings.get('auto_save', False):
            self.save_settings()

        if voice['api'] in ['gtts', 'edge_tts'] and not self.check_internet():
            if callback:
                callback(False, "Ошибка: Нет подключения к интернету")
            return

        def run_synthesis():
            temp_files = []
            try:
                segments = self.process_pauses(text)
                combined_audio = np.array([], dtype=np.float32)
                sr = 44100

                for segment_text, pause_duration in segments:
                    if self.stop_requested:
                        break
                    if segment_text:
                        temp_file = None
                        if voice['api'] == 'pyttsx3':
                            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
                            self.engine.setProperty('voice', voice['id'])
                            self.engine.setProperty('rate', speed)
                            self.engine.save_to_file(segment_text, temp_wav)
                            self.engine.runAndWait()
                            audio, sr = librosa.load(temp_wav)
                            temp_file = temp_wav
                        elif voice['api'] == 'gtts':
                            tts = gTTS(text=segment_text, lang=voice['languages'][0], tld=voice.get('tld', 'com'), slow=False)
                            temp_mp3 = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                            temp_mp3_path = temp_mp3.name
                            temp_mp3.close()
                            tts.save(temp_mp3_path)
                            speed_adjusted = speed / 150.0
                            audio, sr = librosa.load(temp_mp3_path)
                            if speed_adjusted != 1.0:
                                audio = librosa.effects.time_stretch(audio, rate=1.0 / speed_adjusted)
                            temp_file = temp_mp3_path
                        elif voice['api'] == 'edge_tts':
                            rate_str = f"+{(speed - 150) * 2}%" if speed >= 150 else f"-{(150 - speed) * 2}%"
                            emotion = self.settings['effects'].get('emotion', {}).get('type', 'neutral') if self.settings['effects'].get('emotion', {}).get('enabled', False) else 'neutral'
                            temp_mp3 = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                            temp_mp3_path = temp_mp3.name
                            temp_mp3.close()
                            asyncio.run(self._edge_tts_synthesize(segment_text, voice['id'], rate_str, temp_mp3_path, emotion))
                            audio, sr = librosa.load(temp_mp3_path)
                            temp_file = temp_mp3_path
                        audio, sr = self.apply_effects(audio, sr)
                        combined_audio = np.concatenate((combined_audio, audio))
                        temp_files.append(temp_file)
                    if pause_duration > 0:
                        silence = np.zeros(int(pause_duration * sr), dtype=np.float32)
                        combined_audio = np.concatenate((combined_audio, silence))

                if self.stop_requested:
                    if callback:
                        callback(False, "Синтез остановлен")
                    return

                if save_path:
                    sf.write(save_path, combined_audio, sr)
                    logging.info(f"Saved audio to {save_path}")
                else:
                    temp_out = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                    sf.write(temp_out.name, combined_audio, sr)
                    temp_files.append(temp_out.name)
                    temp_out.close()
                    pygame.mixer.music.load(temp_files[-1])
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() and not self.stop_requested:
                        time.sleep(0.1)
                    pygame.mixer.music.stop()

                if callback:
                    callback(True, "Воспроизведение завершено" if not save_path else "Аудио сохранено")
            except Exception as e:
                logging.error(f"Synthesis error: {e}")
                if callback:
                    callback(False, f"Ошибка синтеза: {str(e)}")
            finally:
                for temp_file in temp_files:
                    Path(temp_file).unlink(missing_ok=True)

        threading.Thread(target=run_synthesis, daemon=True).start()

    def preview_voice(self, voice_idx: int, callback: Optional[Callable] = None):
        """Previews a sample of the selected voice with caching."""
        sample_texts = {
            'ru': "Тест голоса.",
            'ru-RU': "Тест голоса.",
            'en-US': "Voice test.",
            'en': "Voice test.",
            'fr': "Test de voix.",
            'fr-FR': "Test de voix.",
            'es': "Prueba de voz.",
            'es-ES': "Prueba de voz.",
            'de-DE': "Stimmtest.",
            'it-IT': "Test vocale."
        }
        voice = self.voices[voice_idx]
        lang = voice['languages'][0]
        text = sample_texts.get(lang, sample_texts['en-US'])
        cache_key = (voice_idx, text, self.settings['last_speed'])

        if cache_key in self.preview_cache:
            try:
                pygame.mixer.music.load(self.preview_cache[cache_key])
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() and not self.stop_requested:
                    time.sleep(0.1)
                pygame.mixer.music.stop()
                if callback:
                    callback(True, "Воспроизведение завершено")
                return
            except Exception as e:
                logging.error(f"Cache playback error: {e}")
                del self.preview_cache[cache_key]

        def run_preview():
            temp_file = None
            try:
                temp_out = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                temp_file = temp_out.name
                temp_out.close()
                self.text_to_speech(text, voice_idx, speed=150, save_path=temp_file, callback=None)
                self.preview_cache[cache_key] = temp_file
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() and not self.stop_requested:
                    time.sleep(0.1)
                pygame.mixer.music.stop()
                if callback:
                    callback(True, "Воспроизведение завершено")
            except Exception as e:
                logging.error(f"Preview error: {e}")
                if callback:
                    callback(False, f"Ошибка предпросмотра: {str(e)}")
                if temp_file and temp_file in self.preview_cache:
                    del self.preview_cache[cache_key]
                    Path(temp_file).unlink(missing_ok=True)

        threading.Thread(target=run_preview, daemon=True).start()

    def get_voice_info(self, voice_idx: int) -> Optional[dict]:
        """Returns information about the selected voice."""
        if 0 <= voice_idx < len(self.voices):
            return self.voices[voice_idx]
        return None

    def get_default_output_path(self, ext: str) -> str:
        """Returns the default output file path with a timestamp."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return str(Path(self.settings['output_folder']) / f"speech_{timestamp}.{ext}")

    def import_text(self, file_path: str) -> str:
        """Imports text from various file formats."""
        try:
            ext = Path(file_path).suffix.lower()
            if ext == '.pdf':
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ''
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + '\n'
                    return text.strip() if text.strip() else ''
            elif ext == '.docx':
                doc = Document(file_path)
                return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
            elif ext == '.rtf':
                with open(file_path, 'r', encoding='utf-8') as f:
                    rtf_content = f.read()
                return pyth.rtf2text(rtf_content)
            else:
                # Try to read as a text file with multiple encoding attempts
                encodings = ['utf-8', 'latin-1', 'cp1252']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            return f.read().strip()
                    except UnicodeDecodeError:
                        continue
                raise ValueError("Не удалось декодировать текстовый файл")
        except Exception as e:
            logging.error(f"Import error: {e}")
            raise