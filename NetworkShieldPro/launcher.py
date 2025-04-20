import os
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

if is_admin():
    # Zaten yönetici olarak çalışıyoruz, uygulamayı başlat
    print("Yönetici haklarıyla çalıştırılıyor...")
    os.system("python main.py")
else:
    # Yönetici haklarıyla yeniden başlat
    print("Yönetici hakları isteniyor...")
    ctypes.windll.shell32.ShellExecuteW(
        None, 
        "runas", 
        sys.executable, 
        "launcher.py", 
        os.path.abspath(os.path.dirname(sys.argv[0])), 
        1
    )
