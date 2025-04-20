#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spotify tarzı animasyon efektleri
Bu modül, uygulamada kullanılan animasyon efektlerini içerir.
"""

import tkinter as tk
import math
import time
from ui.colors import THEME

class SmoothTransition:
    """Yumuşak geçiş animasyonu için yardımcı sınıf"""
    def __init__(self, widget, property_name, start_value, end_value, duration=THEME["animation_medium"]):
        self.widget = widget
        self.property_name = property_name  # 'x', 'y', 'width', 'height', 'alpha', vb.
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration  # milisaniye
        self.start_time = None
        self.animation_id = None
    
    def start(self):
        """Animasyonu başlatır"""
        self.start_time = time.time() * 1000  # milisaniye olarak
        self._animate()
    
    def _animate(self):
        """Animasyon adımını gerçekleştirir"""
        current_time = time.time() * 1000
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            # Animasyon tamamlandı, son değeri ayarla
            self._set_property(self.end_value)
            self.animation_id = None
            return
        
        # İlerleme oranını hesapla (0-1 arası)
        progress = elapsed / self.duration
        
        # Yavaşlayarak azalma/artma efekti için ease-out fonksiyonu
        progress = self._ease_out_quad(progress)
        
        # Ara değeri hesapla
        current_value = self.start_value + (self.end_value - self.start_value) * progress
        
        # Özelliği ayarla
        self._set_property(current_value)
        
        # Bir sonraki kareyi planla
        self.animation_id = self.widget.after(16, self._animate)  # ~60 FPS
    
    def _set_property(self, value):
        """Widget'ın belirtilen özelliğini ayarlar"""
        if self.property_name == 'x':
            self.widget.place_configure(x=value)
        elif self.property_name == 'y':
            self.widget.place_configure(y=value)
        elif self.property_name == 'width':
            self.widget.configure(width=int(value))
        elif self.property_name == 'height':
            self.widget.configure(height=int(value))
        elif self.property_name == 'alpha':
            # Alfa değeri 0-1 arasında olmalı
            # Bu işlem widget'ın tipine bağlı olarak yapılmalı
            pass
        elif hasattr(self.widget, self.property_name):
            # Özel özellikler için
            setattr(self.widget, self.property_name, value)
    
    def _ease_out_quad(self, t):
        """Ease-out quadratic easing fonksiyonu"""
        return -t * (t - 2)

class FadeEffect:
    """Açılma/kapanma efekti için yardımcı sınıf"""
    def __init__(self, widget, start_alpha=0, end_alpha=1, duration=THEME["animation_medium"]):
        self.widget = widget
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.duration = duration
        self.start_time = None
        self.animation_id = None
    
    def start(self):
        """Animasyonu başlatır"""
        self.start_time = time.time() * 1000
        self._animate()
    
    def _animate(self):
        """Animasyon adımını gerçekleştirir"""
        current_time = time.time() * 1000
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            # Animasyon tamamlandı, son değeri ayarla
            self._set_alpha(self.end_alpha)
            self.animation_id = None
            return
        
        # İlerleme oranını hesapla (0-1 arası)
        progress = elapsed / self.duration
        
        # Yavaşlayarak değişim için ease-out fonksiyonu
        progress = self._ease_out_quad(progress)
        
        # Ara değeri hesapla
        current_alpha = self.start_alpha + (self.end_alpha - self.start_alpha) * progress
        
        # Alfa değerini ayarla
        self._set_alpha(current_alpha)
        
        # Bir sonraki kareyi planla
        self.animation_id = self.widget.after(16, self._animate)  # ~60 FPS
    
    def _set_alpha(self, alpha):
        """Widget'ın alfa değerini ayarlar (şeffaflık)"""
        # Tkinter doğrudan alfa değeri desteklemez
        # Farklı widget tipleri için farklı yöntemler kullanılabilir
        
        if isinstance(self.widget, tk.Canvas):
            # Tüm öğelerin alfa değerini ayarla
            items = self.widget.find_all()
            for item in items:
                # Öğelerin alfa değerini ayarlamak için tag'leri kullanabiliriz
                # Örnek: self.widget.itemconfigure(item, stipple='gray50')
                pass
        
        # Frame, Label gibi widget'lar için bir geçici çözüm
        if alpha < 0.1:
            self.widget.place_forget()  # Tamamen şeffafsa gizle
        else:
            # Frame'in arkaplan rengini alfa değeriyle ayarlama
            # Gerçek RGBA desteklemediği için bu yaklaşık bir yöntem
            self.widget.place(x=self.widget.winfo_x(), y=self.widget.winfo_y())
    
    def _ease_out_quad(self, t):
        """Ease-out quadratic easing fonksiyonu"""
        return -t * (t - 2)

class PulseEffect:
    """Nabız atma efekti için yardımcı sınıf"""
    def __init__(self, widget, min_scale=0.95, max_scale=1.05, duration=1000, repeat=True):
        self.widget = widget
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.duration = duration
        self.repeat = repeat
        self.start_time = None
        self.animation_id = None
        self.original_width = widget.winfo_reqwidth()
        self.original_height = widget.winfo_reqheight()
    
    def start(self):
        """Animasyonu başlatır"""
        self.start_time = time.time() * 1000
        self._animate()
    
    def stop(self):
        """Animasyonu durdurur"""
        if self.animation_id:
            self.widget.after_cancel(self.animation_id)
            self.animation_id = None
            
            # Widget'ı orijinal boyutuna getir
            self.widget.configure(width=self.original_width, height=self.original_height)
    
    def _animate(self):
        """Animasyon adımını gerçekleştirir"""
        current_time = time.time() * 1000
        elapsed = (current_time - self.start_time) % self.duration
        
        # İlerleme oranını hesapla (0-1 arası)
        progress = elapsed / self.duration
        
        # Sinüs fonksiyonu ile yumuşak nabız atma efekti
        scale = self.min_scale + (self.max_scale - self.min_scale) * (math.sin(progress * 2 * math.pi) + 1) / 2
        
        # Boyutları ayarla
        new_width = int(self.original_width * scale)
        new_height = int(self.original_height * scale)
        self.widget.configure(width=new_width, height=new_height)
        
        # Tekrar et veya durdur
        if self.repeat:
            self.animation_id = self.widget.after(16, self._animate)  # ~60 FPS
        else:
            if progress > 0.99:  # Animasyon tamamlandı
                self.animation_id = None
            else:
                self.animation_id = self.widget.after(16, self._animate)

class SlideTransition:
    """Kaydırma geçiş efekti"""
    def __init__(self, container, old_widget=None, new_widget=None, direction="left", duration=THEME["animation_medium"]):
        self.container = container
        self.old_widget = old_widget
        self.new_widget = new_widget
        self.direction = direction  # "left", "right", "up", "down"
        self.duration = duration
        self.start_time = None
        self.animation_id = None
        
        # Konteyner boyutları
        self.width = container.winfo_width()
        self.height = container.winfo_height()
    
    def start(self):
        """Animasyonu başlatır"""
        # Boyut bilgilerini güncelle
        self.width = self.container.winfo_width()
        self.height = self.container.winfo_height()
        
        # Yeni widget'ı görünür yap ve hazırla
        if self.new_widget:
            self.new_widget.place(x=0, y=0, width=self.width, height=self.height)
            
            # Başlangıç pozisyonunu ayarla
            if self.direction == "left":
                self.new_widget.place(x=self.width, y=0)
            elif self.direction == "right":
                self.new_widget.place(x=-self.width, y=0)
            elif self.direction == "up":
                self.new_widget.place(x=0, y=self.height)
            elif self.direction == "down":
                self.new_widget.place(x=0, y=-self.height)
        
        self.start_time = time.time() * 1000
        self._animate()
    
    def _animate(self):
        """Animasyon adımını gerçekleştirir"""
        current_time = time.time() * 1000
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            # Animasyon tamamlandı, son pozisyonları ayarla
            if self.old_widget:
                self.old_widget.place_forget()
            
            if self.new_widget:
                self.new_widget.place(x=0, y=0, width=self.width, height=self.height)
            
            self.animation_id = None
            return
        
        # İlerleme oranını hesapla (0-1 arası)
        progress = elapsed / self.duration
        
        # Yavaşlayarak değişim için ease-out fonksiyonu
        progress = self._ease_out_quad(progress)
        
        # Yeni ve eski widget'ları hareket ettir
        if self.direction == "left":
            if self.old_widget:
                self.old_widget.place(x=-(self.width * progress), y=0)
            if self.new_widget:
                self.new_widget.place(x=self.width * (1 - progress), y=0)
        
        elif self.direction == "right":
            if self.old_widget:
                self.old_widget.place(x=self.width * progress, y=0)
            if self.new_widget:
                self.new_widget.place(x=-(self.width * (1 - progress)), y=0)
        
        elif self.direction == "up":
            if self.old_widget:
                self.old_widget.place(x=0, y=-(self.height * progress))
            if self.new_widget:
                self.new_widget.place(x=0, y=self.height * (1 - progress))
        
        elif self.direction == "down":
            if self.old_widget:
                self.old_widget.place(x=0, y=self.height * progress)
            if self.new_widget:
                self.new_widget.place(x=0, y=-(self.height * (1 - progress)))
        
        # Bir sonraki kareyi planla
        self.animation_id = self.container.after(16, self._animate)  # ~60 FPS
    
    def _ease_out_quad(self, t):
        """Ease-out quadratic easing fonksiyonu"""
        return -t * (t - 2)
