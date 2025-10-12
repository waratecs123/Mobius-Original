# main.py
import tkinter as tk
from gui import ConverterGUI
from functions import ConverterController

def main():
    root = tk.Tk()
    controller = ConverterController()
    app = ConverterGUI(root, controller)
    app.run()

if __name__ == "__main__":
    main()