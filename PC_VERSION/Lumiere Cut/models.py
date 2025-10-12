# models.py
from datetime import timedelta
import os


class Project:
    def __init__(self, name, resolution, fps):
        self.name = name
        self.resolution = resolution
        self.fps = fps
        self.file_path = None
        self.created = None
        self.modified = None


class VideoClip:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.start_frame = 0
        self.end_frame = 0
        self.position = 0  # Position on timeline in seconds
        self.total_frames = 0
        self.fps = 0
        self.duration = 0
        self.effects = []
        self.transitions = []

    @property
    def duration(self):
        if self.fps > 0:
            return (self.end_frame - self.start_frame) / self.fps
        return 0

    @duration.setter
    def duration(self, value):
        pass


class AudioClip:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.start_time = 0
        self.end_time = 0
        self.position = 0
        self.duration = 0
        self.volume = 1.0
        self.fade_in = 0
        self.fade_out = 0

    @property
    def duration(self):
        return self.end_time - self.start_time

    @duration.setter
    def duration(self, value):
        pass


class Track:
    def __init__(self, index, type="video"):
        self.index = index
        self.type = type
        self.clips = []
        self.muted = False
        self.locked = False
        self.volume = 1.0


class Effect:
    def __init__(self, name, type, parameters):
        self.name = name
        self.type = type  # "video", "audio", "transition"
        self.parameters = parameters


class Transition:
    def __init__(self, type, duration, parameters=None):
        self.type = type  # "fade", "slide", "wipe", etc.
        self.duration = duration
        self.parameters = parameters or {}