@echo off
chcp 65001 >nul
title YouTube Music Player - Otomatik Kurulum ve Derleme
color 0A

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║        YouTube Music Player - Otomatik Kurulum               ║
echo ║                                                               ║
echo ║  Bu script şunları yapacak:                                  ║
echo ║  1. Python kurulu mu kontrol et                              ║
echo ║  2. MPV Player indir ve kur                                  ║
echo ║  3. Gerekli Python paketlerini kur                           ║
echo ║  4. PyInstaller ile .exe dosyası oluştur                     ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo.
pause

:: Python kontrolü
echo [1/4] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ HATA: Python bulunamadı!
    echo.
    echo Python'u indirmek için tarayıcınızda şu sayfayı açın:
    echo https://www.python.org/downloads/
    echo.
    echo Kurulum sırasında "Add Python to PATH" seçeneğini işaretlemeyi unutmayın!
    echo.
    pause
    exit /b 1
)
python --version
echo ✅ Python bulundu!
echo.

:: MPV kontrolü ve kurulumu
echo [2/4] MPV Player kontrol ediliyor...
where mpv >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MPV bulunamadı. İndiriliyor...
    echo.
    
    :: MPV indirme URL'si (Windows 64-bit)
    set MPV_URL=https://sourceforge.net/projects/mpv-player-windows/files/64bit/mpv-x86_64-20231231-git-e58a38b.7z/download
    set MPV_FILE=mpv.7z
    
    echo MPV indiriliyor (bu biraz zaman alabilir)...
    curl -L -o "%MPV_FILE%" "%MPV_URL%"
    
    if not exist "%MPV_FILE%" (
        echo ❌ MPV indirilemedi!
        echo Manuel olarak şu adresten indirebilirsiniz:
        echo https://mpv.io/installation/
        echo.
        echo Ardından mpv.exe dosyasını bu klasöre kopyalayın veya
        echo mpv.exe'nin bulunduğu klasörü PATH'e ekleyin.
        echo.
        pause
        exit /b 1
    )
    
    :: 7-Zip kontrolü (MPV arşivini açmak için)
    where 7z >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  MPV arşivini açmak için 7-Zip gerekli.
        echo.
        echo Manuel kurulum:
        echo 1. MPV'yi şu adresten indirin: https://mpv.io/installation/
        echo 2. mpv.exe dosyasını PATH'e ekleyin veya bu klasöre kopyalayın
        echo.
        pause
        exit /b 1
    )
    
    :: MPV'yi çıkar
    echo MPV arşivi açılıyor...
    7z x "%MPV_FILE%" -o"mpv" -y >nul
    
    :: mpv.exe'yi doğru konuma taşı
    if exist "mpv\mpv.exe" (
        copy "mpv\mpv.exe" . >nul
        echo ✅ MPV kuruldu!
    ) else (
        echo ❌ MPV kurulumu başarısız!
        echo Manuel olarak mpv.exe'yi bu klasöre kopyalayın.
        pause
        exit /b 1
    )
    
    :: Temizlik
    del "%MPV_FILE%" >nul 2>&1
    rd /s /q "mpv" >nul 2>&1
) else (
    mpv --version | findstr /i "mpv"
    echo ✅ MPV bulundu!
)
echo.

:: yt-dlp kontrolü ve kurulumu
echo Ek kontrol: yt-dlp...
where yt-dlp >nul 2>&1
if errorlevel 1 (
    echo ⚠️  yt-dlp bulunamadı, pip ile kurulacak...
) else (
    yt-dlp --version
    echo ✅ yt-dlp bulundu!
)
echo.

:: Python paketlerini kur
echo [3/4] Python paketleri kuruluyor...
echo.
echo PyQt6 kuruluyor...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install PyQt6 --quiet
if errorlevel 1 (
    echo ❌ PyQt6 kurulamadı!
    pause
    exit /b 1
)
echo ✅ PyQt6 kuruldu!

echo yt-dlp kuruluyor...
python -m pip install yt-dlp --quiet
if errorlevel 1 (
    echo ❌ yt-dlp kurulamadı!
    pause
    exit /b 1
)
echo ✅ yt-dlp kuruldu!

echo PyInstaller kuruluyor...
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo ❌ PyInstaller kurulamadı!
    pause
    exit /b 1
)
echo ✅ PyInstaller kuruldu!
echo.

:: Python script kontrolü
if not exist "ytmusic.py" (
    echo ❌ HATA: ytmusic.py bulunamadı!
    echo Lütfen bu .bat dosyasını ytmusic.py ile aynı klasöre koyun.
    pause
    exit /b 1
)

:: .exe oluştur
echo [4/4] .exe dosyası oluşturuluyor...
echo Bu işlem birkaç dakika sürebilir, lütfen bekleyin...
echo.

pyinstaller --noconfirm --onefile --windowed ^
    --name "YouTubeMusicPlayer" ^
    --icon=NONE ^
    --add-data "ytmusic.py;." ^
    --hidden-import "PyQt6" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "yt_dlp" ^
    --collect-all "yt_dlp" ^
    --collect-all "PyQt6" ^
    ytmusic.py

if errorlevel 1 (
    echo.
    echo ❌ Derleme başarısız!
    echo Hata detayları için yukarıdaki mesajları kontrol edin.
    pause
    exit /b 1
)

echo.
echo ✅ Derleme tamamlandı!
echo.

:: .exe dosyasını dist klasöründen al
if exist "dist\YouTubeMusicPlayer.exe" (
    copy "dist\YouTubeMusicPlayer.exe" . >nul
    echo.
    echo ╔═══════════════════════════════════════════════════════════════╗
    echo ║                    KURULUM TAMAMLANDI!                        ║
    echo ╚═══════════════════════════════════════════════════════════════╝
    echo.
    echo 🎉 YouTubeMusicPlayer.exe oluşturuldu!
    echo.
    echo 📁 Dosya konumu: %CD%\YouTubeMusicPlayer.exe
    echo.
    echo 📋 Gerekli dosyalar:
    echo    - YouTubeMusicPlayer.exe (ana program)
    echo    - mpv.exe (oynatıcı - aynı klasörde olmalı)
    echo.
    echo ⚠️  ÖNEMLİ:
    echo    - mpv.exe dosyasını YouTubeMusicPlayer.exe ile aynı klasörde tutun
    echo    - veya mpv.exe'yi sistem PATH'ine ekleyin
    echo.
    echo 🚀 Uygulamayı çalıştırmak için YouTubeMusicPlayer.exe'ye çift tıklayın!
    echo.
    
    :: Temizlik önerisi
    echo.
    echo 🧹 Temizlik (opsiyonel):
    echo    Aşağıdaki klasörleri silebilirsiniz:
    echo    - build
    echo    - dist
    echo    - __pycache__
    echo    - YouTubeMusicPlayer.spec
    echo.
) else (
    echo ❌ YouTubeMusicPlayer.exe oluşturulamadı!
    echo dist klasörünü kontrol edin.
)

echo.
pause
