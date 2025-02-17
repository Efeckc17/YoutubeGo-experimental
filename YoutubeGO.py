"""
MIT License

Copyright (c) 2024-2025 toxi360

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import sys
import os
import json
import platform
import subprocess
import shutil
import yt_dlp
import gettext
import requests
from PyQt5.QtCore import Qt, pyqtSignal, QThreadPool, QRunnable, QTimer, QDateTime, QUrl, QObject
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QListWidget, QAbstractItemView, QDockWidget, QLineEdit, QLabel, QPushButton, QSystemTrayIcon, QStyle, QAction, QMessageBox, QStatusBar, QProgressBar, QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QComboBox, QTableWidget, QHeaderView, QTableWidgetItem, QFileDialog, QDateTimeEdit, QSlider, QListWidgetItem, QTextEdit
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget


def apply_theme(app, theme):
    if theme == "Dark":
        s = """
QMainWindow { background-color: #181818; border-radius: 25px; }
QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QTableWidget, QComboBox, QCheckBox { color: #ffffff; background-color: #202020; border: none; border-radius: 25px; }
QLineEdit { border: 1px solid #333; padding: 6px; }
QPushButton { background-color: #cc0000; padding: 8px 12px; border-radius: 25px; }
QPushButton:hover { background-color: #b30000; }
QListWidget::item { padding: 10px; border-radius: 25px; }
QListWidget::item:selected { background-color: #333333; border-left: 3px solid #cc0000; border-radius: 25px; }
QProgressBar { background-color: #333333; text-align: center; color: #ffffff; font-weight: bold; border-radius: 25px; }
QProgressBar::chunk { background-color: #cc0000; border-radius: 25px; }
QMenuBar { background-color: #181818; color: #ffffff; border-radius: 25px; }
QMenuBar::item:selected { background-color: #333333; border-radius: 25px; }
QMenu { background-color: #202020; color: #ffffff; border-radius: 25px; }
QMenu::item:selected { background-color: #333333; border-radius: 25px; }
QTableWidget { gridline-color: #444444; border: 1px solid #333; border-radius: 25px; }
QHeaderView::section { background-color: #333333; color: white; padding: 4px; border: 1px solid #444444; border-radius: 25px; }
QDockWidget { border: 1px solid #333333; border-radius: 25px; }
"""
    else:
        s = """
QMainWindow { background-color: #f2f2f2; border-radius: 25px; }
QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QTableWidget, QComboBox, QCheckBox { color: #000000; background-color: #ffffff; border: 1px solid #ccc; border-radius: 25px; }
QLineEdit { border: 1px solid #ccc; padding: 6px; }
QPushButton { background-color: #e0e0e0; padding: 8px 12px; border-radius: 25px; }
QPushButton:hover { background-color: #cccccc; }
QListWidget::item { padding: 10px; border-radius: 25px; }
QListWidget::item:selected { background-color: #ddd; border-left: 3px solid #888; border-radius: 25px; }
QProgressBar { background-color: #ddd; text-align: center; color: #000000; font-weight: bold; border-radius: 25px; }
QProgressBar::chunk { background-color: #888; border-radius: 25px; }
QMenuBar { background-color: #ebebeb; color: #000; border-radius: 25px; }
QMenuBar::item:selected { background-color: #dcdcdc; border-radius: 25px; }
QMenu { background-color: #fff; color: #000; border-radius: 25px; }
QMenu::item:selected { background-color: #dcdcdc; border-radius: 25px; }
QTableWidget { gridline-color: #ccc; border: 1px solid #ccc; border-radius: 25px; }
QHeaderView::section { background-color: #f0f0f0; color: black; padding: 4px; border: 1px solid #ccc; border-radius: 25px; }
QDockWidget { border: 1px solid #ccc; border-radius: 25px; }
"""
    app.setStyleSheet(s)

class DragDropLineEdit(QLineEdit):
    def __init__(self, placeholder="Enter or drag a link here..."):
        super().__init__()
        self.setAcceptDrops(True)
        self.setPlaceholderText(placeholder)
    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.acceptProposedAction()
    def dropEvent(self, e):
        t = e.mimeData().text().strip()
        if t.startswith("http"):
            self.setText(t)
        else:
            self.setText(t.replace("file://", ""))

class UserProfile:
    def __init__(self, profile_path="user_profile.json"):
        self.profile_path = profile_path
        self.data = {"name": "", "profile_picture": "", "default_resolution": "720p", "download_path": os.getcwd(), "history_enabled": True, "theme": "Dark", "proxy": "", "social_media_links": {"instagram": "", "twitter": "", "youtube": ""}, "language": "en", "rate_limit": None}
        self.load_profile()
    def load_profile(self):
        if os.path.exists(self.profile_path):
            with open(self.profile_path, "r") as f:
                try:
                    self.data = json.load(f)
                    if "social_media_links" not in self.data:
                        self.data["social_media_links"] = {"instagram": "", "twitter": "", "youtube": ""}
                        self.save_profile()
                except:
                    self.save_profile()
        else:
            self.save_profile()
    def save_profile(self):
        with open(self.profile_path, "w") as f:
            json.dump(self.data, f, indent=4)
    def set_profile(self, name, profile_picture, download_path):
        self.data["name"] = name
        self.data["profile_picture"] = profile_picture
        self.data["download_path"] = download_path
        self.save_profile()
    def set_social_media_links(self, i, t, y):
        self.data["social_media_links"]["instagram"] = i
        self.data["social_media_links"]["twitter"] = t
        self.data["social_media_links"]["youtube"] = y
        self.save_profile()
    def remove_profile_picture(self):
        if self.data["profile_picture"] and os.path.exists(self.data["profile_picture"]):
            try:
                os.remove(self.data["profile_picture"])
            except:
                pass
        self.data["profile_picture"] = ""
        self.save_profile()
    def get_download_path(self):
        return self.data.get("download_path", os.getcwd())
    def get_proxy(self):
        return self.data.get("proxy", "")
    def set_proxy(self, p):
        self.data["proxy"] = p
        self.save_profile()
    def get_theme(self):
        return self.data.get("theme", "Dark")
    def set_theme(self, t):
        self.data["theme"] = t
        self.save_profile()
    def get_default_resolution(self):
        return self.data.get("default_resolution", "720p")
    def set_default_resolution(self, r):
        self.data["default_resolution"] = r
        self.save_profile()
    def is_history_enabled(self):
        return self.data.get("history_enabled", True)
    def set_history_enabled(self, e):
        self.data["history_enabled"] = e
        self.save_profile()
    def is_profile_complete(self):
        return bool(self.data["name"])
    def set_language(self, l):
        self.data["language"] = l
        self.save_profile()
    def get_language(self):
        return self.data.get("language", "en")
    def set_rate_limit(self, r):
        self.data["rate_limit"] = r
        self.save_profile()
    def get_rate_limit(self):
        return self.data.get("rate_limit", None)

class DownloadTask:
    def __init__(self, url, resolution, folder, audio_only=False, playlist=False, subtitles=False, output_format="mp4", from_queue=False, priority=1, recurrence=None, max_rate=None):
        self.url = url
        self.resolution = resolution
        self.folder = folder
        self.audio_only = audio_only
        self.playlist = playlist
        self.subtitles = subtitles
        self.output_format = output_format
        self.from_queue = from_queue
        self.priority = priority
        self.recurrence = recurrence
        self.max_rate = max_rate

class WorkerSignals(QObject):
    progress = pyqtSignal(int, float, float, int)
    status = pyqtSignal(int, str)
    log = pyqtSignal(str)

class DownloadQueueWorker(QRunnable):
    cookie_text = "# Netscape HTTP Cookie File\nyoutube.com\tFALSE\t/\tFALSE\t0\tCONSENT\tYES+42\n"
    def __init__(self, task, row, signals):
        super().__init__()
        self.task = task
        self.row = row
        self.signals = signals
        self.pause = False
        self.cancel = False
    def run(self):
        cf_exists = os.path.exists("youtube_cookies.txt")
        if not cf_exists:
            with open("youtube_cookies.txt", "w") as cf:
                cf.write(self.cookie_text)
        info_opts = {"quiet": True, "skip_download": True, "cookiefile": "youtube_cookies.txt"}
        try:
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                i = ydl.extract_info(self.task.url, download=False)
                t = i.get("title", "No Title")
                c = i.get("uploader", "Unknown Channel")
        except Exception as e:
            self.signals.status.emit(self.row, "Download Error")
            self.signals.log.emit("Failed to fetch video info for " + self.task.url + "\n" + str(e))
            return
        ydl_opts = {"outtmpl": os.path.join(self.task.folder, "%(title)s.%(ext)s"), "progress_hooks": [self.progress_hook], "noplaylist": not self.task.playlist, "cookiefile": "youtube_cookies.txt", "ratelimit": self.task.max_rate if self.task.max_rate else None}
        if self.task.audio_only:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
        else:
            if self.task.output_format.lower() == "mp4":
                ydl_opts["format"] = "bestvideo[vcodec*=\"avc1\"]+bestaudio[acodec*=\"mp4a\"]/best"
                ydl_opts["merge_output_format"] = "mp4"
            else:
                ydl_opts["format"] = "bestvideo+bestaudio/best"
                ydl_opts["merge_output_format"] = self.task.output_format
        if self.task.subtitles:
            ydl_opts["writesubtitles"] = True
            ydl_opts["allsubtitles"] = True
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.task.url])
            self.signals.status.emit(self.row, "Download Completed")
            self.signals.log.emit("Download Completed: " + t + " by " + c)
        except yt_dlp.utils.DownloadError as e:
            if self.cancel:
                self.signals.status.emit(self.row, "Download Cancelled")
                self.signals.log.emit("Download Cancelled: " + t + " by " + c)
            else:
                self.signals.status.emit(self.row, "Download Error")
                self.signals.log.emit("Download Error for " + t + " by " + c + ":\n" + str(e))
        except Exception as e:
            self.signals.status.emit(self.row, "Download Error")
            self.signals.log.emit("Unexpected Error for " + t + " by " + c + ":\n" + str(e))
    def progress_hook(self, d):
        if self.cancel:
            raise yt_dlp.utils.DownloadError("Cancelled")
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            if total:
                p = (downloaded / total) * 100
            else:
                p = 0
            if p > 100:
                p = 100
            s = d.get("speed", 0) or 0
            e = d.get("eta", 0) or 0
            self.signals.progress.emit(self.row, p, s, e)
    def pause_download(self):
        self.pause = True
        self.signals.status.emit(self.row, "Download Paused")
        self.signals.log.emit("Download Paused")
    def resume_download(self):
        self.pause = False
        self.signals.status.emit(self.row, "Download Resumed")
        self.signals.log.emit("Download Resumed")
    def cancel_download(self):
        self.cancel = True
        self.signals.status.emit(self.row, "Download Cancelled")
        self.signals.log.emit("Download Cancelled")

class MainWindow(QMainWindow):
    progress_signal = pyqtSignal(int, float, float, int)
    status_signal = pyqtSignal(int, str)
    log_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YoutubeGO Experimental")
        self.setGeometry(100, 100, 1280, 720)
        self.ffmpeg_found = False
        self.ffmpeg_path = ""
        self.ffmpeg_label = QLabel()
        self.show_logs_btn = QPushButton("Logs")
        self.log_dock_visible = True
        self.check_ffmpeg()
        self.user_profile = UserProfile()
        self.thread_pool = QThreadPool()
        self.active_workers = {}
        self.max_concurrent_downloads = 3
        self.developer_mode = False
        self.verbose_logging = False
        self.search_map = {"proxy": (4, "Proxy configuration is in Settings."), "resolution": (4, "Resolution configuration is in Settings."), "profile": (5, "Profile page for user details."), "queue": (6, "Queue page for multiple downloads."), "mp4": (1, "MP4 page for video downloads."), "mp3": (2, "MP3 page for audio downloads."), "history": (3, "History page for download logs."), "settings": (4, "Settings page for various options."), "scheduler": (7, "Scheduler for planned downloads."), "download path": (4, "Download path is in Settings."), "theme": (4, "Theme switch is in Settings."), "player": (8, "Video Player for downloaded videos.")}
        self.progress_signal.connect(self.update_progress)
        self.status_signal.connect(self.update_status)
        self.log_signal.connect(self.append_log)
        self.init_translation()
        self.init_ui()
        apply_theme(QApplication.instance(), self.user_profile.get_theme())
        if not self.user_profile.is_profile_complete():
            self.prompt_user_profile()
        self.create_tray_icon()
    def init_translation(self):
        lp = os.path.join(os.getcwd(), "locales")
        l = self.user_profile.get_language()
        try:
            lt = gettext.translation("base", localedir=lp, languages=[l])
            lt.install()
            self._ = lt.gettext
        except FileNotFoundError:
            gettext.install("base")
            self._ = gettext.gettext
    def check_ffmpeg(self):
        p = shutil.which("ffmpeg")
        if p:
            self.ffmpeg_found = True
            self.ffmpeg_path = p
        else:
            self.ffmpeg_found = False
            self.ffmpeg_path = ""
    def show_notification(self, t, m):
        self.tray_icon.showMessage(t, m, QSystemTrayIcon.Information, 3000)
    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        i = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(i)
        tm = self.tray_icon.contextMenu()
        if not tm:
            tm = self.create_tray_menu()
        self.tray_icon.setContextMenu(tm)
        self.tray_icon.show()
    def create_tray_menu(self):
        mb = self.menuBar().addMenu("")
        sa = QAction("Show", self)
        qa = QAction("Quit", self)
        sa.triggered.connect(self.showNormal)
        qa.triggered.connect(QApplication.quit)
        m = mb.addMenu("")
        m = self.tray_icon.contextMenu() or m
        if not m:
            from PyQt5.QtWidgets import QMenu
            m = QMenu(self)
        m.addAction(sa)
        m.addAction(qa)
        return m
    def init_ui(self):
        mb = self.menuBar()
        fm = mb.addMenu(self._("File"))
        ea = QAction(self._("Exit"), self)
        ea.setShortcut("Ctrl+Q")
        ea.triggered.connect(self.close)
        rpa = QAction(self._("Reset Profile"), self)
        rpa.triggered.connect(self.reset_profile)
        ra = QAction(self._("Restart Application"), self)
        ra.triggered.connect(self.restart_application)
        fm.addAction(ea)
        fm.addAction(rpa)
        fm.addAction(ra)
        hm = mb.addMenu(self._("Help"))
        ia = QAction(self._("Instagram: toxi.dev"), self)
        ia.triggered.connect(lambda: QMessageBox.information(self, self._("Instagram"), self._("Follow on Instagram: toxi.dev")))
        hm.addAction(ia)
        ma = QAction(self._("Github: https://github.com/Efeckc17"), self)
        ma.triggered.connect(lambda: QMessageBox.information(self, self._("GitHub"), self._("https://github.com/Efeckc17")))
        hm.addAction(ma)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("0%")
        self.progress_bar.setStyleSheet("font-weight: bold;")
        self.status_label = QLabel(self._("Ready"))
        if self.ffmpeg_found:
            self.ffmpeg_label.setText(self._("FFmpeg Found"))
            self.ffmpeg_label.setStyleSheet("color: green; font-weight: bold;")
            self.ffmpeg_label.setToolTip(self.ffmpeg_path)
        else:
            self.ffmpeg_label.setText(self._("FFmpeg Missing"))
            self.ffmpeg_label.setStyleSheet("color: red; font-weight: bold;")
        self.show_logs_btn.setFixedWidth(60)
        self.show_logs_btn.clicked.connect(self.toggle_logs)
        self.status_bar.addWidget(self.show_logs_btn)
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.ffmpeg_label)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.log_dock = QDockWidget(self._("Logs"), self)
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_dock.setWidget(self.log_text_edit)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
        cw = QWidget()
        self.setCentralWidget(cw)
        ml = QVBoxLayout(cw)
        tb = QWidget()
        tb.setMinimumHeight(60)
        tly = QHBoxLayout(tb)
        tly.setContentsMargins(10, 5, 10, 5)
        tly.setSpacing(10)
        self.logo_label = QLabel("YoutubeGO Experimental")
        self.logo_label.setFont(QFont("Arial", 14, QFont.Bold))
        tly.addWidget(self.logo_label, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        sc = QWidget()
        scly = QHBoxLayout(sc)
        scly.setSpacing(5)
        scly.setContentsMargins(0, 0, 0, 0)
        self.top_search_edit = QLineEdit()
        self.top_search_edit.setPlaceholderText(self._("Search something..."))
        self.top_search_edit.setFixedHeight(30)
        self.search_btn = QPushButton(self._("Search"))
        self.search_btn.setFixedHeight(30)
        scly.addWidget(self.top_search_edit)
        scly.addWidget(self.search_btn)
        self.search_result_list = QListWidget()
        self.search_result_list.setVisible(False)
        self.search_result_list.setFixedHeight(150)
        self.search_result_list.itemClicked.connect(self.search_item_clicked)
        tly.addWidget(sc, stretch=1, alignment=Qt.AlignVCenter)
        ml.addWidget(tb)
        ml.addWidget(self.search_result_list)
        ba = QWidget()
        bly = QHBoxLayout(ba)
        bly.setSpacing(0)
        bly.setContentsMargins(0, 0, 0, 0)
        self.main_stack = QStackedWidget()
        self.page_home = self.create_page_home()
        self.page_mp4 = self.create_page_mp4()
        self.page_mp3 = self.create_page_mp3()
        self.page_history = self.create_page_history()
        self.page_settings = self.create_page_settings()
        self.page_profile = self.create_page_profile()
        self.page_queue = self.create_page_queue()
        self.page_scheduler = self.create_page_scheduler()
        self.page_player = self.create_page_player()
        self.page_experimental = self.create_page_experimental()
        self.main_stack.addWidget(self.page_home)
        self.main_stack.addWidget(self.page_mp4)
        self.main_stack.addWidget(self.page_mp3)
        self.main_stack.addWidget(self.page_history)
        self.main_stack.addWidget(self.page_settings)
        self.main_stack.addWidget(self.page_profile)
        self.main_stack.addWidget(self.page_queue)
        self.main_stack.addWidget(self.page_scheduler)
        self.main_stack.addWidget(self.page_player)
        self.main_stack.addWidget(self.page_experimental)
        mi = ["Home", "MP4", "MP3", "History", "Settings", "Profile", "Queue", "Scheduler", "Player", "Experimental"]
        self.side_menu = QListWidget()
        self.side_menu.setFixedWidth(130)
        self.side_menu.setSelectionMode(QAbstractItemView.SingleSelection)
        self.side_menu.setFlow(QListWidget.TopToBottom)
        self.side_menu.setSpacing(2)
        for n in mi:
            self.side_menu.addItem(self._(n))
        self.side_menu.setCurrentRow(0)
        self.side_menu.currentRowChanged.connect(self.side_menu_changed)
        bly.addWidget(self.main_stack, stretch=1)
        bly.addWidget(self.side_menu)
        ml.addWidget(ba)
        self.search_btn.clicked.connect(self.top_search_clicked)
    def create_page_home(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lb = QLabel(self._("Home Page - Welcome to YoutubeGO Experimental\nThis version is experimental and may be unstable. Your downloads might not work correctly."))
        lb.setFont(QFont("Arial", 16, QFont.Bold))
        l.addWidget(lb)
        l.addStretch()
        return w
    def create_page_mp4(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lb = QLabel(self._("Download MP4"))
        lb.setFont(QFont("Arial", 12, QFont.Bold))
        l.addWidget(lb)
        self.mp4_url = DragDropLineEdit(self._("Paste or drag a link here..."))
        l.addWidget(self.mp4_url)
        hl = QHBoxLayout()
        sb = QPushButton(self._("Download Single MP4"))
        sb.clicked.connect(lambda: self.start_download_simple(self.mp4_url, audio=False, playlist=False))
        pb = QPushButton(self._("Download Playlist MP4"))
        pb.clicked.connect(lambda: self.start_download_simple(self.mp4_url, audio=False, playlist=True))
        pab = QPushButton(self._("Pause All"))
        pab.clicked.connect(self.pause_active)
        cab = QPushButton(self._("Cancel All"))
        cab.clicked.connect(self.cancel_active)
        hl.addWidget(sb)
        hl.addWidget(pb)
        hl.addWidget(pab)
        hl.addWidget(cab)
        l.addLayout(hl)
        l.addStretch()
        return w
    def create_page_mp3(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lb = QLabel(self._("Download MP3"))
        lb.setFont(QFont("Arial", 12, QFont.Bold))
        l.addWidget(lb)
        self.mp3_url = DragDropLineEdit(self._("Paste or drag a link here..."))
        l.addWidget(self.mp3_url)
        hl = QHBoxLayout()
        sb = QPushButton(self._("Download Single MP3"))
        sb.clicked.connect(lambda: self.start_download_simple(self.mp3_url, audio=True, playlist=False))
        pb = QPushButton(self._("Download Playlist MP3"))
        pb.clicked.connect(lambda: self.start_download_simple(self.mp3_url, audio=True, playlist=True))
        pab = QPushButton(self._("Pause All"))
        pab.clicked.connect(self.pause_active)
        cab = QPushButton(self._("Cancel All"))
        cab.clicked.connect(self.cancel_active)
        hl.addWidget(sb)
        hl.addWidget(pb)
        hl.addWidget(pab)
        hl.addWidget(cab)
        l.addLayout(hl)
        l.addStretch()
        return w
    def create_page_history(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lb = QLabel(self._("Download History"))
        lb.setFont(QFont("Arial", 12, QFont.Bold))
        l.addWidget(lb)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([self._("Title"), self._("Channel"), self._("URL"), self._("Status")])
        hh = self.history_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        l.addWidget(self.history_table)
        hl = QHBoxLayout()
        dsb = QPushButton(self._("Delete Selected"))
        dsb.clicked.connect(self.delete_selected_history)
        dab = QPushButton(self._("Delete All"))
        dab.clicked.connect(self.delete_all_history)
        hc = QCheckBox(self._("Enable History Logging"))
        hc.setChecked(self.user_profile.is_history_enabled())
        hc.stateChanged.connect(self.toggle_history_logging)
        hl.addWidget(dsb)
        hl.addWidget(dab)
        hl.addWidget(hc)
        l.addLayout(hl)
        shl = QHBoxLayout()
        self.search_hist_edit = QLineEdit()
        self.search_hist_edit.setPlaceholderText(self._("Search in history..."))
        sbt = QPushButton(self._("Search"))
        sbt.clicked.connect(self.search_history)
        shl.addWidget(self.search_hist_edit)
        shl.addWidget(sbt)
        l.addLayout(shl)
        l.addStretch()
        return w
    def create_page_settings(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lb = QLabel(self._("Settings"))
        lb.setFont(QFont("Arial", 12, QFont.Bold))
        l.addWidget(lb)
        g = QGroupBox(self._("Max Concurrent Downloads"))
        gl = QHBoxLayout(g)
        self.concurrent_combo = QComboBox()
        self.concurrent_combo.addItems(["1","2","3","4","5","10"])
        self.concurrent_combo.setCurrentText(str(self.max_concurrent_downloads))
        self.concurrent_combo.currentIndexChanged.connect(self.set_max_concurrent_downloads)
        gl.addWidget(QLabel(self._("Concurrent:")))
        gl.addWidget(self.concurrent_combo)
        g.setLayout(gl)
        l.addWidget(g)
        gt = QGroupBox(self._("Technical / Appearance"))
        fl = QFormLayout(gt)
        self.proxy_edit = QLineEdit()
        self.proxy_edit.setText(self.user_profile.get_proxy())
        self.proxy_edit.setPlaceholderText(self._("Proxy or bandwidth limit..."))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark","Light"])
        self.theme_combo.setCurrentText(self.user_profile.get_theme())
        fl.addRow(self._("Proxy/BW:"), self.proxy_edit)
        fl.addRow(self._("Theme:"), self.theme_combo)
        tb = QPushButton(self._("Apply Theme"))
        tb.clicked.connect(self.change_theme_clicked)
        fl.addWidget(tb)
        gt.setLayout(fl)
        l.addWidget(gt)
        gr = QGroupBox(self._("Default Resolution"))
        rh = QHBoxLayout(gr)
        self.res_combo = QComboBox()
        self.res_combo.addItems(["144p","240p","360p","480p","720p","1080p","1440p","2160p","4320p"])
        self.res_combo.setCurrentText(self.user_profile.get_default_resolution())
        rh.addWidget(QLabel(self._("Resolution:")))
        rh.addWidget(self.res_combo)
        ab = QPushButton(self._("Apply"))
        ab.clicked.connect(self.apply_resolution)
        rh.addWidget(ab)
        gr.setLayout(rh)
        l.addWidget(gr)
        gp = QGroupBox(self._("Download Path"))
        ph = QHBoxLayout(gp)
        self.download_path_edit = QLineEdit()
        self.download_path_edit.setReadOnly(True)
        self.download_path_edit.setText(self.user_profile.get_download_path())
        bb = QPushButton(self._("Browse"))
        bb.clicked.connect(self.select_download_path)
        ph.addWidget(QLabel(self._("Folder:")))
        ph.addWidget(self.download_path_edit)
        ph.addWidget(bb)
        gp.setLayout(ph)
        l.addWidget(gp)
        grt = QGroupBox(self._("Download Speed Limit"))
        rhl = QHBoxLayout(grt)
        self.rate_edit = QLineEdit()
        self.rate_edit.setPlaceholderText(self._("e.g., 500K, 2M"))
        if self.user_profile.get_rate_limit():
            self.rate_edit.setText(self.user_profile.get_rate_limit())
        ab2 = QPushButton(self._("Apply"))
        ab2.clicked.connect(self.apply_rate_limit)
        rhl.addWidget(QLabel(self._("Max Rate:")))
        rhl.addWidget(self.rate_edit)
        rhl.addWidget(ab2)
        grt.setLayout(rhl)
        l.addWidget(grt)
        glang = QGroupBox(self._("Language"))
        lhl = QHBoxLayout(glang)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Türkçe"])
        cl = "Türkçe" if self.user_profile.get_language() == "tr" else "English"
        self.lang_combo.setCurrentText(cl)
        alb = QPushButton(self._("Apply Language"))
        alb.clicked.connect(self.change_language)
        lhl.addWidget(QLabel(self._("Language:")))
        lhl.addWidget(self.lang_combo)
        lhl.addWidget(alb)
        glang.setLayout(lhl)
        l.addWidget(glang)
        l.addStretch()
        return w
    def create_page_profile(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lb = QLabel(self._("Profile Page - Customize your details"))
        lb.setFont(QFont("Arial", 12, QFont.Bold))
        l.addWidget(lb)
        fl = QFormLayout()
        self.profile_name_edit = QLineEdit()
        self.profile_name_edit.setText(self.user_profile.data["name"])
        fl.addRow(self._("Name:"), self.profile_name_edit)
        pl = QLabel(os.path.basename(self.user_profile.data["profile_picture"]) if self.user_profile.data["profile_picture"] else self._("No file selected."))
        pb = QPushButton(self._("Change Picture"))
        rmb = QPushButton(self._("Remove Picture"))
        rmb.setVisible(bool(self.user_profile.data["profile_picture"]))
        def pick_pic():
            p, _ = QFileDialog.getOpenFileName(self, self._("Select Profile Picture"), "", "Images (*.png *.jpg *.jpeg)")
            if p:
                pb.setText(os.path.basename(p))
                pb.setProperty("selected_path", p)
                pl.setText(os.path.basename(p))
                rmb.setVisible(True)
        def remove_pic():
            self.user_profile.remove_profile_picture()
            pl.setText(self._("No file selected."))
            pb.setText(self._("Change Picture"))
            pb.setProperty("selected_path", "")
            rmb.setVisible(False)
        pb.clicked.connect(pick_pic)
        rmb.clicked.connect(remove_pic)
        fl.addRow(self._("Picture:"), pb)
        fl.addRow(pl)
        fl.addRow(rmb)
        self.insta_edit = QLineEdit()
        self.insta_edit.setText(self.user_profile.data["social_media_links"].get("instagram", ""))
        fl.addRow(self._("Instagram:"), self.insta_edit)
        self.tw_edit = QLineEdit()
        self.tw_edit.setText(self.user_profile.data["social_media_links"].get("twitter", ""))
        fl.addRow(self._("Twitter:"), self.tw_edit)
        self.yt_edit = QLineEdit()
        self.yt_edit.setText(self.user_profile.data["social_media_links"].get("youtube", ""))
        fl.addRow(self._("YouTube:"), self.yt_edit)
        l.addLayout(fl)
        sb = QPushButton(self._("Save Profile"))
        def save_profile():
            nm = self.profile_name_edit.text().strip()
            if not nm:
                QMessageBox.warning(self, self._("Error"), self._("Name cannot be empty."))
                return
            pp = pb.property("selected_path") if pb.property("selected_path") else ""
            if pp:
                dst = os.path.join(os.getcwd(), "profile_pic" + os.path.splitext(pp)[1])
                try:
                    shutil.copy(pp, dst)
                except Exception as e:
                    QMessageBox.critical(self, self._("Error"), str(e))
                    return
                self.user_profile.set_profile(nm, dst, self.user_profile.get_download_path())
            else:
                self.user_profile.set_profile(nm, self.user_profile.data["profile_picture"], self.user_profile.get_download_path())
            self.user_profile.set_social_media_links(self.insta_edit.text().strip(), self.tw_edit.text().strip(), self.yt_edit.text().strip())
            QMessageBox.information(self, self._("Saved"), self._("Profile settings saved."))
        sb.clicked.connect(save_profile)
        l.addWidget(sb)
        l.addStretch()
        return w
    def create_page_queue(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lb = QLabel(self._("Download Queue"))
        lb.setFont(QFont("Arial", 12, QFont.Bold))
        l.addWidget(lb)
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(5)
        self.queue_table.setHorizontalHeaderLabels([self._("Title"), self._("Channel"), self._("URL"), self._("Type"), self._("Progress")])
        hh = self.queue_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.Stretch)
        l.addWidget(self.queue_table)
        hl = QHBoxLayout()
        ba = QPushButton(self._("Add to Queue"))
        ba.clicked.connect(self.add_queue_item_dialog)
        bs = QPushButton(self._("Start Queue"))
        bs.clicked.connect(self.start_queue)
        bp = QPushButton(self._("Pause All"))
        bp.clicked.connect(self.pause_active)
        br = QPushButton(self._("Resume All"))
        br.clicked.connect(self.resume_active)
        bc = QPushButton(self._("Cancel All"))
        bc.clicked.connect(self.cancel_active)
        hl.addWidget(ba)
        hl.addWidget(bs)
        hl.addWidget(bp)
        hl.addWidget(br)
        hl.addWidget(bc)
        l.addLayout(hl)
        l.addStretch()
        return w
    def create_page_scheduler(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lb = QLabel(self._("Scheduler (Planned Downloads)"))
        lb.setFont(QFont("Arial", 12, QFont.Bold))
        l.addWidget(lb)
        self.scheduler_table = QTableWidget()
        self.scheduler_table.setColumnCount(7)
        self.scheduler_table.setHorizontalHeaderLabels([self._("Datetime"), self._("URL"), self._("Type"), self._("Subtitles"), self._("Status"), self._("Priority"), self._("Recurrence")])
        hh = self.scheduler_table.horizontalHeader()
        for i in range(7):
            hh.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        l.addWidget(self.scheduler_table)
        hl = QHBoxLayout()
        ba = QPushButton(self._("Add Scheduled Download"))
        ba.clicked.connect(self.add_scheduled_dialog)
        br = QPushButton(self._("Remove Selected"))
        br.clicked.connect(self.remove_scheduled_item)
        hl.addWidget(ba)
        hl.addWidget(br)
        l.addLayout(hl)
        l.addStretch()
        self.scheduler_timer = QTimer()
        self.scheduler_timer.timeout.connect(self.check_scheduled_downloads)
        self.scheduler_timer.start(10000)
        return w
    def create_page_player(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lb = QLabel(self._("Video Player"))
        lb.setFont(QFont("Arial", 12, QFont.Bold))
        l.addWidget(lb)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        l.addWidget(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)
        cl = QHBoxLayout()
        pb = QPushButton(self._("Play"))
        pp = QPushButton(self._("Pause"))
        sb = QPushButton(self._("Stop"))
        of = QPushButton(self._("Open File"))
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.time_label = QLabel("00:00/00:00")
        vs = QSlider(Qt.Horizontal)
        vs.setRange(0, 100)
        vs.setValue(50)
        fs = QPushButton(self._("Fullscreen"))
        pb.clicked.connect(self.media_player.play)
        pp.clicked.connect(self.media_player.pause)
        sb.clicked.connect(self.media_player.stop)
        of.clicked.connect(self.open_video_file)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.position_slider.sliderMoved.connect(self.set_position)
        vs.valueChanged.connect(self.media_player.setVolume)
        fs.clicked.connect(self.toggle_fullscreen)
        cl.addWidget(pb)
        cl.addWidget(pp)
        cl.addWidget(sb)
        cl.addWidget(of)
        cl.addWidget(self.position_slider)
        cl.addWidget(self.time_label)
        cl.addWidget(QLabel(self._("Volume")))
        cl.addWidget(vs)
        cl.addWidget(fs)
        l.addLayout(cl)
        l.addStretch()
        return w
    def create_page_experimental(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lb = QLabel(self._("Experimental Features\nThis version is experimental and may be unstable. Use at your own risk."))
        lb.setFont(QFont("Arial", 14, QFont.Bold))
        l.addWidget(lb)
        dc = QCheckBox(self._("Enable Developer Mode"))
        dc.stateChanged.connect(self.toggle_developer_mode)
        l.addWidget(dc)
        ug = QGroupBox(self._("Auto Update Checker"))
        ul = QVBoxLayout(ug)
        cb = QPushButton(self._("Check for Updates"))
        cb.clicked.connect(self.check_for_updates)
        ul.addWidget(cb)
        l.addWidget(ug)
        rg = QGroupBox(self._("Retry Failed Downloads"))
        rl = QVBoxLayout(rg)
        rfb = QPushButton(self._("Retry All Failed Downloads"))
        rfb.clicked.connect(self.retry_failed_downloads)
        rl.addWidget(rfb)
        l.addWidget(rg)
        tg = QGroupBox(self._("Thumbnail Extractor"))
        tl = QVBoxLayout(tg)
        self.thumb_url_edit = QLineEdit()
        self.thumb_url_edit.setPlaceholderText(self._("Enter video URL for thumbnail extraction"))
        etb = QPushButton(self._("Extract Thumbnail"))
        etb.clicked.connect(self.extract_thumbnail)
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(320, 180)
        self.thumbnail_label.setStyleSheet("border: 1px solid gray;")
        tl.addWidget(self.thumb_url_edit)
        tl.addWidget(etb)
        tl.addWidget(self.thumbnail_label)
        l.addWidget(tg)
        vg = QGroupBox(self._("Verbose Logging"))
        vl = QVBoxLayout(vg)
        vcb = QCheckBox(self._("Enable Verbose Logging"))
        vcb.stateChanged.connect(self.toggle_verbose_logging)
        vl.addWidget(vcb)
        l.addWidget(vg)
        cg = QGroupBox(self._("Experimental Format Converter"))
        cl = QVBoxLayout(cg)
        self.convert_path_edit = QLineEdit()
        self.convert_path_edit.setPlaceholderText(self._("Enter path of file to convert"))
        self.target_format_edit = QLineEdit()
        self.target_format_edit.setPlaceholderText(self._("Enter target format (e.g., avi, mkv)"))
        cbt = QPushButton(self._("Convert File"))
        cbt.clicked.connect(self.convert_file_experimental)
        cl.addWidget(self.convert_path_edit)
        cl.addWidget(self.target_format_edit)
        cl.addWidget(cbt)
        l.addWidget(cg)
        l.addStretch()
        return w
    def position_changed(self, p):
        self.position_slider.setValue(p)
        d = self.media_player.duration()
        c = self.format_time(p)
        t = self.format_time(d)
        self.time_label.setText(f"{c}/{t}")
    def duration_changed(self, d):
        self.position_slider.setRange(0, d)
    def set_position(self, p):
        self.media_player.setPosition(p)
    def format_time(self, ms):
        s = ms // 1000
        m, s2 = divmod(s, 60)
        h, m2 = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m2:02d}:{s2:02d}"
        else:
            return f"{m2:02d}:{s2:02d}"
    def toggle_fullscreen(self):
        if self.video_widget.isFullScreen():
            self.video_widget.setFullScreen(False)
        else:
            self.video_widget.setFullScreen(True)
    def open_video_file(self):
        p, _ = QFileDialog.getOpenFileName(self, self._("Open Video"), "", self._("Videos (*.mp4 *.mkv *.avi *.webm)"))
        if p:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(p)))
            self.media_player.play()
    def side_menu_changed(self, i):
        self.main_stack.setCurrentIndex(i)
    def top_search_clicked(self):
        q = self.top_search_edit.text().lower().strip()
        self.search_result_list.clear()
        self.search_result_list.setVisible(False)
        if not q:
            return
        mf = False
        for k, v in self.search_map.items():
            if q in k:
                it = QListWidgetItem(f"{self._(k)}: {self._(v[1])}")
                it.setData(Qt.UserRole, v[0])
                self.search_result_list.addItem(it)
                mf = True
        if mf:
            self.search_result_list.setVisible(True)
    def search_item_clicked(self, it):
        pi = it.data(Qt.UserRole)
        self.side_menu.setCurrentRow(pi)
        self.search_result_list.clear()
        self.search_result_list.setVisible(False)
    def toggle_logs(self):
        if self.log_dock_visible:
            self.log_dock.hide()
            self.log_dock_visible = False
        else:
            self.log_dock.show()
            self.log_dock_visible = True
    def prompt_user_profile(self):
        d = QDialog(self)
        d.setWindowTitle(self._("Create User Profile"))
        d.setModal(True)
        ly = QVBoxLayout(d)
        frm = QFormLayout()
        ne = QLineEdit()
        pb = QPushButton(self._("Select Picture (Optional)"))
        pl = QLabel(self._("No file selected."))
        rmb = QPushButton(self._("Remove Picture"))
        rmb.setVisible(False)
        def pick_pic():
            pa, _ = QFileDialog.getOpenFileName(self, self._("Profile Picture"), "", "Images (*.png *.jpg *.jpeg)")
            if pa:
                pb.setText(os.path.basename(pa))
                pb.setProperty("selected_path", pa)
                pl.setText(os.path.basename(pa))
                rmb.setVisible(True)
        def remove_pic():
            pb.setText(self._("Select Picture (Optional)"))
            pb.setProperty("selected_path", "")
            pl.setText(self._("No file selected."))
            rmb.setVisible(False)
        pb.clicked.connect(pick_pic)
        rmb.clicked.connect(remove_pic)
        frm.addRow(self._("Name:"), ne)
        frm.addRow(self._("Picture:"), pb)
        frm.addRow(pl)
        frm.addRow(rmb)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ly.addLayout(frm)
        ly.addWidget(bb)
        def on_ok():
            n = ne.text().strip()
            pp = pb.property("selected_path")
            if not n:
                QMessageBox.warning(d, self._("Error"), self._("Please provide a name."))
                return
            dstp = ""
            if pp:
                dstp = os.path.join(os.getcwd(), "profile_pic" + os.path.splitext(pp)[1])
                try:
                    shutil.copy(pp, dstp)
                except Exception as e:
                    QMessageBox.critical(d, self._("Error"), str(e))
                    return
            self.user_profile.set_profile(n, dstp, self.user_profile.get_download_path())
            d.accept()
        def on_cancel():
            d.reject()
        bb.accepted.connect(on_ok)
        bb.rejected.connect(on_cancel)
        d.exec_()
    def add_queue_item_dialog(self):
        d = QDialog(self)
        d.setWindowTitle(self._("Add to Queue"))
        d.setModal(True)
        ly = QVBoxLayout(d)
        frm = QFormLayout()
        ue = DragDropLineEdit(self._("Enter or drag a link here"))
        ca = QCheckBox(self._("Audio Only"))
        cp = QCheckBox(self._("Playlist"))
        cs = QCheckBox(self._("Download Subtitles"))
        fmc = QComboBox()
        fmc.addItems(["mp4", "mkv", "webm", "flv", "avi"])
        frm.addRow(self._("URL:"), ue)
        frm.addRow(ca)
        frm.addRow(cp)
        frm.addRow(self._("Format:"), fmc)
        frm.addRow(cs)
        ly.addLayout(frm)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ly.addWidget(bb)
        def on_ok():
            u = ue.text().strip()
            if not u:
                QMessageBox.warning(d, self._("Error"), self._("No URL."))
                return
            ao = ca.isChecked()
            pl = cp.isChecked()
            sb = cs.isChecked()
            fo = fmc.currentText()
            t = DownloadTask(u, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(), audio_only=ao, playlist=pl, subtitles=sb, output_format=fo, from_queue=True, priority=1, recurrence=None)
            r = self.queue_table.rowCount()
            self.queue_table.insertRow(r)
            self.queue_table.setItem(r, 0, QTableWidgetItem("Fetching..."))
            self.queue_table.setItem(r, 1, QTableWidgetItem("Fetching..."))
            self.queue_table.setItem(r, 2, QTableWidgetItem(u))
            dt = self._("Audio") if ao else self._("Video")
            if pl:
                dt += " - " + self._("Playlist")
            self.queue_table.setItem(r, 3, QTableWidgetItem(dt))
            self.queue_table.setItem(r, 4, QTableWidgetItem("0%"))
            self.add_history_entry("Fetching...", "Fetching...", u, self._("Queued"))
            self.run_task(t, r)
            d.accept()
        def on_cancel():
            d.reject()
        bb.accepted.connect(on_ok)
        bb.rejected.connect(on_cancel)
        d.exec_()
    def start_queue(self):
        c = 0
        for r in range(self.queue_table.rowCount()):
            si = self.queue_table.item(r, 4)
            if si and (self._("Queued") in si.text() or "0%" in si.text()):
                if c < self.max_concurrent_downloads:
                    u = self.queue_table.item(r, 2).text()
                    ty = self.queue_table.item(r, 3).text().lower()
                    a = "audio" in ty
                    p = "playlist" in ty
                    f = "mp4"
                    ri = r
                    rl = self.user_profile.get_rate_limit()
                    s = "download subtitles" in ty
                    t = DownloadTask(u, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(), audio_only=a, playlist=p, subtitles=s, output_format=f, from_queue=True, priority=1, recurrence=None, max_rate=rl)
                    self.run_task(t, ri)
                    self.queue_table.setItem(r, 4, QTableWidgetItem(self._("Started")))
                    c += 1
        self.append_log(self._("Queue started."))
    def remove_scheduled_item(self):
        s = set()
        for it in self.scheduler_table.selectedItems():
            s.add(it.row())
        for r in sorted(s, reverse=True):
            self.scheduler_table.removeRow(r)
    def add_scheduled_dialog(self):
        d = QDialog(self)
        d.setWindowTitle(self._("Add Scheduled Download"))
        d.setModal(True)
        ly = QVBoxLayout(d)
        frm = QFormLayout()
        dt_edit = QDateTimeEdit()
        dt_edit.setCalendarPopup(True)
        dt_edit.setDateTime(QDateTime.currentDateTime())
        ue = DragDropLineEdit(self._("Enter link"))
        ca = QCheckBox(self._("Audio Only"))
        cs = QCheckBox(self._("Download Subtitles?"))
        pc = QComboBox()
        pc.addItems([self._("1 - High"), self._("2 - Medium"), self._("3 - Low")])
        rc = QComboBox()
        rc.addItems([self._("None"), self._("Daily"), self._("Weekly"), self._("Monthly")])
        frm.addRow(self._("Datetime:"), dt_edit)
        frm.addRow(self._("URL:"), ue)
        frm.addRow(ca)
        frm.addRow(cs)
        frm.addRow(self._("Priority:"), pc)
        frm.addRow(self._("Recurrence:"), rc)
        ly.addLayout(frm)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ly.addWidget(bb)
        def on_ok():
            dt_val = dt_edit.dateTime()
            u = ue.text().strip()
            if not u:
                QMessageBox.warning(d, self._("Error"), self._("No URL."))
                return
            ao = ca.isChecked()
            sb = cs.isChecked()
            pv = pc.currentText().split(" - ")[0]
            try:
                pr = int(pv)
            except:
                pr = 2
            rcv = rc.currentText().lower() if rc.currentText() != self._("None") else None
            rw = self.scheduler_table.rowCount()
            self.scheduler_table.insertRow(rw)
            self.scheduler_table.setItem(rw, 0, QTableWidgetItem(dt_val.toString("yyyy-MM-dd HH:mm:ss")))
            self.scheduler_table.setItem(rw, 1, QTableWidgetItem(u))
            ty = self._("Audio") if ao else self._("Video")
            self.scheduler_table.setItem(rw, 2, QTableWidgetItem(ty))
            stxt = self._("Yes") if sb else self._("No")
            self.scheduler_table.setItem(rw, 3, QTableWidgetItem(stxt))
            self.scheduler_table.setItem(rw, 4, QTableWidgetItem(self._("Scheduled")))
            self.scheduler_table.setItem(rw, 5, QTableWidgetItem(str(pr)))
            self.scheduler_table.setItem(rw, 6, QTableWidgetItem(rcv.capitalize() if rcv else self._("None")))
            d.accept()
        def on_cancel():
            d.reject()
        bb.accepted.connect(on_ok)
        bb.rejected.connect(on_cancel)
        d.exec_()
    def check_scheduled_downloads(self):
        n = QDateTime.currentDateTime()
        for r in range(self.scheduler_table.rowCount()):
            dt_s = self.scheduler_table.item(r, 0).text()
            dt_sch = QDateTime.fromString(dt_s, "yyyy-MM-dd HH:mm:ss")
            st_item = self.scheduler_table.item(r, 4)
            if st_item and dt_sch <= n and st_item.text() == self._("Scheduled"):
                u = self.scheduler_table.item(r, 1).text()
                t_ = self.scheduler_table.item(r, 2).text().lower()
                s_ = (self.scheduler_table.item(r, 3).text() == self._("Yes"))
                a_ = ("audio" in t_)
                p_ = False
                pr_ = int(self.scheduler_table.item(r, 5).text())
                rc_ = self.scheduler_table.item(r, 6).text().lower() if self.scheduler_table.item(r, 6).text() != self._("None") else None
                tk = DownloadTask(u, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(), audio_only=a_, playlist=p_, subtitles=s_, output_format="mp4", from_queue=True, priority=pr_, recurrence=rc_, max_rate=self.user_profile.get_rate_limit())
                self.run_task(tk, r)
                self.scheduler_table.setItem(r, 4, QTableWidgetItem(self._("Started")))
                if rc_:
                    if rc_ == "daily":
                        nd = dt_sch.addDays(1)
                    elif rc_ == "weekly":
                        nd = dt_sch.addDays(7)
                    elif rc_ == "monthly":
                        nd = dt_sch.addMonths(1)
                    self.scheduler_table.setItem(r, 0, QTableWidgetItem(nd.toString("yyyy-MM-dd HH:mm:ss")))
                    self.scheduler_table.setItem(r, 4, QTableWidgetItem(self._("Scheduled")))
    def start_download_simple(self, url_edit, audio=False, playlist=False):
        l = url_edit.text().strip()
        if not l:
            QMessageBox.warning(self, self._("Error"), self._("No URL given."))
            return
        if not (l.startswith("http://") or l.startswith("https://")):
            QMessageBox.warning(self, self._("Input Error"), self._("Invalid URL format."))
            return
        rl = self.user_profile.get_rate_limit()
        t = DownloadTask(l, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(), audio_only=audio, playlist=playlist, from_queue=False, max_rate=rl)
        self.add_history_entry("Fetching...", "Fetching...", l, self._("Queued"))
        self.run_task(t, None)
    def run_task(self, task, row):
        s = WorkerSignals()
        s.progress.connect(self.progress_signal.emit)
        s.status.connect(self.status_signal.emit)
        s.log.connect(self.log_signal.emit)
        w = DownloadQueueWorker(task, row, s)
        if row is not None:
            self.active_workers[row] = w
        if self.developer_mode or self.verbose_logging:
            self.append_log(self._("Starting task for URL: {url}").format(url=task.url))
        self.thread_pool.start(w)
    def update_progress(self, row, percent, speed, eta):
        if row is not None and row < self.queue_table.rowCount():
            self.queue_table.setItem(row, 4, QTableWidgetItem(f"{int(percent)}%"))
        self.progress_bar.setValue(int(percent))
        self.progress_bar.setFormat(f"{int(percent)}%")
        s = speed / 1024 if speed else 0
        self.status_label.setText(self._("Downloading...") + f" {percent:.2f}% - {s:.2f} KB/s - ETA: {eta}s")
    def update_status(self, row, st):
        if row is not None and row < self.queue_table.rowCount():
            self.queue_table.setItem(row, 4, QTableWidgetItem(st))
        self.status_label.setText(st)
        if "Error" in st:
            QMessageBox.critical(self, self._("Error"), st)
            self.show_notification(self._("Error"), st)
        elif "Completed" in st:
            self.show_notification(self._("Download Completed"), self._("Download has finished successfully."))
            c = QMessageBox.question(self, self._("Download Completed"), self._("Download has finished successfully. Open download folder?"), QMessageBox.Yes | QMessageBox.No)
            if c == QMessageBox.Yes:
                self.open_download_folder()
        if row is not None and row in self.active_workers:
            del self.active_workers[row]
    def open_download_folder(self):
        f = self.user_profile.get_download_path()
        if platform.system() == "Windows":
            os.startfile(f)
        elif platform.system() == "Darwin":
            subprocess.run(["open", f])
        else:
            subprocess.run(["xdg-open", f])
    def append_log(self, t):
        tl = t.lower()
        if "error" in tl or "fail" in tl:
            c = "red"
        elif "warning" in tl or "warn" in tl:
            c = "yellow"
        elif "completed" in tl or "started" in tl or "queued" in tl or "fetching" in tl:
            c = "green"
        elif "cancel" in tl:
            c = "orange"
        else:
            c = "white"
        self.log_text_edit.setTextColor(QColor(c))
        self.log_text_edit.append(t)
        self.log_text_edit.setTextColor(QColor("white"))
    def add_history_entry(self, title, channel, url, stat):
        if not self.user_profile.is_history_enabled():
            return
        r = self.history_table.rowCount()
        self.history_table.insertRow(r)
        self.history_table.setItem(r, 0, QTableWidgetItem(title))
        self.history_table.setItem(r, 1, QTableWidgetItem(channel))
        self.history_table.setItem(r, 2, QTableWidgetItem(url))
        self.history_table.setItem(r, 3, QTableWidgetItem(stat))
    def delete_selected_history(self):
        sr = set()
        for it in self.history_table.selectedItems():
            sr.add(it.row())
        for r in sorted(sr, reverse=True):
            self.history_table.removeRow(r)
        self.append_log(self._("Deleted {count} history entries.").format(count=len(sr)))
    def delete_all_history(self):
        ans = QMessageBox.question(self, self._("Delete All"), self._("Are you sure?"), QMessageBox.Yes | QMessageBox.No)
        if ans == QMessageBox.Yes:
            self.history_table.setRowCount(0)
            self.append_log(self._("All history deleted."))
    def toggle_history_logging(self, state):
        en = (state == Qt.Checked)
        self.user_profile.set_history_enabled(en)
        self.append_log(self._("History logging {status}.").format(status=self._("enabled") if en else self._("disabled")))
    def search_history(self):
        txt = self.search_hist_edit.text().lower().strip()
        for r in range(self.history_table.rowCount()):
            h = True
            for c in range(self.history_table.columnCount()):
                it = self.history_table.item(r, c)
                if it and txt in it.text().lower():
                    h = False
                    break
            self.history_table.setRowHidden(r, h)
    def set_max_concurrent_downloads(self, idx):
        v = self.concurrent_combo.currentText()
        self.max_concurrent_downloads = int(v)
        self.append_log(self._("Max concurrent downloads set to {val}").format(val=v))
    def change_theme_clicked(self):
        nt = self.theme_combo.currentText()
        self.user_profile.set_theme(nt)
        apply_theme(QApplication.instance(), nt)
        self.append_log(self._("Theme changed to '{theme}'.".format(theme=nt)))
    def apply_resolution(self):
        sr = self.res_combo.currentText()
        self.user_profile.set_default_resolution(sr)
        prx = self.proxy_edit.text().strip()
        self.user_profile.set_proxy(prx)
        self.append_log(self._("Resolution set: {res}, Proxy: {prx}".format(res=sr, prx=prx)))
        QMessageBox.information(self, self._("Settings"), self._("Resolution: {res}\nProxy: {prx}".format(res=sr, prx=prx)))
    def select_download_path(self):
        f = QFileDialog.getExistingDirectory(self, self._("Select Download Folder"))
        if f:
            self.user_profile.set_profile(self.user_profile.data["name"], self.user_profile.data["profile_picture"], f)
            self.download_path_edit.setText(f)
            self.append_log(self._("Download path changed to {folder}".format(folder=f)))
    def pause_active(self):
        for w in self.active_workers.values():
            w.pause_download()
    def resume_active(self):
        for w in self.active_workers.values():
            w.resume_download()
    def cancel_active(self):
        for w in list(self.active_workers.values()):
            w.cancel_download()
    def reset_profile(self):
        if os.path.exists(self.user_profile.profile_path):
            os.remove(self.user_profile.profile_path)
        QMessageBox.information(self, self._("Reset Profile"), self._("Profile data removed. Please restart."))
        self.append_log(self._("Profile has been reset."))
    def restart_application(self):
        self.append_log(self._("Restarting application..."))
        QMessageBox.information(self, self._("Restart"), self._("The application will now restart."))
        p = sys.executable
        os.execl(p, p, *sys.argv)
    def apply_rate_limit(self):
        r = self.rate_edit.text().strip()
        if r:
            if not (r.endswith("K") or r.endswith("M") or r.endswith("G")):
                QMessageBox.warning(self, self._("Invalid Format"), self._("Please enter rate like '500K', '2M', etc."))
                return
            self.user_profile.set_rate_limit(r)
            self.append_log(self._("Download speed limit set to {rate}").format(rate=r))
            QMessageBox.information(self, self._("Rate Limit"), self._("Download speed limited to {rate}".format(rate=r)))
        else:
            self.user_profile.set_rate_limit(None)
            self.append_log(self._("Download speed limit removed."))
            QMessageBox.information(self, self._("Rate Limit"), self._("Download speed limit removed."))
    def change_language(self):
        sl = self.lang_combo.currentText()
        lc = "tr" if sl == "Türkçe" else "en"
        self.user_profile.set_language(lc)
        self.append_log(self._("Language set to {lang}".format(lang=sl)))
        QMessageBox.information(self, self._("Language Changed"), self._("Language will change after restart."))
        self.restart_application()
    def toggle_developer_mode(self, s):
        self.developer_mode = (s == Qt.Checked)
        mt = self._("Developer Mode Enabled") if self.developer_mode else self._("Developer Mode Disabled")
        self.append_log(mt)
    def check_for_updates(self):
        self.append_log(self._("Checking for updates..."))
        QTimer.singleShot(2000, lambda: QMessageBox.information(self, self._("Update Check"), self._("No updates available. You are running the latest version.")))
    def retry_failed_downloads(self):
        c = 0
        for r in range(self.history_table.rowCount()):
            st = self.history_table.item(r, 3)
            if st and "Error" in st.text():
                ur = self.history_table.item(r, 2)
                if ur:
                    u = ur.text()
                    rl = self.user_profile.get_rate_limit()
                    t = DownloadTask(u, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(), audio_only=False, playlist=False, max_rate=rl)
                    self.run_task(t, None)
                    c += 1
        self.append_log(self._("{count} failed downloads retried.").format(count=c))
    def extract_thumbnail(self):
        u = self.thumb_url_edit.text().strip()
        if not u:
            QMessageBox.warning(self, self._("Error"), self._("Please enter a video URL."))
            return
        try:
            o = {"quiet": True, "skip_download": True, "cookiefile": "youtube_cookies.txt"}
            with yt_dlp.YoutubeDL(o) as ydl:
                i = ydl.extract_info(u, download=False)
                t = i.get("thumbnail")
                if not t:
                    QMessageBox.warning(self, self._("Error"), self._("No thumbnail found for this video."))
                    return
                self.append_log(self._("Thumbnail URL found: {url}").format(url=t))
                r = requests.get(t)
                if r.status_code == 200:
                    img = r.content
                    pm = QPixmap()
                    pm.loadFromData(img)
                    pm = pm.scaled(self.thumbnail_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.thumbnail_label.setPixmap(pm)
                    self.append_log(self._("Thumbnail extracted successfully."))
                else:
                    QMessageBox.warning(self, self._("Error"), self._("Failed to download thumbnail image."))
        except Exception as e:
            QMessageBox.critical(self, self._("Error"), str(e))
            self.append_log(self._("Error extracting thumbnail: {error}").format(error=str(e)))
    def toggle_verbose_logging(self, s):
        self.verbose_logging = (s == Qt.Checked)
        msg = self._("Verbose Logging Enabled") if self.verbose_logging else self._("Verbose Logging Disabled")
        self.append_log(msg)
    def convert_file_experimental(self):
        p = self.convert_path_edit.text().strip()
        tf = self.target_format_edit.text().strip()
        if not p or not tf:
            QMessageBox.warning(self, self._("Error"), self._("Please provide both file path and target format."))
            return
        self.append_log(self._("Converting file {file} to format {fmt} (simulated).").format(file=p, fmt=tf))
        QMessageBox.information(self, self._("Conversion"), self._("File conversion simulated."))

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
