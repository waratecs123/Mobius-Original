import cv2
import numpy as np
import pyautogui
import threading
import time
import pyaudio
import wave
import os
import logging
from PIL import Image
import subprocess  # For ffmpeg merge

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
        self.transition_frame = None
        self.transition_start_time = 0

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
                raise Exception("Не удалось инициализировать видео-райтер")

            self.recording = True
            self.thread = threading.Thread(target=self.record, daemon=True)
            self.thread.start()
            logging.info("VideoRecorder запущен успешно")
        except Exception as e:
            logging.error(f"Ошибка запуска VideoRecorder: {e}")
            raise

    def apply_effects(self, frame):
        try:
            # Brightness and Contrast
            frame = cv2.convertScaleAbs(frame, alpha=self.gui.contrast_var.get(), beta=self.gui.brightness_var.get())

            # Blur
            if self.gui.blur_var.get() > 0:
                kernel_size = max(3, int(self.gui.blur_var.get() * 2) | 1)
                frame = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)

            # Hue
            if self.gui.hue_var.get() != 0:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hsv[:, :, 0] = (hsv[:, :, 0] + int(self.gui.hue_var.get())) % 180
                frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # Saturation
            saturation = self.gui.saturation_var.get()
            if saturation != 1.0:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255).astype(np.uint8)
                frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # Sharpness
            sharpness = self.gui.sharpness_var.get()
            if sharpness > 0:
                kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) * sharpness
                kernel[1, 1] = 1 + 8 * sharpness
                frame = cv2.filter2D(frame, -1, kernel)

            # Gamma
            gamma = self.gui.gamma_var.get()
            if gamma != 1.0:
                inv_gamma = 1.0 / gamma
                table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
                frame = cv2.LUT(frame, table)

            # Color Temperature
            temperature = self.gui.temperature_var.get()
            if temperature != 0:
                temp_val = temperature * 0.5
                if temperature > 0:
                    frame[:, :, 2] = np.clip(frame[:, :, 2] + temp_val, 0, 255)
                    frame[:, :, 0] = np.clip(frame[:, :, 0] - temp_val / 2, 0, 255)
                else:
                    frame[:, :, 0] = np.clip(frame[:, :, 0] - temp_val / 2, 0, 255)
                    frame[:, :, 2] = np.clip(frame[:, :, 2] + temp_val, 0, 255)

            # Tint
            tint = self.gui.tint_var.get()
            if tint != 0:
                tint_val = tint * 0.5
                if tint > 0:
                    frame[:, :, 0] = np.clip(frame[:, :, 0] + tint_val, 0, 255)
                    frame[:, :, 2] = np.clip(frame[:, :, 2] + tint_val, 0, 255)
                else:
                    frame[:, :, 1] = np.clip(frame[:, :, 1] - tint_val, 0, 255)

            # Vignette
            vignette = self.gui.vignette_var.get()
            if vignette > 0:
                rows, cols = frame.shape[:2]
                X, Y = np.meshgrid(np.arange(cols), np.arange(rows))
                centerX, centerY = cols / 2, rows / 2
                R = np.sqrt((X - centerX) ** 2 + (Y - centerY) ** 2)
                maxR = np.sqrt(centerX ** 2 + centerY ** 2)
                vig = 1 - vignette * (R / maxR) ** 2
                vig = np.clip(vig, 0, 1)[:, :, np.newaxis]
                frame = np.clip(frame * vig, 0, 255).astype(np.uint8)

            # Noise
            noise = self.gui.noise_var.get()
            if noise > 0:
                noise_img = np.random.normal(0, noise * 25, frame.shape)
                frame = np.clip(frame + noise_img, 0, 255).astype(np.uint8)

            # Sepia
            sepia = self.gui.sepia_var.get()
            if sepia > 0:
                sepia_kernel = np.array([
                    [0.272, 0.534, 0.131],
                    [0.349, 0.686, 0.168],
                    [0.393, 0.769, 0.189]
                ])
                sepia_frame = cv2.transform(frame, sepia_kernel)
                frame = cv2.addWeighted(frame, 1 - sepia, sepia_frame, sepia, 0)

            # Grayscale
            grayscale = self.gui.grayscale_var.get()
            if grayscale > 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                frame = cv2.addWeighted(frame, 1 - grayscale, gray, grayscale, 0)

            # Invert
            invert = self.gui.invert_var.get()
            if invert > 0:
                inverted = 255 - frame
                frame = cv2.addWeighted(frame, 1 - invert, inverted, invert, 0)

            # Edge Enhancement
            edge = self.gui.edge_var.get()
            if edge > 0:
                edges = cv2.Laplacian(frame, cv2.CV_8U, ksize=3)
                edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                frame = cv2.addWeighted(frame, 1 - edge, edges, edge, 0)

            # Emboss
            emboss = self.gui.emboss_var.get()
            if emboss > 0:
                kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
                embossed = cv2.filter2D(frame, -1, kernel)
                frame = cv2.addWeighted(frame, 1 - emboss, embossed, emboss, 0)

            # Posterize
            posterize = self.gui.posterize_var.get()
            if posterize > 0:
                levels = int(8 * (1 - posterize)) + 2
                frame = (frame // (256 // levels)) * (256 // levels)

            # Solarize
            solarize = self.gui.solarize_var.get()
            if solarize > 0:
                threshold = 128 * solarize
                frame = np.where(frame < threshold, frame, 255 - frame)

            return frame
        except Exception as e:
            logging.error(f"Ошибка применения эффектов: {e}")
            return frame

    def apply_transition(self, old_frame, new_frame):
        if self.gui.transition_type == 'cut' or not old_frame:
            return new_frame
        elif self.gui.transition_type == 'fade':
            elapsed = time.time() - self.transition_start_time
            alpha = min(elapsed / self.gui.transition_duration, 1.0)
            return cv2.addWeighted(old_frame, 1 - alpha, new_frame, alpha, 0.0)
        elif self.gui.transition_type == 'wipe':
            elapsed = time.time() - self.transition_start_time
            progress = min(elapsed / self.gui.transition_duration, 1.0)
            width = int(self.resolution[0] * progress)
            result = new_frame.copy()
            result[:, :width] = old_frame[:, :width]
            return result
        return new_frame

    def record(self):
        frame_time = 1.0 / self.fps
        while self.recording:
            start_time = time.time()
            with self.lock:
                composite_frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
                base_frame = None
                if self.gui.screen_capture_enabled and not self.gui.only_camera_var.get():
                    try:
                        screenshot = pyautogui.screenshot()
                        base_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                        base_frame = cv2.resize(base_frame, self.resolution, interpolation=cv2.INTER_AREA)
                        base_frame = self.apply_effects(base_frame)
                        composite_frame = base_frame.copy()
                    except Exception as e:
                        logging.error(f"Ошибка захвата экрана: {e}")
                if self.gui.camera_enabled:
                    try:
                        ret, camera_frame = self.cap.read()
                        if ret:
                            if self.gui.only_camera_var.get():
                                camera_frame = cv2.resize(camera_frame, self.resolution, interpolation=cv2.INTER_LINEAR)
                                camera_frame = self.apply_effects(camera_frame)
                                composite_frame = camera_frame
                            else:
                                scale = self.gui.camera_scale
                                position = self.gui.camera_position
                                base_size = (160, 120)
                                scaled_size = (int(base_size[0] * scale), int(base_size[1] * scale))
                                camera_frame = cv2.resize(camera_frame, scaled_size, interpolation=cv2.INTER_LINEAR)
                                camera_frame = self.apply_effects(camera_frame)
                                h, w = camera_frame.shape[:2]
                                pos_x, pos_y = position
                                if pos_y + h <= self.resolution[1] and pos_x + w <= self.resolution[0]:
                                    composite_frame[pos_y:pos_y + h, pos_x:pos_x + w] = camera_frame
                    except Exception as e:
                        logging.error(f"Ошибка записи камеры: {e}")

                if base_frame is not None and self.transition_frame is not None and time.time() - self.transition_start_time < self.gui.transition_duration:
                    composite_frame = self.apply_transition(self.transition_frame, composite_frame)
                else:
                    self.transition_frame = None

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
        logging.info("VideoRecorder остановлен")

class AudioRecorder:
    def __init__(self, mic_volume=1.0, system_volume=1.0, noise_suppression=False, gain=0.0, compression=1.0):
        self.recording = False
        self.mic_volume = mic_volume
        self.system_volume = system_volume
        self.noise_suppression = noise_suppression
        self.gain = gain
        self.compression = compression
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.system_frames = []

    def start(self):
        try:
            self.recording = True
            self.frames = []
            self.system_frames = []
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=2,
                rate=44100,
                input=True,
                frames_per_buffer=1024
            )
            self.system_stream = self.stream  # Placeholder for system audio
            self.thread = threading.Thread(target=self.record, daemon=True)
            self.thread.start()
            logging.info("AudioRecorder запущен успешно")
        except Exception as e:
            logging.error(f"Ошибка запуска AudioRecorder: {e}")
            raise

    def record(self):
        while self.recording:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                if self.noise_suppression:
                    data = self.apply_noise_suppression(data)
                data = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                gain_factor = 10 ** (self.gain / 20.0)
                data *= gain_factor
                data = np.clip(data / self.compression, -1.0, 1.0) * self.compression
                data = data * self.mic_volume * self.system_volume
                data = np.clip(data, -32768, 32767).astype(np.int16)
                self.frames.append(data.tobytes())
            except Exception as e:
                logging.error(f"Ошибка записи аудио: {e}")

    def apply_noise_suppression(self, data):
        data_np = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        data_np[::2] *= 0.8
        return data_np.astype(np.int16).tobytes()

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
            logging.info("Аудио сохранено успешно")
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
        self.transition_frame = None
        self.transition_start_time = 0
        self.preview_resolution = (960, 540)  # Default to higher resolution for better quality

    def start(self):
        self.update_preview_resolution()
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
        logging.info("PreviewUpdater запущен")

    def update_preview_resolution(self):
        res_str = self.gui.resolution_var.get()
        full_w, full_h = map(int, res_str.split('x'))
        # Scale to fit within 960x540 while preserving aspect ratio
        scale = min(960 / full_w, 540 / full_h)
        self.preview_resolution = (int(full_w * scale), int(full_h * scale))

    def restart_preview(self):
        self.update_preview_resolution()

    def apply_effects(self, frame):
        try:
            frame = cv2.convertScaleAbs(frame, alpha=self.gui.contrast_var.get(), beta=self.gui.brightness_var.get())

            if self.gui.blur_var.get() > 0:
                kernel_size = max(3, int(self.gui.blur_var.get() * 2) | 1)
                frame = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)

            if self.gui.hue_var.get() != 0:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hsv[:, :, 0] = (hsv[:, :, 0] + int(self.gui.hue_var.get())) % 180
                frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            saturation = self.gui.saturation_var.get()
            if saturation != 1.0:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255).astype(np.uint8)
                frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            sharpness = self.gui.sharpness_var.get()
            if sharpness > 0:
                kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) * sharpness
                kernel[1, 1] = 1 + 8 * sharpness
                frame = cv2.filter2D(frame, -1, kernel)

            gamma = self.gui.gamma_var.get()
            if gamma != 1.0:
                inv_gamma = 1.0 / gamma
                table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
                frame = cv2.LUT(frame, table)

            temperature = self.gui.temperature_var.get()
            if temperature != 0:
                temp_val = temperature * 0.5
                if temperature > 0:
                    frame[:, :, 2] = np.clip(frame[:, :, 2] + temp_val, 0, 255)
                    frame[:, :, 0] = np.clip(frame[:, :, 0] - temp_val / 2, 0, 255)
                else:
                    frame[:, :, 0] = np.clip(frame[:, :, 0] - temp_val / 2, 0, 255)
                    frame[:, :, 2] = np.clip(frame[:, :, 2] + temp_val, 0, 255)

            tint = self.gui.tint_var.get()
            if tint != 0:
                tint_val = tint * 0.5
                if tint > 0:
                    frame[:, :, 0] = np.clip(frame[:, :, 0] + tint_val, 0, 255)
                    frame[:, :, 2] = np.clip(frame[:, :, 2] + tint_val, 0, 255)
                else:
                    frame[:, :, 1] = np.clip(frame[:, :, 1] - tint_val, 0, 255)

            vignette = self.gui.vignette_var.get()
            if vignette > 0:
                rows, cols = frame.shape[:2]
                X, Y = np.meshgrid(np.arange(cols), np.arange(rows))
                centerX, centerY = cols / 2, rows / 2
                R = np.sqrt((X - centerX) ** 2 + (Y - centerY) ** 2)
                maxR = np.sqrt(centerX ** 2 + centerY ** 2)
                vig = 1 - vignette * (R / maxR) ** 2
                vig = np.clip(vig, 0, 1)[:, :, np.newaxis]
                frame = np.clip(frame * vig, 0, 255).astype(np.uint8)

            noise = self.gui.noise_var.get()
            if noise > 0:
                noise_img = np.random.normal(0, noise * 25, frame.shape)
                frame = np.clip(frame + noise_img, 0, 255).astype(np.uint8)

            sepia = self.gui.sepia_var.get()
            if sepia > 0:
                sepia_kernel = np.array([
                    [0.272, 0.534, 0.131],
                    [0.349, 0.686, 0.168],
                    [0.393, 0.769, 0.189]
                ])
                sepia_frame = cv2.transform(frame, sepia_kernel)
                frame = cv2.addWeighted(frame, 1 - sepia, sepia_frame, sepia, 0)

            grayscale = self.gui.grayscale_var.get()
            if grayscale > 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                frame = cv2.addWeighted(frame, 1 - grayscale, gray, grayscale, 0)

            invert = self.gui.invert_var.get()
            if invert > 0:
                inverted = 255 - frame
                frame = cv2.addWeighted(frame, 1 - invert, inverted, invert, 0)

            edge = self.gui.edge_var.get()
            if edge > 0:
                edges = cv2.Laplacian(frame, cv2.CV_8U, ksize=3)
                edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                frame = cv2.addWeighted(frame, 1 - edge, edges, edge, 0)

            emboss = self.gui.emboss_var.get()
            if emboss > 0:
                kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
                embossed = cv2.filter2D(frame, -1, kernel)
                frame = cv2.addWeighted(frame, 1 - emboss, embossed, emboss, 0)

            posterize = self.gui.posterize_var.get()
            if posterize > 0:
                levels = int(8 * (1 - posterize)) + 2
                frame = (frame // (256 // levels)) * (256 // levels)

            solarize = self.gui.solarize_var.get()
            if solarize > 0:
                threshold = 128 * solarize
                frame = np.where(frame < threshold, frame, 255 - frame)

            return frame
        except Exception as e:
            logging.error(f"Ошибка применения эффектов: {e}")
            return frame

    def apply_transition(self, old_frame, new_frame):
        if not old_frame:
            return new_frame
        if self.gui.transition_type == 'cut':
            return new_frame
        elif self.gui.transition_type == 'fade':
            elapsed = time.time() - self.transition_start_time
            alpha = min(elapsed / self.gui.transition_duration, 1.0)
            return cv2.addWeighted(old_frame, 1 - alpha, new_frame, alpha, 0.0)
        elif self.gui.transition_type == 'wipe':
            elapsed = time.time() - self.transition_start_time
            progress = min(elapsed / self.gui.transition_duration, 1.0)
            width = int(new_frame.shape[1] * progress)
            result = new_frame.copy()
            result[:, :width] = old_frame[:, :width]
            return result
        return new_frame

    def create_preview_frame(self):
        preview_res = self.preview_resolution
        preview_frame = np.zeros((preview_res[1], preview_res[0], 3), dtype=np.uint8)
        canvas_width = self.gui.preview_canvas_rec.winfo_width()
        canvas_height = self.gui.preview_canvas_rec.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            logging.warning("Холст предпросмотра не инициализирован")
            return preview_frame

        base_frame = None
        if self.gui.screen_capture_enabled and not self.gui.only_camera_var.get():
            try:
                current_time = time.time()
                if (self.last_screenshot is None or
                        current_time - self.last_screenshot_time > self.screenshot_cache_duration):
                    screenshot = pyautogui.screenshot()
                    if screenshot is None:
                        logging.error("Не удалось захватить скриншот")
                        return preview_frame
                    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    self.last_screenshot = frame
                    self.last_screenshot_time = current_time
                else:
                    frame = self.last_screenshot
                if frame.size == 0:
                    return preview_frame
                # Resize to preview resolution with high-quality interpolation
                frame = cv2.resize(frame, preview_res, interpolation=cv2.INTER_LANCZOS4)
                frame = self.apply_effects(frame)
                preview_frame = frame.copy()
                base_frame = preview_frame.copy()
            except Exception as e:
                logging.error(f"Ошибка предпросмотра экрана: {e}")
        if self.gui.camera_enabled and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret:
                    if self.gui.only_camera_var.get():
                        frame = cv2.resize(frame, preview_res, interpolation=cv2.INTER_LANCZOS4)
                        frame = self.apply_effects(frame)
                        preview_frame = frame
                    else:
                        scale = self.gui.camera_scale
                        position = self.gui.camera_position
                        base_size = (160, 120)
                        scaled_size = (int(base_size[0] * scale), int(base_size[1] * scale))
                        frame = cv2.resize(frame, scaled_size, interpolation=cv2.INTER_LANCZOS4)
                        frame = self.apply_effects(frame)
                        h, w = frame.shape[:2]
                        pos_x, pos_y = position
                        if pos_y + h <= preview_res[1] and pos_x + w <= preview_res[0]:
                            preview_frame[pos_y:pos_y + h, pos_x:pos_x + w] = frame
            except Exception as e:
                logging.error(f"Ошибка предпросмотра камеры: {e}")

        if base_frame is not None and self.transition_frame is not None and time.time() - self.transition_start_time < self.gui.transition_duration:
            preview_frame = self.apply_transition(self.transition_frame, preview_frame)
        else:
            self.transition_frame = None

        return preview_frame

    def update_loop(self):
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            canvas_width = self.gui.preview_canvas_rec.winfo_width()
            canvas_height = self.gui.preview_canvas_rec.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                break
            logging.debug(f"Ожидание инициализации холста (попытка {attempt + 1}/{max_attempts})")
            time.sleep(0.1)
            attempt += 1
        if attempt == max_attempts:
            logging.error("Холст не удалось инициализировать")
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

    def stop(self):
        self.active = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        logging.info("PreviewUpdater остановлен")