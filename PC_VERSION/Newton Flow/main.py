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
        root.title("Newton Flow Beat Pad - Professional Music Studio")

        # Автоматический полноэкранный режим
        root.attributes("-fullscreen", True)

        # Кнопка выхода из полноэкранного режима
        root.bind("<F11>", lambda e: root.attributes("-fullscreen",
                                                     not root.attributes("-fullscreen")))
        root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

        app = BeatPadGUI(root)

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