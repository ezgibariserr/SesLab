import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from PIL import Image, ImageTk, ImageDraw
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui_constants import COLORS, FONTS

USER_DB = "users.json"

# Dil çevirileri
TRANSLATIONS = {
    'tr': {
        'title': 'SesLab',
        'subtitle': 'Ses Analiz ve İşleme Laboratuvarı',
        'username': 'Kullanıcı Adı',
        'password': 'Şifre',
        'login': 'Giriş Yap',
        'register': 'Kayıt Ol',
        'copyright': '© 2024 SesLab. Tüm hakları saklıdır.',
        'fill_all': 'Lütfen tüm alanları doldurun.',
        'password_short': 'Şifre en az 6 karakter olmalıdır.',
        'user_exists': 'Bu kullanıcı adı zaten alınmış.',
        'login_success': 'Giriş başarılı! Yönlendiriliyorsunuz...',
        'login_error': 'Geçersiz kullanıcı adı veya şifre.',
        'register_success': 'Kayıt başarılı! Giriş yapabilirsiniz.'
    },
    'en': {
        'title': 'SesLab',
        'subtitle': 'Sound Analysis and Processing Laboratory',
        'username': 'Username',
        'password': 'Password',
        'login': 'Login',
        'register': 'Register',
        'copyright': '© 2024 SesLab. All rights reserved.',
        'fill_all': 'Please fill in all fields.',
        'password_short': 'Password must be at least 6 characters.',
        'user_exists': 'This username is already taken.',
        'login_success': 'Login successful! Redirecting...',
        'login_error': 'Invalid username or password.',
        'register_success': 'Registration successful! You can now login.'
    }
}

class LoginRegisterFrame(ttk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success
        
        # Varsayılan dil
        self.current_lang = tk.StringVar(value='tr')
        
        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.is_register = tk.BooleanVar(value=False)
        
        # Style Configuration
        self.style = ttk.Style()
        
        # Gradient arka plan için canvas
        self.canvas = tk.Canvas(
            self,
            highlightthickness=0
        )
        self.canvas.place(relwidth=1, relheight=1)
        self.draw_gradient()
        
        # Ana konteyner
        self.main_container = ttk.Frame(self)
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Dil seçimi
        self.create_language_selector()
        
        # Giriş kartı
        self.login_card = ttk.Frame(
            self.main_container,
            style='LoginCard.TFrame',
            padding=40
        )
        self.login_card.pack(padx=20, pady=20)
        
        # Kart stili
        self.style.configure('LoginCard.TFrame',
            background='white',
            relief='solid',
            borderwidth=0
        )
        
        # Gölge efekti
        self.style.configure('Shadow.TFrame',
            background='#00000022'
        )
        
        # Gölge frame'leri
        for i in range(3):
            shadow = ttk.Frame(
                self.main_container,
                style='Shadow.TFrame'
            )
            shadow.place(
                relx=0.5,
                rely=0.5,
                anchor="center",
                width=self.login_card.winfo_reqwidth() + (i * 2),
                height=self.login_card.winfo_reqheight() + (i * 2),
                x=i+2,
                y=i+2
            )
        
        self.create_widgets()
        
        # Pencere boyutu değiştiğinde gradient'i güncelle
        self.bind('<Configure>', lambda e: self.draw_gradient())

    def draw_gradient(self):
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return
            
        # Gradient renkleri
        color1 = COLORS['primary']
        color2 = COLORS['secondary']
        
        # RGB değerlerini al
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # Gradient görüntüsü oluştur
        gradient_img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(gradient_img)
        
        for y in range(height):
            r = r1 + (r2 - r1) * y // height
            g = g1 + (g2 - g1) * y // height
            b = b1 + (b2 - b1) * y // height
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        self.gradient_img = ImageTk.PhotoImage(gradient_img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.gradient_img)

    def create_language_selector(self):
        # Dil seçimi için çerçeve
        lang_frame = ttk.Frame(self)
        lang_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        
        # TR butonu
        tr_btn = ttk.Button(
            lang_frame,
            text="🇹🇷 TR",
            style='Lang.TButton',
            command=lambda: self.change_language('tr')
        )
        tr_btn.pack(side="left", padx=2)
        
        # Ayraç
        ttk.Label(
            lang_frame,
            text="|",
            foreground='white'
        ).pack(side="left", padx=5)
        
        # EN butonu
        en_btn = ttk.Button(
            lang_frame,
            text="🇬🇧 EN",
            style='Lang.TButton',
            command=lambda: self.change_language('en')
        )
        en_btn.pack(side="left", padx=2)
        
        # Dil butonları için stil
        self.style.configure('Lang.TButton',
            font=('Helvetica', 10, 'bold'),
            foreground='black',
            background='transparent',
            borderwidth=0,
            relief="flat",
            padding=5
        )
        self.style.map('Lang.TButton',
            background=[('active', '#ffffff22')],
            foreground=[('active', 'black')]
        )

    def create_widgets(self):
        # Logo ve başlık
        logo_frame = ttk.Frame(self.login_card)
        logo_frame.pack(fill="x", pady=(0, 30))
        
        # Logo
        canvas = tk.Canvas(
            logo_frame,
            width=80,
            height=80,
            highlightthickness=0,
            bg='white'
        )
        canvas.pack()
        
        # Daire logo
        canvas.create_oval(
            10, 10, 70, 70,
            fill=COLORS['primary'],
            outline=COLORS['secondary'],
            width=2
        )
        canvas.create_text(
            40, 40,
            text="S",
            fill='white',
            font=('Helvetica', 36, 'bold')
        )
        
        # Başlık
        title_label = ttk.Label(
            logo_frame,
            text=TRANSLATIONS[self.current_lang.get()]['title'],
            font=('Helvetica', 28, 'bold'),
            foreground=COLORS['primary']
        )
        title_label.pack()
        
        # Alt başlık
        subtitle_label = ttk.Label(
            logo_frame,
            text=TRANSLATIONS[self.current_lang.get()]['subtitle'],
            font=('Helvetica', 12),
            foreground=COLORS['text_secondary']
        )
        subtitle_label.pack()
        
        # Giriş formu
        form_frame = ttk.Frame(self.login_card)
        form_frame.pack(fill="x", pady=20)
        
        # Kullanıcı adı
        username_frame = ttk.Frame(form_frame)
        username_frame.pack(fill="x", pady=5)
        
        self.username_label = ttk.Label(
            username_frame,
            text=TRANSLATIONS[self.current_lang.get()]['username'],
            font=FONTS['body'],
            foreground=COLORS['text']
        )
        self.username_label.pack(anchor="w")
        
        username_entry = ttk.Entry(
            username_frame,
            textvariable=self.username_var,
            font=FONTS['body'],
            style='Custom.TEntry'
        )
        username_entry.pack(fill="x", pady=5)
        
        # Şifre
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill="x", pady=5)
        
        self.password_label = ttk.Label(
            password_frame,
            text=TRANSLATIONS[self.current_lang.get()]['password'],
            font=FONTS['body'],
            foreground=COLORS['text']
        )
        self.password_label.pack(anchor="w")
        
        password_entry = ttk.Entry(
            password_frame,
            textvariable=self.password_var,
            show="•",
            font=FONTS['body'],
            style='Custom.TEntry'
        )
        password_entry.pack(fill="x", pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(self.login_card)
        button_frame.pack(fill="x", pady=20)
        
        # Giriş butonu
        self.login_button = ttk.Button(
            button_frame,
            text=TRANSLATIONS[self.current_lang.get()]['login'],
            style='Auth.TButton',
            command=self.login
        )
        self.login_button.pack(fill="x", pady=5)
        
        # Kayıt butonu
        self.register_button = ttk.Button(
            button_frame,
            text=TRANSLATIONS[self.current_lang.get()]['register'],
            style='Auth.TButton',
            command=self.register
        )
        self.register_button.pack(fill="x", pady=5)
        
        # Alt bilgi
        self.footer_text = ttk.Label(
            self.login_card,
            text=TRANSLATIONS[self.current_lang.get()]['copyright'],
            font=('Helvetica', 8),
            foreground=COLORS['text_secondary']
        )
        self.footer_text.pack(pady=(20, 0))
        
        # Entry stil ayarları
        self.style.configure('Custom.TEntry',
            padding=10,
            relief='solid',
            borderwidth=1,
            background='white'
        )
        
        # Buton stilleri
        self.style.configure('Auth.TButton',
            font=FONTS['button'],
            padding=10,
            relief='flat',
            borderwidth=1,
            background=COLORS['primary'],
            foreground='black'
        )
        self.style.map('Auth.TButton',
            foreground=[('active', 'black')],
            background=[('active', COLORS['secondary'])]
        )

    def change_language(self, lang):
        self.current_lang.set(lang)
        self.update_texts()

    def update_texts(self):
        lang = self.current_lang.get()
        texts = TRANSLATIONS[lang]
        
        # Başlık güncelleme
        for widget in self.login_card.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        if child.cget('text') == TRANSLATIONS['tr']['title'] or \
                           child.cget('text') == TRANSLATIONS['en']['title']:
                            child.configure(text=texts['title'])
                        elif child.cget('text') == TRANSLATIONS['tr']['subtitle'] or \
                             child.cget('text') == TRANSLATIONS['en']['subtitle']:
                            child.configure(text=texts['subtitle'])
        
        # Form etiketleri
        self.username_label.configure(text=texts['username'])
        self.password_label.configure(text=texts['password'])
        
        # Butonlar
        self.login_button.configure(text=texts['login'])
        self.register_button.configure(text=texts['register'])
        
        # Alt bilgi
        self.footer_text.configure(text=texts['copyright'])

    def show_message(self, message_key, is_error=False):
        lang = self.current_lang.get()
        message = TRANSLATIONS[lang][message_key]
        if is_error:
            messagebox.showerror("Hata" if lang == 'tr' else "Error", message)
        else:
            messagebox.showinfo("Bilgi" if lang == 'tr' else "Information", message)

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            self.show_message('fill_all', True)
            return
        
        users = self.load_users()
        if username in users and users[username] == password:
            self.show_message('login_success')
            self.on_login_success(username)
        else:
            self.show_message('login_error', True)

    def register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            self.show_message('fill_all', True)
            return
            
        if len(password) < 6:
            self.show_message('password_short', True)
            return
        
        users = self.load_users()
        if username in users:
            self.show_message('user_exists', True)
            return
        
        users[username] = password
        self.save_users(users)
        self.show_message('register_success')

    def load_users(self):
        if os.path.exists(USER_DB):
            with open(USER_DB, 'r') as f:
                return json.load(f)
        return {}

    def save_users(self, users):
        with open(USER_DB, 'w') as f:
            json.dump(users, f)
