# main.py remains unchanged
import tkinter as tk
from gui import TarantinoCatch

def main():
    root = tk.Tk()
    app = TarantinoCatch(root)

    def on_closing():
        app.on_closing()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()