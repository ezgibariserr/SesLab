
import tkinter as tk
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class OscilloscopeTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg="#FFFFFF")
        self.running = True

        self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=44100, blocksize=1024)
        self.stream.start()
        self.data = np.zeros(1024)

        # Grafik alanı
        self.fig, (self.ax_osc, self.ax_wave, self.ax_spec) = plt.subplots(3, 1, figsize=(10, 6), dpi=100)
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(pady=10)

        self.update_plot()

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.data = indata[:, 0]

    def update_plot(self):
        self.ax_osc.clear()
        self.ax_wave.clear()
        self.ax_spec.clear()

        # Osiloskop (Zaman domeninde)
        self.ax_osc.plot(self.data, color='lime')
        self.ax_osc.set_title("Canlı Osiloskop")
        self.ax_osc.set_ylim(-1, 1)

        # Dalga Formu (Zoom'lu)
        zoom = 100
        wave = self.data[:zoom] if len(self.data) > zoom else self.data
        self.ax_wave.plot(wave, color='blue')
        self.ax_wave.set_title("Canlı Dalga Formu")
        self.ax_wave.set_ylim(-1, 1)

        # Spektrogram
        self.ax_spec.specgram(self.data, NFFT=256, Fs=44100, noverlap=128, cmap="inferno")
        self.ax_spec.set_title("Canlı Spektrogram")

        self.canvas.draw()
        if self.running:
            self.after(200, self.update_plot)

    def configure_theme(self, bg, fg):
        self.configure(bg=bg)
        self.canvas.get_tk_widget().configure(bg=bg)

    def destroy(self):
        self.running = False
        self.stream.stop()
        self.stream.close()
        super().destroy()
