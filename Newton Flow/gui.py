import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk


class NewtonFlowGUI:
    def __init__(self, root, pad_handler, sample_handler, midi_handler):
        self.root = root
        self.root.title("Newton Flow BeatPad")
        self.root.geometry("800x600")

        self.pad_handler = pad_handler
        self.sample_handler = sample_handler
        self.midi_handler = midi_handler

        self.setup_ui()

    def setup_ui(self):
        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Фреймы
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Пэды (4x4 по умолчанию)
        self.pad_frame = ctk.CTkFrame(self.main_frame)
        self.pad_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.pads = []
        self.setup_pad_grid(4, 4)  # По умолчанию 4x4

        # Панель управления
        self.control_frame = ctk.CTkFrame(self.main_frame, width=200)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        # Элементы управления
        self.grid_size_label = ctk.CTkLabel(self.control_frame, text="Grid Size:")
        self.grid_size_label.pack(pady=5)

        self.grid_size = ctk.CTkOptionMenu(self.control_frame, values=["4x4", "8x8", "Custom"])
        self.grid_size.pack(pady=5)
        self.grid_size.set("4x4")

        self.load_sample_btn = ctk.CTkButton(self.control_frame, text="Load Sample", command=self.load_sample)
        self.load_sample_btn.pack(pady=5)

        self.record_btn = ctk.CTkButton(self.control_frame, text="Record Jam", command=self.record_jam)
        self.record_btn.pack(pady=5)

        self.midi_toggle = ctk.CTkSwitch(self.control_frame, text="MIDI Output")
        self.midi_toggle.pack(pady=5)

        # Статус бар
        self.status_bar = ctk.CTkLabel(self.root, text="Ready", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=10, pady=5)

    def setup_pad_grid(self, rows, cols):
        # Очищаем старые пэды
        for widget in self.pad_frame.winfo_children():
            widget.destroy()
        self.pads = []

        # Создаем новую сетку
        for row in range(rows):
            for col in range(cols):
                pad = ctk.CTkButton(
                    self.pad_frame,
                    text=f"{row * cols + col + 1}",
                    width=80,
                    height=80,
                    corner_radius=10,
                    command=lambda r=row, c=col: self.pad_handler(r, c)
                )
                pad.grid(row=row, column=col, padx=5, pady=5)
                self.pads.append(pad)

    def load_sample(self):
        # Здесь будет вызов функции загрузки сэмпла
        sample_path = self.sample_handler.load_sample_dialog()
        if sample_path:
            self.status_bar.configure(text=f"Loaded: {sample_path}")

    def record_jam(self):
        # Здесь будет вызов функции записи
        self.status_bar.configure(text="Recording...")
        output_file = self.midi_handler.record_jam()
        self.status_bar.configure(text=f"Saved to: {output_file}")

    def update_pad_color(self, pad_index, color):
        self.pads[pad_index].configure(fg_color=color)
        self.root.after(200, lambda: self.pads[pad_index].configure(fg_color="#2B2B2B"))