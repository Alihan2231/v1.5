#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ayarlar Modülü
Bu modül, uygulama ayarlarını kaydetmek ve yüklemek için fonksiyonlar içerir.
"""

import os
import json
import logging

# Loglama
logger = logging.getLogger("V-ARP.settings")

# Ayarlar dosyasının yolu
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE = os.path.join(APP_DIR, "arp_settings.json")

def load_settings():
    """
    Ayarları dosyadan yükler, dosya yoksa varsayılan ayarları döndürür.
    
    Returns:
        dict: Ayarlar sözlüğü
    """
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            logger.debug(f"Ayarlar yüklendi: {settings}")
            return settings
        else:
            logger.info("Ayarlar dosyası bulunamadı, varsayılan ayarlar kullanılıyor.")
            # Varsayılan ayarlar
            default_settings = {
                "scan_interval": 24,
                "auto_scan": True,
                "dark_mode": False,
                "notifications_enabled": True,
                "periodic_scan_active": False
            }
            # Varsayılan ayarları kaydet
            save_settings(default_settings)
            return default_settings
    except Exception as e:
        logger.error(f"Ayarlar yüklenirken hata: {e}")
        # Hata durumunda en temel varsayılan ayarları döndür
        return {
            "scan_interval": 24,
            "auto_scan": True,
            "dark_mode": False,
            "notifications_enabled": True,
            "periodic_scan_active": False
        }

def save_settings(settings):
    """
    Ayarları dosyaya kaydeder.
    
    Args:
        settings (dict): Kaydedilecek ayarlar sözlüğü
        
    Returns:
        bool: İşlem başarılı ise True, aksi halde False
    """
    try:
        logger.debug(f"Ayarlar kaydediliyor: {settings}")
        # Dosya dizininin varlığını kontrol et
        directory = os.path.dirname(SETTINGS_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        logger.info(f"Ayarlar başarıyla kaydedildi: {SETTINGS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ayarlar kaydedilirken hata: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_setting(key, default=None):
    """
    Belirli bir ayarı getirir.
    
    Args:
        key (str): Ayar anahtarı
        default: Ayar bulunamazsa döndürülecek değer
        
    Returns:
        Ayar değeri veya default değeri
    """
    settings = load_settings()
    value = settings.get(key, default)
    logger.debug(f"Ayar okundu: {key} = {value}")
    return value

def set_setting(key, value):
    """
    Belirli bir ayarı günceller ve kaydeder.
    
    Args:
        key (str): Ayar anahtarı
        value: Ayarlanacak değer
        
    Returns:
        bool: İşlem başarılı ise True, aksi halde False
    """
    settings = load_settings()
    settings[key] = value
    logger.debug(f"Ayar güncellendi: {key} = {value}")
    return save_settings(settings)

def update_settings(settings_dict):
    """
    Birden fazla ayarı aynı anda günceller.
    
    Args:
        settings_dict (dict): Güncellenecek ayarlar sözlüğü
        
    Returns:
        bool: İşlem başarılı ise True, aksi halde False
    """
    settings = load_settings()
    settings.update(settings_dict)
    logger.debug(f"Ayarlar toplu güncellendi: {settings_dict}")
    return save_settings(settings)

def reset_settings():
    """
    Ayarları varsayılan değerlerine sıfırlar.
    
    Returns:
        bool: İşlem başarılı ise True, aksi halde False
    """
    default_settings = {
        "scan_interval": 24,
        "auto_scan": True,
        "dark_mode": False,
        "notifications_enabled": True,
        "periodic_scan_active": False
    }
    logger.info("Ayarlar varsayılan değerlere sıfırlanıyor")
    return save_settings(default_settings)
