import tkinter as tk
import numpy as np
import sounddevice as sd

class SquareWaveTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg="#FFFFFF")
        self.freq = tk.DoubleVar(value=440.0)
        self.duration = 1.0  # seconds

        tk.Label(self, text="Frekans (Hz):", bg="#FFFFFF").pack(pady=5)
        self.freq_entry = tk.Entry(self, textvariable=self.freq)
        self.freq_entry.pack(pady=5)

        self.play_button = tk.Button(self, text="Sinyal Üret", command=self.play_square_wave)
        self.play_button.pack(pady=10)

    def play_square_wave(self):
        fs = 44100  # sampling rate
        t = np.linspace(0, self.duration, int(fs * self.duration), endpoint=False)
        waveform = 0.5 * np.sign(np.sin(2 * np.pi * self.freq.get() * t))
        sd.play(waveform, fs)

    def configure_theme(self, bg, fg):
        self.configure(bg=bg)
        self.play_button.configure(bg=bg, fg=fg)
        self.freq_entry.configure(bg=bg, fg=fg, insertbackground=fg)
