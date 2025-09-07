# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Scale, Menu, colorchooser, scrolledtext
from PIL import Image, ImageTk, ImageDraw, ImageFont
import cv2
import os
import threading
import json
import numpy as np
from datetime import datetime, timedelta
import time
import pygame
from functions import VideoEditorFunctions
from models import VideoClip, AudioClip
import webbrowser


class LumiereCutPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Lumiere Cut Pro")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)

        # Fibonacci Scan цветовая палитра
        self.bg_color = "#0a0a1a"
        self.sidebar_color = "#12122a"
        self.card_color = "#1a1a3a"
        self.accent_color = "#6366f1"
        self.accent_light = "#818cf8"
        self.accent_dark = "#4f46e5"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#2d3748"
        self.hover_color = "#252547"
        self.success_color = "#10b981"
        self.warning_color = "#f59e0b"
        self.error_color = "#ef4444"

        # Цвета дорожек (Fibonacci sequence inspired)
        self.track_colors = ["#1e1e3f", "#252547", "#2a2a4f", "#2f2f57", "#34345f"]
        self.audio_track_colors = ["#2a2a3a", "#252532", "#20202a"]

        # Шрифты Fibonacci
        self.title_font = ('SF Pro Display', 24, 'bold')
        self.app_font = ('SF Pro Text', 14)
        self.button_font = ('SF Pro Text', 13)
        self.small_font = ('SF Pro Text', 12)
        self.mono_font = ('SF Mono', 11)

        # Настройка окна
        self.root.configure(bg=self.bg_color)
        self.setup_styles()

        # Инициализация функционала
        self.functions = VideoEditorFunctions()
        self.current_frame_image = None
        self.preview_frame_image = None
        self.timeline_images = []
        self.dragging = False
        self.drag_start_x = 0
        self.selected_clip = None
        self.zoom_level = 1.0
        self.is_playing = False
        self.playback_thread = None

        self.setup_ui()
        self.create_menu()
        self.setup_keyboard_shortcuts()
        self.create_context_menus()

        # Автосохранение
        self.setup_auto_save()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color, font=self.app_font)
        style.configure('TButton', font=self.button_font, padding=6)
        style.configure('Accent.TButton', background=self.accent_color, foreground='white')
        style.configure('Secondary.TButton', background=self.card_color, foreground=self.text_color)
        style.configure('TEntry', fieldbackground=self.card_color, foreground=self.text_color)
        style.configure('TCombobox', fieldbackground=self.card_color, foreground=self.text_color)
        style.configure('TScale', background=self.bg_color, troughcolor=self.card_color)
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.sidebar_color, foreground=self.text_color, padding=[15, 5])
        style.configure('TCanvas', background=self.bg_color)

    def setup_ui(self):
        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Верхняя панель инструментов
        self.create_toolbar(main_container)

        # Основная область
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Левая боковая панель
        left_sidebar = ttk.Frame(content_frame, width=300, style='TFrame')
        left_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_sidebar.pack_propagate(False)

        self.create_media_library(left_sidebar)
        self.create_effects_panel(left_sidebar)

        # Центральная область
        center_frame = ttk.Frame(content_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Область предпросмотра
        preview_frame = ttk.LabelFrame(center_frame, text="Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.preview_canvas = tk.Canvas(preview_frame, bg=self.bg_color, highlightthickness=0)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)

        # Панель управления воспроизведением
        self.create_playback_controls(center_frame)

        # Временная шкала
        timeline_frame = ttk.LabelFrame(center_frame, text="Timeline", padding=10)
        timeline_frame.pack(fill=tk.BOTH, expand=False)
        timeline_frame.configure(height=300)

        self.create_timeline(timeline_frame)

        # Правая боковая панель
        right_sidebar = ttk.Frame(content_frame, width=300, style='TFrame')
        right_sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_sidebar.pack_propagate(False)

        self.create_properties_panel(right_sidebar)
        self.create_export_panel(right_sidebar)

    def create_toolbar(self, parent):
        toolbar = ttk.Frame(parent, height=60, style='TFrame')
        toolbar.pack(fill=tk.X, pady=(0, 5))
        toolbar.pack_propagate(False)

        # Логотип и название
        logo_frame = ttk.Frame(toolbar)
        logo_frame.pack(side=tk.LEFT, padx=20)

        logo_label = ttk.Label(logo_frame, text="Lumiere Cut", font=self.title_font,
                               foreground=self.accent_light)
        logo_label.pack()

        # Кнопки управления проектом
        project_buttons = ttk.Frame(toolbar)
        project_buttons.pack(side=tk.LEFT, padx=20)

        ttk.Button(project_buttons, text="New Project", command=self.new_project,
                   style='Secondary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(project_buttons, text="Open", command=self.open_project,
                   style='Secondary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(project_buttons, text="Save", command=self.save_project,
                   style='Secondary.TButton').pack(side=tk.LEFT, padx=2)

        # Кнопки редактирования
        edit_buttons = ttk.Frame(toolbar)
        edit_buttons.pack(side=tk.LEFT, padx=20)

        ttk.Button(edit_buttons, text="Undo", command=self.undo,
                   style='Secondary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(edit_buttons, text="Redo", command=self.redo,
                   style='Secondary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(edit_buttons, text="Cut", command=self.cut_clip,
                   style='Secondary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(edit_buttons, text="Split", command=self.split_clip,
                   style='Secondary.TButton').pack(side=tk.LEFT, padx=2)

        # Информация о проекте
        info_frame = ttk.Frame(toolbar)
        info_frame.pack(side=tk.RIGHT, padx=20)

        self.project_info = ttk.Label(info_frame, text="No Project | 1920x1080 | 30fps",
                                      font=self.small_font, foreground=self.secondary_text)
        self.project_info.pack()

    def create_media_library(self, parent):
        media_frame = ttk.LabelFrame(parent, text="Media Library", padding=10)
        media_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Кнопки импорта
        import_buttons = ttk.Frame(media_frame)
        import_buttons.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(import_buttons, text="Import Video", command=self.import_video,
                   style='Accent.TButton').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(import_buttons, text="Import Audio", command=self.import_audio,
                   style='Secondary.TButton').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Список медиа
        self.media_listbox = tk.Listbox(media_frame, bg=self.card_color, fg=self.text_color,
                                        selectbackground=self.accent_color, font=self.mono_font,
                                        borderwidth=0, highlightthickness=0)
        self.media_listbox.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(media_frame, orient=tk.VERTICAL, command=self.media_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.media_listbox.configure(yscrollcommand=scrollbar.set)

        self.media_listbox.bind('<Double-Button-1>', self.on_media_double_click)

    def create_effects_panel(self, parent):
        effects_frame = ttk.LabelFrame(parent, text="Effects & Transitions", padding=10)
        effects_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

        # Вкладки для эффектов и переходов
        notebook = ttk.Notebook(effects_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Эффекты видео
        video_effects = ttk.Frame(notebook, padding=5)
        notebook.add(video_effects, text="Video Effects")

        effects = ["Brightness", "Contrast", "Saturation", "Blur", "Sharpen", "Vignette"]
        for effect in effects:
            btn = ttk.Button(video_effects, text=effect, command=lambda e=effect: self.apply_effect(e),
                             style='Secondary.TButton')
            btn.pack(fill=tk.X, pady=2)

        # Переходы
        transitions = ttk.Frame(notebook, padding=5)
        notebook.add(transitions, text="Transitions")

        trans_types = ["Fade", "Slide", "Wipe", "Zoom", "Rotate"]
        for trans in trans_types:
            btn = ttk.Button(transitions, text=trans, command=lambda t=trans: self.add_transition(t),
                             style='Secondary.TButton')
            btn.pack(fill=tk.X, pady=2)

    def create_playback_controls(self, parent):
        controls_frame = ttk.Frame(parent, height=60)
        controls_frame.pack(fill=tk.X, pady=(5, 0))
        controls_frame.pack_propagate(False)

        # Ползунок времени
        self.time_slider = ttk.Scale(controls_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     command=self.on_time_slider_change)
        self.time_slider.pack(fill=tk.X, padx=20, pady=(10, 5))

        # Кнопки управления
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        ttk.Button(buttons_frame, text="⏮", command=self.go_to_start).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="⏪", command=self.step_backward).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="⏯", command=self.toggle_playback).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="⏩", command=self.step_forward).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="⏭", command=self.go_to_end).pack(side=tk.LEFT)

        # Информация о времени
        self.time_label = ttk.Label(buttons_frame, text="00:00:00 / 00:00:00",
                                    font=self.mono_font, foreground=self.secondary_text)
        self.time_label.pack(side=tk.RIGHT)

    def create_timeline(self, parent):
        # Заголовок дорожек
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X)

        ttk.Label(header_frame, text="Tracks", width=10).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Clips", width=20).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Область дорожек с прокруткой
        timeline_container = ttk.Frame(parent)
        timeline_container.pack(fill=tk.BOTH, expand=True)

        # Холст для дорожек
        self.timeline_canvas = tk.Canvas(timeline_container, bg=self.bg_color, highlightthickness=0)
        self.timeline_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(timeline_container, orient=tk.VERTICAL, command=self.timeline_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.timeline_canvas.configure(yscrollcommand=scrollbar.set)

        # Привязка событий
        self.timeline_canvas.bind("<Button-1>", self.on_timeline_click)
        self.timeline_canvas.bind("<B1-Motion>", self.on_timeline_drag)
        self.timeline_canvas.bind("<ButtonRelease-1>", self.on_timeline_release)
        self.timeline_canvas.bind("<MouseWheel>", self.on_timeline_scroll)

    def create_properties_panel(self, parent):
        props_frame = ttk.LabelFrame(parent, text="Properties", padding=10)
        props_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Вкладки свойств
        notebook = ttk.Notebook(props_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Свойства клипа
        clip_props = ttk.Frame(notebook, padding=5)
        notebook.add(clip_props, text="Clip")

        ttk.Label(clip_props, text="Name:").pack(anchor=tk.W)
        self.clip_name = ttk.Entry(clip_props)
        self.clip_name.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(clip_props, text="Duration:").pack(anchor=tk.W)
        self.clip_duration = ttk.Label(clip_props, text="00:00:00")
        self.clip_duration.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(clip_props, text="Speed:").pack(anchor=tk.W)
        self.speed_slider = ttk.Scale(clip_props, from_=0.25, to=4.0, orient=tk.HORIZONTAL)
        self.speed_slider.set(1.0)
        self.speed_slider.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(clip_props, text="Volume:").pack(anchor=tk.W)
        self.volume_slider = ttk.Scale(clip_props, from_=0, to=100, orient=tk.HORIZONTAL)
        self.volume_slider.set(100)
        self.volume_slider.pack(fill=tk.X, pady=(0, 10))

        # Свойства проекта
        project_props = ttk.Frame(notebook, padding=5)
        notebook.add(project_props, text="Project")

        ttk.Label(project_props, text="Project Name:").pack(anchor=tk.W)
        self.project_name = ttk.Entry(project_props)
        self.project_name.pack(fill=tk.X, pady=(0, 10))
        self.project_name.bind("<Return>", self.rename_project)

        ttk.Label(project_props, text="Resolution:").pack(anchor=tk.W)
        self.resolution_var = tk.StringVar(value="1920x1080")
        res_combo = ttk.Combobox(project_props, textvariable=self.resolution_var,
                                 values=["1280x720", "1920x1080", "2560x1440", "3840x2160"])
        res_combo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(project_props, text="FPS:").pack(anchor=tk.W)
        self.fps_var = tk.StringVar(value="30")
        fps_combo = ttk.Combobox(project_props, textvariable=self.fps_var,
                                 values=["24", "25", "30", "50", "60"])
        fps_combo.pack(fill=tk.X, pady=(0, 10))

    def create_export_panel(self, parent):
        export_frame = ttk.LabelFrame(parent, text="Export", padding=10)
        export_frame.pack(fill=tk.BOTH, expand=False)

        ttk.Label(export_frame, text="Format:").pack(anchor=tk.W)
        self.format_var = tk.StringVar(value="MP4")
        format_combo = ttk.Combobox(export_frame, textvariable=self.format_var,
                                    values=["MP4", "AVI", "MOV", "WMV"])
        format_combo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(export_frame, text="Quality:").pack(anchor=tk.W)
        self.quality_var = tk.StringVar(value="High")
        quality_combo = ttk.Combobox(export_frame, textvariable=self.quality_var,
                                     values=["Low", "Medium", "High", "Ultra"])
        quality_combo.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(export_frame, text="Export Video", command=self.export_video,
                   style='Accent.TButton').pack(fill=tk.X, pady=10)

        self.export_progress = ttk.Progressbar(export_frame, mode='determinate')
        self.export_progress.pack(fill=tk.X, pady=(0, 5))

        self.export_status = ttk.Label(export_frame, text="", foreground=self.secondary_text)
        self.export_status.pack()

    def create_menu(self):
        menubar = Menu(self.root)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_command(label="Save As", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Import Video", command=self.import_video)
        file_menu.add_command(label="Import Audio", command=self.import_audio)
        file_menu.add_separator()
        file_menu.add_command(label="Export", command=self.export_video)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_clip)
        edit_menu.add_command(label="Copy", command=self.copy_clip)
        edit_menu.add_command(label="Paste", command=self.paste_clip)
        edit_menu.add_command(label="Delete", command=self.delete_clip)
        edit_menu.add_separator()
        edit_menu.add_command(label="Split Clip", command=self.split_clip)
        edit_menu.add_command(label="Trim Clip", command=self.trim_clip)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View menu
        view_menu = Menu(menubar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom)
        menubar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menubar)

    def setup_keyboard_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.new_project())
        self.root.bind('<Control-o>', lambda e: self.open_project())
        self.root.bind('<Control-s>', lambda e: self.save_project())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut_clip())
        self.root.bind('<Control-c>', lambda e: self.copy_clip())
        self.root.bind('<Control-v>', lambda e: self.paste_clip())
        self.root.bind('<Delete>', lambda e: self.delete_clip())
        self.root.bind('<space>', lambda e: self.toggle_playback())
        self.root.bind('<Left>', lambda e: self.step_backward())
        self.root.bind('<Right>', lambda e: self.step_forward())

    def create_context_menus(self):
        self.timeline_menu = Menu(self.root, tearoff=0)
        self.timeline_menu.add_command(label="Split", command=self.split_clip)
        self.timeline_menu.add_command(label="Trim", command=self.trim_clip)
        self.timeline_menu.add_command(label="Delete", command=self.delete_clip)
        self.timeline_menu.add_separator()
        self.timeline_menu.add_command(label="Properties", command=self.show_clip_properties)

    def setup_auto_save(self):
        def auto_save_task():
            while True:
                time.sleep(300)  # 5 минут
                if hasattr(self, 'functions') and self.functions.project.file_path:
                    self.functions.auto_save()

        auto_save_thread = threading.Thread(target=auto_save_task, daemon=True)
        auto_save_thread.start()

    # Event handlers and functional methods
    def new_project(self):
        # Создание диалога для нового проекта
        dialog = tk.Toplevel(self.root)
        dialog.title("New Project")
        dialog.geometry("400x300")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Project Name:", font=self.app_font).pack(pady=10)
        name_entry = ttk.Entry(dialog, font=self.app_font)
        name_entry.pack(fill=tk.X, padx=20, pady=(0, 20))
        name_entry.insert(0, "New Project")

        ttk.Label(dialog, text="Resolution:", font=self.app_font).pack()
        res_var = tk.StringVar(value="1920x1080")
        res_combo = ttk.Combobox(dialog, textvariable=res_var,
                                 values=["1280x720", "1920x1080", "2560x1440", "3840x2160"])
        res_combo.pack(fill=tk.X, padx=20, pady=(0, 20))

        ttk.Label(dialog, text="Frame Rate:", font=self.app_font).pack()
        fps_var = tk.StringVar(value="30")
        fps_combo = ttk.Combobox(dialog, textvariable=fps_var,
                                 values=["24", "25", "30", "50", "60"])
        fps_combo.pack(fill=tk.X, padx=20, pady=(0, 20))

        def create_project():
            name = name_entry.get()
            resolution = tuple(map(int, res_var.get().split('x')))
            fps = float(fps_var.get())

            success, message = self.functions.new_project(name, resolution, fps)
            if success:
                self.update_project_info()
                dialog.destroy()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

        ttk.Button(dialog, text="Create Project", command=create_project,
                   style='Accent.TButton').pack(pady=20)

    def open_project(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".lumiere",
            filetypes=[("Lumiere Projects", "*.lumiere"), ("All files", "*.*")]
        )
        if file_path:
            success, message = self.functions.load_project(file_path)
            if success:
                self.update_project_info()
                self.update_timeline()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def save_project(self):
        if not self.functions.project.file_path:
            self.save_project_as()
        else:
            success, message = self.functions.save_project()
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def save_project_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".lumiere",
            filetypes=[("Lumiere Projects", "*.lumiere"), ("All files", "*.*")]
        )
        if file_path:
            success, message = self.functions.save_project(file_path)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def import_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            success, message, thumbnail = self.functions.open_video(file_path)
            if success:
                self.media_listbox.insert(tk.END, message)
                messagebox.showinfo("Success", f"Video imported: {message}")
            else:
                messagebox.showerror("Error", message)

    def import_audio(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Audio files", "*.mp3 *.wav *.ogg *.flac *.aac"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            success, message = self.functions.add_audio_clip(file_path)
            if success:
                self.media_listbox.insert(tk.END, f"🎵 {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Audio imported: {message}")
            else:
                messagebox.showerror("Error", message)

    def on_media_double_click(self, event):
        selection = self.media_listbox.curselection()
        if selection:
            item = self.media_listbox.get(selection[0])
            # Добавляем медиа на временную шкалу
            if item.startswith("🎵"):
                success, message = self.functions.add_audio_clip(
                    self.functions.audio_clips[selection[0]].path
                )
            else:
                success, message = self.functions.add_to_timeline()

            if success:
                self.update_timeline()
            else:
                messagebox.showerror("Error", message)

    def update_project_info(self):
        project = self.functions.project
        info = f"{project.name} | {project.resolution[0]}x{project.resolution[1]} | {project.fps}fps"
        self.project_info.config(text=info)
        self.project_name.delete(0, tk.END)
        self.project_name.insert(0, project.name)

    def rename_project(self, event):
        new_name = self.project_name.get()
        self.functions.project.name = new_name
        self.update_project_info()

    def update_timeline(self):
        self.timeline_canvas.delete("all")
        # Здесь будет логика отрисовки дорожек и клипов
        self.draw_timeline()

    def draw_timeline(self):
        # Очистка холста
        self.timeline_canvas.delete("all")

        # Размеры и отступы
        track_height = 60
        header_height = 30
        time_scale_width = 100
        clip_height = 50
        padding = 10

        # Рисуем заголовок времени
        self.timeline_canvas.create_rectangle(0, 0, time_scale_width, header_height,
                                              fill=self.sidebar_color, outline=self.border_color)
        self.timeline_canvas.create_text(time_scale_width // 2, header_height // 2,
                                         text="Time", fill=self.text_color, font=self.small_font)

        # Рисуем дорожки
        for i, track in enumerate(self.functions.tracks):
            y = header_height + i * track_height

            # Фон дорожки
            self.timeline_canvas.create_rectangle(0, y, time_scale_width, y + track_height,
                                                  fill=self.track_colors[i % len(self.track_colors)],
                                                  outline=self.border_color)

            # Название дорожки
            self.timeline_canvas.create_text(time_scale_width // 2, y + track_height // 2,
                                             text=f"V{i + 1}", fill=self.text_color, font=self.small_font)

            # Клипы на дорожке
            for clip in track:
                clip_width = (clip.end_frame - clip.start_frame) * self.zoom_level
                x = time_scale_width + clip.position * self.zoom_level

                # Прямоугольник клипа
                self.timeline_canvas.create_rectangle(x, y + padding,
                                                      x + clip_width, y + track_height - padding,
                                                      fill=self.accent_color,
                                                      outline=self.accent_dark, width=2)

                # Название клипа
                clip_name = clip.name[:15] + "..." if len(clip.name) > 15 else clip.name
                self.timeline_canvas.create_text(x + clip_width // 2, y + track_height // 2,
                                                 text=clip_name, fill="white", font=self.small_font)

    def on_timeline_click(self, event):
        # Обработка клика на временной шкале
        pass

    def on_timeline_drag(self, event):
        # Обработка перетаскивания на временной шкале
        pass

    def on_timeline_release(self, event):
        # Обработка отпускания кнопки мыши на временной шкале
        pass

    def on_timeline_scroll(self, event):
        # Масштабирование временной шкалы
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.update_timeline()

    def zoom_out(self):
        self.zoom_level /= 1.2
        self.update_timeline()

    def reset_zoom(self):
        self.zoom_level = 1.0
        self.update_timeline()

    def toggle_playback(self):
        if self.is_playing:
            self.is_playing = False
        else:
            self.is_playing = True
            self.playback_thread = threading.Thread(target=self.playback_loop, daemon=True)
            self.playback_thread.start()

    def playback_loop(self):
        while self.is_playing and self.functions.current_clip:
            frame = self.functions.get_frame(self.functions.current_frame)
            if frame is not None:
                self.update_preview(frame)
                self.functions.current_frame += 1
                time.sleep(1 / self.functions.fps)
            else:
                self.is_playing = False

    def update_preview(self, frame):
        # Конвертация кадра для отображения в Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((self.preview_canvas.winfo_width(), self.preview_canvas.winfo_height()),
                         Image.Resampling.LANCZOS)
        self.preview_image = ImageTk.PhotoImage(img)

        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_image)

    def go_to_start(self):
        self.functions.current_frame = 0
        self.update_preview_from_current_frame()

    def go_to_end(self):
        if self.functions.current_clip:
            self.functions.current_frame = self.functions.current_clip.total_frames - 1
            self.update_preview_from_current_frame()

    def step_forward(self):
        if self.functions.current_clip:
            self.functions.current_frame = min(self.functions.current_frame + 1,
                                               self.functions.current_clip.total_frames - 1)
            self.update_preview_from_current_frame()

    def step_backward(self):
        if self.functions.current_clip:
            self.functions.current_frame = max(self.functions.current_frame - 1, 0)
            self.update_preview_from_current_frame()

    def update_preview_from_current_frame(self):
        frame = self.functions.get_frame()
        if frame is not None:
            self.update_preview(frame)

    def on_time_slider_change(self, value):
        if self.functions.current_clip:
            frame_num = int(float(value) * self.functions.current_clip.total_frames / 100)
            self.functions.current_frame = frame_num
            self.update_preview_from_current_frame()

    def split_clip(self):
        if self.selected_clip:
            track_idx, clip_idx = self.selected_clip
            split_frame = self.functions.current_frame
            success, message = self.functions.split_clip(track_idx, clip_idx, split_frame)
            if success:
                self.update_timeline()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def trim_clip(self):
        if self.selected_clip:
            track_idx, clip_idx = self.selected_clip
            start_frame = 0  # Получаем из интерфейса
            end_frame = self.functions.current_clip.total_frames  # Получаем из интерфейса
            success, message = self.functions.trim_clip(track_idx, clip_idx, start_frame, end_frame)
            if success:
                self.update_timeline()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def cut_clip(self):
        if self.selected_clip:
            track_idx, clip_idx = self.selected_clip
            success, message = self.functions.remove_clip(track_idx, clip_idx)
            if success:
                self.update_timeline()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def copy_clip(self):
        if self.selected_clip:
            track_idx, clip_idx = self.selected_clip
            self.functions.copy_clip(track_idx, clip_idx)

    def paste_clip(self):
        if hasattr(self.functions, 'copied_clip'):
            track_idx = 0  # Выбранная дорожка
            position = 0  # Позиция на дорожке
            success, message = self.functions.paste_clip(track_idx, position)
            if success:
                self.update_timeline()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def delete_clip(self):
        if self.selected_clip:
            track_idx, clip_idx = self.selected_clip
            success, message = self.functions.remove_clip(track_idx, clip_idx)
            if success:
                self.update_timeline()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def apply_effect(self, effect_name):
        if self.selected_clip:
            track_idx, clip_idx = self.selected_clip
            success, message = self.functions.apply_effect(track_idx, clip_idx, effect_name)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def add_transition(self, transition_type):
        if self.selected_clip:
            track_idx, clip_idx = self.selected_clip
            success, message = self.functions.add_transition(track_idx, clip_idx, transition_type)
            if success:
                self.update_timeline()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)

    def export_video(self):
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All files", "*.*")]
        )
        if output_path:
            format_type = self.format_var.get().lower()
            quality = self.quality_var.get()

            def export_thread():
                try:
                    success, message = self.functions.export_video(output_path, format_type, quality)
                    if success:
                        self.export_status.config(text="Export completed!")
                        messagebox.showinfo("Success", message)
                    else:
                        self.export_status.config(text="Export failed!")
                        messagebox.showerror("Error", message)
                except Exception as e:
                    self.export_status.config(text=f"Error: {str(e)}")
                    messagebox.showerror("Error", f"Export failed: {str(e)}")

            threading.Thread(target=export_thread, daemon=True).start()
            self.export_status.config(text="Exporting...")

    def undo(self):
        success, message = self.functions.undo()
        if success:
            self.update_timeline()
        else:
            messagebox.showinfo("Info", message)

    def redo(self):
        success, message = self.functions.redo()
        if success:
            self.update_timeline()
        else:
            messagebox.showinfo("Info", message)

    def show_clip_properties(self):
        if self.selected_clip:
            track_idx, clip_idx = self.selected_clip
            clip = self.functions.tracks[track_idx][clip_idx]

            dialog = tk.Toplevel(self.root)
            dialog.title("Clip Properties")
            dialog.geometry("400x300")
            dialog.configure(bg=self.bg_color)

            ttk.Label(dialog, text=f"Name: {clip.name}").pack(pady=5)
            ttk.Label(dialog, text=f"Duration: {clip.duration}").pack(pady=5)
            ttk.Label(dialog, text=f"Start Frame: {clip.start_frame}").pack(pady=5)
            ttk.Label(dialog, text=f"End Frame: {clip.end_frame}").pack(pady=5)
            ttk.Label(dialog, text=f"Position: {clip.position}").pack(pady=5)

    def run(self):
        self.root.mainloop()