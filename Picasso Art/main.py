# [file name]: main.py
import tkinter as tk
from gui import PaintApp

if __name__ == "__main__":
    root = tk.Tk()
    # Устанавливаем полноэкранный режим
    root.attributes('-fullscreen', True)

    app = PaintApp(root)
    root.mainloop()