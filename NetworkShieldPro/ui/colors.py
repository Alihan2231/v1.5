#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Renk Teması ve Stil Sabitlerini İçeren Modül
Bu modül, uygulama genelinde kullanılan renk ve stil sabitlerini içerir.
"""

# Temel Spotify tarzı renk şeması
THEME = {
    # Ana renkler
    "background": "#121212",  # Koyu arka plan
    "card_background": "#181818",  # Kart arka planı
    "sidebar_background": "#000000",  # Kenar çubuğu arka planı
    
    # Vurgu renkleri
    "primary": "#1DB954",  # Spotify yeşili
    "secondary": "#535353",  # Gri ton
    "tertiary": "#B3B3B3",  # Açık gri
    
    # Durum renkleri
    "success": "#1DB954",  # Yeşil (başarı)
    "warning": "#F9A825",  # Sarı (uyarı)
    "error": "#E53935",  # Kırmızı (hata)
    "info": "#2196F3",  # Mavi (bilgi)
    
    # Metin renkleri
    "text_primary": "#FFFFFF",  # Beyaz
    "text_secondary": "#B3B3B3",  # Gri
    "text_tertiary": "#6F6F6F",  # Koyu gri
    "text_disabled": "#535353",  # Pasif metin
    
    # Etkileşim durumları
    "hover_primary": "#1ED760",  # Yeşil hover durumu
    "active_primary": "#169C46",  # Yeşil aktif/basılı durumu
    "hover_secondary": "#636363",  # Gri hover durumu
    "active_secondary": "#434343",  # Gri aktif/basılı durumu
    
    # Kenar çizgisi
    "border": "#333333",  # Kenar çizgisi
    
    # Yarıçap değerleri
    "radius_small": 4,  # Küçük köşe yuvarlaklığı
    "radius_medium": 8,  # Orta köşe yuvarlaklığı
    "radius_large": 16,  # Büyük köşe yuvarlaklığı
    
    # Animasyon süreleri (ms)
    "animation_fast": 150,  # Hızlı animasyon
    "animation_medium": 300,  # Orta hızda animasyon
    "animation_slow": 600,  # Yavaş animasyon
    
    # Gölge efektleri
    "shadow": "0 4px 8px rgba(0, 0, 0, 0.3)",  # Standart gölge
    "shadow_large": "0 8px 16px rgba(0, 0, 0, 0.5)",  # Büyük gölge
    
    # Özel renkler (uygulamaya özgü)
    "network_secure": "#1DB954",  # Güvenli ağ
    "network_warning": "#F9A825",  # Şüpheli ağ
    "network_danger": "#E53935",  # Tehlikeli ağ
    "network_unknown": "#757575",  # Bilinmeyen/taranmamış ağ
}

# Renk temaları (koyu/açık)
THEMES = {
    "dark": THEME,
    "light": {
        # Ana renkler
        "background": "#FFFFFF",  # Beyaz arka plan
        "card_background": "#F5F5F5",  # Açık gri kart arka planı
        "sidebar_background": "#EEEEEE",  # Kenar çubuğu arka planı
        
        # Vurgu renkleri (aynı)
        "primary": "#1DB954",  # Spotify yeşili
        "secondary": "#BDBDBD",  # Gri ton
        "tertiary": "#757575",  # Koyu gri
        
        # Durum renkleri (aynı)
        "success": "#1DB954",  # Yeşil (başarı)
        "warning": "#F9A825",  # Sarı (uyarı)
        "error": "#E53935",  # Kırmızı (hata)
        "info": "#2196F3",  # Mavi (bilgi)
        
        # Metin renkleri (ters)
        "text_primary": "#212121",  # Siyah
        "text_secondary": "#616161",  # Koyu gri
        "text_tertiary": "#9E9E9E",  # Açık gri
        "text_disabled": "#BDBDBD",  # Pasif metin
        
        # Etkileşim durumları
        "hover_primary": "#1ED760",  # Yeşil hover durumu
        "active_primary": "#169C46",  # Yeşil aktif/basılı durumu
        "hover_secondary": "#D5D5D5",  # Gri hover durumu
        "active_secondary": "#C2C2C2",  # Gri aktif/basılı durumu
        
        # Kenar çizgisi
        "border": "#E0E0E0",  # Kenar çizgisi
        
        # Yuvarlaklık değerleri (aynı)
        "radius_small": 4,
        "radius_medium": 8,
        "radius_large": 16,
        
        # Animasyon süreleri (aynı)
        "animation_fast": 150,
        "animation_medium": 300,
        "animation_slow": 600,
        
        # Gölge efektleri
        "shadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
        "shadow_large": "0 4px 8px rgba(0, 0, 0, 0.2)",
        
        # Özel renkler (aynı)
        "network_secure": "#1DB954",
        "network_warning": "#F9A825",
        "network_danger": "#E53935",
        "network_unknown": "#9E9E9E",
    }
}

def get_status_color(status):
    """
    Durum bilgisine göre uygun rengi döndürür.
    
    Args:
        status (str): Durum metni (success, warning, error, info, vb.)
        
    Returns:
        str: Renk kodu
    """
    status_map = {
        "success": THEME["success"],
        "warning": THEME["warning"],
        "error": THEME["error"],
        "info": THEME["info"],
        "none": THEME["text_secondary"],
        "high": THEME["error"],
        "medium": THEME["warning"],
        "low": THEME["info"],
        "secure": THEME["success"],
        "unknown": THEME["text_tertiary"]
    }
    
    return status_map.get(status.lower(), THEME["text_primary"])
