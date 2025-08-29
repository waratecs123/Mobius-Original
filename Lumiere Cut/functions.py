# functions.py
import cv2
import numpy as np
from models import VideoClip
import threading
from tkinter import messagebox
import os


class VideoEditorFunctions:
    def __init__(self):
        self.video_clips = []
        self.timeline_clips = []
        self.current_clip = None
        self.cap = None
        self.total_frames = 0
        self.fps = 30
        self.current_frame = 0
        self.video_width = 640
        self.video_height = 480
        self.tracks = [[] for _ in range(3)]
        self.current_track = 0
        self.dragging_clip = None
        self.dragging_start_pos = None
        self.dragging_clip_info = None  # Для перемещения клипов

    def open_video(self, file_path):
        try:
            clip = VideoClip(file_path)
            self.video_clips.append(clip)

            if len(self.video_clips) == 1:
                self.set_current_clip(clip)

            return True, os.path.basename(file_path), clip.thumbnail
        except Exception as e:
            return False, f"Ошибка при открытии видео: {str(e)}", None

    def set_current_clip(self, clip):
        self.current_clip = clip
        self.cap = cv2.VideoCapture(clip.path)
        self.total_frames = clip.total_frames
        self.fps = clip.fps
        self.current_frame = 0

    def add_to_timeline(self, track_index=None):
        if not self.current_clip:
            return False, "Сначала выберите видео в библиотеке"

        if track_index is None:
            track_index = self.current_track

        timeline_clip = VideoClip(
            self.current_clip.path,
            track=track_index
        )

        if track_index >= len(self.tracks):
            self.tracks.append([])

        self.tracks[track_index].append(timeline_clip)
        return True, "Клип добавлен на временную шкалу"

    def add_track(self):
        self.tracks.append([])
        return len(self.tracks) - 1

    def remove_track(self, track_index):
        if 0 <= track_index < len(self.tracks):
            if not self.tracks[track_index]:
                del self.tracks[track_index]
                return True, "Дорожка удалена"
            else:
                return False, "Дорожка не пуста, удалите сначала все клипы"
        return False, "Неверный индекс дорожки"

    def remove_clip(self, track_index, clip_index):
        if 0 <= track_index < len(self.tracks):
            if 0 <= clip_index < len(self.tracks[track_index]):
                del self.tracks[track_index][clip_index]
                return True, "Клип удален"
        return False, "Неверные индексы дорожки или клипа"

    def move_clip(self, from_track, from_index, to_track, to_position):
        if (0 <= from_track < len(self.tracks) and
                0 <= from_index < len(self.tracks[from_track]) and
                0 <= to_track < len(self.tracks)):

            clip = self.tracks[from_track].pop(from_index)
            clip.track = to_track

            if to_position >= len(self.tracks[to_track]):
                self.tracks[to_track].append(clip)
            else:
                self.tracks[to_track].insert(to_position, clip)

            return True, "Клип перемещен"
        return False, "Ошибка перемещения клипа"

    def update_clip_position(self, track_index, clip_index, new_position):
        if (0 <= track_index < len(self.tracks) and
                0 <= clip_index < len(self.tracks[track_index])):
            self.tracks[track_index][clip_index].position = new_position
            return True
        return False

    def get_frame(self, frame_num=None):
        if frame_num is None:
            frame_num = self.current_frame

        if self.current_clip:
            frame = self.current_clip.get_frame(frame_num)
            return frame
        return None

    def get_preview_frame(self, frame_num):
        """Получает кадр из смонтированного видео"""
        if not self.tracks or all(len(track) == 0 for track in self.tracks):
            return None

        # Создаем черный кадр
        frame = np.zeros((self.video_height, self.video_width, 3), dtype=np.uint8)

        # Накладываем клипы
        for track in reversed(self.tracks):
            for clip in track:
                clip_duration = clip.end_frame - clip.start_frame
                if clip.position <= frame_num < clip.position + clip_duration:
                    clip_frame_num = frame_num - clip.position + clip.start_frame
                    clip_frame = clip.get_frame(clip_frame_num)
                    if clip_frame is not None:
                        clip_frame = cv2.resize(clip_frame, (self.video_width, self.video_height))
                        # Наложение с альфа-каналом
                        frame = np.where(clip_frame > 0, clip_frame, frame)

        return frame

    def export_video(self, file_path, progress_callback=None):
        if not self.tracks or all(len(track) == 0 for track in self.tracks):
            return False, "Нет клипов на временной шкале для экспорта"

        try:
            # Находим максимальную длину проекта
            max_duration = 0
            for track in self.tracks:
                for clip in track:
                    clip_end = clip.position + (clip.end_frame - clip.start_frame)
                    if clip_end > max_duration:
                        max_duration = clip_end

            # Создаем видеописатель
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(file_path, fourcc, self.fps,
                                  (self.video_width, self.video_height))

            # Рендерим каждый кадр
            for frame_num in range(0, max_duration):
                frame = self.get_preview_frame(frame_num)
                out.write(frame)

                if progress_callback and frame_num % 10 == 0:
                    progress = (frame_num / max_duration) * 100
                    progress_callback(progress)

            out.release()
            return True, "Видео успешно экспортировано"

        except Exception as e:
            return False, f"Ошибка при экспорте: {str(e)}"