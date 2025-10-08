import tkinter as tk
from gui import MondrianGridApp

def main():
    root = tk.Tk()
    app = MondrianGridApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()