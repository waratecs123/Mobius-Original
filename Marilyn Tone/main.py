# main.py
from gui import MarilynToneApp
import tkinter as tk
import sys

if __name__ == "__main__":
    try:
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

    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        sys.exit(1)