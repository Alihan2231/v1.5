#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spotify stili özel arayüz bileşenleri
Bu modül, uygulamanın Spotify tarzı özel arayüz bileşenlerini içerir.
"""

import tkinter as tk
from tkinter import ttk, font
import traceback
import time
import math
from ui.colors import THEME, get_status_color
import random
import os
import logging

# Loglama
logger = logging.getLogger("NetworkShieldPro.custom_widgets")

class RoundedFrame(tk.Canvas):
    """Yuvarlatılmış köşeli çerçeve"""
    def __init__(self, parent, bg=THEME["card_background"], width=200, height=100, 
                 corner_radius=THEME["radius_medium"], **kwargs):
        super().__init__(parent, bg=THEME["background"], highlightthickness=0, 
                          width=width, height=height, **kwargs)
        self.corner_radius = corner_radius
        self.bg = bg
        
        # Yuvarlatılmış dikdörtgen çiz
        self._draw_rounded_rect()
        
        # Boyut değiştiğinde yeniden çiz
        self.bind("<Configure>", self._on_resize)
    
    def _draw_rounded_rect(self):
        """Yuvarlatılmış dikdörtgen çizer"""
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        
        # Boyutlar çok küçükse çizme
        if width < 1 or height < 1:
            return
        
        # Köşe yarıçapı boyutlara göre ayarla
        radius = min(self.corner_radius, width//2, height//2)
        
        # Yuvarlatılmış dikdörtgen
        self.create_rounded_rectangle(0, 0, width, height, radius=radius, fill=self.bg, outline="")
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
        """Yuvarlatılmış dikdörtgen oluşturur"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_resize(self, event):
        """Boyut değiştiğinde yeniden çizer"""
        self._draw_rounded_rect()

class SpotifyButton(tk.Canvas):
    """Spotify tarzı buton"""
    def __init__(self, parent, text="Buton", command=None, bg=THEME["primary"], fg=THEME["text_primary"],
                 width=120, height=40, corner_radius=THEME["radius_small"], 
                 hover_color=THEME["hover_primary"], active_color=THEME["active_primary"], **kwargs):
        super().__init__(parent, bg=THEME["background"], highlightthickness=0, 
                          width=width, height=height, **kwargs)
        self.text = text
        self.command = command
        self.normal_color = bg
        self.hover_color = hover_color
        self.active_color = active_color
        self.fg = fg
        self.corner_radius = corner_radius
        self.state = "normal"
        
        # Buton çiz
        self._draw_button()
        
        # Etkileşim için event'leri bağla
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", self._on_resize)
    
    def _draw_button(self):
        """Butonu çizer"""
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        
        # Boyutlar çok küçükse çizme
        if width < 1 or height < 1:
            return
        
        # Köşe yarıçapı boyutlara göre ayarla
        radius = min(self.corner_radius, width//2, height//2)
        
        # Buton rengi
        if self.state == "disabled":
            color = THEME["secondary"]
        elif self.state == "active":
            color = self.active_color
        elif self.state == "hover":
            color = self.hover_color
        else:
            color = self.normal_color
        
        # Yuvarlatılmış dikdörtgen
        self.create_rounded_rectangle(0, 0, width, height, radius=radius, fill=color, outline="")
        
        # Metin
        text_color = self.fg
        if self.state == "disabled":
            text_color = THEME["text_disabled"]
        
        self.create_text(width//2, height//2, text=self.text, fill=text_color, 
                         font=("Arial", 11, "bold"))
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
        """Yuvarlatılmış dikdörtgen oluşturur"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        """Üzerine gelince rengini değiştirir"""
        if self.state != "disabled":
            self.state = "hover"
            self._draw_button()
    
    def _on_leave(self, event):
        """Üzerinden ayrılınca rengini değiştirir"""
        if self.state != "disabled":
            self.state = "normal"
            self._draw_button()
    
    def _on_press(self, event):
        """Tıklandığında aktif duruma geçer"""
        if self.state != "disabled":
            self.state = "active"
            self._draw_button()
    
    def _on_release(self, event):
        """Tıklama bırakılınca fonksiyonu çalıştırır"""
        if self.state != "disabled":
            x, y = event.x, event.y
            if 0 <= x <= self.winfo_width() and 0 <= y <= self.winfo_height():
                if self.command:
                    try:
                        self.command()
                    except Exception as e:
                        logger.error(f"Buton komutu çalıştırılırken hata: {e}")
                        traceback.print_exc()
                self.state = "hover"
            else:
                self.state = "normal"
            self._draw_button()
    
    def _on_resize(self, event):
        """Boyut değiştiğinde yeniden çizer"""
        self._draw_button()
    
    def configure(self, **kwargs):
        """Buton özelliklerini yapılandırır"""
        if "text" in kwargs:
            self.text = kwargs.pop("text")
        if "command" in kwargs:
            self.command = kwargs.pop("command")
        if "state" in kwargs:
            self.state = kwargs.pop("state")
        if "bg" in kwargs:
            self.normal_color = kwargs.pop("bg")
        if "fg" in kwargs:
            self.fg = kwargs.pop("fg")
        
        super().configure(**kwargs)
        self._draw_button()

class CircularProgressbar(tk.Canvas):
    """Dairesel ilerleme çubuğu"""
    def __init__(self, parent, width=100, height=100, progress=0, thickness=8, 
                 bg_color=THEME["secondary"], fg_color=THEME["primary"], **kwargs):
        super().__init__(parent, width=width, height=height, bg=THEME["background"], 
                         highlightthickness=0, **kwargs)
        self.progress = min(max(progress, 0), 100)  # 0-100 arası
        self.thickness = thickness
        self.bg_color = bg_color
        self.fg_color = fg_color
        
        self._draw_progressbar()
        
        # Boyut değiştiğinde yeniden çiz
        self.bind("<Configure>", self._on_resize)
    
    def _draw_progressbar(self):
        """Dairesel ilerleme çubuğunu çizer"""
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        
        # Boyutlar çok küçükse çizme
        if width < 1 or height < 1:
            return
        
        # Merkez ve yarıçap
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2 - self.thickness
        
        # Arka plan daire
        self.create_arc(center_x - radius, center_y - radius,
                       center_x + radius, center_y + radius,
                       start=0, extent=359.999, style=tk.ARC,
                       width=self.thickness, outline=self.bg_color)
        
        # İlerleme dairesi
        if self.progress > 0:
            extent = 359.999 * (self.progress / 100.0)
            self.create_arc(center_x - radius, center_y - radius,
                           center_x + radius, center_y + radius,
                           start=90, extent=-extent, style=tk.ARC,
                           width=self.thickness, outline=self.fg_color)
        
        # İlerleme yüzdesi
        self.create_text(center_x, center_y, text=f"{int(self.progress)}%", 
                         font=("Arial", 14, "bold"), fill=THEME["text_primary"])
    
    def set_progress(self, progress):
        """İlerleme değerini ayarlar ve yeniden çizer"""
        self.progress = min(max(progress, 0), 100)
        self._draw_progressbar()
    
    def _on_resize(self, event):
        """Boyut değiştiğinde yeniden çizer"""
        self._draw_progressbar()

class ParticleAnimationCanvas(tk.Canvas):
    """Arka plan parçacık animasyonu"""
    def __init__(self, parent, width=800, height=600, num_particles=30, **kwargs):
        super().__init__(parent, width=width, height=height, bg=THEME["background"], 
                         highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.num_particles = num_particles
        self.particles = []
        self.running = False
        
        # Parçacıkları oluştur
        self._create_particles()
    
    def _create_particles(self):
        """Parçacıkları oluşturur"""
        self.particles = []
        for _ in range(self.num_particles):
            # Rastgele parçacık özellikleri
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(2, 6)
            speed = random.uniform(0.2, 1.0)
            direction = random.uniform(0, 2 * math.pi)
            opacity = random.uniform(0.1, 0.5)
            
            # Yeşil tonlarında rastgele renk
            color_r = random.randint(0, 40)
            color_g = random.randint(180, 255)
            color_b = random.randint(0, 40)
            color = f'#{color_r:02x}{color_g:02x}{color_b:02x}'
            
            self.particles.append({
                'x': x,
                'y': y,
                'size': size,
                'speed': speed,
                'direction': direction,
                'color': color,
                'opacity': opacity,
                'id': None  # Canvas üzerindeki id
            })
    
    def start_animation(self):
        """Animasyonu başlatır"""
        self.running = True
        self._animate()
    
    def stop_animation(self):
        """Animasyonu durdurur"""
        self.running = False
    
    def _animate(self):
        """Parçacık animasyonunu günceller"""
        if not self.running:
            return
        
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        
        for particle in self.particles:
            # Parçacığı hareket ettir
            particle['x'] += particle['speed'] * math.cos(particle['direction'])
            particle['y'] += particle['speed'] * math.sin(particle['direction'])
            
            # Ekrandan çıkınca yeniden konumlandır
            if particle['x'] < -10 or particle['x'] > width + 10 or \
               particle['y'] < -10 or particle['y'] > height + 10:
                particle['x'] = random.randint(0, width)
                particle['y'] = random.randint(0, height)
                particle['direction'] = random.uniform(0, 2 * math.pi)
            
            # Parçacığı çiz
            size = particle['size']
            x, y = particle['x'], particle['y']
            
            # Opaklık ayarı için renk hesapla
            r, g, b = int(particle['color'][1:3], 16), int(particle['color'][3:5], 16), int(particle['color'][5:7], 16)
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            # Parçacığı çiz (oval)
            self.create_oval(x-size, y-size, x+size, y+size, 
                             fill=color, outline='', 
                             stipple='gray50' if particle['opacity'] < 0.5 else '')
        
        # Sonraki kareyi planla
        if self.running:
            self.after(40, self._animate)  # ~25 FPS
    
    def resize(self, width, height):
        """Canvas boyutunu değiştirir"""
        self.width = width
        self.height = height
        self.config(width=width, height=height)

class SidebarItem(tk.Frame):
    """Spotify tarzı kenar çubuğu öğesi"""
    def __init__(self, parent, icon, text, command=None, is_active=False, **kwargs):
        super().__init__(parent, bg=THEME["sidebar_background"], 
                         height=50, **kwargs)
        self.command = command
        self.is_active = is_active
        
        # El işaretçisi göster
        self.configure(cursor="hand2")
        
        # İkon ve metin
        self.icon_label = tk.Label(self, text=icon, font=("Arial", 20), 
                                  bg=THEME["sidebar_background"],
                                  fg=THEME["primary"] if is_active else THEME["text_secondary"],
                                  cursor="hand2")  # El işaretçisi göster
        self.icon_label.pack(side=tk.LEFT, padx=(20, 10))
        
        self.text_label = tk.Label(self, text=text, font=("Arial", 12), 
                                 bg=THEME["sidebar_background"],
                                 fg=THEME["text_primary"] if is_active else THEME["text_secondary"],
                                 cursor="hand2")  # El işaretçisi göster
        self.text_label.pack(side=tk.LEFT, fill=tk.Y)
        
        # Sol kenar işaretleyicisi (aktif durumda)
        self.indicator = tk.Canvas(self, width=4, height=50, bg=THEME["sidebar_background"], highlightthickness=0)
        self.indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0))
        
        if is_active:
            self._draw_active_indicator()
        
        # Etkileşimler
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.icon_label.bind("<Button-1>", self._on_click)
        self.text_label.bind("<Button-1>", self._on_click)
        self.indicator.bind("<Button-1>", self._on_click)
    
    def _draw_active_indicator(self):
        """Aktif durum göstergesini çizer"""
        self.indicator.delete("all")
        if self.is_active:
            self.indicator.create_rectangle(0, 5, 4, 45, fill=THEME["primary"], outline="")
    
    def _on_enter(self, event):
        """Üzerine gelince stilini değiştirir"""
        if not self.is_active:
            self.config(bg=THEME["card_background"])
            self.icon_label.config(bg=THEME["card_background"])
            self.text_label.config(bg=THEME["card_background"])
            self.indicator.config(bg=THEME["card_background"])
    
    def _on_leave(self, event):
        """Üzerinden ayrılınca stilini geri döndürür"""
        if not self.is_active:
            self.config(bg=THEME["sidebar_background"])
            self.icon_label.config(bg=THEME["sidebar_background"])
            self.text_label.config(bg=THEME["sidebar_background"])
            self.indicator.config(bg=THEME["sidebar_background"])
    
    def _on_click(self, event):
        """Tıklandığında komutu çalıştırır"""
        if self.command:
            try:
                print(f"Sidebar item tıklandı: {self.text_label['text']}")  # Debug log
                self.command()
            except Exception as e:
                # Python 'traceback' modulünü import et
                import traceback
                print(f"Sidebar item tıklanması sırasında hata: {e}")
                traceback.print_exc()
    
    def set_active(self, active):
        """Aktif durumu değiştirir"""
        self.is_active = active
        
        if active:
            self.text_label.config(fg=THEME["text_primary"])
            self.icon_label.config(fg=THEME["primary"])
            self._draw_active_indicator()
            
            # Aktif durumda hover efekti kaldır
            self.config(bg=THEME["sidebar_background"])
            self.icon_label.config(bg=THEME["sidebar_background"])
            self.text_label.config(bg=THEME["sidebar_background"])
            self.indicator.config(bg=THEME["sidebar_background"])
        else:
            self.text_label.config(fg=THEME["text_secondary"])
            self.icon_label.config(fg=THEME["text_secondary"])
            self.indicator.delete("all")

class StatusBadge(tk.Canvas):
    """Durum rozeti"""
    def __init__(self, parent, text="", status="none", width=80, height=24, 
                 corner_radius=THEME["radius_small"], **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=THEME["background"], highlightthickness=0, **kwargs)
        self.text = text
        self.status = status
        self.corner_radius = corner_radius
        
        self._draw_badge()
        
        # Boyut değiştiğinde yeniden çiz
        self.bind("<Configure>", self._on_resize)
    
    def _draw_badge(self):
        """Durum rozetini çizer"""
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        
        # Boyutlar çok küçükse çizme
        if width < 1 or height < 1:
            return
        
        # Köşe yarıçapı boyutlara göre ayarla
        radius = min(self.corner_radius, height//2)
        
        # Durum rengini al
        color = get_status_color(self.status)
        
        # Yuvarlatılmış dikdörtgen (arka plan)
        self.create_rounded_rectangle(0, 0, width, height, radius=radius, 
                                     fill=color, outline="")
        
        # Metin
        self.create_text(width//2, height//2, text=self.text, 
                        fill=THEME["text_primary"], font=("Arial", 10, "bold"))
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
        """Yuvarlatılmış dikdörtgen oluşturur"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def set_status(self, text, status="none"):
        """Durum metnini ve rengini günceller"""
        self.text = text
        self.status = status
        self._draw_badge()
    
    def _on_resize(self, event):
        """Boyut değiştiğinde yeniden çizer"""
        self._draw_badge()

class AnimatedChart(tk.Canvas):
    """Animasyonlu çubuk grafik"""
    def __init__(self, parent, data=None, width=400, height=200, bar_width=30, 
                 padding=40, animation_duration=THEME["animation_slow"], **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=THEME["background"], highlightthickness=0, **kwargs)
        self.data = data or []  # (etiket, değer, renk) tuple'larının listesi
        self.bar_width = bar_width
        self.padding = padding
        self.animation_duration = animation_duration
        self.current_values = []  # Animasyon için geçici değerler
        
        self._draw_chart()
        
        # Boyut değiştiğinde yeniden çiz
        self.bind("<Configure>", self._on_resize)
    
    def _draw_chart(self):
        """Çubuk grafiği çizer"""
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        
        # Boyutlar çok küçükse çizme
        if width < 1 or height < 1 or not self.data:
            return
        
        # Y ekseni sınırları
        max_value = max(entry[1] for entry in self.data) if self.data else 1
        max_value = max(max_value, 1)  # Sıfıra bölünmeyi önle
        
        # Çizim alanı
        chart_height = height - 2 * self.padding
        chart_width = width - 2 * self.padding
        
        # Çubukların toplam genişliği
        total_bar_width = len(self.data) * self.bar_width
        # Çubuklar arası boşluk
        spacing = (chart_width - total_bar_width) / (len(self.data) + 1)
        
        # X ekseni çizgisi
        self.create_line(self.padding, height - self.padding, 
                        width - self.padding, height - self.padding, 
                        fill=THEME["border"], width=1)
        
        # Geçici değerler listesini ilk kez oluştur
        if not self.current_values:
            self.current_values = [0] * len(self.data)
        
        # Her çubuğu çiz
        for i, (label, value, color) in enumerate(self.data):
            # X pozisyonu
            x = self.padding + spacing * (i + 1) + i * self.bar_width
            
            # Y ekseni değeri (şu anki animasyon değeri)
            current_value = self.current_values[i]
            bar_height = (current_value / max_value) * chart_height
            
            # Çubuğu çiz
            self.create_rectangle(x, height - self.padding - bar_height, 
                                x + self.bar_width, height - self.padding, 
                                fill=color, outline="")
            
            # Etiketi çiz
            self.create_text(x + self.bar_width / 2, height - self.padding + 15, 
                           text=label, fill=THEME["text_secondary"], 
                           font=("Arial", 10))
            
            # Değeri çiz
            if current_value > 0:
                self.create_text(x + self.bar_width / 2, height - self.padding - bar_height - 10, 
                               text=str(int(current_value)), fill=THEME["text_primary"], 
                               font=("Arial", 10, "bold"))
    
    def set_data(self, data):
        """Grafik verilerini günceller ve animasyonu başlatır"""
        old_data = self.data
        self.data = data
        
        # Eğer önceki veri yoksa, animasyonsuz direkt çiz
        if not old_data or not self.current_values:
            self.current_values = [entry[1] for entry in data]
            self._draw_chart()
            return
        
        # Animasyon için hedef değerler
        target_values = [entry[1] for entry in data]
        
        # Mevcut değerleri uygun uzunluğa getir
        if len(self.current_values) < len(target_values):
            self.current_values.extend([0] * (len(target_values) - len(self.current_values)))
        elif len(self.current_values) > len(target_values):
            self.current_values = self.current_values[:len(target_values)]
        
        # Animasyonu başlat
        self._start_animation(target_values)
    
    def _start_animation(self, target_values):
        """Çubuk animasyonunu başlatır"""
        start_time = time.time()
        duration = self.animation_duration / 1000  # saniye cinsinden
        
        def update_animation():
            nonlocal start_time
            
            # Geçen süre
            elapsed = time.time() - start_time
            progress = min(elapsed / duration, 1.0)
            
            # Ease-out fonksiyonu
            progress = 1 - (1 - progress) ** 2
            
            # Değerleri güncelle
            all_done = True
            for i, target in enumerate(target_values):
                current = self.current_values[i]
                new_value = current + (target - current) * progress
                self.current_values[i] = new_value
                
                # Hedefe ulaşılıp ulaşılmadığını kontrol et
                if abs(new_value - target) > 0.1:
                    all_done = False
            
            # Grafiği güncelle
            self._draw_chart()
            
            # Animasyon tamamlanmadıysa devam et
            if not all_done and progress < 1:
                self.after(16, update_animation)  # ~60 FPS
            else:
                # Son duruma getir
                self.current_values = target_values.copy()
                self._draw_chart()
        
        # Animasyonu başlat
        update_animation()
    
    def _on_resize(self, event):
        """Boyut değiştiğinde yeniden çizer"""
        self._draw_chart()


class SpotifyCheckbox(tk.Canvas):
    """Spotify tarzı onay kutusu (checkbox)"""
    def __init__(self, parent, text="", command=None, checked=False, 
                 width=300, height=30, **kwargs):
        super().__init__(parent, bg=THEME["background"], highlightthickness=0, 
                         width=width, height=height, **kwargs)
        self.text = text
        self.command = command
        self.checked = checked
        self.hover = False
        
        # Checkbox çiz
        self._draw_checkbox()
        
        # Etkileşim için event'leri bağla
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", self._on_resize)
    
    def _draw_checkbox(self):
        """Checkbox'ı çizer"""
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        
        # Boyutlar çok küçükse çizme
        if width < 20 or height < 20:
            return
        
        # Kutucuk boyutu ve pozisyonu
        box_size = min(20, height - 4)
        box_x = 5
        box_y = height // 2 - box_size // 2
        
        # Arkaplan rengi
        bg_color = THEME["hover_secondary"] if self.hover else THEME["secondary"]
        
        # Kutucuk çiz (yuvarlatılmış köşeli dikdörtgen)
        radius = min(4, box_size // 4)
        box_rect = self.create_rounded_rectangle(
            box_x, box_y,
            box_x + box_size, box_y + box_size,
            radius=radius, fill=bg_color, outline=""
        )
        
        # İşaretliyse tik işareti çiz
        if self.checked:
            # Tik işareti için noktalar (tick mark)
            padding = box_size // 4
            self.create_line(
                box_x + padding, box_y + box_size // 2,
                box_x + box_size // 3, box_y + box_size - padding,
                box_x + box_size - padding, box_y + padding,
                fill=THEME["primary"], width=2, smooth=True
            )
        
        # Metin
        text_x = box_x + box_size + 10
        text_y = height // 2
        self.create_text(
            text_x, text_y,
            text=self.text, anchor="w",
            fill=THEME["text_primary"],
            font=("Arial", 11)
        )
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
        """Yuvarlatılmış dikdörtgen oluşturur"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        """Fare üzerine gelince efekt uygula"""
        self.hover = True
        self._draw_checkbox()
    
    def _on_leave(self, event):
        """Fare ayrılınca normal haline döndür"""
        self.hover = False
        self._draw_checkbox()
    
    def _on_click(self, event):
        """Tıklandığında durumu değiştir"""
        self.checked = not self.checked
        self._draw_checkbox()
        if self.command:
            try:
                self.command()
            except Exception as e:
                logger.error(f"Checkbox komutu çalıştırılırken hata: {e}")
                traceback.print_exc()
    
    def _on_resize(self, event):
        """Boyut değiştiğinde yeniden çizer"""
        self._draw_checkbox()
    
    def is_checked(self):
        """Checkbox'ın durumunu döndürür"""
        return self.checked
    
    def set_checked(self, checked):
        """Checkbox'ın durumunu ayarlar"""
        self.checked = checked
        self._draw_checkbox()
    
    def configure(self, **kwargs):
        """Checkbox özelliklerini yapılandırır"""
        if "text" in kwargs:
            self.text = kwargs.pop("text")
        if "command" in kwargs:
            self.command = kwargs.pop("command")
            
        super().configure(**kwargs)
        self._draw_checkbox()


class SpotifyCombobox(tk.Frame):
    """Spotify tarzı açılır menü (combobox)"""
    def __init__(self, parent, values=None, default=None, command=None, 
                 width=120, height=30, **kwargs):
        super().__init__(parent, bg=THEME["background"], **kwargs)
        
        if values is None:
            values = []
        
        self.values = values
        self.command = command
        self.current_value = default if default in values else (values[0] if values else "")
        self.dropdown_visible = False
        self.hover = False
        
        # Ana çerçeve boyutlarını ayarla
        self.config(width=width, height=height)
        
        # Açılır menü buton alanı
        self.button_canvas = tk.Canvas(
            self, bg=THEME["background"], 
            highlightthickness=0, 
            width=width, height=height
        )
        self.button_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Dropdown menü penceresi (başlangıçta gizli)
        self.dropdown_frame = None
        
        # Buton görünümünü çiz
        self._draw_button()
        
        # Etkileşim için event'leri bağla
        self.button_canvas.bind("<Enter>", self._on_enter)
        self.button_canvas.bind("<Leave>", self._on_leave)
        self.button_canvas.bind("<Button-1>", self._on_click)
        self.button_canvas.bind("<Configure>", self._on_resize)
    
    def _draw_button(self):
        """Açılır menü butonunu çizer"""
        self.button_canvas.delete("all")
        width = self.button_canvas.winfo_width()
        height = self.button_canvas.winfo_height()
        
        # Boyutlar çok küçükse çizme
        if width < 10 or height < 10:
            return
        
        # Arkaplan rengi
        bg_color = THEME["hover_secondary"] if self.hover else THEME["secondary"]
        
        # Yuvarlatılmış dikdörtgen arkaplan
        radius = min(height // 4, 5)
        self.button_canvas.create_rounded_rectangle(
            0, 0, width, height,
            radius=radius, fill=bg_color, outline=""
        )
        
        # Seçili değer metni
        text_width = width - 25  # Ok ikon için yer bırak
        self.button_canvas.create_text(
            10, height // 2,
            text=self.current_value, anchor="w",
            fill=THEME["text_primary"], 
            font=("Arial", 11),
            width=text_width
        )
        
        # Aşağı ok ikonu
        arrow_x = width - 15
        arrow_y = height // 2
        arrow_size = 6
        self.button_canvas.create_polygon(
            arrow_x - arrow_size, arrow_y - arrow_size // 2,
            arrow_x + arrow_size, arrow_y - arrow_size // 2,
            arrow_x, arrow_y + arrow_size // 2,
            fill=THEME["text_secondary"]
        )
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
        """Yuvarlatılmış dikdörtgen oluşturur"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        """Fare üzerine gelince efekt uygula"""
        self.hover = True
        self._draw_button()
    
    def _on_leave(self, event):
        """Fare ayrılınca normal haline döndür"""
        self.hover = False
        self._draw_button()
    
    def _on_click(self, event):
        """Tıklandığında dropdown menüyü göster/gizle"""
        if self.dropdown_visible:
            self._hide_dropdown()
        else:
            self._show_dropdown()
    
    def _on_resize(self, event):
        """Boyut değiştiğinde yeniden çizer"""
        self._draw_button()
    
    def _show_dropdown(self):
        """Dropdown menüyü göster"""
        if self.dropdown_frame:
            self._hide_dropdown()
            return
        
        # Dropdown için yeni bir toplevel pencere oluştur
        self.dropdown_frame = tk.Toplevel(self)
        self.dropdown_frame.overrideredirect(True)  # Başlık çubuğunu gizle
        
        # Butonun konumunu al ve dropdown'u altına yerleştir
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        width = self.winfo_width()
        
        # Dropdown pozisyonunu ayarla
        self.dropdown_frame.geometry(f"{width}x{len(self.values) * 30}+{x}+{y}")
        
        # Dropdown arkaplanı
        dropdown_bg = tk.Canvas(
            self.dropdown_frame, 
            bg=THEME["card_background"],
            highlightthickness=0,
            width=width,
            height=len(self.values) * 30
        )
        dropdown_bg.pack(fill=tk.BOTH, expand=True)
        
        # Değerler için butonlar oluştur
        for i, value in enumerate(self.values):
            # Değer butonu için frame
            item_y = i * 30
            item_frame = tk.Frame(
                dropdown_bg, 
                bg=THEME["card_background"],
                width=width,
                height=30
            )
            item_frame.place(x=0, y=item_y)
            
            # Değer metni
            value_label = tk.Label(
                item_frame, 
                text=value,
                bg=THEME["card_background"],
                fg=THEME["text_primary"],
                font=("Arial", 11),
                anchor="w",
                padx=10
            )
            value_label.pack(fill=tk.BOTH, expand=True)
            
            # Fare efektleri
            def on_enter(e, frame=item_frame):
                frame.config(bg=THEME["hover_secondary"])
                for widget in frame.winfo_children():
                    widget.config(bg=THEME["hover_secondary"])
            
            def on_leave(e, frame=item_frame):
                frame.config(bg=THEME["card_background"])
                for widget in frame.winfo_children():
                    widget.config(bg=THEME["card_background"])
            
            # Değer seçimi
            def on_select(selected_value=value):
                self.current_value = selected_value
                self._hide_dropdown()
                self._draw_button()
                if self.command:
                    try:
                        self.command(selected_value)
                    except Exception as e:
                        logger.error(f"Combobox seçim hatası: {e}")
                        traceback.print_exc()
            
            # Etkileşim için event'leri bağla
            item_frame.bind("<Enter>", on_enter)
            item_frame.bind("<Leave>", on_leave)
            item_frame.bind("<Button-1>", lambda e, sv=value: on_select(sv))
            value_label.bind("<Enter>", on_enter)
            value_label.bind("<Leave>", on_leave)
            value_label.bind("<Button-1>", lambda e, sv=value: on_select(sv))
        
        # Dropdown dışına tıklandığında kapat
        def on_click_outside(event):
            x, y = event.x_root, event.y_root
            dropdown_x = self.dropdown_frame.winfo_rootx()
            dropdown_y = self.dropdown_frame.winfo_rooty()
            dropdown_width = self.dropdown_frame.winfo_width()
            dropdown_height = self.dropdown_frame.winfo_height()
            
            if not (dropdown_x <= x <= dropdown_x + dropdown_width and
                    dropdown_y <= y <= dropdown_y + dropdown_height):
                self._hide_dropdown()
        
        # Fare tıklamasını yakalama
        self.root_click_binding = self.winfo_toplevel().bind("<Button-1>", on_click_outside, add="+")
        
        self.dropdown_visible = True
    
    def _hide_dropdown(self):
        """Dropdown menüyü gizle"""
        if self.dropdown_frame:
            # Event binding'i kaldır
            if hasattr(self, 'root_click_binding'):
                self.winfo_toplevel().unbind("<Button-1>", self.root_click_binding)
            
            # Dropdown'u kapat
            self.dropdown_frame.destroy()
            self.dropdown_frame = None
            self.dropdown_visible = False
    
    def get(self):
        """Mevcut seçili değeri döndürür"""
        return self.current_value
    
    def set(self, value):
        """Seçili değeri ayarlar"""
        if value in self.values:
            self.current_value = value
            self._draw_button()
            return True
        return False
