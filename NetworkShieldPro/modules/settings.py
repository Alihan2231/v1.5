#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ayarlar Modülü
Bu modül, uygulama ayarlarını kaydetmek ve yüklemek için fonksiyonlar içerir.
"""

import os
import json

# Ayarlar dosyasının yolu
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "arp_settings.json")

def load_settings():
    """
    Ayarları dosyadan yükler, dosya yoksa boş sözlük döndürür.
    
    Returns:
        dict: Ayarlar sözlüğü
    """
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            return settings
        else:
            return {}
    except Exception as e:
        print(f"Ayarlar yüklenirken hata: {e}")
        return {}

def save_settings(settings):
    """
    Ayarları dosyaya kaydeder.
    
    Args:
        settings (dict): Kaydedilecek ayarlar sözlüğü
        
    Returns:
        bool: İşlem başarılı ise True, aksi halde False
    """
    try:
        print(f"Ayarlar kaydediliyor: {settings}")
        # Dosya dizininin varlığını kontrol et
        directory = os.path.dirname(SETTINGS_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        print(f"Ayarlar başarıyla kaydedildi: {SETTINGS_FILE}")
        return True
    except Exception as e:
        print(f"Ayarlar kaydedilirken hata: {e}")
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
    return settings.get(key, default)

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
    return save_settings(settings)