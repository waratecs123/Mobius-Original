import tkinter as tk
from tkinter import ttk, font
import webbrowser
import random


class MöbiusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Möbius")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a0a0a")

        # Шрифты
        self.title_font = ('Segoe UI', 24, 'bold')
        self.app_font = ('Segoe UI', 13)
        self.small_font = ('Segoe UI', 11)
        self.button_font = ('Segoe UI', 12)

        # Цветовая палитра
        self.bg_color = "#0a0a0a"
        self.sidebar_color = "#151515"
        self.card_color = "#1e1e1e"
        self.accent_color = "#4870ff"
        self.text_color = "#f0f0f0"
        self.secondary_text = "#909090"
        self.disabled_color = "#404040"

        # Социальные ссылки
        self.social_links = {
            "Telegram": "https://t.me/mobius_studio",
            "YouTube": "https://youtube.com/mobius_studio",
            "GitHub": "https://github.com/mobius-studio"
        }

        # Приложения, которые не имеют проектов
        self.disabled_apps = ["Gagarin Bridge", "Jobs Archive", "Marilyn Tone", "Fibonacci Scan"]

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TFrame", background=self.bg_color)
        style.configure("Sidebar.TFrame", background=self.sidebar_color)
        style.configure("Card.TFrame", background=self.card_color)
        style.configure("TLabel", background=self.card_color, foreground=self.text_color, font=self.app_font)
        style.configure("Title.TLabel", font=self.title_font)
        style.configure("Secondary.TLabel", foreground=self.secondary_text)

        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True)

        self.setup_sidebar(main_container)
        self.setup_main_area(main_container)

        self.show_app(self.apps[0][0])

    def setup_sidebar(self, parent):
        sidebar = ttk.Frame(parent, width=250, style="Sidebar.TFrame")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Верхняя часть сайдбара с логотипом
        top_sidebar = ttk.Frame(sidebar, style="Sidebar.TFrame")
        top_sidebar.pack(fill="x")

        logo_frame = ttk.Frame(top_sidebar, style="Sidebar.TFrame")
        logo_frame.pack(pady=(40, 50), padx=20, fill="x")

        logo_canvas = tk.Canvas(logo_frame, bg=self.sidebar_color, width=40, height=40,
                                highlightthickness=0, bd=0)
        logo_canvas.pack(side="left")
        logo_canvas.create_oval(5, 5, 35, 35, fill=self.accent_color, outline="")
        logo_canvas.create_text(20, 20, text="M", font=('Segoe UI', 16, 'bold'), fill="#ffffff")

        tk.Label(logo_frame, text="MÖBIUS", font=('Segoe UI', 16, 'bold'),
                 bg=self.sidebar_color, fg=self.text_color).pack(side="left", padx=12)

        apps_frame = ttk.Frame(top_sidebar, style="Sidebar.TFrame")
        apps_frame.pack(fill="x", padx=15)

        self.apps = [
            ("Lumière Cut", "#4870ff"),
            ("Chopin Keys", "#9c4dff"),
            ("Gagarin Bridge", "#ff4d8d"),
            ("Picasso Art", "#ff6b35"),
            ("Newton Flow", "#ffc233"),
            ("Fibonacci Scan", "#4dffdf"),
            ("Marilyn Tone", "#ff4df0"),
            ("Jobs Archive", "#b84dff")
        ]

        self.app_buttons = []
        for app_name, color in self.apps:
            btn_frame = tk.Frame(apps_frame, bg=self.sidebar_color, highlightthickness=0)
            btn_frame.pack(fill="x", pady=2)

            is_disabled = app_name in self.disabled_apps

            btn = tk.Button(btn_frame,
                            text=app_name,
                            font=('Segoe UI', 12, 'italic' if is_disabled else 'normal'),
                            bg=self.sidebar_color,
                            fg=self.disabled_color if is_disabled else self.text_color,
                            bd=0,
                            activebackground="#252525",
                            activeforeground="#ffffff",
                            padx=20,
                            pady=12,
                            anchor="w",
                            highlightthickness=0,
                            command=lambda n=app_name: self.show_app(n) if n not in self.disabled_apps else None)
            btn.pack(fill="x")

            btn.indicator = tk.Frame(btn_frame,
                                     bg=color if not is_disabled else self.disabled_color,
                                     width=0,
                                     height=0)
            btn.indicator.place(relx=0,
                                rely=0.5,
                                anchor="w",
                                relheight=0.8)

            if not is_disabled:
                btn.bind("<Enter>", lambda e, b=btn, c=color: self.on_app_btn_hover(b, c, True))
                btn.bind("<Leave>", lambda e, b=btn: self.on_app_btn_hover(b, None, False))

            self.app_buttons.append(btn)

        # Нижняя часть сайдбара с социальными ссылками
        bottom_sidebar = ttk.Frame(sidebar, style="Sidebar.TFrame")
        bottom_sidebar.pack(side="bottom", fill="x", pady=(0, 20))

        social_frame = ttk.Frame(bottom_sidebar, style="Sidebar.TFrame")
        social_frame.pack(side="bottom", padx=15, pady=10, fill="x")

        ttk.Label(social_frame, text="Социальные сети", style="Secondary.TLabel").pack(anchor="w", pady=(0, 10))

        for platform, url in self.social_links.items():
            btn = tk.Button(social_frame, text=platform, font=self.small_font,
                            bg=self.sidebar_color, fg=self.secondary_text, bd=0,
                            activebackground="#252525", activeforeground=self.accent_color,
                            padx=20, pady=6, anchor="w", command=lambda u=url: webbrowser.open(u))
            btn.pack(fill="x", pady=2)

    def setup_main_area(self, parent):
        self.main_area = ttk.Frame(parent, style="TFrame")
        self.main_area.pack(side="right", fill="both", expand=True)

        header_frame = ttk.Frame(self.main_area, style="TFrame")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        self.current_app = tk.StringVar(value="Добро пожаловать в Möbius")
        ttk.Label(header_frame, textvariable=self.current_app,
                  style="Title.TLabel").pack(side="left")

        new_btn_frame = tk.Frame(header_frame, bg=self.bg_color)
        new_btn_frame.pack(side="right")

        new_btn = tk.Button(new_btn_frame, text="Новый проект  ", font=self.button_font,
                            bg=self.accent_color, fg="#ffffff", bd=0,
                            activebackground="#3a5bd9", padx=16, pady=8,
                            compound="right", command=self.create_new_project)
        new_btn.pack()

        plus_icon = tk.Label(new_btn, text="+", font=('Segoe UI', 16),
                             bg=self.accent_color, fg="#ffffff")
        plus_icon.place(relx=0.8, rely=0.5, anchor="center")

        # Улучшенная прокрутка
        self.scroll_frame = ttk.Frame(self.main_area, style="TFrame")
        self.scroll_frame.pack(fill="both", expand=True, padx=(30, 15), pady=(0, 15))

        self.canvas = tk.Canvas(self.scroll_frame, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Стилизованный скроллбар
        style = ttk.Style()
        style.configure("TScrollbar", gripcount=0, background=self.card_color,
                        troughcolor=self.bg_color, bordercolor=self.bg_color)
        style.map("TScrollbar", background=[("active", self.accent_color)])

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_app_btn_hover(self, button, color, is_hover):
        if is_hover:
            button.config(bg="#252525")
            button.indicator.config(bg=color, width=4)
        else:
            button.config(bg=self.sidebar_color)
            button.indicator.config(bg=self.sidebar_color, width=0)

    def show_app(self, app_name):
        self.current_app.set(app_name)

        for btn in self.app_buttons:
            if btn.cget("text") == app_name:
                btn.indicator.config(bg=self.accent_color, width=4)
                btn.config(fg="#ffffff")
            else:
                is_disabled = btn.cget("text") in self.disabled_apps
                btn.indicator.config(bg=self.sidebar_color, width=0)
                btn.config(fg=self.disabled_color if is_disabled else self.secondary_text)

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if app_name in self.disabled_apps:
            self.show_empty_state(app_name)
        else:
            self.show_projects(app_name)

    def show_empty_state(self, app_name):
        empty_frame = ttk.Frame(self.scrollable_frame, style="TFrame")
        empty_frame.pack(fill="both", expand=True, pady=100)

        ttk.Label(empty_frame, text="✖", font=('Segoe UI', 48),
                  foreground=self.secondary_text).pack(pady=20)

        ttk.Label(empty_frame, text=f"{app_name} не имеет проектов",
                  font=('Segoe UI', 14), foreground=self.secondary_text).pack()

    def show_projects(self, app_name):
        ttk.Label(self.scrollable_frame, text="ПОСЛЕДНИЕ ПРОЕКТЫ",
                  font=('Segoe UI', 12, 'bold'),
                  foreground=self.secondary_text).pack(anchor="nw", pady=(0, 20), padx=5)

        projects_frame = ttk.Frame(self.scrollable_frame, style="TFrame")
        projects_frame.pack(fill="both", expand=True)

        project_count = random.randint(6, 12)
        for i in range(project_count):
            row = i // 3
            col = i % 3

            card = tk.Frame(projects_frame, bg=self.card_color, padx=0, pady=0,
                            highlightthickness=0, bd=0)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Миниатюра с плавным градиентом
            thumbnail = tk.Canvas(card, bg="#252525", width=240, height=160,
                                  highlightthickness=0, bd=0)
            thumbnail.pack()

            # Выбираем цвет на основе названия приложения для консистентности
            if app_name == "Lumière Cut":
                color1 = "#4870ff"
            elif app_name == "Chopin Keys":
                color1 = "#9c4dff"
            elif app_name == "Picasso Art":
                color1 = "#ff6b35"
            elif app_name == "Newton Flow":
                color1 = "#ffc233"
            else:
                color1 = random.choice(["#4870ff", "#9c4dff", "#ff4d8d", "#ff6b35"])

            color2 = self.darken_color(color1, 30)

            # Создаем градиент
            for y in range(160):
                ratio = y / 160
                r = int(int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio)
                g = int(int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio)
                b = int(int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                thumbnail.create_line(0, y, 240, y, fill=color)

            thumbnail.create_text(120, 80, text=app_name[0],
                                  font=('Segoe UI', 48, 'bold'),
                                  fill="#ffffff")

            # Информация о проекте
            info_frame = tk.Frame(card, bg=self.card_color)
            info_frame.pack(fill="x", padx=15, pady=(12, 10))

            tk.Label(info_frame, text=f"{app_name[:3].upper()}-{random.randint(1000, 9999)}",
                     bg=self.card_color, fg=self.text_color,
                     font=('Segoe UI', 12, 'bold')).pack(anchor="w")

            tk.Label(info_frame,
                     text=f"Изменено: {random.randint(1, 30)}.{random.randint(1, 12)}.2023 • {random.randint(1, 50)}MB",
                     bg=self.card_color, fg=self.secondary_text,
                     font=('Segoe UI', 9)).pack(anchor="w", pady=(4, 0))

            # Кнопки действий
            actions_frame = tk.Frame(card, bg=self.card_color)
            actions_frame.pack(fill="x", padx=15, pady=(0, 15))

            open_btn = tk.Button(actions_frame, text="Открыть", font=self.button_font,
                                 bg="#333333", fg=self.text_color, bd=0,
                                 activebackground="#3a3a3a", padx=0, pady=6,
                                 command=lambda n=f"{app_name[:3]}_project_{i + 1}": self.open_project(n))
            open_btn.pack(side="left", fill="x", expand=True)

            export_btn = tk.Button(actions_frame, text="Экспорт", font=self.button_font,
                                   bg="#252525", fg=self.secondary_text, bd=0,
                                   activebackground="#303030", padx=0, pady=6)
            export_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))

            projects_frame.grid_rowconfigure(row, weight=1)
            projects_frame.grid_columnconfigure(col, weight=1)

    def darken_color(self, color, percent):
        r = max(0, int(int(color[1:3], 16) * (100 - percent) / 100))
        g = max(0, int(int(color[3:5], 16) * (100 - percent) / 100))
        b = max(0, int(int(color[5:7], 16) * (100 - percent) / 100))
        return f"#{r:02x}{g:02x}{b:02x}"

    def open_project(self, project_name):
        print(f"Открытие проекта: {project_name}")

    def create_new_project(self):
        current_app = self.current_app.get()
        print(f"Создание нового проекта в {current_app}")


if __name__ == "__main__":
    root = tk.Tk()

    try:
        root.iconbitmap("mobius_icon.ico")
    except:
        pass

    window_width = 1200
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    app = MöbiusApp(root)
    root.mainloop()