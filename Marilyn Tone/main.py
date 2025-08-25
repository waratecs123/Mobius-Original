# main.py
from gui import MarilynToneApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()

    # Центрирование окна
    window_width = 1200
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    app = MarilynToneApp(root)
    root.mainloop()