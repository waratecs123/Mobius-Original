# main.py (без изменений)
import tkinter as tk
from gui import VideoEditorGUI

def main():
    root = tk.Tk()
    app = VideoEditorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()