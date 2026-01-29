# 🎵 YouTube Music Player

Modern, hareketli GUI'ye sahip YouTube playlist müzik çalar uygulaması.

## ✨ Özellikler

- 🎨 **Modern ve Hareketli GUI**: Gradient renkler, animasyonlu kontroller
- 🔒 **Cookie'siz Çalışma**: Android client kullanarak güvenli erişim
- 📋 **Playlist Desteği**: YouTube playlistlerini kolayca yükleyin
- 💾 **Playlist Kaydetme**: Favori playlistlerinizi kaydedin
- 🎛️ **Tam Kontrol**: Çal/duraklat, ileri/geri, ses kontrolü
- ⏸️ **Akıllı Pause**: Durdurduğunuz yerde kalır, devam ettiğinizde kaldığı yerden başlar
- 🔀 **Rastgele Çalma**: Shuffle modu ile rastgele şarkı dinleyin
- 📊 **İlerleme Çubuğu**: Şarkının neresinde olduğunuzu görün ve atlayın
- 📝 **Canlı Log**: Tüm işlemleri takip edin
- 🚫 **GUI Donması Yok**: Tüm işlemler arka plan thread'lerinde çalışır

## 🔧 Gereksinimler

### Zorunlu Bağımlılıklar

1. **Python 3.8+**
2. **MPV Player**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install mpv
   
   # macOS
   brew install mpv
   
   # Fedora
   sudo dnf install mpv
   ```

3. **yt-dlp**
   ```bash
   # pip ile
   pip install yt-dlp
   
   # veya direkt binary
   sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
   sudo chmod a+rx /usr/local/bin/yt-dlp
   ```

4. **PyQt6**
   ```bash
   pip install PyQt6
   ```

### Tüm Python Paketleri

```bash
pip install PyQt6 yt-dlp
```

## 🚀 Kurulum ve Çalıştırma

### 🐧 Linux/Mac - Python ile

1. **Bağımlılıkları yükleyin:**
   ```bash
   # MPV
   sudo apt install mpv  # Ubuntu/Debian
   # veya
   brew install mpv      # macOS
   
   # Python paketleri
   pip install -r requirements.txt
   # veya
   pip install PyQt6 yt-dlp
   ```

2. **Uygulamayı çalıştırın:**
   ```bash
   python3 youtube_music_player.py
   ```

### 🪟 Windows - Otomatik .EXE Kurulum

**Basit Yöntem (Önerilen):**
```cmd
build_exe_simple.bat
```

Bu script:
- ✅ Python'u kontrol eder
- ✅ MPV kurulumunu kontrol eder (sizin kurmanızı bekler)
- ✅ Gerekli Python paketlerini kurar
- ✅ PyInstaller ile YouTubeMusicPlayer.exe oluşturur

**Tam Otomatik (MPV'yi de indirir):**
```cmd
build_exe.bat
```

Bu script ek olarak:
- ✅ MPV'yi otomatik indirir ve kurar

**Manuel .EXE Oluşturma:**
```cmd
# Önce gereksinimleri kurun
pip install -r requirements.txt

# Sonra derleyin
pyinstaller --onefile --windowed --name YouTubeMusicPlayer ytmusic.py
```

**⚠️ Önemli Notlar:**
- .exe çalışması için **mpv.exe** aynı klasörde olmalı veya sistem PATH'inde bulunmalı
- Python 3.8+ gereklidir: https://www.python.org/downloads/
- MPV Player gereklidir: https://mpv.io/installation/

  🪟 Windows için MPV Kurulum Adımları
Windows kullanıcıları için MPV'nin manuel olarak kurulması ve programa tanıtılması gerekir. Aşağıdaki adımları izleyin:

1. Doğru Dosyayı İndirme
[shinchiro builds](https://github.com/shinchiro/mpv-winbuild-cmake/releases) adresine gidin ve sisteminize uygun olan güncel sürümü seçin:

Önerilen (Modern PC'ler): Adında v3 geçen dosyayı indirin (Örn: mpv-x86_64-v3-git-xxxx.7z). Bu sürüm modern işlemciler için optimize edilmiştir.

Standart: Eğer bilgisayarınız eskiyse veya v3 hata verirse, içinde v3 yazmayan standart sürümü (mpv-x86_64-git-xxxx.7z) indirin.

⚠️ Dikkat: * İçinde dev veya ffmpeg yazan dosyaları indirmeyin; bunlar geliştiriciler içindir veya oynatıcıyı içermez.

i686 yazan dosyalar 32-bit sistemler içindir, modern 64-bit bilgisayarlarda performans düşüklüğüne neden olur.

2. Kurulum ve Tanımlama
İndirdiğiniz .7z arşivini bir klasöre çıkartın (7-Zip veya WinRAR gerekebilir).

Yöntem A (Önerilen): Klasör içindeki mpv.exe dosyasını kopyalayıp bu projenin (YouTube Music Player) ana dizinine yapıştırın.

Yöntem B (Sistem Geneli): Klasör içindeki mpv-install.bat dosyasına sağ tıklayıp "Yönetici Olarak Çalıştır" diyerek MPV'yi sisteme kaydedin.

## 📖 Kullanım Kılavuzu

### İlk Kullanım

1. **Uygulama açıldığında**, otomatik olarak bağımlılıkları kontrol eder
2. Eksik bağımlılık varsa uyarı verir ve kurulum talimatlarını gösterir

### Playlist Ekleme

1. **YouTube'dan bir playlist URL'si kopyalayın**
   - Örnek: `https://www.youtube.com/playlist?list=PLxxxxxx`
   
2. **URL'yi "Playlist Ekle" alanına yapıştırın**

3. **(Opsiyonel) Playlist'e bir isim verin**
   - Örnek: "Favori Şarkılarım", "Çalışma Müzikleri"

4. **"📥 Yükle" butonuna tıklayın**

5. Playlist otomatik olarak yüklenecek ve kaydedilecektir

### Müzik Çalma

#### Yöntem 1: Liste'den Seç
- Şarkı listesinden bir şarkıya **çift tıklayın**

#### Yöntem 2: Kontrol Düğmeleri
- **"▶️ Çal"** butonuna basın (ilk şarkıdan başlar)
- **"⏸️ Duraklat"** - Şarkıyı duraklatır (tam olarak durdurduğunuz yerde kalır)
- **"▶️ Devam"** - Duraklattığınız yerden devam eder
- **"⏭️ Sonraki"** - Sonraki şarkıya geçer (rastgele modda random şarkı)
- **"⏮️ Önceki"** - Önceki şarkıya geçer (rastgele modda random şarkı)
- **"⏹️ Durdur"** - Çalmayı tamamen durdurur
- **"🔀 Rastgele"** - Shuffle modunu açar/kapatır

### Rastgele Çalma (Shuffle)

1. **"🔀 Rastgele: Kapalı"** butonuna tıklayın
2. Buton **turuncu** renge döner: "🔀 Rastgele: Açık"
3. Artık ileri/geri butonları rastgele şarkı seçer
4. Şarkı bitince otomatik olarak rastgele bir şarkı çalar
5. Tekrar tıklayarak kapatabilirsiniz

### Duraklat ve Devam Et

- **Pause özelliği akıllıdır**: 
  - Bir şarkıyı duraklattığınızda, tam olarak o saniyede durur
  - "▶️ Devam" butonuna bastığınızda, kaldığı yerden devam eder
  - Başka bir şarkıya geçene kadar pozisyon korunur

### İlerleme ve Ses Kontrolü

#### İlerleme Çubuğu
- **Görüntüleme**: Şarkının neresinde olduğunuzu gösterir
- **Atlama**: Çubuk üzerinde istediğiniz yere tıklayın veya sürükleyin

#### Ses Kontrolü
- Sağ alttaki **ses çubuğunu** kullanın
- **0-100 arası** ayarlanabilir
- Ayarlar otomatik kaydedilir

### Kayıtlı Playlistler

- Eklediğiniz tüm playlistler otomatik kaydedilir
- **"💾 Kayıtlı Playlistler"** listesinden **çift tıklayarak** yeniden yükleyebilirsiniz
- Playlist'ler `playlists.json` dosyasında saklanır

## 🎨 GUI Özellikleri

### Tasarım
- **Gradient arka plan**: Mor-mavi tonları
- **Smooth animasyonlar**: Buton hover efektleri
- **Modern renkler**: Koyu tema, göz yormayan
- **Responsive**: Pencere boyutlandırılabilir

### Donma Önleme
- ✅ **Tüm ağır işlemler arka planda** (QThread)
- ✅ **Playlist yükleme** - Thread
- ✅ **MPV kontrolü** - Ayrı thread
- ✅ **Bağımlılık kontrolü** - Thread
- ✅ **Pozisyon güncelleme** - Async

## 🐛 Sorun Giderme

### "MPV bulunamadı" Hatası
```bash
# MPV'yi yükleyin
sudo apt install mpv
```

### "yt-dlp bulunamadı" Hatası
```bash
pip install yt-dlp
# veya
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp
```

### "Playlist yüklenemedi" Hatası
- İnternet bağlantınızı kontrol edin
- URL'nin geçerli bir YouTube playlist URL'si olduğundan emin olun
- Log sekmesinden detaylı hata mesajını kontrol edin

### "Video çalınmıyor" Hatası
- MPV'nin düzgün kurulu olduğundan emin olun: `mpv --version`
- Log sekmesinden hata detaylarına bakın
- Farklı bir şarkı deneyin

### GUI Donuyor
- Bu uygulama özel olarak donmaması için tasarlanmıştır
- Tüm ağır işlemler arka planda çalışır
- Eğer donma olursa, log sekmesini kontrol edin

## 📁 Dosyalar

Uygulama çalıştırıldığında şu dosyalar oluşturulur:

- **`playlists.json`**: Kayıtlı playlistler
- **`music_player_config.json`**: Ses seviyesi gibi ayarlar
- **`/tmp/mpv_socket_*`**: MPV iletişim socket'i (geçici)

## 🎯 Özellikler ve İpuçları

### Otomatik Sonraki Şarkı
- Bir şarkı bittiğinde otomatik olarak sonraki şarkıya geçer
- Playlist sonunda başa döner

### Keyboard Shortcuts (Planlanan)
- Space: Çal/Duraklat
- →: 10 saniye ileri
- ←: 10 saniye geri
- ↑: Ses artır
- ↓: Ses azalt

### Playlist Sıralaması
- Son eklenen playlist en üstte görünür
- Playlistler alfabetik sıralanmaz

## 🔐 Güvenlik

- ✅ **Cookie gerekmez**: Android client kullanır
- ✅ **Oturum açma yok**: YouTube hesabı gerektirmez
- ✅ **Veri toplama yok**: Tamamen lokal çalışır
- ✅ **Açık kaynak**: Kodları inceleyebilirsiniz

## 📊 Performans

- **Düşük CPU kullanımı**: Sadece çalarken aktif
- **Düşük RAM**: ~50-100 MB
- **Network**: Sadece streaming sırasında
- **Disk**: JSON dosyaları çok küçük (<1 MB)

## 🚧 Bilinen Sınırlamalar

- Premium içerik çalmaz (YouTube Premium gerektiren)
- Yaş kısıtlamalı videolar çalmayabilir
- Çok uzun playlistlerde yükleme biraz yavaş olabilir
- İndirme özelliği yok (sadece streaming)

## 💡 Gelecek Özellikler

- [x] Shuffle (Karışık çalma) - ✅ EKLENDİ
- [x] Akıllı Pause/Resume - ✅ EKLENDİ
- [ ] Repeat (Tekrar)
- [ ] Playlist düzenleme
- [ ] Equalizer
- [ ] Keyboard shortcuts
- [ ] Playlist export/import
- [ ] Mini player modu

## 📄 Lisans

Bu proje GPL-3.0 lisansı altında lisanslanmıştır.

**GPL-3.0 (GNU General Public License v3.0)**
- ✅ Özgür kullanım
- ✅ Değiştirme ve dağıtma hakkı
- ✅ Ticari kullanım
- ⚠️ Kaynak kodu paylaşma zorunluluğu
- ⚠️ Değişikliklerin belgelenmesi

Detaylar: https://www.gnu.org/licenses/gpl-3.0.html

## 🔗 Bağlantılar

- **GitHub**: https://github.com/Lifantel/ytmusic
- **Lisans**: GPL-3.0
- **Sorunlar**: https://github.com/Lifantel/ytmusic/issues

## 🤝 Katkıda Bulunma

Önerileriniz ve hata raporlarınız için GitHub'da issue açabilirsiniz.

**Geliştirme:**
1. Fork yapın
2. Yeni branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request açın

---

**🎵 İyi Dinlemeler! 🎵**
