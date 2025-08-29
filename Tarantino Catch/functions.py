import cv2
import numpy as np
import pyautogui
import threading
import time
import pyaudio
import wave
import os


class VideoRecorder:
    def __init__(self, gui, resolution, fps, bitrate):
        self.gui = gui
        self.resolution = resolution
        self.fps = fps
        self.bitrate = bitrate
        self.recording = False
        self.cap = None
        self.out = None

    def start(self):
        if self.gui.camera_enabled:
            camera_index = int(self.gui.camera_index_var.get())
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                raise Exception(f"Не удалось открыть камеру {camera_index}")

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('temp_video.avi', fourcc, self.fps, self.resolution)
        self.recording = True

        self.thread = threading.Thread(target=self.record, daemon=True)
        self.thread.start()

    def record(self):
        frame_time = 1.0 / self.fps

        while self.recording:
            start_time = time.time()

            composite_frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)

            # Захват экрана
            if self.gui.screen_capture_enabled:
                try:
                    screenshot = pyautogui.screenshot()
                    screen_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    screen_frame = cv2.resize(screen_frame, self.resolution)
                    composite_frame = screen_frame
                except Exception as e:
                    print(f"Ошибка захвата экрана: {e}")

            # Захват камеры
            if self.gui.camera_enabled and self.cap:
                ret, camera_frame = self.cap.read()
                if ret:
                    camera_frame = cv2.resize(camera_frame, (160, 120))
                    h, w = camera_frame.shape[:2]

                    # Позиционирование камеры
                    canvas_width = self.gui.preview_canvas.winfo_width() or 800
                    canvas_height = self.gui.preview_canvas.winfo_height() or 600

                    norm_x = self.gui.camera_position[0] / canvas_width
                    norm_y = self.gui.camera_position[1] / canvas_height

                    pos_x = int(norm_x * self.resolution[0])
                    pos_y = int(norm_y * self.resolution[1])

                    if pos_y + h <= self.resolution[1] and pos_x + w <= self.resolution[0]:
                        composite_frame[pos_y:pos_y + h, pos_x:pos_x + w] = camera_frame

            self.out.write(composite_frame)

            # Поддержание постоянного FPS
            elapsed = time.time() - start_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

    def stop(self):
        self.recording = False
        if self.cap:
            self.cap.release()
        if self.out:
            self.out.release()


class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start(self):
        self.recording = True
        self.frames = []

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )

        self.thread = threading.Thread(target=self.record, daemon=True)
        self.thread.start()

    def record(self):
        while self.recording:
            data = self.stream.read(1024)
            self.frames.append(data)

    def stop(self):
        self.recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        # Сохранение аудио в файл
        wf = wave.open('temp_audio.wav', 'wb')
        wf.setnchannels(2)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        self.audio.terminate()


class PreviewUpdater:
    def __init__(self, gui):
        self.gui = gui
        self.active = True
        self.preview_fps = 30

    def start(self):
        self.thread = threading.Thread(target=self.update_loop, daemon=True)
        self.thread.start()

    def update_loop(self):
        while self.active:
            try:
                preview_frame = self.create_preview_frame()
                self.gui.root.after(0, self.gui.update_preview_gui, preview_frame)

                # Динамический FPS предпросмотра
                current_fps = int(self.gui.preview_fps_var.get()) if hasattr(self.gui, 'preview_fps_var') else 30
                sleep_time = 1.0 / current_fps
                time.sleep(sleep_time)

            except Exception as e:
                print(f"Ошибка предпросмотра: {e}")
                time.sleep(1)

    def create_preview_frame(self):
        # Разрешение предпросмотра (фиксированное, без растягивания)
        preview_res = (800, 600)
        preview_frame = np.zeros((preview_res[1], preview_res[0], 3), dtype=np.uint8)

        # Захват экрана для предпросмотра
        if self.gui.screen_capture_enabled:
            try:
                screenshot = pyautogui.screenshot()
                screen_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                # Сохранение пропорций
                h, w = screen_frame.shape[:2]
                scale = min(preview_res[0] / w, preview_res[1] / h)
                new_w, new_h = int(w * scale), int(h * scale)

                screen_frame = cv2.resize(screen_frame, (new_w, new_h))

                # Центрирование
                x_offset = (preview_res[0] - new_w) // 2
                y_offset = (preview_res[1] - new_h) // 2

                preview_frame[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = screen_frame
            except Exception as e:
                print(f"Ошибка захвата экрана для предпросмотра: {e}")

        # Захват камеры для предпросмотра
        if self.gui.camera_enabled:
            try:
                camera_index = int(self.gui.camera_index_var.get())
                temp_cap = cv2.VideoCapture(camera_index)
                if temp_cap.isOpened():
                    ret, camera_frame = temp_cap.read()
                    if ret:
                        camera_frame = cv2.resize(camera_frame, (160, 120))
                        h, w = camera_frame.shape[:2]

                        # Позиционирование камеры в предпросмотре
                        pos_x = min(max(int(self.gui.camera_position[0]), 0), preview_res[0] - w)
                        pos_y = min(max(int(self.gui.camera_position[1]), 0), preview_res[1] - h)

                        if pos_y + h <= preview_res[1] and pos_x + w <= preview_res[0]:
                            preview_frame[pos_y:pos_y + h, pos_x:pos_x + w] = camera_frame
                    temp_cap.release()
            except Exception as e:
                print(f"Ошибка захвата камеры для предпросмотра: {e}")

        return preview_frame

    def stop(self):
        self.active = False