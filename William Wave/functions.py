import os
import numpy as np
import soundfile as sf
from scipy import signal
from dataclasses import dataclass
from typing import Optional

@dataclass
class AudioData:
    samples: Optional[np.ndarray] = None
    samplerate: int = 44100

def read_audio(path: str) -> AudioData:
    data, sr = sf.read(path, always_2d=False)
    return AudioData(samples=data, samplerate=sr)

def write_audio(path: str, audio: AudioData):
    sf.write(path, audio.samples, audio.samplerate)

def resample_if_needed(audio: AudioData, target_sr: int) -> AudioData:
    if audio.samplerate == target_sr:
        return audio
    gcd = np.gcd(audio.samplerate, target_sr)
    up = target_sr // gcd
    down = audio.samplerate // gcd
    s = audio.samples
    if s is None:
        return AudioData(samples=None, samplerate=target_sr)
    if s.ndim == 1:
        out = signal.resample_poly(s, up, down)
    else:
        out = np.vstack([signal.resample_poly(s[:, ch], up, down) for ch in range(s.shape[1])]).T
    return AudioData(samples=out, samplerate=target_sr)

def apply_gain(samples: np.ndarray, gain_db: float) -> np.ndarray:
    g = 10 ** (gain_db / 20.0)
    return samples * g

def make_biquad(freq, q, g_db, sr):
    A = 10 ** (g_db / 40.0)
    omega = 2 * np.pi * freq / sr
    alpha = np.sin(omega) / (2 * q)
    cosw = np.cos(omega)
    b0 = 1 + alpha * A
    b1 = -2 * cosw
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * cosw
    a2 = 1 - alpha / A
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return b, a

def apply_eq(samples: np.ndarray, sr: int, low_db: float, mid_db: float, high_db: float, low_freq: float, mid_freq: float, high_freq: float, low_q: float, mid_q: float, high_q: float) -> np.ndarray:
    if samples is None:
        return samples
    out = samples.astype(np.float64)
    was_1d = False
    if out.ndim == 1:
        out = out[:, None]
        was_1d = True
    bands = [(low_freq, low_q, low_db), (mid_freq, mid_q, mid_db), (high_freq, high_q, high_db)]
    for freq, q, gdb in bands:
        if abs(gdb) < 0.01:
            continue
        b, a = make_biquad(freq, q, gdb, sr)
        for ch in range(out.shape[1]):
            out[:, ch] = signal.lfilter(b, a, out[:, ch])
    if was_1d:
        out = out[:, 0]
    return out

def spectral_subtract_noise_reduction(samples: np.ndarray, sr: int, reduction_db: float = 10.0, noise_floor_db: float = -80.0) -> np.ndarray:
    if samples is None:
        return samples
    was_1d = False
    if samples.ndim == 1:
        samples = samples[:, None]
        was_1d = True
    out = np.zeros_like(samples)
    n_fft = 1024
    hop = n_fft // 4
    for ch in range(samples.shape[1]):
        x = samples[:, ch]
        f, t, Zxx = signal.stft(x, fs=sr, nperseg=n_fft, noverlap=n_fft - hop)
        mag = np.abs(Zxx)
        ph = np.angle(Zxx)
        noise_est = np.percentile(mag, 10, axis=1, keepdims=True)
        reduction_lin = 10 ** (-reduction_db / 20.0)
        proc_mag = mag - noise_est * (1.0 - reduction_lin)
        proc_mag = np.maximum(proc_mag, 10 ** (noise_floor_db / 20.0))
        Zxx_proc = proc_mag * np.exp(1j * ph)
        _, x_rec = signal.istft(Zxx_proc, fs=sr, nperseg=n_fft, noverlap=n_fft - hop)
        if x_rec.shape[0] < x.shape[0]:
            x_rec = np.pad(x_rec, (0, x.shape[0] - x_rec.shape[0]))
        else:
            x_rec = x_rec[: x.shape[0]]
        out[:, ch] = x_rec
    if was_1d:
        out = out[:, 0]
    return out

def simple_reverb(samples: np.ndarray, sr: int, reverb_seconds: float = 0.25, mix: float = 0.2) -> np.ndarray:
    if samples is None:
        return samples
    n = int(sr * reverb_seconds)
    if n < 1:
        return samples
    ir = np.logspace(0, -3, n)
    ir *= np.random.normal(1.0, 0.01, size=ir.shape)
    was_1d = False
    if samples.ndim == 1:
        samples = samples[:, None]
        was_1d = True
    out = np.zeros((samples.shape[0] + n - 1, samples.shape[1]))
    for ch in range(samples.shape[1]):
        out[:, ch] = signal.fftconvolve(samples[:, ch], ir, mode='full')
    out = out[: samples.shape[0], :]
    out = (1 - mix) * samples + mix * out
    if was_1d:
        out = out[:, 0]
    return out

def simple_delay(samples: np.ndarray, sr: int, delay_ms: float = 150.0, feedback: float = 0.2, mix: float = 0.2) -> np.ndarray:
    if samples is None:
        return samples
    delay_samples = int(sr * (delay_ms / 1000.0))
    if delay_samples <= 0:
        return samples
    was_1d = False
    if samples.ndim == 1:
        samples = samples[:, None]
        was_1d = True
    out = np.copy(samples).astype(np.float64)
    buf = np.zeros((delay_samples + 1, samples.shape[1]))
    wp = 0
    for i in range(samples.shape[0]):
        delayed = buf[wp]
        buf[wp] = samples[i] + delayed * feedback
        out[i] = (1 - mix) * samples[i] + mix * delayed
        wp = (wp + 1) % buf.shape[0]
    if was_1d:
        out = out[:, 0]
    return out

def simple_chorus(samples: np.ndarray, sr: int, depth_ms: float = 10.0, rate_hz: float = 0.5, mix: float = 0.3) -> np.ndarray:
    if samples is None:
        return samples
    depth_samples = int(sr * (depth_ms / 1000.0))
    if depth_samples <= 0:
        return samples
    was_1d = False
    if samples.ndim == 1:
        samples = samples[:, None]
        was_1d = True
    out = np.copy(samples)
    t = np.arange(samples.shape[0]) / sr
    mod = depth_samples * (0.5 + 0.5 * np.sin(2 * np.pi * rate_hz * t))
    for ch in range(samples.shape[1]):
        for i in range(samples.shape[0]):
            delay_idx = int(i - mod[i])
            if delay_idx >= 0:
                out[i, ch] = (1 - mix) * samples[i, ch] + mix * samples[delay_idx, ch]
    if was_1d:
        out = out[:, 0]
    return out

def soft_clip_distortion(samples: np.ndarray, drive: float = 1.0, mix: float = 0.5) -> np.ndarray:
    if samples is None:
        return samples
    distorted = np.tanh(samples * drive) / np.tanh(drive)
    return (1 - mix) * samples + mix * distorted

def pan_samples(samples: np.ndarray, pan: float) -> np.ndarray:
    if samples is None:
        return samples
    if samples.ndim == 1:
        samples = np.vstack([samples, samples]).T
    if samples.shape[1] == 1:
        samples = np.hstack([samples, samples])
    angle = (pan + 1) * (np.pi / 4)
    left = np.cos(angle)
    right = np.sin(angle)
    out = np.zeros_like(samples[:, :2])
    out[:, 0] = samples[:, 0] * left
    out[:, 1] = samples[:, 1] * right
    return out

def highpass(samples: np.ndarray, sr: int, cutoff_hz: float) -> np.ndarray:
    if samples is None or cutoff_hz <= 0:
        return samples
    sos = signal.butter(4, cutoff_hz, btype='highpass', fs=sr, output='sos')
    return signal.sosfilt(sos, samples)

def lowpass(samples: np.ndarray, sr: int, cutoff_hz: float) -> np.ndarray:
    if samples is None or cutoff_hz <= 0:
        return samples
    sos = signal.butter(4, cutoff_hz, btype='lowpass', fs=sr, output='sos')
    return signal.sosfilt(sos, samples)

def compress(samples: np.ndarray, threshold_db: float = -24.0, ratio: float = 4.0, attack_ms: float = 10.0, release_ms: float = 100.0, sr: int = 44100) -> np.ndarray:
    if samples is None:
        return samples
    eps = 1e-9
    mono = samples if samples.ndim == 1 else samples.mean(axis=1)
    env = np.zeros_like(mono)
    alpha_a = np.exp(-1.0 / (0.001 * attack_ms * sr))
    alpha_r = np.exp(-1.0 / (0.001 * release_ms * sr))
    prev = 0.0
    for i, x in enumerate(mono):
        rect = abs(x)
        if rect > prev:
            prev = alpha_a * prev + (1 - alpha_a) * rect
        else:
            prev = alpha_r * prev + (1 - alpha_r) * rect
        env[i] = prev
    env_db = 20 * np.log10(env + eps)
    gain_db = np.minimum(0.0, -(env_db - threshold_db) * (1 - 1 / ratio))
    gain_lin = 10 ** (gain_db / 20.0)
    if samples.ndim == 1:
        return samples * gain_lin
    else:
        return samples * gain_lin[:, None]

def normalize(samples: np.ndarray, target_db: float = -1.0) -> np.ndarray:
    if samples is None:
        return samples
    peak = np.max(np.abs(samples))
    if peak <= 0:
        return samples
    target = 10 ** (target_db / 20.0)
    return samples * (target / peak)

def autogain(samples: np.ndarray, target_rms_db: float = -18.0) -> np.ndarray:
    if samples is None:
        return samples
    rms = np.sqrt(np.mean(samples.astype(np.float64) ** 2))
    if rms <= 0:
        return samples
    target = 10 ** (target_rms_db / 20.0)
    return samples * (target / rms)

def compute_metrics(samples: np.ndarray, sr: int):
    if samples is None or samples.size == 0:
        return {
            'duration': 0.0,
            'channels': 0,
            'sample_rate': sr,
            'peak_db': -np.inf,
            'rms_db': -np.inf,
            'crest_factor': 0.0,
            'dynamic_range_db': 0.0,
        }
    duration = samples.shape[0] / sr
    channels = 1 if samples.ndim == 1 else samples.shape[1]
    peak = np.max(np.abs(samples))
    rms = np.sqrt(np.mean(samples ** 2))
    peak_db = 20 * np.log10(peak + 1e-9)
    rms_db = 20 * np.log10(rms + 1e-9)
    crest_factor = peak / (rms + 1e-9)
    non_zero_samples = samples[samples != 0]
    min_val = np.min(np.abs(non_zero_samples)) if non_zero_samples.size > 0 else 1e-9
    dynamic_range_db = 20 * np.log10(peak / (min_val + 1e-9))
    return {
        'duration': duration,
        'channels': channels,
        'sample_rate': sr,
        'peak_db': peak_db,
        'rms_db': rms_db,
        'crest_factor': crest_factor,
        'dynamic_range_db': dynamic_range_db,
    }