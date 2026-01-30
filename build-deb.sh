#!/bin/bash
# YouTube Music Player - Otomatik .DEB Paket Oluşturucu
# Bu script sizin için tüm adımları otomatik olarak yapar

set -e  # Hata olursa dur

echo "=========================================="
echo "YouTube Music Player - .DEB Oluşturucu"
echo "=========================================="
echo ""

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Gerekli dosyaları kontrol et
if [ ! -f "ytmusic.py" ]; then
    echo -e "${RED}HATA: ytmusic.py dosyası bulunamadı!${NC}"
    echo "Bu scripti ytmusic.py dosyasıyla aynı klasörde çalıştırın."
    exit 1
fi

echo -e "${GREEN}✓${NC} ytmusic.py dosyası bulundu"

# Paket bilgilerini al
echo ""
echo "Paket bilgilerini girin (Enter ile geçebilirsiniz):"
read -p "Paket adı [ytmusic-player]: " PACKAGE_NAME
PACKAGE_NAME=${PACKAGE_NAME:-ytmusic-player}

read -p "Versiyon [1.0.0]: " VERSION
VERSION=${VERSION:-1.0.0}

read -p "Maintainer adı [$(whoami)]: " MAINTAINER_NAME
MAINTAINER_NAME=${MAINTAINER_NAME:-$(whoami)}

read -p "Maintainer e-mail [user@example.com]: " MAINTAINER_EMAIL
MAINTAINER_EMAIL=${MAINTAINER_EMAIL:-user@example.com}

# Geçici dizini temizle
echo ""
echo -e "${YELLOW}📁 Proje yapısı oluşturuluyor...${NC}"
BUILD_DIR="${PACKAGE_NAME}_${VERSION}"
rm -rf "$BUILD_DIR"

# Klasör yapısını oluştur
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/pixmaps"
mkdir -p "$BUILD_DIR/usr/share/$PACKAGE_NAME"

echo -e "${GREEN}✓${NC} Klasör yapısı oluşturuldu"

# DEBIAN/control dosyası
echo -e "${YELLOW}📝 control dosyası oluşturuluyor...${NC}"
# Depends kısmına yt-dlp eklendi, böylece apt üzerinden kurulmaya çalışılır
cat > "$BUILD_DIR/DEBIAN/control" <<EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: sound
Priority: optional
Architecture: all
Depends: python3 (>= 3.8), python3-pyqt6, mpv, yt-dlp, python3-pip
Maintainer: $MAINTAINER_NAME <$MAINTAINER_EMAIL>
Description: YouTube Playlist Music Player
 Modern GUI ile YouTube playlistlerini çalan müzik çalar.
 MPV ve yt-dlp kullanarak YouTube'dan müzik çalar.
 PyQt6 arayüzü ile kullanımı kolaydır.
 .
 Özellikler:
  - YouTube playlist desteği
  - Modern ve kullanıcı dostu arayüz
  - Ses kontrolü
  - Rastgele çalma modu
  - Playlist yönetimi
EOF
echo -e "${GREEN}✓${NC} control dosyası oluşturuldu"

# DEBIAN/postinst
echo -e "${YELLOW}📝 postinst scripti oluşturuluyor...${NC}"
cat > "$BUILD_DIR/DEBIAN/postinst" <<'EOF'
#!/bin/bash
set -e

echo "YouTube Music Player kurulumu tamamlanıyor..."

# Gerekli paketleri kontrol et
missing=""
if ! command -v mpv &> /dev/null; then
    missing="${missing}mpv "
fi

# yt-dlp kontrolü: Önce apt ile kuruldu mu bak, yoksa pip ile dene
if ! command -v yt-dlp &> /dev/null; then
    echo "yt-dlp bulunamadı, pip ile kurulmaya çalışılıyor..."
    pip3 install yt-dlp --break-system-packages 2>/dev/null || pip3 install yt-dlp || true
fi

if [ -n "$missing" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  UYARI: Bazı bağımlılıklar eksik olabilir!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Eksik: $missing"
    echo "Otomatik kurulum deneniyor..."
    apt-get install -y $missing || true
fi

echo ""
echo "✅ YouTube Music Player başarıyla kuruldu!"
echo ""
echo "Kullanım:"
echo "  • Menüden: YouTube Music Player"
echo "  • Terminalden: ytmusic-player"
echo ""

exit 0
EOF
chmod 755 "$BUILD_DIR/DEBIAN/postinst"
echo -e "${GREEN}✓${NC} postinst scripti oluşturuldu"

# DEBIAN/prerm
echo -e "${YELLOW}📝 prerm scripti oluşturuluyor...${NC}"
cat > "$BUILD_DIR/DEBIAN/prerm" <<'EOF'
#!/bin/bash
set -e

echo "YouTube Music Player kaldırılıyor..."

# Kullanıcı verilerini koru (isteğe bağlı)
if [ -d "$HOME/.ytmusic-player" ]; then
    echo "Not: Kullanıcı verileri korunuyor (~/.ytmusic-player)"
fi

exit 0
EOF
chmod 755 "$BUILD_DIR/DEBIAN/prerm"
echo -e "${GREEN}✓${NC} prerm scripti oluşturuldu"

# Python scriptini kopyala
echo -e "${YELLOW}📋 Python scripti kopyalanıyor...${NC}"
cp ytmusic.py "$BUILD_DIR/usr/share/$PACKAGE_NAME/ytmusic.py"
chmod 755 "$BUILD_DIR/usr/share/$PACKAGE_NAME/ytmusic.py"
echo -e "${GREEN}✓${NC} Python scripti kopyalandı"

# Başlatıcı script
# LOGLAMA EKLENDİ: Hata durumunda debug.log dosyasına yazar
echo -e "${YELLOW}🚀 Başlatıcı script oluşturuluyor...${NC}"
cat > "$BUILD_DIR/usr/bin/$PACKAGE_NAME" <<EOF
#!/bin/bash
# YouTube Music Player Başlatıcı

# Kullanıcı verilerini saklamak için klasör oluştur
USERDIR="\$HOME/.ytmusic-player"
if [ ! -d "\$USERDIR" ]; then
    mkdir -p "\$USERDIR"
fi

# Uygulamayı kullanıcı dizininden başlat (config dosyaları için)
cd "\$USERDIR"

# Python scriptini çalıştır ve log tut
# Hata oluşursa kullanıcının debug.log dosyasını inceleyebilmesi için
echo "Başlatılıyor: \$(date)" > "\$USERDIR/debug.log"
exec python3 /usr/share/$PACKAGE_NAME/ytmusic.py "\$@" >> "\$USERDIR/debug.log" 2>&1
EOF
chmod 755 "$BUILD_DIR/usr/bin/$PACKAGE_NAME"
echo -e "${GREEN}✓${NC} Başlatıcı script oluşturuldu"

# Desktop Entry
echo -e "${YELLOW}🖥️  Desktop entry oluşturuluyor...${NC}"
cat > "$BUILD_DIR/usr/share/applications/$PACKAGE_NAME.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=YouTube Music Player
Name[tr]=YouTube Müzik Çalar
GenericName=Music Player
GenericName[tr]=Müzik Çalar
Comment=Play YouTube playlists with a modern GUI
Comment[tr]=YouTube playlistlerini modern bir arayüzle çal
Exec=$PACKAGE_NAME
Icon=multimedia-audio-player
Terminal=false
Categories=AudioVideo;Audio;Player;Qt;
Keywords=music;audio;youtube;player;playlist;mpv;
StartupNotify=true
EOF
echo -e "${GREEN}✓${NC} Desktop entry oluşturuldu"

# İzinleri düzelt
echo -e "${YELLOW}🔒 Dosya izinleri ayarlanıyor...${NC}"
chmod 755 "$BUILD_DIR/DEBIAN"
chmod 644 "$BUILD_DIR/DEBIAN/control"
chmod 755 "$BUILD_DIR/usr"
chmod 755 "$BUILD_DIR/usr/bin"
chmod 755 "$BUILD_DIR/usr/share"
chmod 755 "$BUILD_DIR/usr/share/applications"
chmod 644 "$BUILD_DIR/usr/share/applications/$PACKAGE_NAME.desktop"
echo -e "${GREEN}✓${NC} İzinler ayarlandı"

# .deb paketi oluştur
echo ""
echo -e "${YELLOW}📦 .deb paketi oluşturuluyor...${NC}"
echo ""

DEB_FILE="${PACKAGE_NAME}_${VERSION}_all.deb"
fakeroot dpkg-deb --build "$BUILD_DIR" "$DEB_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✅ BAŞARILI!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Paket oluşturuldu: $DEB_FILE"
    echo ""
    echo "Kurulum için:"
    echo "  sudo dpkg -i $DEB_FILE"
    echo "  sudo apt --fix-broken install  (eğer bağımlılık hatası olursa)"
    echo ""
    echo "Test için:"
    echo "  $PACKAGE_NAME"
    echo ""
    echo "Eğer çalışmazsa logu kontrol edin:"
    echo "  cat ~/.ytmusic-player/debug.log"
    echo ""
    
else
    echo -e "${RED}❌ HATA: Paket oluşturulamadı!${NC}"
    exit 1
fi

# Temizlik yap? (opsiyonel)
echo ""
read -p "Build klasörünü temizlemek ister misiniz? (y/N): " CLEANUP
if [[ $CLEANUP =~ ^[Yy]$ ]]; then
    rm -rf "$BUILD_DIR"
    echo -e "${GREEN}✓${NC} Build klasörü temizlendi"
fi

echo ""
echo "Tamamlandı! 🎉"
