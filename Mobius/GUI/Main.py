import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import random

class MobiusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Möbius")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#0d0d0d")

        # Цвета
        self.bg_color = "#0d0d0d"
        self.sidebar_color = "#161616"
        self.card_color = "#1f1f1f"
        self.accent_color = "#3fa9f5"
        self.text_color = "#f0f0f0"
        self.secondary_text = "#9a9a9a"
        self.disabled_color = "#555555"

        # Шрифты
        self.title_font = ("Segoe UI", 28, "bold")
        self.app_font = ("Segoe UI", 13)
        self.small_font = ("Segoe UI", 11)
        self.button_font = ("Segoe UI", 12, "bold")

        # Приложения
        self.apps = [
            ("Lumière Cut", "#4870ff"),
            ("Chopin Keys", "#9c4dff"),
            ("Gagarin Bridge", "#ff4d8d"),
            ("Picasso Art", "#ff6b35"),
            ("Newton Flow", "#ffc233"),
            ("Fibonacci Scan", "#4dffdf"),
            ("Marilyn Tone", "#ff4df0"),
            ("Jobs Archive", "#b84dff"),
            ("Tarantino Catch", "#ff3333"),
            ("Michael Byte", "#33cc33")
        ]

        self.disabled_apps = ["Gagarin Bridge", "Jobs Archive", "Marilyn Tone",
                              "Fibonacci Scan", "Tarantino Catch", "Michael Byte"]

        self.setup_ui()

        self.root.bind("<Escape>", lambda e: self.root.quit())

    def setup_ui(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True)

        self.setup_sidebar(main_container)
        self.setup_main_area(main_container)

        self.show_app(self.apps[0][0])

    def setup_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.sidebar_color, width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Логотип
        logo_frame = tk.Frame(sidebar, bg=self.sidebar_color)
        logo_frame.pack(pady=30)
        tk.Label(logo_frame, text="MÖBIUS", font=("Segoe UI", 20, "bold"), fg=self.accent_color, bg=self.sidebar_color).pack()

        # Кнопки приложений
        self.app_buttons = []
        for app_name, color in self.apps:
            is_disabled = app_name in self.disabled_apps

            btn_frame = tk.Frame(sidebar, bg=self.sidebar_color)
            btn_frame.pack(fill="x")

            indicator = tk.Frame(btn_frame, bg=self.sidebar_color, width=5)
            indicator.pack(side="left", fill="y")

            btn = tk.Label(btn_frame,
                           text=app_name,
                           font=("Segoe UI", 13, "italic" if is_disabled else "normal"),
                           fg=self.disabled_color if is_disabled else self.text_color,
                           bg=self.sidebar_color,
                           padx=20, pady=12, anchor="w")
            btn.pack(side="left", fill="x", expand=True)

            if not is_disabled:
                btn.bind("<Button-1>", lambda e, n=app_name: self.show_app(n))
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#252525"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.sidebar_color))

            self.app_buttons.append((btn, indicator, color, is_disabled))

        # Социальные сети
        social_frame = tk.Frame(sidebar, bg=self.sidebar_color)
        social_frame.pack(side="bottom", pady=30, fill="x")
        for name, url in {"GitHub": "https://github.com/mobius-studio", "YouTube": "https://youtube.com/mobius_studio", "Telegram": "https://t.me/mobius_studio"}.items():
            link = tk.Label(social_frame, text=name, font=self.small_font, fg=self.secondary_text,
                            bg=self.sidebar_color, anchor="w", cursor="hand2")
            link.pack(fill="x", padx=20, pady=4)
            link.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

    def setup_main_area(self, parent):
        self.main_area = tk.Frame(parent, bg=self.bg_color)
        self.main_area.pack(side="right", fill="both", expand=True)

        header = tk.Frame(self.main_area, bg=self.bg_color)
        header.pack(fill="x", pady=25, padx=40)

        self.current_app = tk.StringVar(value="Добро пожаловать")
        tk.Label(header, textvariable=self.current_app, font=self.title_font, fg=self.text_color, bg=self.bg_color).pack(side="left")

        new_btn = tk.Label(header, text="+ Новый проект", font=self.button_font, fg="white", bg=self.accent_color, padx=15, pady=8, cursor="hand2")
        new_btn.pack(side="right")
        new_btn.bind("<Enter>", lambda e: new_btn.config(bg="#2a7ed1"))
        new_btn.bind("<Leave>", lambda e: new_btn.config(bg=self.accent_color))
        new_btn.bind("<Button-1>", lambda e: self.create_new_project())

        self.projects_frame = tk.Frame(self.main_area, bg=self.bg_color)
        self.projects_frame.pack(fill="both", expand=True, padx=40, pady=20)

    def show_app(self, app_name):
        self.current_app.set(app_name)
        for btn, indicator, color, is_disabled in self.app_buttons:
            if btn.cget("text") == app_name and not is_disabled:
                indicator.config(bg=color)
                btn.config(fg="white")
            else:
                indicator.config(bg=self.sidebar_color)
                btn.config(fg=self.disabled_color if is_disabled else self.secondary_text)

        for widget in self.projects_frame.winfo_children():
            widget.destroy()

        if app_name in self.disabled_apps:
            tk.Label(self.projects_frame, text=f"{app_name} не имеет проектов", fg=self.secondary_text, bg=self.bg_color, font=("Segoe UI", 16)).pack(pady=100)
        else:
            self.show_projects(app_name)

    def show_projects(self, app_name):
        for i in range(6):
            card = tk.Frame(self.projects_frame, bg=self.card_color, width=260, height=200, highlightthickness=0)
            card.grid(row=i//3, column=i%3, padx=20, pady=20)
            card.grid_propagate(False)

            # Hover эффект glow и подъем
            def on_enter(e, c=card):
                c.config(bg="#2a2a2a")
                c.place_configure()
            def on_leave(e, c=card):
                c.config(bg=self.card_color)
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

            tk.Label(card, text=f"{app_name} — Проект {i+1}", fg=self.text_color, bg=card["bg"], font=("Segoe UI", 12, "bold"), anchor="w").pack(pady=(15,5), padx=10, anchor="w")
            tk.Label(card, text=f"Изменено: {random.randint(1,28)}.09.2023", fg=self.secondary_text, bg=card["bg"], font=("Segoe UI", 10), anchor="w").pack(padx=10, anchor="w")

            actions = tk.Frame(card, bg=card["bg"])
            actions.pack(side="bottom", fill="x", pady=10, padx=10)

            btn_open = tk.Label(actions, text="Открыть", font=self.button_font, fg="white", bg=self.accent_color, padx=10, pady=5, cursor="hand2")
            btn_open.pack(side="left", padx=5)
            btn_open.bind("<Enter>", lambda e, b=btn_open: b.config(bg="#2a7ed1"))
            btn_open.bind("<Leave>", lambda e, b=btn_open: b.config(bg=self.accent_color))
            btn_open.bind("<Button-1>", lambda e, n=f"{app_name}_proj_{i+1}": self.open_project(n))

            btn_export = tk.Label(actions, text="Экспорт", font=self.button_font, fg=self.secondary_text, bg="#2a2a2a", padx=10, pady=5, cursor="hand2")
            btn_export.pack(side="right", padx=5)
            btn_export.bind("<Enter>", lambda e, b=btn_export: b.config(fg="white"))
            btn_export.bind("<Leave>", lambda e, b=btn_export: b.config(fg=self.secondary_text))

    def create_new_project(self):
        messagebox.showinfo("Новый проект", f"Создание нового проекта в {self.current_app.get()}")

    def open_project(self, project_name):
        messagebox.showinfo("Открытие проекта", f"Открытие: {project_name}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MobiusApp(root)
    root.mainloop()