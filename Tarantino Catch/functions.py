import cv2
import numpy as np
import pyautogui
import threading
import time
import pyaudio
import wave
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class VideoRecorder:
    def __init__(self, gui, resolution, fps, bitrate):
        self.gui = gui
        self.resolution = resolution
        self.fps = fps
        self.bitrate = bitrate
        self.recording = False
        self.cap = None
        self.out = None
        self.lock = threading.Lock()

    def start(self):
        try:
            if self.gui.camera_enabled:
                camera_index = int(self.gui.camera_index_var.get())
                self.cap = cv2.VideoCapture(camera_index)
                if not self.cap.isOpened():
                    raise Exception(f"Не удалось открыть камеру {camera_index}")

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out = cv2.VideoWriter('temp_video.avi', fourcc, self.fps, self.resolution)
            if not self.out.isOpened():
                raise Exception("Не удалось инициализировать запись видео")

            self.recording = True
            self.thread = threading.Thread(target=self.record, daemon=True)
            self.thread.start()
            logging.info("VideoRecorder started successfully")

        except Exception as e:
            logging.error(f"Ошибка запуска VideoRecorder: {e}")
            raise

    def record(self):
        frame_time = 1.0 / self.fps

        while self.recording:
            start_time = time.time()
            with self.lock:
                composite_frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)

                if self.gui.screen_capture_enabled:
                    try:
                        screenshot = pyautogui.screenshot()
                        screen_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                        screen_frame = cv2.resize(screen_frame, self.resolution, interpolation=cv2.INTER_AREA)
                        composite_frame = screen_frame
                    except Exception as e:
                        logging.error(f"Ошибка захвата экрана: {e}")

                if self.gui.camera_enabled and self.cap and self.cap.isOpened():
                    ret, camera_frame = self.cap.read()
                    if ret:
                        base_size = (160, 120)
                        scaled_size = (int(base_size[0] * self.gui.camera_scale),
                                       int(base_size[1] * self.gui.camera_scale))
                        camera_frame = cv2.resize(camera_frame, scaled_size, interpolation=cv2.INTER_LINEAR)
                        h, w = camera_frame.shape[:2]

                        canvas_width = self.gui.preview_canvas.winfo_width() or 800
                        canvas_height = self.gui.preview_canvas.winfo_height() or 600
                        norm_x = self.gui.camera_position[0] / canvas_width
                        norm_y = self.gui.camera_position[1] / canvas_height
                        pos_x = int(norm_x * self.resolution[0])
                        pos_y = int(norm_y * self.resolution[1])

                        if pos_y + h <= self.resolution[1] and pos_x + w <= self.resolution[0]:
                            composite_frame[pos_y:pos_y + h, pos_x:pos_x + w] = camera_frame

                self.out.write(composite_frame)

            elapsed = time.time() - start_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

    def stop(self):
        self.recording = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if self.out:
            self.out.release()
        logging.info("VideoRecorder stopped")

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start(self):
        try:
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
            logging.info("AudioRecorder started successfully")
        except Exception as e:
            logging.error(f"Ошибка запуска AudioRecorder: {e}")
            raise

    def record(self):
        while self.recording:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                logging.error(f"Ошибка записи аудио: {e}")

    def stop(self):
        self.recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        try:
            wf = wave.open('temp_audio.wav', 'wb')
            wf.setnchannels(2)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            logging.info("Audio saved successfully")
        except Exception as e:
            logging.error(f"Ошибка сохранения аудио: {e}")

        self.audio.terminate()

class PreviewUpdater:
    def __init__(self, gui):
        self.gui = gui
        self.active = True
        self.preview_fps = 30
        self.last_screenshot = None
        self.last_screenshot_time = 0
        self.screenshot_cache_duration = 0.5
        self.lock = threading.Lock()
        self.cap = None

    def start(self):
        if self.gui.camera_enabled:
            try:
                camera_index = int(self.gui.camera_index_var.get())
                self.cap = cv2.VideoCapture(camera_index)
                if not self.cap.isOpened():
                    logging.error(f"Не удалось открыть камеру {camera_index} для предпросмотра")
                    self.cap = None
            except Exception as e:
                logging.error(f"Ошибка инициализации камеры для предпросмотра: {e}")
                self.cap = None

        self.thread = threading.Thread(target=self.update_loop, daemon=True)
        self.thread.start()
        logging.info("PreviewUpdater started")

    def update_loop(self):
        # Wait for canvas to initialize
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            canvas_width = self.gui.preview_canvas.winfo_width()
            canvas_height = self.gui.preview_canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                break
            logging.debug(f"Waiting for canvas initialization (attempt {attempt + 1}/{max_attempts})")
            time.sleep(0.1)
            attempt += 1

        if attempt == max_attempts:
            logging.error("Canvas failed to initialize after maximum attempts")
            return

        while self.active:
            try:
                current_fps = int(self.gui.preview_fps_var.get()) if hasattr(self.gui, 'preview_fps_var') else 30
                sleep_time = 1.0 / max(1, current_fps)

                with self.lock:
                    preview_frame = self.create_preview_frame()
                    if preview_frame is not None:
                        self.gui.root.after(0, self.gui.update_preview_gui, preview_frame)

                time.sleep(sleep_time)
            except Exception as e:
                logging.error(f"Ошибка обновления предпросмотра: {e}")
                time.sleep(0.5)

    def create_preview_frame(self):
        preview_res = (960, 540)
        preview_frame = np.zeros((preview_res[1], preview_res[0], 3), dtype=np.uint8)

        canvas_width = self.gui.preview_canvas.winfo_width()
        canvas_height = self.gui.preview_canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            logging.warning("Preview canvas not initialized properly")
            return preview_frame

        if self.gui.screen_capture_enabled:
            try:
                current_time = time.time()
                if (self.gui.last_screenshot is None or
                        current_time - self.gui.last_screenshot_time > self.gui.screenshot_cache_duration):
                    screenshot = pyautogui.screenshot()
                    if screenshot is None:
                        logging.error("Failed to capture screenshot")
                        return preview_frame
                    screen_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    self.gui.last_screenshot = screen_frame
                    self.gui.last_screenshot_time = current_time
                else:
                    screen_frame = self.gui.last_screenshot

                if screen_frame.size == 0:
                    logging.error("Empty screenshot captured")
                    return preview_frame

                h, w = screen_frame.shape[:2]
                scale = min(preview_res[0] / w, preview_res[1] / h)
                new_w, new_h = int(w * scale), int(h * scale)
                screen_frame = cv2.resize(screen_frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                x_offset = (preview_res[0] - new_w) // 2
                y_offset = (preview_res[1] - new_h) // 2
                preview_frame[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = screen_frame
            except Exception as e:
                logging.error(f"Ошибка предпросмотра захвата экрана: {e}")

        if self.gui.camera_enabled and self.cap and self.cap.isOpened():
            try:
                ret, camera_frame = self.cap.read()
                if ret:
                    base_size = (160, 120)
                    scaled_size = (int(base_size[0] * self.gui.camera_scale),
                                   int(base_size[1] * self.gui.camera_scale))
                    camera_frame = cv2.resize(camera_frame, scaled_size, interpolation=cv2.INTER_LINEAR)
                    h, w = camera_frame.shape[:2]

                    pos_x = min(max(int(self.gui.camera_position[0]), 0), preview_res[0] - w)
                    pos_y = min(max(int(self.gui.camera_position[1]), 0), preview_res[1] - h)

                    if pos_y + h <= preview_res[1] and pos_x + w <= preview_res[0]:
                        preview_frame[pos_y:pos_y + h, pos_x:pos_x + w] = camera_frame
                else:
                    logging.warning("Failed to read camera frame")
            except Exception as e:
                logging.error(f"Ошибка предпросмотра камеры: {e}")

        return preview_frame

    def stop(self):
        self.active = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        logging.info("PreviewUpdater stopped")