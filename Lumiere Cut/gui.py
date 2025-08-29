import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Scale
from PIL import Image, ImageTk
import cv2
import os
import threading
from functions import VideoEditorFunctions
from utils import format_time, VideoPlayer, PreviewPlayer


class VideoEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lumiere Cut")

        # Полноэкранный режим
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#0a0a0a')

        # Цветовая палитра темной темы
        self.bg_color = "#0a0a0a"
        self.sidebar_color = "#151515"
        self.card_color = "#1e1e1e"
        self.accent_color = "#4870ff"
        self.text_color = "#f0f0f0"
        self.secondary_text = "#909090"
        self.track_colors = ["#2a2a2a", "#252525", "#202020"]

        self.functions = VideoEditorFunctions()
        self.player = VideoPlayer(self.update_source_frame)
        self.preview_player = PreviewPlayer(self.update_preview_frame, self.functions)

        self.setup_ui()
        self.create_menu()

        # Кнопка выхода из полноэкранного режима
        self.bind_exit_fullscreen()

        # Переменные для перетаскивания
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.current_drag_clip = None

    def bind_exit_fullscreen(self):
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen())

    def toggle_fullscreen(self):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def setup_ui(self):
        # Настройка стилей
        style = ttk.Style()
        style.theme_use('clam')

        # Конфигурация стилей
        style.configure("TFrame", background=self.bg_color)
        style.configure("Sidebar.TFrame", background=self.sidebar_color)
        style.configure("Card.TFrame", background=self.card_color)
        style.configure("TLabel", background=self.card_color, foreground=self.text_color, font=('Segoe UI', 11))
        style.configure("Title.TLabel", font=('Segoe UI', 16, 'bold'))
        style.configure("Secondary.TLabel", foreground=self.secondary_text)
        style.configure("TButton", background=self.accent_color, foreground=self.text_color)
        style.map("TButton", background=[('active', '#3a5bd9')])

        # Главный контейнер
        main_container = ttk.Frame(self.root, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Сайдбар
        self.setup_sidebar(main_container)

        # Основная область
        self.setup_main_area(main_container)

    def setup_sidebar(self, parent):
        sidebar = ttk.Frame(parent, width=280, style="Sidebar.TFrame")
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Логотип и заголовок
        logo_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        logo_frame.pack(pady=(30, 40), padx=20, fill=tk.X)

        logo_canvas = tk.Canvas(logo_frame, bg=self.sidebar_color, width=40, height=40,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side=tk.LEFT)
        logo_canvas.create_oval(5, 5, 35, 35, fill=self.accent_color, outline="")
        logo_canvas.create_text(20, 20, text="L", font=('Segoe UI', 16, 'bold'), fill="#ffffff")

        tk.Label(logo_frame, text="Lumiere Cut", font=('Segoe UI', 14, 'bold'),
                 bg=self.sidebar_color, fg=self.text_color).pack(side=tk.LEFT, padx=12)

        # Инструменты
        tools_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        tools_frame.pack(fill=tk.X, padx=15, pady=20)

        tools = [
            ("📁 Добавить видео", self.open_video),
            ("▶ Исходное видео", self.play_video),
            ("⏸ Пауза", self.pause_video),
            ("⏹ Стоп", self.stop_video),
            ("🎬 Превью монтажа", self.play_preview),
            ("⏸ Пауза превью", self.pause_preview),
            ("💾 Экспорт", self.export_video),
            ("➕ Добавить дорожку", self.add_track),
            ("➖ Удалить дорожку", self.remove_track)
        ]

        for tool_text, tool_command in tools:
            btn = tk.Button(tools_frame, text=tool_text, font=('Segoe UI', 12),
                            bg=self.sidebar_color, fg=self.text_color, bd=0,
                            activebackground="#252525", activeforeground=self.accent_color,
                            padx=20, pady=12, anchor="w", command=tool_command)
            btn.pack(fill=tk.X, pady=2)

    def setup_main_area(self, parent):
        main_area = ttk.Frame(parent, style="TFrame")
        main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Верхняя панель с превью
        preview_frame = ttk.Frame(main_area, style="Card.TFrame")
        preview_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        # Исходное видео
        source_frame = ttk.LabelFrame(preview_frame, text="Исходное видео", style="Card.TFrame")
        source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.source_preview_label = tk.Label(source_frame, text="Откройте видео для начала работы",
                                             background='#252525', foreground=self.secondary_text,
                                             height=15, font=('Segoe UI', 10))
        self.source_preview_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Основное превью
        main_preview_frame = ttk.LabelFrame(preview_frame, text="Превью монтажа", style="Card.TFrame")
        main_preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.main_preview_label = tk.Label(main_preview_frame, text="Превью монтажа",
                                           background='#252525', foreground=self.secondary_text,
                                           height=15, font=('Segoe UI', 10))
        self.main_preview_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Таймлайн
        timeline_frame = ttk.Frame(main_area, style="Card.TFrame")
        timeline_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Ползунок времени исходного видео
        time_control_frame = ttk.Frame(timeline_frame, style="Card.TFrame")
        time_control_frame.pack(fill=tk.X, padx=20, pady=(10, 5))

        ttk.Label(time_control_frame, text="Исходное видео:", style="TLabel").pack(side=tk.LEFT)

        self.time_slider = ttk.Scale(time_control_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.time_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.time_slider.bind("<ButtonRelease-1>", self.on_slider_change)

        # Временные метки
        time_labels_frame = ttk.Frame(time_control_frame, style="Card.TFrame")
        time_labels_frame.pack(side=tk.RIGHT)

        self.current_time_label = ttk.Label(time_labels_frame, text="00:00:00", style="Secondary.TLabel")
        self.current_time_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(time_labels_frame, text="/", style="Secondary.TLabel").pack(side=tk.LEFT, padx=2)

        self.total_time_label = ttk.Label(time_labels_frame, text="00:00:00", style="Secondary.TLabel")
        self.total_time_label.pack(side=tk.LEFT, padx=5)

        # Ползунок превью монтажа
        preview_control_frame = ttk.Frame(timeline_frame, style="Card.TFrame")
        preview_control_frame.pack(fill=tk.X, padx=20, pady=(5, 10))

        ttk.Label(preview_control_frame, text="Превью монтажа:", style="TLabel").pack(side=tk.LEFT)

        self.preview_slider = ttk.Scale(preview_control_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.preview_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.preview_slider.bind("<ButtonRelease-1>", self.on_preview_slider_change)

        self.preview_time_label = ttk.Label(preview_control_frame, text="00:00:00", style="Secondary.TLabel")
        self.preview_time_label.pack(side=tk.RIGHT, padx=5)

        # Контейнер для дорожек с прокруткой
        track_container = ttk.Frame(timeline_frame, style="Card.TFrame")
        track_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Холст для дорожек
        self.timeline_canvas = tk.Canvas(track_container, bg='#1a1a1a', height=250)
        self.timeline_canvas.pack(fill=tk.BOTH, expand=True)

        # Привязка событий перетаскивания
        self.timeline_canvas.bind("<ButtonPress-1>", self.on_timeline_click)
        self.timeline_canvas.bind("<B1-Motion>", self.on_timeline_drag)
        self.timeline_canvas.bind("<ButtonRelease-1>", self.on_timeline_release)

        # Библиотека медиа
        media_frame = ttk.LabelFrame(main_area, text="Библиотека медиа", style="Card.TFrame")
        media_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Прокрутка для библиотеки медиа
        media_scrollbar = ttk.Scrollbar(media_frame)
        media_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.media_canvas = tk.Canvas(media_frame, bg='#1a1a1a', yscrollcommand=media_scrollbar.set)
        self.media_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        media_scrollbar.config(command=self.media_canvas.yview)

        # Фрейм для медиа элементов
        self.media_frame = ttk.Frame(self.media_canvas, style="Card.TFrame")
        self.media_canvas.create_window((0, 0), window=self.media_frame, anchor="nw")

    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.sidebar_color, fg=self.text_color)

        file_menu = tk.Menu(menubar, tearoff=0, bg=self.sidebar_color, fg=self.text_color)
        file_menu.add_command(label="Открыть видео", command=self.open_video)
        file_menu.add_command(label="Экспорт", command=self.export_video)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.sidebar_color, fg=self.text_color)
        edit_menu.add_command(label="Обрезать", command=self.trim_video)
        edit_menu.add_command(label="Разделить", command=self.split_video)

        menubar.add_cascade(label="Файл", menu=file_menu)
        menubar.add_cascade(label="Редактировать", menu=edit_menu)

        self.root.config(menu=menubar)

    def update_source_frame(self, frame_num):
        self.functions.current_frame = frame_num
        self.show_source_frame(frame_num)
        self.time_slider.config(to=self.functions.total_frames)
        self.time_slider.set(frame_num)

    def update_preview_frame(self, frame_num):
        self.show_preview_frame(frame_num)
        max_duration = self.calculate_max_duration()
        if max_duration > 0:
            self.preview_slider.config(to=max_duration)
            self.preview_slider.set(frame_num)
            current_time = frame_num / self.functions.fps
            self.preview_time_label.config(text=format_time(current_time))

    def calculate_max_duration(self):
        max_duration = 0
        for track in self.functions.tracks:
            for clip in track:
                clip_end = clip.position + (clip.end_frame - clip.start_frame)
                if clip_end > max_duration:
                    max_duration = clip_end
        return max_duration

    def show_source_frame(self, frame_num=None):
        frame = self.functions.get_frame(frame_num)
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((380, 240), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            self.source_preview_label.configure(image=img_tk, text="")
            self.source_preview_label.image = img_tk

            # Обновляем время
            current_time = self.functions.current_frame / self.functions.fps
            total_time = self.functions.total_frames / self.functions.fps
            current_str = format_time(current_time)
            total_str = format_time(total_time)
            self.current_time_label.config(text=current_str)
            self.total_time_label.config(text=total_str)

    def show_preview_frame(self, frame_num=None):
        frame = self.functions.get_preview_frame(frame_num)
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((380, 240), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            self.main_preview_label.configure(image=img_tk, text="")
            self.main_preview_label.image = img_tk

    def open_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv")]
        )

        if file_path:
            success, result, thumbnail = self.functions.open_video(file_path)
            if success:
                self.add_media_to_library(result, thumbnail, file_path)
                self.show_source_frame()
            else:
                messagebox.showerror("Ошибка", result)

    def add_media_to_library(self, name, thumbnail, file_path):
        media_item = ttk.Frame(self.media_frame, style="Card.TFrame")
        media_item.pack(fill=tk.X, pady=5, padx=5)

        # Контейнер для превью
        preview_container = ttk.Frame(media_item, style="Card.TFrame")
        preview_container.pack(fill=tk.X, padx=5, pady=5)

        # Превью
        if thumbnail is not None:
            img = Image.fromarray(cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB))
            img = img.resize((120, 70), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            preview_label = tk.Label(preview_container, image=img_tk, background='#2a2a2a')
            preview_label.image = img_tk
            preview_label.pack(side=tk.LEFT, padx=(0, 10))
        else:
            preview_label = tk.Label(preview_container, text="No preview", background='#2a2a2a',
                                     width=15, height=5, foreground='white')
            preview_label.pack(side=tk.LEFT, padx=(0, 10))

        # Информация и кнопки
        info_frame = ttk.Frame(preview_container, style="Card.TFrame")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Название файла
        name_label = tk.Label(info_frame, text=name, background='#2a2a2a',
                              foreground='white', font=('Segoe UI', 10))
        name_label.pack(anchor="w")

        # Кнопка добавления на таймлайн
        btn_frame = ttk.Frame(info_frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        add_btn = tk.Button(btn_frame, text="Добавить на дорожку",
                            bg=self.accent_color, fg="white", font=('Segoe UI', 9),
                            command=lambda f=file_path: self.add_selected_to_timeline(f))
        add_btn.pack(side=tk.LEFT)

        # Обновляем scrollregion
        self.media_frame.update_idletasks()
        self.media_canvas.configure(scrollregion=self.media_canvas.bbox("all"))

    def add_selected_to_timeline(self, file_path):
        for clip in self.functions.video_clips:
            if clip.path == file_path:
                self.functions.set_current_clip(clip)
                success, message = self.functions.add_to_timeline()
                if success:
                    self.draw_timeline()
                else:
                    messagebox.showerror("Ошибка", message)
                break

    def play_video(self):
        if self.functions.current_clip:
            self.time_slider.config(to=self.functions.total_frames - 1)
            self.player.play(self.functions.current_frame,
                             self.functions.total_frames,
                             self.functions.fps)

    def pause_video(self):
        self.player.pause()

    def stop_video(self):
        self.player.stop()
        self.functions.current_frame = 0
        self.show_source_frame(0)
        self.time_slider.set(0)

    def play_preview(self):
        max_duration = self.calculate_max_duration()
        if max_duration > 0:
            self.preview_slider.config(to=max_duration - 1)
            current_frame = int(self.preview_slider.get())
            self.preview_player.play(current_frame, max_duration, self.functions.fps)

    def pause_preview(self):
        self.preview_player.pause()

    def on_slider_change(self, event):
        try:
            frame_pos = int(float(self.time_slider.get()))
            if 0 <= frame_pos < self.functions.total_frames:
                self.functions.current_frame = frame_pos
                self.show_source_frame(frame_pos)
        except:
            pass

    def on_preview_slider_change(self, event):
        try:
            frame_pos = int(float(self.preview_slider.get()))
            self.show_preview_frame(frame_pos)
        except:
            pass

    def add_track(self):
        track_index = self.functions.add_track()
        messagebox.showinfo("Успех", f"Добавлена дорожка #{track_index + 1}")
        self.draw_timeline()

    def remove_track(self):
        if len(self.functions.tracks) > 1:
            success, message = self.functions.remove_track(len(self.functions.tracks) - 1)
            if success:
                self.draw_timeline()
            messagebox.showinfo("Информация", message)
        else:
            messagebox.showinfo("Информация", "Нельзя удалить последнюю дорожку")

    def draw_timeline(self):
        self.timeline_canvas.delete("all")

        track_height = 80
        timeline_width = 2000

        for i, track in enumerate(self.functions.tracks):
            y_pos = i * track_height

            # Рисуем фон дорожки
            track_color = self.track_colors[i % len(self.track_colors)]
            self.timeline_canvas.create_rectangle(0, y_pos, timeline_width, y_pos + track_height,
                                                  fill=track_color, outline="#444444", width=1)

            # Подписываем дорожку
            self.timeline_canvas.create_text(20, y_pos + track_height / 2,
                                             text=f"Дорожка {i + 1}", fill="white",
                                             font=('Segoe UI', 10), anchor="w")

            # Рисуем клипы на дорожке
            for j, clip in enumerate(track):
                clip_width = 120
                x_pos = clip.position * 2  # Масштабируем позицию для визуализации

                # Превью клипа
                if hasattr(clip, 'thumbnail') and clip.thumbnail is not None:
                    thumb_img = Image.fromarray(cv2.cvtColor(clip.thumbnail, cv2.COLOR_BGR2RGB))
                    thumb_img = thumb_img.resize((100, 60), Image.Resampling.LANCZOS)
                    thumb_tk = ImageTk.PhotoImage(thumb_img)

                    # Сохраняем ссылку на изображение
                    if not hasattr(self, 'timeline_images'):
                        self.timeline_images = []
                    self.timeline_images.append(thumb_tk)

                    self.timeline_canvas.create_image(x_pos + 10, y_pos + 10,
                                                      image=thumb_tk, anchor="nw")

                # Контур клипа
                clip_rect = self.timeline_canvas.create_rectangle(
                    x_pos, y_pos, x_pos + clip_width, y_pos + track_height,
                    fill="#3a3a3a", outline=self.accent_color, width=2
                )

                # Название файла
                file_name = os.path.basename(clip.path)
                self.timeline_canvas.create_text(
                    x_pos + clip_width / 2, y_pos + track_height - 15,
                    text=file_name[:12] + "..." if len(file_name) > 12 else file_name,
                    fill="white", font=("Segoe UI", 8)
                )

                # Время клипа
                duration = (clip.end_frame - clip.start_frame) / clip.fps
                self.timeline_canvas.create_text(
                    x_pos + clip_width / 2, y_pos + 15,
                    text=format_time(duration),
                    fill="white", font=("Segoe UI", 8)
                )

                # Сохраняем информацию о клипе для обработки событий
                self.timeline_canvas.addtag_withtag(f"clip_{i}_{j}", clip_rect)

    def on_timeline_click(self, event):
        # Находим, по какому клипу кликнули
        items = self.timeline_canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in items:
            tags = self.timeline_canvas.gettags(item)
            for tag in tags:
                if tag.startswith("clip_"):
                    parts = tag.split("_")
                    track_idx = int(parts[1])
                    clip_idx = int(parts[2])

                    self.dragging = True
                    self.drag_start_x = event.x
                    self.drag_start_y = event.y
                    self.current_drag_clip = (track_idx, clip_idx)
                    return

    def on_timeline_drag(self, event):
        if self.dragging and self.current_drag_clip:
            track_idx, clip_idx = self.current_drag_clip
            if 0 <= track_idx < len(self.functions.tracks):
                if 0 <= clip_idx < len(self.functions.tracks[track_idx]):
                    clip = self.functions.tracks[track_idx][clip_idx]

                    # Вычисляем новую позицию
                    new_position = max(0, (event.x - 50) // 2)  # Масштабируем обратно

                    # Обновляем позицию клипа
                    self.functions.update_clip_position(track_idx, clip_idx, new_position)

                    # Перерисовываем таймлайн
                    self.draw_timeline()

    def on_timeline_release(self, event):
        self.dragging = False
        self.current_drag_clip = None

    def export_video(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All files", "*.*")]
        )

        if file_path:
            progress = tk.Toplevel(self.root)
            progress.title("Экспорт видео")
            progress.geometry("300x120")
            progress.configure(bg=self.bg_color)
            progress.resizable(False, False)

            # Центрирование окна
            progress.transient(self.root)
            progress.grab_set()

            progress_label = ttk.Label(progress, text="Экспорт видео...", style="TLabel")
            progress_label.pack(pady=10)

            progress_bar = ttk.Progressbar(progress, mode='determinate')
            progress_bar.pack(fill=tk.X, padx=20, pady=10)

            def update_progress(percent):
                progress_bar['value'] = percent
                progress_label.config(text=f"Экспорт: {int(percent)}%")
                if percent >= 100:
                    progress.destroy()

            def export_thread():
                success, result = self.functions.export_video(file_path, update_progress)
                if success:
                    messagebox.showinfo("Успех", result)
                else:
                    messagebox.showerror("Ошибка", result)

            threading.Thread(target=export_thread, daemon=True).start()

    def trim_video(self):
        messagebox.showinfo("Информация", "Функция обрезки в разработке")

    def split_video(self):
        messagebox.showinfo("Информация", "Функция разделения в разработке")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoEditorGUI(root)
    root.mainloop()