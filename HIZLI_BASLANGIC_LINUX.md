# 🚀 Hızlı Başlangıç - .DEB Paketi Oluşturma

Bu dosya, en hızlı şekilde .deb paketi oluşturmanız için gereken adımları içerir.

## ⚡ Otomatik Yöntem (ÖNERİLEN)

### 1. Dosyaları Hazırlayın

```bash
# Bir klasör oluşturun
mkdir youtube-music-player
cd youtube-music-player

# ytmusic.py ve build-deb.sh dosyalarını bu klasöre koyun
```

### 2. Gerekli Araçları Kurun

```bash
sudo apt update
sudo apt install dpkg-dev fakeroot python3
```

### 3. Build Scriptini Çalıştırın

```bash
# Scripti çalıştırılabilir yapın
chmod +x build-deb.sh

# Scripti çalıştırın
./build-deb.sh
```

Script size birkaç soru soracak:
- Paket adı (Enter = ytmusic-player)
- Versiyon (Enter = 1.0.0)
- Adınız (Enter = kullanıcı adınız)
- E-mail (Enter = user@example.com)

### 4. Paketi Kurun ve Test Edin

```bash
# Paketi kurun
sudo dpkg -i ytmusic-player_1.0.0_all.deb

# Eğer bağımlılık hatası olursa:
sudo apt --fix-broken install

# Uygulamayı başlatın
ytmusic-player
```

**İşte bu kadar! 🎉**

---

## 📖 Manuel Yöntem

Eğer otomatik script çalışmazsa veya kendi elinizle yapmak isterseniz, `PAKETLEME_REHBERI.md` dosyasındaki adımları takip edin.

---

## 🔧 Sorun Giderme

### "dpkg-deb: command not found"
```bash
sudo apt install dpkg-dev
```

### "Permission denied" hatası
```bash
chmod +x build-deb.sh
chmod +x ytmusic.py
```

### "fakeroot: command not found"
```bash
sudo apt install fakeroot
```

### Paket kuruldu ama çalışmıyor
```bash
# Bağımlılıkları kontrol edin
sudo apt install python3-pyqt6 mpv
pip3 install yt-dlp

# Uygulamayı terminalde çalıştırıp hataları görün
ytmusic-player
```

---

## 📦 Hazır Paket Dağıtımı

Oluşturduğunuz .deb dosyasını başkalarıyla paylaşabilirsiniz:

1. `ytmusic-player_1.0.0_all.deb` dosyasını kopyalayın
2. Alıcılar şu komutla kurabilir:
   ```bash
   sudo dpkg -i ytmusic-player_1.0.0_all.deb
   sudo apt --fix-broken install
   ```

---

## 💡 İpuçları

- **Versiyon güncellemesi:** build-deb.sh'yi tekrar çalıştırın ve farklı bir versiyon girin
- **Paket bilgileri:** `dpkg-deb -I paket.deb` ile görüntüleyin
- **Paket içeriği:** `dpkg-deb -c paket.deb` ile görüntüleyin
- **Kurulu paket:** `dpkg -l | grep ytmusic` ile kontrol edin

---

## 📝 Notlar

- Build scripti otomatik olarak tüm gerekli dosyaları ve klasörleri oluşturur
- Kullanıcı ayarları `~/.ytmusic-player/` klasöründe saklanır
- Paket kaldırıldığında kullanıcı verileri korunur
- Desktop entry sayesinde uygulama menüde görünür

---

## ❓ Yardım

Herhangi bir sorun yaşarsanız:

1. `PAKETLEME_REHBERI.md` dosyasını okuyun
2. Hata mesajlarını kontrol edin
3. Build klasörünü inceleyin
4. Log dosyalarına bakın

İyi çalışmalar! 🎵
