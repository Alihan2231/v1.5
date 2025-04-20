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
import logging
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
from modules.settings import get_setting, set_setting, update_settings, reset_settings

# Loglama
logger = logging.getLogger("NetworkShieldPro.screens")

class BaseScreen:
    """Tüm ekranlar için temel sınıf"""
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg=THEME["background"])
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.pack_propagate(False)
        
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        pass
        
    def on_hide(self):
        """Ekran gizlendiğinde çağrılır"""
        pass
        
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        pass

class DashboardScreen(BaseScreen):
    """Ana gösterge paneli ekranı"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        # Dashboard oluştur
        self._create_widgets()
        self.last_scan_result = None
        
    def _create_widgets(self):
        """Arayüz öğelerini oluşturur"""
        # Ana başlık
        title_frame = tk.Frame(self.frame, bg=THEME["background"], height=60)
        title_frame.pack(fill=tk.X, pady=(20, 0))
        
        title_label = tk.Label(title_frame, text="Gösterge Paneli", font=("Arial", 24, "bold"), 
                              bg=THEME["background"], fg=THEME["text_primary"])
        title_label.pack(side=tk.LEFT, padx=30)
        
        # Tarama butonu
        self.scan_button = SpotifyButton(title_frame, text="Ağı Tara", command=self._start_scan,
                                       width=120, height=36, bg=THEME["primary"])
        self.scan_button.pack(side=tk.RIGHT, padx=30)
        
        # Ana içerik grid düzeni
        content_frame = tk.Frame(self.frame, bg=THEME["background"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Sol sütun (Güvenlik özeti ve son tarama)
        left_column = tk.Frame(content_frame, bg=THEME["background"])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Güvenlik skoru kartı
        self.security_card = RoundedFrame(left_column, bg=THEME["card_background"], height=250)
        self.security_card.pack(fill=tk.X, pady=10)
        
        security_title = tk.Label(self.security_card, text="Ağ Güvenlik Skoru", 
                                font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                                fg=THEME["text_primary"])
        security_title.place(x=20, y=20)
        
        # Güvenlik skoru göstergesi
        self.security_score_frame = tk.Frame(self.security_card, bg=THEME["card_background"])
        self.security_score_frame.place(x=20, y=60, width=210, height=170)
        
        self.score_progressbar = CircularProgressbar(self.security_score_frame, progress=0, 
                                                 width=170, height=170, thickness=12)
        self.score_progressbar.pack(pady=10)
        
        # Güvenlik durumu
        self.security_status = tk.Label(self.security_card, text="Bilinmiyor", 
                                     font=("Arial", 14, "bold"), bg=THEME["card_background"], 
                                     fg=THEME["warning"])
        self.security_status.place(x=240, y=90)
        
        self.security_details = tk.Label(self.security_card, text="Ağınızın güvenlik durumu bilinmiyor.\nTarama yaparak güvenlik durumunu öğrenebilirsiniz.", 
                                     font=("Arial", 11), bg=THEME["card_background"], 
                                     fg=THEME["text_secondary"], justify=tk.LEFT)
        self.security_details.place(x=240, y=120)
        
        # Son tarama kartı
        self.last_scan_card = RoundedFrame(left_column, bg=THEME["card_background"], height=250)
        self.last_scan_card.pack(fill=tk.X, pady=10)
        
        last_scan_title = tk.Label(self.last_scan_card, text="Son Tarama", 
                                 font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                                 fg=THEME["text_primary"])
        last_scan_title.place(x=20, y=20)
        
        # Son tarama zamanı
        self.last_scan_time = tk.Label(self.last_scan_card, text="Henüz tarama yapılmadı", 
                                    font=("Arial", 12), bg=THEME["card_background"], 
                                    fg=THEME["text_secondary"])
        self.last_scan_time.place(x=20, y=50)
        
        # Son tarama özeti
        self.last_scan_summary_frame = tk.Frame(self.last_scan_card, bg=THEME["card_background"])
        self.last_scan_summary_frame.place(x=20, y=80, width=400, height=150)
        
        # Varsayılan içerik
        self.no_scan_label = tk.Label(self.last_scan_summary_frame, 
                                   text="Tarama yapılmadı", font=("Arial", 14),
                                   bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.no_scan_label.pack(pady=50)
        
        # Sağ sütun (Tarama geçmişi, tehdit grafiği)
        right_column = tk.Frame(content_frame, bg=THEME["background"])
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Tehdit dağılımı kartı
        self.threat_chart_card = RoundedFrame(right_column, bg=THEME["card_background"], height=250)
        self.threat_chart_card.pack(fill=tk.X, pady=10)
        
        threat_chart_title = tk.Label(self.threat_chart_card, text="Tehdit Dağılımı", 
                                    font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                                    fg=THEME["text_primary"])
        threat_chart_title.place(x=20, y=20)
        
        # Tehdit grafiği
        self.threat_chart_frame = tk.Frame(self.threat_chart_card, bg=THEME["card_background"])
        self.threat_chart_frame.place(x=20, y=60, width=400, height=170)
        
        self.threat_chart = AnimatedChart(self.threat_chart_frame, width=400, height=170)
        self.threat_chart.pack(fill=tk.BOTH, expand=True)
        
        # Tehdit geçmişi kartı
        self.threat_history_card = RoundedFrame(right_column, bg=THEME["card_background"], height=250)
        self.threat_history_card.pack(fill=tk.X, pady=10)
        
        threat_history_title = tk.Label(self.threat_history_card, text="Tehdit Geçmişi", 
                                      font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                                      fg=THEME["text_primary"])
        threat_history_title.place(x=20, y=20)
        
        # Tehdit geçmişi grafiği
        self.threat_history_frame = tk.Frame(self.threat_history_card, bg=THEME["card_background"])
        self.threat_history_frame.place(x=20, y=60, width=400, height=170)
        
        self.history_chart = AnimatedChart(self.threat_history_frame, width=400, height=170)
        self.history_chart.pack(fill=tk.BOTH, expand=True)
        
    def _start_scan(self):
        """Tarama başlatır"""
        if self.app.start_scan():
            self.scan_button.configure(text="Taranıyor...", state="disabled")
    
    def _create_scan_summary(self, result):
        """Tarama sonuç özetini oluşturur"""
        # Eski özet widget'ları temizle
        for widget in self.last_scan_summary_frame.winfo_children():
            widget.destroy()
        
        # Tehdit seviyesine göre renk
        threat_level = result.get("threat_level", "unknown")
        threat_color = get_status_color(threat_level)
        
        # Çerçeve oluştur
        summary_canvas = tk.Canvas(self.last_scan_summary_frame, bg=THEME["card_background"],
                                 highlightthickness=0, width=400, height=150)
        summary_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Ağ geçidi bilgilerini göster
        gateway = result.get("gateway", {})
        gateway_ip = gateway.get("ip", "Bilinmiyor")
        gateway_mac = gateway.get("mac", "Bilinmiyor")
        
        summary_canvas.create_text(10, 10, text="Ağ Geçidi:", font=("Arial", 12, "bold"), 
                                  fill=THEME["text_primary"], anchor="w")
        summary_canvas.create_text(10, 30, text=f"IP: {gateway_ip}", font=("Arial", 11), 
                                  fill=THEME["text_secondary"], anchor="w")
        summary_canvas.create_text(10, 50, text=f"MAC: {format_mac_for_display(gateway_mac)}", 
                                 font=("Arial", 11), fill=THEME["text_secondary"], anchor="w")
        
        # Şüpheli durumların sayısını göster
        suspicious_entries = result.get("suspicious_entries", [])
        high_threats = sum(1 for entry in suspicious_entries if entry.get("threat_level") == "high")
        medium_threats = sum(1 for entry in suspicious_entries if entry.get("threat_level") == "medium")
        
        summary_canvas.create_text(10, 80, text="Tehditler:", font=("Arial", 12, "bold"), 
                                fill=THEME["text_primary"], anchor="w")
        
        if high_threats > 0:
            summary_canvas.create_text(10, 100, text=f"• {high_threats} yüksek seviye tehdit", 
                                    font=("Arial", 11), fill=THEME["error"], anchor="w")
        
        if medium_threats > 0:
            summary_canvas.create_text(10, 120, text=f"• {medium_threats} orta seviye tehdit", 
                                     font=("Arial", 11), fill=THEME["warning"], anchor="w")
        
        if high_threats == 0 and medium_threats == 0:
            summary_canvas.create_text(10, 100, text="• Tehdit bulunamadı", font=("Arial", 11), 
                                     fill=THEME["success"], anchor="w")
        
        # Tehdit durumunu göster
        threat_text = threat_level_to_text(threat_level)
        summary_canvas.create_text(230, 25, text=threat_text, font=("Arial", 14, "bold"), 
                                 fill=threat_color)
        
        # Durum rozeti
        if threat_level == "high":
            badge_text = "TEHLİKE"
            badge_status = "error"
        elif threat_level == "medium":
            badge_text = "DİKKAT"
            badge_status = "warning"
        else:
            badge_text = "GÜVENLİ"
            badge_status = "success"
        
        badge = StatusBadge(summary_canvas, text=badge_text, status=badge_status, width=80, height=24)
        badge.place(x=290, y=20)
    
    def _update_security_score(self, score, threat_level):
        """Güvenlik skorunu günceller"""
        self.score_progressbar.set_progress(score)
        
        # Durum metni ve rengi ayarla
        if score >= 80:
            status_text = "Güvenli"
            status_color = THEME["success"]
        elif score >= 50:
            status_text = "Orta Seviyede Güvenli"
            status_color = THEME["warning"]
        else:
            status_text = "Risk Altında"
            status_color = THEME["error"]
        
        self.security_status.config(text=status_text, fg=status_color)
        
        # Durum detayları
        if threat_level == "high":
            details = "Ağınızda ciddi güvenlik tehditleri tespit edildi.\nAcil önlem almanız gerekmektedir."
        elif threat_level == "medium":
            details = "Ağınızda potansiyel güvenlik riskleri tespit edildi.\nDikkatli olmanız önerilir."
        elif threat_level == "none":
            details = "Ağınızda herhangi bir güvenlik tehdidi tespit edilmedi.\nGüvenlik durumu iyi görünüyor."
        else:
            details = "Ağınızın güvenlik durumu belirsiz.\nYeni bir tarama yapmayı deneyin."
        
        self.security_details.config(text=details)
    
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        try:
            logger.debug("DashboardScreen tarama tamamlandı bildirimi alındı")
            self.last_scan_result = result
            
            # Tarama sonuç zamanını güncelle
            scan_time = result.get("timestamp", time.time())
            self.last_scan_time.config(text=f"Son tarama: {format_time_ago(scan_time)}")
            
            # Tarama özeti
            self._create_scan_summary(result)
            
            # Güvenlik skoru
            security_score = get_network_security_score(result)
            self._update_security_score(security_score, result.get("threat_level", "unknown"))
            
            # Tehdit dağılımı grafiğini güncelle
            suspicious_entries = result.get("suspicious_entries", [])
            chart_data = create_threat_data_chart(suspicious_entries)
            self.threat_chart.set_data(chart_data)
            
            # Tehdit geçmişi grafiğini güncelle
            if hasattr(self.app, 'scanner'):
                scan_history = self.app.scanner.get_scan_history()
                history_data = create_scan_history_chart(scan_history)
                self.history_chart.set_data(history_data)
            
            # Tarama butonunu normal duruma getir
            self.scan_button.configure(text="Ağı Tara", state="normal")
        except Exception as e:
            logger.error(f"Tarama sonucu işlenirken hata: {e}")
            traceback.print_exc()
            # Hataya rağmen butonu normal duruma getir
            self.scan_button.configure(text="Ağı Tara", state="normal")
    
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        # En son tarama sonucunu güncelle
        if hasattr(self.app, 'scanner'):
            last_result = self.app.scanner.get_last_scan_result()
            if last_result:
                self.on_scan_completed(last_result)

class ScanScreen(BaseScreen):
    """Ağ tarama ekranı"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        # Tarama ekranı oluştur
        self._create_widgets()
        self.scan_in_progress = False
        self.devices = []  # Bulunan cihazlar listesi
        
    def _create_widgets(self):
        """Arayüz öğelerini oluşturur"""
        # Ana başlık
        title_frame = tk.Frame(self.frame, bg=THEME["background"], height=60)
        title_frame.pack(fill=tk.X, pady=(20, 0))
        
        title_label = tk.Label(title_frame, text="Ağ Taraması", font=("Arial", 24, "bold"), 
                            bg=THEME["background"], fg=THEME["text_primary"])
        title_label.pack(side=tk.LEFT, padx=30)
        
        # Tarama butonları
        buttons_frame = tk.Frame(title_frame, bg=THEME["background"])
        buttons_frame.pack(side=tk.RIGHT, padx=30)
        
        self.scan_button = SpotifyButton(buttons_frame, text="Ağı Tara", command=self._start_scan,
                                     width=120, height=36, bg=THEME["primary"])
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        self.periodic_button = SpotifyButton(buttons_frame, text="Periyodik Tarama", 
                                         command=self._toggle_periodic_scan,
                                         width=150, height=36, bg=THEME["secondary"])
        self.periodic_button.pack(side=tk.LEFT, padx=5)
        
        # Ana içerik
        content_frame = tk.Frame(self.frame, bg=THEME["background"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tarama durumu kartı
        self.status_card = RoundedFrame(content_frame, bg=THEME["card_background"], height=150)
        self.status_card.pack(fill=tk.X, pady=10)
        
        self.status_title = tk.Label(self.status_card, text="Tarama Durumu", 
                                 font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                                 fg=THEME["text_primary"])
        self.status_title.place(x=20, y=20)
        
        self.status_label = tk.Label(self.status_card, text="Hazır", 
                                 font=("Arial", 14), bg=THEME["card_background"], 
                                 fg=THEME["text_secondary"])
        self.status_label.place(x=20, y=50)
        
        self.last_scan_label = tk.Label(self.status_card, text="Son tarama: Henüz tarama yapılmadı", 
                                    font=("Arial", 12), bg=THEME["card_background"], 
                                    fg=THEME["text_tertiary"])
        self.last_scan_label.place(x=20, y=80)
        
        # Periyodik tarama durumu
        self.periodic_status = tk.Label(self.status_card, text="Periyodik tarama: Kapalı", 
                                    font=("Arial", 12), bg=THEME["card_background"], 
                                    fg=THEME["text_tertiary"])
        self.periodic_status.place(x=20, y=110)
        
        # Bulunan cihazlar kartı
        self.devices_card = RoundedFrame(content_frame, bg=THEME["card_background"])
        self.devices_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        devices_title = tk.Label(self.devices_card, text="Bulunan Cihazlar", 
                              font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                              fg=THEME["text_primary"])
        devices_title.place(x=20, y=20)
        
        # Tablo başlık çerçevesi
        header_frame = tk.Frame(self.devices_card, bg=THEME["card_background"])
        header_frame.place(x=20, y=60, right=20, height=30)
        
        # Tablo başlıkları
        header_columns = [
            {"text": "IP Adresi", "width": 150},
            {"text": "MAC Adresi", "width": 200},
            {"text": "Durum", "width": 150},
            {"text": "Arayüz", "width": 100},
            {"text": "Son Görülme", "width": 150}
        ]
        
        for i, col in enumerate(header_columns):
            x_pos = sum(c["width"] for c in header_columns[:i])
            header = tk.Label(header_frame, text=col["text"], font=("Arial", 12, "bold"),
                           bg=THEME["card_background"], fg=THEME["text_primary"], 
                           width=col["width"]//10, anchor="w")
            header.place(x=x_pos, y=0)
        
        # Cihaz listesi için kaydırılabilir çerçeve
        self.devices_canvas = tk.Canvas(self.devices_card, bg=THEME["card_background"],
                                    highlightthickness=0)
        self.devices_canvas.place(x=20, y=100, right=40, bottom=20)
        
        # Kaydırma çubuğu
        scrollbar = ttk.Scrollbar(self.devices_card, orient="vertical", 
                                command=self.devices_canvas.yview)
        scrollbar.place(relx=1, y=100, bottom=20, anchor="ne", width=20)
        
        self.devices_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Cihaz listesi için iç çerçeve
        self.devices_list_frame = tk.Frame(self.devices_canvas, bg=THEME["card_background"])
        self.devices_canvas.create_window((0, 0), window=self.devices_list_frame, 
                                       anchor="nw", tags="devices_list")
        
        # Cihaz listesi yeniden boyutlandırma
        self.devices_list_frame.bind("<Configure>", self._on_frame_configure)
        self.devices_canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Varsayılan içerik
        self.no_devices_label = tk.Label(self.devices_list_frame, 
                                     text="Henüz tarama yapılmadı", font=("Arial", 14),
                                     bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.no_devices_label.pack(pady=50)
    
    def _on_frame_configure(self, event):
        """İç çerçeve boyutu değiştiğinde kaydırma alanını günceller"""
        self.devices_canvas.configure(scrollregion=self.devices_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Canvas boyutu değiştiğinde iç çerçeveyi yeniden boyutlandırır"""
        # İç çerçevenin genişliğini canvas genişliğine eşitle
        self.devices_canvas.itemconfig("devices_list", width=event.width)
    
    def _start_scan(self):
        """Tarama başlatır"""
        if not self.scan_in_progress:
            if self.app.start_scan():
                self.scan_in_progress = True
                self.scan_button.configure(text="Taranıyor...", state="disabled")
                self.status_label.config(text="Ağ taranıyor...", fg=THEME["info"])
    
    def _toggle_periodic_scan(self):
        """Periyodik taramayı açar/kapatır"""
        # Mevcut durumu kontrol et
        if hasattr(self.app, 'scanner') and hasattr(self.app.scanner, 'periodic_running'):
            if self.app.scanner.periodic_running:
                # Periyodik taramayı durdur
                if self.app.stop_periodic_scan():
                    self.periodic_button.configure(text="Periyodik Tarama", bg=THEME["secondary"])
                    self.periodic_status.config(text="Periyodik tarama: Kapalı")
            else:
                # Periyodik taramayı başlat
                if self.app.start_periodic_scan():
                    self.periodic_button.configure(text="Taramayı Durdur", bg=THEME["warning"])
                    interval = self.app.scanner.scan_interval
                    self.periodic_status.config(text=f"Periyodik tarama: Aktif (Her {interval} saatte bir)")
    
    def _populate_devices_list(self, devices):
        """Cihaz listesini doldurur"""
        # Mevcut içeriği temizle
        for widget in self.devices_list_frame.winfo_children():
            widget.destroy()
        
        if not devices:
            self.no_devices_label = tk.Label(self.devices_list_frame, 
                                        text="Hiç cihaz bulunamadı", font=("Arial", 14),
                                        bg=THEME["card_background"], fg=THEME["text_secondary"])
            self.no_devices_label.pack(pady=50)
            return
        
        # Her cihaz için satır oluştur
        row_height = 40
        columns = [150, 200, 150, 100, 150]  # Sütun genişlikleri
        
        for i, device in enumerate(devices):
            row_frame = tk.Frame(self.devices_list_frame, bg=THEME["card_background"], 
                              height=row_height)
            row_frame.pack(fill=tk.X, pady=2)
            row_frame.pack_propagate(False)
            
            # Alternatif satır renklendirmesi
            if i % 2 == 1:
                row_bg = THEME["background"]
                # Arka plan için canvas kullan
                bg_canvas = tk.Canvas(row_frame, bg=row_bg, highlightthickness=0)
                bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
            
            # IP adresi
            ip_label = tk.Label(row_frame, text=device.get("ip", "Bilinmiyor"), 
                             font=("Arial", 11), bg=row_frame["bg"], fg=THEME["text_primary"],
                             anchor="w", width=columns[0]//10)
            ip_label.place(x=0, y=10)
            
            # MAC adresi
            mac = format_mac_for_display(device.get("mac", "Bilinmiyor"))
            mac_label = tk.Label(row_frame, text=mac, font=("Arial", 11), 
                              bg=row_frame["bg"], fg=THEME["text_primary"],
                              anchor="w", width=columns[1]//10)
            mac_label.place(x=columns[0], y=10)
            
            # Durum (varsayılan ağ geçidi, şüpheli, normal)
            is_gateway = (device.get("ip") == self.app.scanner.get_last_scan_result().get("gateway", {}).get("ip"))
            is_suspicious = any(entry.get("mac") == device.get("mac") 
                               for entry in self.app.scanner.get_last_scan_result().get("suspicious_entries", [])
                               if entry.get("threat_level") in ["high", "medium"])
            
            if is_gateway:
                status_text = "Ağ Geçidi"
                status_color = THEME["info"]
            elif is_suspicious:
                status_text = "Şüpheli"
                status_color = THEME["warning"]
            else:
                status_text = "Normal"
                status_color = THEME["success"]
            
            status_label = tk.Label(row_frame, text=status_text, font=("Arial", 11), 
                                 bg=row_frame["bg"], fg=status_color,
                                 anchor="w", width=columns[2]//10)
            status_label.place(x=columns[0]+columns[1], y=10)
            
            # Arayüz
            interface_label = tk.Label(row_frame, text=device.get("interface", "Bilinmiyor"), 
                                    font=("Arial", 11), bg=row_frame["bg"], 
                                    fg=THEME["text_primary"], anchor="w", width=columns[3]//10)
            interface_label.place(x=columns[0]+columns[1]+columns[2], y=10)
            
            # Son görülme
            last_seen_label = tk.Label(row_frame, text="Az önce", 
                                    font=("Arial", 11), bg=row_frame["bg"], 
                                    fg=THEME["text_secondary"], anchor="w", width=columns[4]//10)
            last_seen_label.place(x=columns[0]+columns[1]+columns[2]+columns[3], y=10)
    
    def _update_status(self, result=None):
        """Tarama durumunu günceller"""
        self.scan_in_progress = False
        self.scan_button.configure(text="Ağı Tara", state="normal")
        
        if not result:
            self.status_label.config(text="Hazır", fg=THEME["text_secondary"])
            return
        
        # Tarama zamanını güncelle
        scan_time = result.get("timestamp", time.time())
        time_ago = format_time_ago(scan_time)
        self.last_scan_label.config(text=f"Son tarama: {time_ago}")
        
        # Tehdit durumuna göre durum etiketini güncelle
        threat_level = result.get("threat_level", "unknown")
        
        if threat_level == "high":
            status_text = "Tehdit tespit edildi!"
            status_color = THEME["error"]
        elif threat_level == "medium":
            status_text = "Olası tehdit tespit edildi"
            status_color = THEME["warning"]
        elif threat_level == "none":
            status_text = "Ağ güvenli görünüyor"
            status_color = THEME["success"]
        else:
            status_text = "Bilinmeyen durum"
            status_color = THEME["text_secondary"]
        
        self.status_label.config(text=status_text, fg=status_color)
        
        # Periyodik tarama durumunu güncelle
        if hasattr(self.app, 'scanner') and hasattr(self.app.scanner, 'periodic_running'):
            if self.app.scanner.periodic_running:
                interval = self.app.scanner.scan_interval
                self.periodic_status.config(text=f"Periyodik tarama: Aktif (Her {interval} saatte bir)")
                self.periodic_button.configure(text="Taramayı Durdur", bg=THEME["warning"])
            else:
                self.periodic_status.config(text="Periyodik tarama: Kapalı")
                self.periodic_button.configure(text="Periyodik Tarama", bg=THEME["secondary"])
    
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        try:
            # Tarama durumunu güncelle
            self._update_status(result)
            
            # Cihaz listesini oluştur
            devices = result.get("arp_table", [])
            self.devices = devices
            self._populate_devices_list(devices)
        except Exception as e:
            logger.error(f"Tarama sonucu işlenirken hata: {e}")
            traceback.print_exc()
            self._update_status(None)
    
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        # En son tarama sonucunu ve durumunu güncelle
        if hasattr(self.app, 'scanner'):
            last_result = self.app.scanner.get_last_scan_result()
            if last_result:
                self.on_scan_completed(last_result)
            else:
                self._update_status(None)

class ThreatAnalysisScreen(BaseScreen):
    """Tehdit analizi ekranı"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        # Tehdit analizi ekranı oluştur
        self._create_widgets()
        self.threats = []  # Tespit edilen tehditler
        
    def _create_widgets(self):
        """Arayüz öğelerini oluşturur"""
        # Ana başlık
        title_frame = tk.Frame(self.frame, bg=THEME["background"], height=60)
        title_frame.pack(fill=tk.X, pady=(20, 0))
        
        title_label = tk.Label(title_frame, text="Tehdit Analizi", font=("Arial", 24, "bold"), 
                            bg=THEME["background"], fg=THEME["text_primary"])
        title_label.pack(side=tk.LEFT, padx=30)
        
        # Tarama butonu
        self.scan_button = SpotifyButton(title_frame, text="Ağı Tara", command=self._start_scan,
                                     width=120, height=36, bg=THEME["primary"])
        self.scan_button.pack(side=tk.RIGHT, padx=30)
        
        # Ana içerik
        content_frame = tk.Frame(self.frame, bg=THEME["background"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tehdit özeti kartı
        self.summary_card = RoundedFrame(content_frame, bg=THEME["card_background"], height=150)
        self.summary_card.pack(fill=tk.X, pady=10)
        
        self.summary_title = tk.Label(self.summary_card, text="Tehdit Özeti", 
                                  font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                                  fg=THEME["text_primary"])
        self.summary_title.place(x=20, y=20)
        
        self.status_label = tk.Label(self.summary_card, text="Tarama yapılmadı", 
                                 font=("Arial", 14), bg=THEME["card_background"], 
                                 fg=THEME["text_secondary"])
        self.status_label.place(x=20, y=50)
        
        self.last_scan_label = tk.Label(self.summary_card, text="Son tarama: Henüz tarama yapılmadı", 
                                    font=("Arial", 12), bg=THEME["card_background"], 
                                    fg=THEME["text_tertiary"])
        self.last_scan_label.place(x=20, y=80)
        
        # Güvenlik durumu rozeti
        self.status_badge = StatusBadge(self.summary_card, text="BİLİNMİYOR", status="unknown", 
                                    width=120, height=30)
        self.status_badge.place(x=400, y=50)
        
        # Tehdit listesi kartı
        self.threats_card = RoundedFrame(content_frame, bg=THEME["card_background"])
        self.threats_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        threats_title = tk.Label(self.threats_card, text="Tespit Edilen Tehditler", 
                              font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                              fg=THEME["text_primary"])
        threats_title.place(x=20, y=20)
        
        # Filtreleme alanı
        filter_frame = tk.Frame(self.threats_card, bg=THEME["card_background"])
        filter_frame.place(x=400, y=20, height=30)
        
        # Filtre butonları
        self.all_filter = tk.Label(filter_frame, text="Tümü", font=("Arial", 12, "bold"),
                               bg=THEME["card_background"], fg=THEME["primary"], cursor="hand2")
        self.all_filter.pack(side=tk.LEFT, padx=10)
        self.all_filter.bind("<Button-1>", lambda e: self._filter_threats("all"))
        
        self.high_filter = tk.Label(filter_frame, text="Yüksek", font=("Arial", 12),
                                bg=THEME["card_background"], fg=THEME["text_secondary"], cursor="hand2")
        self.high_filter.pack(side=tk.LEFT, padx=10)
        self.high_filter.bind("<Button-1>", lambda e: self._filter_threats("high"))
        
        self.medium_filter = tk.Label(filter_frame, text="Orta", font=("Arial", 12),
                                  bg=THEME["card_background"], fg=THEME["text_secondary"], cursor="hand2")
        self.medium_filter.pack(side=tk.LEFT, padx=10)
        self.medium_filter.bind("<Button-1>", lambda e: self._filter_threats("medium"))
        
        self.info_filter = tk.Label(filter_frame, text="Bilgi", font=("Arial", 12),
                                bg=THEME["card_background"], fg=THEME["text_secondary"], cursor="hand2")
        self.info_filter.pack(side=tk.LEFT, padx=10)
        self.info_filter.bind("<Button-1>", lambda e: self._filter_threats("info"))
        
        # Tehditler için kaydırılabilir alan
        self.threats_canvas = tk.Canvas(self.threats_card, bg=THEME["card_background"],
                                    highlightthickness=0)
        self.threats_canvas.place(x=20, y=60, right=40, bottom=20)
        
        # Kaydırma çubuğu
        scrollbar = ttk.Scrollbar(self.threats_card, orient="vertical", 
                               command=self.threats_canvas.yview)
        scrollbar.place(relx=1, y=60, bottom=20, anchor="ne", width=20)
        
        self.threats_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Tehdit listesi için iç çerçeve
        self.threats_list_frame = tk.Frame(self.threats_canvas, bg=THEME["card_background"])
        self.threats_canvas.create_window((0, 0), window=self.threats_list_frame, 
                                      anchor="nw", tags="threats_list")
        
        # Yeniden boyutlandırma
        self.threats_list_frame.bind("<Configure>", lambda e: self.threats_canvas.configure(
            scrollregion=self.threats_canvas.bbox("all")))
        self.threats_canvas.bind("<Configure>", lambda e: self.threats_canvas.itemconfig(
            "threats_list", width=e.width))
        
        # Varsayılan içerik
        self.no_threats_label = tk.Label(self.threats_list_frame, 
                                     text="Henüz tarama yapılmadı", font=("Arial", 14),
                                     bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.no_threats_label.pack(pady=50)
        
        # Aktif filtre
        self.active_filter = "all"
    
    def _start_scan(self):
        """Tarama başlatır"""
        if self.app.start_scan():
            self.scan_button.configure(text="Taranıyor...", state="disabled")
            self.status_label.config(text="Ağ taranıyor...", fg=THEME["info"])
    
    def _filter_threats(self, filter_type):
        """Tehditleri filtrelemek için kullanılır"""
        # Aktif filtreyi güncelle
        self.active_filter = filter_type
        
        # Filtre butonlarının stilini güncelle
        for filter_label, filter_id in [
            (self.all_filter, "all"),
            (self.high_filter, "high"),
            (self.medium_filter, "medium"),
            (self.info_filter, "info")
        ]:
            if filter_id == filter_type:
                filter_label.config(font=("Arial", 12, "bold"), fg=THEME["primary"])
            else:
                filter_label.config(font=("Arial", 12), fg=THEME["text_secondary"])
        
        # Tehditleri yeniden yükle (mevcut filtre ile)
        self._populate_threats_list()
    
    def _create_threat_card(self, parent, threat):
        """Tehdit kartı oluşturur"""
        # Tehdit seviyesini belirle
        threat_level = threat.get("threat_level", "none")
        
        # Filtre durumunu kontrol et
        if self.active_filter != "all":
            if self.active_filter == "info" and not threat.get("type", "").startswith("info_"):
                return None
            elif self.active_filter == "high" and threat_level != "high":
                return None
            elif self.active_filter == "medium" and threat_level != "medium":
                return None
        
        # Kart rengi ve simgesi
        if threat_level == "high":
            icon = "❌"
            color = THEME["error"]
            bg_color = THEME["card_background"]
        elif threat_level == "medium":
            icon = "⚠️"
            color = THEME["warning"]
            bg_color = THEME["card_background"]
        else:
            icon = "📌"
            color = THEME["info"]
            bg_color = THEME["card_background"]
        
        # Kart çerçevesi
        card = tk.Frame(parent, bg=bg_color, padx=10, pady=10, bd=1, relief="solid")
        card.pack(fill=tk.X, pady=5, padx=5)
        
        # Başlık çerçevesi
        header_frame = tk.Frame(card, bg=bg_color)
        header_frame.pack(fill=tk.X)
        
        # İkon ve mesaj
        icon_label = tk.Label(header_frame, text=icon, font=("Arial", 16), 
                           bg=bg_color, fg=color)
        icon_label.pack(side=tk.LEFT)
        
        # Tehdit mesajı
        message = threat.get("message", "Bilinmeyen tehdit")
        message_label = tk.Label(header_frame, text=message, font=("Arial", 12, "bold"), 
                              bg=bg_color, fg=THEME["text_primary"], justify=tk.LEFT,
                              wraplength=600, anchor="w")
        message_label.pack(side=tk.LEFT, padx=10)
        
        # Tehdit detayları
        details_frame = tk.Frame(card, bg=bg_color)
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        # MAC adresi
        if "mac" in threat:
            mac_frame = tk.Frame(details_frame, bg=bg_color)
            mac_frame.pack(fill=tk.X, pady=2)
            
            mac_title = tk.Label(mac_frame, text="MAC:", font=("Arial", 11, "bold"), 
                              bg=bg_color, fg=THEME["text_secondary"], width=10, anchor="w")
            mac_title.pack(side=tk.LEFT)
            
            mac_value = tk.Label(mac_frame, text=format_mac_for_display(threat["mac"]), 
                              font=("Arial", 11), bg=bg_color, fg=THEME["text_primary"])
            mac_value.pack(side=tk.LEFT)
        
        # IP adresi
        if "ip" in threat:
            ip_frame = tk.Frame(details_frame, bg=bg_color)
            ip_frame.pack(fill=tk.X, pady=2)
            
            ip_title = tk.Label(ip_frame, text="IP:", font=("Arial", 11, "bold"), 
                             bg=bg_color, fg=THEME["text_secondary"], width=10, anchor="w")
            ip_title.pack(side=tk.LEFT)
            
            ip_value = tk.Label(ip_frame, text=threat["ip"], font=("Arial", 11), 
                             bg=bg_color, fg=THEME["text_primary"])
            ip_value.pack(side=tk.LEFT)
        
        # Birden fazla IP
        if "ips" in threat:
            ips_frame = tk.Frame(details_frame, bg=bg_color)
            ips_frame.pack(fill=tk.X, pady=2)
            
            ips_title = tk.Label(ips_frame, text="IP'ler:", font=("Arial", 11, "bold"), 
                              bg=bg_color, fg=THEME["text_secondary"], width=10, anchor="w")
            ips_title.pack(side=tk.LEFT)
            
            ips_value = tk.Label(ips_frame, text=", ".join(threat["ips"][:3]) + 
                              ("..." if len(threat["ips"]) > 3 else ""), 
                              font=("Arial", 11), bg=bg_color, fg=THEME["text_primary"])
            ips_value.pack(side=tk.LEFT)
        
        # Birden fazla MAC
        if "macs" in threat:
            macs_frame = tk.Frame(details_frame, bg=bg_color)
            macs_frame.pack(fill=tk.X, pady=2)
            
            macs_title = tk.Label(macs_frame, text="MAC'ler:", font=("Arial", 11, "bold"), 
                               bg=bg_color, fg=THEME["text_secondary"], width=10, anchor="w")
            macs_title.pack(side=tk.LEFT)
            
            formatted_macs = [format_mac_for_display(m) for m in threat["macs"]]
            macs_value = tk.Label(macs_frame, text=", ".join(formatted_macs[:3]) + 
                               ("..." if len(formatted_macs) > 3 else ""), 
                               font=("Arial", 11), bg=bg_color, fg=THEME["text_primary"])
            macs_value.pack(side=tk.LEFT)
        
        # Öneriler
        if threat_level in ["high", "medium"]:
            recom_frame = tk.Frame(card, bg=bg_color)
            recom_frame.pack(fill=tk.X, pady=(10, 0))
            
            recom_title = tk.Label(recom_frame, text="Öneriler:", font=("Arial", 11, "bold"), 
                                bg=bg_color, fg=THEME["text_secondary"])
            recom_title.pack(anchor="w")
            
            if threat_level == "high":
                recom = "Ağ bağlantınızı kesin ve güvenli bir ağa geçin. Router'ınızı yeniden başlatın."
            else:
                recom = "MAC-IP eşleşmelerini kontrol edin. Şüpheli cihazları ağdan çıkartın."
            
            recom_value = tk.Label(recom_frame, text=recom, font=("Arial", 11), 
                                bg=bg_color, fg=THEME["text_primary"],
                                wraplength=600, justify=tk.LEFT)
            recom_value.pack(anchor="w", pady=5)
        
        return card
    
    def _populate_threats_list(self):
        """Tehdit listesini doldurur"""
        # Mevcut içeriği temizle
        for widget in self.threats_list_frame.winfo_children():
            widget.destroy()
        
        if not self.threats:
            self.no_threats_label = tk.Label(self.threats_list_frame, 
                                        text="Hiç tehdit tespit edilmedi", font=("Arial", 14),
                                        bg=THEME["card_background"], fg=THEME["text_secondary"])
            self.no_threats_label.pack(pady=50)
            return
        
        # Tehditleri öncelik sırasına göre sırala
        priority_order = {"high": 0, "medium": 1, "none": 2, "unknown": 3}
        sorted_threats = sorted(self.threats, 
                             key=lambda x: priority_order.get(x.get("threat_level", "unknown"), 4))
        
        # Her tehdit için kart oluştur
        created_cards = 0
        for threat in sorted_threats:
            card = self._create_threat_card(self.threats_list_frame, threat)
            if card:
                created_cards += 1
        
        if created_cards == 0:
            no_results = tk.Label(self.threats_list_frame, 
                               text=f"Seçilen filtreye uygun tehdit bulunamadı", font=("Arial", 14),
                               bg=THEME["card_background"], fg=THEME["text_secondary"])
            no_results.pack(pady=50)
    
    def _update_threat_summary(self, result):
        """Tehdit özetini günceller"""
        # Sonuç olup olmadığını kontrol et
        if not result:
            self.status_label.config(text="Tarama yapılmadı", fg=THEME["text_secondary"])
            self.status_badge.set_status("BİLİNMİYOR", "unknown")
            return
        
        # Tarama zamanını güncelle
        scan_time = result.get("timestamp", time.time())
        time_ago = format_time_ago(scan_time)
        self.last_scan_label.config(text=f"Son tarama: {time_ago}")
        
        # Tehditleri al
        suspicious_entries = result.get("suspicious_entries", [])
        self.threats = suspicious_entries
        
        # Tehdit seviyesi ve sayılarını hesapla
        threat_level = result.get("threat_level", "unknown")
        high_threats = sum(1 for t in suspicious_entries if t.get("threat_level") == "high")
        medium_threats = sum(1 for t in suspicious_entries if t.get("threat_level") == "medium")
        info_entries = sum(1 for t in suspicious_entries if t.get("type", "").startswith("info_"))
        
        # Tehdit seviyesine göre özeti güncelle
        if threat_level == "high":
            status_text = f"{high_threats} Yüksek, {medium_threats} Orta seviye tehdit tespit edildi"
            status_color = THEME["error"]
            badge_text = "TEHLİKE"
            badge_status = "error"
        elif threat_level == "medium":
            status_text = f"{medium_threats} Orta seviye tehdit tespit edildi"
            status_color = THEME["warning"]
            badge_text = "DİKKAT"
            badge_status = "warning"
        elif threat_level == "none":
            status_text = "Herhangi bir tehdit tespit edilmedi"
            status_color = THEME["success"]
            badge_text = "GÜVENLİ"
            badge_status = "success"
        else:
            status_text = "Bilinmeyen durum"
            status_color = THEME["text_secondary"]
            badge_text = "BİLİNMİYOR"
            badge_status = "unknown"
        
        self.status_label.config(text=status_text, fg=status_color)
        self.status_badge.set_status(badge_text, badge_status)
    
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        try:
            # UI güncellemelerini yap
            self.scan_button.configure(text="Ağı Tara", state="normal")
            
            # Tehdit özetini güncelle
            self._update_threat_summary(result)
            
            # Tehdit listesini güncelle
            self._populate_threats_list()
        except Exception as e:
            logger.error(f"Tehdit analizi güncellenirken hata: {e}")
            traceback.print_exc()
    
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        # En son tarama sonucunu ve durumunu güncelle
        if hasattr(self.app, 'scanner'):
            last_result = self.app.scanner.get_last_scan_result()
            if last_result:
                self.on_scan_completed(last_result)

class HistoryScreen(BaseScreen):
    """Geçmiş ekranı"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        # Geçmiş ekranı oluştur
        self._create_widgets()
        
    def _create_widgets(self):
        """Arayüz öğelerini oluşturur"""
        # Ana başlık
        title_frame = tk.Frame(self.frame, bg=THEME["background"], height=60)
        title_frame.pack(fill=tk.X, pady=(20, 0))
        
        title_label = tk.Label(title_frame, text="Tarama Geçmişi", font=("Arial", 24, "bold"), 
                            bg=THEME["background"], fg=THEME["text_primary"])
        title_label.pack(side=tk.LEFT, padx=30)
        
        # Temizle butonu
        self.clear_button = SpotifyButton(title_frame, text="Geçmişi Temizle", 
                                      command=self._clear_history,
                                      width=140, height=36, bg=THEME["secondary"])
        self.clear_button.pack(side=tk.RIGHT, padx=30)
        
        # Ana içerik
        content_frame = tk.Frame(self.frame, bg=THEME["background"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # İstatistikler kartı
        self.stats_card = RoundedFrame(content_frame, bg=THEME["card_background"], height=150)
        self.stats_card.pack(fill=tk.X, pady=10)
        
        stats_title = tk.Label(self.stats_card, text="Özet İstatistikler", 
                            font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                            fg=THEME["text_primary"])
        stats_title.place(x=20, y=20)
        
        # İstatistik göstergeleri
        self.total_scans_label = tk.Label(self.stats_card, text="Toplam Tarama: 0", 
                                      font=("Arial", 14), bg=THEME["card_background"], 
                                      fg=THEME["text_primary"])
        self.total_scans_label.place(x=20, y=60)
        
        self.high_threats_label = tk.Label(self.stats_card, text="Tespit Edilen Yüksek Tehditler: 0", 
                                      font=("Arial", 14), bg=THEME["card_background"], 
                                      fg=THEME["text_primary"])
        self.high_threats_label.place(x=20, y=90)
        
        self.first_scan_label = tk.Label(self.stats_card, text="İlk Tarama: -", 
                                     font=("Arial", 12), bg=THEME["card_background"], 
                                     fg=THEME["text_secondary"])
        self.first_scan_label.place(x=400, y=60)
        
        self.last_scan_label = tk.Label(self.stats_card, text="Son Tarama: -", 
                                    font=("Arial", 12), bg=THEME["card_background"], 
                                    fg=THEME["text_secondary"])
        self.last_scan_label.place(x=400, y=90)
        
        # Geçmiş listesi kartı
        self.history_card = RoundedFrame(content_frame, bg=THEME["card_background"])
        self.history_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        history_title = tk.Label(self.history_card, text="Tarama Geçmişi", 
                              font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                              fg=THEME["text_primary"])
        history_title.place(x=20, y=20)
        
        # Tablo başlık çerçevesi
        header_frame = tk.Frame(self.history_card, bg=THEME["card_background"])
        header_frame.place(x=20, y=60, right=20, height=30)
        
        # Tablo başlıkları
        header_columns = [
            {"text": "Tarih ve Saat", "width": 200},
            {"text": "Tehdit Seviyesi", "width": 150},
            {"text": "Tespit Edilen Tehditler", "width": 200},
            {"text": "Süre", "width": 100},
            {"text": "Ağ Güvenlik Skoru", "width": 150}
        ]
        
        for i, col in enumerate(header_columns):
            x_pos = sum(c["width"] for c in header_columns[:i])
            header = tk.Label(header_frame, text=col["text"], font=("Arial", 12, "bold"),
                           bg=THEME["card_background"], fg=THEME["text_primary"], 
                           width=col["width"]//10, anchor="w")
            header.place(x=x_pos, y=0)
        
        # Geçmiş listesi için kaydırılabilir çerçeve
        self.history_canvas = tk.Canvas(self.history_card, bg=THEME["card_background"],
                                    highlightthickness=0)
        self.history_canvas.place(x=20, y=100, right=40, bottom=20)
        
        # Kaydırma çubuğu
        scrollbar = ttk.Scrollbar(self.history_card, orient="vertical", 
                               command=self.history_canvas.yview)
        scrollbar.place(relx=1, y=100, bottom=20, anchor="ne", width=20)
        
        self.history_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Geçmiş listesi için iç çerçeve
        self.history_list_frame = tk.Frame(self.history_canvas, bg=THEME["card_background"])
        self.history_canvas.create_window((0, 0), window=self.history_list_frame, 
                                      anchor="nw", tags="history_list")
        
        # Yeniden boyutlandırma
        self.history_list_frame.bind("<Configure>", lambda e: self.history_canvas.configure(
            scrollregion=self.history_canvas.bbox("all")))
        self.history_canvas.bind("<Configure>", lambda e: self.history_canvas.itemconfig(
            "history_list", width=e.width))
        
        # Varsayılan içerik
        self.no_history_label = tk.Label(self.history_list_frame, 
                                     text="Henüz tarama geçmişi yok", font=("Arial", 14),
                                     bg=THEME["card_background"], fg=THEME["text_secondary"])
        self.no_history_label.pack(pady=50)
    
    def _clear_history(self):
        """Tarama geçmişini temizler"""
        if not hasattr(self.app, 'scanner') or not self.app.scanner.scan_history:
            return
            
        # Onay sor
        if messagebox.askyesno("Geçmişi Temizle", 
                             "Tüm tarama geçmişi silinecek. Devam etmek istiyor musunuz?"):
            # Geçmişi temizle
            self.app.scanner.scan_history = []
            
            # Arayüzü güncelle
            self._update_history_display()
            self._update_statistics()
    
    def _update_statistics(self):
        """İstatistiksel bilgileri günceller"""
        if not hasattr(self.app, 'scanner'):
            return
            
        scan_history = self.app.scanner.scan_history
        
        # Toplam tarama sayısı
        total_scans = len(scan_history)
        self.total_scans_label.config(text=f"Toplam Tarama: {total_scans}")
        
        # Tespit edilen yüksek tehdit sayısı
        high_threats = 0
        for scan in scan_history:
            high_threats += sum(1 for entry in scan.get("suspicious_entries", []) 
                              if entry.get("threat_level") == "high")
        
        self.high_threats_label.config(text=f"Tespit Edilen Yüksek Tehditler: {high_threats}")
        
        # İlk ve son tarama zamanları
        if scan_history:
            first_scan_time = scan_history[0].get("timestamp", 0)
            last_scan_time = scan_history[-1].get("timestamp", 0)
            
            self.first_scan_label.config(text=f"İlk Tarama: {format_timestamp(first_scan_time)}")
            self.last_scan_label.config(text=f"Son Tarama: {format_timestamp(last_scan_time)}")
        else:
            self.first_scan_label.config(text="İlk Tarama: -")
            self.last_scan_label.config(text="Son Tarama: -")
    
    def _update_history_display(self):
        """Tarama geçmişi görüntüsünü günceller"""
        # Mevcut içeriği temizle
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()
            
        if not hasattr(self.app, 'scanner') or not self.app.scanner.scan_history:
            self.no_history_label = tk.Label(self.history_list_frame, 
                                        text="Henüz tarama geçmişi yok", font=("Arial", 14),
                                        bg=THEME["card_background"], fg=THEME["text_secondary"])
            self.no_history_label.pack(pady=50)
            return
            
        scan_history = self.app.scanner.scan_history
        
        # Taramaları tersine çevir (en yeniden en eskiye)
        reversed_history = list(reversed(scan_history))
        
        # Tablo sütun genişlikleri
        columns = [200, 150, 200, 100, 150]
        row_height = 40
        
        # Her tarama için satır oluştur
        for i, scan in enumerate(reversed_history):
            row_frame = tk.Frame(self.history_list_frame, bg=THEME["card_background"], 
                              height=row_height)
            row_frame.pack(fill=tk.X, pady=2)
            row_frame.pack_propagate(False)
            
            # Alternatif satır renklendirmesi
            if i % 2 == 1:
                row_bg = THEME["background"]
                # Arka plan için canvas kullan
                bg_canvas = tk.Canvas(row_frame, bg=row_bg, highlightthickness=0)
                bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Tarih ve saat
            scan_time = scan.get("timestamp", 0)
            date_label = tk.Label(row_frame, text=format_timestamp(scan_time), 
                               font=("Arial", 11), bg=row_frame["bg"], fg=THEME["text_primary"],
                               anchor="w", width=columns[0]//10)
            date_label.place(x=0, y=10)
            
            # Tehdit seviyesi
            threat_level = scan.get("threat_level", "unknown")
            threat_text = threat_level_to_text(threat_level)
            threat_color = get_status_color(threat_level)
            
            threat_label = tk.Label(row_frame, text=threat_text, font=("Arial", 11), 
                                 bg=row_frame["bg"], fg=threat_color,
                                 anchor="w", width=columns[1]//10)
            threat_label.place(x=columns[0], y=10)
            
            # Tespit edilen tehditler
            suspicious_entries = scan.get("suspicious_entries", [])
            high_threats = sum(1 for entry in suspicious_entries if entry.get("threat_level") == "high")
            medium_threats = sum(1 for entry in suspicious_entries if entry.get("threat_level") == "medium")
            
            threats_text = f"{high_threats} yüksek, {medium_threats} orta seviye"
            threats_label = tk.Label(row_frame, text=threats_text, font=("Arial", 11), 
                                 bg=row_frame["bg"], fg=THEME["text_primary"],
                                 anchor="w", width=columns[2]//10)
            threats_label.place(x=columns[0]+columns[1], y=10)
            
            # Tarama süresi
            duration = scan.get("duration", 0)
            duration_text = f"{duration:.2f} sn"
            duration_label = tk.Label(row_frame, text=duration_text, font=("Arial", 11), 
                                   bg=row_frame["bg"], fg=THEME["text_primary"],
                                   anchor="w", width=columns[3]//10)
            duration_label.place(x=columns[0]+columns[1]+columns[2], y=10)
            
            # Ağ güvenlik skoru
            security_score = get_network_security_score(scan)
            score_text = f"{security_score}/100"
            
            if security_score >= 80:
                score_color = THEME["success"]
            elif security_score >= 50:
                score_color = THEME["warning"]
            else:
                score_color = THEME["error"]
                
            score_label = tk.Label(row_frame, text=score_text, font=("Arial", 11, "bold"), 
                                bg=row_frame["bg"], fg=score_color,
                                anchor="w", width=columns[4]//10)
            score_label.place(x=columns[0]+columns[1]+columns[2]+columns[3], y=10)
    
    def on_scan_completed(self, result):
        """Tarama tamamlandığında çağrılır"""
        # Listeyi güncelle
        self._update_statistics()
        self._update_history_display()
    
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        # İstatistikleri ve listeyi güncelle
        self._update_statistics()
        self._update_history_display()

class SettingsScreen(BaseScreen):
    """Ayarlar ekranı"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        # Ayarlar ekranı oluştur
        self._create_widgets()
        
    def _create_widgets(self):
        """Arayüz öğelerini oluşturur"""
        # Ana başlık
        title_frame = tk.Frame(self.frame, bg=THEME["background"], height=60)
        title_frame.pack(fill=tk.X, pady=(20, 0))
        
        title_label = tk.Label(title_frame, text="Ayarlar", font=("Arial", 24, "bold"), 
                            bg=THEME["background"], fg=THEME["text_primary"])
        title_label.pack(side=tk.LEFT, padx=30)
        
        # Kaydet butonu
        self.save_button = SpotifyButton(title_frame, text="Ayarları Kaydet", 
                                     command=self._save_settings,
                                     width=140, height=36, bg=THEME["primary"])
        self.save_button.pack(side=tk.RIGHT, padx=30)
        
        # Ana içerik
        content_frame = tk.Frame(self.frame, bg=THEME["background"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Genel ayarlar kartı
        self.general_card = RoundedFrame(content_frame, bg=THEME["card_background"], height=250)
        self.general_card.pack(fill=tk.X, pady=10)
        
        general_title = tk.Label(self.general_card, text="Genel Ayarlar", 
                              font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                              fg=THEME["text_primary"])
        general_title.place(x=20, y=20)
        
        # Ayarlar içeriği
        settings_frame = tk.Frame(self.general_card, bg=THEME["card_background"])
        settings_frame.place(x=20, y=60, right=20, height=170)
        
        # Periyodik tarama ayarı
        interval_frame = tk.Frame(settings_frame, bg=THEME["card_background"], height=40)
        interval_frame.pack(fill=tk.X, pady=10)
        
        interval_label = tk.Label(interval_frame, text="Tarama Aralığı:", 
                               font=("Arial", 12), bg=THEME["card_background"], 
                               fg=THEME["text_primary"], width=20, anchor="w")
        interval_label.pack(side=tk.LEFT)
        
        self.interval_var = tk.StringVar()
        self.interval_var.set("24")  # Varsayılan değer
        
        interval_options = ["1", "3", "6", "12", "24", "48"]
        self.interval_dropdown = ttk.Combobox(interval_frame, textvariable=self.interval_var,
                                         values=interval_options, width=10, state="readonly")
        self.interval_dropdown.pack(side=tk.LEFT, padx=10)
        
        interval_unit = tk.Label(interval_frame, text="saat", 
                             font=("Arial", 12), bg=THEME["card_background"], 
                             fg=THEME["text_primary"])
        interval_unit.pack(side=tk.LEFT)
        
        # Otomatik tarama ayarı
        auto_scan_frame = tk.Frame(settings_frame, bg=THEME["card_background"], height=40)
        auto_scan_frame.pack(fill=tk.X, pady=10)
        
        auto_scan_label = tk.Label(auto_scan_frame, text="Başlangıçta Tarama:", 
                                font=("Arial", 12), bg=THEME["card_background"], 
                                fg=THEME["text_primary"], width=20, anchor="w")
        auto_scan_label.pack(side=tk.LEFT)
        
        self.auto_scan_var = tk.BooleanVar()
        self.auto_scan_var.set(True)  # Varsayılan değer
        
        auto_scan_check = ttk.Checkbutton(auto_scan_frame, text="Uygulama başladığında otomatik tarama başlat", 
                                      variable=self.auto_scan_var)
        auto_scan_check.pack(side=tk.LEFT, padx=10)
        
        # Bildirim ayarı
        notifications_frame = tk.Frame(settings_frame, bg=THEME["card_background"], height=40)
        notifications_frame.pack(fill=tk.X, pady=10)
        
        notifications_label = tk.Label(notifications_frame, text="Bildirimler:", 
                                   font=("Arial", 12), bg=THEME["card_background"], 
                                   fg=THEME["text_primary"], width=20, anchor="w")
        notifications_label.pack(side=tk.LEFT)
        
        self.notifications_var = tk.BooleanVar()
        self.notifications_var.set(True)  # Varsayılan değer
        
        notifications_check = ttk.Checkbutton(notifications_frame, text="Tehdit tespit edildiğinde bildirim göster", 
                                         variable=self.notifications_var)
        notifications_check.pack(side=tk.LEFT, padx=10)
        
        # Tema ayarı
        theme_frame = tk.Frame(settings_frame, bg=THEME["card_background"], height=40)
        theme_frame.pack(fill=tk.X, pady=10)
        
        theme_label = tk.Label(theme_frame, text="Tema:", 
                           font=("Arial", 12), bg=THEME["card_background"], 
                           fg=THEME["text_primary"], width=20, anchor="w")
        theme_label.pack(side=tk.LEFT)
        
        self.theme_var = tk.BooleanVar()
        self.theme_var.set(False)  # Varsayılan değer (koyu tema)
        
        theme_check = ttk.Checkbutton(theme_frame, text="Açık tema kullan", 
                                  variable=self.theme_var)
        theme_check.pack(side=tk.LEFT, padx=10)
        
        # Uygulama bilgileri kartı
        self.about_card = RoundedFrame(content_frame, bg=THEME["card_background"], height=250)
        self.about_card.pack(fill=tk.X, pady=10)
        
        about_title = tk.Label(self.about_card, text="Uygulama Hakkında", 
                            font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                            fg=THEME["text_primary"])
        about_title.place(x=20, y=20)
        
        # Uygulama bilgileri
        about_frame = tk.Frame(self.about_card, bg=THEME["card_background"])
        about_frame.place(x=20, y=60, right=20, height=170)
        
        app_name = tk.Label(about_frame, text="NetworkShieldPro", 
                        font=("Arial", 16, "bold"), bg=THEME["card_background"], 
                        fg=THEME["primary"])
        app_name.pack(anchor="w")
        
        app_desc = tk.Label(about_frame, text="ARP Spoofing Tespit ve Koruma Uygulaması", 
                        font=("Arial", 12), bg=THEME["card_background"], 
                        fg=THEME["text_primary"])
        app_desc.pack(anchor="w", pady=5)
        
        app_version = tk.Label(about_frame, text="Sürüm 1.0.0", 
                           font=("Arial", 11), bg=THEME["card_background"], 
                           fg=THEME["text_secondary"])
        app_version.pack(anchor="w", pady=2)
        
        copyright_label = tk.Label(about_frame, text="© 2023 Tüm hakları saklıdır.", 
                               font=("Arial", 11), bg=THEME["card_background"], 
                               fg=THEME["text_secondary"])
        copyright_label.pack(anchor="w", pady=2)
        
        # Sıfırlama butonu
        reset_frame = tk.Frame(about_frame, bg=THEME["card_background"])
        reset_frame.pack(fill=tk.X, pady=20)
        
        reset_button = SpotifyButton(reset_frame, text="Ayarları Sıfırla", 
                                 command=self._reset_settings,
                                 width=140, height=36, bg=THEME["secondary"])
        reset_button.pack(side=tk.LEFT)
    
    def _load_settings(self):
        """Ayarları yükler"""
        try:
            # Tarama aralığı
            scan_interval = get_setting("scan_interval", 24)
            self.interval_var.set(str(scan_interval))
            
            # Otomatik tarama
            auto_scan = get_setting("auto_scan", True)
            self.auto_scan_var.set(auto_scan)
            
            # Bildirimler
            notifications = get_setting("notifications_enabled", True)
            self.notifications_var.set(notifications)
            
            # Tema
            dark_mode = not get_setting("dark_mode", False)
            self.theme_var.set(not dark_mode)  # Koyu tema varsayılan
        except Exception as e:
            logger.error(f"Ayarlar yüklenirken hata: {e}")
            traceback.print_exc()
    
    def _save_settings(self):
        """Ayarları kaydeder"""
        try:
            # Değerleri al
            scan_interval = int(self.interval_var.get())
            auto_scan = self.auto_scan_var.get()
            notifications = self.notifications_var.get()
            dark_mode = not self.theme_var.get()  # Açık tema = Karanlık mod değil
            
            # Ayarları kaydet
            settings = {
                "scan_interval": scan_interval,
                "auto_scan": auto_scan,
                "notifications_enabled": notifications,
                "dark_mode": dark_mode
            }
            
            # Eğer periyodik tarama çalışıyorsa, yeni aralığı uygula
            old_interval = get_setting("scan_interval", 24)
            if hasattr(self.app, "scanner") and self.app.scanner.periodic_running and old_interval != scan_interval:
                self.app.start_periodic_scan(scan_interval)
            
            # Ayarları güncelle
            update_settings(settings)
            
            # Başarı mesajı
            messagebox.showinfo("Başarılı", "Ayarlar başarıyla kaydedildi.")
        except Exception as e:
            logger.error(f"Ayarlar kaydedilirken hata: {e}")
            traceback.print_exc()
            messagebox.showerror("Hata", f"Ayarlar kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def _reset_settings(self):
        """Ayarları sıfırlar"""
        if messagebox.askyesno("Ayarları Sıfırla", 
                           "Tüm ayarlar varsayılan değerlere sıfırlanacak. Devam etmek istiyor musunuz?"):
            try:
                # Ayarları sıfırla
                reset_settings()
                
                # Yeni ayarları yükle
                self._load_settings()
                
                # Başarı mesajı
                messagebox.showinfo("Başarılı", "Ayarlar varsayılan değerlere sıfırlandı.")
            except Exception as e:
                logger.error(f"Ayarlar sıfırlanırken hata: {e}")
                traceback.print_exc()
                messagebox.showerror("Hata", f"Ayarlar sıfırlanırken bir hata oluştu:\n{str(e)}")
    
    def on_show(self):
        """Ekran gösterildiğinde çağrılır"""
        # Ayarları yükle
        self._load_settings()

class SpotifyARPApp:
    """Ana uygulama sınıfı"""
    def __init__(self, root):
        try:
            logger.info("SpotifyARPApp.__init__ başlatılıyor...")
            self.root = root
        
            try:
                logger.debug("Background ayarlanıyor...")
                self.root.configure(bg=THEME["background"])
                logger.debug("Background ayarlandı")
            except Exception as e:
                logger.error(f"Background ayarlanırken hata: {e}")
                traceback.print_exc()
        
            # ARP tarayıcısını başlat
            try:
                logger.debug("ARPScanner oluşturuluyor...")
                self.scanner = ARPScanner(callback=self.on_scan_completed)
                logger.debug("ARPScanner başarıyla oluşturuldu.")
            except Exception as e:
                logger.error(f"ARPScanner oluşturulurken hata: {e}")
                traceback.print_exc()
        
            # Ekran değişkenlerini ayarla
            self.current_screen = None
            self.screens = {}
          
            # Animasyon değişkenleri
            self.particle_animation = None
        
            try:
                logger.debug("Ana düzen oluşturuluyor...")
                self._create_layout()
                logger.debug("Ana düzen oluşturuldu.")
            except Exception as e:
               logger.error(f"Ana düzen oluşturulurken hata: {e}")
               traceback.print_exc()
        
            try:
                logger.debug("Ekranlar oluşturuluyor...")
                self._create_screens()
                logger.debug("Ekranlar oluşturuldu.")
            except Exception as e:
                logger.error(f"Ekranlar oluşturulurken hata: {e}")
                traceback.print_exc()
        
            try:
                logger.debug("Başlangıç ekranı gösteriliyor...")
                self.show_screen("dashboard")
                logger.debug("Başlangıç ekranı gösterildi.")
            except Exception as e:
                logger.error(f"Başlangıç ekranı gösterilirken hata: {e}")
                traceback.print_exc()
        
            try:
                logger.debug("Arka plan animasyonu başlatılıyor...")
                self._start_background_animation()
                logger.debug("Arka plan animasyonu başlatıldı.")
            except Exception as e:
                logger.error(f"Arka plan animasyonu başlatılırken hata: {e}")
                traceback.print_exc()
        
            # Pencere boyut değişikliğini işle
            self.root.bind("<Configure>", self._on_window_resize)
        
            # İlk taramayı başlat
            self.root.after(500, self.scanner.start_scan)
        
            logger.info("SpotifyARPApp.__init__ tamamlandı")
        except Exception as e:
            logger.critical(f"SpotifyARPApp.__init__ içinde kritik hata: {e}")
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
        
        app_title = tk.Label(logo_frame, text="NetworkShieldPro", font=("Arial", 16, "bold"), 
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
            width = self.content_frame.winfo_width()
            height = self.content_frame.winfo_height()
            if width > 1 and height > 1:  # Geçerli boyutlar için kontrol
                self.background_canvas.resize(width, height)
    
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
                logger.info(f"Periyodik tarama başlatıldı - Her {self.scanner.scan_interval} saatte bir")
                self.update_status_label(f"Periyodik tarama aktif: Her {self.scanner.scan_interval} saatte bir")
            return result
        return False

    def stop_periodic_scan(self):
        """Periyodik taramayı durdurur"""
        if hasattr(self, 'scanner'):
            result = self.scanner.stop_periodic_scan()
            if result:
                logger.info("Periyodik tarama durduruldu")
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
        
        # Bildirimler açıksa uyarı göster
        if get_setting("notifications_enabled", True):
            messagebox.showwarning("Güvenlik Tehdidi Tespit Edildi", message)
