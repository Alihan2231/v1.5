#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ARP Spoofing Tespit Modülü
Bu modül, ağda ARP spoofing tespit etmek için gerekli tüm fonksiyonları içerir.
"""

import sys
import subprocess
import socket
import struct
import time
import subprocess
import re
import os
import threading
from collections import defaultdict

# MAC adreslerini düzgün formatta gösterme
def format_mac(mac_bytes):
    """Binary MAC adresini okunabilir formata çevirir."""
    if isinstance(mac_bytes, bytes):
        return ':'.join(f'{b:02x}' for b in mac_bytes)
    return mac_bytes

# IP adreslerini düzgün formatta gösterme
def format_ip(ip_bytes):
    """Binary IP adresini okunabilir formata çevirir."""
    if isinstance(ip_bytes, bytes):
        return socket.inet_ntoa(ip_bytes)
    return ip_bytes

# ARP tablosunu alma
def get_arp_table():
    """
    Sistemin ARP tablosunu alır.
    
    Returns:
        list: ARP tablosundaki kayıtlar listesi
    """
    arp_entries = []
    
    try:
        # Platforma göre uygun komutu belirle
        if os.name == 'nt':  # Windows
            # Windows'ta arp komutunu çalıştır
            output = subprocess.check_output(['arp', '-a'], text=True)
            # Windows ARP çıktısını ayrıştır
            pattern = r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f-]+)\s+(\w+)'
            for line in output.split('\n'):
                match = re.search(pattern, line)
                if match:
                    ip, mac, interface_type = match.groups()
                    mac = mac.replace('-', ':')  # Standart formata çevir
                    arp_entries.append({"ip": ip, "mac": mac, "interface": interface_type})
        else:  # Linux/Unix
            # Linux'ta arp komutunu çalıştır
            output = subprocess.check_output(['arp', '-n'], text=True)
            # Linux ARP çıktısını ayrıştır
            for line in output.split('\n')[1:]:  # Başlık satırını atla
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        ip = parts[0]
                        mac = parts[2]
                        interface = parts[-1] if len(parts) > 3 else "unknown"
                        if mac != "(incomplete)":  # Eksik kayıtları atla
                            arp_entries.append({"ip": ip, "mac": mac, "interface": interface})
        
        return arp_entries
        
    except Exception as e:
        print(f"ARP tablosu alınırken hata oluştu: {e}")
        print("Test verileri kullanılıyor.")
        
        # Normal ve şüpheli durumları içeren test verileri oluştur
        test_entries = [
            {"ip": "192.168.1.1", "mac": "aa:bb:cc:dd:ee:ff", "interface": "eth0"},  # Ağ geçidi
            {"ip": "192.168.1.2", "mac": "11:22:33:44:55:66", "interface": "eth0"},  # Normal cihaz
            {"ip": "192.168.1.3", "mac": "aa:bb:cc:dd:ee:ff", "interface": "eth0"},  # Şüpheli (ağ geçidi MAC'i ile aynı)
            {"ip": "192.168.1.4", "mac": "22:33:44:55:66:77", "interface": "eth0"},  # Normal cihaz
            {"ip": "192.168.1.5", "mac": "33:22:55:66:77:88", "interface": "eth0"},  # Normal cihaz 
            {"ip": "192.168.1.6", "mac": "aa:bb:cc:11:22:33", "interface": "eth0"},  # Normal cihaz
            {"ip": "192.168.1.7", "mac": "aa:bb:cc:11:22:33", "interface": "eth0"},  # Normal IP eşlemesi (aynı cihazın 2 IP'si)
            {"ip": "192.168.1.8", "mac": "ff:ff:ff:ff:ff:ff", "interface": "eth0"},  # Broadcast MAC
            {"ip": "192.168.1.10", "mac": "11:22:33:44:55:66", "interface": "eth0"}, # IP çakışması (aynı MAC farklı IP)
            {"ip": "192.168.1.100", "mac": "de:ad:be:ef:12:34", "interface": "eth0"} # Normal cihaz
        ]
        
        return test_entries

# Varsayılan ağ geçidini bulma
def get_default_gateway():
    """
    Varsayılan ağ geçidini (default gateway) bulur.
    
    Returns:
        dict: Ağ geçidi IP ve MAC adresi
    """
    try:
        if sys.platform == 'win32':
            # Windows üzerinde çalışılıyorsa
            result = subprocess.check_output('ipconfig', encoding='cp1254', errors='replace')
            lines = result.splitlines()
            gateway_ip = None
            
            for i, line in enumerate(lines):
                if "Varsayılan Ağ Geçidi" in line or "Default Gateway" in line:
                    # Türkçe veya İngilizce arayüzler için kontrol
                    parts = line.split(":")
                    if len(parts) > 1:
                        gateway_ip = parts[1].strip()
                        break
            
            if gateway_ip:
                # Gateway IP bulundu, şimdi MAC adresini bulalım
                try:
                    arp_result = subprocess.check_output(f'arp -a {gateway_ip}', encoding='cp1254', errors='replace', shell=True)
                    arp_lines = arp_result.splitlines()
                    
                    for line in arp_lines:
                        if gateway_ip in line:
                            # MAC adresi genellikle ikinci sütundadır
                            parts = line.split()
                            if len(parts) >= 2:
                                gateway_mac = parts[1].replace('-', ':')
                                return {"ip": gateway_ip, "mac": gateway_mac}
                except Exception as e:
                    print(f"ARP tablosunda gateway MAC adresi aranırken hata: {e}")
                    
                # MAC bulunamadıysa sadece IP ile devam et
                return {"ip": gateway_ip, "mac": "00:00:00:00:00:00"}
        else:
            # Linux üzerinde çalışılıyorsa
            result = subprocess.check_output('ip route show default', shell=True, encoding='utf-8')
            gateway_ip = result.split('default via ')[1].split(' ')[0]
            
            # MAC adresini bul
            result = subprocess.check_output(f'ip neigh show {gateway_ip}', shell=True, encoding='utf-8')
            gateway_mac = result.split('lladdr ')[1].split(' ')[0]
            
            return {"ip": gateway_ip, "mac": gateway_mac}
            
    except Exception as e:
        print(f"Varsayılan ağ geçidi bulunurken hata oluştu: {e}")
        
    # Hata durumunda test verisi dön
    print("Test ağ geçidi verisi kullanılıyor.")
    return {"ip": "192.168.1.1", "mac": "aa:bb:cc:dd:ee:ff"}

# ARP spoofing tespiti
def detect_arp_spoofing(arp_table):
    """
    ARP tablosunu inceleyerek olası ARP spoofing saldırılarını tespit eder.
    
    Args:
        arp_table (list): ARP tablosu kayıtları
        
    Returns:
        list: Tespit edilen şüpheli durumlar
    """
    suspicious_entries = []
    mac_to_ips = defaultdict(list)
    
    # Her MAC adresine bağlı IP'leri topla
    for entry in arp_table:
        mac = entry["mac"].lower()  # Büyük/küçük harf duyarlılığını kaldır
        ip = entry["ip"]
        
        # Broadcast MAC adresini atla (normal bir ağ özelliği, saldırı değil)
        if mac == "ff:ff:ff:ff:ff:ff":
            continue
            
        # Multicast MAC adresini atla (normal bir ağ özelliği, saldırı değil)
        if mac.startswith(("01:", "03:", "05:", "07:", "09:", "0b:", "0d:", "0f:")):
            continue
            
        mac_to_ips[mac].append(ip)
    
    # Bir MAC'in birden fazla IP'si varsa (1'den çok cihaz olabilir)
    for mac, ips in mac_to_ips.items():
        if len(ips) > 1:
            suspicious_entries.append({
                "type": "multiple_ips",
                "mac": mac,
                "ips": ips,
                "threat_level": "medium",
                "message": f"⚠️ Şüpheli: {mac} MAC adresine sahip {len(ips)} farklı IP adresi var: {', '.join(ips)}"
            })
    
    # Ağ geçidinin MAC adresi değişmiş mi kontrol et
    gateway = get_default_gateway()
    if gateway["ip"] != "Bilinmiyor" and gateway["mac"] != "Bilinmiyor":
        gateway_entries = [entry for entry in arp_table if entry["ip"] == gateway["ip"]]
        if len(gateway_entries) > 0:
            if len(gateway_entries) > 1:
                suspicious_entries.append({
                    "type": "gateway_multiple_macs",
                    "ip": gateway["ip"],
                    "macs": [entry["mac"] for entry in gateway_entries],
                    "threat_level": "high",
                    "message": f"❌ TEHLİKE: Ağ geçidi {gateway['ip']} için birden fazla MAC adresi var!"
                })
    
    # Bilgi amaçlı özel MAC adreslerini ekle (saldırı değil)
    info_entries = []
    for entry in arp_table:
        mac = entry["mac"].lower()
        # Broadcast MAC (ff:ff:ff:ff:ff:ff)
        if mac == "ff:ff:ff:ff:ff:ff":
            info_entries.append({
                "type": "info_broadcast",
                "ip": entry["ip"],
                "mac": mac,
                "threat_level": "none",
                "message": f"📌 Bilgi: Broadcast MAC adresi: IP={entry['ip']}, MAC={mac}"
            })
        # Multicast MAC (ilk byte'ın en düşük biti 1)
        elif mac.startswith(("01:", "03:", "05:", "07:", "09:", "0b:", "0d:", "0f:")):
            info_entries.append({
                "type": "info_multicast",
                "ip": entry["ip"],
                "mac": mac,
                "threat_level": "none",
                "message": f"📌 Bilgi: Multicast MAC adresi: IP={entry['ip']}, MAC={mac}"
            })
    
    # Bilgi amaçlı girdileri listeye ekle (şüpheli durumlar listesinin sonuna)
    for entry in info_entries:
        suspicious_entries.append(entry)
    
    return suspicious_entries

from modules.settings import load_settings, save_settings, get_setting, set_setting, update_settings

class ARPScanner:
    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.scan_thread = None
        self.periodic_running = False
        self.periodic_thread = None
        
        # Ayarlardan tarama aralığını yüklemeyi dene
        try:
            from modules.settings import get_setting
            saved_interval = get_setting("scan_interval", 24)
            self.scan_interval = saved_interval
            print(f"Kaydedilmiş tarama aralığı yüklendi: {saved_interval} saat")
        except Exception as e:
            print(f"Ayarlar yüklenirken hata, varsayılan değer kullanılıyor: {e}")
            self.scan_interval = 24  # saat
        
        self.scan_history = []  # Tarama geçmişi
        self.stop_event = threading.Event()  # Durdurma sinyali için
        
        # Önceki oturumdan periyodik tarama durumunu yüklemeyi dene
        try:
            from modules.settings import get_setting
            if get_setting("periodic_scan_active", False):
                print("Önceki oturumdan periyodik tarama aktif ayarı bulundu.")
                # Bu direkt olarak başlatma işlemi değil, sadece bir log
        except Exception as e:
            print(f"Periyodik tarama durumu yüklenirken hata: {e}")
    
    def start_scan(self):
        """Tek seferlik tarama başlatır"""
        self.running = True
        if self.scan_thread and self.scan_thread.is_alive():
            return False
        
        self.scan_thread = threading.Thread(target=self._scan_thread, daemon=True)
        self.scan_thread.start()
        return True
    
    def start_periodic_scan(self, interval_hours=None):
        """Periyodik tarama başlatır"""
        if interval_hours:
            self.scan_interval = interval_hours
            
            # Tarama aralığını ayarlara kaydet
            try:
                from modules.settings import set_setting
                set_setting("scan_interval", interval_hours)
                print(f"Tarama aralığı kaydedildi: {interval_hours} saat")
            except Exception as e:
                print(f"Tarama aralığı kaydedilirken hata: {e}")
        
        if self.periodic_running:
            return False
        
        self.periodic_running = True
        self.stop_event.clear()  # Durdurma sinyalini temizle
        
        # Periyodik tarama durumunu ayarlara kaydet
        try:
            from modules.settings import set_setting
            set_setting("periodic_scan_active", True)
            print("Periyodik tarama durumu kaydedildi (aktif)")
        except Exception as e:
            print(f"Periyodik tarama durumu kaydedilirken hata: {e}")
        
        self.periodic_thread = threading.Thread(target=self._periodic_thread, daemon=True)
        self.periodic_thread.start()
        return True
    
    def stop_periodic_scan(self):
        """Periyodik taramayı durdurur"""
        if not self.periodic_running:
            return False  # Zaten aktif değil
        
        self.periodic_running = False
        self.stop_event.set()  # Thread'e durma sinyali gönder
        
        # Periyodik tarama durumunu ayarlara kaydet
        try:
            from modules.settings import set_setting
            set_setting("periodic_scan_active", False)
            print("Periyodik tarama durumu kaydedildi (kapalı)")
        except Exception as e:
            print(f"Periyodik tarama durumu kaydedilirken hata: {e}")
        
        if self.periodic_thread and self.periodic_thread.is_alive():
            self.periodic_thread.join(timeout=1.0)  # Thread'in durmasını bekle (max 1 saniye)
        
        return True
    
    def _scan_thread(self):
        """Arka planda tarama yapar"""
        try:
            # ARP tablosunu al
            arp_table = get_arp_table()
            
            # Varsayılan ağ geçidini bul
            gateway = get_default_gateway()
            
            # ARP spoofing tespiti
            suspicious_entries = detect_arp_spoofing(arp_table)
            
            # Tehlike seviyesini belirle
            threat_level = "none"
            for entry in suspicious_entries:
                # Sadece bilgi değil gerçek şüpheli durumlar
                if entry.get("threat_level") == "high":
                    threat_level = "high"
                    break
                elif entry.get("threat_level") == "medium" and threat_level != "high":
                    threat_level = "medium"
            
            # Sonuçları oluştur
            result = {
                "timestamp": time.time(),
                "arp_table": arp_table,
                "gateway": gateway,
                "suspicious_entries": suspicious_entries,
                "threat_level": threat_level
            }
            
            # Tarama geçmişine ekle (en fazla 100 kayıt tut)
            self.scan_history.append(result)
            if len(self.scan_history) > 100:
                self.scan_history = self.scan_history[-100:]
            
            # Callback fonksiyonu çağır
            if self.callback:
                self.callback(result)
            
            self.running = False
            return result
            
        except Exception as e:
            error_result = {
                "timestamp": time.time(),
                "error": str(e),
                "threat_level": "unknown"
            }
            if self.callback:
                self.callback(error_result)
            
            self.running = False
            return error_result
    
    def _periodic_thread(self):
        """Periyodik tarama arka plan thread'i"""
        while self.periodic_running:
            # Tarama başlat
            self._scan_thread()
            
            # Seçilen saat değerine göre saniye hesapla
            interval_seconds = self.scan_interval * 3600  # Saat başına 3600 saniye
            
            # Bekleme döngüsü (her 10 saniyede bir durdurma sinyalini kontrol eder)
            for _ in range(int(interval_seconds / 10)):
                if self.stop_event.wait(10):  # 10 saniye bekle veya sinyal gelirse çık
                    return  # Döngüden çık ve thread'i sonlandır
                if not self.periodic_running:
                    return