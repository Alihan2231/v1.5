#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spotify temalı renkler ve stil sabitleri
Bu modül, uygulamanın genel renk şemasını ve stil sabitlerini tanımlar.
"""

# Ana renkler
BACKGROUND = "#121212"  # Ana arka plan rengi
CARD_BACKGROUND = "#181818"  # Kart arka plan rengi
SIDEBAR_BACKGROUND = "#000000"  # Kenar çubuğu arka plan rengi
PRIMARY = "#1DB954"  # Spotify yeşili - ana vurgu rengi
SECONDARY = "#535353"  # İkincil vurgu rengi

# Metin renkleri
TEXT_PRIMARY = "#FFFFFF"  # Beyaz ana metin
TEXT_SECONDARY = "#B3B3B3"  # Gri ikincil metin
TEXT_DISABLED = "#707070"  # Devre dışı metin

# Uyarı renkleri
WARNING = "#F59B23"  # Turuncu uyarı
ERROR = "#E61E32"  # Kırmızı hata
SUCCESS = "#1DB954"  # Yeşil başarı

# Kenarlık renkleri
BORDER = "#333333"  # Kenarlık rengi

# Hover ve Active durumları
HOVER_LIGHT = "#282828"  # Üzerine gelindiğinde arka plan (açık)
HOVER_PRIMARY = "#1ED760"  # Üzerine gelindiğinde ana renk
ACTIVE_PRIMARY = "#1AA64C"  # Tıklandığında ana renk

# Metin boyutları
FONT_LARGE = 20  # Büyük metin
FONT_MEDIUM = 14  # Orta metin
FONT_SMALL = 12  # Küçük metin
FONT_TINY = 10  # Çok küçük metin

# Yuvarlatılmış köşe yarıçapları
RADIUS_SMALL = 4  # Küçük yuvarlatılmış köşe
RADIUS_MEDIUM = 8  # Orta yuvarlatılmış köşe
RADIUS_LARGE = 16  # Büyük yuvarlatılmış köşe

# Dolgular
PADDING_SMALL = 8  # Küçük dolgu
PADDING_MEDIUM = 16  # Orta dolgu
PADDING_LARGE = 24  # Büyük dolgu

# Animasyon süresi (milisaniye)
ANIMATION_FAST = 150  # Hızlı animasyon
ANIMATION_MEDIUM = 300  # Orta animasyon
ANIMATION_SLOW = 500  # Yavaş animasyon

# Ek özellikler
ICON_SMALL = 16  # Küçük simge boyutu
ICON_MEDIUM = 24  # Orta simge boyutu
ICON_LARGE = 32  # Büyük simge boyutu

# Tüm renkleri ve stilleri içeren sözlük
THEME = {
    # Ana renkler
    "background": BACKGROUND,
    "card_background": CARD_BACKGROUND,
    "sidebar_background": SIDEBAR_BACKGROUND,
    "primary": PRIMARY,
    "secondary": SECONDARY,
    
    # Metin renkleri
    "text_primary": TEXT_PRIMARY,
    "text_secondary": TEXT_SECONDARY,
    "text_disabled": TEXT_DISABLED,
    
    # Uyarı renkleri
    "warning": WARNING,
    "error": ERROR,
    "success": SUCCESS,
    
    # Kenarlık renkleri
    "border": BORDER,
    
    # Hover ve Active durumları
    "hover_light": HOVER_LIGHT,
    "hover_primary": HOVER_PRIMARY,
    "active_primary": ACTIVE_PRIMARY,
    
    # Metin boyutları
    "font_large": FONT_LARGE,
    "font_medium": FONT_MEDIUM,
    "font_small": FONT_SMALL,
    "font_tiny": FONT_TINY,
    
    # Yuvarlatılmış köşe yarıçapları
    "radius_small": RADIUS_SMALL,
    "radius_medium": RADIUS_MEDIUM,
    "radius_large": RADIUS_LARGE,
    
    # Dolgular
    "padding_small": PADDING_SMALL,
    "padding_medium": PADDING_MEDIUM,
    "padding_large": PADDING_LARGE,
    
    # Animasyon süresi
    "animation_fast": ANIMATION_FAST,
    "animation_medium": ANIMATION_MEDIUM,
    "animation_slow": ANIMATION_SLOW,
    
    # Ek özellikler
    "icon_small": ICON_SMALL,
    "icon_medium": ICON_MEDIUM,
    "icon_large": ICON_LARGE,
}

# Durumlar için renk getirme fonksiyonu
def get_status_color(threat_level):
    """Tehdit seviyesine göre renk döndürür"""
    if threat_level == "high":
        return ERROR
    elif threat_level == "medium":
        return WARNING
    elif threat_level == "none":
        return SUCCESS
    else:
        return SECONDARY
