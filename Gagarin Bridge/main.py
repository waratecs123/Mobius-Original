# main.py
import tkinter as tk
from gui import ConverterGUI
from functions import ConverterController


def main():
    """Главная функция приложения"""
    root = tk.Tk()

    # Инициализация контроллера
    controller = ConverterController()

    # Инициализация GUI
    app = ConverterGUI(root, controller)

    # Запуск главного цикла
    root.mainloop()


if __name__ == "__main__":
    main()