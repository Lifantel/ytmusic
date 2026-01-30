# YouTube Music Player - .DEB Paketleme Rehberi

Bu rehber, Python uygulamanızı .deb paketine dönüştürmeniz için adım adım talimatlar içerir.

## 📋 Gereksinimler

Öncelikle sisteminizde şunlar kurulu olmalı:
```bash
sudo apt install python3 python3-pip dpkg-dev fakeroot
```

## 📁 Adım 1: Proje Klasör Yapısını Oluşturun

Terminal açın ve şu komutları çalıştırın:

```bash
# Ana klasörü oluştur
mkdir -p ytmusic-player
cd ytmusic-player

# DEBIAN klasörünü oluştur (paket bilgileri için)
mkdir -p DEBIAN

# Uygulama dosyalarının gideceği klasörleri oluştur
mkdir -p usr/bin
mkdir -p usr/share/applications
mkdir -p usr/share/pixmaps
mkdir -p usr/share/ytmusic-player
```

## 📝 Adım 2: DEBIAN/control Dosyasını Oluşturun

Bu dosya paketinizin bilgilerini içerir:

```bash
nano DEBIAN/control
```

İçine şunu yazın:

```
Package: ytmusic-player
Version: 1.0.0
Section: sound
Priority: optional
Architecture: all
Depends: python3 (>= 3.8), python3-pyqt6, python3-pip, mpv, yt-dlp
Maintainer: Sizin Adınız <email@example.com>
Description: YouTube Playlist Music Player
 Modern GUI ile YouTube playlistlerini çalan müzik çalar.
 MPV ve yt-dlp kullanarak YouTube'dan müzik çalar.
 PyQt6 arayüzü ile kullanımı kolaydır.
```

Kaydet ve çık (Ctrl+O, Enter, Ctrl+X)

## 📝 Adım 3: DEBIAN/postinst Dosyasını Oluşturun

Bu dosya kurulum sonrası çalışacak script:

```bash
nano DEBIAN/postinst
```

İçine şunu yazın:

```bash
#!/bin/bash
set -e

# Python bağımlılıklarını kur
pip3 install yt-dlp --break-system-packages 2>/dev/null || pip3 install yt-dlp

# Gerekli paketleri kontrol et
if ! command -v mpv &> /dev/null; then
    echo "MPV kurulmamış. Lütfen 'sudo apt install mpv' komutuyla kurun."
fi

if ! command -v yt-dlp &> /dev/null; then
    echo "yt-dlp kurulmamış. Lütfen 'pip3 install yt-dlp' komutuyla kurun."
fi

echo "YouTube Music Player başarıyla kuruldu!"
echo "Uygulamayı menüden başlatabilir veya terminalde 'ytmusic-player' yazabilirsiniz."

exit 0
```

Kaydet ve çık, sonra çalıştırılabilir yap:

```bash
chmod 755 DEBIAN/postinst
```

## 📝 Adım 4: DEBIAN/prerm Dosyasını Oluşturun

Kaldırma öncesi script:

```bash
nano DEBIAN/prerm
```

İçine şunu yazın:

```bash
#!/bin/bash
set -e

echo "YouTube Music Player kaldırılıyor..."

exit 0
```

Kaydet ve çalıştırılabilir yap:

```bash
chmod 755 DEBIAN/prerm
```

## 📝 Adım 5: Ana Python Dosyasını Kopyalayın

```bash
# Python scriptinizi usr/share/ytmusic-player/ klasörüne kopyalayın
cp /yol/ytmusic.py usr/share/ytmusic-player/ytmusic.py
chmod 755 usr/share/ytmusic-player/ytmusic.py
```

## 📝 Adım 6: Başlatıcı Script Oluşturun

```bash
nano usr/bin/ytmusic-player
```

İçine şunu yazın:

```bash
#!/bin/bash
cd ~/.ytmusic-player 2>/dev/null || mkdir -p ~/.ytmusic-player && cd ~/.ytmusic-player
exec python3 /usr/share/ytmusic-player/ytmusic.py "$@"
```

Kaydet ve çalıştırılabilir yap:

```bash
chmod 755 usr/bin/ytmusic-player
```

## 📝 Adım 7: Desktop Entry Oluşturun

Uygulamanızın menüde görünmesi için:

```bash
nano usr/share/applications/ytmusic-player.desktop
```

İçine şunu yazın:

```
[Desktop Entry]
Version=1.0
Type=Application
Name=YouTube Music Player
Name[tr]=YouTube Müzik Çalar
Comment=Play YouTube playlists with a modern GUI
Comment[tr]=YouTube playlistlerini modern bir arayüzle çal
Exec=ytmusic-player
Icon=ytmusic-player
Terminal=false
Categories=AudioVideo;Audio;Player;Qt;
Keywords=music;audio;youtube;player;playlist;
```

## 🖼️ Adım 8: İkon Ekleyin (İsteğe Bağlı)

Bir ikon dosyanız varsa (PNG, 48x48 veya 128x128):

```bash
cp ikon.png usr/share/pixmaps/ytmusic-player.png
```

İkon yoksa basit bir tane oluşturabilirsiniz veya şimdilik atlayabilirsiniz.

## 🔨 Adım 9: .DEB Paketini Oluşturun

Artık paketi oluşturabilirsiniz:

```bash
# ytmusic-player klasörünün üst dizinine gidin
cd ..

# Paketi oluştur
dpkg-deb --build ytmusic-player

# veya daha detaylı çıktı için:
fakeroot dpkg-deb --build ytmusic-player
```

Başarılı olursa `ytmusic-player.deb` dosyası oluşacak!

## 📦 Adım 10: Paketi Test Edin

```bash
# Paketi kurun
sudo dpkg -i ytmusic-player.deb

# Bağımlılık hatası olursa:
sudo apt --fix-broken install

# Uygulamayı çalıştırın
ytmusic-player

# Veya menüden "YouTube Music Player" uygulamasını başlatın
```

## 🗑️ Paketi Kaldırma

```bash
sudo apt remove ytmusic-player
# veya
sudo dpkg -r ytmusic-player
```

## ✅ Kontrol Listesi

- [ ] DEBIAN/control dosyası oluşturuldu
- [ ] DEBIAN/postinst oluşturuldu ve çalıştırılabilir yapıldı
- [ ] DEBIAN/prerm oluşturuldu ve çalıştırılabilir yapıldı
- [ ] Python scripti kopyalandı
- [ ] Başlatıcı script oluşturuldu
- [ ] Desktop entry oluşturuldu
- [ ] İkon eklendi (opsiyonel)
- [ ] Paket oluşturuldu
- [ ] Paket test edildi

## 🐛 Sorun Giderme

**Hata: "dpkg-deb: error: control directory has bad permissions"**
```bash
chmod 755 DEBIAN
chmod 644 DEBIAN/control
```

**Hata: "dpkg-deb: error: failed to open package info file"**
- DEBIAN/control dosyasının doğru yazıldığından emin olun

**Uygulama açılmıyor:**
```bash
# Logları kontrol edin
ytmusic-player
# veya
journalctl -xe
```

**Bağımlılık sorunları:**
```bash
sudo apt --fix-broken install
```

## 📚 Ek Bilgiler

### Paket Versiyonunu Güncelleme

DEBIAN/control dosyasındaki Version satırını değiştirin:
```
Version: 1.0.1
```

### Paket Bilgilerini Görüntüleme

```bash
dpkg-deb -I ytmusic-player.deb
dpkg-deb -c ytmusic-player.deb  # İçindeki dosyaları göster
```

### Kurulu Paketi Kontrol Etme

```bash
dpkg -l | grep ytmusic
dpkg -L ytmusic-player  # Paket dosyalarını listele
```
