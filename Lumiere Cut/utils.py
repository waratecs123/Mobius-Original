# utils.py
import cv2
import numpy as np
from datetime import timedelta
import threading
import time

def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

class VideoPlayer:
    def __init__(self, update_callback):
        self.is_playing = False
        self.update_callback = update_callback
        self.play_thread = None

    def play(self, current_frame, total_frames, fps):
        if not self.is_playing:
            self.is_playing = True
            self.play_thread = threading.Thread(
                target=self._play_thread,
                args=(current_frame, total_frames, fps)
            )
            self.play_thread.daemon = True
            self.play_thread.start()

    def _play_thread(self, current_frame, total_frames, fps):
        frame_num = current_frame
        while self.is_playing and frame_num < total_frames - 1:
            frame_num += 1
            if self.update_callback:
                self.update_callback(frame_num)
            time.sleep(1 / fps)

    def pause(self):
        self.is_playing = False

    def stop(self):
        self.is_playing = False

class PreviewPlayer:
    def __init__(self, update_callback, functions):
        self.is_playing = False
        self.update_callback = update_callback
        self.functions = functions
        self.play_thread = None

    def play(self, current_frame, total_frames, fps):
        if not self.is_playing:
            self.is_playing = True
            self.play_thread = threading.Thread(
                target=self._play_thread,
                args=(current_frame, total_frames, fps)
            )
            self.play_thread.daemon = True
            self.play_thread.start()

    def _play_thread(self, current_frame, total_frames, fps):
        frame_num = current_frame
        while self.is_playing and frame_num < total_frames - 1:
            frame_num += 1
            if self.update_callback:
                self.update_callback(frame_num)
            time.sleep(1 / fps)

    def pause(self):
        self.is_playing = False

    def stop(self):
        self.is_playing = False