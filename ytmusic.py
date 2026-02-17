#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Playlist Music Player
Modern, hareketli GUI ile YouTube playlistlerini çalar
MPV ve yt-dlp kullanır, GUI donması engellenmiştir
"""

import sys
import json
import os
import subprocess
import shutil
import time
import re
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QSlider, QListWidget, QListWidgetItem,
    QMessageBox, QFrame, QProgressBar, QTextEdit, QSplitter, QGroupBox,
    QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QLinearGradient, QGradient

# yt-dlp için Güvenli Import
# Eğer kütüphane yoksa uygulama çökmez, GUI açılır ve hata mesajı verir.
try:
    import yt_dlp
    HAS_YT_DLP_LIB = True
except ImportError:
    HAS_YT_DLP_LIB = False


# ==================== KONFİGÜRASYON ====================
CONFIG_FILE = "music_player_config.json"
PLAYLISTS_FILE = "playlists.json"


class Config:
    """Uygulama yapılandırması"""
    @staticmethod
    def load():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"volume": 70, "last_playlist": ""}
    
    @staticmethod
    def save(config):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)


class PlaylistManager:
    """Playlist yönetimi"""
    @staticmethod
    def load():
        if os.path.exists(PLAYLISTS_FILE):
            try:
                with open(PLAYLISTS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    @staticmethod
    def save(playlists):
        with open(PLAYLISTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(playlists, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def add(url, name):
        playlists = PlaylistManager.load()
        playlist_id = url.split('list=')[-1].split('&')[0] if 'list=' in url else url
        
        # Aynı playlist varsa güncelle
        for pl in playlists:
            if pl['id'] == playlist_id:
                pl['name'] = name
                pl['url'] = url
                pl['updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                PlaylistManager.save(playlists)
                return
        
        # Yeni playlist ekle
        playlists.insert(0, {
            'id': playlist_id,
            'name': name,
            'url': url,
            'added': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'updated': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        PlaylistManager.save(playlists)


# ==================== BACKGROUND THREADS ====================

class DependencyChecker(QThread):
    """Bağımlılıkları kontrol eder - GUI donmasını engeller"""
    finished = pyqtSignal(bool, str)
    
    def run(self):
        missing = []
        
        # MPV kontrolü
        if not shutil.which("mpv"):
            missing.append("MPV (Sistem Paketi)")
        
        # yt-dlp binary kontrolü (CLI)
        if not shutil.which("yt-dlp"):
            # Sadece binary yoksa sorun değil, kütüphane varsa çalışabilir ama yine de uyaralım
            # Ancak çoğu zaman ikisi beraber gelir.
            pass

        # yt-dlp kütüphane kontrolü (Import)
        if not HAS_YT_DLP_LIB:
            missing.append("yt-dlp (Python Modülü)")
        
        if missing:
            msg = f"Eksik bağımlılıklar: {', '.join(missing)}\n\n"
            msg += "Kurulum için:\n"
            if "MPV (Sistem Paketi)" in missing:
                msg += "  - Ubuntu/Debian: sudo apt install mpv\n"
            if "yt-dlp (Python Modülü)" in missing:
                msg += "  - Terminalden: sudo apt install yt-dlp\n"
                msg += "  - Veya: pip3 install yt-dlp --break-system-packages\n"
            self.finished.emit(False, msg)
        else:
            self.finished.emit(True, "Tüm bağımlılıklar mevcut!")


class PlaylistLoader(QThread):
    """Playlist bilgilerini yükler - arka planda"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        if not HAS_YT_DLP_LIB:
            self.error.emit("Kritik Hata: yt-dlp kütüphanesi yüklü değil! Lütfen 'pip3 install yt-dlp' komutunu çalıştırın.")
            return

        try:
            self.progress.emit("Playlist bilgileri alınıyor...")
            
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'ignoreerrors': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'skip': ['hls', 'dash']
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                if not info:
                    self.error.emit("Playlist bilgisi alınamadı")
                    return
                
                entries = info.get('entries', [])
                if not entries:
                    self.error.emit("Playlist boş veya geçersiz")
                    return
                
                songs = []
                for entry in entries:
                    if entry and 'id' in entry and 'title' in entry:
                        songs.append({
                            'id': entry['id'],
                            'title': entry['title'],
                            'url': f"https://www.youtube.com/watch?v={entry['id']}",
                            'duration': entry.get('duration', 0)
                        })
                
                self.finished.emit(songs)
                
        except Exception as e:
            self.error.emit(f"Hata: {str(e)}")


class MPVPlayer(QThread):
    """MPV player kontrolü - ayrı thread'de"""
    position_changed = pyqtSignal(float, float)  # current, duration
    state_changed = pyqtSignal(str)  # playing, paused, stopped
    volume_changed = pyqtSignal(int)
    error = pyqtSignal(str)
    song_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.current_url = None
        self.is_running = False
        self.is_paused = False
        self.socket_path = f"/tmp/mpv_socket_{os.getpid()}"
        
    def run(self):
        """Thread ana döngüsü - pozisyon takibi"""
        self.is_running = True
        last_pos = -1
        
        while self.is_running:
            if self.process and self.process.poll() is None:
                # MPV'den pozisyon bilgisi al
                try:
                    pos = self.get_property('time-pos')
                    duration = self.get_property('duration')
                    
                    if pos is not None and duration is not None:
                        if abs(pos - last_pos) > 0.5:  # Sadece önemli değişikliklerde sinyal gönder
                            self.position_changed.emit(float(pos), float(duration))
                            last_pos = pos
                        
                        # Şarkı bitti mi?
                        if duration > 0 and pos >= duration - 1:
                            self.song_finished.emit()
                            
                except:
                    pass
                    
                time.sleep(0.5)
            else:
                time.sleep(0.1)
    
    def play(self, url, volume=70):
        """Yeni şarkı çal"""
        self.stop()
        
        try:
            # Socket varsa temizle
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)
            
            cmd = [
                'mpv',
                '--no-video',
                '--no-terminal',
                f'--input-ipc-server={self.socket_path}',
                f'--volume={volume}',
                '--ytdl-format=bestaudio[ext=m4a]/bestaudio/best',
                '--script-opts=ytdl_hook-try_ytdl_first=yes',
                '--ytdl-raw-options=extractor-args=youtube:player_client=android',
                url
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            
            self.current_url = url
            self.is_paused = False  # Yeni şarkı başladı, pause değil
            time.sleep(0.5)  # MPV'nin başlaması için kısa bekle
            
            if self.process.poll() is not None:
                stderr = self.process.stderr.read().decode('utf-8', errors='ignore')
                raise Exception(f"MPV başlatılamadı: {stderr[:300]}")
            
            self.state_changed.emit('playing')
            
        except Exception as e:
            self.error.emit(str(e))
    
    def pause(self):
        """Duraklat/Devam"""
        self.send_command('cycle pause')
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.state_changed.emit('paused')
        else:
            self.state_changed.emit('playing')
    
    def stop(self):
        """Durdur"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
        self.is_paused = False
        self.state_changed.emit('stopped')
    
    def seek(self, position):
        """Belirli pozisyona git"""
        self.send_command(f'seek {position} absolute')
    
    def set_volume(self, volume):
        """Ses seviyesi ayarla"""
        self.send_command(f'set volume {volume}')
        self.volume_changed.emit(volume)
    
    def send_command(self, command):
        """MPV'ye komut gönder"""
        try:
            if os.path.exists(self.socket_path):
                import socket
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                sock.connect(self.socket_path)
                sock.send(f'{{"command": {json.dumps(command.split())}}}\n'.encode())
                sock.close()
        except:
            pass
    
    def get_property(self, prop):
        """MPV'den özellik al"""
        try:
            if os.path.exists(self.socket_path):
                import socket
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                sock.connect(self.socket_path)
                cmd = json.dumps({"command": ["get_property", prop]}) + '\n'
                sock.send(cmd.encode())
                response = sock.recv(4096).decode('utf-8')
                sock.close()
                
                data = json.loads(response)
                if data.get('error') == 'success':
                    return data.get('data')
        except:
            pass
        return None
    
    def cleanup(self):
        """Temizlik - thread güvenli"""
        self.is_running = False
        self.stop()
        
        # Socket temizliği
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except:
                pass
        
        # Thread'in durmasını bekle
        time.sleep(0.5)


# ==================== MAIN WINDOW ====================

class MusicPlayer(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("🎵 YouTube Music Player")
        self.setGeometry(100, 100, 1000, 700)
        
        # State
        self.current_playlist = []
        self.current_index = -1
        self.is_playing = False
        self.is_shuffle = False  # Rastgele çalma modu
        self.config = Config.load()
        
        # MPV Player
        self.player = MPVPlayer()
        self.player.position_changed.connect(self.on_position_changed)
        self.player.state_changed.connect(self.on_state_changed)
        self.player.error.connect(self.on_player_error)
        self.player.song_finished.connect(self.play_next)
        self.player.start()  # Thread'i başlat
        
        # UI Setup
        self.setup_theme()
        self.setup_ui()
        
        # Bağımlılık kontrolü
        self.check_dependencies()
        
        # Kayıtlı playlistleri yükle
        self.load_saved_playlists()
    
    def setup_theme(self):
        """Modern, gradient tema"""
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        # Koyu tema paleti
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 40))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Base, QColor(20, 20, 28))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 45))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Button, QColor(40, 40, 50))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(100, 60, 200))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        app.setPalette(palette)
        
        # Stil
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a28, stop:1 #2d1b3d);
            }
            
            QGroupBox {
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                background: rgba(40, 40, 50, 0.6);
                font-weight: bold;
                color: #e0e0e0;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #a0a0ff;
            }
            
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #5a5a6a;
                border-radius: 8px;
                background: #2a2a38;
                color: white;
                font-size: 13px;
                selection-background-color: #6a4aaa;
            }
            
            QLineEdit:focus {
                border-color: #8a6aca;
            }
            
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6a4aaa, stop:1 #5a3a9a);
                color: white;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7a5aba, stop:1 #6a4aaa);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a3a9a, stop:1 #4a2a8a);
            }
            
            QPushButton:disabled {
                background: #3a3a4a;
                color: #6a6a7a;
            }
            
            QPushButton#playButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60);
                font-size: 16px;
                padding: 12px 30px;
            }
            
            QPushButton#playButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3edc81, stop:1 #37be70);
            }
            
            QPushButton#stopButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
            }
            
            QPushButton#stopButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f75c4c, stop:1 #d0493b);
            }
            
            QListWidget {
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                background: #20202a;
                outline: none;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #3a3a4a;
                border-radius: 4px;
                color: #d0d0d0;
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6a4aaa, stop:1 #8a6aca);
                color: white;
                font-weight: bold;
            }
            
            QListWidget::item:hover {
                background: #3a3a4a;
            }
            
            QSlider::groove:horizontal {
                height: 8px;
                background: #3a3a4a;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8a6aca, stop:1 #6a4aaa);
                border: 2px solid #5a3a9a;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #9a7ada, stop:1 #7a5aba);
            }
            
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6a4aaa, stop:1 #8a6aca);
                border-radius: 4px;
            }
            
            QLabel {
                color: #e0e0e0;
            }
            
            QTextEdit {
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                background: #20202a;
                color: #b0b0b0;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            
            QProgressBar {
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                text-align: center;
                color: white;
                background: #2a2a38;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6a4aaa, stop:1 #8a6aca);
                border-radius: 6px;
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                background: #2a2a38;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6a4aaa, stop:1 #8a6aca);
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7a5aba, stop:1 #9a7ada);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
    
    def setup_ui(self):
        """UI bileşenlerini oluştur"""
        # Scroll Area oluştur
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # İçerik widget'ı
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        # Ana layout
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Scroll area'yı central widget olarak ayarla
        self.setCentralWidget(scroll_area)
        
        # ========== HEADER ==========
        header = QLabel("🎵 YouTube Music Player")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #a0a0ff; padding: 10px;")
        layout.addWidget(header)
        
        # ========== PLAYLIST INPUT ==========
        playlist_group = QGroupBox("📋 Playlist Ekle")
        playlist_layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.playlist_input = QLineEdit()
        self.playlist_input.setPlaceholderText("YouTube Playlist URL'sini buraya yapıştırın...")
        self.playlist_input.returnPressed.connect(self.load_playlist)
        
        self.playlist_name_input = QLineEdit()
        self.playlist_name_input.setPlaceholderText("Playlist adı (opsiyonel)")
        self.playlist_name_input.setMaximumWidth(250)
        
        load_btn = QPushButton("📥 Yükle")
        load_btn.clicked.connect(self.load_playlist)
        load_btn.setMaximumWidth(120)
        
        input_layout.addWidget(self.playlist_input)
        input_layout.addWidget(self.playlist_name_input)
        input_layout.addWidget(load_btn)
        
        playlist_layout.addLayout(input_layout)
        
        # Kayıtlı playlistler
        saved_layout = QHBoxLayout()
        saved_label = QLabel("💾 Kayıtlı Playlistler:")
        self.saved_playlists_list = QListWidget()
        self.saved_playlists_list.setMaximumHeight(80)
        self.saved_playlists_list.itemDoubleClicked.connect(self.load_saved_playlist)
        
        saved_layout.addWidget(saved_label)
        saved_layout.addWidget(self.saved_playlists_list)
        
        playlist_layout.addLayout(saved_layout)
        playlist_group.setLayout(playlist_layout)
        layout.addWidget(playlist_group)
        
        # ========== MAIN CONTENT - SPLIT ==========
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Şarkı listesi
        songs_group = QGroupBox("🎼 Şarkı Listesi")
        songs_layout = QVBoxLayout()
        
        self.songs_list = QListWidget()
        self.songs_list.setMinimumHeight(250)  # Minimum yükseklik
        self.songs_list.itemDoubleClicked.connect(self.play_selected_song)
        songs_layout.addWidget(self.songs_list)
        
        songs_group.setLayout(songs_layout)
        splitter.addWidget(songs_group)
        
        # Sağ panel - Log
        log_group = QGroupBox("📝 Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        splitter.addWidget(log_group)
        
        splitter.setSizes([750, 250])  # Sol tarafa daha fazla alan
        layout.addWidget(splitter)
        
        # ========== NOW PLAYING ==========
        now_playing_group = QGroupBox("▶️ Şu Anda Çalıyor")
        now_playing_layout = QVBoxLayout()
        
        self.now_playing_label = QLabel("Henüz bir şarkı seçilmedi")
        self.now_playing_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.now_playing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.now_playing_label.setStyleSheet("color: #c0c0ff; padding: 8px;")
        now_playing_layout.addWidget(self.now_playing_label)
        
        now_playing_group.setLayout(now_playing_layout)
        layout.addWidget(now_playing_group)
        
        # ========== PROGRESS BAR ==========
        progress_layout = QHBoxLayout()
        
        self.time_label = QLabel("00:00")
        self.time_label.setMinimumWidth(50)
        self.time_label.setStyleSheet("color: #b0b0b0;")
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderPressed.connect(self.on_progress_pressed)
        self.progress_slider.sliderReleased.connect(self.on_progress_released)
        
        self.duration_label = QLabel("00:00")
        self.duration_label.setMinimumWidth(50)
        self.duration_label.setStyleSheet("color: #b0b0b0;")
        
        progress_layout.addWidget(self.time_label)
        progress_layout.addWidget(self.progress_slider)
        progress_layout.addWidget(self.duration_label)
        
        layout.addLayout(progress_layout)
        
        # ========== CONTROLS ==========
        controls_layout = QHBoxLayout()
        
        # Playback controls
        prev_btn = QPushButton("⏮️ Önceki")
        prev_btn.clicked.connect(self.play_previous)
        
        self.play_pause_btn = QPushButton("▶️ Çal")
        self.play_pause_btn.setObjectName("playButton")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        
        next_btn = QPushButton("⏭️ Sonraki")
        next_btn.clicked.connect(self.play_next)
        
        stop_btn = QPushButton("⏹️ Durdur")
        stop_btn.setObjectName("stopButton")
        stop_btn.clicked.connect(self.stop_playback)
        
        # Shuffle button
        self.shuffle_btn = QPushButton("🔀 Rastgele: Kapalı")
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.shuffle_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a5a, stop:1 #3a3a4a);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a5a6a, stop:1 #4a4a5a);
            }
        """)
        
        # Volume control
        volume_label = QLabel("🔊")
        volume_label.setStyleSheet("font-size: 16px;")
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.config.get('volume', 70))
        self.volume_slider.setMaximumWidth(150)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        
        self.volume_label_val = QLabel(f"{self.config.get('volume', 70)}%")
        self.volume_label_val.setMinimumWidth(45)
        
        controls_layout.addWidget(prev_btn)
        controls_layout.addWidget(self.play_pause_btn)
        controls_layout.addWidget(next_btn)
        controls_layout.addWidget(stop_btn)
        controls_layout.addWidget(self.shuffle_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(volume_label)
        controls_layout.addWidget(self.volume_slider)
        controls_layout.addWidget(self.volume_label_val)
        
        layout.addLayout(controls_layout)
        
        # ========== STATUS BAR ==========
        self.status_label = QLabel("Hazır")
        self.status_label.setStyleSheet("""
            background: #2a2a38;
            padding: 8px 15px;
            border-radius: 6px;
            color: #a0a0a0;
        """)
        layout.addWidget(self.status_label)
        
        # ========== FOOTER ==========
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 5, 0, 0)
        
        footer_label = QLabel()
        footer_label.setText('<a href="https://github.com/Lifantel/ytmusic" style="color: #8a6aca; text-decoration: none;">GPL-3.0 License</a> | © 2025 Lifantel')
        footer_label.setOpenExternalLinks(True)
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("""
            QLabel {
                color: #6a6a7a;
                font-size: 11px;
                padding: 5px;
            }
            QLabel a {
                color: #8a6aca;
                text-decoration: none;
            }
            QLabel a:hover {
                color: #9a7ada;
                text-decoration: underline;
            }
        """)
        
        footer_layout.addWidget(footer_label)
        layout.addLayout(footer_layout)
    
    def check_dependencies(self):
        """Bağımlılıkları kontrol et"""
        self.log("Bağımlılıklar kontrol ediliyor...")
        self.status_label.setText("Bağımlılıklar kontrol ediliyor...")
        
        self.dep_checker = DependencyChecker()
        self.dep_checker.finished.connect(self.on_dependencies_checked)
        self.dep_checker.finished.connect(self.dep_checker.deleteLater)  # Thread'i temizle
        self.dep_checker.start()
    
    def on_dependencies_checked(self, success, message):
        """Bağımlılık kontrolü tamamlandı"""
        if success:
            self.log("✅ " + message)
            self.status_label.setText("Hazır - Playlist ekleyebilirsiniz")
        else:
            self.log("❌ " + message)
            self.status_label.setText("Eksik bağımlılıklar tespit edildi!")
            QMessageBox.critical(self, "Eksik Bağımlılıklar", message)
    
    def load_saved_playlists(self):
        """Kayıtlı playlistleri yükle"""
        self.saved_playlists_list.clear()
        playlists = PlaylistManager.load()
        
        for pl in playlists:
            item_text = f"{pl['name']} ({pl['added']})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, pl)
            self.saved_playlists_list.addItem(item)
    
    def load_saved_playlist(self, item):
        """Kayıtlı playlist'i yükle"""
        pl_data = item.data(Qt.ItemDataRole.UserRole)
        self.playlist_input.setText(pl_data['url'])
        self.playlist_name_input.setText(pl_data['name'])
        self.load_playlist()
    
    def load_playlist(self):
        """Playlist'i yükle"""
        url = self.playlist_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir playlist URL'si girin!")
            return
        
        name = self.playlist_name_input.text().strip()
        if not name:
            # URL'den playlist ID'sini al
            playlist_id = url.split('list=')[-1].split('&')[0] if 'list=' in url else "Playlist"
            name = f"Playlist {playlist_id[:8]}"
        
        self.log(f"Playlist yükleniyor: {name}")
        self.status_label.setText("Playlist yükleniyor...")
        
        # Playlist kaydet
        PlaylistManager.add(url, name)
        self.load_saved_playlists()
        
        # Şarkıları yükle
        self.playlist_loader = PlaylistLoader(url)
        self.playlist_loader.progress.connect(self.log)
        self.playlist_loader.finished.connect(self.on_playlist_loaded)
        self.playlist_loader.error.connect(self.on_playlist_error)
        self.playlist_loader.finished.connect(self.playlist_loader.deleteLater)  # Thread'i temizle
        self.playlist_loader.start()
    
    def on_playlist_loaded(self, songs):
        """Playlist yüklendi"""
        self.current_playlist = songs
        self.songs_list.clear()
        
        for i, song in enumerate(songs):
            duration_str = self.format_time(song.get('duration', 0))
            item_text = f"{i+1}. {song['title']} [{duration_str}]"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, song)
            self.songs_list.addItem(item)
        
        self.log(f"✅ {len(songs)} şarkı yüklendi")
        self.status_label.setText(f"{len(songs)} şarkı hazır - Çalmaya başlayabilirsiniz")
        
        # İlk şarkıyı seç
        if songs:
            self.songs_list.setCurrentRow(0)
    
    def on_playlist_error(self, error_msg):
        """Playlist yükleme hatası"""
        self.log(f"❌ Hata: {error_msg}")
        self.status_label.setText("Playlist yüklenemedi!")
        QMessageBox.critical(self, "Hata", error_msg)
    
    def play_selected_song(self):
        """Seçili şarkıyı çal"""
        current_item = self.songs_list.currentItem()
        if not current_item:
            return
        
        self.current_index = self.songs_list.currentRow()
        self.play_current_song()
    
    def play_current_song(self):
        """Mevcut index'teki şarkıyı çal"""
        if not self.current_playlist or self.current_index < 0:
            return
        
        song = self.current_playlist[self.current_index]
        self.log(f"▶️ Çalınıyor: {song['title']}")
        
        self.now_playing_label.setText(f"🎵 {song['title']}")
        self.status_label.setText("Çalıyor...")
        
        volume = self.volume_slider.value()
        self.player.play(song['url'], volume)
        
        self.is_playing = True
        self.play_pause_btn.setText("⏸️ Duraklat")
        
        # Listede vurgula
        self.songs_list.setCurrentRow(self.current_index)
    
    def toggle_play_pause(self):
        """Çal/Duraklat"""
        if not self.current_playlist:
            QMessageBox.information(self, "Bilgi", "Önce bir playlist yükleyin!")
            return
        
        # Eğer şarkı çalmıyorsa ve hiç başlamadıysa
        if not self.is_playing and self.current_index < 0:
            self.current_index = 0
            self.play_current_song()
        # Eğer şarkı çalıyorsa ama pause edilmişse
        elif self.player.is_paused:
            self.player.pause()  # Resume
            self.play_pause_btn.setText("⏸️ Duraklat")
            self.is_playing = True
            self.log("▶️ Devam ediliyor")
        # Eğer şarkı çalıyorsa ve pause edilmemişse
        elif self.is_playing:
            self.player.pause()  # Pause
            self.play_pause_btn.setText("▶️ Devam")
            self.is_playing = False
            self.log("⏸️ Duraklatıldı")
        # Eğer durmuşsa, yeniden başlat
        else:
            if self.current_index < 0:
                self.current_index = 0
            self.play_current_song()
    
    def toggle_shuffle(self):
        """Rastgele çalma modunu aç/kapat"""
        self.is_shuffle = not self.is_shuffle
        
        if self.is_shuffle:
            self.shuffle_btn.setText("🔀 Rastgele: Açık")
            self.shuffle_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f39c12, stop:1 #e67e22);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f5ab35, stop:1 #e98b39);
                }
            """)
            self.log("🔀 Rastgele çalma: AÇIK")
        else:
            self.shuffle_btn.setText("🔀 Rastgele: Kapalı")
            self.shuffle_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4a4a5a, stop:1 #3a3a4a);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5a5a6a, stop:1 #4a4a5a);
                }
            """)
            self.log("🔀 Rastgele çalma: KAPALI")
    
    def stop_playback(self):
        """Çalmayı durdur"""
        self.player.stop()
        self.is_playing = False
        self.play_pause_btn.setText("▶️ Çal")
        self.now_playing_label.setText("Durduruldu")
        self.status_label.setText("Durduruldu")
        self.log("⏹️ Durduruldu")
    
    def play_next(self):
        """Sonraki şarkı - shuffle moduna göre"""
        if not self.current_playlist:
            return
        
        if self.is_shuffle:
            # Rastgele bir şarkı seç (mevcut hariç)
            import random
            available_indices = [i for i in range(len(self.current_playlist)) if i != self.current_index]
            if available_indices:
                self.current_index = random.choice(available_indices)
            else:
                self.current_index = 0
            self.log("⏭️🔀 Rastgele şarkıya geçildi")
        else:
            # Sıralı şekilde ilerle
            self.current_index = (self.current_index + 1) % len(self.current_playlist)
            self.log("⏭️ Sonraki şarkıya geçildi")
        
        self.play_current_song()
    
    def play_previous(self):
        """Önceki şarkı - shuffle modunda rastgele"""
        if not self.current_playlist:
            return
        
        if self.is_shuffle:
            # Rastgele bir şarkı seç (mevcut hariç)
            import random
            available_indices = [i for i in range(len(self.current_playlist)) if i != self.current_index]
            if available_indices:
                self.current_index = random.choice(available_indices)
            else:
                self.current_index = 0
            self.log("⏮️🔀 Rastgele şarkıya geçildi")
        else:
            # Sıralı şekilde geri git
            self.current_index = (self.current_index - 1) % len(self.current_playlist)
            self.log("⏮️ Önceki şarkıya geçildi")
        
        self.play_current_song()
    
    def on_position_changed(self, position, duration):
        """Pozisyon güncellendi"""
        if not self.progress_slider.isSliderDown():  # Kullanıcı sürüklüyorsa güncelleme
            self.progress_slider.setValue(int((position / duration) * 100) if duration > 0 else 0)
        
        self.time_label.setText(self.format_time(int(position)))
        self.duration_label.setText(self.format_time(int(duration)))
    
    def on_progress_pressed(self):
        """Progress bar tıklandı"""
        pass
    
    def on_progress_released(self):
        """Progress bar bırakıldı - seek yap"""
        duration = self.player.get_property('duration')
        if duration:
            position = (self.progress_slider.value() / 100) * duration
            self.player.seek(position)
            self.log(f"⏩ {self.format_time(int(position))} konumuna gidildi")
    
    def on_volume_changed(self, value):
        """Ses seviyesi değişti"""
        self.player.set_volume(value)
        self.volume_label_val.setText(f"{value}%")
        
        # Konfige kaydet
        self.config['volume'] = value
        Config.save(self.config)
    
    def on_state_changed(self, state):
        """Player durumu değişti"""
        if state == 'playing':
            self.status_label.setText("▶️ Çalıyor")
            self.play_pause_btn.setText("⏸️ Duraklat")
            self.is_playing = True
        elif state == 'paused':
            self.status_label.setText("⏸️ Duraklatıldı")
            self.play_pause_btn.setText("▶️ Devam")
            self.is_playing = False
        elif state == 'stopped':
            self.status_label.setText("⏹️ Durduruldu")
            self.play_pause_btn.setText("▶️ Çal")
            self.is_playing = False
    
    def on_player_error(self, error_msg):
        """Player hatası"""
        self.log(f"❌ Player hatası: {error_msg}")
        QMessageBox.critical(self, "Player Hatası", error_msg)
    
    def log(self, message):
        """Log mesajı ekle"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def format_time(self, seconds):
        """Saniyeyi MM:SS formatına çevir"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
    
    def closeEvent(self, event):
        """Pencere kapatılıyor - tüm thread'leri düzgün temizle"""
        self.log("Uygulama kapatılıyor...")
        
        # Player thread'ini durdur
        if self.player:
            self.player.is_running = False
            self.player.cleanup()
            self.player.quit()
            self.player.wait(2000)  # 2 saniye bekle
            
            if self.player.isRunning():
                self.player.terminate()
                self.player.wait(1000)
        
        # Diğer thread'leri kontrol et
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(1000)
        
        event.accept()


# ==================== MAIN ====================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Music Player")
    
    window = MusicPlayer()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()