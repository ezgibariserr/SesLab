import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from login_register import LoginRegisterFrame
#from waveform_tab import WaveformTab
from oscilloscope_tab import OscilloscopeTab
from square_wave_tab import SquareWaveTab
from record_tab import RecordTab
from ui_constants import COLORS, FONTS
import sv_ttk  # Modern tema için
from PIL import Image, ImageTk
import os


class MainApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("SesLab - Ses Analiz ve İşleme Laboratuvarı")
        self.geometry("1200x800")  # Daha geniş pencere
        self.minsize(1000, 700)    # Minimum boyut
        
        # Modern tema uygula
        sv_ttk.set_theme("light")
        
        # Stil ayarları
        self._style = ttk.Style()
        self._style.theme_use("litera")
        
        # Pencereyi merkeze konumlandır
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1200) // 2
        y = (screen_height - 800) // 2
        self.geometry(f"1200x800+{x}+{y}")

        # Giriş ekranını oluştur
        self.login_frame = LoginRegisterFrame(self, self.launch_main_ui)
        self.login_frame.pack(fill="both", expand=True)
        
        self.main_content = None
        self.current_user = None
        self.current_lang = 'tr'  # Varsayılan dil

    def launch_main_ui(self, username=None):
        self.current_user = username
        self.login_frame.pack_forget()
        self.create_main_content()

    def create_main_content(self):
        # Ana içerik konteyneri
        self.main_content = ttk.Frame(self)
        self.main_content.pack(fill="both", expand=True)
        
        # Üst panel (header)
        self.create_header()
        
        # Ana içerik alanı
        self.create_content_area()

    def create_header(self):
        # Üst panel konteyneri
        header = ttk.Frame(self.main_content, style='Header.TFrame')
        header.pack(fill="x", pady=0)
        
        # Header stili
        self._style.configure('Header.TFrame', background=COLORS['primary'])
        
        # Logo ve başlık alanı
        title_frame = ttk.Frame(header, style='Header.TFrame')
        title_frame.pack(side="left", padx=20, pady=10)
        
        # Logo (placeholder)
        logo_canvas = tk.Canvas(
            title_frame,
            width=32,
            height=32,
            bg=COLORS['primary'],
            highlightthickness=0
        )
        logo_canvas.pack(side="left", padx=(0, 10))
        logo_canvas.create_oval(2, 2, 30, 30, fill="white", outline="")
        logo_canvas.create_text(16, 16, text="S", fill=COLORS['primary'], font=('Helvetica', 18, 'bold'))
        
        title_label = ttk.Label(
            title_frame,
            text="SesLab",
            font=('Helvetica', 20, 'bold'),
            foreground="white",
            style='Header.TLabel'
        )
        title_label.pack(side="left")
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Ses Analiz ve İşleme Laboratuvarı" if self.current_lang == 'tr' else "Sound Analysis and Processing Laboratory",
            font=('Helvetica', 12),
            foreground="white",
            style='Header.TLabel'
        )
        subtitle_label.pack(side="left", padx=10)
        
        # Sağ taraf araçları
        tools_frame = ttk.Frame(header, style='Header.TFrame')
        tools_frame.pack(side="right", padx=20, pady=10)
        
        # Dil seçimi
        lang_frame = ttk.Frame(tools_frame, style='Header.TFrame')
        lang_frame.pack(side="right", padx=10)
        
        tr_btn = ttk.Button(
            lang_frame,
            text="🇹🇷",
            style='Header.TButton',
            command=lambda: self.change_language('tr')
        )
        tr_btn.pack(side="left", padx=2)
        
        en_btn = ttk.Button(
            lang_frame,
            text="🇬🇧",
            style='Header.TButton',
            command=lambda: self.change_language('en')
        )
        en_btn.pack(side="left", padx=2)
        
        # Kullanıcı profili
        if self.current_user:
            user_frame = ttk.Frame(tools_frame, style='Header.TFrame')
            user_frame.pack(side="right", padx=10)
            
            # Profil ikonu
            profile_canvas = tk.Canvas(
                user_frame,
                width=24,
                height=24,
                bg=COLORS['primary'],
                highlightthickness=0
            )
            profile_canvas.pack(side="left", padx=(0, 5))
            profile_canvas.create_oval(2, 2, 22, 22, fill="white", outline="")
            profile_canvas.create_text(12, 12, text=self.current_user[0].upper(), fill=COLORS['primary'], font=('Helvetica', 12, 'bold'))
            
            user_label = ttk.Label(
                user_frame,
                text=f"{self.current_user}",
                font=FONTS['body'],
                foreground="white",
                style='Header.TLabel'
            )
            user_label.pack(side="left", padx=5)
        
        # Ayarlar butonu
        settings_btn = ttk.Button(
            tools_frame,
            text="⚙",
            style='Header.TButton',
            command=self.show_settings
        )
        settings_btn.pack(side="right", padx=5)
        
        # Yardım butonu
        help_btn = ttk.Button(
            tools_frame,
            text="?",
            style='Header.TButton',
            command=self.show_help
        )
        help_btn.pack(side="right", padx=5)
        
        # Çıkış butonu
        exit_btn = ttk.Button(
            tools_frame,
            text="←",
            style='Header.TButton',
            command=self.return_to_login
        )
        exit_btn.pack(side="right", padx=5)
        
        # Header buton stili
        self._style.configure('Header.TButton',
            font=('Helvetica', 12),
            foreground="black",
            background=COLORS['primary'],
            borderwidth=0,
            relief="flat",
            padding=5
        )
        self._style.configure('Header.TLabel',
            background=COLORS['primary']
        )
        
        # Buton hover efekti
        self._style.map('Header.TButton',
            background=[('active', COLORS['primary'])],
            foreground=[('active', 'black')]
        )

    def create_content_area(self):
        # Ana içerik alanı için konteyner
        content_frame = ttk.Frame(self.main_content, style='Content.TFrame')
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sekmeleri oluştur
        self.create_tabs(content_frame)

    def create_tabs(self, parent):
        # Sekme stili
        style = ttk.Style()
        style.configure(
            'Custom.TNotebook',
            background=COLORS['background']
        )
        style.configure(
            'Custom.TNotebook.Tab',
            padding=[20, 10],
            font=FONTS['body'],
            background=COLORS['background']
        )
        style.map('Custom.TNotebook.Tab',
            background=[('selected', COLORS['primary'])],
            foreground=[('selected', 'white')]
        )
        
        self.tabs = ttk.Notebook(
            parent,
            style='Custom.TNotebook'
        )
        self.tabs.pack(expand=True, fill="both")

        # Sekme içerikleri
        self.record_tab = RecordTab(self.tabs)
        self.osc_tab = OscilloscopeTab(self.tabs)
        self.square_tab = SquareWaveTab(self.tabs)

        self.tabs.add(self.record_tab, text="🎙 Ses Kayıt ve Analiz")
        self.tabs.add(self.osc_tab, text="📊 Canlı Osiloskop")
        self.tabs.add(self.square_tab, text="⚡ Sinyal Üreteci")
        
        # Başlangıçta kayıt sekmesini seç
        self.tabs.select(0)

    def change_language(self, lang):
        self.current_lang = lang
        # Dil değişikliği için gerekli güncellemeleri yap
        if self.main_content:
            self.main_content.destroy()
            self.create_main_content()

    def show_settings(self):
        # Ayarlar penceresi
        settings_window = ttk.Toplevel(self)
        settings_window.title("Ayarlar" if self.current_lang == 'tr' else "Settings")
        settings_window.geometry("400x300")
        
        # Pencereyi merkeze konumlandır
        settings_window.transient(self)
        settings_window.grab_set()
        
        # Ayarlar içeriği
        ttk.Label(
            settings_window,
            text="Ayarlar" if self.current_lang == 'tr' else "Settings",
            font=FONTS['heading']
        ).pack(pady=20)
        
        # Tema seçimi
        theme_frame = ttk.LabelFrame(
            settings_window,
            text="Tema" if self.current_lang == 'tr' else "Theme",
            padding=10
        )
        theme_frame.pack(fill="x", padx=20, pady=10)
        
        theme_var = ttk.StringVar(value="light")
        ttk.Radiobutton(
            theme_frame,
            text="Açık Tema" if self.current_lang == 'tr' else "Light Theme",
            value="light",
            variable=theme_var,
            command=lambda: sv_ttk.set_theme("light")
        ).pack(side="left", padx=10)
        
        ttk.Radiobutton(
            theme_frame,
            text="Koyu Tema" if self.current_lang == 'tr' else "Dark Theme",
            value="dark",
            variable=theme_var,
            command=lambda: sv_ttk.set_theme("dark")
        ).pack(side="left", padx=10)

    def show_help(self):
        # Yardım penceresi
        help_window = ttk.Toplevel(self)
        help_window.title("Yardım" if self.current_lang == 'tr' else "Help")
        help_window.geometry("600x400")
        
        # Pencereyi merkeze konumlandır
        help_window.transient(self)
        help_window.grab_set()
        
        # Yardım içeriği
        ttk.Label(
            help_window,
            text="SesLab Yardım" if self.current_lang == 'tr' else "SesLab Help",
            font=FONTS['heading']
        ).pack(pady=20)
        
        help_text_tr = """
        SesLab, ses analizi ve işleme için geliştirilmiş bir laboratuvar uygulamasıdır.
        
        Özellikler:
        • Ses Kayıt ve Analiz: Ses kaydı yapın ve detaylı analiz grafikleri görüntüleyin
        • Canlı Osiloskop: Gerçek zamanlı ses sinyallerini izleyin
        • Sinyal Üreteci: Özel ses sinyalleri oluşturun ve test edin
        
        Daha fazla bilgi için: https://seslab.com/docs
        """
        
        help_text_en = """
        SesLab is a laboratory application developed for sound analysis and processing.
        
        Features:
        • Sound Recording and Analysis: Record sound and view detailed analysis graphs
        • Live Oscilloscope: Monitor real-time audio signals
        • Signal Generator: Create and test custom audio signals
        
        For more information: https://seslab.com/docs
        """
        
        ttk.Label(
            help_window,
            text=help_text_tr if self.current_lang == 'tr' else help_text_en,
            font=FONTS['body'],
            justify="left",
            wraplength=500
        ).pack(padx=20, pady=10)

    def return_to_login(self):
        if self.main_content:
            self.main_content.destroy()
            self.main_content = None
        
        self.current_user = None
        self.login_frame.username_var.set("")
        self.login_frame.password_var.set("")
        self.login_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
