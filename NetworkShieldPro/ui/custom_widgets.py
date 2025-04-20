#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spotify stili özel arayüz bileşenleri
Bu modül, uygulamanın Spotify tarzı özel arayüz bileşenlerini içerir.
"""

import tkinter as tk
from tkinter import ttk
import traceback
import time
import math
from ui.colors import THEME, get_status_color
import random

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
        """Tıklandığında"""
        if self.command is not None:
            try:
                self.command()
            except Exception as e:
                print(f"Sidebar item tıklanması sırasında hata: {e}")
                import traceback
                traceback.print_exc()
    
    def _on_release(self, event):
        """Tıklama bırakılınca fonksiyonu çalıştırır"""
        if self.state != "disabled":
            x, y = event.x, event.y
            if 0 <= x <= self.winfo_width() and 0 <= y <= self.winfo_height():
                if self.command:
                    self.command()
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
    def __init__(self, parent, width, height, num_particles=30, **kwargs):
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
            self.after(50, self._animate)
    
    def resize(self, width, height):
        """Canvas boyutunu değiştirir"""
        self.width = width
        self.height = height
        self.configure(width=width, height=height)
        
        # Mevcut parçacıkları yeniden konumlandır
        for particle in self.particles:
            particle['x'] = random.randint(0, width)
            particle['y'] = random.randint(0, height)

class AnimatedChart(tk.Canvas):
    """Animasyonlu çubuk grafik"""
    def __init__(self, parent, width=400, height=200, title="Grafik", **kwargs):
        super().__init__(parent, width=width, height=height, bg=THEME["card_background"], 
                         highlightthickness=0, **kwargs)
        self.title = title
        self.data = []  # (etiket, değer, renk) üçlüleri
        self.max_value = 0
        self.animation_step = 0
        self.animation_duration = THEME["animation_medium"]  # ms
        
        # Canvas çiz
        self._draw_chart()
        
        # Boyut değiştiğinde yeniden çiz
        self.bind("<Configure>", self._on_resize)
    
    def set_data(self, data):
        """
        Grafik verisini ayarlar ve animasyonu başlatır
        data: [(etiket, değer, renk), ...] liste
        """
        self.data = data
        self.max_value = max([value for _, value, _ in data]) if data else 1
        
        # Animasyonu başlat
        self.animation_step = 0
        self._animate()
    
    def _draw_chart(self):
        """Grafik arka planını çizer"""
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        
        # Boyutlar çok küçükse çizme
        if width < 10 or height < 10:
            return
        
        # Başlık
        self.create_text(width/2, 15, text=self.title, 
                         font=("Arial", 12, "bold"), fill=THEME["text_primary"], 
                         anchor="n")
        
        # Arka plan çizgiler
        for i in range(1, 5):
            y = height - (i * height / 5) - 20
            self.create_line(30, y, width-20, y, 
                             fill=THEME["border"], dash=(2, 4), width=1)
    
    def _animate(self):
        """Çubukları animasyonlu şekilde çizer"""
        if self.animation_step <= self.animation_duration:
            progress = self.animation_step / self.animation_duration
            self._draw_bars(progress)
            self.animation_step += 20  # Her karede 20ms ilerle
            self.after(20, self._animate)
        else:
            self._draw_bars(1.0)  # Son hali
    
    def _draw_bars(self, progress):
        """Çubukları belirli bir ilerleme oranına göre çizer"""
        self.delete("bar")  # Önceki çubukları sil
        
        width, height = self.winfo_width(), self.winfo_height()
        if not self.data:
            return
        
        num_bars = len(self.data)
        bar_width = min(60, (width - 60) / num_bars)
        bar_spacing = min(20, (width - 60 - num_bars * bar_width) / (num_bars + 1))
        
        chart_top = 40
        chart_bottom = height - 30
        chart_height = chart_bottom - chart_top
        
        # Sıfıra bölme hatasını önlemek için
        if self.max_value <= 0:
            self.max_value = 1  # Eğer max_value sıfır veya negatifse, 1 olarak ayarla
        
        for i, (label, value, color) in enumerate(self.data):
            # Çubuğun gerçek yüksekliğini hesapla
            bar_height = (value / self.max_value) * chart_height * progress
            
            # Çubuğun sol üst köşesi
            x0 = 40 + i * (bar_width + bar_spacing)
            y0 = chart_bottom - bar_height
            
            # Çubuğun sağ alt köşesi
            x1 = x0 + bar_width
            y1 = chart_bottom
            
            # Çubuk çiz
            self.create_rectangle(x0, y0, x1, y1, fill=color, outline="", tags="bar")
            
            # Etiket çiz
            self.create_text(x0 + bar_width/2, chart_bottom + 15, 
                           text=label, fill=THEME["text_secondary"], 
                           font=("Arial", 8), tags="bar")
            
            # Değer çiz
            if bar_height > 20:  # Çubuk yeterince büyükse değeri içine yaz
                self.create_text(x0 + bar_width/2, y0 + 10, 
                               text=str(value), fill=THEME["text_primary"], 
                               font=("Arial", 9, "bold"), tags="bar")
    
    def _on_resize(self, event):
        """Boyut değiştiğinde yeniden çizer"""
        self._draw_chart()
        self._draw_bars(1.0)  # Mevcut veriyi tamamen göster

class SidebarItem(tk.Frame):
    """Kenar çubuğu öğesi"""
    def __init__(self, parent, icon, text, command=None, is_active=False, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.icon_text = icon
        self.label_text = text
        self.command = command
        self.is_active = is_active
        
        self.config(
            bg=THEME["sidebar_background"],
            padx=0,
            pady=0,
            cursor="hand2"
        )
        
        self._create_widgets()
        
        # Olayları bağla
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        
        # Etiketler için de olayları bağla
        self.icon_label.bind("<Enter>", self._on_enter)
        self.icon_label.bind("<Leave>", self._on_leave)
        self.icon_label.bind("<Button-1>", self._on_press)
        
        self.text_label.bind("<Enter>", self._on_enter)
        self.text_label.bind("<Leave>", self._on_leave)
        self.text_label.bind("<Button-1>", self._on_press)

    def _create_widgets(self):
        # İkon
        self.icon_label = tk.Label(self, text=self.icon_text, font=("Arial", 16),
                             bg=THEME["sidebar_background"])
        self.icon_label.pack(side=tk.LEFT, padx=(15, 5), pady=8)
        
        # Metin
        self.text_label = tk.Label(self, text=self.label_text, font=("Arial", 10),
                             bg=THEME["sidebar_background"])
        self.text_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=8)
        
        # Sol kenar göstergesi
        self.indicator = tk.Frame(self, width=3, 
                             bg=THEME["sidebar_background"])
        self.indicator.place(x=0, y=0, relheight=1)
        
        # İlk renkleri güncelle
        self._update_colors()

    def _update_colors(self):
        """Aktif duruma göre renkleri günceller"""
        if self.is_active:
            self.config(bg=THEME["hover_light"])
            self.icon_label.config(bg=THEME["hover_light"], fg=THEME["primary"])
            self.text_label.config(bg=THEME["hover_light"], fg=THEME["primary"])
            self.indicator.config(bg=THEME["primary"])  # Aktif gösterge ana renk
        else:
            self.config(bg=THEME["sidebar_background"])
            self.icon_label.config(bg=THEME["sidebar_background"], fg=THEME["text_secondary"])
            self.text_label.config(bg=THEME["sidebar_background"], fg=THEME["text_secondary"])
            self.indicator.config(bg=THEME["sidebar_background"])  # İnaktif gösterge arka plan ile aynı

    def _on_enter(self, event):
        """Fare üzerine geldiğinde"""
        if not self.is_active:
            self.config(bg=THEME["hover_light"])
            self.icon_label.config(bg=THEME["hover_light"])
            self.text_label.config(bg=THEME["hover_light"])
            self.indicator.config(bg=THEME["hover_light"])

    def _on_leave(self, event):
        """Fare üzerinden ayrıldığında"""
        if not self.is_active:
            self.config(bg=THEME["sidebar_background"])
            self.icon_label.config(bg=THEME["sidebar_background"])
            self.text_label.config(bg=THEME["sidebar_background"])
            self.indicator.config(bg=THEME["sidebar_background"])

    def _on_press(self, event):
        """Tıklandığında"""
        if self.command:
            self.command()

    def set_active(self, active):
        """Aktif durumu ayarlar"""
        self.is_active = active
        self._update_colors()
        if not active:
            self._on_leave(None)

class StatusBadge(tk.Canvas):
    """Durum rozeti"""
    def __init__(self, parent, status="none", text="", width=120, height=28, **kwargs):
        super().__init__(parent, width=width, height=height, bg=THEME["background"], 
                         highlightthickness=0, **kwargs)
        self.status = status
        self.text = text
        self.width_val = width
        self.height_val = height
        
        # Rozeti çiz
        self._draw_badge()
    
    def _draw_badge(self):
        """Durum rozetini çizer"""
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        
        # Boyutlar çok küçükse çizme
        if width < 10 or height < 10:
            return
        
        # Durum rengini al
        color = get_status_color(self.status)
        
        # Yuvarlatılmış dikdörtgen çiz
        radius = height // 2
        self.create_rounded_rectangle(0, 0, width, height, radius=radius, fill=color, outline="")
        
        # Metin çiz
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
    
    def set_status(self, status, text=""):
        """Durum ve metni günceller"""
        self.status = status
        if text:
            self.text = text
        self._draw_badge()
    
    def configure(self, **kwargs):
        """Rozet özelliklerini yapılandırır"""
        if "status" in kwargs:
            self.status = kwargs.pop("status")
        if "text" in kwargs:
            self.text = kwargs.pop("text")
        
        super().configure(**kwargs)
        self._draw_badge()
