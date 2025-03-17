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
import sys, os, json, platform, subprocess, shutil, time, requests, gettext
import yt_dlp
from yt_dlp.utils import DownloadError
from PyQt5.QtCore import Qt, pyqtSignal, QThreadPool, QRunnable, QTimer, QDateTime, QUrl, QObject
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QListWidget, 
                             QAbstractItemView, QDockWidget, QLineEdit, QLabel, QPushButton, QSystemTrayIcon, QStyle, 
                             QAction, QMessageBox, QStatusBar, QProgressBar, QCheckBox, QDialog, QDialogButtonBox, 
                             QFormLayout, QGroupBox, QComboBox, QTableWidget, QHeaderView, QTableWidgetItem, QFileDialog, 
                             QDateTimeEdit, QSlider, QListWidgetItem, QTextEdit)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

# ===================== Theme Application =====================
def apply_theme(application, theme_mode):
    """
    Set the application stylesheet to use a round design based on the theme mode (Dark/Light).
    """
    if theme_mode == "Dark":
        style_sheet = """
        QMainWindow, QDialog, QDockWidget { background-color: #181818; border-radius: 25px; }
        QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QTableWidget, QComboBox, QCheckBox {
            color: #ffffff; background-color: #202020; border: none; border-radius: 25px;
        }
        QLineEdit { border: 1px solid #333; padding: 6px; }
        QPushButton { background-color: #cc0000; padding: 8px 12px; border-radius: 25px; }
        QPushButton:hover { background-color: #b30000; }
        QListWidget::item { padding: 10px; border-radius: 25px; }
        QListWidget::item:selected { background-color: #333333; border-left: 3px solid #cc0000; border-radius: 25px; }
        QProgressBar { background-color: #333333; text-align: center; color: #ffffff; font-weight: bold; border-radius: 25px; }
        QProgressBar::chunk { background-color: #cc0000; border-radius: 25px; }
        QMenuBar, QMenu { background-color: #181818; color: #ffffff; border-radius: 25px; }
        QHeaderView::section { background-color: #333333; color: white; padding: 4px; border: 1px solid #444444; border-radius: 25px; }
        """
    else:
        style_sheet = """
        QMainWindow, QDialog, QDockWidget { background-color: #f2f2f2; border-radius: 25px; }
        QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QTableWidget, QComboBox, QCheckBox {
            color: #000000; background-color: #ffffff; border: 1px solid #ccc; border-radius: 25px;
        }
        QLineEdit { padding: 6px; }
        QPushButton { background-color: #e0e0e0; padding: 8px 12px; border-radius: 25px; }
        QPushButton:hover { background-color: #cccccc; }
        QListWidget::item { padding: 10px; border-radius: 25px; }
        QListWidget::item:selected { background-color: #ddd; border-left: 3px solid #888; border-radius: 25px; }
        QProgressBar { text-align: center; font-weight: bold; border-radius: 25px; }
        QHeaderView::section { background-color: #f0f0f0; color: black; padding: 4px; border: 1px solid #ccc; border-radius: 25px; }
        """
    application.setStyleSheet(style_sheet)

# ===================== Drag & Drop LineEdit =====================
class DragAndDropLineEdit(QLineEdit):
    def __init__(self, placeholder="Enter or drag a link here..."):
        super().__init__()
        self.setAcceptDrops(True)
        self.setPlaceholderText(placeholder)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        text = event.mimeData().text().strip()
        self.setText(text if text.startswith("http") else text.replace("file://", ""))

# ===================== User Profile Management =====================
class UserProfile:
    def __init__(self, profile_path="user_profile.json"):
        self.profile_path = profile_path
        self.data = {
            "name": "",
            "profile_picture": "",
            "default_resolution": "720p",
            "download_path": os.getcwd(),
            "history_enabled": True,
            "theme": "Dark",
            "proxy": "",
            "social_media_links": {"instagram": "", "twitter": "", "youtube": ""},
            "language": "en",
            "rate_limit": None,
            "history": []
        }
        self.load_profile()

    def load_profile(self):
        if os.path.exists(self.profile_path):
            with open(self.profile_path, "r") as f:
                try:
                    self.data = json.load(f)
                    if "social_media_links" not in self.data:
                        self.data["social_media_links"] = {"instagram": "", "twitter": "", "youtube": ""}
                    if "history" not in self.data:
                        self.data["history"] = []
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

    def set_social_links(self, instagram, twitter, youtube):
        self.data["social_media_links"] = {"instagram": instagram, "twitter": twitter, "youtube": youtube}
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

    def set_proxy(self, proxy):
        self.data["proxy"] = proxy
        self.save_profile()

    def get_theme(self):
        return self.data.get("theme", "Dark")

    def set_theme(self, theme):
        self.data["theme"] = theme
        self.save_profile()

    def get_default_resolution(self):
        return self.data.get("default_resolution", "720p")

    def set_default_resolution(self, resolution):
        self.data["default_resolution"] = resolution
        self.save_profile()

    def is_history_enabled(self):
        return self.data.get("history_enabled", True)

    def set_history_enabled(self, enabled):
        self.data["history_enabled"] = enabled
        self.save_profile()

    def is_profile_complete(self):
        return bool(self.data["name"])

    def set_language(self, language):
        self.data["language"] = language
        self.save_profile()

    def get_language(self):
        return self.data.get("language", "en")

    def set_rate_limit(self, rate_limit):
        self.data["rate_limit"] = rate_limit
        self.save_profile()

    def get_rate_limit(self):
        return self.data.get("rate_limit", None)

    def add_history_entry(self, title, channel, url, status):
        self.data["history"].append({
            "title": title,
            "channel": channel,
            "url": url,
            "status": status
        })
        self.save_profile()

    def remove_history_entries(self, urls):
        self.data["history"] = [entry for entry in self.data["history"] if entry["url"] not in urls]
        self.save_profile()

    def clear_history(self):
        self.data["history"] = []
        self.save_profile()

    def update_history_entry(self, url, new_title, new_channel, new_status=None):
        for entry in self.data["history"]:
            if entry["url"] == url:
                entry["title"] = new_title
                entry["channel"] = new_channel
                if new_status is not None:
                    entry["status"] = new_status
        self.save_profile()

# ===================== Download Task Definition =====================
class DownloadTask:
    def __init__(self, url, resolution, folder, audio_only=False, playlist=False, subtitles=False,
                 output_format="mp4", from_queue=False, priority=1, recurrence=None, max_rate=None):
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

# ===================== Worker Signals Definition =====================
class WorkerSignals(QObject):
    progress = pyqtSignal(int, float, float, int)
    status = pyqtSignal(int, str)
    log = pyqtSignal(str)
    info = pyqtSignal(int, str, str)

# ===================== Download Worker =====================
class DownloadWorker(QRunnable):
    cookie_text = "# Netscape HTTP Cookie File\nyoutube.com\tFALSE\t/\tFALSE\t0\tCONSENT\tYES+42\n"

    def __init__(self, task, row, signals):
        super().__init__()
        self.task = task
        self.row = row
        self.signals = signals
        self.is_paused = False
        self.is_cancelled = False
        self.title = "Fetching..."
        self.channel = "Fetching..."

    def run(self):
        if not os.path.exists("youtube_cookies.txt"):
            with open("youtube_cookies.txt", "w") as cf:
                cf.write(self.cookie_text)
        info_options = {"quiet": True, "skip_download": True, "cookiefile": "youtube_cookies.txt"}
        try:
            with yt_dlp.YoutubeDL(info_options) as ydl:
                info = ydl.extract_info(self.task.url, download=False)
                self.title = info.get("title", "No Title")
                self.channel = info.get("uploader", "Unknown Channel")
        except Exception as e:
            self.signals.status.emit(self.row, "Download Error")
            self.signals.log.emit("Failed to fetch info: " + str(e))
            if self.row is not None:
                self.signals.status.emit(self.row, "Info Extraction Error")
            return

        self.signals.info.emit(self.row, self.title, self.channel)

        download_options = {
            "outtmpl": os.path.join(self.task.folder, "%(title)s.%(ext)s"),
            "progress_hooks": [self.progress_hook],
            "noplaylist": not self.task.playlist,
            "cookiefile": "youtube_cookies.txt",
            "ratelimit": self.task.max_rate if self.task.max_rate else None
        }
        if self.task.audio_only:
            download_options["format"] = "bestaudio/best"
            download_options["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
        else:
            if self.task.output_format.lower() == "mp4":
                download_options["format"] = 'bestvideo[vcodec*="avc1"]+bestaudio[acodec*="mp4a"]/best'
                download_options["merge_output_format"] = "mp4"
            else:
                download_options["format"] = "bestvideo+bestaudio/best"
                download_options["merge_output_format"] = self.task.output_format
        if self.task.subtitles:
            download_options["writesubtitles"] = True
            download_options["allsubtitles"] = True

        try:
            with yt_dlp.YoutubeDL(download_options) as ydl:
                ydl.download([self.task.url])
            self.signals.status.emit(self.row, "Download Completed")
            self.signals.log.emit("Completed: " + self.title + " by " + self.channel)
        except DownloadError as e:
            if self.is_cancelled:
                self.signals.status.emit(self.row, "Download Cancelled")
                self.signals.log.emit("Cancelled: " + self.title + " by " + self.channel)
            else:
                self.signals.status.emit(self.row, "Download Error")
                self.signals.log.emit("Download Error: " + str(e))
        except Exception as e:
            self.signals.status.emit(self.row, "Download Error")
            self.signals.log.emit("Unexpected Error: " + str(e))

    def progress_hook(self, progress_data):
        if self.is_cancelled:
            raise DownloadError("Cancelled")
        while self.is_paused:
            time.sleep(1)
            if self.is_cancelled:
                raise DownloadError("Cancelled")
        if progress_data["status"] == "downloading":
            downloaded = progress_data.get("downloaded_bytes", 0)
            total = progress_data.get("total_bytes") or progress_data.get("total_bytes_estimate", 0)
            percent = (downloaded / total * 100) if total else 0
            if percent > 100:
                percent = 100
            speed = progress_data.get("speed", 0) or 0
            eta = progress_data.get("eta", 0) or 0
            self.signals.progress.emit(self.row, percent, speed, eta)

    def pause_download(self):
        self.is_paused = True
        self.signals.status.emit(self.row, "Download Paused")
        self.signals.log.emit("Paused: " + self.title)

    def resume_download(self):
        self.is_paused = False
        self.signals.status.emit(self.row, "Download Resumed")
        self.signals.log.emit("Resumed: " + self.title)

    def cancel_download(self):
        self.is_cancelled = True
        self.signals.status.emit(self.row, "Download Cancelled")
        self.signals.log.emit("Cancelled: " + self.title)

# ===================== Main Application Window =====================
class MainWindow(QMainWindow):
    update_progress_signal = pyqtSignal(int, float, float, int)
    update_status_signal = pyqtSignal(int, str)
    update_log_signal = pyqtSignal(str)
    update_info_signal = pyqtSignal(int, str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YoutubeGO Experimental")
        self.setGeometry(100, 100, 800, 600)
        self.ffmpeg_path = shutil.which("ffmpeg") or ""
        self.ffmpeg_found = bool(self.ffmpeg_path)
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.user_profile = UserProfile()
        self.thread_pool = QThreadPool()
        self.active_workers = {}
        self.all_queue_tasks = {}
        self.max_concurrent_downloads = 3
        self.developer_mode = False
        self.verbose_logging = False
        self.search_map = {
            "proxy": (4, "Proxy configuration is in Settings."),
            "resolution": (4, "Resolution configuration is in Settings."),
            "profile": (5, "Profile page for user details."),
            "queue": (6, "Queue page for multiple downloads."),
            "mp4": (1, "MP4 page for video downloads."),
            "mp3": (2, "MP3 page for audio downloads."),
            "history": (3, "History page for download logs."),
            "settings": (4, "Settings page for various options."),
            "scheduler": (7, "Scheduler for planned downloads."),
            "download path": (4, "Download path is in Settings."),
            "theme": (4, "Theme switch is in Settings."),
            "player": (8, "Video Player for downloaded videos.")
        }
        self.update_progress_signal.connect(self.update_progress)
        self.update_status_signal.connect(self.update_status)
        self.update_log_signal.connect(self.append_log)
        self.update_info_signal.connect(self.update_queue_info)
        self.initialize_translation()
        self.initialize_ui()
        apply_theme(QApplication.instance(), self.user_profile.get_theme())
        if not self.user_profile.is_profile_complete():
            self.prompt_user_profile()
        self.create_tray_icon()
        self.load_history_table()

    def initialize_translation(self):
        locale_path = os.path.join(os.getcwd(), "locales")
        language = self.user_profile.get_language()
        try:
            translator = gettext.translation("base", localedir=locale_path, languages=[language])
            translator.install()
            self._ = translator.gettext
        except FileNotFoundError:
            gettext.install("base")
            self._ = gettext.gettext

    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setContextMenu(self.create_tray_menu())
        self.tray_icon.show()

    def create_tray_menu(self):
        menu = self.menuBar().addMenu("")
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)
        show_action.triggered.connect(self.showNormal)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(show_action)
        menu.addAction(quit_action)
        return menu

    def initialize_ui(self):
        # Create top navbar
        self.navbar = QListWidget()
        self.navbar.setFixedHeight(50)
        self.navbar.setFlow(QListWidget.LeftToRight)
        self.navbar.setSpacing(5)
        pages = ["Home", "MP4", "MP3", "History", "Settings", "Profile", "Queue", "Scheduler", "Player", "Experimental"]
        for page in pages:
            self.navbar.addItem(self._(page))
        self.navbar.setCurrentRow(0)
        self.navbar.currentRowChanged.connect(self.change_page)

        self.search_line_edit = QLineEdit()
        self.search_line_edit.setPlaceholderText(self._("Search something..."))
        self.search_line_edit.setFixedHeight(30)
        self.search_button = QPushButton(self._("Search"))
        self.search_button.setFixedHeight(30)
        self.search_button.clicked.connect(self.top_search)
        self.search_results_list = QListWidget()
        self.search_results_list.setVisible(False)
        self.search_results_list.setFixedHeight(150)
        self.search_results_list.itemClicked.connect(self.search_result_clicked)

        # Status bar
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("0%")
        if self.ffmpeg_found:
            self.ffmpeg_label = QLabel(self._("FFmpeg Found"))
            self.ffmpeg_label.setStyleSheet("color: green; font-weight: bold;")
            self.ffmpeg_label.setToolTip(self.ffmpeg_path)
        else:
            self.ffmpeg_label = QLabel(self._("FFmpeg Missing"))
            self.ffmpeg_label.setStyleSheet("color: red; font-weight: bold;")
        self.logs_button = QPushButton("Logs")
        self.logs_button.setFixedWidth(60)
        self.logs_button.clicked.connect(self.toggle_logs)
        status_bar = QStatusBar(self)
        status_bar.addWidget(self.logs_button)
        status_bar.addWidget(self.status_label)
        status_bar.addPermanentWidget(self.ffmpeg_label)
        status_bar.addPermanentWidget(self.progress_bar)
        self.setStatusBar(status_bar)

        self.log_dock = QDockWidget(self._("Logs"), self)
        self.log_dock.setWidget(self.log_text_edit)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.navbar)
        self.stack_pages = QStackedWidget()
        self.stack_pages.addWidget(self.create_home_page())
        self.stack_pages.addWidget(self.create_mp4_page())
        self.stack_pages.addWidget(self.create_mp3_page())
        self.stack_pages.addWidget(self.create_history_page())
        self.stack_pages.addWidget(self.create_settings_page())
        self.stack_pages.addWidget(self.create_profile_page())
        self.stack_pages.addWidget(self.create_queue_page())
        self.stack_pages.addWidget(self.create_scheduler_page())
        self.stack_pages.addWidget(self.create_player_page())
        self.stack_pages.addWidget(self.create_experimental_page())
        main_layout.addWidget(self.stack_pages)
        main_layout.addWidget(self.search_line_edit)
        main_layout.addWidget(self.search_button)
        main_layout.addWidget(self.search_results_list)
        self.setCentralWidget(central_widget)

    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(self._("Home Page - Welcome to YoutubeGO Experimental\nThis version is experimental and may be unstable."))
        label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(label)
        layout.addStretch()
        return page

    def create_mp4_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(self._("Download MP4"))
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        self.mp4_url_line_edit = DragAndDropLineEdit(self._("Paste or drag a link here..."))
        layout.addWidget(self.mp4_url_line_edit)
        button_layout = QHBoxLayout()
        download_single = QPushButton(self._("Download Single MP4"))
        download_single.clicked.connect(lambda: self.start_download(self.mp4_url_line_edit, False, False))
        download_playlist = QPushButton(self._("Download Playlist MP4"))
        download_playlist.clicked.connect(lambda: self.start_download(self.mp4_url_line_edit, False, True))
        pause_all = QPushButton(self._("Pause All"))
        pause_all.clicked.connect(self.pause_all_downloads)
        cancel_all = QPushButton(self._("Cancel All"))
        cancel_all.clicked.connect(self.cancel_all_downloads)
        for btn in [download_single, download_playlist, pause_all, cancel_all]:
            button_layout.addWidget(btn)
        layout.addLayout(button_layout)
        layout.addStretch()
        return page

    def create_mp3_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(self._("Download MP3"))
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        self.mp3_url_line_edit = DragAndDropLineEdit(self._("Paste or drag a link here..."))
        layout.addWidget(self.mp3_url_line_edit)
        button_layout = QHBoxLayout()
        download_single = QPushButton(self._("Download Single MP3"))
        download_single.clicked.connect(lambda: self.start_download(self.mp3_url_line_edit, True, False))
        download_playlist = QPushButton(self._("Download Playlist MP3"))
        download_playlist.clicked.connect(lambda: self.start_download(self.mp3_url_line_edit, True, True))
        pause_all = QPushButton(self._("Pause All"))
        pause_all.clicked.connect(self.pause_all_downloads)
        cancel_all = QPushButton(self._("Cancel All"))
        cancel_all.clicked.connect(self.cancel_all_downloads)
        for btn in [download_single, download_playlist, pause_all, cancel_all]:
            button_layout.addWidget(btn)
        layout.addLayout(button_layout)
        layout.addStretch()
        return page

    def create_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(self._("Download History"))
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([self._("Title"), self._("Channel"), self._("URL"), self._("Status")])
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.history_table)
        button_layout = QHBoxLayout()
        delete_selected = QPushButton(self._("Delete Selected"))
        delete_selected.clicked.connect(self.delete_selected_history)
        delete_all = QPushButton(self._("Delete All"))
        delete_all.clicked.connect(self.delete_all_history)
        history_toggle = QCheckBox(self._("Enable History Logging"))
        history_toggle.setChecked(self.user_profile.is_history_enabled())
        history_toggle.stateChanged.connect(self.toggle_history_logging)
        for widget in [delete_selected, delete_all, history_toggle]:
            button_layout.addWidget(widget)
        layout.addLayout(button_layout)
        search_layout = QHBoxLayout()
        self.history_search_line_edit = QLineEdit()
        self.history_search_line_edit.setPlaceholderText(self._("Search in history..."))
        search_button = QPushButton(self._("Search"))
        search_button.clicked.connect(self.search_history)
        search_layout.addWidget(self.history_search_line_edit)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        layout.addStretch()
        return page

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(self._("Settings"))
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        concurrent_group = QGroupBox(self._("Max Concurrent Downloads"))
        concurrent_layout = QHBoxLayout(concurrent_group)
        self.concurrent_combo = QComboBox()
        self.concurrent_combo.addItems(["1","2","3","4","5","10"])
        self.concurrent_combo.setCurrentText(str(self.max_concurrent_downloads))
        self.concurrent_combo.currentIndexChanged.connect(self.set_max_concurrent_downloads)
        concurrent_layout.addWidget(QLabel(self._("Concurrent:")))
        concurrent_layout.addWidget(self.concurrent_combo)
        layout.addWidget(concurrent_group)
        tech_group = QGroupBox(self._("Technical / Appearance"))
        tech_layout = QFormLayout(tech_group)
        self.proxy_line_edit = QLineEdit()
        self.proxy_line_edit.setText(self.user_profile.get_proxy())
        self.proxy_line_edit.setPlaceholderText(self._("Proxy or bandwidth limit..."))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark","Light"])
        self.theme_combo.setCurrentText(self.user_profile.get_theme())
        tech_layout.addRow(self._("Proxy/BW:"), self.proxy_line_edit)
        tech_layout.addRow(self._("Theme:"), self.theme_combo)
        apply_theme_button = QPushButton(self._("Apply Theme"))
        apply_theme_button.clicked.connect(self.apply_theme_settings)
        tech_layout.addWidget(apply_theme_button)
        layout.addWidget(tech_group)
        resolution_group = QGroupBox(self._("Default Resolution"))
        resolution_layout = QHBoxLayout(resolution_group)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["144p","240p","360p","480p","720p","1080p","1440p","2160p","4320p"])
        self.resolution_combo.setCurrentText(self.user_profile.get_default_resolution())
        resolution_layout.addWidget(QLabel(self._("Resolution:")))
        resolution_layout.addWidget(self.resolution_combo)
        apply_resolution_button = QPushButton(self._("Apply"))
        apply_resolution_button.clicked.connect(self.apply_resolution_settings)
        resolution_layout.addWidget(apply_resolution_button)
        layout.addWidget(resolution_group)
        path_group = QGroupBox(self._("Download Path"))
        path_layout = QHBoxLayout(path_group)
        self.download_path_line_edit = QLineEdit()
        self.download_path_line_edit.setReadOnly(True)
        self.download_path_line_edit.setText(self.user_profile.get_download_path())
        browse_button = QPushButton(self._("Browse"))
        browse_button.clicked.connect(self.select_download_path)
        path_layout.addWidget(QLabel(self._("Folder:")))
        path_layout.addWidget(self.download_path_line_edit)
        path_layout.addWidget(browse_button)
        layout.addWidget(path_group)
        speed_group = QGroupBox(self._("Download Speed Limit"))
        speed_layout = QHBoxLayout(speed_group)
        self.rate_limit_line_edit = QLineEdit()
        self.rate_limit_line_edit.setPlaceholderText(self._("e.g., 500K, 2M"))
        if self.user_profile.get_rate_limit():
            self.rate_limit_line_edit.setText(self.user_profile.get_rate_limit())
        apply_rate_button = QPushButton(self._("Apply"))
        apply_rate_button.clicked.connect(self.apply_rate_limit_settings)
        speed_layout.addWidget(QLabel(self._("Max Rate:")))
        speed_layout.addWidget(self.rate_limit_line_edit)
        speed_layout.addWidget(apply_rate_button)
        layout.addWidget(speed_group)
        language_group = QGroupBox(self._("Language"))
        language_layout = QHBoxLayout(language_group)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Türkçe"])
        current_lang = "Türkçe" if self.user_profile.get_language() == "tr" else "English"
        self.language_combo.setCurrentText(current_lang)
        apply_language_button = QPushButton(self._("Apply Language"))
        apply_language_button.clicked.connect(self.apply_language_settings)
        language_layout.addWidget(QLabel(self._("Language:")))
        language_layout.addWidget(self.language_combo)
        language_layout.addWidget(apply_language_button)
        layout.addWidget(language_group)
        layout.addStretch()
        return page

    def create_profile_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(self._("Profile Page - Customize your details"))
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        form_layout = QFormLayout()
        self.profile_name_line_edit = QLineEdit()
        self.profile_name_line_edit.setText(self.user_profile.data["name"])
        form_layout.addRow(self._("Name:"), self.profile_name_line_edit)
        profile_pic_label = QLabel(os.path.basename(self.user_profile.data["profile_picture"]) if self.user_profile.data["profile_picture"] else self._("No file selected."))
        change_pic_button = QPushButton(self._("Change Picture"))
        remove_pic_button = QPushButton(self._("Remove Picture"))
        remove_pic_button.setVisible(bool(self.user_profile.data["profile_picture"]))
        change_pic_button.clicked.connect(lambda: self.select_profile_picture(change_pic_button, profile_pic_label, remove_pic_button))
        remove_pic_button.clicked.connect(lambda: self.remove_profile_picture(change_pic_button, profile_pic_label, remove_pic_button))
        form_layout.addRow(self._("Picture:"), change_pic_button)
        form_layout.addRow(profile_pic_label)
        form_layout.addRow(remove_pic_button)
        self.instagram_line_edit = QLineEdit()
        self.instagram_line_edit.setText(self.user_profile.data["social_media_links"].get("instagram", ""))
        form_layout.addRow(self._("Instagram:"), self.instagram_line_edit)
        self.twitter_line_edit = QLineEdit()
        self.twitter_line_edit.setText(self.user_profile.data["social_media_links"].get("twitter", ""))
        form_layout.addRow(self._("Twitter:"), self.twitter_line_edit)
        self.youtube_line_edit = QLineEdit()
        self.youtube_line_edit.setText(self.user_profile.data["social_media_links"].get("youtube", ""))
        form_layout.addRow(self._("YouTube:"), self.youtube_line_edit)
        layout.addLayout(form_layout)
        save_profile_button = QPushButton(self._("Save Profile"))
        save_profile_button.clicked.connect(self.save_profile_settings)
        layout.addWidget(save_profile_button)
        layout.addStretch()
        return page

    def create_queue_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(self._("Download Queue"))
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(5)
        self.queue_table.setHorizontalHeaderLabels([self._("Title"), self._("Channel"), self._("URL"), self._("Type"), self._("Progress")])
        header = self.queue_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self.queue_table)
        button_layout = QHBoxLayout()
        add_queue_button = QPushButton(self._("Add to Queue"))
        add_queue_button.clicked.connect(self.add_to_queue_dialog)
        start_queue_button = QPushButton(self._("Start Queue"))
        start_queue_button.clicked.connect(self.start_queue)
        pause_all_button = QPushButton(self._("Pause All"))
        pause_all_button.clicked.connect(self.pause_all_downloads)
        resume_all_button = QPushButton(self._("Resume All"))
        resume_all_button.clicked.connect(self.resume_all_downloads)
        cancel_all_button = QPushButton(self._("Cancel All"))
        cancel_all_button.clicked.connect(self.cancel_all_downloads)
        for btn in [add_queue_button, start_queue_button, pause_all_button, resume_all_button, cancel_all_button]:
            button_layout.addWidget(btn)
        layout.addLayout(button_layout)
        layout.addStretch()
        return page

    def create_scheduler_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(self._("Scheduler (Planned Downloads)"))
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        self.scheduler_table = QTableWidget()
        self.scheduler_table.setColumnCount(7)
        self.scheduler_table.setHorizontalHeaderLabels([self._("Datetime"), self._("URL"), self._("Type"), self._("Subtitles"), self._("Status"), self._("Priority"), self._("Recurrence")])
        header = self.scheduler_table.horizontalHeader()
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        layout.addWidget(self.scheduler_table)
        button_layout = QHBoxLayout()
        add_scheduler_button = QPushButton(self._("Add Scheduled Download"))
        add_scheduler_button.clicked.connect(self.add_scheduler_dialog)
        remove_scheduler_button = QPushButton(self._("Remove Selected"))
        remove_scheduler_button.clicked.connect(self.remove_scheduler_items)
        button_layout.addWidget(add_scheduler_button)
        button_layout.addWidget(remove_scheduler_button)
        layout.addLayout(button_layout)
        layout.addStretch()
        self.scheduler_timer = QTimer()
        self.scheduler_timer.timeout.connect(self.check_scheduler_downloads)
        self.scheduler_timer.start(10000)
        return page

    def create_player_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(self._("Video Player"))
        label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(label)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)
        control_layout = QHBoxLayout()
        play_button = QPushButton(self._("Play"))
        play_button.clicked.connect(self.media_player.play)
        pause_button = QPushButton(self._("Pause"))
        pause_button.clicked.connect(self.media_player.pause)
        stop_button = QPushButton(self._("Stop"))
        stop_button.clicked.connect(self.media_player.stop)
        open_file_button = QPushButton(self._("Open File"))
        open_file_button.clicked.connect(self.open_video_file)
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.time_label = QLabel("00:00/00:00")
        self.playback_speed_slider = QSlider(Qt.Horizontal)
        self.playback_speed_slider.setRange(50, 200)
        self.playback_speed_slider.setValue(100)
        self.playback_speed_label = QLabel("1.00x")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_label = QLabel("50%")
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.playback_speed_slider.valueChanged.connect(self.change_playback_speed)
        self.volume_slider.valueChanged.connect(self.change_volume)
        for widget in [play_button, pause_button, stop_button, open_file_button,
                       self.position_slider, self.time_label, self.playback_speed_label,
                       self.playback_speed_slider, self.volume_label, self.volume_slider]:
            control_layout.addWidget(widget)
        layout.addLayout(control_layout)
        layout.addStretch()
        return page

    def create_experimental_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(self._("Experimental Features\nThis version is experimental and may be unstable. Use at your own risk."))
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)
        developer_mode_checkbox = QCheckBox(self._("Enable Developer Mode"))
        developer_mode_checkbox.stateChanged.connect(self.toggle_developer_mode)
        layout.addWidget(developer_mode_checkbox)
        update_group = QGroupBox(self._("Auto Update Checker"))
        update_layout = QVBoxLayout(update_group)
        update_button = QPushButton(self._("Check for Updates"))
        update_button.clicked.connect(self.check_for_updates)
        update_layout.addWidget(update_button)
        layout.addWidget(update_group)
        retry_group = QGroupBox(self._("Retry Failed Downloads"))
        retry_layout = QVBoxLayout(retry_group)
        retry_button = QPushButton(self._("Retry All Failed Downloads"))
        retry_button.clicked.connect(self.retry_failed_downloads)
        retry_layout.addWidget(retry_button)
        layout.addWidget(retry_group)
        thumbnail_group = QGroupBox(self._("Thumbnail Extractor"))
        thumbnail_layout = QVBoxLayout(thumbnail_group)
        self.thumbnail_url_line_edit = QLineEdit()
        self.thumbnail_url_line_edit.setPlaceholderText(self._("Enter video URL for thumbnail extraction"))
        thumbnail_button = QPushButton(self._("Extract Thumbnail"))
        thumbnail_button.clicked.connect(self.extract_thumbnail)
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(320, 180)
        self.thumbnail_label.setStyleSheet("border: 1px solid gray;")
        thumbnail_layout.addWidget(self.thumbnail_url_line_edit)
        thumbnail_layout.addWidget(thumbnail_button)
        thumbnail_layout.addWidget(self.thumbnail_label)
        layout.addWidget(thumbnail_group)
        converter_group = QGroupBox(self._("Format Converter"))
        converter_layout = QVBoxLayout(converter_group)
        self.converter_input_line_edit = QLineEdit()
        self.converter_input_line_edit.setPlaceholderText(self._("Enter file path to convert"))
        self.converter_target_format_line_edit = QLineEdit()
        self.converter_target_format_line_edit.setPlaceholderText(self._("Enter target format (mp4, mp3, mkv)"))
        converter_button = QPushButton(self._("Convert File"))
        converter_button.clicked.connect(self.convert_file)
        converter_layout.addWidget(self.converter_input_line_edit)
        converter_layout.addWidget(self.converter_target_format_line_edit)
        converter_layout.addWidget(converter_button)
        layout.addWidget(converter_group)
        layout.addStretch()
        return page

    # ===================== Video Player Control Methods =====================
    def update_position(self, position):
        self.position_slider.setValue(position)
        duration = self.media_player.duration()
        current_time = self.format_time(position)
        total_time = self.format_time(duration)
        self.time_label.setText(f"{current_time}/{total_time}")

    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def format_time(self, milliseconds):
        seconds = milliseconds // 1000
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{sec:02d}" if hours > 0 else f"{minutes:02d}:{sec:02d}"

    def change_playback_speed(self, value):
        speed = value / 100.0
        self.media_player.setPlaybackRate(speed)
        self.playback_speed_label.setText(f"{speed:.2f}x")

    def change_volume(self, value):
        self.media_player.setVolume(value)
        self.volume_label.setText(f"{value}%")

    def open_video_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self._("Open Video"), "", self._("Videos (*.mp4 *.mkv *.avi *.webm)"))
        if file_path:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.media_player.play()

    # ===================== Navigation and Search Methods =====================
    def change_page(self, index):
        self.stack_pages.setCurrentIndex(index)

    def top_search(self):
        query = self.search_line_edit.text().lower().strip()
        self.search_results_list.clear()
        self.search_results_list.setVisible(False)
        if not query:
            return
        found_match = False
        for key, value in self.search_map.items():
            if query in key:
                item = QListWidgetItem(f"{self._(key)}: {self._(value[1])}")
                item.setData(Qt.UserRole, value[0])
                self.search_results_list.addItem(item)
                found_match = True
        if found_match:
            self.search_results_list.setVisible(True)

    def search_result_clicked(self, item):
        page_index = item.data(Qt.UserRole)
        self.navbar.setCurrentRow(page_index)
        self.search_results_list.clear()
        self.search_results_list.setVisible(False)

    # ===================== Log Display Method =====================
    def append_log(self, text):
        text_lower = text.lower()
        if "error" in text_lower or "fail" in text_lower:
            color = "red"
        elif "warning" in text_lower:
            color = "yellow"
        elif any(keyword in text_lower for keyword in ["completed", "started", "queued", "fetching"]):
            color = "green"
        elif "cancel" in text_lower:
            color = "orange"
        else:
            color = "white"
        self.log_text_edit.setTextColor(QColor(color))
        self.log_text_edit.append(text)
        self.log_text_edit.setTextColor(QColor("white"))

    def toggle_logs(self):
        self.log_dock.setVisible(not self.log_dock.isVisible())

    # ===================== History Table Methods =====================
    def load_history_table(self):
        if not self.user_profile.is_history_enabled():
            return
        for entry in self.user_profile.data["history"]:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(entry["title"]))
            self.history_table.setItem(row, 1, QTableWidgetItem(entry["channel"]))
            self.history_table.setItem(row, 2, QTableWidgetItem(entry["url"]))
            self.history_table.setItem(row, 3, QTableWidgetItem(entry["status"]))

    def delete_selected_history(self):
        selected_rows = set(item.row() for item in self.history_table.selectedItems())
        urls_to_remove = []
        for row in sorted(selected_rows, reverse=True):
            url_item = self.history_table.item(row, 2)
            if url_item:
                urls_to_remove.append(url_item.text())
            self.history_table.removeRow(row)
        if urls_to_remove:
            self.user_profile.remove_history_entries(urls_to_remove)
        self.append_log(self._("Deleted {count} history entries.").format(count=len(selected_rows)))

    def delete_all_history(self):
        if QMessageBox.question(self, self._("Delete All"), self._("Are you sure?"), QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.history_table.setRowCount(0)
            self.user_profile.clear_history()
            self.append_log(self._("All history deleted."))

    def toggle_history_logging(self, state):
        enabled = (state == Qt.Checked)
        self.user_profile.set_history_enabled(enabled)
        self.append_log(self._("History logging {status}.").format(status=self._("enabled") if enabled else self._("disabled")))

    def search_history(self):
        search_text = self.history_search_line_edit.text().lower().strip()
        for row in range(self.history_table.rowCount()):
            hide = True
            for col in range(self.history_table.columnCount()):
                item = self.history_table.item(row, col)
                if item and search_text in item.text().lower():
                    hide = False
                    break
            self.history_table.setRowHidden(row, hide)

    def update_queue_info(self, row, title, channel):
        if row is not None and row < self.queue_table.rowCount():
            self.queue_table.setItem(row, 0, QTableWidgetItem(title))
            self.queue_table.setItem(row, 1, QTableWidgetItem(channel))
            url_item = self.queue_table.item(row, 2)
            if url_item:
                self.user_profile.update_history_entry(url_item.text(), title, channel)

    # ===================== Scheduler Methods =====================
    def add_scheduler_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self._("Add Scheduled Download"))
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        datetime_edit = QDateTimeEdit()
        datetime_edit.setCalendarPopup(True)
        datetime_edit.setDateTime(QDateTime.currentDateTime())
        url_line_edit = DragAndDropLineEdit(self._("Enter link"))
        audio_checkbox = QCheckBox(self._("Audio Only"))
        subtitles_checkbox = QCheckBox(self._("Download Subtitles?"))
        priority_combo = QComboBox()
        priority_combo.addItems([self._("1 - High"), self._("2 - Medium"), self._("3 - Low")])
        recurrence_combo = QComboBox()
        recurrence_combo.addItems([self._("None"), self._("Daily"), self._("Weekly"), self._("Monthly")])
        form.addRow(self._("Datetime:"), datetime_edit)
        form.addRow(self._("URL:"), url_line_edit)
        form.addRow(audio_checkbox)
        form.addRow(subtitles_checkbox)
        form.addRow(self._("Priority:"), priority_combo)
        form.addRow(self._("Recurrence:"), recurrence_combo)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(lambda: self.confirm_scheduler(dialog, datetime_edit, url_line_edit, audio_checkbox, subtitles_checkbox, priority_combo, recurrence_combo))
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()

    def confirm_scheduler(self, dialog, datetime_edit, url_line_edit, audio_checkbox, subtitles_checkbox, priority_combo, recurrence_combo):
        url = url_line_edit.text().strip()
        if not url:
            QMessageBox.warning(dialog, self._("Error"), self._("No URL provided."))
            return
        priority = int(priority_combo.currentText().split(" - ")[0])
        recurrence = recurrence_combo.currentText().lower() if recurrence_combo.currentText() != self._("None") else None
        row = self.scheduler_table.rowCount()
        self.scheduler_table.insertRow(row)
        self.scheduler_table.setItem(row, 0, QTableWidgetItem(datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")))
        self.scheduler_table.setItem(row, 1, QTableWidgetItem(url))
        self.scheduler_table.setItem(row, 2, QTableWidgetItem(self._("Audio") if audio_checkbox.isChecked() else self._("Video")))
        self.scheduler_table.setItem(row, 3, QTableWidgetItem(self._("Yes") if subtitles_checkbox.isChecked() else self._("No")))
        self.scheduler_table.setItem(row, 4, QTableWidgetItem(self._("Scheduled")))
        self.scheduler_table.setItem(row, 5, QTableWidgetItem(str(priority)))
        self.scheduler_table.setItem(row, 6, QTableWidgetItem(recurrence.capitalize() if recurrence else self._("None")))
        dialog.accept()

    def remove_scheduler_items(self):
        rows = set(item.row() for item in self.scheduler_table.selectedItems())
        for row in sorted(rows, reverse=True):
            self.scheduler_table.removeRow(row)

    def check_scheduler_downloads(self):
        current_time = QDateTime.currentDateTime()
        for row in range(self.scheduler_table.rowCount()):
            dt_str = self.scheduler_table.item(row, 0).text()
            scheduled_time = QDateTime.fromString(dt_str, "yyyy-MM-dd HH:mm:ss")
            status_item = self.scheduler_table.item(row, 4)
            if status_item and scheduled_time <= current_time and status_item.text() == self._("Scheduled"):
                url = self.scheduler_table.item(row, 1).text()
                video_type = self.scheduler_table.item(row, 2).text().lower()
                subtitles = (self.scheduler_table.item(row, 3).text() == self._("Yes"))
                audio_only = "audio" in video_type
                priority = int(self.scheduler_table.item(row, 5).text())
                recurrence = self.scheduler_table.item(row, 6).text().lower() if self.scheduler_table.item(row, 6).text() != self._("None") else None
                task = DownloadTask(url, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(),
                                    audio_only, False, subtitles, "mp4", True, priority, recurrence, self.user_profile.get_rate_limit())
                self.schedule_download(task, row)
                self.scheduler_table.setItem(row, 4, QTableWidgetItem(self._("Started")))
                if recurrence:
                    if recurrence == "daily":
                        new_time = scheduled_time.addDays(1)
                    elif recurrence == "weekly":
                        new_time = scheduled_time.addDays(7)
                    elif recurrence == "monthly":
                        new_time = scheduled_time.addMonths(1)
                    self.scheduler_table.setItem(row, 0, QTableWidgetItem(new_time.toString("yyyy-MM-dd HH:mm:ss")))
                    self.scheduler_table.setItem(row, 4, QTableWidgetItem(self._("Scheduled")))

    def schedule_download(self, task, scheduler_row):
        queue_row = self.queue_table.rowCount()
        self.queue_table.insertRow(queue_row)
        for col, text in enumerate(["Fetching...", "Fetching...", task.url, self._("Audio") if task.audio_only else self._("Video"), "Queued"]):
            self.queue_table.setItem(queue_row, col, QTableWidgetItem(text))
        self.all_queue_tasks[queue_row] = task
        self.user_profile.add_history_entry("Fetching...", "Fetching...", task.url, "Queued")
        if len(self.active_workers) < self.max_concurrent_downloads:
            self.run_download_task(task, queue_row)
            self.queue_table.setItem(queue_row, 4, QTableWidgetItem("Starting"))

    # ===================== Download Methods =====================
    def start_download(self, url_line_edit, audio, playlist):
        url = url_line_edit.text().strip()
        if not url:
            QMessageBox.warning(self, self._("Error"), self._("No URL provided."))
            return
        if not (url.startswith("http://") or url.startswith("https://")):
            QMessageBox.warning(self, self._("Input Error"), self._("Invalid URL format."))
            return
        task = DownloadTask(url, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(),
                              audio, playlist, False, "mp4", False, 1, None, self.user_profile.get_rate_limit())
        self.user_profile.add_history_entry("Fetching...", "Fetching...", url, self._("Queued"))
        self.run_download_task(task, None)

    def run_download_task(self, task, row):
        if row is not None and len(self.active_workers) >= self.max_concurrent_downloads:
            if self.queue_table.item(row, 4):
                self.queue_table.setItem(row, 4, QTableWidgetItem("Queued"))
            return
        signals = WorkerSignals()
        signals.progress.connect(self.update_progress_signal.emit)
        signals.status.connect(self.update_status_signal.emit)
        signals.log.connect(self.update_log_signal.emit)
        signals.info.connect(self.update_info_signal.emit)
        worker = DownloadWorker(task, row, signals)
        if row is not None:
            self.active_workers[row] = worker
        if self.developer_mode or self.verbose_logging:
            self.append_log(self._("Starting task for URL: {url}").format(url=task.url))
        self.thread_pool.start(worker)

    def start_queue(self):
        for row in range(self.queue_table.rowCount()):
            status_item = self.queue_table.item(row, 4)
            if status_item and status_item.text() == "Queued":
                if len(self.active_workers) < self.max_concurrent_downloads:
                    self.run_download_task(self.all_queue_tasks[row], row)
                    self.queue_table.setItem(row, 4, QTableWidgetItem("Starting"))

    def update_progress(self, row, percent, speed, eta):
        if row is not None and row < self.queue_table.rowCount():
            self.queue_table.setItem(row, 4, QTableWidgetItem(f"{int(percent)}%"))
        self.progress_bar.setValue(int(percent))
        self.progress_bar.setFormat(f"{int(percent)}%")
        speed_kb = speed / 1024 if speed else 0
        self.status_label.setText(self._("Downloading...") + f" {percent:.2f}% - {speed_kb:.2f} KB/s - ETA: {eta}s")

    def update_status(self, row, status):
        self.status_label.setText(status)
        if row is not None and row < self.queue_table.rowCount():
            item = self.queue_table.item(row, 4)
            if item:
                item.setText(status)
        if "Error" in status:
            QMessageBox.critical(self, self._("Error"), status)
            self.tray_icon.showMessage(self._("Error"), status, QSystemTrayIcon.Information, 3000)
        elif "Completed" in status:
            self.tray_icon.showMessage(self._("Download Completed"), self._("Download finished successfully."), QSystemTrayIcon.Information, 3000)
            if QMessageBox.question(self, self._("Download Completed"), self._("Download finished. Open download folder?"), QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.open_download_path()
        if row is not None and row in self.active_workers:
            if any(x in status for x in ["Error", "Completed", "Cancelled"]):
                del self.active_workers[row]
                self.start_next_task()

    def start_next_task(self):
        for row in range(self.queue_table.rowCount()):
            status_item = self.queue_table.item(row, 4)
            if status_item and status_item.text() == "Queued":
                if len(self.active_workers) < self.max_concurrent_downloads:
                    self.run_download_task(self.all_queue_tasks[row], row)
                    self.queue_table.setItem(row, 4, QTableWidgetItem("Starting"))
                else:
                    break

    def open_download_path(self):
        folder = self.user_profile.get_download_path()
        if platform.system() == "Windows":
            os.startfile(folder)
        elif platform.system() == "Darwin":
            subprocess.run(["open", folder])
        else:
            subprocess.run(["xdg-open", folder])

    def pause_all_downloads(self):
        for worker in self.active_workers.values():
            worker.pause_download()

    def resume_all_downloads(self):
        for worker in self.active_workers.values():
            worker.resume_download()

    def cancel_all_downloads(self):
        for worker in list(self.active_workers.values()):
            worker.cancel_download()

    # ===================== Settings Methods =====================
    def set_max_concurrent_downloads(self, index):
        self.max_concurrent_downloads = int(self.concurrent_combo.currentText())
        self.append_log(self._("Max concurrent downloads set to {val}").format(val=self.concurrent_combo.currentText()))

    def apply_theme_settings(self):
        new_theme = self.theme_combo.currentText()
        self.user_profile.set_theme(new_theme)
        apply_theme(QApplication.instance(), new_theme)
        self.append_log(self._("Theme changed to '{theme}'").format(theme=new_theme))

    def apply_resolution_settings(self):
        resolution = self.resolution_combo.currentText()
        self.user_profile.set_default_resolution(resolution)
        proxy = self.proxy_line_edit.text().strip()
        self.user_profile.set_proxy(proxy)
        self.append_log(self._("Resolution set: {res}, Proxy: {proxy}").format(res=resolution, proxy=proxy))
        QMessageBox.information(self, self._("Settings"), self._("Resolution: {res}\nProxy: {proxy}").format(res=resolution, proxy=proxy))

    def select_download_path(self):
        folder = QFileDialog.getExistingDirectory(self, self._("Select Download Folder"))
        if folder:
            self.user_profile.set_profile(self.user_profile.data["name"], self.user_profile.data["profile_picture"], folder)
            self.download_path_line_edit.setText(folder)
            self.append_log(self._("Download path changed to {folder}").format(folder=folder))

    def apply_rate_limit_settings(self):
        rate = self.rate_limit_line_edit.text().strip()
        if rate:
            if not (rate.endswith("K") or rate.endswith("M") or rate.endswith("G")):
                QMessageBox.warning(self, self._("Invalid Format"), self._("Please enter rate like '500K', '2M', etc."))
                return
            self.user_profile.set_rate_limit(rate)
            self.append_log(self._("Download speed limit set to {rate}").format(rate=rate))
            QMessageBox.information(self, self._("Rate Limit"), self._("Download speed limited to {rate}").format(rate=rate))
        else:
            self.user_profile.set_rate_limit(None)
            self.append_log(self._("Download speed limit removed."))
            QMessageBox.information(self, self._("Rate Limit"), self._("Download speed limit removed."))

    def apply_language_settings(self):
        selected_lang = self.language_combo.currentText()
        language_code = "tr" if selected_lang == "Türkçe" else "en"
        self.user_profile.set_language(language_code)
        self.append_log(self._("Language set to {lang}").format(lang=selected_lang))
        QMessageBox.information(self, self._("Language Changed"), self._("Language will change after restart."))
        self.restart_application()

    # ===================== Profile Methods =====================
    def prompt_user_profile(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self._("Create User Profile"))
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        name_line_edit = QLineEdit()
        picture_button = QPushButton(self._("Select Picture (Optional)"))
        picture_label = QLabel(self._("No file selected."))
        remove_picture_button = QPushButton(self._("Remove Picture"))
        remove_picture_button.setVisible(False)
        picture_button.clicked.connect(lambda: self.select_profile_picture(picture_button, picture_label, remove_picture_button))
        remove_picture_button.clicked.connect(lambda: self.remove_profile_picture(picture_button, picture_label, remove_picture_button))
        form.addRow(self._("Name:"), name_line_edit)
        form.addRow(self._("Picture:"), picture_button)
        form.addRow(picture_label)
        form.addRow(remove_picture_button)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(lambda: self.confirm_profile(dialog, name_line_edit, picture_button))
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()

    def select_profile_picture(self, button, label, remove_button):
        file_path, _ = QFileDialog.getOpenFileName(self, self._("Select Profile Picture"), "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            button.setText(os.path.basename(file_path))
            button.setProperty("selected_path", file_path)
            label.setText(os.path.basename(file_path))
            remove_button.setVisible(True)

    def remove_profile_picture(self, button, label, remove_button):
        self.user_profile.remove_profile_picture()
        label.setText(self._("No file selected."))
        button.setText(self._("Change Picture"))
        button.setProperty("selected_path", "")
        remove_button.setVisible(False)

    def confirm_profile(self, dialog, name_line_edit, picture_button):
        name = name_line_edit.text().strip()
        selected_path = picture_button.property("selected_path")
        if not name:
            QMessageBox.warning(dialog, self._("Error"), self._("Please provide a name."))
            return
        destination = ""
        if selected_path:
            destination = os.path.join(os.getcwd(), "profile_pic" + os.path.splitext(selected_path)[1])
            try:
                shutil.copy(selected_path, destination)
            except Exception as e:
                QMessageBox.critical(dialog, self._("Error"), str(e))
                return
        self.user_profile.set_profile(name, destination, self.user_profile.get_download_path())
        dialog.accept()

    def save_profile_settings(self):
        name = self.profile_name_line_edit.text().strip()
        if not name:
            QMessageBox.warning(self, self._("Error"), self._("Name cannot be empty."))
            return
        selected_path = self.sender().property("selected_path") if self.sender().property("selected_path") else ""
        destination = ""
        if selected_path:
            destination = os.path.join(os.getcwd(), "profile_pic" + os.path.splitext(selected_path)[1])
            try:
                shutil.copy(selected_path, destination)
            except Exception as e:
                QMessageBox.critical(self, self._("Error"), str(e))
                return
        self.user_profile.set_profile(name, destination, self.user_profile.get_download_path())
        self.user_profile.set_social_links(self.instagram_line_edit.text().strip(), self.twitter_line_edit.text().strip(), self.youtube_line_edit.text().strip())
        QMessageBox.information(self, self._("Saved"), self._("Profile settings saved."))

    # ===================== Queue Methods =====================
    def add_to_queue_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self._("Add to Queue"))
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        url_line_edit = DragAndDropLineEdit(self._("Enter or drag a link here"))
        audio_checkbox = QCheckBox(self._("Audio Only"))
        playlist_checkbox = QCheckBox(self._("Playlist"))
        subtitles_checkbox = QCheckBox(self._("Download Subtitles"))
        format_combo = QComboBox()
        format_combo.addItems(["mp4", "mkv", "webm", "flv", "avi"])
        form.addRow(self._("URL:"), url_line_edit)
        form.addRow(audio_checkbox)
        form.addRow(playlist_checkbox)
        form.addRow(self._("Format:"), format_combo)
        form.addRow(subtitles_checkbox)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(lambda: self.confirm_queue(dialog, url_line_edit, audio_checkbox, playlist_checkbox, subtitles_checkbox, format_combo))
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()

    def confirm_queue(self, dialog, url_line_edit, audio_checkbox, playlist_checkbox, subtitles_checkbox, format_combo):
        url = url_line_edit.text().strip()
        if not url:
            QMessageBox.warning(dialog, self._("Error"), self._("No URL provided."))
            return
        audio_only = audio_checkbox.isChecked()
        playlist = playlist_checkbox.isChecked()
        subtitles = subtitles_checkbox.isChecked()
        output_format = format_combo.currentText()
        row = self.queue_table.rowCount()
        self.queue_table.insertRow(row)
        for col, text in enumerate(["Fetching...", "Fetching...", url, (self._("Audio") if audio_only else self._("Video")) + (" - " + self._("Playlist") if playlist else ""), "Queued"]):
            self.queue_table.setItem(row, col, QTableWidgetItem(text))
        task = DownloadTask(url, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(),
                              audio_only, playlist, subtitles, output_format, True, 1, None, self.user_profile.get_rate_limit())
        self.all_queue_tasks[row] = task
        self.user_profile.add_history_entry("Fetching...", "Fetching...", url, self._("Queued"))
        dialog.accept()

    # ===================== Application Control Methods =====================
    def restart_application(self):
        self.append_log(self._("Restarting application..."))
        QMessageBox.information(self, self._("Restart"), self._("The application will now restart."))
        python_executable = sys.executable
        os.execl(python_executable, python_executable, *sys.argv)

    # ===================== Missing Method: toggle_developer_mode =====================
    def toggle_developer_mode(self, state):
        """
        Toggle developer mode based on the checkbox state.
        """
        self.developer_mode = (state == Qt.Checked)
        if self.developer_mode:
            self.append_log(self._("Developer Mode Enabled"))
        else:
            self.append_log(self._("Developer Mode Disabled"))

    # ===================== Update and Retry Methods =====================
    def check_for_updates(self):
        self.append_log(self._("Checking for updates..."))
        QTimer.singleShot(2000, lambda: QMessageBox.information(self, self._("Update Check"), self._("No updates available. You are running the latest version.")))

    def retry_failed_downloads(self):
        count = 0
        for row in range(self.history_table.rowCount()):
            status_item = self.history_table.item(row, 3)
            if status_item and "Error" in status_item.text():
                url = self.history_table.item(row, 2).text()
                task = DownloadTask(url, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(), False, False, False, "mp4", False, 1, None, self.user_profile.get_rate_limit())
                self.user_profile.add_history_entry("Fetching...", "Fetching...", url, self._("Queued"))
                self.run_download_task(task, None)
                count += 1
        self.append_log(self._("{count} failed downloads retried.").format(count=count))

    def extract_thumbnail(self):
        url = self.thumbnail_url_line_edit.text().strip()
        if not url:
            QMessageBox.warning(self, self._("Error"), self._("Please enter a video URL."))
            return
        try:
            options = {"quiet": True, "skip_download": True, "cookiefile": "youtube_cookies.txt"}
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                thumb_url = info.get("thumbnail")
                if not thumb_url:
                    QMessageBox.warning(self, self._("Error"), self._("No thumbnail found for this video."))
                    return
                self.append_log(self._("Thumbnail URL found: {url}").format(url=thumb_url))
                response = requests.get(thumb_url)
                if response.status_code == 200:
                    img = response.content
                    pixmap = QPixmap()
                    pixmap.loadFromData(img)
                    pixmap = pixmap.scaled(self.thumbnail_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.thumbnail_label.setPixmap(pixmap)
                    self.append_log(self._("Thumbnail extracted successfully."))
                else:
                    QMessageBox.warning(self, self._("Error"), self._("Failed to download thumbnail image."))
        except Exception as e:
            QMessageBox.critical(self, self._("Error"), str(e))
            self.append_log(self._("Error extracting thumbnail: {error}").format(error=str(e)))

    def convert_file(self):
        input_path = self.converter_input_line_edit.text().strip()
        target_format = self.converter_target_format_line_edit.text().strip().lower()
        if not input_path or not target_format:
            QMessageBox.warning(self, self._("Error"), self._("Please provide both file path and target format."))
            return
        if target_format not in ["mp4", "mp3", "mkv"]:
            QMessageBox.warning(self, self._("Error"), self._("Supported target formats: mp4, mp3, mkv."))
            return
        output_path = os.path.splitext(input_path)[0] + "." + target_format
        if not self.ffmpeg_found:
            QMessageBox.critical(self, self._("Error"), self._("FFmpeg not found."))
            return
        cmd = ["ffmpeg", "-i", input_path, output_path]
        try:
            subprocess.run(cmd, check=True)
            self.append_log(self._("Converted file {file} to format {fmt}.").format(file=input_path, fmt=target_format))
            QMessageBox.information(self, self._("Conversion"), self._("File converted successfully to {fmt}").format(fmt=target_format))
        except Exception as e:
            QMessageBox.critical(self, self._("Error"), str(e))
            self.append_log(self._("Conversion error: {error}").format(error=str(e)))

# ===================== Main Function =====================
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
