import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import os
from functions import AudioData, read_audio, write_audio, resample_if_needed, compute_metrics, apply_gain, apply_eq, spectral_subtract_noise_reduction, simple_reverb, simple_delay, simple_chorus, soft_clip_distortion, pan_samples, highpass, lowpass, compress, normalize, autogain

class AudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("William Wave — Styled")
        self.attributes('-fullscreen', True)
        self.configure(background="#0f0f23")
        # Palette inspired by Fibonacci Scan
        self.bg_color = "#0f0f23"
        self.card_color = "#1a1a2e"
        self.accent_color = "#6366f1"
        self.secondary_accent = "#818cf8"
        self.text_color = "#e2e8f0"
        self.secondary_text = "#94a3b8"
        self.border_color = "#0f0f23"
        self.success_color = "#10b981"
        self.warning_color = "#f59e0b"
        self.title_bg_color = "#2d3748"

        # Fonts
        self.title_font = ('Arial', 20, 'bold')
        self.label_font = ('Arial', 11)
        self.small_font = ('Arial', 10)
        self.button_font = ('Arial', 11, 'bold')
        self.mono_font = ('Courier New', 10)

        self.audio = AudioData(samples=None, samplerate=44100)
        self.processed = None
        self._proc_lock = threading.Lock()
        self._debounce_timer = None
        self._version = 0

        # Build UI and draw empty plots
        self._build_ui()
        self.draw_waveform(self.audio.samples)
        self.draw_spectrogram(self.audio.samples, self.audio.samplerate)
        self.draw_magnitude_spectrum(self.audio.samples, self.audio.samplerate)
        self.draw_histogram(self.audio.samples)
        self.update_metrics(self.audio.samples, self.audio.samplerate)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # Configure ttk theme and styles (clam + customizations)
        style = ttk.Style()
        try:
            style.theme_create("styled", parent="clam", settings={
                "TFrame": {"configure": {"background": self.bg_color}},
                "TLabel": {"configure": {"background": self.card_color, "foreground": self.text_color, "font": self.label_font}},
                "TButton": {"configure": {"padding": 6, "font": self.button_font}},
                "Horizontal.TScale": {"configure": {"troughcolor": "#252535", "background": self.card_color}}
            })
            style.theme_use("styled")
        except Exception:
            style.theme_use("clam")

        # Button styles
        style.configure('Accent.TButton',
                        background=self.accent_color,
                        foreground='white',
                        font=self.button_font,
                        padding=(8, 6),
                        relief='flat')
        style.map('Accent.TButton',
                  background=[('active', '#4f46e5')])

        style.configure('Secondary.TButton',
                        background=self.card_color,
                        foreground=self.text_color,
                        font=self.button_font,
                        padding=(8, 6),
                        relief='flat')
        style.map('Secondary.TButton',
                  background=[('active', '#2d3748')])

        # Main layout
        container = ttk.Frame(self, style="TFrame")
        container.pack(fill='both', expand=True, padx=20, pady=18)

        top_bar = tk.Frame(container, bg=self.bg_color, height=50)
        top_bar.pack(fill='x', pady=(0, 12))
        top_bar.pack_propagate(False)

        # Gradient header
        grad = tk.Canvas(top_bar, bg=self.bg_color, highlightthickness=0, height=50)
        grad.pack(fill='both', expand=True)
        w = 1200
        for i in range(w):
            ratio = i / max(1, w - 1)
            r = int(int(self.bg_color[1:3], 16) * (1 - ratio) + int(self.bg_color[1:3], 16) * ratio)
            g = int(int(self.bg_color[3:5], 16) * (1 - ratio) + int(self.bg_color[3:5], 16) * ratio)
            b = int(int(self.bg_color[5:7], 16) * (1 - ratio) + int(self.bg_color[5:7], 16) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            grad.create_line(i, 0, i, 50, fill=color)

        title = tk.Label(grad, text="William Wave", bg=self.bg_color, fg="white", font=('Arial', 22, 'bold'))
        title.place(relx=0.02, rely=0.22)

        # Top control buttons
        top_controls = tk.Frame(container, bg=self.bg_color)
        top_controls.pack(fill='x', pady=(0, 8))

        btns = [
            ('Импорт', self.import_file, 'Secondary.TButton'),
            ('Запись', self.open_record_dialog, 'Secondary.TButton'),
            ('Проиграть оригинал', self.play_original, 'Accent.TButton'),
            ('Проиграть обработанное', self.play_processed, 'Accent.TButton'),
            ('Сохранить обработанное', self.save_processed, 'Secondary.TButton'),
            ('Инвертировать', self.reverse_processed, 'Secondary.TButton'),
            ('Сбросить', self.reset_sliders, 'Secondary.TButton'),
        ]
        for text, cmd, style_name in btns:
            b = ttk.Button(top_controls, text=text, command=cmd, style=style_name)
            b.pack(side='left', padx=6)

        # Body layout: left sliders, right visualizations
        body = tk.Frame(container, bg=self.bg_color)
        body.pack(fill='both', expand=True)

        left = tk.Frame(body, bg=self.card_color, width=380, padx=12, pady=12)
        left.pack(side='left', fill='y', padx=(0, 12), pady=6)
        left.pack_propagate(False)

        # Sliders
        self.vars = {}
        sliders = [
            ('gain_db', -24, 24, 0, 'Гейн (дБ)'),
            ('low_db', -12, 12, 0, 'Низкие (дБ)'),
            ('low_freq', 20, 500, 120, 'Низ. частота (Гц)'),
            ('low_q', 0.1, 10, 0.7, 'Низ. Q'),
            ('mid_db', -12, 12, 0, 'Средние (дБ)'),
            ('mid_freq', 200, 5000, 1000, 'Ср. частота (Гц)'),
            ('mid_q', 0.1, 10, 1.0, 'Ср. Q'),
            ('high_db', -12, 12, 0, 'Верх (дБ)'),
            ('high_freq', 2000, 20000, 6000, 'Верх частота (Гц)'),
            ('high_q', 0.1, 10, 0.7, 'Верх Q'),
            ('nr_db', 0, 30, 8, 'Шумоподавление (дБ)'),
            ('reverb_ms', 0, 1500, 250, 'Реверб (мс)'),
            ('reverb_mix', 0, 100, 20, 'Реверб микс (%)'),
            ('delay_ms', 0, 1000, 120, 'Дейлей (мс)'),
            ('delay_fb', 0, 95, 20, 'Фидбек (%)'),
            ('delay_mix', 0, 100, 20, 'Дейлей микс (%)'),
            ('chorus_depth_ms', 0, 50, 10, 'Хорус глубина (мс)'),
            ('chorus_rate_hz', 0.1, 5, 0.5, 'Хорус скорость (Гц)'),
            ('chorus_mix', 0, 100, 30, 'Хорус микс (%)'),
            ('dist_drive', 1, 20, 1, 'Дисторшн драйв'),
            ('dist_mix', 0, 100, 50, 'Дисторшн микс (%)'),
            ('pan', -100, 100, 0, 'Панорама'),
            ('hpf', 0, 2000, 0, 'HPF срез (Гц)'),
            ('lpf', 0, 20000, 0, 'LPF срез (Гц)'),
            ('compress_th', -60, 0, -24, 'Компрессор порог (дБ)'),
            ('compress_ratio', 1, 20, 4, 'Компрессор отношение'),
            ('compress_attack_ms', 1, 100, 10, 'Компрессор атака (мс)'),
            ('compress_release_ms', 10, 500, 100, 'Компрессор релиз (мс)'),
            ('normalize', 0, 1, 0, 'Нормализация (0/1)'),
            ('autogain', 0, 1, 0, 'Авто-гейн (0/1)'),
        ]
        slider_canvas = tk.Canvas(left, bg=self.card_color, highlightthickness=0)
        slider_canvas.pack(side='left', fill='both', expand=True)
        slider_scroll = ttk.Scrollbar(left, orient='vertical', command=slider_canvas.yview)
        slider_scroll.pack(side='right', fill='y')
        slider_canvas.configure(yscrollcommand=slider_scroll.set)
        sliders_frame = tk.Frame(slider_canvas, bg=self.card_color)
        slider_canvas.create_window((0, 0), window=sliders_frame, anchor='nw')

        def on_frame_config(e):
            slider_canvas.configure(scrollregion=slider_canvas.bbox("all"))
        sliders_frame.bind("<Configure>", on_frame_config)

        for key, mn, mx, default, label in sliders:
            row = tk.Frame(sliders_frame, bg=self.card_color)
            row.pack(fill='x', pady=6)
            lbl = tk.Label(row, text=label, bg=self.card_color, fg=self.text_color, font=self.small_font, width=20, anchor='w')
            lbl.pack(side='left', padx=(2, 8))
            var = tk.DoubleVar(value=default)
            scl = ttk.Scale(row, from_=mn, to=mx, variable=var, orient='horizontal', command=lambda v, k=key: self._on_slider(k))
            scl.pack(side='left', fill='x', expand=True)
            val_lbl = tk.Label(row, text=str(default), bg=self.card_color, fg=self.secondary_text, font=self.small_font, width=8)
            val_lbl.pack(side='left', padx=6)
            self.vars[key] = (var, val_lbl, mn, mx, default)

        ttk.Button(sliders_frame, text='Обработать', command=self.process_audio, style='Accent.TButton').pack(fill='x', pady=(12, 6))

        # Right visualizations
        right = tk.Frame(body, bg=self.bg_color)
        right.pack(side='left', fill='both', expand=True)

        # Waveform canvas (top)
        self.canvas_wave = tk.Canvas(right, bg='#12131a', height=160, highlightthickness=0)
        self.canvas_wave.pack(fill='x', padx=8, pady=(0, 8))

        # Configure matplotlib dark background and custom colors
        plt.style.use('dark_background')
        for fig in ['fig_spec', 'fig_mag', 'fig_hist']:
            fig_obj = plt.figure(figsize=(5, 2), facecolor='#1a1a2e')
            ax = fig_obj.add_subplot(111, facecolor='#1a1a2e')
            ax.tick_params(colors=self.secondary_text, labelsize=9)
            for spine in ax.spines.values():
                spine.set_color(self.secondary_text)
            setattr(self, fig, fig_obj)
            setattr(self, f'ax_{fig.split("_")[1]}', ax)

        spec_frame = tk.Frame(right, bg=self.bg_color)
        spec_frame.pack(fill='both', expand=True, padx=8, pady=6)
        self.fig_spec.tight_layout(pad=1.5)
        self.spec_canvas = FigureCanvasTkAgg(self.fig_spec, master=spec_frame)
        self.spec_canvas.get_tk_widget().configure(bg='#1a1a2e', highlightthickness=0)
        self.spec_canvas.get_tk_widget().pack(fill='both', expand=True)

        mag_frame = tk.Frame(right, bg=self.bg_color)
        mag_frame.pack(fill='both', expand=True, padx=8, pady=6)
        self.fig_mag.tight_layout(pad=1.5)
        self.mag_canvas = FigureCanvasTkAgg(self.fig_mag, master=mag_frame)
        self.mag_canvas.get_tk_widget().configure(bg='#1a1a2e', highlightthickness=0)
        self.mag_canvas.get_tk_widget().pack(fill='both', expand=True)

        hist_frame = tk.Frame(right, bg=self.bg_color)
        hist_frame.pack(fill='both', expand=True, padx=8, pady=6)
        self.fig_hist.tight_layout(pad=1.5)
        self.hist_canvas = FigureCanvasTkAgg(self.fig_hist, master=hist_frame)
        self.hist_canvas.get_tk_widget().configure(bg='#1a1a2e', highlightthickness=0)
        self.hist_canvas.get_tk_widget().pack(fill='both', expand=True)

        # Metrics bottom bar
        metrics_frame = tk.Frame(self, bg=self.card_color)
        metrics_frame.pack(fill='x', padx=20, pady=(10, 20))
        self.metrics_labels = {}
        metrics_keys = ['duration', 'channels', 'sample_rate', 'peak_db', 'rms_db', 'crest_factor', 'dynamic_range_db']
        for key in metrics_keys:
            row = tk.Frame(metrics_frame, bg=self.card_color)
            row.pack(side='left', padx=8)
            label_text = {
                'duration': 'Длительность (с):',
                'channels': 'Каналы:',
                'sample_rate': 'Частота (Гц):',
                'peak_db': 'Пик (дБ):',
                'rms_db': 'RMS (дБ):',
                'crest_factor': 'Крест-фактор:',
                'dynamic_range_db': 'Динамический диапазон (дБ):',
            }[key]
            tk.Label(row, text=label_text, bg=self.card_color, fg=self.secondary_text, font=self.small_font).pack(side='left')
            val_lbl = tk.Label(row, text='N/A', bg=self.card_color, fg=self.text_color, font=self.small_font)
            val_lbl.pack(side='left', padx=(6, 0))
            self.metrics_labels[key] = val_lbl

        # Status bar
        status_bar = tk.Frame(self, bg=self.bg_color)
        status_bar.pack(fill='x', padx=20, pady=(0, 10))
        self.status = tk.Label(status_bar, text='Готово', bg=self.bg_color, fg=self.secondary_text, font=self.small_font)
        self.status.pack(side='left')

    def reset_sliders(self):
        for key, (var, lbl, mn, mx, default) in self.vars.items():
            var.set(default)
            lbl.config(text=f"{default:.2f}" if isinstance(default, float) else str(default))
        self.process_audio()

    def _on_slider(self, key):
        var, lbl, mn, mx, _ = self.vars[key]
        v = var.get()
        lbl.config(text=f"{v:.2f}" if isinstance(v, float) else str(v))
        self.schedule_process()

    def schedule_process(self, delay_ms=300):
        self._version += 1
        vid = self._version
        if self._debounce_timer:
            self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(delay_ms, lambda: self._debounced_worker(vid))

    def _debounced_worker(self, vid):
        def worker():
            if vid != self._version:
                return
            vals = self.get_slider_values()
            try:
                s = self.audio.samples
                sr = self.audio.samplerate
                proc = self._apply_chain(s, sr, vals)
                with self._proc_lock:
                    self.processed = AudioData(samples=proc.astype(np.float32), samplerate=sr)
                self.after(0, lambda: self.draw_spectrogram(self.processed.samples, sr))
                self.after(0, lambda: self.draw_waveform(self.processed.samples))
                self.after(0, lambda: self.draw_magnitude_spectrum(self.processed.samples, sr))
                self.after(0, lambda: self.draw_histogram(self.processed.samples))
                self.after(0, lambda: self.update_metrics(self.processed.samples, sr))
                self.after(0, lambda: self.status.config(text='Обновлено'))
            except Exception as e:
                self.after(0, lambda: self.status.config(text=f'Ошибка: {e}'))
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def get_slider_values(self):
        vals = {}
        for key, (var, lbl, mn, mx, _) in self.vars.items():
            v = var.get()
            if key in ('normalize', 'autogain'):
                vals[key] = int(round(v))
            else:
                vals[key] = float(v)
        return vals

    def _apply_chain(self, samples, sr, vals):
        if samples is None:
            return samples
        s = samples.astype(np.float64)
        s = apply_gain(s, vals.get('gain_db', 0.0))
        s = apply_eq(s, sr, vals.get('low_db', 0.0), vals.get('mid_db', 0.0), vals.get('high_db', 0.0),
                     vals.get('low_freq', 120.0), vals.get('mid_freq', 1000.0), vals.get('high_freq', 6000.0),
                     vals.get('low_q', 0.7), vals.get('mid_q', 1.0), vals.get('high_q', 0.7))
        nr_db = vals.get('nr_db', 0.0)
        if nr_db > 0.01:
            s = spectral_subtract_noise_reduction(s, sr, reduction_db=nr_db)
        hpf = vals.get('hpf', 0.0)
        lpf = vals.get('lpf', 0.0)
        if hpf > 1:
            s = highpass(s, sr, hpf)
        if lpf > 1:
            s = lowpass(s, sr, lpf)
        if vals.get('autogain', 0) == 1:
            s = autogain(s)
        if vals.get('normalize', 0) == 1:
            s = normalize(s)
        s = compress(s, threshold_db=vals.get('compress_th', -24.0), ratio=vals.get('compress_ratio', 4.0),
                    attack_ms=vals.get('compress_attack_ms', 10.0), release_ms=vals.get('compress_release_ms', 100.0), sr=sr)
        reverb_sec = vals.get('reverb_ms', 0.0) / 1000.0
        reverb_mix = vals.get('reverb_mix', 0.0) / 100.0
        if reverb_sec > 0.001 and reverb_mix > 0.001:
            s = simple_reverb(s, sr, reverb_seconds=reverb_sec, mix=reverb_mix)
        delay_ms = vals.get('delay_ms', 0.0)
        delay_fb = vals.get('delay_fb', 0.0) / 100.0
        delay_mix = vals.get('delay_mix', 0.0) / 100.0
        if delay_ms > 1 and delay_mix > 0.001:
            s = simple_delay(s, sr, delay_ms=delay_ms, feedback=delay_fb, mix=delay_mix)
        chorus_depth_ms = vals.get('chorus_depth_ms', 0.0)
        chorus_rate_hz = vals.get('chorus_rate_hz', 0.0)
        chorus_mix = vals.get('chorus_mix', 0.0) / 100.0
        if chorus_depth_ms > 0.1 and chorus_mix > 0.001:
            s = simple_chorus(s, sr, depth_ms=chorus_depth_ms, rate_hz=chorus_rate_hz, mix=chorus_mix)
        dist_drive = vals.get('dist_drive', 1.0)
        dist_mix = vals.get('dist_mix', 0.0) / 100.0
        if dist_drive > 1.01 and dist_mix > 0.001:
            s = soft_clip_distortion(s, drive=dist_drive, mix=dist_mix)
        pan = vals.get('pan', 0.0) / 100.0
        s = pan_samples(s, pan)
        peak = np.max(np.abs(s)) if s is not None else 0
        if peak > 0:
            s = s / max(1.0, peak)
        return s

    def process_audio(self):
        if self.audio.samples is None:
            messagebox.showinfo('Инфо', 'Нет загруженного аудио')
            return
        self.status.config(text='Обработка...')
        vals = self.get_slider_values()
        def worker():
            try:
                proc = self._apply_chain(self.audio.samples, self.audio.samplerate, vals)
                with self._proc_lock:
                    self.processed = AudioData(samples=proc.astype(np.float32), samplerate=self.audio.samplerate)
                self.after(0, lambda: self.draw_waveform(self.processed.samples))
                self.after(0, lambda: self.draw_spectrogram(self.processed.samples, self.audio.samplerate))
                self.after(0, lambda: self.draw_magnitude_spectrum(self.processed.samples, self.audio.samplerate))
                self.after(0, lambda: self.draw_histogram(self.processed.samples))
                self.after(0, lambda: self.update_metrics(self.processed.samples, self.audio.samplerate))
                self.after(0, lambda: self.status.config(text='Готово'))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror('Ошибка', str(e)))
                self.after(0, lambda: self.status.config(text='Ошибка'))
        threading.Thread(target=worker, daemon=True).start()

    def import_file(self):
        path = filedialog.askopenfilename(filetypes=[('Аудио', '*.wav *.flac *.aiff *.aif')])
        if not path:
            return
        try:
            self.audio = read_audio(path)
            self.audio = resample_if_needed(self.audio, 44100)
            self.processed = None
            self.draw_waveform(self.audio.samples)
            self.draw_spectrogram(self.audio.samples, self.audio.samplerate)
            self.draw_magnitude_spectrum(self.audio.samples, self.audio.samplerate)
            self.draw_histogram(self.audio.samples)
            self.update_metrics(self.audio.samples, self.audio.samplerate)
            self.status.config(text=f'Загружено {os.path.basename(path)}')
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

    def open_record_dialog(self):
        dlg = RecordDialog(self)
        self.wait_window(dlg)
        if dlg.result is not None:
            self.audio = dlg.result
            self.processed = None
            self.draw_waveform(self.audio.samples)
            self.draw_spectrogram(self.audio.samples, self.audio.samplerate)
            self.draw_magnitude_spectrum(self.audio.samples, self.audio.samplerate)
            self.draw_histogram(self.audio.samples)
            self.update_metrics(self.audio.samples, self.audio.samplerate)
            self.status.config(text='Записано')

    def play_original(self):
        if self.audio.samples is None:
            messagebox.showinfo('Инфо', 'Нет аудио')
            return
        try:
            sd.stop()
            sd.play(self.audio.samples, self.audio.samplerate)
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

    def play_processed(self):
        with self._proc_lock:
            p = self.processed
        if p is None or p.samples is None:
            messagebox.showinfo('Инфо', 'Нет обработанного аудио')
            return
        try:
            sd.stop()
            sd.play(p.samples, p.samplerate)
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

    def save_processed(self):
        with self._proc_lock:
            p = self.processed
        if p is None or p.samples is None:
            messagebox.showinfo('Инфо', 'Нет обработанного аудио')
            return
        path = filedialog.asksaveasfilename(defaultextension='.wav', filetypes=[('WAV', '*.wav')])
        if not path:
            return
        try:
            write_audio(path, p)
            self.status.config(text=f'Сохранено {os.path.basename(path)}')
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

    def reverse_processed(self):
        with self._proc_lock:
            p = self.processed
        if p is None or p.samples is None:
            messagebox.showinfo('Инфо', 'Нет обработанного аудио')
            return
        s = p.samples
        if s.ndim == 1:
            s = s[::-1]
        else:
            s = s[::-1, :]
        with self._proc_lock:
            self.processed = AudioData(samples=s, samplerate=p.samplerate)
        self.draw_waveform(self.processed.samples)
        self.draw_spectrogram(self.processed.samples, self.processed.samplerate)
        self.draw_magnitude_spectrum(self.processed.samples, self.processed.samplerate)
        self.draw_histogram(self.processed.samples)
        self.update_metrics(self.processed.samples, self.processed.samplerate)

    def draw_waveform(self, samples):
        self.canvas_wave.delete('all')
        w = self.canvas_wave.winfo_width() or 900
        h = self.canvas_wave.winfo_height() or 160
        if samples is None or samples.size == 0:
            self.canvas_wave.create_text(w/2, h/2, text="(нет вейвформы)", fill=self.accent_color, font=self.small_font)
            return
        if samples.ndim > 1:
            data = samples.mean(axis=1)
        else:
            data = samples
        N = min(data.size, 2000)
        step = max(1, data.size // N)
        data = data[::step][:N]
        maxv = np.max(np.abs(data))
        if maxv <= 0:
            maxv = 1.0
            self.canvas_wave.create_text(w/2, h/2, text="(нулевой сигнал)", fill=self.accent_color, font=self.small_font)
            return
        ys = (data / maxv) * (h / 2 - 4)
        mid = h / 2
        points = []
        dx = w / max(1, N - 1)
        for i, y in enumerate(ys):
            x = i * dx
            points.extend([x, mid - y])
        if len(points) >= 4:
            self.canvas_wave.create_line(points, fill=self.accent_color, width=1.6, smooth=True)
        else:
            self.canvas_wave.create_text(w/2, h/2, text="(короткий сигнал)", fill=self.accent_color, font=self.small_font)

    def draw_spectrogram(self, samples, sr):
        from scipy import signal
        self.ax_spec.clear()
        if samples is None or samples.size < 512:
            self.ax_spec.text(0.5, 0.5, '(нет спектрограммы)', ha='center', va='center', transform=self.ax_spec.transAxes, color=self.secondary_text, fontsize=9)
            self.spec_canvas.draw()
            return
        if samples.ndim > 1:
            data = samples.mean(axis=1)
        else:
            data = samples
        nfft = 512
        noverlap = nfft // 2
        try:
            self.ax_spec.specgram(data, NFFT=nfft, Fs=sr, noverlap=noverlap, cmap='magma')
            self.ax_spec.set_ylim(0, sr/2)
            self.ax_spec.set_title('Спектрограмма', color=self.text_color, fontsize=10, pad=5)
            self.ax_spec.set_xlabel('Время (с)', color=self.secondary_text, fontsize=9)
            self.ax_spec.set_ylabel('Частота (Гц)', color=self.secondary_text, fontsize=9)
        except Exception as e:
            self.ax_spec.text(0.5, 0.5, f'(ошибка спектрограммы: {str(e)})', ha='center', va='center', transform=self.ax_spec.transAxes, color=self.secondary_text, fontsize=9)
        self.spec_canvas.draw()

    def draw_magnitude_spectrum(self, samples, sr):
        self.ax_mag.clear()
        if samples is None or samples.size < 2:
            self.ax_mag.text(0.5, 0.5, '(нет спектра)', ha='center', va='center', transform=self.ax_mag.transAxes, color=self.secondary_text, fontsize=9)
            self.mag_canvas.draw()
            return
        if samples.ndim > 1:
            data = samples.mean(axis=1)
        else:
            data = samples
        try:
            freqs = np.fft.rfftfreq(len(data), 1/sr)
            mag = np.abs(np.fft.rfft(data))
            mag_db = 20 * np.log10(mag + 1e-9)
            self.ax_mag.semilogx(freqs, mag_db)
            self.ax_mag.set_xlim(20, sr/2)
            self.ax_mag.set_ylim(-120, 0)
            self.ax_mag.set_title('Магнитуда спектра (дБ)', color=self.text_color, fontsize=10, pad=5)
            self.ax_mag.set_xlabel('Частота (Гц)', color=self.secondary_text, fontsize=9)
            self.ax_mag.set_ylabel('Амплитуда (дБ)', color=self.secondary_text, fontsize=9)
        except Exception as e:
            self.ax_mag.text(0.5, 0.5, f'(ошибка спектра: {str(e)})', ha='center', va='center', transform=self.ax_mag.transAxes, color=self.secondary_text, fontsize=9)
        self.mag_canvas.draw()

    def draw_histogram(self, samples):
        self.ax_hist.clear()
        if samples is None or samples.size == 0:
            self.ax_hist.text(0.5, 0.5, '(нет гистограммы)', ha='center', va='center', transform=self.ax_hist.transAxes, color=self.secondary_text, fontsize=9)
            self.hist_canvas.draw()
            return
        try:
            data = samples.flatten()
            self.ax_hist.hist(data, bins=100, density=True, alpha=0.8)
            self.ax_hist.set_title('Гистограмма амплитуд', color=self.text_color, fontsize=10, pad=5)
            self.ax_hist.set_xlabel('Амплитуда', color=self.secondary_text, fontsize=9)
            self.ax_hist.set_ylabel('Плотность', color=self.secondary_text, fontsize=9)
        except Exception as e:
            self.ax_hist.text(0.5, 0.5, f'(ошибка гистограммы: {str(e)})', ha='center', va='center', transform=self.ax_hist.transAxes, color=self.secondary_text, fontsize=9)
        self.hist_canvas.draw()

    def update_metrics(self, samples, sr):
        metrics = compute_metrics(samples, sr)
        for key, val in metrics.items():
            if isinstance(val, float):
                text = f"{val:.2f}"
            else:
                text = str(val)
            self.metrics_labels[key].config(text=text)

    def _on_close(self):
        try:
            sd.stop()
        except Exception:
            pass
        self.destroy()

class RecordDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Запись')
        self.geometry('380x160')
        self.configure(bg='#0f0f23')
        self.result = None
        self.sr = 44100
        self._frames = []
        self._stream = None
        style = ttk.Style()
        style.theme_use("clam")
        ttk.Label(self, text='Нажмите Старт для записи', background='#0f0f23', foreground='#e2e8f0').pack(pady=10)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        self.btn_start = ttk.Button(btn_frame, text='Старт', command=self.start_record)
        self.btn_start.pack(side='left', padx=5)
        self.btn_stop = ttk.Button(btn_frame, text='Стоп', command=self.stop_record, state='disabled')
        self.btn_stop.pack(side='left', padx=5)
        self.duration = tk.IntVar(value=10)
        ttk.Label(self, text='Макс. секунд (0 для ручной остановки):', background='#0f0f23', foreground='#94a3b8').pack()
        ttk.Spinbox(self, from_=0, to=600, textvariable=self.duration, font=("Helvetica", 10)).pack(pady=5)

    def start_record(self):
        self._frames = []
        try:
            self._stream = sd.InputStream(samplerate=self.sr, channels=1, callback=self._callback)
            self._stream.start()
            self.btn_start.config(state='disabled')
            self.btn_stop.config(state='normal')
            maxsec = self.duration.get()
            if maxsec > 0:
                self.after(maxsec * 1000, self.stop_record)
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

    def _callback(self, indata, frames, time, status):
        if status:
            pass
        self._frames.append(indata.copy())

    def stop_record(self):
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        self.btn_start.config(state='normal')
        self.btn_stop.config(state='disabled')
        if self._frames:
            arr = np.concatenate(self._frames, axis=0)
            arr = arr.squeeze()
            self.result = AudioData(samples=arr.astype(np.float32), samplerate=self.sr)
        self.destroy()