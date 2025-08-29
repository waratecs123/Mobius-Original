import tkinter as tk
from gui import TarantinoCatch


def main():
    root = tk.Tk()
    app = TarantinoCatch(root)

    def on_closing():
        app.preview_update_active = False
        if hasattr(app, 'cap') and app.cap:
            app.cap.release()
        if hasattr(app, 'out') and app.out:
            app.out.release()
        if hasattr(app, 'audio_cap') and app.audio_cap:
            app.audio_cap.terminate()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()