import tkinter as tk
from gui import JobsArchiveApp
import os

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.bind('<Escape>', lambda e: None)
    root.bind('<F11>', lambda e: None)

    try:
        root.iconbitmap("jobs_archive_icon.ico")
    except:
        pass

    os.makedirs("downloads", exist_ok=True)
    app = JobsArchiveApp(root)
    root.mainloop()