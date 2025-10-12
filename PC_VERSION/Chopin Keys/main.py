# main.py
import tkinter as tk
from gui import ModernChopinKeysGUI

def main():
    root = tk.Tk()
    app = ModernChopinKeysGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()