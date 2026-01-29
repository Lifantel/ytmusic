@echo off
chcp 65001 >nul
title YouTube Music Player - Basit Kurulum
color 0B

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║     YouTube Music Player - Basit Kurulum ve Derleme          ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo Bu script:
echo  ✓ Python paketlerini kurar
echo  ✓ .exe dosyası oluşturur
echo.
echo ÖNCELİKLE KURMANIZ GEREKENLER:
echo  1. Python 3.8+ (https://www.python.org/downloads/)
echo  2. MPV Player (https://mpv.io/installation/)
echo.
pause

echo.
echo ═══════════════════════════════════════════════════════════════
echo ADIM 1: Python Kontrolü
echo ═══════════════════════════════════════════════════════════════
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı!
    echo.
    echo Python'u indirin: https://www.python.org/downloads/
    echo Kurulumda "Add Python to PATH" seçeneğini işaretleyin!
    echo.
    pause
    exit /b 1
)
python --version
echo ✅ Python bulundu!
echo.

echo ═══════════════════════════════════════════════════════════════
echo ADIM 2: MPV Kontrolü
echo ═══════════════════════════════════════════════════════════════
where mpv >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MPV Player bulunamadı!
    echo.
    echo MPV'yi şu adreslerden indirin:
    echo   • Windows: https://mpv.io/installation/
    echo   • Scoop:   scoop install mpv
    echo   • Chocolatey: choco install mpv
    echo.
    echo İndirdikten sonra:
    echo   1. mpv.exe'yi bu klasöre koyun, VEYA
    echo   2. mpv.exe'yi sistem PATH'ine ekleyin
    echo.
    echo Devam etmek için MPV'yi kurun ve bu scripti tekrar çalıştırın.
    pause
    exit /b 1
)
mpv --version | findstr /C:"mpv"
echo ✅ MPV bulundu!
echo.

echo ═══════════════════════════════════════════════════════════════
echo ADIM 3: Python Paketlerini Kurma
echo ═══════════════════════════════════════════════════════════════
echo.
echo Pip güncelleniyor...
python -m pip install --upgrade pip --quiet

echo PyQt6 kuruluyor...
python -m pip install PyQt6 --quiet
if errorlevel 1 (
    echo ❌ PyQt6 kurulamadı!
    pause
    exit /b 1
)
echo ✅ PyQt6 kuruldu

echo yt-dlp kuruluyor...
python -m pip install yt-dlp --quiet
if errorlevel 1 (
    echo ❌ yt-dlp kurulamadı!
    pause
    exit /b 1
)
echo ✅ yt-dlp kuruldu

echo PyInstaller kuruluyor...
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo ❌ PyInstaller kurulamadı!
    pause
    exit /b 1
)
echo ✅ PyInstaller kuruldu
echo.

echo ═══════════════════════════════════════════════════════════════
echo ADIM 4: Dosya Kontrolü
echo ═══════════════════════════════════════════════════════════════
if not exist "ytmusic.py" (
    echo ❌ ytmusic.py bulunamadı!
    echo Bu dosyayı .bat ile aynı klasöre koyun.
    pause
    exit /b 1
)
echo ✅ ytmusic.py bulundu
echo.

echo ═══════════════════════════════════════════════════════════════
echo ADIM 5: .EXE Dosyası Oluşturuluyor
echo ═══════════════════════════════════════════════════════════════
echo.
echo Bu işlem 2-5 dakika sürebilir, lütfen bekleyin...
echo.

:: Eski build dosyalarını temizle
if exist "build" rd /s /q "build" 2>nul
if exist "dist" rd /s /q "dist" 2>nul
if exist "YouTubeMusicPlayer.spec" del "YouTubeMusicPlayer.spec" 2>nul

:: PyInstaller ile derle
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "YouTubeMusicPlayer" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "yt_dlp" ^
    --collect-all "yt_dlp" ^
    ytmusic.py

if errorlevel 1 (
    echo.
    echo ❌ Derleme başarısız oldu!
    echo.
    echo Olası çözümler:
    echo  1. Tüm Python paketlerini tekrar kurun
    echo  2. Python'u yönetici olarak çalıştırın
    echo  3. Antivirüsü geçici olarak kapatın
    echo.
    pause
    exit /b 1
)

:: .exe'yi kopyala
if exist "dist\YouTubeMusicPlayer.exe" (
    copy "dist\YouTubeMusicPlayer.exe" . >nul
    echo.
    echo ╔═══════════════════════════════════════════════════════════════╗
    echo ║                ✅ BAŞARIYLA TAMAMLANDI! ✅                    ║
    echo ╚═══════════════════════════════════════════════════════════════╝
    echo.
    echo 🎉 YouTubeMusicPlayer.exe oluşturuldu!
    echo.
    echo 📁 Dosya: %CD%\YouTubeMusicPlayer.exe
    echo 📦 Boyut: 
    for %%A in (YouTubeMusicPlayer.exe) do echo    %%~zA bytes
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo ÖNEMLİ NOTLAR:
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo 1. MPV GEREKLI:
    echo    - mpv.exe'yi YouTubeMusicPlayer.exe ile AYNI klasörde tutun
    echo    - VEYA mpv.exe'yi sistem PATH'inde tutun
    echo.
    echo 2. ÇALIŞTIRMA:
    echo    - YouTubeMusicPlayer.exe'ye çift tıklayın
    echo    - İlk çalıştırmada Windows Defender uyarı verebilir
    echo      (Zararsızdır, "More info" → "Run anyway" tıklayın)
    echo.
    echo 3. DAĞITIM:
    echo    - YouTubeMusicPlayer.exe'yi paylaşabilirsiniz
    echo    - mpv.exe'yi de birlikte paylaşın
    echo    - Kullanıcıların mpv'ye ihtiyacı olacak
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo TEMİZLİK (Opsiyonel):
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Aşağıdaki dosya/klasörleri silebilirsiniz:
    echo  - build\
    echo  - dist\
    echo  - __pycache__\
    echo  - YouTubeMusicPlayer.spec
    echo.
    echo Bunları silmek için 'Y' tuşuna basın (silmemek için herhangi bir tuş):
    choice /C YN /N /M ""
    if errorlevel 2 goto :skip_cleanup
    if errorlevel 1 (
        echo.
        echo Temizlik yapılıyor...
        rd /s /q "build" 2>nul
        rd /s /q "dist" 2>nul
        rd /s /q "__pycache__" 2>nul
        del "YouTubeMusicPlayer.spec" 2>nul
        echo ✅ Temizlik tamamlandı!
    )
    :skip_cleanup
    echo.
) else (
    echo ❌ .exe dosyası oluşturulamadı!
    echo dist klasörünü kontrol edin.
    pause
    exit /b 1
)

echo.
echo 🚀 Uygulamayı test etmek için YouTubeMusicPlayer.exe'yi çalıştırın!
echo.
echo GitHub: https://github.com/Lifantel/ytmusic
echo Lisans: GPL-3.0
echo.
pause
