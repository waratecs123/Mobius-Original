# functions.py
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
from yt_dlp import YoutubeDL

# Разрешённые домены
ALLOWED_HOSTS = {
    # YouTube
    "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be",
    # TikTok
    "tiktok.com", "www.tiktok.com", "m.tiktok.com", "vt.tiktok.com",
    # VK
    "vk.com", "www.vk.com", "m.vk.com",
    # Rutube
    "rutube.ru", "www.rutube.ru",
    # Dailymotion
    "dailymotion.com", "www.dailymotion.com",
    # Bilibili
    "bilibili.com", "www.bilibili.com", "m.bilibili.com",
    # Instagram
    "instagram.com", "www.instagram.com"
}


def is_allowed_url(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
        return any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS)
    except Exception:
        return False


def build_format(quality: str, audio_only: bool) -> str:
    if audio_only:
        return "bestaudio/best"
    mapping = {
        "720p": 720, "1080p": 1080, "1440p": 1440,
        "2160p": 2160, "4320p": 4320, "best": None
    }
    target = mapping[quality]
    if target is None:
        # прогрессивные форматы (видео+аудио в одном контейнере)
        return "best[ext=mp4][acodec!=none]/best"
    return f"best[height<={target}][ext=mp4][acodec!=none]/best[height<={target}]"


class JobsArchiveFunctions:
    def __init__(self, gui):
        self.gui = gui
        self.downloading = False

    def start_download(self):
        url = self.gui.url_var.get().strip()
        quality = self.gui.quality_var.get()
        audio_only = self.gui.audio_var.get()
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

        # Очищаем лог перед началом загрузки
        self.gui.log_text.delete("1.0", tk.END)
        self.gui.log_text.insert(tk.END, f"Начало загрузки: {url}\n")

        # Запускаем загрузку в отдельном потоке
        threading.Thread(
            target=self.download_video,
            args=(url, quality, audio_only, out_dir, proxy),
            daemon=True
        ).start()

    def download_video(self, url, quality, audio_only, out_dir, proxy):
        try:
            self.downloading = True
            os.makedirs(out_dir, exist_ok=True)

            ydl_opts = {
                "outtmpl": os.path.join(out_dir, "%(title).200B [%(id)s].%(ext)s"),
                "format": build_format(quality, audio_only),
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

    def progress_hook(self, d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            if total:
                pct = downloaded / total * 100
                speed = d.get("speed", 0)
                speed_str = f"{speed / (1024 * 1024):.1f} MB/s" if speed > 1024 * 1024 else f"{speed / 1024:.1f} KB/s"

                # Обновляем лог
                self.gui.log_text.insert(tk.END, f"\r⬇ {pct:.1f}% | {speed_str}\n")
                self.gui.log_text.see(tk.END)
        elif d.get("status") == "finished":
            self.gui.log_text.insert(tk.END, "\nФайл загружен.\n")

    def choose_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.gui.out_dir_var.set(folder)

    def paste_url(self):
        try:
            url = self.gui.root.clipboard_get()
            self.gui.url_var.set(url)
            # Убираем placeholder при вставке
            if self.gui.url_entry.get() == "Вставьте ссылку на видео здесь...":
                self.gui.url_entry.config(fg=self.gui.text_color)
        except tk.TclError:
            self.gui.show_error("Ошибка", "Буфер обмена пуст или не содержит ссылку.")