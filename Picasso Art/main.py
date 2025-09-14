import tkinter as tk
from gui import PaintApp

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    app = PaintApp(root)
    app.run()