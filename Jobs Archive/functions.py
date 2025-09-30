# Improved functions.py with fake User-Agent and host-specific options for better compatibility

import os
import threading
import tkinter as tk
from tkinter import filedialog
from urllib.parse import urlparse
from yt_dlp import YoutubeDL
import time
import json
from datetime import datetime
import random  # Added for randomizing User-Agent if needed

ALLOWED_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be",
    "tiktok.com", "www.tiktok.com", "m.tiktok.com", "vt.tiktok.com",
    "vk.com", "www.vk.com", "m.vk.com",
    "rutube.ru", "www.rutube.ru",
    "dailymotion.com", "www.dailymotion.com",
    "bilibili.com", "www.bilibili.com", "m.bilibili.com",
    "instagram.com", "www.instagram.com",
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    "facebook.com", "www.facebook.com", "fb.watch", "fb.com",
    "vimeo.com", "www.vimeo.com", "player.vimeo.com",
    "reddit.com", "www.reddit.com", "v.redd.it",
    "twitch.tv", "www.twitch.tv", "clips.twitch.tv",
    "soundcloud.com", "www.soundcloud.com",
    "pinterest.com", "www.pinterest.com", "pin.it",
    "linkedin.com", "www.linkedin.com",
    "ok.ru", "www.ok.ru",
    "streamable.com", "www.streamable.com",
    "tumblr.com", "www.tumblr.com",
    "flickr.com", "www.flickr.com",
    "vine.co", "www.vine.co",
    "peertube.tv", "www.peertube.tv",
    "rumble.com", "www.rumble.com",
    "nicovideo.jp", "www.nicovideo.jp",
    "bitchute.com", "www.bitchute.com"
}

# List of fake User-Agents for rotation (to avoid detection/blocking)
FAKE_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
]


def get_random_user_agent():
    return random.choice(FAKE_USER_AGENTS)


def is_allowed_url(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
        return any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS)
    except Exception:
        return False


def build_format(quality: str, audio_only: bool, fps: str = None, codec: str = None) -> str:
    if audio_only:
        return "bestaudio/best"
    base_format = "best[ext=mp4][acodec!=none]"
    filters = []

    if quality != "best":
        try:
            height = int(quality.replace("p", ""))
            filters.append(f"height<={height}")
        except ValueError:
            pass

    if fps:
        try:
            fps_value = int(fps)
            filters.append(f"fps<={fps_value}")
        except ValueError:
            pass

    if codec:
        filters.append(f"vcodec~={codec}")

    if filters:
        base_format = f"best[{'+'.join(filters)}][ext=mp4][acodec!=none]/best"

    return base_format


def user_friendly_error(error: Exception) -> str:
    """Convert technical errors to user-friendly messages."""
    error_str = str(error).lower()
    if "url" in error_str or "invalid" in error_str:
        return "Неправильная или неподдерживаемая ссылка. Проверьте URL и попробуйте снова."
    elif "network" in error_str or "connection" in error_str:
        return "Ошибка сети. Проверьте ваше интернет-соединение."
    elif "permission" in error_str or "access" in error_str:
        return "Нет доступа к папке для сохранения. Выберите другую папку или проверьте права доступа."
    elif "format" in error_str or "codec" in error_str:
        return "Выбранный формат видео недоступен. Попробуйте другой формат или качество."
    elif "timeout" in error_str:
        return "Время ожидания истекло. Проверьте соединение или попробуйте позже."
    else:
        return f"Произошла ошибка: {str(error)}. Попробуйте снова или обратитесь в поддержку."


class JobsArchiveFunctions:
    def __init__(self, gui):
        self.gui = gui
        self.downloading = False
        self.start_time = None
        self.download_queue = []
        self.history_file = "history/download_history.json"
        self.settings_file = "history/settings.json"
        self.load_settings()

    def save_history(self, url, title, status, filepath):
        history_entry = {
            "url": url,
            "title": title,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "filepath": filepath
        }
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass
        history.append(history_entry)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def load_history(self):
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass
        return history

    def clear_history(self):
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        self.gui.update_history_display()
        self.gui.update_stats_display()

    def save_settings(self):
        settings = {
            "quality": self.gui.quality_var.get(),
            "fps": self.gui.fps_var.get(),
            "codec": self.gui.codec_var.get(),
            "audio_only": self.gui.audio_var.get(),
            "out_dir": self.gui.out_dir_var.get(),
            "proxy": self.gui.proxy_var.get()
        }
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.gui.quality_var.set(settings.get("quality", "best"))
                    self.gui.fps_var.set(settings.get("fps", "any"))
                    self.gui.codec_var.set(settings.get("codec", "any"))
                    self.gui.audio_var.set(settings.get("audio_only", False))
                    self.gui.out_dir_var.set(settings.get("out_dir", os.path.join(os.getcwd(), "downloads")))
                    self.gui.proxy_var.set(settings.get("proxy", ""))
            except:
                pass

    def add_to_queue(self, url):
        if url and url not in self.download_queue and url != "Вставьте ссылку на видео здесь...":
            self.download_queue.append(url)
            self.gui.update_queue_display()
            self.gui.update_error_display(f"Добавлено в очередь: {url}")
            if not self.downloading:
                self.start_download()

    def remove_from_queue(self, index):
        if 0 <= index < len(self.download_queue):
            removed_url = self.download_queue.pop(index)
            self.gui.log_text.insert(tk.END, f"Удалено из очереди: {removed_url}\n")
            self.gui.update_queue_display()
            self.gui.update_error_display(f"Удалено из очереди: {removed_url}")
            if index == 0 and self.downloading:
                self.downloading = False
                self.start_download()

    def retry_download(self, url):
        self.add_to_queue(url)
        self.gui.update_error_display(f"Повторная загрузка добавлена в очередь: {url}")

    def start_download(self):
        if not self.download_queue:
            return

        url = self.download_queue[0]
        quality = self.gui.quality_var.get()
        audio_only = self.gui.audio_var.get()
        fps = self.gui.fps_var.get() if hasattr(self.gui, 'fps_var') else None
        codec = self.gui.codec_var.get() if hasattr(self.gui, 'codec_var') else None
        out_dir = self.gui.out_dir_var.get()
        proxy = self.gui.proxy_var.get().strip() or None

        if not url or url == "Вставьте ссылку на видео здесь...":
            self.gui.update_error_display("Введите ссылку на видео!")
            self.download_queue.pop(0)
            self.gui.update_queue_display()
            self.start_download()
            return
        if not out_dir:
            self.gui.update_error_display("Выберите папку для сохранения!")
            self.download_queue.pop(0)
            self.gui.update_queue_display()
            self.start_download()
            return

        if not is_allowed_url(url):
            self.gui.update_error_display("Источник не поддерживается этим загрузчиком.")
            self.download_queue.pop(0)
            self.gui.update_queue_display()
            self.start_download()
            return

        self.gui.log_text.delete("1.0", tk.END)
        self.gui.log_text.insert(tk.END, f"Начало загрузки: {url}\n")
        self.gui.reset_progress_and_timer()
        self.gui.update_error_display("")
        self.start_time = time.time()

        threading.Thread(
            target=self.download_video,
            args=(url, quality, audio_only, fps, codec, out_dir, proxy),
            daemon=True
        ).start()

    def get_host_specific_options(self, url):
        """Add host-specific yt-dlp options to improve compatibility."""
        host = urlparse(url).hostname or ""
        options = {}

        if "tiktok.com" in host:
            options['cookiefile'] = 'cookies.txt'
            options['format'] = 'best[watermark=none]/best'

        elif "instagram.com" in host:
            options['cookiefile'] = 'cookies.txt'

        elif "twitter.com" in host or "x.com" in host:
            options['referer'] = 'https://twitter.com/'

        elif "facebook.com" in host:
            options['referer'] = 'https://www.facebook.com/'

        return options

    def download_video(self, url, quality, audio_only, fps, codec, out_dir, proxy):
        try:
            self.downloading = True
            os.makedirs(out_dir, exist_ok=True)

            user_agent = get_random_user_agent()

            ydl_opts_info = {
                "quiet": True,
                "simulate": True,
                "listformats": True,
                "proxy": proxy,
                "http_headers": {
                    "User-Agent": user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                },
            }
            ydl_opts_info.update(self.get_host_specific_options(url))

            with YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                title = info.get('title', 'Unknown')

            if not audio_only:
                video_formats = [f for f in formats if f.get('vcodec') != 'none']
                selected_format = self.gui.show_format_selector(video_formats)
                if not selected_format:
                    self.gui.log_text.insert(tk.END, "\n❌ Загрузка отменена пользователем.\n")
                    self.gui.update_error_display("Загрузка отменена пользователем.")
                    self.downloading = False
                    self.download_queue.pop(0)
                    self.gui.update_queue_display()
                    self.start_download()
                    return
                format_id = selected_format.get('format_id')
            else:
                format_id = None

            ydl_opts = {
                "outtmpl": os.path.join(out_dir, "%(title).200B [%(id)s].%(ext)s"),
                "format": format_id if format_id else build_format(quality, audio_only, fps, codec),
                "restrictfilenames": True,
                "progress_hooks": [self.progress_hook],
                "quiet": True,
                "socket_timeout": 60,
                "retries": 10,
                "fragment_retries": 10,
                "concurrent_fragment_downloads": 5,
                "http_headers": {
                    "User-Agent": user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                },
            }
            if proxy:
                ydl_opts["proxy"] = proxy

            ydl_opts.update(self.get_host_specific_options(url))

            with YoutubeDL(ydl_opts) as ydl:
                code = ydl.download([url])

            if code == 0:
                filepath = os.path.join(out_dir,
                                        f"{title[:200]} [{info.get('id', 'unknown')}].{ydl.params.get('ext', 'mp4')}")
                self.gui.log_text.insert(tk.END, "\n✅ Загрузка завершена.\n")
                self.gui.update_error_display(f"Загрузка завершена: {filepath}")
                self.save_history(url, title, "Completed", filepath)
            else:
                raise RuntimeError(f"yt-dlp вернул код {code}")

        except Exception as e:
            friendly_error = user_friendly_error(e)
            self.gui.log_text.insert(tk.END, f"\n❌ Ошибка: {friendly_error}\n")
            self.gui.update_error_display(friendly_error)
            self.save_history(url, "Unknown", f"Failed: {friendly_error}", "")
        finally:
            self.downloading = False
            self.download_queue.pop(0)
            self.gui.update_queue_display()
            self.gui.update_history_display()
            self.gui.update_stats_display()
            self.start_download()

    def progress_hook(self, d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            if total:
                pct = downloaded / total * 100
                speed = d.get("speed", 0)
                speed_str = f"{speed / (1024 * 1024):.1f} MB/s" if speed > 1024 * 1024 else f"{speed / 1024:.1f} KB/s"
                elapsed_time = time.time() - self.start_time

                self.gui.update_progress(pct)
                self.gui.update_timer(elapsed_time)
                self.gui.log_text.insert(tk.END, f"\r⬇ {pct:.1f}% | {speed_str}\n")
                self.gui.log_text.see(tk.END)
        elif d.get("status") == "finished":
            self.gui.log_text.insert(tk.END, "\nФайл загружен.\n")
            self.gui.update_progress(100)
            elapsed_time = time.time() - self.start_time
            self.gui.update_timer(elapsed_time)

    def choose_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.gui.out_dir_var.set(folder)
            self.save_settings()

    def paste_url(self):
        try:
            url = self.gui.root.clipboard_get()
            self.gui.url_var.set(url)
            if self.gui.url_entry.get() == "Вставьте ссылку на видео здесь...":
                self.gui.url_entry.config(fg=self.gui.text_color)
            self.add_to_queue(url)
        except tk.TclError:
            self.gui.update_error_display("Буфер обмена пуст или не содержит ссылку.")

    def open_file(self, filepath):
        try:
            if os.path.exists(filepath):
                if os.name == 'nt':
                    os.startfile(filepath)
                elif os.name == 'posix':
                    import platform
                    if platform.system() == 'Darwin':
                        os.system(f'open "{filepath}"')
                    else:
                        os.system(f'xdg-open "{filepath}"')
            else:
                self.gui.update_error_display(f"Файл не найден: {filepath}")
        except Exception as e:
            self.gui.update_error_display(f"Не удалось открыть файл: {str(e)}")

    def open_download_folder(self):
        try:
            path = os.path.abspath(self.gui.out_dir_var.get())
            os.makedirs(path, exist_ok=True)
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                import platform
                if platform.system() == 'Darwin':
                    os.system(f'open "{path}"')
                else:
                    os.system(f'xdg-open "{path}"')
        except Exception as e:
            self.gui.update_error_display(f"Не удалось открыть папку: {str(e)}")