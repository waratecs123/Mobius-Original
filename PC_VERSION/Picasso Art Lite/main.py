import tkinter as tk
from gui import PicassoGUI

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Picasso Art Lite')
    root.attributes('-fullscreen', True)
    root.configure(bg='#07101a')
    app = PicassoGUI(root)
    root.mainloop()