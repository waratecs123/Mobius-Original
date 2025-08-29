# models.py
import cv2
import numpy as np


class VideoClip:
    def __init__(self, path, start_frame=0, end_frame=None, track=0, position=0):
        self.path = path
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.track = track
        self.position = position

        # Получаем информацию о видео
        cap = cv2.VideoCapture(path)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        if self.end_frame is None or self.end_frame > self.total_frames:
            self.end_frame = self.total_frames

        # Генерируем превью
        self.thumbnail = self._generate_thumbnail()

    def _generate_thumbnail(self):
        cap = cv2.VideoCapture(self.path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        ret, frame = cap.read()
        cap.release()

        if ret:
            return frame
        return None

    def get_frame(self, frame_num):
        if frame_num < self.start_frame or frame_num >= self.end_frame:
            return None

        cap = cv2.VideoCapture(self.path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        cap.release()

        if ret:
            return frame
        return None