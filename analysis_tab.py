import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import soundfile as sf
from scipy import signal  # Spektrogram için
from ui_constants import COLORS, FONTS  # UI sabitlerini yeni modülden import et

class AnalysisTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg=COLORS['card'])
        
        # Başlık
        self.title_label = tk.Label(
            self,
            text="Ses Analizi",
            font=FONTS['heading'],
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        self.title_label.pack(pady=(20, 10))

        # Dosya yükleme butonu çerçevesi
        self.upload_frame = tk.Frame(
            self,
            bg=COLORS['primary'],
            highlightthickness=0
        )
        self.upload_frame.pack(pady=10)
        
        self.upload_button = tk.Button(
            self.upload_frame,
            text="WAV Dosyası Yükle",
            command=self.load_wav_file,
            bg=COLORS['primary'],
            fg=COLORS['card'],
            font=FONTS['button'],
            width=20,
            height=2,
            relief='flat',
            activebackground=COLORS['secondary'],
            activeforeground=COLORS['card'],
            cursor='hand2'
        )
        self.upload_button.pack(padx=1, pady=1)

        # Grafik alanı için çerçeve
        self.graph_frame = tk.Frame(
            self,
            bg=COLORS['card'],
            highlightbackground=COLORS['text_secondary'],
            highlightthickness=1
        )
        self.graph_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Grafik sekmeleri
        self.notebook = ttk.Notebook(self.graph_frame)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Spektrogram Sekmesi
        self.spec_frame = tk.Frame(self.notebook, bg=COLORS['card'])
        self.notebook.add(self.spec_frame, text='Spektrogram')
        
        # Dalga Formu Sekmesi
        self.wave_frame = tk.Frame(self.notebook, bg=COLORS['card'])
        self.notebook.add(self.wave_frame, text='Dalga Formu')
        
        # Frekans Spektrumu Sekmesi
        self.freq_frame = tk.Frame(self.notebook, bg=COLORS['card'])
        self.notebook.add(self.freq_frame, text='Frekans Spektrumu')

        # Stil ayarları
        style = ttk.Style()
        style.configure(
            "TNotebook",
            background=COLORS['card'],
            borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            padding=[10, 5],
            background=COLORS['background'],
            foreground=COLORS['text']
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS['primary'])],
            foreground=[("selected", COLORS['card'])]
        )

        # Durum etiketi
        self.status_label = tk.Label(
            self,
            text="Analiz için hazır",
            font=FONTS['body'],
            bg=COLORS['card'],
            fg=COLORS['text_secondary']
        )
        self.status_label.pack(pady=10)

    def load_wav_file(self):
        try:
            filename = filedialog.askopenfilename(
                title="WAV Dosyası Seç",
                filetypes=[("WAV files", "*.wav")]
            )
            
            if filename:
                self.load_and_analyze(filename)
        except Exception as e:
            self.status_label.config(
                text=f"Hata: {str(e)}",
                fg=COLORS['error']
            )

    def load_and_analyze(self, filename):
        """Dosyayı yükle ve analiz et"""
        try:
            self.status_label.config(
                text="Dosya yükleniyor...",
                fg=COLORS['primary']
            )
            self.update()
            
            data, samplerate = sf.read(filename)
            self.plot_spectrogram(data, samplerate)
            self.plot_waveform(data, samplerate)
            self.plot_frequency_spectrum(data, samplerate)
            
            self.status_label.config(
                text="Analiz tamamlandı",
                fg=COLORS['success']
            )
            
            # Spektrogram sekmesini seç
            self.notebook.select(0)
            
        except Exception as e:
            self.status_label.config(
                text=f"Hata: {str(e)}",
                fg=COLORS['error']
            )
            raise e

    def configure_theme(self, bg, fg):
        """Tema renklerini güncelle"""
        self.configure(bg=bg)
        self.title_label.configure(bg=bg, fg=fg)
        self.status_label.configure(bg=bg, fg=fg)
        self.graph_frame.configure(bg=bg)
        self.spec_frame.configure(bg=bg)
        self.wave_frame.configure(bg=bg)
        self.freq_frame.configure(bg=bg)

    def plot_spectrogram(self, data, samplerate):
        """Spektrogram çizimi"""
        # Önceki grafikleri temizle
        for widget in self.spec_frame.winfo_children():
            widget.destroy()

        # Yeni figür oluştur
        fig = Figure(figsize=(10, 6), dpi=100)
        fig.patch.set_facecolor(COLORS['card'])
        
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS['card'])
        
        # Spektrogram hesapla
        f, t, Sxx = signal.spectrogram(data, samplerate, 
                                     nperseg=1024,
                                     noverlap=512,
                                     window='hann',
                                     scaling='spectrum')
        
        # dB cinsinden güç spektral yoğunluğu
        Sxx_db = 10 * np.log10(Sxx + 1e-10)
        
        # Spektrogramı çiz
        im = ax.pcolormesh(t, f, Sxx_db, 
                          shading='gouraud',
                          cmap='viridis',
                          vmin=Sxx_db.max() - 60)  # Dinamik aralık: 60 dB
        
        # Colorbar ekle
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Güç/Frekans (dB/Hz)', color=COLORS['text'])
        cbar.ax.yaxis.set_tick_params(colors=COLORS['text'])
        
        ax.set_title('Spektrogram Analizi', color=COLORS['text'], pad=20)
        ax.set_xlabel('Zaman (s)', color=COLORS['text'])
        ax.set_ylabel('Frekans (Hz)', color=COLORS['text'])
        
        ax.tick_params(colors=COLORS['text'])
        
        for spine in ax.spines.values():
            spine.set_color(COLORS['text_secondary'])

        canvas = FigureCanvasTkAgg(fig, master=self.spec_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)

    def plot_waveform(self, data, samplerate):
        """Dalga formu çizimi"""
        # Önceki grafikleri temizle
        for widget in self.wave_frame.winfo_children():
            widget.destroy()

        # Yeni figür oluştur
        fig = Figure(figsize=(10, 4), dpi=100)
        fig.patch.set_facecolor(COLORS['card'])
        
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS['card'])
        
        time = np.arange(len(data)) / samplerate
        ax.plot(time, data, color=COLORS['primary'], linewidth=0.5)
        
        ax.set_title('Dalga Formu', color=COLORS['text'], pad=20)
        ax.set_xlabel('Zaman (s)', color=COLORS['text'])
        ax.set_ylabel('Genlik', color=COLORS['text'])
        
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.tick_params(colors=COLORS['text'])
        
        for spine in ax.spines.values():
            spine.set_color(COLORS['text_secondary'])

        canvas = FigureCanvasTkAgg(fig, master=self.wave_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)

    def plot_frequency_spectrum(self, data, samplerate):
        """Frekans spektrumu çizimi"""
        # Önceki grafikleri temizle
        for widget in self.freq_frame.winfo_children():
            widget.destroy()

        # Yeni figür oluştur
        fig = Figure(figsize=(10, 4), dpi=100)
        fig.patch.set_facecolor(COLORS['card'])
        
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS['card'])
        
        # FFT hesapla
        n = len(data)
        fft_data = np.fft.fft(data)
        freqs = np.fft.fftfreq(n, 1/samplerate)
        
        # Pozitif frekansları göster
        positive_mask = freqs >= 0
        freqs = freqs[positive_mask]
        magnitude = np.abs(fft_data[positive_mask])
        
        # dB cinsinden genlik spektrumu
        magnitude_db = 20 * np.log10(magnitude + 1e-10)
        
        ax.plot(freqs, magnitude_db, color=COLORS['secondary'], linewidth=1)
        
        ax.set_title('Frekans Spektrumu', color=COLORS['text'], pad=20)
        ax.set_xlabel('Frekans (Hz)', color=COLORS['text'])
        ax.set_ylabel('Genlik (dB)', color=COLORS['text'])
        
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.tick_params(colors=COLORS['text'])
        
        # Frekans eksenini sınırla
        ax.set_xlim(0, samplerate/2)
        
        for spine in ax.spines.values():
            spine.set_color(COLORS['text_secondary'])

        canvas = FigureCanvasTkAgg(fig, master=self.freq_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5) 