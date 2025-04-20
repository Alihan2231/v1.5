#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARP Spoofing Tespit Aracı - Spotify UI Versiyonu
Bu araç, ağda olası ARP spoofing saldırılarını tespit etmek için gerekli tüm fonksiyonları ve 
tkinter tabanlı Spotify tarzında bir grafik arayüz içerir.

Versiyon: 2.0 - Windows Uyumlu
"""

import os
import sys
import tkinter as tk
import traceback
from tkinter import messagebox

# Debug için
print("Program başlatılıyor...")

# Global değişkenler
root = None
app = None
icon = None
HAS_PYSTRAY = False

# Pystray için gerekli modüller
try:
    import PIL.Image
    import pystray
    HAS_PYSTRAY = True
    print("Pystray başarıyla import edildi.")
except ImportError:
    HAS_PYSTRAY = False
    print("Uyarı: pystray veya PIL modülü bulunamadı. Sistem tepsisi özellikleri devre dışı.")

# Diğer modüller
import socket
import re
import threading
import time
import subprocess
import logging
from collections import defaultdict

# Debug modu
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def create_system_tray():
    """Sistem tepsisi ikonu oluşturur"""
    print("Sistem tepsisi oluşturuluyor...")
    if not HAS_PYSTRAY:
        print("Pystray yok, sistem tepsisi oluşturulamıyor.")
        return
        
    global icon, root, app
    
    # Logo için PIL görüntüsü oluştur
    try:
        image_path = os.path.join(os.path.dirname(__file__), "assets", "shield.png")
        if os.path.exists(image_path):
            print(f"Logo bulundu: {image_path}")
            image = PIL.Image.open(image_path)
        else:
            print("Logo bulunamadı, basit bir görüntü oluşturuluyor.")
            # Basit bir siyah kare oluştur
            image = PIL.Image.new('RGB', (16, 16), color = (0, 0, 0))
    except Exception as e:
        print(f"Logo yüklenirken hata: {e}")
        # Hata durumunda basit bir görüntü oluştur
        image = PIL.Image.new('RGB', (16, 16), color = (0, 0, 0))
    
    # Menü işlevleri
    def show_window(icon, item):
        print("Pencereyi göster komutu alındı.")
        icon.stop()  # İkonu durdur
        root.after(0, root.deiconify)  # Ana pencereyi göster
    
    def exit_app(icon, item):
        print("Tamamen kapat komutu alındı.")
        # Periyodik taramayı durdur
        if hasattr(app, 'scanner'):
            app.scanner.stop_periodic_scan()
        icon.stop()  # İkonu durdur
        root.after(0, root.destroy)  # Uygulamayı tamamen kapat
    
    # Menü oluştur
    print("Sistem tepsisi menüsü oluşturuluyor...")
    menu = pystray.Menu(
        pystray.MenuItem("ARP Tarama Aracını Göster", show_window),
        pystray.MenuItem("Tamamen Kapat", exit_app)
    )
    
    # İkonu oluştur ve başlat
    print("Sistem tepsisi ikonu oluşturuluyor...")
    icon = pystray.Icon("arp_shield", image, "ARP Tarama Aracı (Arka planda çalışıyor)", menu)
    
    # İkonu ayrı bir thread'de başlat
    print("Sistem tepsisi ikonu thread'de başlatılıyor...")
    threading.Thread(target=icon.run, daemon=True).start()

def start_desktop_app():
    """Desktop uygulamasını başlatır"""
    try:
        print("Tkinter UI başlatılıyor...")
        
        global root, app, icon
        
        # UI modüllerini import etmeye çalışalım
        try:
            from ui.screens import SpotifyARPApp
            print("SpotifyARPApp başarıyla import edildi.")
        except Exception as e:
            print(f"SpotifyARPApp import edilirken hata: {e}")
            traceback.print_exc()
            messagebox.showerror("Hata", f"UI modülleri yüklenirken hata:\n{e}")
            return
        
        # Ayarları yüklemeyi dene
        try:
            from modules.settings import load_settings, get_setting
            settings = load_settings()
            print(f"Ayarlar yüklendi: {settings}")
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
            settings = {}  # Boş sözlük
        
        # Ana tkinter penceresini oluştur
        root = tk.Tk()
        root.title("ARP Spoofing Tespit Aracı")
        root.geometry("1000x650")
        root.minsize(800, 600)
        
        # Ana uygulama sınıfını oluştur
        try:
            print("SpotifyARPApp oluşturuluyor...")
            app = SpotifyARPApp(root)
            print("SpotifyARPApp başarıyla oluşturuldu!")
        except Exception as e:
            print(f"SpotifyARPApp oluşturulurken hata: {e}")
            traceback.print_exc()
            messagebox.showerror("Hata", f"Uygulama başlatılırken hata:\n{e}")
            return
        
        # Eğer periyodik tarama ayarı varsa, başlat
        try:
            if settings.get("periodic_scan_active", False):
                scan_interval = settings.get("scan_interval", 24)
                print(f"Önceki oturumdan periyodik tarama başlatılıyor... Aralık: {scan_interval}")
                # UI tam yüklendikten sonra periyodik taramayı başlat
                root.after(2000, lambda: app.start_periodic_scan(scan_interval))
        except Exception as e:
            print(f"Periyodik tarama başlatılırken hata: {e}")
        
        # Kapatma işlemi yeniden tanımla
        def on_close():
            print("Kapatma isteği alındı.")
            # Periyodik tarama aktif mi kontrol et
            periodic_active = False
            if hasattr(app, 'scanner'):
                periodic_active = getattr(app.scanner, 'periodic_running', False)
                print(f"Periyodik tarama aktif: {periodic_active}")
            
            if periodic_active:
                # Periyodik tarama aktifse
                if messagebox.askyesno("Kapat", "Periyodik tarama aktif. Uygulama kapatılsa bile arka planda çalışmaya devam edecektir.\n\nDevam etmek istiyor musunuz?"):
                    if HAS_PYSTRAY:
                        print("Pencere gizleniyor ve sistem tepsisine alınıyor.")
                        root.withdraw()  # Pencereyi gizle
                        create_system_tray()  # Sistem tepsisi oluştur
                    else:
                        # Pystray yoksa, kullanıcıya bilgi ver
                        print("Pystray yok, uygulama tamamen kapatılıyor.")
                        messagebox.showinfo("Bilgi", "Sistem tepsisi desteği olmadığı için uygulama tamamen kapatılacak.")
                        root.destroy()
            else:
                # Periyodik tarama aktif değilse normal kapat
                if messagebox.askyesno("Kapat", "Uygulamayı kapatmak istiyor musunuz?"):
                    print("Uygulama kapatılıyor.")
                    root.destroy()
        
        # Pencere kapatma olayını yakala
        root.protocol("WM_DELETE_WINDOW", on_close)
        
        # Ana döngüyü başlat
        print("Tkinter ana döngüsü başlatılıyor...")
        root.mainloop()
        print("Mainloop'dan çıkıldı.")
        
    except Exception as e:
        print(f"Uygulama başlatılırken hata: {e}")
        traceback.print_exc()
        messagebox.showerror("Hata", f"Uygulama başlatılırken hata:\n{e}")

if __name__ == "__main__":
    try:
        print("Ana program başlatılıyor...")
        start_desktop_app()
        print("Program sonlandı.")
    except Exception as e:
        print(f"Ana programda hata: {e}")
        traceback.print_exc()
        input("Devam etmek için Enter tuşuna basın...")