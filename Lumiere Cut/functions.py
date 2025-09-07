# functions.py
import cv2
import os
import json
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageTk
import pygame
from models import VideoClip, AudioClip, Project, Track


class VideoEditorFunctions:
    def __init__(self):
        self.project = Project("Untitled Project", (1920, 1080), 30.0)
        self.current_clip = None
        self.current_frame = 0
        self.copied_clip = None
        self.undo_stack = []
        self.redo_stack = []
        self.video_clips = []
        self.audio_clips = []
        self.tracks = [[] for _ in range(5)]  # 5 video tracks
        self.audio_tracks = [[] for _ in range(3)]  # 3 audio tracks

    def new_project(self, name, resolution, fps):
        try:
            self.project = Project(name, resolution, fps)
            self.current_clip = None
            self.current_frame = 0
            self.video_clips = []
            self.audio_clips = []
            self.tracks = [[] for _ in range(5)]
            self.audio_tracks = [[] for _ in range(3)]
            self.undo_stack = []
            self.redo_stack = []
            return True, f"Project '{name}' created successfully"
        except Exception as e:
            return False, f"Error creating project: {str(e)}"

    def load_project(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            self.project = Project(data['name'], tuple(data['resolution']), data['fps'])
            self.project.file_path = file_path

            # Load video clips
            self.video_clips = []
            for clip_data in data.get('video_clips', []):
                clip = VideoClip(clip_data['path'])
                clip.start_frame = clip_data['start_frame']
                clip.end_frame = clip_data['end_frame']
                clip.position = clip_data['position']
                self.video_clips.append(clip)

            # Load audio clips
            self.audio_clips = []
            for clip_data in data.get('audio_clips', []):
                clip = AudioClip(clip_data['path'])
                clip.start_time = clip_data['start_time']
                clip.end_time = clip_data['end_time']
                clip.position = clip_data['position']
                self.audio_clips.append(clip)

            # Load tracks
            self.tracks = [[] for _ in range(5)]
            for track_idx, track_data in enumerate(data.get('tracks', [])):
                for clip_data in track_data:
                    clip = next((c for c in self.video_clips if c.path == clip_data['path']), None)
                    if clip:
                        self.tracks[track_idx].append(clip)

            return True, f"Project loaded from {file_path}"
        except Exception as e:
            return False, f"Error loading project: {str(e)}"

    def save_project(self, file_path=None):
        try:
            if file_path:
                self.project.file_path = file_path

            if not self.project.file_path:
                return False, "No file path specified"

            data = {
                'name': self.project.name,
                'resolution': self.project.resolution,
                'fps': self.project.fps,
                'video_clips': [{
                    'path': clip.path,
                    'start_frame': clip.start_frame,
                    'end_frame': clip.end_frame,
                    'position': clip.position
                } for clip in self.video_clips],
                'audio_clips': [{
                    'path': clip.path,
                    'start_time': clip.start_time,
                    'end_time': clip.end_time,
                    'position': clip.position
                } for clip in self.audio_clips],
                'tracks': [
                    [{'path': clip.path, 'position': clip.position} for clip in track]
                    for track in self.tracks
                ]
            }

            with open(self.project.file_path, 'w') as f:
                json.dump(data, f, indent=2)

            return True, f"Project saved to {self.project.file_path}"
        except Exception as e:
            return False, f"Error saving project: {str(e)}"

    def auto_save(self):
        if self.project.file_path:
            auto_save_path = self.project.file_path.replace('.lumiere', '_autosave.lumiere')
            self.save_project(auto_save_path)

    def open_video(self, file_path):
        try:
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return False, "Cannot open video file", None

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0

            # Generate thumbnail
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.thumbnail((200, 200))
                thumbnail = ImageTk.PhotoImage(img)
            else:
                thumbnail = None

            cap.release()

            clip = VideoClip(file_path)
            clip.total_frames = total_frames
            clip.fps = fps
            clip.duration = duration
            clip.end_frame = total_frames

            self.video_clips.append(clip)
            self.current_clip = clip
            self.current_frame = 0

            return True, os.path.basename(file_path), thumbnail
        except Exception as e:
            return False, f"Error opening video: {str(e)}", None

    def add_audio_clip(self, file_path):
        try:
            # Initialize pygame mixer if not already initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            sound = pygame.mixer.Sound(file_path)
            duration = sound.get_length()

            clip = AudioClip(file_path)
            clip.duration = duration
            clip.end_time = duration

            self.audio_clips.append(clip)
            return True, os.path.basename(file_path)
        except Exception as e:
            return False, f"Error adding audio: {str(e)}"

    def add_to_timeline(self, track_idx=0, position=0):
        if not self.current_clip:
            return False, "No clip selected"

        try:
            # Create a copy of the clip for the timeline
            timeline_clip = VideoClip(self.current_clip.path)
            timeline_clip.start_frame = 0
            timeline_clip.end_frame = self.current_clip.total_frames
            timeline_clip.position = position
            timeline_clip.total_frames = self.current_clip.total_frames
            timeline_clip.fps = self.current_clip.fps
            timeline_clip.duration = self.current_clip.duration

            if track_idx < len(self.tracks):
                self.tracks[track_idx].append(timeline_clip)
                self.push_undo_state()
                return True, "Clip added to timeline"
            else:
                return False, "Invalid track index"
        except Exception as e:
            return False, f"Error adding to timeline: {str(e)}"

    def get_frame(self, frame_num=None):
        if not self.current_clip:
            return None

        if frame_num is None:
            frame_num = self.current_frame

        try:
            cap = cv2.VideoCapture(self.current_clip.path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            cap.release()

            if ret:
                return frame
            else:
                return None
        except Exception as e:
            print(f"Error getting frame: {str(e)}")
            return None

    def split_clip(self, track_idx, clip_idx, split_frame):
        try:
            if track_idx >= len(self.tracks) or clip_idx >= len(self.tracks[track_idx]):
                return False, "Invalid clip selection"

            clip = self.tracks[track_idx][clip_idx]

            if split_frame <= clip.start_frame or split_frame >= clip.end_frame:
                return False, "Invalid split point"

            # Create new clip for the second part
            new_clip = VideoClip(clip.path)
            new_clip.start_frame = split_frame
            new_clip.end_frame = clip.end_frame
            new_clip.position = clip.position + (split_frame - clip.start_frame)
            new_clip.total_frames = clip.total_frames
            new_clip.fps = clip.fps

            # Update original clip
            clip.end_frame = split_frame

            # Insert new clip after the original
            self.tracks[track_idx].insert(clip_idx + 1, new_clip)
            self.push_undo_state()

            return True, "Clip split successfully"
        except Exception as e:
            return False, f"Error splitting clip: {str(e)}"

    def trim_clip(self, track_idx, clip_idx, start_frame, end_frame):
        try:
            if track_idx >= len(self.tracks) or clip_idx >= len(self.tracks[track_idx]):
                return False, "Invalid clip selection"

            clip = self.tracks[track_idx][clip_idx]

            if start_frame < 0 or end_frame > clip.total_frames or start_frame >= end_frame:
                return False, "Invalid trim range"

            clip.start_frame = start_frame
            clip.end_frame = end_frame
            self.push_undo_state()

            return True, "Clip trimmed successfully"
        except Exception as e:
            return False, f"Error trimming clip: {str(e)}"

    def remove_clip(self, track_idx, clip_idx):
        try:
            if track_idx >= len(self.tracks) or clip_idx >= len(self.tracks[track_idx]):
                return False, "Invalid clip selection"

            removed_clip = self.tracks[track_idx].pop(clip_idx)
            self.push_undo_state()

            return True, "Clip removed successfully"
        except Exception as e:
            return False, f"Error removing clip: {str(e)}"

    def copy_clip(self, track_idx, clip_idx):
        try:
            if track_idx >= len(self.tracks) or clip_idx >= len(self.tracks[track_idx]):
                return False

            self.copied_clip = self.tracks[track_idx][clip_idx]
            return True
        except Exception as e:
            print(f"Error copying clip: {str(e)}")
            return False

    def paste_clip(self, track_idx, position):
        if not self.copied_clip:
            return False, "No clip to paste"

        try:
            new_clip = VideoClip(self.copied_clip.path)
            new_clip.start_frame = self.copied_clip.start_frame
            new_clip.end_frame = self.copied_clip.end_frame
            new_clip.position = position
            new_clip.total_frames = self.copied_clip.total_frames
            new_clip.fps = self.copied_clip.fps

            if track_idx < len(self.tracks):
                self.tracks[track_idx].append(new_clip)
                self.push_undo_state()
                return True, "Clip pasted successfully"
            else:
                return False, "Invalid track index"
        except Exception as e:
            return False, f"Error pasting clip: {str(e)}"

    def apply_effect(self, track_idx, clip_idx, effect_name):
        try:
            if track_idx >= len(self.tracks) or clip_idx >= len(self.tracks[track_idx]):
                return False, "Invalid clip selection"

            clip = self.tracks[track_idx][clip_idx]

            # Apply effect (this would be more complex in a real implementation)
            if effect_name == "Brightness":
                clip.effects.append({"type": "brightness", "value": 1.2})
            elif effect_name == "Contrast":
                clip.effects.append({"type": "contrast", "value": 1.2})
            elif effect_name == "Blur":
                clip.effects.append({"type": "blur", "value": 5})

            self.push_undo_state()
            return True, f"{effect_name} effect applied"
        except Exception as e:
            return False, f"Error applying effect: {str(e)}"

    def add_transition(self, track_idx, clip_idx, transition_type):
        try:
            if track_idx >= len(self.tracks) or clip_idx >= len(self.tracks[track_idx]) or clip_idx == 0:
                return False, "Cannot add transition here"

            # This would create a transition between clip_idx-1 and clip_idx
            prev_clip = self.tracks[track_idx][clip_idx - 1]
            current_clip = self.tracks[track_idx][clip_idx]

            # Add transition effect (simplified)
            transition = {
                "type": transition_type,
                "duration": 30,  # 1 second at 30fps
                "position": prev_clip.position + (prev_clip.end_frame - prev_clip.start_frame)
            }

            if not hasattr(prev_clip, 'transitions'):
                prev_clip.transitions = []
            prev_clip.transitions.append(transition)

            self.push_undo_state()
            return True, f"{transition_type} transition added"
        except Exception as e:
            return False, f"Error adding transition: {str(e)}"

    def export_video(self, output_path, format_type, quality):
        try:
            # This is a simplified export function
            # In a real implementation, you would use OpenCV or FFmpeg to render the timeline

            if not self.tracks or not any(self.tracks):
                return False, "No clips in timeline to export"

            # Get the total duration
            max_duration = 0
            for track in self.tracks:
                for clip in track:
                    clip_end = clip.position + (clip.end_frame - clip.start_frame) / clip.fps
                    max_duration = max(max_duration, clip_end)

            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, self.project.fps, self.project.resolution)

            # Render each frame (simplified - would need to handle multiple tracks, effects, etc.)
            for frame_num in range(int(max_duration * self.project.fps)):
                frame = np.zeros((self.project.resolution[1], self.project.resolution[0], 3), dtype=np.uint8)

                # Render tracks from bottom to top
                for track in reversed(self.tracks):
                    for clip in track:
                        clip_start_frame = clip.position * clip.fps
                        clip_end_frame = clip_start_frame + (clip.end_frame - clip.start_frame)

                        if clip_start_frame <= frame_num < clip_end_frame:
                            clip_frame_num = clip.start_frame + (frame_num - clip_start_frame)
                            clip_frame = self.get_frame_from_clip(clip, clip_frame_num)
                            if clip_frame is not None:
                                # Simple overlay (would need proper compositing)
                                frame = clip_frame

                out.write(frame)

            out.release()
            return True, f"Video exported to {output_path}"
        except Exception as e:
            return False, f"Error exporting video: {str(e)}"

    def get_frame_from_clip(self, clip, frame_num):
        try:
            cap = cv2.VideoCapture(clip.path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            cap.release()

            if ret:
                # Apply effects (simplified)
                for effect in getattr(clip, 'effects', []):
                    if effect['type'] == 'brightness':
                        frame = cv2.convertScaleAbs(frame, alpha=effect['value'], beta=0)
                    elif effect['type'] == 'contrast':
                        frame = cv2.convertScaleAbs(frame, alpha=effect['value'], beta=0)

                # Resize to project resolution
                frame = cv2.resize(frame, self.project.resolution)
                return frame
            return None
        except Exception as e:
            print(f"Error getting frame from clip: {str(e)}")
            return None

    def push_undo_state(self):
        # Save current state to undo stack
        state = {
            'tracks': [[{
                'path': clip.path,
                'start_frame': clip.start_frame,
                'end_frame': clip.end_frame,
                'position': clip.position
            } for clip in track] for track in self.tracks],
            'current_frame': self.current_frame,
            'current_clip_path': self.current_clip.path if self.current_clip else None
        }
        self.undo_stack.append(state)
        self.redo_stack = []  # Clear redo stack when new action is performed

    def undo(self):
        if not self.undo_stack:
            return False, "Nothing to undo"

        # Save current state to redo stack
        current_state = {
            'tracks': [[{
                'path': clip.path,
                'start_frame': clip.start_frame,
                'end_frame': clip.end_frame,
                'position': clip.position
            } for clip in track] for track in self.tracks],
            'current_frame': self.current_frame,
            'current_clip_path': self.current_clip.path if self.current_clip else None
        }
        self.redo_stack.append(current_state)

        # Restore previous state
        previous_state = self.undo_stack.pop()
        self.restore_state(previous_state)

        return True, "Undo successful"

    def redo(self):
        if not self.redo_stack:
            return False, "Nothing to redo"

        # Save current state to undo stack
        current_state = {
            'tracks': [[{
                'path': clip.path,
                'start_frame': clip.start_frame,
                'end_frame': clip.end_frame,
                'position': clip.position
            } for clip in track] for track in self.tracks],
            'current_frame': self.current_frame,
            'current_clip_path': self.current_clip.path if self.current_clip else None
        }
        self.undo_stack.append(current_state)

        # Restore next state
        next_state = self.redo_stack.pop()
        self.restore_state(next_state)

        return True, "Redo successful"

    def restore_state(self, state):
        # Restore tracks
        self.tracks = [[] for _ in range(5)]
        for track_idx, track_data in enumerate(state['tracks']):
            for clip_data in track_data:
                clip = next((c for c in self.video_clips if c.path == clip_data['path']), None)
                if clip:
                    new_clip = VideoClip(clip.path)
                    new_clip.start_frame = clip_data['start_frame']
                    new_clip.end_frame = clip_data['end_frame']
                    new_clip.position = clip_data['position']
                    new_clip.total_frames = clip.total_frames
                    new_clip.fps = clip.fps
                    self.tracks[track_idx].append(new_clip)

        # Restore current frame and clip
        self.current_frame = state['current_frame']
        if state['current_clip_path']:
            self.current_clip = next((c for c in self.video_clips if c.path == state['current_clip_path']), None)