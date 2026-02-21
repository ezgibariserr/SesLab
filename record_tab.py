# record_tab.py
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sounddevice as sd
import soundfile as sf
import threading
import numpy as np
import queue
import time
from analysis_tab import AnalysisTab
from ui_constants import COLORS, FONTS  # UI sabitlerini yeni modülden import et

class RecordTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg=COLORS['background'])

        # Ses ayarları
        self.fs = 44100  # örnekleme hızı
        self.channels = 1  # mono
        self.chunk_duration = 0.05  # saniye başına parça
        self.chunk_samples = int(self.fs * self.chunk_duration)
        
        # Ses cihazları listesi
        self.devices = sd.query_devices()
        self.input_devices = []
        print("\nKullanılabilir ses cihazları:")
        for i, dev in enumerate(self.devices):
            if dev['max_input_channels'] > 0:
                print(f"{i}: {dev['name']} (maksimum kanal: {dev['max_input_channels']})")
                self.input_devices.append((i, dev['name']))

        self.stream_config = None
        self.is_recording = False
        self.recorded_frames = []
        self.recording_duration = 10  # 10 saniye kayıt süresi
        self.start_time = None

        # Ana konteyner - Gölgeli kart görünümü
        self.main_container = tk.Frame(
            self,
            bg=COLORS['card'],
            highlightbackground=COLORS['text_secondary'],
            highlightthickness=1
        )
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Kontrol Çerçevesi
        self.control_frame = tk.Frame(self.main_container, bg=COLORS['card'])
        self.control_frame.pack(side='left', fill='both', padx=20, pady=20)

        # Başlık
        tk.Label(
            self.control_frame,
            text="Ses Kayıt Paneli",
            font=FONTS['heading'],
            bg=COLORS['card'],
            fg=COLORS['text']
        ).pack(pady=(0, 20))

        # Kayıt butonu ve açıklaması
        self.record_description = tk.Label(
            self.control_frame,
            text="10 saniyelik ses kaydı almak için tıklayın",
            bg=COLORS['card'],
            fg=COLORS['text_secondary'],
            font=FONTS['body']
        )
        self.record_description.pack(pady=5)

        # Özel stil ile kayıt butonu
        self.record_button_frame = tk.Frame(
            self.control_frame,
            bg=COLORS['success'],
            highlightthickness=0
        )
        self.record_button_frame.pack(pady=10)
        
        self.record_button = tk.Button(
            self.record_button_frame,
            text="10 Saniye Kaydet",
            command=self.show_device_selection,
            bg=COLORS['success'],
            fg=COLORS['card'],
            width=20,
            height=2,
            font=FONTS['button'],
            relief='flat',
            activebackground=COLORS['primary'],
            activeforeground=COLORS['card'],
            cursor='hand2'
        )
        self.record_button.pack(padx=1, pady=1)

        # WAV dosyası yükleme butonu
        self.load_button_frame = tk.Frame(
            self.control_frame,
            bg=COLORS['primary'],
            highlightthickness=0
        )
        self.load_button_frame.pack(pady=10)
        
        self.load_button = tk.Button(
            self.load_button_frame,
            text="WAV Dosyası Yükle",
            command=self.load_wav_file,
            bg=COLORS['primary'],
            fg=COLORS['card'],
            width=20,
            height=2,
            font=FONTS['button'],
            relief='flat',
            activebackground=COLORS['secondary'],
            activeforeground=COLORS['card'],
            cursor='hand2'
        )
        self.load_button.pack(padx=1, pady=1)

        # Durum göstergesi
        self.status_label = tk.Label(
            self.control_frame,
            text="Kayıt için hazır",
            bg=COLORS['card'],
            fg=COLORS['text_secondary'],
            font=FONTS['body']
        )
        self.status_label.pack(pady=10)

        # Kalan süre göstergesi
        self.time_label = tk.Label(
            self.control_frame,
            text="",
            bg=COLORS['card'],
            fg=COLORS['primary'],
            font=FONTS['subheading']
        )
        self.time_label.pack(pady=5)

        # Analiz Çerçevesi
        self.analysis_tab = AnalysisTab(self.main_container)
        self.analysis_tab.pack(side='right', fill='both', expand=True)
        
        # Başlangıçta analiz sekmesini göster
        self.after(100, lambda: self.analysis_tab.notebook.select(0))

    def show_device_selection(self):
        device_window = tk.Toplevel(self)
        device_window.title("Mikrofon Seçimi")
        device_window.geometry("400x400")
        device_window.configure(bg=COLORS['background'])
        
        # Pencereyi merkeze konumlandır
        device_window.transient(self)
        device_window.grab_set()
        
        # Başlık
        tk.Label(
            device_window,
            text="Mikrofon Seçimi",
            bg=COLORS['background'],
            fg=COLORS['text'],
            font=FONTS['heading']
        ).pack(pady=(20, 5))
        
        tk.Label(
            device_window,
            text="Lütfen kullanmak istediğiniz mikrofonu seçin",
            bg=COLORS['background'],
            fg=COLORS['text_secondary'],
            font=FONTS['body']
        ).pack(pady=(0, 20))
        
        # Mikrofon listesi için kart görünümü
        list_frame = tk.Frame(
            device_window,
            bg=COLORS['card'],
            highlightbackground=COLORS['text_secondary'],
            highlightthickness=1
        )
        list_frame.pack(fill='both', expand=True, padx=20, pady=5)
        
        # Scrollbar ve Listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        device_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=FONTS['body'],
            selectmode='single',
            height=10,
            bg=COLORS['card'],
            fg=COLORS['text'],
            selectbackground=COLORS['primary'],
            selectforeground=COLORS['card'],
            relief='flat',
            highlightthickness=0
        )
        device_listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        scrollbar.config(command=device_listbox.yview)
        
        for idx, name in self.input_devices:
            device_listbox.insert('end', f"{name}")
        
        if device_listbox.size() > 0:
            device_listbox.select_set(0)
        
        def on_device_select():
            try:
                selection = device_listbox.curselection()[0]
                device_id = self.input_devices[selection][0]
                
                self.stream_config = {
                    'device': device_id,
                    'samplerate': self.fs,
                    'channels': self.channels,
                    'dtype': 'float32',
                    'blocksize': 1024,
                    'latency': 'high',
                    'clip_off': True
                }
                
                device_window.destroy()
                self.start_recording()
                
            except Exception as e:
                messagebox.showerror("Hata", f"Mikrofon seçiminde hata oluştu: {str(e)}")
                device_window.destroy()
        
        # Seçim butonu
        select_button_frame = tk.Frame(
            device_window,
            bg=COLORS['primary'],
            highlightthickness=0
        )
        select_button_frame.pack(pady=20)
        
        tk.Button(
            select_button_frame,
            text="Seçili Mikrofon ile Kaydet",
            command=on_device_select,
            bg=COLORS['primary'],
            fg=COLORS['card'],
            font=FONTS['button'],
            width=25,
            height=2,
            relief='flat',
            activebackground=COLORS['secondary'],
            activeforeground=COLORS['card'],
            cursor='hand2'
        ).pack(padx=1, pady=1)

    def update_timer(self):
        if self.is_recording and self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            remaining_time = max(0, self.recording_duration - elapsed_time)
            
            if remaining_time > 0:
                self.time_label.config(text=f"Kalan süre: {remaining_time:.1f} saniye")
                self.after(50, self.update_timer)
            else:
                self.stop_recording()

    def audio_callback(self, indata, frames, time, status):
        if status:
            print('Durum:', status)
        self.recorded_frames.append(indata.copy())

    def record_audio(self):
        try:
            self.start_time = time.time()
            self.update_timer()
            
            # Yeni ses akışı yapılandırması
            stream = sd.InputStream(**self.stream_config)
            stream.start()
            
            while self.is_recording:
                elapsed_time = time.time() - self.start_time
                if elapsed_time >= self.recording_duration:
                    self.is_recording = False
                    break
                    
                try:
                    data, overflowed = stream.read(self.chunk_samples)
                    if not overflowed:
                        self.recorded_frames.append(data)
                except Exception as e:
                    print(f"Okuma hatası: {str(e)}")
                    continue
                    
                self.after(10)
            
            stream.stop()
            stream.close()
                    
        except Exception as e:
            print(f"Kayıt hatası: {str(e)}")
            self.after(0, lambda: self.status_label.config(text=f"Hata: {str(e)}"))

    def process_recording(self):
        try:
            if not self.recorded_frames:
                self.status_label.config(text="Kaydedilecek ses verisi yok")
                return

            # Kayıt verilerini birleştir
            recording = np.vstack(self.recorded_frames)
            if recording.size > 0:
                recording = recording.flatten()
                # Normalize et
                if np.max(np.abs(recording)) > 0:
                    recording = recording / np.max(np.abs(recording))
                
                # WAV dosyasına kaydet
                filename = "kayit.wav"
                sf.write(filename, recording, self.fs)
                
                # Analiz sekmesine geç ve grafikleri güncelle
                self.show_analysis(filename)
            else:
                self.status_label.config(text="Geçerli ses verisi kaydedilemedi")
            
        except Exception as e:
            print(f"İşleme hatası: {str(e)}")
            self.status_label.config(text=f"Hata: {str(e)}")

    def show_analysis(self, filename):
        """Analiz sekmesini göster ve analizi başlat"""
        try:
            # Analiz sekmesini güncelle
            self.analysis_tab.load_and_analyze(filename)
            
            # Analiz sekmesine geç
            if isinstance(self.master, ttk.Notebook):
                self.master.select(1)  # Analiz sekmesi indeksi
            
        except Exception as e:
            messagebox.showerror("Hata", f"Analiz gösterilirken hata oluştu: {str(e)}")

    def start_recording(self):
        if self.stream_config is None:
            self.status_label.config(text="Ses ayarları yapılandırılamadı!")
            return
            
        self.is_recording = True
        self.recorded_frames = []
        self.status_label.config(text="Kayıt yapılıyor...")
        self.record_button.config(state="disabled")
        self.time_label.config(text="Başlatılıyor...")
        
        # Kayıt thread'ini başlat
        self.record_thread = threading.Thread(target=self.record_audio)
        self.record_thread.start()

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.status_label.config(text="Kayıt işleniyor...")
            self.time_label.config(text="")
            
            # Kayıt thread'inin bitmesini bekle
            if hasattr(self, 'record_thread'):
                self.record_thread.join()
            
            # Kayıt işleme ve analizi başlat
            self.process_recording()

    def configure_theme(self, bg, fg):
        self.configure(bg=bg)
        self.main_container.configure(bg=bg)
        self.control_frame.configure(bg=bg)
        self.record_description.configure(bg=bg, fg=fg)
        self.status_label.configure(bg=bg, fg=fg)
        self.time_label.configure(bg=bg, fg=fg)
        self.analysis_tab.configure_theme(bg, fg)

    def load_wav_file(self):
        """WAV dosyası yükleme fonksiyonu"""
        try:
            filename = filedialog.askopenfilename(
                title="WAV Dosyası Seç",
                filetypes=[("WAV files", "*.wav")]
            )
            
            if filename:
                # Dosyayı analiz için gönder
                self.show_analysis(filename)
                
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yüklenirken hata oluştu: {str(e)}")
