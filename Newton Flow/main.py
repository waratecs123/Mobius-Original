import tkinter as tk
from gui import BeatPadGUI
import ctypes
import sys


def main():
    try:
        # Улучшаем масштабирование для высоких DPI дисплеев
        if hasattr(ctypes, 'windll'):
            ctypes.windll.shcore.SetProcessDpiAwareness(1)

        root = tk.Tk()
        root.title("Newton Flow Beat Pad")

        # Минимальный размер окна
        root.minsize(1200, 800)

        app = BeatPadGUI(root)

        # Центрируем окно
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        # Обработка закрытия окна
        root.protocol("WM_DELETE_WINDOW", app.on_closing)

        root.mainloop()

    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()