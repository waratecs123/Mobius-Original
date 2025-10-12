import tkinter as tk
from gui import PaintApp

def main():
    root = tk.Tk()
    app = PaintApp(root)
    app.run()

if __name__ == "__main__":
    main()