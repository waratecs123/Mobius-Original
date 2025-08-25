import yt_dlp
import threading
import os
import re
from urllib.parse import urlparse


class JobsArchiveFunctions:
    def __init__(self, gui):
        self.gui = gui
        self.download_queue = []
        self.is_downloading = False
        self.current_download_index = None
        self.ydl_opts_template = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'progress_hooks': [self.download_progress_hook],
        }

    def is_valid_url(self, url, platform):
        """Проверяет, является ли URL допустимым для указанной платформы"""
        # Игнорируем placeholder текст
        if url == "Вставьте ссылку YouTube или TikTok здесь...":
            return False

        if platform == "youtube":
            # Проверка для YouTube
            youtube_regex = (
                r'(https?://)?(www\.)?'
                r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
                r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
            return re.match(youtube_regex, url) is not None
        elif platform == "tiktok":
            # Проверка для TikTok
            tiktok_regex = (
                r'(https?://)?(www\.)?'
                r'(tiktok\.com|vm\.tiktok\.com)/'
                r'([a-zA-Z0-9_@.#&+-]+/)?([a-zA-Z0-9_@.#&+-]+)')
            return re.match(tiktok_regex, url) is not None
        return False

    def get_video_info(self, url):
        """Получает информацию о видео"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            print(f"Ошибка получения информации: {e}")
            return None

    def get_available_formats(self, url):
        """Получает доступные форматы видео"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('formats', [])
        except Exception as e:
            print(f"Ошибка получения форматов: {e}")
            return []

    def add_to_queue(self):
        url = self.gui.url_entry.get().strip()
        if not url or url == "Вставьте ссылку YouTube или TikTok здесь...":
            self.gui.show_error("Ошибка", "Введите URL видео")
            return

        # Проверяем, является ли URL YouTube или TikTok
        is_youtube = self.is_valid_url(url, "youtube")
        is_tiktok = self.is_valid_url(url, "tiktok")

        if not (is_youtube or is_tiktok):
            self.gui.show_error("Недопустимый URL", "Поддерживаются только YouTube и TikTok ссылки")
            return

        # Запускаем в отдельном потоке, чтобы не блокировать интерфейс
        thread = threading.Thread(target=self._process_video_add, args=(url, is_tiktok))
        thread.daemon = True
        thread.start()

    def _process_video_add(self, url, is_tiktok):
        """Обрабатывает добавление видео в очередь (в отдельном потоке)"""
        # Получаем информацию о видео
        video_info = self.get_video_info(url)
        if not video_info:
            self.gui.root.after(0, lambda: self.gui.show_error("Ошибка", "Не удалось получить информацию о видео"))
            return

        # Получаем доступные форматы
        formats = self.get_available_formats(url)
        if not formats:
            self.gui.root.after(0, lambda: self.gui.show_error("Ошибка", "Не удалось получить доступные форматы"))
            return

        # Фильтруем только видео форматы
        video_formats = [fmt for fmt in formats if fmt.get('vcodec') != 'none']

        if not video_formats:
            self.gui.root.after(0, lambda: self.gui.show_error("Ошибка", "Не найдено подходящих видео форматов"))
            return

        # Показываем диалог выбора формата в главном потоке
        def show_dialog():
            selected_format = self.gui.show_format_selector(video_formats, is_tiktok)
            if selected_format:
                # Добавляем новую загрузку в очередь
                self.download_queue.append({
                    "status": "В очереди",
                    "progress": "0%",
                    "size": "—",
                    "speed": "—",
                    "url": url,
                    "format_id": selected_format['format_id'],
                    "format_note": selected_format.get('format_note', 'N/A'),
                    "fps": selected_format.get('fps', 'N/A'),
                    "title": video_info.get('title', 'Без названия'),
                    "platform": "TikTok" if is_tiktok else "YouTube"
                })
                self.update_queue_display()
                # Очищаем поле ввода
                self.gui.url_entry.delete(0, "end")
                self.gui.url_entry.config(fg=self.gui.text_color)
                # Возвращаем фокус на поле ввода
                self.gui.root.after(100, self.gui.focus_url_entry)

        self.gui.root.after(0, show_dialog)

    def download_progress_hook(self, d):
        """Обратный вызов для отслеживания прогресса загрузки"""
        if d['status'] == 'downloading':
            # Обновляем прогресс в очереди
            if self.current_download_index is not None:
                item = self.download_queue[self.current_download_index]

                # Расчет процентов
                if d.get('total_bytes'):
                    percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                    item['progress'] = f"{percent:.1f}%"
                    item['size'] = f"{d['total_bytes'] / (1024 * 1024):.1f}MB"
                elif d.get('total_bytes_estimate'):
                    percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                    item['progress'] = f"{percent:.1f}%"
                    item['size'] = f"{d['total_bytes_estimate'] / (1024 * 1024):.1f}MB"

                # Скорость загрузки
                if d.get('speed'):
                    speed_mb = d['speed'] / (1024 * 1024)
                    item['speed'] = f"{speed_mb:.1f}MB/s"

                self.update_queue_display()

        elif d['status'] == 'finished':
            if self.current_download_index is not None:
                self.download_queue[self.current_download_index]['status'] = "Завершено"
                self.download_queue[self.current_download_index]['progress'] = "100%"
                self.update_queue_display()
                self.start_next_download()

    def start_downloads(self):
        if not self.download_queue:
            return

        self.is_downloading = True
        self.start_next_download()

    def start_next_download(self):
        """Начинает следующую загрузку в очереди"""
        if not self.is_downloading:
            return

        # Ищем следующую загрузку в очереди
        next_index = None
        for i, item in enumerate(self.download_queue):
            if item["status"] in ["В очереди", "Приостановлено"]:
                next_index = i
                break

        if next_index is None:
            self.is_downloading = False
            return

        self.current_download_index = next_index
        item = self.download_queue[next_index]
        item["status"] = "Загружается"

        # Настройки для загрузки
        ydl_opts = self.ydl_opts_template.copy()
        ydl_opts['format'] = item['format_id']

        # Запускаем загрузку в отдельном потоке
        thread = threading.Thread(target=self.download_video, args=(item['url'], ydl_opts))
        thread.daemon = True
        thread.start()

        self.update_queue_display()

    def download_video(self, url, ydl_opts):
        """Загружает видео в отдельном потоке"""
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            if self.current_download_index is not None:
                self.download_queue[self.current_download_index]['status'] = f"Ошибка: {str(e)}"
                self.update_queue_display()
            self.is_downloading = False

    def pause_downloads(self):
        self.is_downloading = False
        for i, item in enumerate(self.download_queue):
            if item["status"] == "Загружается":
                self.download_queue[i]["status"] = "Приостановлено"
        self.update_queue_display()

    def remove_selected(self):
        selected = self.gui.queue_tree.selection()
        # Сортируем в обратном порядке, чтобы индексы оставались корректными при удалении
        indices_to_remove = []
        for item in selected:
            idx = self.gui.queue_tree.index(item)
            if 0 <= idx < len(self.download_queue):
                indices_to_remove.append(idx)

        # Удаляем в обратном порядке
        for idx in sorted(indices_to_remove, reverse=True):
            # Если удаляем текущую загрузку, останавливаем её
            if idx == self.current_download_index:
                self.is_downloading = False
                self.current_download_index = None
            del self.download_queue[idx]
        self.update_queue_display()

    def clear_queue(self):
        self.is_downloading = False
        self.current_download_index = None
        self.download_queue = []
        self.update_queue_display()

    def update_queue_display(self):
        items = []
        for item in self.download_queue:
            items.append((
                item["status"],
                item["progress"],
                item["size"],
                item["speed"],
                item["platform"],
                f"{item['format_note']} ({item['fps']}fps)"
            ))
        # Обновляем интерфейс в главном потоке
        self.gui.root.after(0, lambda: self.gui.update_queue(items))