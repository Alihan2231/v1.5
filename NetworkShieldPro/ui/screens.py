#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spotify tarzı uygulama ekranları
Bu modül, uygulamanın tüm ekranlarını ve ana uygulamayı içerir.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os
import threading
import traceback
from collections import defaultdict
import random
import math

from ui.colors import THEME, get_status_color
from ui.custom_widgets import (
    RoundedFrame, SpotifyButton, CircularProgressbar, 
    ParticleAnimationCanvas, AnimatedChart, SidebarItem, StatusBadge
)
from ui.animations import SmoothTransition, FadeEffect, PulseEffect, SlideTransition
from ui.helpers import (
    format_timestamp, format_time_ago, truncate_text, format_mac_for_display,
    format_ip_for_display, threat_level_to_text, create_threat_data_chart,
    create_scan_history_chart, get_network_security_score
)
from modules.arp_detector import ARPScanner

class SpotifyARPApp:
    """Ana uygulama sınıfı"""
    def __init__(self, root):
        try:
            print("SpotifyARPApp.__init__ başlatılıyor...")
            self.root = root
        
            try:
                print("Background ayarlanıyor...")
                self.root.configure(bg=THEME["background"])
                print("Background ayarlandı")
            except Exception as e:
                print(f"Background ayarlanırken hata: {e}")
                traceback.print_exc()
        
            # ARP tarayıcısını başlat
            try:
                print("ARPScanner oluşturuluyor...")
                self.scanner = ARPScanner(callback=self.on_scan_completed)
                print("ARPScanner başarıyla oluşturuldu.")
            except Exception as e:
                print(f"ARPScanner oluşturulurken hata: {e}")
                traceback.print_exc()
        
            # Ekran değişkenlerini ayarla
            self.current_screen = None
            self.screens = {}
          
            # Animasyon değişkenleri
            self.particle_animation = None
        
            try:
                print("Ana düzen oluşturuluyor...")
                self._create_layout()
                print("Ana düzen oluşturuldu.")
            except Exception as e:
               print(f"Ana düzen oluşturulurken hata: {e}")
               traceback.print_exc()
        
            try:
                print("Ekranlar oluşturuluyor...")
                self._create_screens()
                print("Ekranlar oluşturuldu.")
            except Exception as e:
                print(f"Ekranlar oluşturulurken hata: {e}")
                traceback.print_exc()
        
            try:
                print("Başlangıç ekranı gösteriliyor...")
                self.show_screen("dashboard")
                print("Başlangıç ekranı gösterildi.")
            except Exception as e:
                print(f"Başlangıç ekranı gösterilirken hata: {e}")
                traceback.print_exc()
        
            try:
                print("Arka plan animasyonu başlatılıyor...")
                self._start_background_animation()
                print("Arka plan animasyonu başlatıldı.")
            except Exception as e:
                print(f"Arka plan animasyonu başlatılırken hata: {e}")
                traceback.print_exc()
        
            # Pencere boyut değişikliğini işle
            self.root.bind("<Configure>", self._on_window_resize)
        
            # İlk taramayı başlat
            self.root.after(500, self.scanner.start_scan)
        
            print("SpotifyARPApp.__init__ tamamlandı")
        except Exception as e:
            print(f"SpotifyARPApp.__init__ içinde kritik hata: {e}")
            traceback.print_exc()
    
    def _create_layout(self):
        """Ana düzeni oluşturur"""
        # Ana çerçeve
        self.main_frame = tk.Frame(self.root, bg=THEME["background"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Yan menü çerçevesi
        self.sidebar_frame = tk.Frame(self.main_frame, bg=THEME["sidebar_background"], width=220)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)
        
        # Logo ve başlık
        logo_frame = tk.Frame(self.sidebar_frame, bg=THEME["sidebar_background"], height=100)
        logo_frame.pack(fill=tk.X, pady=(20, 0))
        
        logo_text = tk.Label(logo_frame, text="🛡️", font=("Arial", 32), bg=THEME["sidebar_background"], fg=THEME["primary"])
        logo_text.pack(pady=(10, 0))
        
        app_title = tk.Label(logo_frame, text="ARP Guard", font=("Arial", 16, "bold"), 
                           bg=THEME["sidebar_background"], fg=THEME["text_primary"])
        app_title.pack(pady=(5, 20))
        
        # Menü öğeleri
        self.menu_items = []
        
        # Gösterge Paneli
        dashboard_item = SidebarItem(self.sidebar_frame, "📊", "Gösterge Paneli", 
                                   command=lambda: self.show_screen("dashboard"), is_active=True)
        dashboard_item.pack(fill=tk.X, pady=1)
        self.menu_items.append({"id": "dashboard", "item": dashboard_item})
        
        # Ağ Taraması
        scan_item = SidebarItem(self.sidebar_frame, "🔍", "Ağ Taraması", 
                             command=lambda: self.show_screen("scan"))
        scan_item.pack(fill=tk.X, pady=1)
        self.menu_items.append({"id": "scan", "item": scan_item})
        
        # Tehdit Analizi
        threat_item = SidebarItem(self.sidebar_frame, "⚠️", "Tehdit Analizi", 
                               command=lambda: self.show_screen("threats"))
        threat_item.pack(fill=tk.X, pady=1)
        self.menu_items.append({"id": "threats", "item": threat_item})
        
        # Geçmiş
        history_item = SidebarItem(self.sidebar_frame, "📜", "Geçmiş", 
                                command=lambda: self.show_screen("history"))
        history_item.pack(fill=tk.X, pady=1)
        self.menu_items.append({"id": "history", "item": history_item})
        
        # Ayarlar
        settings_item = SidebarItem(self.sidebar_frame, "⚙️", "Ayarlar", 
                                 command=lambda: self.show_screen("settings"))
        settings_item.pack(fill=tk.X, pady=1)
        self.menu_items.append({"id": "settings", "item": settings_item})
        
        # Durum bilgisi
        status_frame = tk.Frame(self.sidebar_frame, bg=THEME["sidebar_background"], height=50)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.status_label = tk.Label(status_frame, text="Hazır", font=("Arial", 10), 
                                   bg=THEME["sidebar_background"], fg=THEME["text_secondary"])
        self.status_label.pack(pady=5)
        
        # İçerik çerçevesi
        self.content_frame = tk.Frame(self.main_frame, bg=THEME["background"])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Arka plan animasyonu için canvas
        self.background_canvas = ParticleAnimationCanvas(self.content_frame, 
                                                     width=self.content_frame.winfo_width(), 
                                                     height=self.content_frame.winfo_height())
        self.background_canvas.pack(fill=tk.BOTH, expand=True)
    
    def _create_screens(self):
        """Uygulama ekranlarını oluşturur"""
        # Gösterge Paneli
        self.screens["dashboard"] = DashboardScreen(self.background_canvas, self)
        
        # Ağ Taraması
        self.screens["scan"] = ScanScreen(self.background_canvas, self)
        
        # Tehdit Analizi
        self.screens["threats"] = ThreatAnalysisScreen(self.background_canvas, self)
        
        # Geçmiş
        self.screens["history"] = HistoryScreen(self.background_canvas, self)
        
        # Ayarlar
        self.screens["settings"] = SettingsScreen(self.background_canvas, self)
    
    def show_screen(self, screen_id):
        """Belirtilen ekranı gösterir"""
        if screen_id not in self.screens:
            return
        
        # Menü öğelerini güncelle
        for item in self.menu_items:
            if item["id"] == screen_id:
                item["item"].set_active(True)
            else:
                item["item"].set_active(False)
        
        # Mevcut ekranı gizle ve yeni ekranı göster
        old_screen = self.current_screen
        new_screen = self.screens[screen_id]
        
        # Animasyonlu geçiş
        if old_screen:
            # Rastgele yön seç
            directions = ["left", "right", "up", "down"]
            direction = random.choice(directions)
            
            # Geçişi başlat
            transition = SlideTransition(
                self.background_canvas, 
                old_widget=old_screen.frame, 
                new_widget=new_screen.frame, 
                direction=direction, 
                duration=THEME["animation_medium"]
            )
            transition.start()
        else:
            # İlk ekran - doğrudan göster
            new_screen.frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.current_screen = new_screen
        new_screen.on_show()
    
    def _start_background_animation(self):
        """Arka plan animasyonunu başlatır"""
        # Parçacık animasyonunu başlat
        self.background_canvas.start_animation()
    
    def _on_window_resize(self, event):
        """Pencere boyutu değiştiğinde çağrılır"""
        if event.widget == self.root:
            # Arka plan canvas'ını yeniden boyutlandır
            self.background_canvas.resize(
                self.content_frame.winfo_width(), 
                self.content_frame.winfo_height()
            )
    
    def start_scan(self):
        """Tarama başlatır"""
        if not self.scanner.running:
            self.scanner.start_scan()
            self.status_label.config(text="Taranıyor...")
            return True
        return False
    
    def start_periodic_scan(self, interval_hours=None):
        """Periyodik taramayı başlatır"""
        if hasattr(self, 'scanner'):
            result = self.scanner.start_periodic_scan(interval_hours)
            if result:
                print(f"Periyodik tarama başlatıldı - Her {self.scanner.scan_interval} saatte bir")
                self.update_status_label(f"Periyodik tarama aktif: Her {self.scanner.scan_interval} saatte bir")
            return result
        return False

    def stop_periodic_scan(self):
        """Periyodik taramayı durdurur"""
        if hasattr(self, 'scanner'):
            result = self.scanner.stop_periodic_scan()
            if result:
                print("Periyodik tarama durduruldu")
                self.update_status_label("Periyodik tarama durduruldu")
            return result
        return False

    def update_status_label(self, text):
        """Durum etiketini günceller"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=text)
    
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        # Durum etiketini güncelle
        self.status_label.config(text="Hazır")
        
        # Tüm ekranları bilgilendir
        for screen in self.screens.values():
            screen.on_scan_completed(result)
        
        # Yüksek tehdit seviyesi varsa uyarı göster
        if result.get("threat_level") == "high":
            self._show_threat_warning(result)
    
    def _show_threat_warning(self, result):
        """Tehdit uyarısı gösterir"""
        high_threats = [entry for entry in result.get("suspicious_entries", []) 
                      if entry.get("threat_level") == "high"]
        
        if not high_threats:
            return
        
        # Uyarı mesajı
        message = "⚠️ DİKKAT! ARP Spoofing tehdidi tespit edildi!\n\n"
        message += "Aşağıdaki yüksek risk durumları tespit edildi:\n"
        
        for i, threat in enumerate(high_threats[:3], 1):
            message += f"{i}. {threat.get('message', 'Bilinmeyen tehdit')}\n"
        
        if len(high_threats) > 3:
            message += f"... ve {len(high_threats) - 3} tehdit daha.\n"
        
        message += "\nDaha fazla bilgi için Tehdit Analizi ekranına bakın."
        
        # Uyarı penceresi göster
        messagebox.showwarning("Güvenlik Uyarısı", message)
        
        # Tehdit analizi ekranına geç
        self.show_screen("threats")

class BaseScreen:
    """Tüm ekranlar için temel sınıf"""
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg=THEME["background"])
        
        # Ortak etkileşim değişkenleri
        self.is_showing = False
        
        # Ekran içeriğini oluştur
        self._create_widgets()
    
    def _create_widgets(self):
        """Ekran widget'larını oluşturur - Alt sınıflarda override edilmeli"""
        pass
    
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        self.is_showing = True
    
    def on_hide(self):
        """Ekran gizlendiğinde çağrılır"""
        self.is_showing = False
    
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        pass

class DashboardScreen(BaseScreen):
    """Gösterge Paneli Ekranı"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.last_scan_result = None
    
    def _create_widgets(self):
        """Dashboard ekranının widget'larını oluşturur"""
        # Üst başlık
        header_frame = tk.Frame(self.frame, bg=THEME["background"], height=60)
        header_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        # Başlık
        title = tk.Label(header_frame, text="Gösterge Paneli", font=("Arial", 24, "bold"),
                       bg=THEME["background"], fg=THEME["text_primary"])
        title.pack(side=tk.LEFT)
        
        # Tarama butonu
        self.scan_button = SpotifyButton(header_frame, text="Hızlı Tarama", 
                                      command=self.app.start_scan)
        self.scan_button.pack(side=tk.RIGHT, pady=10)
        
        # İçerik alanı - Üst Kısım
        self.top_content = tk.Frame(self.frame, bg=THEME["background"])
        self.top_content.pack(fill=tk.X, padx=20, pady=10)
        
        # Güvenlik skoru kartı
        self.score_card = RoundedFrame(self.top_content, 
                                    bg=THEME["card_background"], 
                                    height=200, width=300, 
                                    corner_radius=THEME["radius_medium"])
        self.score_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Skor başlık
        score_title = tk.Label(self.score_card, text="Ağ Güvenlik Skoru", 
                            font=("Arial", 14, "bold"), 
                            bg=THEME["card_background"], fg=THEME["text_primary"])
        score_title.place(relx=0.5, y=25, anchor="center")
        
        # Dairesel ilerleme çubuğu
        self.security_score = CircularProgressbar(self.score_card, width=120, height=120, 
                                              progress=0, thickness=10, 
                                              bg_color=THEME["secondary"], 
                                              fg_color=THEME["primary"])
        self.security_score.place(relx=0.5, rely=0.5, anchor="center")
        
        # Durum etiketi
        self.score_status = tk.Label(self.score_card, text="Henüz tarama yapılmadı", 
                                  font=("Arial", 12), 
                                  bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.score_status.place(relx=0.5, rely=0.85, anchor="center")
        
        # Son tarama kartı
        self.last_scan_card = RoundedFrame(self.top_content, 
                                       bg=THEME["card_background"], 
                                       height=200, width=300, 
                                       corner_radius=THEME["radius_medium"])
        self.last_scan_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Son tarama başlık
        last_scan_title = tk.Label(self.last_scan_card, text="Son Tarama Durumu", 
                                font=("Arial", 14, "bold"), 
                                bg=THEME["card_background"], fg=THEME["text_primary"])
        last_scan_title.place(relx=0.5, y=25, anchor="center")
        
        # Son tarama durumu rozeti
        self.scan_status_badge = StatusBadge(self.last_scan_card, status="none", text="Bilinmiyor", 
                                         width=120, height=30)
        self.scan_status_badge.place(relx=0.5, y=60, anchor="center")
        
        # Son tarama zamanı
        self.last_scan_time = tk.Label(self.last_scan_card, text="Henüz tarama yapılmadı", 
                                   font=("Arial", 11), 
                                   bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.last_scan_time.place(relx=0.5, y=90, anchor="center")
        
        # Ağ geçidi durumu
        self.gateway_status = tk.Label(self.last_scan_card, text="Ağ Geçidi: Bilinmiyor", 
                                     font=("Arial", 11), 
                                     bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.gateway_status.place(relx=0.5, y=115, anchor="center")
        
        # Tehdit durumu
        self.threat_status = tk.Label(self.last_scan_card, text="Tehdit: Bilinmiyor", 
                                    font=("Arial", 11), 
                                    bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.threat_status.place(relx=0.5, y=140, anchor="center")
        
        # İçerik alanı - Alt Kısım
        self.bottom_content = tk.Frame(self.frame, bg=THEME["background"])
        self.bottom_content.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        
        # Tehdit grafiği kartı
        self.threats_chart_card = RoundedFrame(self.bottom_content, 
                                           bg=THEME["card_background"], 
                                           corner_radius=THEME["radius_medium"])
        self.threats_chart_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tehdit grafiği başlık
        threats_chart_title = tk.Label(self.threats_chart_card, text="Tehdit Dağılımı", 
                                    font=("Arial", 14, "bold"), 
                                    bg=THEME["card_background"], fg=THEME["text_primary"])
        threats_chart_title.pack(pady=(15, 0))
        
        # Tehdit grafiği
        self.threats_chart = AnimatedChart(self.threats_chart_card, width=300, height=180, 
                                       title="")
        self.threats_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Geçmiş tarama grafiği kartı
        self.history_chart_card = RoundedFrame(self.bottom_content, 
                                           bg=THEME["card_background"], 
                                           corner_radius=THEME["radius_medium"])
        self.history_chart_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Geçmiş grafiği başlık
        history_chart_title = tk.Label(self.history_chart_card, text="Tehdit Geçmişi", 
                                     font=("Arial", 14, "bold"), 
                                     bg=THEME["card_background"], fg=THEME["text_primary"])
        history_chart_title.pack(pady=(15, 0))
        
        # Geçmiş grafiği
        self.history_chart = AnimatedChart(self.history_chart_card, width=300, height=180, 
                                        title="")
        self.history_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        super().on_show()
        
        # Son tarama sonuçlarını göster
        if self.last_scan_result:
            self._update_with_result(self.last_scan_result)
        
        # Geçmiş grafiği güncelle
        scan_history = self.app.scanner.scan_history
        if scan_history:
            history_data = create_scan_history_chart(scan_history)
            self.history_chart.set_data(history_data)
    
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        self.last_scan_result = result
        
        # Ekran görünür durumdaysa sonuçları göster
        if self.is_showing:
            self._update_with_result(result)
            
            # Geçmiş grafiği güncelle
            scan_history = self.app.scanner.scan_history
            if scan_history:
                history_data = create_scan_history_chart(scan_history)
                self.history_chart.set_data(history_data)
    
    def _update_with_result(self, result):
        """Tarama sonucuna göre arayüzü günceller"""
        if "error" in result:
            # Hata durumunda
            self.score_status.config(text="Tarama hatası")
            self.scan_status_badge.set_status("unknown", "Hata")
            self.last_scan_time.config(text=f"Hata: {result['error']}")
            return
        
        # Güvenlik skoru
        security_score = get_network_security_score(result)
        self.security_score.set_progress(security_score)
        
        # Skorun durumunu ayarla
        if security_score >= 80:
            score_text = "Güvenli"
            score_color = THEME["success"]
        elif security_score >= 50:
            score_text = "Orta Riskli"
            score_color = THEME["warning"]
        else:
            score_text = "Yüksek Riskli"
            score_color = THEME["error"]
        
        self.score_status.config(text=score_text, fg=score_color)
        
        # Son tarama durumu
        threat_level = result.get("threat_level", "unknown")
        status_text = threat_level_to_text(threat_level)
        self.scan_status_badge.set_status(threat_level, status_text)
        
        # Son tarama zamanı
        timestamp = result.get("timestamp", time.time())
        self.last_scan_time.config(text=f"Son tarama: {format_timestamp(timestamp)}")
        
        # Ağ geçidi durumu
        gateway = result.get("gateway", {"ip": "Bilinmiyor", "mac": "Bilinmiyor"})
        self.gateway_status.config(text=f"Ağ Geçidi: {gateway['ip']}")
        
        # Tehdit durumu
        suspicious_entries = result.get("suspicious_entries", [])
        real_threats = [entry for entry in suspicious_entries 
                      if not entry.get("type", "").startswith("info_")]
        
        if not real_threats:
            self.threat_status.config(text="Tehdit: Tespit edilmedi", fg=THEME["success"])
        else:
            high_threats = sum(1 for entry in real_threats if entry.get("threat_level") == "high")
            medium_threats = sum(1 for entry in real_threats if entry.get("threat_level") == "medium")
            
            if high_threats > 0:
                self.threat_status.config(text=f"Tehdit: {high_threats} yüksek, {medium_threats} orta", 
                                       fg=THEME["error"])
            else:
                self.threat_status.config(text=f"Tehdit: {medium_threats} orta seviye", 
                                       fg=THEME["warning"])
        
        # Tehdit dağılımı grafiği güncelle
        threat_data = [
            (entry.get("threat_level", "unknown"), 1, get_status_color(entry.get("threat_level", "unknown")))
            for entry in suspicious_entries
        ]
        
        # Tehditleri grupla
        grouped_threats = defaultdict(int)
        for level, count, _ in threat_data:
            grouped_threats[level] += count
        
        # Grafik verisi oluştur
        chart_data = [
            ("Yüksek", grouped_threats["high"], THEME["error"]),
            ("Orta", grouped_threats["medium"], THEME["warning"]),
            ("Bilgi", grouped_threats.get("none", 0), THEME["success"])
        ]
        
        # Grafiği güncelle
        self.threats_chart.set_data(chart_data)

class ScanScreen(BaseScreen):
    """Ağ Taraması Ekranı"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.is_scanning = False
        self.last_scan_result = None
    
    def _create_widgets(self):
        """Tarama ekranının widget'larını oluşturur"""
        # Üst başlık
        header_frame = tk.Frame(self.frame, bg=THEME["background"], height=60)
        header_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        # Başlık
        title = tk.Label(header_frame, text="Ağ Taraması", font=("Arial", 24, "bold"),
                       bg=THEME["background"], fg=THEME["text_primary"])
        title.pack(side=tk.LEFT)
        
        # Tarama düğmeleri
        buttons_frame = tk.Frame(header_frame, bg=THEME["background"])
        buttons_frame.pack(side=tk.RIGHT)
        
        self.scan_button = SpotifyButton(buttons_frame, text="Taramayı Başlat", 
                                      command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        # Periyodik tarama düğmesi
        self.periodic_button = SpotifyButton(buttons_frame, text="Periyodik Tarama", 
                                         command=self.toggle_periodic_scan,
                                         bg=THEME["secondary"])
        self.periodic_button.pack(side=tk.LEFT, padx=5)
        
        # İçerik çerçevesi
        content_frame = tk.Frame(self.frame, bg=THEME["background"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Sol panel - Tarama Durumu
        left_panel = tk.Frame(content_frame, bg=THEME["background"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Tarama durumu kartı
        self.status_card = RoundedFrame(left_panel, bg=THEME["card_background"], 
                                     corner_radius=THEME["radius_medium"])
        self.status_card.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Durum kartı başlığı
        status_title = tk.Label(self.status_card, text="Tarama Durumu", 
                             font=("Arial", 16, "bold"), 
                             bg=THEME["card_background"], fg=THEME["text_primary"])
        status_title.pack(pady=(15, 10))
        
        # Tarama durum ikonu ve metni
        self.status_icon = tk.Label(self.status_card, text="🔍", 
                                 font=("Arial", 48), 
                                 bg=THEME["card_background"], fg=THEME["text_primary"])
        self.status_icon.pack(pady=(0, 10))
        
        self.status_text = tk.Label(self.status_card, text="Hazır", 
                                 font=("Arial", 14), 
                                 bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.status_text.pack(pady=(0, 10))
        
        # Dairesel ilerleme çubuğu
        self.progress_bar = CircularProgressbar(self.status_card, width=120, height=120, 
                                            progress=0, thickness=10, 
                                            bg_color=THEME["secondary"], 
                                            fg_color=THEME["primary"])
        self.progress_bar.pack(pady=10)
        
        # Son tarama metni
        self.last_scan_text = tk.Label(self.status_card, text="Henüz tarama yapılmadı", 
                                    font=("Arial", 11), 
                                    bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.last_scan_text.pack(pady=(0, 15))
        
        # Sağ panel - Son Tarama Sonuçları
        right_panel = tk.Frame(content_frame, bg=THEME["background"])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Son tarama sonuçları kartı
        self.results_card = RoundedFrame(right_panel, bg=THEME["card_background"], 
                                     corner_radius=THEME["radius_medium"])
        self.results_card.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Sonuçlar kartı başlığı
        results_title = tk.Label(self.results_card, text="Tarama Sonuçları", 
                              font=("Arial", 16, "bold"), 
                              bg=THEME["card_background"], fg=THEME["text_primary"])
        results_title.pack(pady=(15, 10))
        
        # İçindeki scrolled text widget'ı için çerçeve
        text_frame = tk.Frame(self.results_card, bg=THEME["card_background"], padx=15, pady=10)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Kaydırılabilir metin alanı
        self.results_text = tk.Text(text_frame, bg=THEME["background"], fg=THEME["text_primary"],
                                 font=("Consolas", 10), relief=tk.FLAT, wrap=tk.WORD,
                                 padx=10, pady=10, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Kaydırma çubuğu
        scrollbar = ttk.Scrollbar(text_frame, command=self.results_text.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        # Sonuç metninin etiketlerini yapılandır
        self.results_text.tag_configure("header", font=("Consolas", 11, "bold"), foreground=THEME["primary"])
        self.results_text.tag_configure("normal", font=("Consolas", 10), foreground=THEME["text_primary"])
        self.results_text.tag_configure("warning", font=("Consolas", 10, "bold"), foreground=THEME["warning"])
        self.results_text.tag_configure("error", font=("Consolas", 10, "bold"), foreground=THEME["error"])
        self.results_text.tag_configure("success", font=("Consolas", 10, "bold"), foreground=THEME["success"])
        self.results_text.tag_configure("info", font=("Consolas", 10), foreground=THEME["text_secondary"])
        
        # Sonuç metnini salt okunur yap
        self.results_text.config(state=tk.DISABLED)
        
        # Periyodik tarama ayarları
        self.periodic_settings = tk.Frame(right_panel, bg=THEME["background"])
        self.periodic_settings.pack(fill=tk.X, pady=5)
        
        # Ayarlar kartı
        self.settings_card = RoundedFrame(self.periodic_settings, bg=THEME["card_background"], 
                                      corner_radius=THEME["radius_medium"], height=50)
        self.settings_card.pack(fill=tk.BOTH)
        
        # İçerik
        settings_content = tk.Frame(self.settings_card, bg=THEME["card_background"])
        settings_content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Periyodik tarama süresi etiketi
        interval_label = tk.Label(settings_content, text="Tarama Sıklığı:", 
                               bg=THEME["card_background"], fg=THEME["text_primary"],
                               font=("Arial", 11))
        interval_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Periyodik tarama süresi seçici
        self.interval_hours = tk.StringVar(value="24")
        interval_values = ["1", "2", "4", "6", "8", "12", "24", "48", "72"]
        
        self.interval_dropdown = ttk.Combobox(settings_content, textvariable=self.interval_hours,
                                           values=interval_values, width=4)
        self.interval_dropdown.pack(side=tk.LEFT)
        
        # Saat etiketi
        hours_label = tk.Label(settings_content, text="saat", 
                            bg=THEME["card_background"], fg=THEME["text_primary"],
                            font=("Arial", 11))
        hours_label.pack(side=tk.LEFT, padx=5)
        
        # Nabız efekti başlatıcı
        self.pulse_effect = None
    
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        super().on_show()
        
        # Periyodik tarama düğmesini güncelle
        if self.app.scanner.periodic_running:
            self.periodic_button.configure(text="Periyodik Durdur", bg=THEME["error"])
        else:
            self.periodic_button.configure(text="Periyodik Başlat", bg=THEME["secondary"])
        
        # Son tarama sonuçlarını göster
        if self.last_scan_result:
            self.display_scan_results(self.last_scan_result)
    
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        self.last_scan_result = result
        self.is_scanning = False
        
        # İlerleme çubuğunu %100 yap
        self.progress_bar.set_progress(100)
        
        # Nabız efektini durdur
        if self.pulse_effect:
            self.pulse_effect.stop()
            self.pulse_effect = None
        
        # Tarama durumunu güncelle
        self.status_text.config(text="Tarama Tamamlandı")
        
        # Icon'u güncelle
        if "error" in result:
            self.status_icon.config(text="❌", fg=THEME["error"])
        else:
            threat_level = result.get("threat_level", "unknown")
            if threat_level == "high":
                self.status_icon.config(text="⚠️", fg=THEME["error"])
            elif threat_level == "medium":
                self.status_icon.config(text="⚠️", fg=THEME["warning"])
            else:
                self.status_icon.config(text="✅", fg=THEME["success"])
        
        # Son tarama zamanını güncelle
        timestamp = result.get("timestamp", time.time())
        self.last_scan_text.config(text=f"Son tarama: {format_timestamp(timestamp)}")
        
        # Sonuçları görüntüle
        if self.is_showing:
            self.display_scan_results(result)
        
        # Tarama düğmesini etkinleştir
        self.scan_button.configure(text="Taramayı Başlat", state="normal")
    
    def start_scan(self):
        """Tarama başlatır"""
        if self.is_scanning:
            return
        
        if self.app.start_scan():
            self.is_scanning = True
            
            # İlerleme çubuğunu sıfırla ve başlat
            self.progress_bar.set_progress(0)
            
            # Durum metnini güncelle
            self.status_text.config(text="Taranıyor...")
            
            # Durum ikonunu güncelle
            self.status_icon.config(text="🔍", fg=THEME["primary"])
            
            # Nabız efektini başlat
            self.pulse_effect = PulseEffect(self.status_icon, min_scale=0.9, max_scale=1.1, duration=1000)
            self.pulse_effect.start()
            
            # Tarama düğmesini devre dışı bırak
            self.scan_button.configure(text="Taranıyor...", state="disabled")
            
            # Yapay ilerleme başlat
            self.simulate_progress()
    
    def toggle_periodic_scan(self):
        """Periyodik taramayı açar/kapatır"""
        if self.app.scanner.periodic_running:
            if self.app.stop_periodic_scan():
                self.periodic_button.configure(text="Periyodik Başlat", bg=THEME["secondary"])
        else:
            try:
                interval = int(self.interval_hours.get())
                if interval < 1:
                    interval = 1
                elif interval > 72:
                    interval = 72
                
                if self.app.start_periodic_scan(interval):
                    self.periodic_button.configure(text="Periyodik Durdur", bg=THEME["error"])
            except ValueError:
                self.interval_hours.set("24")
    
    def simulate_progress(self):
        """Tarama ilerleme durumunu simüle eder"""
        if not self.is_scanning:
            return
        
        # Mevcut ilerlemeyi al
        current = self.progress_bar.progress
        
        # Yeni ilerleme hesapla - taramayı bitmeden önce %90'a kadar götür
        if current < 90:
            # Logaritmik bir ilerleme - başlangıçta hızlı, sonra yavaşlar
            new_progress = current + (90 - current) * 0.1
            self.progress_bar.set_progress(new_progress)
            
            # Sonraki güncellemeyi planla
            self.frame.after(200, self.simulate_progress)
    
    def display_scan_results(self, result):
        """Tarama sonuçlarını metin alanında gösterir"""
        # Metin alanını temizle
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        if "error" in result:
            # Hata durumunda
            self.results_text.insert(tk.END, "TARAMA HATASI\n", "header")
            self.results_text.insert(tk.END, "=" * 50 + "\n", "normal")
            self.results_text.insert(tk.END, f"Hata: {result['error']}\n", "error")
            self.results_text.config(state=tk.DISABLED)
            return
        
        # Tarama zamanı
        self.results_text.insert(tk.END, "TARAMA SONUÇLARI\n", "header")
        self.results_text.insert(tk.END, "=" * 50 + "\n", "normal")
        
        timestamp = result.get("timestamp", time.time())
        time_str = format_timestamp(timestamp)
        self.results_text.insert(tk.END, f"Tarama Zamanı: {time_str}\n\n", "normal")
        
        # Ağ Geçidi Bilgisi
        self.results_text.insert(tk.END, "AĞ GEÇİDİ BİLGİSİ\n", "header")
        self.results_text.insert(tk.END, "-" * 50 + "\n", "normal")
        
        gateway = result.get("gateway", {"ip": "Bilinmiyor", "mac": "Bilinmiyor"})
        self.results_text.insert(tk.END, f"IP: {gateway['ip']}\n", "normal")
        self.results_text.insert(tk.END, f"MAC: {gateway['mac']}\n\n", "normal")
        
        # ARP Tablosu
        self.results_text.insert(tk.END, "ARP TABLOSU\n", "header")
        self.results_text.insert(tk.END, "-" * 50 + "\n", "normal")
        
        arp_table = result.get("arp_table", [])
        self.results_text.insert(tk.END, f"{'IP Adresi':<16} {'MAC Adresi':<18} {'Arayüz':<10}\n", "info")
        self.results_text.insert(tk.END, "-" * 50 + "\n", "normal")
        
        for entry in arp_table:
            ip = entry.get("ip", "?")
            mac = entry.get("mac", "?")
            interface = entry.get("interface", "?")
            
            self.results_text.insert(tk.END, f"{ip:<16} {mac:<18} {interface:<10}\n", "normal")
        
        self.results_text.insert(tk.END, "\n", "normal")
        
        # Şüpheli Durumlar
        self.results_text.insert(tk.END, "ŞÜPHELİ DURUMLAR ANALİZİ\n", "header")
        self.results_text.insert(tk.END, "-" * 50 + "\n", "normal")
        
        suspicious_entries = result.get("suspicious_entries", [])
        
        if not suspicious_entries:
            self.results_text.insert(tk.END, "Herhangi bir şüpheli durum tespit edilmedi.\n", "success")
        else:
            # Önce gerçek tehditleri göster
            high_threats = [entry for entry in suspicious_entries 
                          if entry.get("threat_level") == "high"]
            
            medium_threats = [entry for entry in suspicious_entries 
                            if entry.get("threat_level") == "medium"]
            
            info_entries = [entry for entry in suspicious_entries 
                          if entry.get("type", "").startswith("info_")]
            
            # Yüksek tehditler
            if high_threats:
                self.results_text.insert(tk.END, "YÜKSEK TEHDİTLER:\n", "error")
                for entry in high_threats:
                    self.results_text.insert(tk.END, f"- {entry.get('message', 'Bilinmeyen tehdit')}\n", "error")
                self.results_text.insert(tk.END, "\n", "normal")
            
            # Orta tehditler
            if medium_threats:
                self.results_text.insert(tk.END, "ORTA SEVİYE TEHDİTLER:\n", "warning")
                for entry in medium_threats:
                    self.results_text.insert(tk.END, f"- {entry.get('message', 'Bilinmeyen tehdit')}\n", "warning")
                self.results_text.insert(tk.END, "\n", "normal")
            
            # Bilgi amaçlı girdiler
            if info_entries:
                self.results_text.insert(tk.END, "BİLGİ AMAÇLI KAYITLAR:\n", "info")
                for entry in info_entries:
                    self.results_text.insert(tk.END, f"- {entry.get('message', 'Bilinmeyen bilgi')}\n", "info")
        
        self.results_text.insert(tk.END, "\n", "normal")
        
        # Özet
        self.results_text.insert(tk.END, "ANALİZ ÖZETİ\n", "header")
        self.results_text.insert(tk.END, "-" * 50 + "\n", "normal")
        
        threat_level = result.get("threat_level", "unknown")
        threat_text = threat_level_to_text(threat_level)
        
        self.results_text.insert(tk.END, f"Toplam kayıt sayısı: {len(arp_table)}\n", "normal")
        
        high_count = sum(1 for entry in suspicious_entries if entry.get("threat_level") == "high")
        medium_count = sum(1 for entry in suspicious_entries if entry.get("threat_level") == "medium")
        info_count = sum(1 for entry in suspicious_entries if entry.get("type", "").startswith("info_"))
        
        self.results_text.insert(tk.END, f"Yüksek tehdit sayısı: {high_count}\n", "normal")
        self.results_text.insert(tk.END, f"Orta seviye tehdit sayısı: {medium_count}\n", "normal")
        self.results_text.insert(tk.END, f"Bilgi kayıtları sayısı: {info_count}\n\n", "normal")
        
        # Genel durum
        if threat_level == "high":
            self.results_text.insert(tk.END, f"⚠️ TEHDİT SEVİYESİ: {threat_text}\n", "error")
            self.results_text.insert(tk.END, "Ağınızda ciddi bir ARP Spoofing tehdidi tespit edildi!\n"
                                   "Hemen önlem almanız önerilir!\n", "error")
        elif threat_level == "medium":
            self.results_text.insert(tk.END, f"⚠️ TEHDİT SEVİYESİ: {threat_text}\n", "warning")
            self.results_text.insert(tk.END, "Ağınızda şüpheli ARP durumları tespit edildi.\n"
                                   "Dikkatli olunması önerilir.\n", "warning")
        else:
            self.results_text.insert(tk.END, f"✅ TEHDİT SEVİYESİ: {threat_text}\n", "success")
            self.results_text.insert(tk.END, "Ağınızda herhangi bir ARP Spoofing tehdidi tespit edilmedi.\n"
                                   "Ağınız şu an güvenli görünüyor.\n", "success")
        
        # Metin alanını salt okunur yap
        self.results_text.config(state=tk.DISABLED)

class ThreatAnalysisScreen(BaseScreen):
    """Tehdit Analizi Ekranı"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.last_scan_result = None
        self.threat_items = []
    
    def _create_widgets(self):
        """Tehdit analizi ekranının widget'larını oluşturur"""
        # Üst başlık
        header_frame = tk.Frame(self.frame, bg=THEME["background"], height=60)
        header_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        # Başlık
        title = tk.Label(header_frame, text="Tehdit Analizi", font=("Arial", 24, "bold"),
                       bg=THEME["background"], fg=THEME["text_primary"])
        title.pack(side=tk.LEFT)
        
        # Tarama butonu
        self.scan_button = SpotifyButton(header_frame, text="Yeniden Tara", 
                                      command=self.app.start_scan)
        self.scan_button.pack(side=tk.RIGHT, pady=10)
        
        # Tehdit özeti
        summary_frame = tk.Frame(self.frame, bg=THEME["background"])
        summary_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Özet kartı
        summary_card = RoundedFrame(summary_frame, bg=THEME["card_background"], 
                                 corner_radius=THEME["radius_medium"], height=80)
        summary_card.pack(fill=tk.X)
        
        # Özet içeriği
        self.summary_content = tk.Frame(summary_card, bg=THEME["card_background"])
        self.summary_content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Tehdit durumu etiketi
        self.threat_status = tk.Label(self.summary_content, text="Tehdit Durumu: Bilinmiyor", 
                                   font=("Arial", 14, "bold"), 
                                   bg=THEME["card_background"], fg=THEME["text_primary"])
        self.threat_status.pack(side=tk.LEFT, padx=20)
        
        # Güvenlik rozeti
        self.security_badge = StatusBadge(self.summary_content, status="none", text="Bilinmiyor", 
                                       width=120, height=30)
        self.security_badge.pack(side=tk.LEFT, padx=20)
        
        # Son tarama zamanı
        self.last_scan_time = tk.Label(self.summary_content, text="Henüz tarama yapılmadı", 
                                    font=("Arial", 11), 
                                    bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.last_scan_time.pack(side=tk.LEFT, padx=20)
        
        # Ana içerik - tehdit listesi
        content_frame = tk.Frame(self.frame, bg=THEME["background"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tehdit listesi kartı
        self.threats_card = RoundedFrame(content_frame, bg=THEME["card_background"], 
                                     corner_radius=THEME["radius_medium"])
        self.threats_card.pack(fill=tk.BOTH, expand=True)
        
        # Tehdit listesi başlığı
        threats_title = tk.Label(self.threats_card, text="Tespit Edilen Tehditler", 
                              font=("Arial", 16, "bold"), 
                              bg=THEME["card_background"], fg=THEME["text_primary"])
        threats_title.pack(pady=(15, 10))
        
        # Kaydırılabilir içerik alanı
        self.scroll_canvas = tk.Canvas(self.threats_card, bg=THEME["card_background"], 
                                   highlightthickness=0)
        self.scroll_canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Kaydırma çubuğu
        scrollbar = ttk.Scrollbar(self.scroll_canvas, orient=tk.VERTICAL, 
                               command=self.scroll_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas'ı kaydırma çubuğuna bağla
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)
        
        # İçerik çerçevesi
        self.threats_frame = tk.Frame(self.scroll_canvas, bg=THEME["card_background"])
        self.threats_frame.bind("<Configure>", 
                            lambda e: self.scroll_canvas.configure(
                                scrollregion=self.scroll_canvas.bbox("all")))
        
        # Canvas'a içerik çerçevesini ekle
        self.canvas_frame = self.scroll_canvas.create_window((0, 0), window=self.threats_frame, 
                                                       anchor="nw")
        
        # Canvas yeniden boyutlandırıldığında içerik çerçevesini de boyutlandır
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Bilgi metni
        self.no_threats_label = tk.Label(self.threats_frame, text="Henüz tarama yapılmadı", 
                                     font=("Arial", 14), 
                                     bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.no_threats_label.pack(pady=50)
    
    def _on_canvas_configure(self, event):
        """Canvas boyutu değiştiğinde içerik çerçevesini günceller"""
        width = event.width
        self.scroll_canvas.itemconfig(self.canvas_frame, width=width)
    
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        super().on_show()
        
        # Son tarama sonuçlarını göster
        if self.last_scan_result:
            self.display_threats(self.last_scan_result)
    
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        self.last_scan_result = result
        
        # Ekran görünür durumdaysa sonuçları göster
        if self.is_showing:
            self.display_threats(result)
    
    def display_threats(self, result):
        """Tarama sonucundaki tehditleri gösterir"""
        # Mevcut tehdit öğelerini temizle
        for item in self.threat_items:
            item.destroy()
        
        self.threat_items = []
        
        if "error" in result:
            # Hata durumunda
            self.threat_status.config(text="Tehdit Durumu: Hata", fg=THEME["error"])
            self.security_badge.set_status("unknown", "Hata")
            self.last_scan_time.config(text=f"Hata: {result['error']}")
            
            self.no_threats_label.config(text=f"Tarama hatası: {result['error']}")
            self.no_threats_label.pack(pady=50)
            return
        
        # Özet bilgileri güncelle
        timestamp = result.get("timestamp", time.time())
        self.last_scan_time.config(text=f"Son tarama: {format_timestamp(timestamp)}")
        
        # Tehdit durumu
        threat_level = result.get("threat_level", "unknown")
        status_text = threat_level_to_text(threat_level)
        
        self.threat_status.config(text=f"Tehdit Durumu: {status_text}")
        self.security_badge.set_status(threat_level, status_text)
        
        # Şüpheli durumları filtrele
        suspicious_entries = result.get("suspicious_entries", [])
        
        # Bilgi türü girdileri çıkar ve gerçek tehditleri bul
        real_threats = [entry for entry in suspicious_entries 
                      if not entry.get("type", "").startswith("info_")]
        
        # Tehdit yok ise bilgi mesajı göster
        if not real_threats:
            self.no_threats_label.config(text="Herhangi bir tehdit tespit edilmedi")
            self.no_threats_label.pack(pady=50)
            return
        
        # Bilgi mesajını gizle
        self.no_threats_label.pack_forget()
        
        # Önce yüksek tehditleri göster
        high_threats = [t for t in real_threats if t.get("threat_level") == "high"]
        medium_threats = [t for t in real_threats if t.get("threat_level") == "medium"]
        
        # Yüksek tehditleri ekle
        if high_threats:
            separator = tk.Label(self.threats_frame, text="YÜKSEK TEHDİTLER", 
                              font=("Arial", 12, "bold"), bg=THEME["card_background"], 
                              fg=THEME["error"])
            separator.pack(fill=tk.X, pady=(10, 5))
            self.threat_items.append(separator)
            
            for threat in high_threats:
                item = ThreatItem(self.threats_frame, threat, "high")
                item.pack(fill=tk.X, padx=10, pady=5)
                self.threat_items.append(item)
        
        # Orta tehditleri ekle
        if medium_threats:
            separator = tk.Label(self.threats_frame, text="ORTA SEVİYE TEHDİTLER", 
                              font=("Arial", 12, "bold"), bg=THEME["card_background"], 
                              fg=THEME["warning"])
            separator.pack(fill=tk.X, pady=(15, 5))
            self.threat_items.append(separator)
            
            for threat in medium_threats:
                item = ThreatItem(self.threats_frame, threat, "medium")
                item.pack(fill=tk.X, padx=10, pady=5)
                self.threat_items.append(item)

class ThreatItem(tk.Frame):
    """Tehdit öğesi bileşeni"""
    def __init__(self, parent, threat_data, level):
        super().__init__(parent, bg=THEME["background"], padx=5, pady=5)
        
        # Threat verisi
        self.threat_data = threat_data
        self.level = level
        
        # Renk ayarla
        if level == "high":
            self.color = THEME["error"]
        elif level == "medium":
            self.color = THEME["warning"]
        else:
            self.color = THEME["secondary"]
        
        # Kart çerçevesi
        self.card = RoundedFrame(self, bg=THEME["card_background"], 
                              corner_radius=THEME["radius_small"])
        self.card.pack(fill=tk.BOTH, expand=True)
        
        # İçerik çerçevesi
        content = tk.Frame(self.card, bg=THEME["card_background"], padx=15, pady=10)
        content.pack(fill=tk.BOTH)
        
        # Tehdit türü bölümü
        type_frame = tk.Frame(content, bg=THEME["card_background"])
        type_frame.pack(fill=tk.X)
        
        # Tehdit ikonları
        icon = "❌" if level == "high" else "⚠️"
        threat_icon = tk.Label(type_frame, text=icon, font=("Arial", 16), 
                            bg=THEME["card_background"], fg=self.color)
        threat_icon.pack(side=tk.LEFT)
        
        # Tehdit türü
        threat_type = threat_data.get("type", "unknown").replace("_", " ").title()
        type_label = tk.Label(type_frame, text=threat_type, font=("Arial", 12, "bold"), 
                           bg=THEME["card_background"], fg=THEME["text_primary"])
        type_label.pack(side=tk.LEFT, padx=5)
        
        # Durum rozeti
        status_text = "Kritik" if level == "high" else "Şüpheli"
        status_badge = StatusBadge(type_frame, status=level, text=status_text, 
                                width=80, height=24)
        status_badge.pack(side=tk.RIGHT)
        
        # Tehdit açıklaması
        message = threat_data.get("message", "").replace("⚠️ ", "").replace("❌ ", "")
        message_label = tk.Label(content, text=message, font=("Arial", 11), 
                              bg=THEME["card_background"], fg=THEME["text_secondary"],
                              wraplength=600, justify=tk.LEFT)
        message_label.pack(fill=tk.X, pady=(5, 0), anchor="w")
        
        # Tehdit detayları
        details_frame = tk.Frame(content, bg=THEME["card_background"], pady=5)
        details_frame.pack(fill=tk.X)
        
        # MAC adresi detayı
        if "mac" in threat_data:
            mac_label = tk.Label(details_frame, text=f"MAC: {threat_data['mac']}", 
                              font=("Arial", 10), bg=THEME["card_background"], 
                              fg=THEME["text_secondary"])
            mac_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # IP adresi detayı
        if "ip" in threat_data:
            ip_label = tk.Label(details_frame, text=f"IP: {threat_data['ip']}", 
                             font=("Arial", 10), bg=THEME["card_background"], 
                             fg=THEME["text_secondary"])
            ip_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Birden çok IP adresi detayı
        if "ips" in threat_data:
            ips_text = ", ".join(threat_data["ips"][:3])
            if len(threat_data["ips"]) > 3:
                ips_text += f"... (+{len(threat_data['ips']) - 3} daha)"
                
            ips_label = tk.Label(details_frame, text=f"IP'ler: {ips_text}", 
                              font=("Arial", 10), bg=THEME["card_background"], 
                              fg=THEME["text_secondary"])
            ips_label.pack(side=tk.LEFT)

class HistoryScreen(BaseScreen):
    """Geçmiş Ekranı"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.history_items = []
    
    def _create_widgets(self):
        """Geçmiş ekranının widget'larını oluşturur"""
        # Üst başlık
        header_frame = tk.Frame(self.frame, bg=THEME["background"], height=60)
        header_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        # Başlık
        title = tk.Label(header_frame, text="Tarama Geçmişi", font=("Arial", 24, "bold"),
                       bg=THEME["background"], fg=THEME["text_primary"])
        title.pack(side=tk.LEFT)
        
        # Geçmiş grafiği kartı - üst kısım
        chart_frame = tk.Frame(self.frame, bg=THEME["background"], height=200)
        chart_frame.pack(fill=tk.X, padx=20, pady=5)
        
        chart_card = RoundedFrame(chart_frame, bg=THEME["card_background"], 
                               corner_radius=THEME["radius_medium"])
        chart_card.pack(fill=tk.BOTH, expand=True)
        
        # Grafik başlığı
        chart_title = tk.Label(chart_card, text="Tehdit Geçmişi", 
                            font=("Arial", 16, "bold"), 
                            bg=THEME["card_background"], fg=THEME["text_primary"])
        chart_title.pack(pady=(15, 5))
        
        # Geçmiş grafiği
        self.history_chart = AnimatedChart(chart_card, height=160, 
                                       title="Son 5 Tarama")
        self.history_chart.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Geçmiş listesi - alt kısım
        history_frame = tk.Frame(self.frame, bg=THEME["background"])
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        history_card = RoundedFrame(history_frame, bg=THEME["card_background"], 
                                 corner_radius=THEME["radius_medium"])
        history_card.pack(fill=tk.BOTH, expand=True)
        
        # Liste başlığı
        history_title = tk.Label(history_card, text="Tarama Kayıtları", 
                              font=("Arial", 16, "bold"), 
                              bg=THEME["card_background"], fg=THEME["text_primary"])
        history_title.pack(pady=(15, 10))
        
        # Kaydırılabilir liste
        self.scroll_canvas = tk.Canvas(history_card, bg=THEME["card_background"], 
                                   highlightthickness=0)
        self.scroll_canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Kaydırma çubuğu
        scrollbar = ttk.Scrollbar(self.scroll_canvas, orient=tk.VERTICAL, 
                               command=self.scroll_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas'ı kaydırma çubuğuna bağla
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)
        
        # İçerik çerçevesi
        self.history_list_frame = tk.Frame(self.scroll_canvas, bg=THEME["card_background"])
        self.history_list_frame.bind("<Configure>", 
                                 lambda e: self.scroll_canvas.configure(
                                     scrollregion=self.scroll_canvas.bbox("all")))
        
        # Canvas'a içerik çerçevesini ekle
        self.canvas_frame = self.scroll_canvas.create_window((0, 0), window=self.history_list_frame, 
                                                       anchor="nw")
        
        # Canvas yeniden boyutlandırıldığında içerik çerçevesini de boyutlandır
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Bilgi metni
        self.no_history_label = tk.Label(self.history_list_frame, text="Henüz tarama geçmişi yok", 
                                     font=("Arial", 14), 
                                     bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.no_history_label.pack(pady=50)
    
    def _on_canvas_configure(self, event):
        """Canvas boyutu değiştiğinde içerik çerçevesini günceller"""
        width = event.width
        self.scroll_canvas.itemconfig(self.canvas_frame, width=width)
    
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        super().on_show()
        
        # Geçmişi göster
        self.display_history()
    
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        # Ekran görünür durumdaysa geçmişi güncelle
        if self.is_showing:
            self.display_history()
    
    def display_history(self):
        """Tarama geçmişini gösterir"""
        # Mevcut geçmiş öğelerini temizle
        for item in self.history_items:
            item.destroy()
        
        self.history_items = []
        
        # Tarama geçmişini al
        scan_history = self.app.scanner.scan_history
        
        # Geçmiş grafiğini güncelle
        history_data = create_scan_history_chart(scan_history)
        self.history_chart.set_data(history_data)
        
        # Geçmiş boş ise bilgi mesajı göster
        if not scan_history:
            self.no_history_label.config(text="Henüz tarama geçmişi yok")
            self.no_history_label.pack(pady=50)
            return
        
        # Bilgi mesajını gizle
        self.no_history_label.pack_forget()
        
        # En yeniden en eskiye doğru göster
        reversed_history = list(reversed(scan_history))
        
        for result in reversed_history:
            item = HistoryItem(self.history_list_frame, result)
            item.pack(fill=tk.X, padx=10, pady=5)
            self.history_items.append(item)

class HistoryItem(tk.Frame):
    """Geçmiş öğesi bileşeni"""
    def __init__(self, parent, history_data):
        super().__init__(parent, bg=THEME["background"], padx=5, pady=5)
        
        # Geçmiş verisi
        self.history_data = history_data
        
        # Hata durumunu kontrol et
        has_error = "error" in history_data
        
        # Tehdit seviyesini al
        if has_error:
            threat_level = "unknown"
        else:
            threat_level = history_data.get("threat_level", "unknown")
        
        # Renk ayarla
        self.color = get_status_color(threat_level)
        
        # Kart çerçevesi
        self.card = RoundedFrame(self, bg=THEME["card_background"], 
                              corner_radius=THEME["radius_small"])
        self.card.pack(fill=tk.BOTH, expand=True)
        
        # İçerik çerçevesi
        content = tk.Frame(self.card, bg=THEME["card_background"], padx=15, pady=10)
        content.pack(fill=tk.BOTH)
        
        # Üst satır
        top_frame = tk.Frame(content, bg=THEME["card_background"])
        top_frame.pack(fill=tk.X)
        
        # Zaman bilgisi
        timestamp = history_data.get("timestamp", time.time())
        time_str = format_timestamp(timestamp)
        time_ago = format_time_ago(timestamp)
        
        time_label = tk.Label(top_frame, text=time_str, font=("Arial", 12, "bold"), 
                           bg=THEME["card_background"], fg=THEME["text_primary"])
        time_label.pack(side=tk.LEFT)
        
        time_ago_label = tk.Label(top_frame, text=f"({time_ago})", font=("Arial", 10), 
                               bg=THEME["card_background"], fg=THEME["text_secondary"])
        time_ago_label.pack(side=tk.LEFT, padx=5)
        
        # Durum rozeti
        if has_error:
            status_text = "Hata"
        else:
            status_text = threat_level_to_text(threat_level)
        
        status_badge = StatusBadge(top_frame, status=threat_level, text=status_text, 
                                width=120, height=24)
        status_badge.pack(side=tk.RIGHT)
        
        # Alt çerçeve - detaylar
        if has_error:
            # Hata mesajı
            error_message = history_data.get("error", "Bilinmeyen hata")
            details_label = tk.Label(content, text=f"Hata: {error_message}", 
                                  font=("Arial", 11), bg=THEME["card_background"], 
                                  fg=THEME["error"], wraplength=600, justify=tk.LEFT)
            details_label.pack(fill=tk.X, pady=(5, 0), anchor="w")
        else:
            # Tehdit detayları
            bottom_frame = tk.Frame(content, bg=THEME["card_background"], pady=5)
            bottom_frame.pack(fill=tk.X)
            
            # Ağ geçidi
            gateway = history_data.get("gateway", {"ip": "Bilinmiyor", "mac": "Bilinmiyor"})
            gateway_label = tk.Label(bottom_frame, text=f"Ağ Geçidi: {gateway['ip']}", 
                                  font=("Arial", 11), bg=THEME["card_background"], 
                                  fg=THEME["text_secondary"])
            gateway_label.pack(side=tk.LEFT, padx=(0, 15))
            
            # Tehdit sayıları
            suspicious_entries = history_data.get("suspicious_entries", [])
            
            high_threats = sum(1 for entry in suspicious_entries 
                            if entry.get("threat_level") == "high")
            
            medium_threats = sum(1 for entry in suspicious_entries 
                              if entry.get("threat_level") == "medium")
            
            info_entries = sum(1 for entry in suspicious_entries 
                            if entry.get("type", "").startswith("info_"))
            
            threat_label = tk.Label(bottom_frame, text=f"Tehditler: {high_threats} yüksek, {medium_threats} orta", 
                                 font=("Arial", 11), bg=THEME["card_background"], 
                                 fg=THEME["text_secondary"])
            threat_label.pack(side=tk.LEFT)
            
            # Detay düğmesi eklenebilir

class SettingsScreen(BaseScreen):
    """Ayarlar Ekranı"""
    def __init__(self, parent, app):
        # Önce değişkenleri tanımlayalım
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg=THEME["background"])
        self.is_showing = False
    
        # Ayarları yükle
        try:
            from modules.settings import get_setting
        
            # Ayarlar değişkenleri - varsayılan değerleri yüklenen ayarlardan al
            self.scan_interval = tk.StringVar(value=str(get_setting("scan_interval", 24)))
            self.auto_scan = tk.BooleanVar(value=get_setting("auto_scan", False))
            self.dark_mode = tk.BooleanVar(value=get_setting("dark_mode", True))
            self.notifications = tk.BooleanVar(value=get_setting("notifications_enabled", True))
          
            print(f"Ayarlar yüklendi: scan_interval={self.scan_interval.get()}, auto_scan={self.auto_scan.get()},    dark_mode={self.dark_mode.get()}, notifications={self.notifications.get()}")
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
            # Hata durumunda varsayılan değerleri kullan
            self.scan_interval = tk.StringVar(value="24")
            self.auto_scan = tk.BooleanVar(value=False)
            self.dark_mode = tk.BooleanVar(value=True)
            self.notifications = tk.BooleanVar(value=True)
    
        # Şimdi widget'ları oluşturalım
        self._create_widgets()

    def _create_widgets(self):
        """Ayarlar ekranının widget'larını oluşturur"""
        # Üst başlık
        header_frame = tk.Frame(self.frame, bg=THEME["background"], height=60)
        header_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        # Başlık
        title = tk.Label(header_frame, text="Ayarlar", font=("Arial", 24, "bold"),
                       bg=THEME["background"], fg=THEME["text_primary"])
        title.pack(side=tk.LEFT)
        
        # Kaydet butonu
        self.save_button = SpotifyButton(header_frame, text="Ayarları Kaydet", 
                                      command=self.save_settings)
        self.save_button.pack(side=tk.RIGHT, pady=10)
        
        # Ayarlar kartı
        settings_frame = tk.Frame(self.frame, bg=THEME["background"])
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        settings_card = RoundedFrame(settings_frame, bg=THEME["card_background"], 
                                  corner_radius=THEME["radius_medium"])
        settings_card.pack(fill=tk.BOTH, expand=True)
        
        # Ayarlar başlığı
        settings_title = tk.Label(settings_card, text="Uygulama Ayarları", 
                               font=("Arial", 16, "bold"), 
                               bg=THEME["card_background"], fg=THEME["text_primary"])
        settings_title.pack(pady=(15, 10))
        
        # Ayarlar listesi için çerçeve
        settings_list = tk.Frame(settings_card, bg=THEME["card_background"])
        settings_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tarama ayarları bölümü
        scan_section = tk.Label(settings_list, text="TARAMA AYARLARI", 
                             font=("Arial", 12, "bold"), 
                             bg=THEME["card_background"], fg=THEME["primary"])
        scan_section.pack(anchor="w", pady=(0, 10))
        
        # Tarama sıklığı ayarı
        interval_frame = tk.Frame(settings_list, bg=THEME["card_background"], pady=5)
        interval_frame.pack(fill=tk.X)
        
        interval_label = tk.Label(interval_frame, text="Periyodik tarama sıklığı:", 
                               font=("Arial", 11), 
                               bg=THEME["card_background"], fg=THEME["text_primary"])
        interval_label.pack(side=tk.LEFT)
        
        # Sıklık seçim kutusu
        interval_values = ["1", "2", "4", "6", "8", "12", "24", "48", "72"]
        interval_dropdown = ttk.Combobox(interval_frame, textvariable=self.scan_interval,
                                      values=interval_values, width=4)
        interval_dropdown.pack(side=tk.LEFT, padx=10)
        
        hours_label = tk.Label(interval_frame, text="saat", 
                            font=("Arial", 11), 
                            bg=THEME["card_background"], fg=THEME["text_primary"])
        hours_label.pack(side=tk.LEFT)
        
        # Otomatik tarama ayarı
        auto_scan_frame = tk.Frame(settings_list, bg=THEME["card_background"], pady=5)
        auto_scan_frame.pack(fill=tk.X)
        
        auto_scan_check = tk.Checkbutton(auto_scan_frame, text="Uygulama başladığında otomatik tarama yap", 
                                      variable=self.auto_scan, 
                                      bg=THEME["card_background"], fg=THEME["text_primary"],
                                      selectcolor=THEME["background"], 
                                      activebackground=THEME["card_background"],
                                      activeforeground=THEME["text_primary"])
        auto_scan_check.pack(anchor="w")
        
        # Arayüz ayarları bölümü
        ui_section = tk.Label(settings_list, text="ARAYÜZ AYARLARI", 
                           font=("Arial", 12, "bold"), 
                           bg=THEME["card_background"], fg=THEME["primary"])
        ui_section.pack(anchor="w", pady=(20, 10))
        
        # Karanlık mod ayarı
        dark_mode_frame = tk.Frame(settings_list, bg=THEME["card_background"], pady=5)
        dark_mode_frame.pack(fill=tk.X)
        
        dark_mode_check = tk.Checkbutton(dark_mode_frame, text="Karanlık mod (yeniden başlatma gerektirir)", 
                                      variable=self.dark_mode, 
                                      bg=THEME["card_background"], fg=THEME["text_primary"],
                                      selectcolor=THEME["background"], 
                                      activebackground=THEME["card_background"],
                                      activeforeground=THEME["text_primary"])
        dark_mode_check.pack(anchor="w")
        
        # Bildirim ayarları bölümü
        notification_section = tk.Label(settings_list, text="BİLDİRİM AYARLARI", 
                                     font=("Arial", 12, "bold"), 
                                     bg=THEME["card_background"], fg=THEME["primary"])
        notification_section.pack(anchor="w", pady=(20, 10))
        
        # Bildirim ayarı
        notification_frame = tk.Frame(settings_list, bg=THEME["card_background"], pady=5)
        notification_frame.pack(fill=tk.X)
        
        notification_check = tk.Checkbutton(notification_frame, text="Tehdit tespit edildiğinde bildirim göster", 
                                         variable=self.notifications, 
                                         bg=THEME["card_background"], fg=THEME["text_primary"],
                                         selectcolor=THEME["background"], 
                                         activebackground=THEME["card_background"],
                                         activeforeground=THEME["text_primary"])
        notification_check.pack(anchor="w")
        
        # Uygulama bilgileri bölümü
        about_section = tk.Label(settings_list, text="UYGULAMA HAKKINDA", 
                              font=("Arial", 12, "bold"), 
                              bg=THEME["card_background"], fg=THEME["primary"])
        about_section.pack(anchor="w", pady=(20, 10))
        
        # Versiyon bilgisi
        version_frame = tk.Frame(settings_list, bg=THEME["card_background"], pady=5)
        version_frame.pack(fill=tk.X)
        
        version_label = tk.Label(version_frame, text="ARP Guard v2.0", 
                              font=("Arial", 11), 
                              bg=THEME["card_background"], fg=THEME["text_primary"])
        version_label.pack(anchor="w")
        
        # Geliştirici bilgisi
        dev_frame = tk.Frame(settings_list, bg=THEME["card_background"], pady=5)
        dev_frame.pack(fill=tk.X)
        
        dev_label = tk.Label(dev_frame, text="Developed by Studio Team, 2025", 
                          font=("Arial", 11), 
                          bg=THEME["card_background"], fg=THEME["text_secondary"])
        dev_label.pack(anchor="w")
    
    def save_settings(self):
        """Ayarları kaydeder"""
        try:
            # Tarama sıklığını ayarla
            interval = int(self.scan_interval.get())
            if interval < 1:
                interval = 1
            elif interval > 72:
                interval = 72
        
            # Ayarları dictionary'e topla
            settings_dict = {
                "scan_interval": interval,
                "auto_scan": self.auto_scan.get(),
                "dark_mode": self.dark_mode.get(),
                "notifications_enabled": self.notifications.get(),
                "periodic_scan_active": self.app.scanner.periodic_running if hasattr(self.app.scanner, "periodic_running") else False
            }
        
            # Ayarları kaydet
            print(f"Ayarlar kaydediliyor: {settings_dict}")
            from modules.settings import update_settings
            success = update_settings(settings_dict)
        
            # Periyodik tarama varsa güncelle
            if self.app.scanner.periodic_running:
                self.app.stop_periodic_scan()
                self.app.start_periodic_scan(interval)
        
            # Kullanıcıya bilgi ver
            if success:
                messagebox.showinfo("Ayarlar", "Ayarlar başarıyla kaydedildi.")
            else:
                messagebox.showwarning("Uyarı", "Ayarlar kaydedildi ancak dosyaya yazılamadı.")
        
        except ValueError:
            # Geçersiz değer girilmişse
            self.scan_interval.set("24")
            messagebox.showerror("Hata", "Lütfen geçerli bir tarama sıklığı girin.")
        except Exception as e:
            # Diğer hatalar
            import traceback
            traceback.print_exc()
            messagebox.showerror("Hata", f"Ayarlar kaydedilirken bir hata oluştu: {e}")
