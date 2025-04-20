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
import re
import os
import threading
import logging
from collections import defaultdict

# Loglama
logger = logging.getLogger("V-ARP.arp_detector")

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
        
        logger.debug(f"ARP tablosu alındı: {len(arp_entries)} kayıt")
        return arp_entries
        
    except Exception as e:
        logger.error(f"ARP tablosu alınırken hata oluştu: {e}")
        logger.warning("Test verileri kullanılıyor.")
        
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
                                logger.debug(f"Gateway bulundu: IP={gateway_ip}, MAC={gateway_mac}")
                                return {"ip": gateway_ip, "mac": gateway_mac}
                except Exception as e:
                    logger.error(f"ARP tablosunda gateway MAC adresi aranırken hata: {e}")
                    
                # MAC bulunamadıysa sadece IP ile devam et
                logger.warning(f"Gateway MAC adresi bulunamadı, sadece IP kullanılıyor: {gateway_ip}")
                return {"ip": gateway_ip, "mac": "Bilinmiyor"}
            else:
                logger.warning("Gateway IP adresi bulunamadı")
                return {"ip": "Bilinmiyor", "mac": "Bilinmiyor"}
        else:
            # Linux üzerinde çalışılıyorsa
            try:
                result = subprocess.check_output('ip route show default', shell=True, encoding='utf-8')
                gateway_ip = result.split('default via ')[1].split(' ')[0]
                
                # MAC adresini bul
                result = subprocess.check_output(f'ip neigh show {gateway_ip}', shell=True, encoding='utf-8')
                gateway_mac = result.split('lladdr ')[1].split(' ')[0]
                
                logger.debug(f"Gateway bulundu: IP={gateway_ip}, MAC={gateway_mac}")
                return {"ip": gateway_ip, "mac": gateway_mac}
            except Exception as e:
                logger.error(f"Linux'ta gateway bilgisi alınırken hata: {e}")
                return {"ip": "Bilinmiyor", "mac": "Bilinmiyor"}
            
    except Exception as e:
        logger.error(f"Varsayılan ağ geçidi bulunurken hata oluştu: {e}")
        
    # Hata durumunda test verisi dön
    logger.warning("Test ağ geçidi verisi kullanılıyor.")
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

class ARPScanner:
    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.scan_thread = None
        self.periodic_running = False
        self.periodic_thread = None
        
        # Loglama
        self.logger = logging.getLogger("V-ARP.ARPScanner")
        
        # Ayarlardan tarama aralığını yüklemeyi dene
        try:
            from modules.settings import get_setting
            saved_interval = get_setting("scan_interval", 24)
            self.scan_interval = saved_interval
            self.logger.info(f"Kaydedilmiş tarama aralığı yüklendi: {saved_interval} saat")
        except Exception as e:
            self.logger.error(f"Ayarlar yüklenirken hata, varsayılan değer kullanılıyor: {e}")
            self.scan_interval = 24  # saat
        
        self.scan_history = []  # Tarama geçmişi
        self.stop_event = threading.Event()  # Durdurma sinyali için
        
        # Önceki oturumdan periyodik tarama durumunu yüklemeyi dene
        try:
            from modules.settings import get_setting
            if get_setting("periodic_scan_active", False):
                self.logger.info("Önceki oturumdan periyodik tarama aktif ayarı bulundu.")
        except Exception as e:
            self.logger.error(f"Periyodik tarama durumu yüklenirken hata: {e}")
    
    def start_scan(self):
        """Tek seferlik tarama başlatır"""
        if self.running:
            self.logger.warning("Tarama zaten çalışıyor")
            return False
        
        self.running = True
        self.stop_event.clear()  # Durdurma sinyalini temizle
        
        # Tarama işlemini ayrı bir thread'de başlat
        # daemon=False olarak ayarla ki uygulama kapanırken thread'i öldürmesin
        # böylece tarama sağlıklı şekilde tamamlanabilir
        self.scan_thread = threading.Thread(target=self._scan_thread, daemon=False)
        self.scan_thread.start()
        
        self.logger.info("Tarama başlatıldı")
        return True
    
    def start_periodic_scan(self, interval_hours=None):
        """Periyodik tarama başlatır"""
        # Eğer periyodik tarama zaten çalışıyorsa ve interval değişmişse, önce durdur
        if self.periodic_running and interval_hours is not None and self.scan_interval != interval_hours:
            self.logger.info(f"Periyodik tarama aralığı değişti: {self.scan_interval} -> {interval_hours} saat. Tarama yeniden başlatılıyor.")
            self.stop_periodic_scan()
        
        if interval_hours is not None:
            self.scan_interval = interval_hours
            
            # Tarama aralığını ayarlara kaydet
            try:
                from modules.settings import set_setting
                set_setting("scan_interval", interval_hours)
                self.logger.info(f"Tarama aralığı kaydedildi: {interval_hours} saat")
            except Exception as e:
                self.logger.error(f"Tarama aralığı kaydedilirken hata: {e}")
        
        if self.periodic_running:
            self.logger.info(f"Periyodik tarama zaten çalışıyor (Aralık: {self.scan_interval} saat)")
            return True
        
        self.periodic_running = True
        self.stop_event.clear()  # Durdurma sinyalini temizle
        
        # Periyodik tarama durumunu ayarlara kaydet
        try:
            from modules.settings import set_setting
            set_setting("periodic_scan_active", True)
            self.logger.info("Periyodik tarama durumu kaydedildi (aktif)")
        except Exception as e:
            self.logger.error(f"Periyodik tarama durumu kaydedilirken hata: {e}")
        
        # Periyodik taramayı ayrı bir thread'de başlat
        # daemon=False olarak ayarla ki uygulama kapanırken thread'i öldürmesin
        self.periodic_thread = threading.Thread(target=self._periodic_scan_thread, daemon=False)
        self.periodic_thread.start()
        
        self.logger.info(f"Periyodik tarama başlatıldı (Her {self.scan_interval} saatte bir)")
        return True
    
    def stop_periodic_scan(self):
        """Periyodik taramayı durdurur"""
        if not self.periodic_running:
            self.logger.warning("Periyodik tarama zaten çalışmıyor")
            return False
        
        self.periodic_running = False
        self.stop_event.set()  # Durdurma sinyali gönder
        
        # Periyodik tarama durumunu ayarlara kaydet
        try:
            from modules.settings import set_setting
            set_setting("periodic_scan_active", False)
            self.logger.info("Periyodik tarama durumu kaydedildi (pasif)")
        except Exception as e:
            self.logger.error(f"Periyodik tarama durumu kaydedilirken hata: {e}")
        
        # Thread halen çalışıyorsa sonlanmasını bekle
        if self.periodic_thread and self.periodic_thread.is_alive():
            self.logger.info("Periyodik tarama thread'i sonlanana kadar bekleniyor...")
            # Thread'i uygun şekilde sonlana kadar bekle (timeout ile)
            self.periodic_thread.join(timeout=2.0)
            
            if self.periodic_thread.is_alive():
                self.logger.warning("Periyodik tarama thread'i sonlanmadı, devam ediliyor")
            else:
                self.logger.info("Periyodik tarama thread'i başarıyla sonlandı")
        
        self.logger.info("Periyodik tarama durduruldu")
        return True
    
    def stop(self):
        """Tüm tarama işlemlerini durdurur"""
        # Periyodik taramayı durdur
        if self.periodic_running:
            self.stop_periodic_scan()
        
        # Tek seferlik taramayı durdur
        if self.running:
            self.running = False
            self.stop_event.set()  # Durdurma sinyali gönder
            
            # Thread halen çalışıyorsa sonlanmasını bekle
            if self.scan_thread and self.scan_thread.is_alive():
                self.logger.info("Tarama thread'i sonlanana kadar bekleniyor...")
                self.scan_thread.join(timeout=1.0)
                
                if self.scan_thread.is_alive():
                    self.logger.warning("Tarama thread'i sonlanmadı, devam ediliyor")
                else:
                    self.logger.info("Tarama thread'i başarıyla sonlandı")
        
        self.logger.info("Tüm tarama işlemleri durduruldu")
    
    def _scan_thread(self):
        """Tarama işlemini gerçekleştiren thread"""
        try:
            self.logger.info("Tarama başlıyor...")
            
            # Tarama başlangıç zamanı
            start_time = time.time()
            
            # ARP tablosunu al
            arp_table = get_arp_table()
            
            # ARP tablosundan gateway bilgisini al
            gateway = get_default_gateway()
            
            # ARP spoofing tespiti yap
            suspicious = detect_arp_spoofing(arp_table)
            
            # Tehdit seviyesini belirle
            threat_level = "none"  # Varsayılan olarak tehdit yok
            
            # Yüksek tehdit varsa seviyeyi yükselt
            if any(entry.get("threat_level") == "high" for entry in suspicious):
                threat_level = "high"
            # Orta seviye tehdit varsa ve henüz yüksek seviye tespit edilmediyse
            elif any(entry.get("threat_level") == "medium" for entry in suspicious):
                threat_level = "medium"
            
            # Sonuçları hazırla
            result = {
                "timestamp": time.time(),
                "arp_table": arp_table,
                "gateway": gateway,
                "suspicious_entries": suspicious,
                "threat_level": threat_level,
                "duration": time.time() - start_time
            }
            
            # Geçmişe ekle (en fazla son 100 taramayı tut)
            self.scan_history.append(result)
            if len(self.scan_history) > 100:
                self.scan_history = self.scan_history[-100:]
            
            # Callback fonksiyonu varsa çağır
            if self.callback:
                self.callback(result)
            
            self.logger.info(f"Tarama tamamlandı. Tehdit seviyesi: {threat_level}")
        except Exception as e:
            self.logger.error(f"Tarama sırasında hata: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
    
    def _periodic_scan_thread(self):
        """Periyodik tarama işlemini gerçekleştiren thread"""
        try:
            self.logger.info(f"Periyodik tarama başlatıldı (Her {self.scan_interval} saatte bir)")
            
            while self.periodic_running and not self.stop_event.is_set():
                # Hemen bir tarama başlat
                if not self.running:  # Eğer halihazırda bir tarama çalışmıyorsa
                    self.start_scan()
                
                # Bir sonraki taramaya kadar bekle
                # Her 10 saniyede bir durdurma sinyalini kontrol et
                interval_seconds = self.scan_interval * 3600  # saat -> saniye
                wait_start = time.time()
                
                while time.time() - wait_start < interval_seconds:
                    if self.stop_event.is_set() or not self.periodic_running:
                        break
                    time.sleep(10)  # 10 saniye bekle ve kontrol et
            
            self.logger.info("Periyodik tarama döngüsü sona erdi")
        except Exception as e:
            self.logger.error(f"Periyodik tarama sırasında hata: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.periodic_running = False
    
    def get_last_scan_result(self):
        """En son tarama sonucunu döndürür"""
        if self.scan_history:
            return self.scan_history[-1]
        return None
    
    def get_scan_history(self):
        """Tarama geçmişini döndürür"""
        return self.scan_history
