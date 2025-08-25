import tkinter as tk
from gui import JobsArchiveApp
import os

if __name__ == "__main__":
    root = tk.Tk()

    # Устанавливаем полноэкранный режим по умолчанию
    root.attributes('-fullscreen', True)

    # Центрирование окна (на случай выхода из полноэкранного режима)
    window_width = 1200
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Иконка приложения
    try:
        root.iconbitmap("jobs_archive_icon.ico")
    except:
        pass

    # Создаем папку для загрузок, если её нет
    os.makedirs("downloads", exist_ok=True)

    app = JobsArchiveApp(root)
    root.mainloop()