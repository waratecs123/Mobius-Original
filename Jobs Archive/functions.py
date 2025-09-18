import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
from yt_dlp import YoutubeDL
import time

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

class JobsArchiveFunctions:
    def __init__(self, gui):
        self.gui = gui
        self.downloading = False
        self.start_time = None

    def start_download(self):
        url = self.gui.url_var.get().strip()
        quality = self.gui.quality_var.get()
        audio_only = self.gui.audio_var.get()
        fps = self.gui.fps_var.get() if hasattr(self.gui, 'fps_var') else None
        codec = self.gui.codec_var.get() if hasattr(self.gui, 'codec_var') else None
        out_dir = self.gui.out_dir_var.get()
        proxy = self.gui.proxy_var.get().strip() or None

        if not url or url == "Вставьте ссылку на видео здесь...":
            self.gui.show_error("Ошибка", "Введите ссылку на видео!")
            return
        if not out_dir:
            self.gui.show_error("Ошибка", "Выберите папку для сохранения!")
            return

        if not is_allowed_url(url):
            self.gui.show_error("Ошибка", "Источник не поддерживается этим загрузчиком.")
            return

        self.gui.log_text.delete("1.0", tk.END)
        self.gui.log_text.insert(tk.END, f"Начало загрузки: {url}\n")
        self.gui.reset_progress_and_timer()
        self.start_time = time.time()

        threading.Thread(
            target=self.download_video,
            args=(url, quality, audio_only, fps, codec, out_dir, proxy),
            daemon=True
        ).start()

    def download_video(self, url, quality, audio_only, fps, codec, out_dir, proxy):
        try:
            self.downloading = True
            os.makedirs(out_dir, exist_ok=True)

            ydl_opts_info = {
                "quiet": True,
                "simulate": True,
                "listformats": True,
                "proxy": proxy
            }
            with YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])

            if not audio_only:
                video_formats = [f for f in formats if f.get('vcodec') != 'none']
                selected_format = self.gui.show_format_selector(video_formats)
                if not selected_format:
                    self.gui.log_text.insert(tk.END, "\n❌ Загрузка отменена пользователем.\n")
                    self.downloading = False
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
            }

            if proxy:
                ydl_opts["proxy"] = proxy

            with YoutubeDL(ydl_opts) as ydl:
                code = ydl.download([url])

            if code == 0:
                self.gui.log_text.insert(tk.END, "\n✅ Загрузка завершена.\n")
                self.gui.show_info("Готово", "Загрузка завершена!")
            else:
                raise RuntimeError(f"yt-dlp вернул код {code}")

        except Exception as e:
            self.gui.log_text.insert(tk.END, f"\n❌ Ошибка: {e}\n")
            self.gui.show_error("Ошибка", str(e))
        finally:
            self.downloading = False
            self.gui.reset_progress_and_timer()

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

    def paste_url(self):
        try:
            url = self.gui.root.clipboard_get()
            self.gui.url_var.set(url)
            if self.gui.url_entry.get() == "Вставьте ссылку на видео здесь...":
                self.gui.url_entry.config(fg=self.gui.text_color)
        except tk.TclError:
            self.gui.show_error("Ошибка", "Буфер обмена пуст или не содержит ссылку.")