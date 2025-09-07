import tkinter as tk
from gui import JobsArchiveApp
import os

if __name__ == "__main__":
    root = tk.Tk()

    # Полноэкранный режим при запуске
    root.attributes('-fullscreen', True)

    # Блокировка клавиш выхода из полноэкранного режима
    root.bind('<Escape>', lambda e: None)
    root.bind('<F11>', lambda e: None)

    # Иконка приложения
    try:
        root.iconbitmap("jobs_archive_icon.ico")
    except:
        pass

    # Создаем папку для загрузок, если её нет
    os.makedirs("downloads", exist_ok=True)

    app = JobsArchiveApp(root)
    root.mainloop()