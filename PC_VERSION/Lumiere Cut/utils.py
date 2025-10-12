# utils.py
import cv2
import numpy as np
from datetime import timedelta
import threading
import time
import pygame
import tempfile
import os


def format_time(seconds):
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def time_to_seconds(time_str):
    try:
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)
    except:
        return 0


def create_thumbnail(video_path, frame_num=0):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None


def apply_effect(frame, effect_type, effect_value):
    if effect_type == 'brightness':
        return cv2.convertScaleAbs(frame, alpha=1, beta=effect_value)
    elif effect_type == 'contrast':
        return cv2.convertScaleAbs(frame, alpha=effect_value, beta=0)
    elif effect_type == 'saturation':
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], effect_value)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    elif effect_type == 'blur':
        return cv2.GaussianBlur(frame, (effect_value, effect_value), 0)
    return frame


class VideoPlayer:
    def __init__(self, update_callback):
        self.is_playing = False
        self.update_callback = update_callback
        self.play_thread = None
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.playback_speed = 1.0

    def play(self, current_frame, total_frames, fps, speed=1.0):
        if not self.is_playing:
            self.is_playing = True
            self.current_frame = current_frame
            self.total_frames = total_frames
            self.fps = fps
            self.playback_speed = speed
            self.play_thread = threading.Thread(target=self._play_thread)
            self.play_thread.daemon = True
            self.play_thread.start()

    def _play_thread(self):
        while self.is_playing and self.current_frame < self.total_frames - 1:
            self.current_frame += self.playback_speed
            if self.current_frame >= self.total_frames:
                self.current_frame = self.total_frames - 1
                self.is_playing = False

            if self.update_callback:
                self.update_callback(int(self.current_frame))

            time.sleep(1 / (self.fps * self.playback_speed))

    def pause(self):
        self.is_playing = False

    def stop(self):
        self.is_playing = False
        self.current_frame = 0

    def seek(self, frame_num):
        self.current_frame = frame_num
        if self.update_callback:
            self.update_callback(int(frame_num))


class PreviewPlayer:
    def __init__(self, update_callback, functions):
        self.is_playing = False
        self.update_callback = update_callback
        self.functions = functions
        self.play_thread = None
        self.current_frame = 0
        self.max_duration = 0
        self.fps = 30
        self.playback_speed = 1.0

    def play(self, current_frame, max_duration, fps, speed=1.0):
        if not self.is_playing:
            self.is_playing = True
            self.current_frame = current_frame
            self.max_duration = max_duration
            self.fps = fps
            self.playback_speed = speed
            self.play_thread = threading.Thread(target=self._play_thread)
            self.play_thread.daemon = True
            self.play_thread.start()

    def _play_thread(self):
        while self.is_playing and self.current_frame < self.max_duration - 1:
            self.current_frame += self.playback_speed
            if self.current_frame >= self.max_duration:
                self.current_frame = self.max_duration - 1
                self.is_playing = False

            if self.update_callback:
                self.update_callback(int(self.current_frame))

            time.sleep(1 / (self.fps * self.playback_speed))

    def pause(self):
        self.is_playing = False

    def stop(self):
        self.is_playing = False
        self.current_frame = 0

    def seek(self, frame_num):
        self.current_frame = frame_num
        if self.update_callback:
            self.update_callback(int(frame_num))


class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_sound = None
        self.is_playing = False

    def play_audio(self, file_path, volume=1.0):
        try:
            if self.is_playing:
                self.stop_audio()

            self.current_sound = pygame.mixer.Sound(file_path)
            self.current_sound.set_volume(volume)
            self.current_sound.play()
            self.is_playing = True
            return True
        except:
            return False

    def stop_audio(self):
        if self.is_playing and self.current_sound:
            self.current_sound.stop()
            self.is_playing = False

    def set_volume(self, volume):
        if self.current_sound:
            self.current_sound.set_volume(volume)


class ExportManager:
    def __init__(self, functions):
        self.functions = functions
        self.is_exporting = False
        self.export_thread = None

    def start_export(self, file_path, progress_callback=None):
        if not self.is_exporting:
            self.is_exporting = True
            self.export_thread = threading.Thread(
                target=self._export_thread,
                args=(file_path, progress_callback)
            )
            self.export_thread.daemon = True
            self.export_thread.start()

    def _export_thread(self, file_path, progress_callback):
        success, message = self.functions.export_video(file_path, progress_callback)
        self.is_exporting = False
        return success, message

    def cancel_export(self):
        self.is_exporting = False


class AutoSaveManager:
    def __init__(self, functions, interval=300):  # 5 минут по умолчанию
        self.functions = functions
        self.interval = interval
        self.timer = None
        self.is_running = False

    def start(self):
        self.is_running = True
        self._schedule_next()

    def stop(self):
        self.is_running = False
        if self.timer:
            self.timer.cancel()

    def _schedule_next(self):
        if self.is_running:
            self.timer = threading.Timer(self.interval, self._auto_save)
            self.timer.daemon = True
            self.timer.start()

    def _auto_save(self):
        if self.is_running:
            # Создаем временный файл для автосохранения
            temp_dir = tempfile.gettempdir()
            auto_save_path = os.path.join(temp_dir, f"autosave_{self.functions.project.name}.json")
            self.functions.save_project(auto_save_path)
            self._schedule_next()