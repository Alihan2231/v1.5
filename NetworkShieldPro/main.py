#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NetworkShieldPro - ARP Spoofing Tespit ve Koruma Uygulaması
Bu uygulama, ağda meydana gelen ARP spoofing saldırılarını tespit eder.

Özellikler:
- Ağ üzerinde ARP paketlerini izleme
- Şüpheli ARP hareketlerini tespit etme
- Periyodik tarama özelliği
- Sistem tepsisi desteği
- Türkçe arayüz
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import threading
import traceback
import logging
import json
import atexit

# Pystray için PIL kütüphanesini import et
try:
    import PIL.Image
    from pystray import Icon, Menu, MenuItem
    SYSTEM_TRAY_AVAILABLE = True
except ImportError:
    SYSTEM_TRAY_AVAILABLE = False
    print("Sistem tepsisi desteği için PIL ve pystray kütüphaneleri gereklidir.")

# Modüller için path ayarlaması
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("networkshieldpro.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NetworkShieldPro")

class NetworkShieldProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetworkShieldPro")
        self.root.geometry("1024x700")
        self.root.minsize(800, 600)
        
        # Pencere dekorasyonlarını kaldır (standart başlık çubuğunu gizle)
        self.root.overrideredirect(True)
        
        # Ana pencere kapatma olayını yakala
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Sistem tepsisi ikonu
        self.system_tray_icon = None
        self.app_visible = True
        
        try:
            from ui.colors import THEME
            # Pencere rengini ayarla
            self.root.configure(bg=THEME["background"])
            
            # Özel başlık çubuğunu oluştur
            self._create_custom_titlebar()
            
            # Uygulamayı başlat
            from ui.screens import SpotifyARPApp
            self.app = SpotifyARPApp(self.root)
            
            # Sistem tepsisi ikonunu oluştur
            if SYSTEM_TRAY_AVAILABLE:
                self.setup_system_tray()
                
            # Auto tarama ayarını kontrol et
            self.check_auto_scan_setting()
                
        except Exception as e:
            logger.error(f"Uygulama başlatılırken hata: {e}")
            traceback.print_exc()
            messagebox.showerror("Başlatma Hatası", 
                f"Uygulama başlatılırken bir hata oluştu:\n{str(e)}")
    
    def setup_system_tray(self):
        """Sistem tepsisi ikonunu hazırlar"""
        try:
            # SVG ikon dosyası yerine kod ile oluşturulmuş basit bir ikon kullan
            width = 64
            height = 64
            image = PIL.Image.new('RGBA', (width, height), (0, 0, 0, 0))
            
            # Kalkan şekli çiz
            from PIL import ImageDraw
            draw = ImageDraw.Draw(image)
            
            # Kalkan şekli (yeşil tonda)
            shield_color = (0, 180, 120, 255)  # Yeşil tonu
            draw.polygon([(width//2, 5), (width-5, height//3), 
                         (width-15, height-10), (width//2, height-5),
                         (15, height-10), (5, height//3)], 
                         fill=shield_color)
            
            # Kalkan içine kilit ikonu ekle
            lock_color = (40, 40, 40, 255)  # Koyu gri
            draw.rectangle([width//3, height//2, 2*width//3, 3*height//4], fill=lock_color)
            draw.rectangle([width//4, height//3, 3*width//4, height//2], fill=lock_color)
            
            # Menü öğelerini oluştur
            menu = Menu(
                MenuItem("Göster", self.show_app),
                MenuItem("Ağı Tara", self.start_scan),
                MenuItem("Periyodik Tarama", Menu(
                    MenuItem("Başlat", self.start_periodic_scan, checked=lambda _: self.is_periodic_active()),
                    MenuItem("Durdur", self.stop_periodic_scan)
                )),
                MenuItem("Çıkış", self.quit_app)
            )
            
            # Sistem tepsisi ikonunu oluştur
            self.system_tray_icon = Icon("networkshieldpro", image, "NetworkShieldPro", menu)
            
            # Arka planda sistem tepsisi ikonunu göster
            threading.Thread(target=self.system_tray_icon.run, daemon=True).start()
            
            logger.info("Sistem tepsisi ikonu başarıyla oluşturuldu")
        except Exception as e:
            logger.error(f"Sistem tepsisi ikonu oluşturulurken hata: {e}")
            traceback.print_exc()
    
    def _create_custom_titlebar(self):
        """Özel siyah başlık çubuğu oluşturur"""
        from ui.colors import THEME
        
        # Başlık çubuğu frame'i
        self.titlebar = tk.Frame(self.root, bg=THEME["card_background"], height=30)
        self.titlebar.pack(side=tk.TOP, fill=tk.X)
        
        # SVG ikon
        try:
            import cairosvg
            import io
            from PIL import Image, ImageTk
            
            # SVG dosyasını oku ve PNG'ye dönüştür
            svg_data = open("assets/icons/app_icon.svg", "rb").read()
            png_data = cairosvg.svg2png(bytestring=svg_data, output_width=20, output_height=20)
            
            # PNG verisini PIL Image'e dönüştür
            icon_image = Image.open(io.BytesIO(png_data))
            icon_photo = ImageTk.PhotoImage(icon_image)
            
            # İkon etiketi
            self.icon_label = tk.Label(self.titlebar, image=icon_photo, bg=THEME["card_background"])
            self.icon_label.image = icon_photo  # Referansı koru
            self.icon_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            logger.error(f"İkon yüklenirken hata: {e}")
            # İkon yükleme başarısız olursa basit bir etiket göster
            self.icon_label = tk.Label(self.titlebar, text="🛡️", bg=THEME["card_background"], 
                                      fg=THEME["primary"], font=("Arial", 12, "bold"))
            self.icon_label.pack(side=tk.LEFT, padx=10)
        
        # Başlık metni
        self.title_label = tk.Label(self.titlebar, text="NetworkShieldPro - ARP Koruması", 
                                  bg=THEME["card_background"], fg=THEME["text_primary"],
                                  font=("Arial", 10, "bold"))
        self.title_label.pack(side=tk.LEFT, pady=5)
        
        # Pencere kontrol butonları için frame
        self.buttons_frame = tk.Frame(self.titlebar, bg=THEME["card_background"])
        self.buttons_frame.pack(side=tk.RIGHT, padx=5)
        
        # Minimize butonu
        self.minimize_btn = tk.Label(self.buttons_frame, text="─", bg=THEME["card_background"], 
                                   fg=THEME["text_primary"], font=("Arial", 12), width=2, cursor="hand2")
        self.minimize_btn.pack(side=tk.LEFT, padx=5)
        self.minimize_btn.bind("<Button-1>", lambda e: self.hide_app())
        self.minimize_btn.bind("<Enter>", lambda e: self.minimize_btn.config(
            bg=THEME["secondary"], fg=THEME["primary"]))
        self.minimize_btn.bind("<Leave>", lambda e: self.minimize_btn.config(
            bg=THEME["card_background"], fg=THEME["text_primary"]))
        
        # Kapat butonu
        self.close_btn = tk.Label(self.buttons_frame, text="×", bg=THEME["card_background"], 
                                 fg=THEME["text_primary"], font=("Arial", 12), width=2, cursor="hand2")
        self.close_btn.pack(side=tk.LEFT, padx=5)
        self.close_btn.bind("<Button-1>", lambda e: self.on_close())
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.config(
            bg="#e81123", fg="white"))  # Kırmızı arka plan ve beyaz metin
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.config(
            bg=THEME["card_background"], fg=THEME["text_primary"]))
        
        # Sürükleme ve bırakma kontrolü için değişkenler
        self._x = 0
        self._y = 0
        
        # Pencereyi sürükleme işlevselliği
        self.titlebar.bind("<ButtonPress-1>", self._start_drag)
        self.titlebar.bind("<ButtonRelease-1>", self._stop_drag)
        self.titlebar.bind("<B1-Motion>", self._on_motion)
        
        # Başlık etiketini de sürüklenebilir yap
        self.title_label.bind("<ButtonPress-1>", self._start_drag)
        self.title_label.bind("<ButtonRelease-1>", self._stop_drag)
        self.title_label.bind("<B1-Motion>", self._on_motion)
        
        # İkon etiketini de sürüklenebilir yap
        self.icon_label.bind("<ButtonPress-1>", self._start_drag)
        self.icon_label.bind("<ButtonRelease-1>", self._stop_drag)
        self.icon_label.bind("<B1-Motion>", self._on_motion)
    
    def _start_drag(self, event):
        """Pencere sürükleme başlatma"""
        self._x = event.x
        self._y = event.y
    
    def _stop_drag(self, event):
        """Pencere sürükleme durdurma"""
        self._x = None
        self._y = None
    
    def _on_motion(self, event):
        """Pencere sürükleme hareketi"""
        if self._x is not None and self._y is not None:
            x = self.root.winfo_x() + (event.x - self._x)
            y = self.root.winfo_y() + (event.y - self._y)
            self.root.geometry(f"+{x}+{y}")
            
    def is_periodic_active(self):
        """Periyodik taramanın aktif olup olmadığını kontrol eder"""
        try:
            return hasattr(self.app, 'scanner') and self.app.scanner.periodic_running
        except:
            return False
    
    def show_app(self, icon=None, item=None):
        """Uygulamayı gösterir"""
        self.app_visible = True
        self.root.deiconify()
        self.root.state('normal')
        self.root.lift()
        self.root.focus_force()

    def hide_app(self):
        """Uygulamayı gizler (sistem tepsisine küçültür)"""
        self.app_visible = False
        self.root.withdraw()
    
    def start_scan(self, icon=None, item=None):
        """Manuel tarama başlatır"""
        try:
            if hasattr(self.app, 'start_scan'):
                self.app.start_scan()
                logger.info("Manuel tarama başlatıldı")
        except Exception as e:
            logger.error(f"Tarama başlatılırken hata: {e}")
    
    def start_periodic_scan(self, icon=None, item=None):
        """Periyodik taramayı başlatır"""
        try:
            if hasattr(self.app, 'start_periodic_scan'):
                success = self.app.start_periodic_scan()
                if success:
                    logger.info("Periyodik tarama başlatıldı")
                else:
                    logger.warning("Periyodik tarama başlatılamadı")
        except Exception as e:
            logger.error(f"Periyodik tarama başlatılırken hata: {e}")
    
    def stop_periodic_scan(self, icon=None, item=None):
        """Periyodik taramayı durdurur"""
        try:
            if hasattr(self.app, 'stop_periodic_scan'):
                success = self.app.stop_periodic_scan()
                if success:
                    logger.info("Periyodik tarama durduruldu")
                else:
                    logger.warning("Periyodik tarama durdurulamadı")
        except Exception as e:
            logger.error(f"Periyodik tarama durdurulurken hata: {e}")
    
    def check_auto_scan_setting(self):
        """Auto scan ayarını kontrol eder ve gerekirse otomatik başlatır"""
        try:
            from modules.settings import get_setting
            auto_scan = get_setting("auto_scan", False)
            
            if auto_scan and hasattr(self.app, 'start_periodic_scan'):
                logger.info("Otomatik tarama ayarı aktif, periyodik tarama başlatılıyor")
                self.app.start_periodic_scan()
        except Exception as e:
            logger.error(f"Auto scan ayarı kontrol edilirken hata: {e}")
    
    def quit_app(self, icon=None, item=None):
        """Uygulamadan çıkar"""
        self.cleanup()
        if self.system_tray_icon:
            self.system_tray_icon.stop()
        self.root.quit()
        sys.exit(0)
    
    def cleanup(self):
        """Çıkış öncesi temizlik işlemleri"""
        try:
            # Tarayıcıyı durdur
            if hasattr(self.app, 'scanner'):
                # Periyodik durumu kaydet
                from modules.settings import set_setting
                periodic_active = hasattr(self.app.scanner, 'periodic_running') and self.app.scanner.periodic_running
                set_setting("periodic_scan_active", periodic_active)
                
                # Tarayıcıyı durdur
                if hasattr(self.app.scanner, 'stop') and callable(self.app.scanner.stop):
                    self.app.scanner.stop()
                
                # Periyodik tarayıcıyı durdur
                if hasattr(self.app.scanner, 'stop_periodic_scan') and callable(self.app.scanner.stop_periodic_scan):
                    self.app.scanner.stop_periodic_scan()
            
            logger.info("Uygulama temizlik işlemleri tamamlandı")
        except Exception as e:
            logger.error(f"Temizlik işlemleri sırasında hata: {e}")
    
    def on_close(self):
        """Pencere kapatıldığında çağrılır"""
        if SYSTEM_TRAY_AVAILABLE and messagebox.askyesno(
            "Küçült", 
            "Uygulamayı sistem tepsisine küçültmek ister misiniz?\n\n"
            "Hayır'ı seçerseniz uygulama tamamen kapatılacaktır."
        ):
            self.hide_app()
        else:
            self.quit_app()


def main():
    try:
        # Ana pencereyi oluştur
        root = tk.Tk()
        
        # Pencereyi ekranın ortasında konumlandır
        window_width = 1024
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        # Pencereyi merkeze konumlandır
        root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        app = NetworkShieldProApp(root)
        
        # Çıkışta temizlik yap
        atexit.register(app.cleanup)
        
        # Ana döngüyü başlat
        root.mainloop()
    except Exception as e:
        logger.critical(f"Kritik hata oluştu: {e}")
        traceback.print_exc()
        messagebox.showerror("Kritik Hata", 
            f"Uygulama çalışırken kritik bir hata oluştu:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
