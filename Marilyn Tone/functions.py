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
from io import BytesIO
import soundfile as sf


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
        pygame.mixer.init()

    def init_engine(self):
        """Initializes the pyttsx3 TTS engine."""
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
        """Returns a list of available voices with parameters, including gTTS and Edge TTS."""
        voices = [
            # pyttsx3 virtual voices
            {'id': 'russian_male', 'name': 'Русский (Мужской)', 'gender': 'male', 'languages': ['ru'], 'system': False,
             'api': 'pyttsx3'},
            {'id': 'russian_female', 'name': 'Русский (Женский)', 'gender': 'female', 'languages': ['ru'],
             'system': False, 'api': 'pyttsx3'},
            {'id': 'english_us_male', 'name': 'English (US Male)', 'gender': 'male', 'languages': ['en-US'],
             'system': False, 'api': 'pyttsx3'},
            {'id': 'english_us_female', 'name': 'English (US Female)', 'gender': 'female', 'languages': ['en-US'],
             'system': False, 'api': 'pyttsx3'},
            {'id': 'english_uk_male', 'name': 'English (UK Male)', 'gender': 'male', 'languages': ['en-GB'],
             'system': False, 'api': 'pyttsx3'},
            {'id': 'english_uk_female', 'name': 'English (UK Female)', 'gender': 'female', 'languages': ['en-GB'],
             'system': False, 'api': 'pyttsx3'},
            {'id': 'german_male', 'name': 'Deutsch (Männlich)', 'gender': 'male', 'languages': ['de'], 'system': False,
             'api': 'pyttsx3'},
            {'id': 'german_female', 'name': 'Deutsch (Weiblich)', 'gender': 'female', 'languages': ['de'],
             'system': False, 'api': 'pyttsx3'},
            {'id': 'french_male', 'name': 'Français (Homme)', 'gender': 'male', 'languages': ['fr'], 'system': False,
             'api': 'pyttsx3'},
            {'id': 'french_female', 'name': 'Français (Femme)', 'gender': 'female', 'languages': ['fr'],
             'system': False, 'api': 'pyttsx3'},
            {'id': 'spanish_male', 'name': 'Español (Hombre)', 'gender': 'male', 'languages': ['es'], 'system': False,
             'api': 'pyttsx3'},
            {'id': 'spanish_female', 'name': 'Español (Mujer)', 'gender': 'female', 'languages': ['es'],
             'system': False, 'api': 'pyttsx3'},
            {'id': 'italian_male', 'name': 'Italiano (Uomo)', 'gender': 'male', 'languages': ['it'], 'system': False,
             'api': 'pyttsx3'},
            {'id': 'italian_female', 'name': 'Italiano (Donna)', 'gender': 'female', 'languages': ['it'],
             'system': False, 'api': 'pyttsx3'},
            {'id': 'japanese_male', 'name': '日本語 (男性)', 'gender': 'male', 'languages': ['ja'], 'system': False,
             'api': 'pyttsx3'},
            {'id': 'japanese_female', 'name': '日本語 (女性)', 'gender': 'female', 'languages': ['ja'], 'system': False,
             'api': 'pyttsx3'},
            {'id': 'chinese_male', 'name': '中文 (男)', 'gender': 'male', 'languages': ['zh'], 'system': False,
             'api': 'pyttsx3'},
            {'id': 'chinese_female', 'name': '中文 (女)', 'gender': 'female', 'languages': ['zh'], 'system': False,
             'api': 'pyttsx3'},
            # gTTS voices
            {'id': 'gtts_russian', 'name': 'Google Русский', 'gender': 'female', 'languages': ['ru'], 'api': 'gtts',
             'tld': 'ru'},
            {'id': 'gtts_english_us', 'name': 'Google English (US)', 'gender': 'female', 'languages': ['en'],
             'api': 'gtts', 'tld': 'us'},
            {'id': 'gtts_english_uk', 'name': 'Google English (UK)', 'gender': 'female', 'languages': ['en'],
             'api': 'gtts', 'tld': 'co.uk'},
            {'id': 'gtts_english_au', 'name': 'Google English (AU)', 'gender': 'female', 'languages': ['en'],
             'api': 'gtts', 'tld': 'com.au'},
            {'id': 'gtts_english_ca', 'name': 'Google English (CA)', 'gender': 'female', 'languages': ['en'],
             'api': 'gtts', 'tld': 'ca'},
            {'id': 'gtts_english_in', 'name': 'Google English (IN)', 'gender': 'female', 'languages': ['en'],
             'api': 'gtts', 'tld': 'co.in'},
            {'id': 'gtts_german', 'name': 'Google Deutsch', 'gender': 'female', 'languages': ['de'], 'api': 'gtts',
             'tld': 'de'},
            {'id': 'gtts_french_fr', 'name': 'Google Français (FR)', 'gender': 'female', 'languages': ['fr'],
             'api': 'gtts', 'tld': 'fr'},
            {'id': 'gtts_french_ca', 'name': 'Google Français (CA)', 'gender': 'female', 'languages': ['fr'],
             'api': 'gtts', 'tld': 'ca'},
            {'id': 'gtts_spanish_es', 'name': 'Google Español (ES)', 'gender': 'female', 'languages': ['es'],
             'api': 'gtts', 'tld': 'es'},
            {'id': 'gtts_spanish_mx', 'name': 'Google Español (MX)', 'gender': 'female', 'languages': ['es'],
             'api': 'gtts', 'tld': 'com.mx'},
            {'id': 'gtts_portuguese_br', 'name': 'Google Português (BR)', 'gender': 'female', 'languages': ['pt'],
             'api': 'gtts', 'tld': 'com.br'},
            {'id': 'gtts_portuguese_pt', 'name': 'Google Português (PT)', 'gender': 'female', 'languages': ['pt'],
             'api': 'gtts', 'tld': 'pt'},
            {'id': 'gtts_italian', 'name': 'Google Italiano', 'gender': 'female', 'languages': ['it'], 'api': 'gtts',
             'tld': 'it'},
            {'id': 'gtts_japanese', 'name': 'Google 日本語', 'gender': 'female', 'languages': ['ja'], 'api': 'gtts',
             'tld': 'jp'},
            {'id': 'gtts_chinese_mandarin', 'name': 'Google 中文 (普通话)', 'gender': 'female', 'languages': ['zh-CN'],
             'api': 'gtts', 'tld': 'com'},
            {'id': 'gtts_korean', 'name': 'Google 한국어', 'gender': 'female', 'languages': ['ko'], 'api': 'gtts',
             'tld': 'kr'},
            {'id': 'gtts_arabic', 'name': 'Google العربية', 'gender': 'female', 'languages': ['ar'], 'api': 'gtts',
             'tld': 'com'},
            # Edge TTS voices
            {'id': 'en-US-GuyNeural', 'name': 'Edge English US Guy (Neural)', 'gender': 'male', 'languages': ['en-US'],
             'api': 'edge_tts'},
            {'id': 'en-US-AnaNeural', 'name': 'Edge English US Ana (Neural)', 'gender': 'female',
             'languages': ['en-US'], 'api': 'edge_tts'},
            {'id': 'en-GB-RyanNeural', 'name': 'Edge English GB Ryan (Neural)', 'gender': 'male',
             'languages': ['en-GB'], 'api': 'edge_tts'},
            {'id': 'en-GB-SoniaNeural', 'name': 'Edge English GB Sonia (Neural)', 'gender': 'female',
             'languages': ['en-GB'], 'api': 'edge_tts'},
            {'id': 'ru-RU-DmitryNeural', 'name': 'Edge Russian Dmitry (Neural)', 'gender': 'male',
             'languages': ['ru-RU'], 'api': 'edge_tts'},
            {'id': 'ru-RU-SvetlanaNeural', 'name': 'Edge Russian Svetlana (Neural)', 'gender': 'female',
             'languages': ['ru-RU'], 'api': 'edge_tts'},
            {'id': 'de-DE-ConradNeural', 'name': 'Edge German Conrad (Neural)', 'gender': 'male',
             'languages': ['de-DE'], 'api': 'edge_tts'},
            {'id': 'de-DE-KatjaNeural', 'name': 'Edge German Katja (Neural)', 'gender': 'female',
             'languages': ['de-DE'], 'api': 'edge_tts'},
            {'id': 'fr-FR-AlainNeural', 'name': 'Edge French Alain (Neural)', 'gender': 'male', 'languages': ['fr-FR'],
             'api': 'edge_tts'},
            {'id': 'fr-FR-DeniseNeural', 'name': 'Edge French Denise (Neural)', 'gender': 'female',
             'languages': ['fr-FR'], 'api': 'edge_tts'},
            {'id': 'es-ES-AlvaroNeural', 'name': 'Edge Spanish Alvaro (Neural)', 'gender': 'male',
             'languages': ['es-ES'], 'api': 'edge_tts'},
            {'id': 'es-ES-ElviraNeural', 'name': 'Edge Spanish Elvira (Neural)', 'gender': 'female',
             'languages': ['es-ES'], 'api': 'edge_tts'},
            {'id': 'pt-BR-AntonioNeural', 'name': 'Edge Portuguese BR Antonio (Neural)', 'gender': 'male',
             'languages': ['pt-BR'], 'api': 'edge_tts'},
            {'id': 'pt-BR-FranciscaNeural', 'name': 'Edge Portuguese BR Francisca (Neural)', 'gender': 'female',
             'languages': ['pt-BR'], 'api': 'edge_tts'},
            {'id': 'it-IT-DiegoNeural', 'name': 'Edge Italian Diego (Neural)', 'gender': 'male', 'languages': ['it-IT'],
             'api': 'edge_tts'},
            {'id': 'it-IT-ElsaNeural', 'name': 'Edge Italian Elsa (Neural)', 'gender': 'female', 'languages': ['it-IT'],
             'api': 'edge_tts'},
            {'id': 'ja-JP-KeitaNeural', 'name': 'Edge Japanese Keita (Neural)', 'gender': 'male',
             'languages': ['ja-JP'], 'api': 'edge_tts'},
            {'id': 'ja-JP-NanamiNeural', 'name': 'Edge Japanese Nanami (Neural)', 'gender': 'female',
             'languages': ['ja-JP'], 'api': 'edge_tts'},
            {'id': 'zh-CN-YunxiNeural', 'name': 'Edge Chinese Yunxi (Neural)', 'gender': 'male', 'languages': ['zh-CN'],
             'api': 'edge_tts'},
            {'id': 'zh-CN-XiaoxiaoNeural', 'name': 'Edge Chinese Xiaoxiao (Neural)', 'gender': 'female',
             'languages': ['zh-CN'], 'api': 'edge_tts'},
            {'id': 'ko-KR-SunHiNeural', 'name': 'Edge Korean Sun-Hi (Neural)', 'gender': 'female',
             'languages': ['ko-KR'], 'api': 'edge_tts'},
            {'id': 'ko-KR-InJoonNeural', 'name': 'Edge Korean InJoon (Neural)', 'gender': 'male',
             'languages': ['ko-KR'], 'api': 'edge_tts'},
            {'id': 'ar-SA-HamedNeural', 'name': 'Edge Arabic Hamed (Neural)', 'gender': 'male', 'languages': ['ar-SA'],
             'api': 'edge_tts'},
            {'id': 'ar-SA-ZariyahNeural', 'name': 'Edge Arabic Zariyah (Neural)', 'gender': 'female',
             'languages': ['ar-SA'], 'api': 'edge_tts'},
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
        """Loads settings from a file or sets defaults."""
        self.default_settings = {
            'last_voice_index': 0,
            'last_speed': 150,
            'output_folder': str(Path.home() / "Documents" / "MarilynTone"),
            'auto_save': False,
            'effects': {
                'pitch_shift': {'enabled': False, 'semitones': 0},
                'volume_adjust': {'enabled': False, 'db': 0},
                'reverb': {'enabled': False, 'room_scale': 50}
            }
        }
        try:
            if Path(self.settings_file).exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = {**self.default_settings, **json.load(f)}
            else:
                self.settings = self.default_settings
            Path(self.settings['output_folder']).mkdir(parents=True, exist_ok=True)
        except:
            self.settings = self.default_settings

    def save_settings(self):
        """Saves settings to a file."""
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
        """Stops the current playback."""
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
        """Helper method for asynchronous edge_tts synthesis."""
        communicate = edge_tts.Communicate(text, voice_id, rate=rate_str)
        if save_path:
            await communicate.save(save_path)
        else:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
                temp_mp3_path = temp_mp3.name
            await communicate.save(temp_mp3_path)
            return temp_mp3_path

    def apply_effects(self, audio: np.ndarray, sr: int) -> tuple[np.ndarray, int]:
        """Applies enabled audio effects to the audio array."""
        effects = self.settings.get('effects', {})
        original_dtype = audio.dtype

        # Normalize audio to prevent clipping
        audio = audio.astype(np.float32)
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0:
            audio = audio / max_amplitude

        # Pitch Shift
        if effects.get('pitch_shift', {}).get('enabled', False):
            semitones = float(effects['pitch_shift'].get('semitones', 0))
            if semitones != 0:
                try:
                    audio = librosa.effects.pitch_shift(audio, sr=sr, n_steps=semitones)
                except Exception as e:
                    print(f"Pitch shift error: {e}")

        # Volume Adjustment
        if effects.get('volume_adjust', {}).get('enabled', False):
            db = float(effects['volume_adjust'].get('db', 0))
            if db != 0:
                try:
                    gain = 10 ** (db / 20.0)
                    audio = audio * gain
                except Exception as e:
                    print(f"Volume adjustment error: {e}")

        # Reverb
        if effects.get('reverb', {}).get('enabled', False):
            room_scale = float(effects['reverb'].get('room_scale', 50))
            try:
                # Create a more natural impulse response for reverb
                reverb_length = int(0.5 * sr)  # Increased reverb length for better effect
                decay = np.exp(-6.0 * np.arange(reverb_length) / (room_scale * sr / 100.0))
                impulse_response = decay * np.random.randn(reverb_length)
                impulse_response[0] = 1.0  # Direct sound
                impulse_response *= (room_scale / 100.0)
                audio = np.convolve(audio, impulse_response, mode='full')[:len(audio)]
            except Exception as e:
                print(f"Reverb error: {e}")

        # Normalize again to prevent clipping
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0:
            audio = audio / max_amplitude

        # Convert back to original dtype
        audio = np.clip(audio, -1.0, 1.0)
        if original_dtype == np.int16:
            audio = (audio * 32767).astype(np.int16)
        else:
            audio = audio.astype(np.float32)

        return audio, sr

    def text_to_speech(self, text: str, voice_idx: int, speed: int = 150,
                       save_path: Optional[str] = None, callback: Optional[Callable] = None):
        """Synthesizes text to speech with support for pyttsx3, gTTS, and edge_tts, applying effects."""
        try:
            if voice_idx >= len(self.voices):
                raise Exception("Invalid voice index")
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
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                audio, sr = librosa.load(audio_buffer, sr=44100)
                audio, sr = self.apply_effects(audio, sr)

                if save_path:
                    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                    sf.write(save_path, audio, sr, format='MP3')
                    if callback:
                        callback(True, "Audio successfully saved")
                else:
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
                        temp_mp3_path = temp_mp3.name
                        sf.write(temp_mp3_path, audio, sr, format='MP3')

                    def play_audio():
                        try:
                            pygame.mixer.music.load(temp_mp3_path)
                            pygame.mixer.music.play()
                            while pygame.mixer.music.get_busy() and not self.stop_requested:
                                pygame.time.wait(100)
                            if callback and not self.stop_requested:
                                callback(True, "Playback completed")
                        except Exception as e:
                            if callback:
                                callback(False, f"Playback error: {str(e)}")
                        finally:
                            try:
                                Path(temp_mp3_path).unlink()
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
                            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                            loop.run_until_complete(self._edge_tts_synthesize(text, voice['id'], rate_str, save_path))
                            audio, sr = librosa.load(save_path, sr=44100)
                            audio, sr = self.apply_effects(audio, sr)
                            sf.write(save_path, audio, sr, format='MP3')
                            if callback:
                                callback(True, "Audio successfully saved")
                        else:
                            temp_mp3_path = loop.run_until_complete(
                                self._edge_tts_synthesize(text, voice['id'], rate_str))
                            audio, sr = librosa.load(temp_mp3_path, sr=44100)
                            audio, sr = self.apply_effects(audio, sr)
                            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
                                temp_mp3_path = temp_mp3.name
                                sf.write(temp_mp3_path, audio, sr, format='MP3')
                            try:
                                pygame.mixer.music.load(temp_mp3_path)
                                pygame.mixer.music.play()
                                while pygame.mixer.music.get_busy() and not self.stop_requested:
                                    pygame.time.wait(100)
                                if callback and not self.stop_requested:
                                    callback(True, "Playback completed")
                            except Exception as e:
                                if callback:
                                    callback(False, f"Playback error: {str(e)}")
                            finally:
                                try:
                                    Path(temp_mp3_path).unlink()
                                except:
                                    pass
                        loop.close()
                    except Exception as e:
                        if callback:
                            callback(False, f"Error: {str(e)}")

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
                    if not save_path.endswith('.wav'):
                        raise Exception("pyttsx3 supports saving only to WAV")
                    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                    self.engine.save_to_file(text, save_path)
                    self.engine.runAndWait()
                    audio, sr = librosa.load(save_path, sr=44100)
                    audio, sr = self.apply_effects(audio, sr)
                    sf.write(save_path, audio, sr, format='WAV')
                    if callback:
                        callback(True, "Audio successfully saved")
                else:
                    def play_audio():
                        try:
                            self.engine.say(text)
                            self.engine.runAndWait()
                            if callback and not self.stop_requested:
                                callback(True, "Playback completed")
                        except Exception as e:
                            if callback:
                                callback(False, f"Playback error: {str(e)}")

                    thread = threading.Thread(target=play_audio)
                    thread.daemon = True
                    thread.start()

        except Exception as e:
            if callback:
                callback(False, f"Error: {str(e)}")
            else:
                raise Exception(f"Error: {str(e)}")

    def preview_voice(self, voice_idx: int, callback: Optional[Callable] = None):
        """Plays a sample of the selected voice."""
        sample_texts = {
            'ru': 'Привет, это пример голоса. Данный голос предназначен для русского языка.',
            'en': 'Hello, this is a voice sample. This voice is designed for English language.',
            'de': 'Hallo, dies ist eine Sprachprobe. Diese Stimme ist für die deutsche Sprache ausgelegt.',
            'fr': 'Bonjour, ceci est un échantillon vocal. Cette voix est conçue pour la langue française.',
            'es': 'Hola, esta es una muestra de voz. Esta voz está diseñada para el idioma español.',
            'it': 'Ciao, questo è un campione vocale. Questa voce è progettata per la lingua italiana.',
            'pt': 'Olá, esta é uma amostra de voz. Esta voz é projetada para a língua portuguesa.',
            'ja': 'こんにちは、これは音声サンプルです。この音声は日本語用に設計されています。',
            'zh': '你好，这是一个语音样本。此语音专为中文设计。',
            'ko': '안녕하세요, 이것은 음성 샘플입니다. 이 음성은 한국어로 설계되었습니다。',
            'ar': 'مرحبًا، هذه عينة صوتية. تم تصميم هذا الصوت للغة العربية.'
        }
        voice = self.voices[voice_idx]
        lang = voice['languages'][0][:2] if voice['languages'] else 'en'
        text = sample_texts.get(lang, sample_texts['en'])
        self.text_to_speech(text, voice_idx, 150, None, callback)

    def get_default_output_path(self, format: str = "mp3") -> str:
        """Returns the default save path."""
        if format not in ["mp3", "wav"]:
            format = "mp3" if self.current_api in ['gtts', 'edge_tts'] else "wav"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"marilyntone_{timestamp}.{format}"
        return str(Path(self.settings['output_folder']) / filename)

    def get_voice_info(self, voice_idx: int) -> dict:
        """Returns information about the voice by index."""
        if 0 <= voice_idx < len(self.voices):
            return self.voices[voice_idx]
        return {}