#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Yardımcı fonksiyonlar ve işlevler
Bu modül, UI oluşturma ve veri işleme için yardımcı fonksiyonlar içerir.
"""

import time
import math
from datetime import datetime
from ui.colors import THEME, get_status_color

def format_timestamp(timestamp):
    """Zaman damgasını insan-okunabilir formata çevirir"""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%d.%m.%Y %H:%M:%S")

def format_time_ago(timestamp):
    """Bir zaman damgasından bu yana geçen süreyi insan-okunabilir formata çevirir"""
    now = time.time()
    diff = now - timestamp
    
    if diff < 60:
        return "Az önce"
    elif diff < 3600:
        minutes = int(diff / 60)
        return f"{minutes} dakika önce"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours} saat önce"
    elif diff < 604800:
        days = int(diff / 86400)
        return f"{days} gün önce"
    else:
        return format_timestamp(timestamp)

def truncate_text(text, max_length=30):
    """Uzun metinleri kısaltır"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_mac_for_display(mac_address):
    """MAC adresini görüntüleme için formatlar"""
    if not mac_address:
        return "Bilinmiyor"
    
    # Tüm harfleri büyüt ve standart formata getir
    formatted = mac_address.lower().replace("-", ":").strip()
    
    # 6 grup halinde 2'şer karakterlik hexler halinde göster
    parts = formatted.split(":")
    if len(parts) == 6:
        return ":".join(parts)
    
    # Format doğru değilse orijinali döndür
    return mac_address

def format_ip_for_display(ip_address):
    """IP adresini görüntüleme için formatlar"""
    if not ip_address or ip_address == "Bilinmiyor":
        return "Bilinmiyor"
    
    # Basit kontrol: IPv4 formatı
    parts = ip_address.split(".")
    if len(parts) == 4:
        try:
            # Tüm parçaların 0-255 arasında olduğunu kontrol et
            if all(0 <= int(p) <= 255 for p in parts):
                return ip_address
        except ValueError:
            pass
    
    # Format doğru değilse orijinali döndür
    return ip_address

def threat_level_to_text(threat_level):
    """Tehdit seviyesini insan-okunabilir metne çevirir"""
    if threat_level == "high":
        return "Yüksek Tehlike"
    elif threat_level == "medium":
        return "Orta Seviye Tehlike"
    elif threat_level == "none":
        return "Güvenli"
    else:
        return "Bilinmiyor"

def create_threat_data_chart(scan_results):
    """Son tarama sonuçlarını grafik verisi formatına dönüştürür"""
    if not scan_results:
        return []
    
    # Tehdit seviyelerine göre sayımları topla
    threat_counts = {"high": 0, "medium": 0, "none": 0, "unknown": 0}
    
    for result in scan_results:
        threat_level = result.get("threat_level", "unknown")
        threat_counts[threat_level] += 1
    
    # Grafik verisi formatına çevir
    chart_data = [
        ("Yüksek", threat_counts["high"], THEME["error"]),
        ("Orta", threat_counts["medium"], THEME["warning"]),
        ("Güvenli", threat_counts["none"], THEME["success"]),
    ]
    
    return chart_data

def create_scan_history_chart(scan_history):
    """Tarama geçmişini grafik verisi formatına dönüştürür"""
    if not scan_history:
        return []
    
    # Son 5 tarama sonucunu kullan (en yeniden en eskiye)
    last_scans = scan_history[-5:]
    last_scans.reverse()  # En eski -> en yeni sırasına çevir
    
    # Her tarama için tehdit sayılarını hesapla
    scan_data = []
    
    for i, scan in enumerate(last_scans):
        # Şüpheli girdileri tehdit seviyesine göre say
        high_threats = sum(1 for entry in scan.get("suspicious_entries", []) 
                         if entry.get("threat_level") == "high")
        
        # Sıra numarasını etiket olarak kullan
        scan_data.append((f"{i+1}", high_threats, THEME["error"]))
    
    return scan_data

def get_network_security_score(scan_result):
    """Tarama sonucuna göre ağ güvenlik skoru hesaplar (0-100)"""
    if not scan_result:
        return 0
    
    # Tehdit seviyesine göre başlangıç puanı
    threat_level = scan_result.get("threat_level", "unknown")
    
    if threat_level == "high":
        base_score = 20  # Yüksek tehdit varsa düşük başla
    elif threat_level == "medium":
        base_score = 60  # Orta tehdit varsa orta başla
    elif threat_level == "none":
        base_score = 100  # Tehdit yoksa tam puan
    else:
        base_score = 50  # Bilinmiyorsa orta puan
    
    # Şüpheli öğe sayısına göre düzeltme yap
    suspicious_entries = scan_result.get("suspicious_entries", [])
    
    # Gerçek tehditleri filtrele (bilgi öğelerini çıkar)
    real_threats = [entry for entry in suspicious_entries 
                   if not entry.get("type", "").startswith("info_")]
    
    # Her gerçek tehdit için puandan düş
    penalty_per_threat = 5
    threat_penalty = min(len(real_threats) * penalty_per_threat, 40)  # En fazla 40 puan düş
    
    # Varsayılan ağ geçidi durumunu kontrol et
    gateway = scan_result.get("gateway", {})
    if gateway.get("ip") == "Bilinmiyor" or gateway.get("mac") == "Bilinmiyor":
        # Ağ geçidi bulunamadıysa ek ceza
        gateway_penalty = 10
    else:
        gateway_penalty = 0
    
    # Son skoru hesapla
    final_score = max(0, base_score - threat_penalty - gateway_penalty)
    
    return round(final_score)
