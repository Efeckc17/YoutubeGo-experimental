import sys
import os
import json
import platform
import subprocess
import shutil
import yt_dlp
from PyQt5.QtCore import Qt, pyqtSignal, QThreadPool, QRunnable, QTimer, QDateTime, QUrl, QObject
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QListWidget, QAbstractItemView, QDockWidget, QTextEdit, QProgressBar, QStatusBar,
    QMenuBar, QAction, QLabel, QLineEdit, QFileDialog, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QCheckBox, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QDateTimeEdit, QComboBox, QListWidgetItem
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import gettext

class DragDropLineEdit(QLineEdit):
    def __init__(self, placeholder="Enter or drag a link here..."):
        super().__init__()
        self.setAcceptDrops(True)
        self.setPlaceholderText(placeholder)

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.acceptProposedAction()

    def dropEvent(self, e):
        txt = e.mimeData().text().strip()
        if txt.startswith("http"):
            self.setText(txt)
        else:
            self.setText(txt.replace("file://", ""))

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
            "rate_limit": None
        }
        self.load_profile()

    def load_profile(self):
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
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
        with open(self.profile_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def set_profile(self, name, profile_picture, download_path):
        self.data["name"] = name
        self.data["profile_picture"] = profile_picture
        self.data["download_path"] = download_path
        self.save_profile()

    def set_social_media_links(self, insta, tw, yt):
        self.data["social_media_links"]["instagram"] = insta
        self.data["social_media_links"]["twitter"] = tw
        self.data["social_media_links"]["youtube"] = yt
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

    def set_language(self, lang):
        self.data["language"] = lang
        self.save_profile()

    def get_language(self):
        return self.data.get("language", "en")

    def set_rate_limit(self, rate):
        self.data["rate_limit"] = rate
        self.save_profile()

    def get_rate_limit(self):
        return self.data.get("rate_limit", None)

def apply_theme(app, theme):
    if theme == "Dark":
        stylesheet = """
        QMainWindow {
            background-color: #181818;
            border-radius: 20px;
        }
        QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QTableWidget, QComboBox, QCheckBox {
            color: #ffffff;
            background-color: #202020;
            border: none;
            border-radius: 12px;
        }
        QLineEdit {
            border: 1px solid #333;
            padding: 6px;
        }
        QPushButton {
            background-color: #cc0000;
            padding: 8px 12px;
        }
        QPushButton:hover {
            background-color: #b30000;
        }
        QListWidget::item {
            padding: 10px;
        }
        QListWidget::item:selected {
            background-color: #333333;
            border-left: 3px solid #cc0000;
        }
        QProgressBar {
            background-color: #333333;
            text-align: center;
            color: #ffffff;
            font-weight: bold;
            border-radius: 12px;
        }
        QProgressBar::chunk {
            background-color: #cc0000;
            border-radius: 12px;
        }
        QMenuBar {
            background-color: #181818;
            color: #ffffff;
            border-radius: 10px;
        }
        QMenuBar::item:selected {
            background-color: #333333;
        }
        QMenu {
            background-color: #202020;
            color: #ffffff;
            border-radius: 10px;
        }
        QMenu::item:selected {
            background-color: #333333;
        }
        QTableWidget {
            gridline-color: #444444;
            border: 1px solid #333;
            border-radius: 12px;
        }
        QHeaderView::section {
            background-color: #333333;
            color: white;
            padding: 4px;
            border: 1px solid #444444;
            border-radius: 4px;
        }
        QDockWidget {
            border: 1px solid #333333;
            border-radius: 12px;
        }
        """
    else:
        stylesheet = """
        QMainWindow {
            background-color: #f2f2f2;
            border-radius: 20px;
        }
        QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QTableWidget, QComboBox, QCheckBox {
            color: #000000;
            background-color: #ffffff;
            border: 1px solid #ccc;
            border-radius: 12px;
        }
        QLineEdit {
            border: 1px solid #ccc;
            padding: 6px;
        }
        QPushButton {
            background-color: #e0e0e0;
            padding: 8px 12px;
        }
        QPushButton:hover {
            background-color: #cccccc;
        }
        QListWidget::item {
            padding: 10px;
        }
        QListWidget::item:selected {
            background-color: #ddd;
            border-left: 3px solid #888;
        }
        QProgressBar {
            background-color: #ddd;
            text-align: center;
            color: #000000;
            font-weight: bold;
            border-radius: 12px;
        }
        QProgressBar::chunk {
            background-color: #888;
            border-radius: 12px;
        }
        QMenuBar {
            background-color: #ebebeb;
            color: #000;
            border-radius: 10px;
        }
        QMenuBar::item:selected {
            background-color: #dcdcdc;
        }
        QMenu {
            background-color: #fff;
            color: #000;
            border-radius: 10px;
        }
        QMenu::item:selected {
            background-color: #dcdcdc;
        }
        QTableWidget {
            gridline-color: #ccc;
            border: 1px solid #ccc;
            border-radius: 12px;
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            color: black;
            padding: 4px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        QDockWidget {
            border: 1px solid #ccc;
            border-radius: 12px;
        }
        """
    app.setStyleSheet(stylesheet)

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
    progress = pyqtSignal(int, float)
    status = pyqtSignal(int, str)
    log = pyqtSignal(str)

class DownloadQueueWorker(QRunnable):
    def __init__(self, task, row, signals):
        super().__init__()
        self.task = task
        self.row = row
        self.signals = signals
        self.pause = False
        self.cancel = False

    def run(self):
        if not os.path.exists("youtube_cookies.txt"):
            with open("youtube_cookies.txt", "w") as cf:
                cf.write("# Netscape HTTP Cookie File\n# This is a generated cookie file.\nyoutube.com\tFALSE\t/\tFALSE\t0\tCONSENT\tYES+42\n")
        ydl_opts_info = {
            "quiet": True,
            "skip_download": True,
            "cookiefile": "youtube_cookies.txt"
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(self.task.url, download=False)
                title = info.get("title", "No Title")
                channel = info.get("uploader", "Unknown Channel")
        except Exception as e:
            self.signals.status.emit(self.row, "Download Error")
            self.signals.log.emit(f"Failed to fetch video info for {self.task.url}\n{str(e)}")
            return
        ydl_opts_download = {
            "outtmpl": os.path.join(self.task.folder, "%(title)s.%(ext)s"),
            "progress_hooks": [self.progress_hook],
            "noplaylist": not self.task.playlist,
            "cookiefile": "youtube_cookies.txt",
            "ratelimit": self.task.max_rate if self.task.max_rate else None
        }
        if self.task.audio_only:
            ydl_opts_download["format"] = "bestaudio/best"
            ydl_opts_download["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        else:
            if self.task.output_format.lower() == "mp4":
                ydl_opts_download["format"] = "bestvideo[vcodec*=\"avc1\"]+bestaudio[acodec*=\"mp4a\"]/best"
                ydl_opts_download["merge_output_format"] = "mp4"
            else:
                ydl_opts_download["format"] = "bestvideo+bestaudio/best"
                ydl_opts_download["merge_output_format"] = self.task.output_format
        if self.task.subtitles:
            ydl_opts_download["writesubtitles"] = True
            ydl_opts_download["allsubtitles"] = True
        try:
            with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                ydl.download([self.task.url])
            self.signals.status.emit(self.row, "Download Completed")
            self.signals.log.emit(f"Download Completed: {title} by {channel}")
        except yt_dlp.utils.DownloadError as e:
            if self.cancel:
                self.signals.status.emit(self.row, "Download Cancelled")
                self.signals.log.emit(f"Download Cancelled: {title} by {channel}")
            else:
                self.signals.status.emit(self.row, "Download Error")
                self.signals.log.emit(f"Download Error for {title} by {channel}:\n{str(e)}")
        except Exception as e:
            self.signals.status.emit(self.row, "Download Error")
            self.signals.log.emit(f"Unexpected Error for {title} by {channel}:\n{str(e)}")

    def progress_hook(self, d):
        if self.cancel:
            raise yt_dlp.utils.DownloadError("Cancelled")
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            percent = (downloaded / total) * 100 if total else 0
            percent = min(percent, 100)
            self.signals.progress.emit(self.row, percent)

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
    progress_signal = pyqtSignal(int, float)
    status_signal = pyqtSignal(int, str)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YoutubeGO 4.2 - Experimental")
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
        self.progress_signal.connect(self.update_progress)
        self.status_signal.connect(self.update_status)
        self.log_signal.connect(self.append_log)
        self.init_translation()
        self.init_ui()
        apply_theme(QApplication.instance(), self.user_profile.get_theme())
        if not self.user_profile.is_profile_complete():
            self.prompt_user_profile()

    def init_translation(self):
        locale_path = os.path.join(os.getcwd(), "locales")
        lang = self.user_profile.get_language()
        try:
            lang_translation = gettext.translation('base', localedir=locale_path, languages=[lang])
            lang_translation.install()
            self._ = lang_translation.gettext
        except FileNotFoundError:
            gettext.install('base')
            self._ = gettext.gettext

    def check_ffmpeg(self):
        path = shutil.which("ffmpeg")
        if path:
            self.ffmpeg_found = True
            self.ffmpeg_path = path
        else:
            self.ffmpeg_found = False
            self.ffmpeg_path = ""

    def init_ui(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(self._("File"))
        exit_action = QAction(self._("Exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        reset_profile_action = QAction(self._("Reset Profile"), self)
        reset_profile_action.triggered.connect(self.reset_profile)
        restart_action = QAction(self._("Restart Application"), self)
        restart_action.triggered.connect(self.restart_application)
        file_menu.addAction(exit_action)
        file_menu.addAction(reset_profile_action)
        file_menu.addAction(restart_action)
        help_menu = menu_bar.addMenu(self._("Help"))
        insta_action = QAction(self._("Instagram: toxi.dev"), self)
        insta_action.triggered.connect(lambda: QMessageBox.information(self, self._("Instagram"), self._("Follow on Instagram: toxi.dev")))
        help_menu.addAction(insta_action)
        mail_action = QAction(self._("Github: https://github.com/Efeckc17"), self)
        mail_action.triggered.connect(lambda: QMessageBox.information(self, self._("GitHub"), self._("https://github.com/Efeckc17")))
        help_menu.addAction(mail_action)
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
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        top_bar = QWidget()
        top_bar.setMinimumHeight(60)
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(10, 5, 10, 5)
        tb_layout.setSpacing(10)
        self.logo_label = QLabel("YoutubeGO 4.2 - Experimental")
        self.logo_label.setFont(QFont("Arial", 14, QFont.Bold))
        tb_layout.addWidget(self.logo_label, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        search_container = QWidget()
        sc_layout = QHBoxLayout(search_container)
        sc_layout.setSpacing(5)
        sc_layout.setContentsMargins(0, 0, 0, 0)
        self.top_search_edit = QLineEdit()
        self.top_search_edit.setPlaceholderText(self._("Search something..."))
        self.top_search_edit.setFixedHeight(30)
        self.search_btn = QPushButton(self._("Search"))
        self.search_btn.setFixedHeight(30)
        sc_layout.addWidget(self.top_search_edit)
        sc_layout.addWidget(self.search_btn)
        self.search_result_list = QListWidget()
        self.search_result_list.setVisible(False)
        self.search_result_list.setFixedHeight(150)
        self.search_result_list.itemClicked.connect(self.search_item_clicked)
        tb_layout.addWidget(search_container, stretch=1, alignment=Qt.AlignVCenter)
        main_layout.addWidget(top_bar)
        main_layout.addWidget(self.search_result_list)
        bottom_area = QWidget()
        bottom_layout = QHBoxLayout(bottom_area)
        bottom_layout.setSpacing(0)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
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
        self.main_stack.addWidget(self.page_home)
        self.main_stack.addWidget(self.page_mp4)
        self.main_stack.addWidget(self.page_mp3)
        self.main_stack.addWidget(self.page_history)
        self.main_stack.addWidget(self.page_settings)
        self.main_stack.addWidget(self.page_profile)
        self.main_stack.addWidget(self.page_queue)
        self.main_stack.addWidget(self.page_scheduler)
        self.main_stack.addWidget(self.page_player)
        self.side_menu = QListWidget()
        self.side_menu.setFixedWidth(130)
        self.side_menu.setSelectionMode(QAbstractItemView.SingleSelection)
        self.side_menu.setFlow(QListWidget.TopToBottom)
        self.side_menu.setSpacing(2)
        menu_items = ["Home", "MP4", "MP3", "History", "Settings", "Profile", "Queue", "Scheduler", "Player"]
        for item_name in menu_items:
            self.side_menu.addItem(self._(item_name))
        self.side_menu.setCurrentRow(0)
        self.side_menu.currentRowChanged.connect(self.side_menu_changed)
        bottom_layout.addWidget(self.main_stack, stretch=1)
        bottom_layout.addWidget(self.side_menu)
        main_layout.addWidget(bottom_area)
        self.search_btn.clicked.connect(self.top_search_clicked)

    def create_page_home(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel(
            self._("Home Page - Welcome to YoutubeGO 4.2 - Experimental\n\n")
            + self._("New Features:\n")
            + self._("- Automatic cookie usage\n")
            + self._("- Modern rounded UI\n")
            + self._("- Large download fix\n")
            + self._("- In-app video playback\n")
            + self._("- Download speed control\n\n")
            + self._("Github: https://github.com/Efeckc17\n")
            + self._("Instagram: toxi.dev\n")
            + self._("Developed by toxi360 under MIT License")
        )
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(lbl)
        layout.addStretch()
        return w

    def create_page_mp4(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel(self._("Download MP4"))
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.mp4_url = DragDropLineEdit(self._("Paste or drag a link here..."))
        layout.addWidget(self.mp4_url)
        hl = QHBoxLayout()
        single_btn = QPushButton(self._("Download Single MP4"))
        single_btn.clicked.connect(lambda: self.start_download_simple(self.mp4_url, audio=False, playlist=False))
        playlist_btn = QPushButton(self._("Download Playlist MP4"))
        playlist_btn.clicked.connect(lambda: self.start_download_simple(self.mp4_url, audio=False, playlist=True))
        pause_btn = QPushButton(self._("Pause All"))
        pause_btn.clicked.connect(self.pause_active)
        cancel_btn = QPushButton(self._("Cancel All"))
        cancel_btn.clicked.connect(self.cancel_active)
        hl.addWidget(single_btn)
        hl.addWidget(playlist_btn)
        hl.addWidget(pause_btn)
        hl.addWidget(cancel_btn)
        layout.addLayout(hl)
        layout.addStretch()
        return w

    def create_page_mp3(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel(self._("Download MP3"))
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.mp3_url = DragDropLineEdit(self._("Paste or drag a link here..."))
        layout.addWidget(self.mp3_url)
        hl = QHBoxLayout()
        single_btn = QPushButton(self._("Download Single MP3"))
        single_btn.clicked.connect(lambda: self.start_download_simple(self.mp3_url, audio=True, playlist=False))
        playlist_btn = QPushButton(self._("Download Playlist MP3"))
        playlist_btn.clicked.connect(lambda: self.start_download_simple(self.mp3_url, audio=True, playlist=True))
        pause_btn = QPushButton(self._("Pause All"))
        pause_btn.clicked.connect(self.pause_active)
        cancel_btn = QPushButton(self._("Cancel All"))
        cancel_btn.clicked.connect(self.cancel_active)
        hl.addWidget(single_btn)
        hl.addWidget(playlist_btn)
        hl.addWidget(pause_btn)
        hl.addWidget(cancel_btn)
        layout.addLayout(hl)
        layout.addStretch()
        return w

    def create_page_history(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel(self._("Download History"))
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([self._("Title"), self._("Channel"), self._("URL"), self._("Status")])
        hh = self.history_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.history_table)
        hl = QHBoxLayout()
        del_sel_btn = QPushButton(self._("Delete Selected"))
        del_sel_btn.clicked.connect(self.delete_selected_history)
        del_all_btn = QPushButton(self._("Delete All"))
        del_all_btn.clicked.connect(self.delete_all_history)
        hist_ck = QCheckBox(self._("Enable History Logging"))
        hist_ck.setChecked(self.user_profile.is_history_enabled())
        hist_ck.stateChanged.connect(self.toggle_history_logging)
        hl.addWidget(del_sel_btn)
        hl.addWidget(del_all_btn)
        hl.addWidget(hist_ck)
        layout.addLayout(hl)
        s_hl = QHBoxLayout()
        self.search_hist_edit = QLineEdit()
        self.search_hist_edit.setPlaceholderText(self._("Search in history..."))
        s_btn = QPushButton(self._("Search"))
        s_btn.clicked.connect(self.search_history)
        s_hl.addWidget(self.search_hist_edit)
        s_hl.addWidget(s_btn)
        layout.addLayout(s_hl)
        layout.addStretch()
        return w

    def create_page_settings(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel(self._("Settings"))
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        g_con = QGroupBox(self._("Max Concurrent Downloads"))
        g_layout = QHBoxLayout(g_con)
        self.concurrent_combo = QComboBox()
        self.concurrent_combo.addItems(["1","2","3","4","5","10"])
        self.concurrent_combo.setCurrentText(str(self.max_concurrent_downloads))
        self.concurrent_combo.currentIndexChanged.connect(self.set_max_concurrent_downloads)
        g_layout.addWidget(QLabel(self._("Concurrent:")))
        g_layout.addWidget(self.concurrent_combo)
        g_con.setLayout(g_layout)
        layout.addWidget(g_con)
        g_tech = QGroupBox(self._("Technical / Appearance"))
        fl = QFormLayout(g_tech)
        self.proxy_edit = QLineEdit()
        self.proxy_edit.setText(self.user_profile.get_proxy())
        self.proxy_edit.setPlaceholderText(self._("Proxy or bandwidth limit..."))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark","Light"])
        self.theme_combo.setCurrentText(self.user_profile.get_theme())
        fl.addRow(self._("Proxy/BW:"), self.proxy_edit)
        fl.addRow(self._("Theme:"), self.theme_combo)
        theme_btn = QPushButton(self._("Apply Theme"))
        theme_btn.clicked.connect(self.change_theme_clicked)
        fl.addWidget(theme_btn)
        g_tech.setLayout(fl)
        layout.addWidget(g_tech)
        g_res = QGroupBox(self._("Default Resolution"))
        r_hl = QHBoxLayout(g_res)
        self.res_combo = QComboBox()
        self.res_combo.addItems(["144p","240p","360p","480p","720p","1080p","1440p","2160p","4320p"])
        self.res_combo.setCurrentText(self.user_profile.get_default_resolution())
        r_hl.addWidget(QLabel(self._("Resolution:")))
        r_hl.addWidget(self.res_combo)
        a_btn = QPushButton(self._("Apply"))
        a_btn.clicked.connect(self.apply_resolution)
        r_hl.addWidget(a_btn)
        g_res.setLayout(r_hl)
        layout.addWidget(g_res)
        g_path = QGroupBox(self._("Download Path"))
        p_hl = QHBoxLayout(g_path)
        self.download_path_edit = QLineEdit()
        self.download_path_edit.setReadOnly(True)
        self.download_path_edit.setText(self.user_profile.get_download_path())
        b_br = QPushButton(self._("Browse"))
        b_br.clicked.connect(self.select_download_path)
        p_hl.addWidget(QLabel(self._("Folder:")))
        p_hl.addWidget(self.download_path_edit)
        p_hl.addWidget(b_br)
        g_path.setLayout(p_hl)
        layout.addWidget(g_path)
        g_rate = QGroupBox(self._("Download Speed Limit"))
        r_hl_rate = QHBoxLayout(g_rate)
        self.rate_edit = QLineEdit()
        self.rate_edit.setPlaceholderText(self._("e.g., 500K, 2M"))
        self.rate_edit.setText(self.user_profile.get_rate_limit() if self.user_profile.get_rate_limit() else "")
        apply_rate_btn = QPushButton(self._("Apply"))
        apply_rate_btn.clicked.connect(self.apply_rate_limit)
        r_hl_rate.addWidget(QLabel(self._("Max Rate:")))
        r_hl_rate.addWidget(self.rate_edit)
        r_hl_rate.addWidget(apply_rate_btn)
        g_rate.setLayout(r_hl_rate)
        layout.addWidget(g_rate)
        g_lang = QGroupBox(self._("Language"))
        lang_layout = QHBoxLayout(g_lang)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Türkçe"])
        current_lang = "Türkçe" if self.user_profile.get_language() == "tr" else "English"
        self.lang_combo.setCurrentText(current_lang)
        apply_lang_btn = QPushButton(self._("Apply Language"))
        apply_lang_btn.clicked.connect(self.change_language)
        lang_layout.addWidget(QLabel(self._("Language:")))
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addWidget(apply_lang_btn)
        g_lang.setLayout(lang_layout)
        layout.addWidget(g_lang)
        layout.addStretch()
        return w

    def create_page_profile(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel(self._("Profile Page - Customize your details"))
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        form_layout = QFormLayout()
        self.profile_name_edit = QLineEdit()
        self.profile_name_edit.setText(self.user_profile.data["name"])
        form_layout.addRow(self._("Name:"), self.profile_name_edit)
        pic_label = QLabel(
            os.path.basename(self.user_profile.data["profile_picture"]) if self.user_profile.data["profile_picture"] else self._("No file selected.")
        )
        pic_btn = QPushButton(self._("Change Picture"))
        remove_pic_btn = QPushButton(self._("Remove Picture"))
        remove_pic_btn.setVisible(bool(self.user_profile.data["profile_picture"]))
        def pick_pic():
            path, _ = QFileDialog.getOpenFileName(self, self._("Select Profile Picture"), "", "Images (*.png *.jpg *.jpeg)")
            if path:
                pic_btn.setText(os.path.basename(path))
                pic_btn.setProperty("selected_path", path)
                pic_label.setText(os.path.basename(path))
                remove_pic_btn.setVisible(True)
        def remove_pic():
            self.user_profile.remove_profile_picture()
            pic_label.setText(self._("No file selected."))
            pic_btn.setText(self._("Change Picture"))
            pic_btn.setProperty("selected_path", "")
            remove_pic_btn.setVisible(False)
        pic_btn.clicked.connect(pick_pic)
        remove_pic_btn.clicked.connect(remove_pic)
        form_layout.addRow(self._("Picture:"), pic_btn)
        form_layout.addRow(pic_label)
        form_layout.addRow(remove_pic_btn)
        self.insta_edit = QLineEdit()
        self.insta_edit.setText(self.user_profile.data["social_media_links"].get("instagram", ""))
        form_layout.addRow(self._("Instagram:"), self.insta_edit)
        self.tw_edit = QLineEdit()
        self.tw_edit.setText(self.user_profile.data["social_media_links"].get("twitter", ""))
        form_layout.addRow(self._("Twitter:"), self.tw_edit)
        self.yt_edit = QLineEdit()
        self.yt_edit.setText(self.user_profile.data["social_media_links"].get("youtube", ""))
        form_layout.addRow(self._("YouTube:"), self.yt_edit)
        layout.addLayout(form_layout)
        save_btn = QPushButton(self._("Save Profile"))
        def save_profile():
            name = self.profile_name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, self._("Error"), self._("Name cannot be empty."))
                return
            pic_path = pic_btn.property("selected_path") if pic_btn.property("selected_path") else ""
            if pic_path:
                dest_pic = os.path.join(os.getcwd(), "profile_pic" + os.path.splitext(pic_path)[1])
                try:
                    shutil.copy(pic_path, dest_pic)
                except Exception as e:
                    QMessageBox.critical(self, self._("Error"), str(e))
                    return
                self.user_profile.set_profile(name, dest_pic, self.user_profile.get_download_path())
            else:
                self.user_profile.set_profile(name, self.user_profile.data["profile_picture"], self.user_profile.get_download_path())
            self.user_profile.set_social_media_links(
                self.insta_edit.text().strip(),
                self.tw_edit.text().strip(),
                self.yt_edit.text().strip()
            )
            QMessageBox.information(self, self._("Saved"), self._("Profile settings saved."))
        save_btn.clicked.connect(save_profile)
        layout.addWidget(save_btn)
        layout.addStretch()
        return w

    def create_page_queue(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel(self._("Download Queue"))
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(5)
        self.queue_table.setHorizontalHeaderLabels([self._("Title"), self._("Channel"), self._("URL"), self._("Type"), self._("Progress")])
        hh = self.queue_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self.queue_table)
        hl = QHBoxLayout()
        b_add = QPushButton(self._("Add to Queue"))
        b_add.clicked.connect(self.add_queue_item_dialog)
        b_start = QPushButton(self._("Start Queue"))
        b_start.clicked.connect(self.start_queue)
        b_pause = QPushButton(self._("Pause All"))
        b_pause.clicked.connect(self.pause_active)
        b_resume = QPushButton(self._("Resume All"))
        b_resume.clicked.connect(self.resume_active)
        b_cancel = QPushButton(self._("Cancel All"))
        b_cancel.clicked.connect(self.cancel_active)
        hl.addWidget(b_add)
        hl.addWidget(b_start)
        hl.addWidget(b_pause)
        hl.addWidget(b_resume)
        hl.addWidget(b_cancel)
        layout.addLayout(hl)
        layout.addStretch()
        return w

    def create_page_scheduler(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel(self._("Scheduler (Planned Downloads)"))
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.scheduler_table = QTableWidget()
        self.scheduler_table.setColumnCount(7)
        self.scheduler_table.setHorizontalHeaderLabels([self._("Datetime"), self._("URL"), self._("Type"), self._("Subtitles"), self._("Status"), self._("Priority"), self._("Recurrence")])
        hh = self.scheduler_table.horizontalHeader()
        for i in range(7):
            hh.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        layout.addWidget(self.scheduler_table)
        hl = QHBoxLayout()
        b_add = QPushButton(self._("Add Scheduled Download"))
        b_add.clicked.connect(self.add_scheduled_dialog)
        b_remove = QPushButton(self._("Remove Selected"))
        b_remove.clicked.connect(self.remove_scheduled_item)
        hl.addWidget(b_add)
        hl.addWidget(b_remove)
        layout.addLayout(hl)
        layout.addStretch()
        self.scheduler_timer = QTimer()
        self.scheduler_timer.timeout.connect(self.check_scheduled_downloads)
        self.scheduler_timer.start(10000)
        return w

    def create_page_player(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel(self._("Video Player"))
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)
        control_layout = QHBoxLayout()
        play_btn = QPushButton(self._("Play"))
        pause_btn = QPushButton(self._("Pause"))
        stop_btn = QPushButton(self._("Stop"))
        open_btn = QPushButton(self._("Open File"))
        play_btn.clicked.connect(self.media_player.play)
        pause_btn.clicked.connect(self.media_player.pause)
        stop_btn.clicked.connect(self.media_player.stop)
        open_btn.clicked.connect(self.open_video_file)
        control_layout.addWidget(play_btn)
        control_layout.addWidget(pause_btn)
        control_layout.addWidget(stop_btn)
        control_layout.addWidget(open_btn)
        layout.addLayout(control_layout)
        layout.addStretch()
        return w

    def open_video_file(self):
        path, _ = QFileDialog.getOpenFileName(self, self._("Open Video"), "", self._("Videos (*.mp4 *.mkv *.avi *.webm)"))
        if path:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.media_player.play()

    def side_menu_changed(self, index):
        self.main_stack.setCurrentIndex(index)

    def top_search_clicked(self):
        query = self.top_search_edit.text().lower().strip()
        self.search_result_list.clear()
        self.search_result_list.setVisible(False)
        if not query:
            return
        matches_found = False
        for k, v in self.search_map.items():
            if query in k:
                item = QListWidgetItem(f"{self._(k)}: {self._(v[1])}")
                item.setData(Qt.UserRole, v[0])
                self.search_result_list.addItem(item)
                matches_found = True
        if matches_found:
            self.search_result_list.setVisible(True)

    def search_item_clicked(self, item):
        page_index = item.data(Qt.UserRole)
        self.side_menu.setCurrentRow(page_index)
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
        dialog = QDialog(self)
        dialog.setWindowTitle(self._("Create User Profile"))
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        frm = QFormLayout()
        name_edit = QLineEdit()
        pic_btn = QPushButton(self._("Select Picture (Optional)"))
        pic_label = QLabel(self._("No file selected."))
        remove_pic_btn = QPushButton(self._("Remove Picture"))
        remove_pic_btn.setVisible(False)
        def pick_pic():
            path, _ = QFileDialog.getOpenFileName(self, self._("Profile Picture"), "", "Images (*.png *.jpg *.jpeg)")
            if path:
                pic_btn.setText(os.path.basename(path))
                pic_btn.setProperty("selected_path", path)
                pic_label.setText(os.path.basename(path))
                remove_pic_btn.setVisible(True)
        def remove_pic():
            pic_btn.setText(self._("Select Picture (Optional)"))
            pic_btn.setProperty("selected_path", "")
            pic_label.setText(self._("No file selected."))
            remove_pic_btn.setVisible(False)
        pic_btn.clicked.connect(pick_pic)
        remove_pic_btn.clicked.connect(remove_pic)
        frm.addRow(self._("Name:"), name_edit)
        frm.addRow(self._("Picture:"), pic_btn)
        frm.addRow(pic_label)
        frm.addRow(remove_pic_btn)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addLayout(frm)
        layout.addWidget(bb)
        def on_ok():
            nm = name_edit.text().strip()
            pp = pic_btn.property("selected_path")
            if not nm:
                QMessageBox.warning(dialog, self._("Error"), self._("Please provide a name."))
                return
            dest_pic = ""
            if pp:
                dest_pic = os.path.join(os.getcwd(), "profile_pic" + os.path.splitext(pp)[1])
                try:
                    shutil.copy(pp, dest_pic)
                except Exception as e:
                    QMessageBox.critical(dialog, self._("Error"), str(e))
                    return
            self.user_profile.set_profile(nm, dest_pic, self.user_profile.get_download_path())
            dialog.accept()
        def on_cancel():
            dialog.reject()
        bb.accepted.connect(on_ok)
        bb.rejected.connect(on_cancel)
        dialog.exec_()

    def add_queue_item_dialog(self):
        d = QDialog(self)
        d.setWindowTitle(self._("Add to Queue"))
        d.setModal(True)
        ly = QVBoxLayout(d)
        frm = QFormLayout()
        url_edit = DragDropLineEdit(self._("Enter or drag a link here"))
        c_audio = QCheckBox(self._("Audio Only"))
        c_pl = QCheckBox(self._("Playlist"))
        c_subs = QCheckBox(self._("Download Subtitles"))
        fmt_combo = QComboBox()
        fmt_combo.addItems(["mp4","mkv","webm","flv","avi"])
        frm.addRow(self._("URL:"), url_edit)
        frm.addRow(c_audio)
        frm.addRow(c_pl)
        frm.addRow(self._("Format:"), fmt_combo)
        frm.addRow(c_subs)
        ly.addLayout(frm)
        b_ok = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ly.addWidget(b_ok)
        def on_ok():
            u = url_edit.text().strip()
            if not u:
                QMessageBox.warning(d, self._("Error"), self._("No URL."))
                return
            ao = c_audio.isChecked()
            pl = c_pl.isChecked()
            subs = c_subs.isChecked()
            f_out = fmt_combo.currentText()
            task = DownloadTask(
                u,
                self.user_profile.get_default_resolution(),
                self.user_profile.get_download_path(),
                audio_only=ao,
                playlist=pl,
                subtitles=subs,
                output_format=f_out,
                from_queue=True,
                priority=1,
                recurrence=None
            )
            row = self.queue_table.rowCount()
            self.queue_table.insertRow(row)
            self.queue_table.setItem(row, 0, QTableWidgetItem("Fetching..."))
            self.queue_table.setItem(row, 1, QTableWidgetItem("Fetching..."))
            self.queue_table.setItem(row, 2, QTableWidgetItem(u))
            dtp = self._("Audio") if ao else self._("Video")
            if pl:
                dtp += f" - {self._('Playlist')}"
            self.queue_table.setItem(row, 3, QTableWidgetItem(dtp))
            self.queue_table.setItem(row, 4, QTableWidgetItem("0%"))
            self.add_history_entry("Fetching...", "Fetching...", u, self._("Queued"))
            self.run_task(task, row)
            d.accept()
        def on_cancel():
            d.reject()
        b_ok.accepted.connect(on_ok)
        b_ok.rejected.connect(on_cancel)
        d.exec_()

    def start_queue(self):
        count_started = 0
        for r in range(self.queue_table.rowCount()):
            st_item = self.queue_table.item(r, 4)
            if st_item and (self._("Queued") in st_item.text() or "0%" in st_item.text()):
                if count_started < self.max_concurrent_downloads:
                    url = self.queue_table.item(r, 2).text()
                    typ = self.queue_table.item(r, 3).text().lower()
                    audio = (self._("audio") in typ)
                    playlist = (self._("playlist") in typ)
                    current_format = "mp4"
                    row_idx = r
                    rate_limit = self.user_profile.get_rate_limit()
                    subtitles = "download subtitles" in typ
                    tsk = DownloadTask(
                        url,
                        self.user_profile.get_default_resolution(),
                        self.user_profile.get_download_path(),
                        audio_only=audio,
                        playlist=playlist,
                        subtitles=subtitles,
                        output_format=current_format,
                        from_queue=True,
                        priority=1,
                        recurrence=None,
                        max_rate=rate_limit
                    )
                    self.run_task(tsk, row_idx)
                    self.queue_table.setItem(r, 4, QTableWidgetItem(self._("Started")))
                    count_started += 1
        self.append_log(self._("Queue started."))

    def remove_scheduled_item(self):
        sel = set()
        for it in self.scheduler_table.selectedItems():
            sel.add(it.row())
        for r in sorted(sel, reverse=True):
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
        url_edit = DragDropLineEdit(self._("Enter link"))
        c_a = QCheckBox(self._("Audio Only"))
        c_s = QCheckBox(self._("Download Subtitles?"))
        priority_combo = QComboBox()
        priority_combo.addItems([self._("1 - High"), self._("2 - Medium"), self._("3 - Low")])
        recurrence_combo = QComboBox()
        recurrence_combo.addItems([self._("None"), self._("Daily"), self._("Weekly"), self._("Monthly")])
        frm.addRow(self._("Datetime:"), dt_edit)
        frm.addRow(self._("URL:"), url_edit)
        frm.addRow(c_a)
        frm.addRow(c_s)
        frm.addRow(self._("Priority:"), priority_combo)
        frm.addRow(self._("Recurrence:"), recurrence_combo)
        ly.addLayout(frm)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ly.addWidget(bb)
        def on_ok():
            dt_val = dt_edit.dateTime()
            u = url_edit.text().strip()
            if not u:
                QMessageBox.warning(d, self._("Error"), self._("No URL."))
                return
            ao = c_a.isChecked()
            pl = False
            subs = c_s.isChecked()
            priority_text = priority_combo.currentText().split(" - ")[0]
            try:
                priority = int(priority_text)
            except:
                priority = 2
            recurrence = recurrence_combo.currentText().lower() if recurrence_combo.currentText() != self._("None") else None
            row = self.scheduler_table.rowCount()
            self.scheduler_table.insertRow(row)
            self.scheduler_table.setItem(row, 0, QTableWidgetItem(dt_val.toString("yyyy-MM-dd HH:mm:ss")))
            self.scheduler_table.setItem(row, 1, QTableWidgetItem(u))
            typ = self._("Audio") if ao else self._("Video")
            self.scheduler_table.setItem(row, 2, QTableWidgetItem(typ))
            subs_txt = self._("Yes") if subs else self._("No")
            self.scheduler_table.setItem(row, 3, QTableWidgetItem(subs_txt))
            self.scheduler_table.setItem(row, 4, QTableWidgetItem(self._("Scheduled")))
            self.scheduler_table.setItem(row, 5, QTableWidgetItem(str(priority)))
            self.scheduler_table.setItem(row, 6, QTableWidgetItem(recurrence.capitalize() if recurrence else self._("None")))
            d.accept()
        def on_cancel():
            d.reject()
        bb.accepted.connect(on_ok)
        bb.rejected.connect(on_cancel)
        d.exec_()

    def check_scheduled_downloads(self):
        now = QDateTime.currentDateTime()
        for r in range(self.scheduler_table.rowCount()):
            dt_str = self.scheduler_table.item(r, 0).text()
            scheduled_dt = QDateTime.fromString(dt_str, "yyyy-MM-dd HH:mm:ss")
            st_item = self.scheduler_table.item(r, 4)
            if st_item and scheduled_dt <= now and st_item.text() == self._("Scheduled"):
                u = self.scheduler_table.item(r, 1).text()
                t = self.scheduler_table.item(r, 2).text().lower()
                s = (self.scheduler_table.item(r, 3).text() == self._("Yes"))
                audio = (self._("audio") in t)
                priority = int(self.scheduler_table.item(r, 5).text())
                recurrence = self.scheduler_table.item(r, 6).text().lower() if self.scheduler_table.item(r, 6).text() != self._("None") else None
                task = DownloadTask(
                    u,
                    self.user_profile.get_default_resolution(),
                    self.user_profile.get_download_path(),
                    audio_only=audio,
                    playlist=False,
                    subtitles=s,
                    output_format="mp4",
                    from_queue=True,
                    priority=priority,
                    recurrence=recurrence,
                    max_rate=self.user_profile.get_rate_limit()
                )
                self.run_task(task, r)
                self.scheduler_table.setItem(r, 4, QTableWidgetItem(self._("Started")))
                if recurrence:
                    if recurrence == 'daily':
                        new_dt = scheduled_dt.addDays(1)
                    elif recurrence == 'weekly':
                        new_dt = scheduled_dt.addDays(7)
                    elif recurrence == 'monthly':
                        new_dt = scheduled_dt.addMonths(1)
                    self.scheduler_table.setItem(r, 0, QTableWidgetItem(new_dt.toString("yyyy-MM-dd HH:mm:ss")))
                    self.scheduler_table.setItem(r, 4, QTableWidgetItem(self._("Scheduled")))

    def start_download_simple(self, url_edit, audio=False, playlist=False):
        link = url_edit.text().strip()
        if not link:
            QMessageBox.warning(self, self._("Error"), self._("No URL given."))
            return
        if not (link.startswith("http://") or link.startswith("https://")):
            QMessageBox.warning(self, self._("Input Error"), self._("Invalid URL format."))
            return
        rate_limit = self.user_profile.get_rate_limit()
        task = DownloadTask(
            link,
            self.user_profile.get_default_resolution(),
            self.user_profile.get_download_path(),
            audio_only=audio,
            playlist=playlist,
            from_queue=False,
            max_rate=rate_limit
        )
        self.add_history_entry("Fetching...", "Fetching...", link, self._("Queued"))
        self.run_task(task, None)

    def run_task(self, task, row):
        signals = WorkerSignals()
        signals.progress.connect(self.progress_signal.emit)
        signals.status.connect(self.status_signal.emit)
        signals.log.connect(self.log_signal.emit)
        worker = DownloadQueueWorker(task, row, signals)
        if row is not None:
            self.active_workers[row] = worker
        self.thread_pool.start(worker)

    def update_progress(self, row, percent):
        if row is not None and row < self.queue_table.rowCount():
            self.queue_table.setItem(row, 4, QTableWidgetItem(f"{int(percent)}%"))
        self.progress_bar.setValue(int(percent))
        self.progress_bar.setFormat(f"{int(percent)}%")
        self.status_label.setText(self._("Downloading...") + f" {percent:.2f}%")

    def update_status(self, row, st):
        if row is not None and row < self.queue_table.rowCount():
            self.queue_table.setItem(row, 4, QTableWidgetItem(self._(st)))
        self.status_label.setText(self._(st))
        if "Error" in st:
            QMessageBox.critical(self, self._("Error"), st)
        elif "Completed" in st:
            user_choice = QMessageBox.question(
                self, self._("Download Completed"), self._("Open Download Folder?"), QMessageBox.Yes | QMessageBox.No
            )
            if user_choice == QMessageBox.Yes:
                self.open_download_folder()
        if row is not None and row in self.active_workers:
            del self.active_workers[row]

    def open_download_folder(self):
        folder = self.user_profile.get_download_path()
        if platform.system() == "Windows":
            os.startfile(folder)
        elif platform.system() == "Darwin":
            subprocess.run(["open", folder])
        else:
            subprocess.run(["xdg-open", folder])

    def append_log(self, text):
        if any(k in text.lower() for k in ["error","fail"]):
            color = "red"
        elif any(k in text.lower() for k in ["warning","warn"]):
            color = "yellow"
        elif any(k in text.lower() for k in ["completed","started","queued","fetching"]):
            color = "green"
        elif "cancel" in text.lower():
            color = "orange"
        else:
            color = "white"
        self.log_text_edit.setTextColor(QColor(color))
        self.log_text_edit.append(text)
        self.log_text_edit.setTextColor(QColor("white"))

    def add_history_entry(self, title, channel, url, stat):
        if not self.user_profile.is_history_enabled():
            return
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        self.history_table.setItem(row, 0, QTableWidgetItem(title))
        self.history_table.setItem(row, 1, QTableWidgetItem(channel))
        self.history_table.setItem(row, 2, QTableWidgetItem(url))
        self.history_table.setItem(row, 3, QTableWidgetItem(stat))

    def delete_selected_history(self):
        selected_rows = set()
        for it in self.history_table.selectedItems():
            selected_rows.add(it.row())
        for r in sorted(selected_rows, reverse=True):
            self.history_table.removeRow(r)
        self.append_log(self._("Deleted {count} history entries.").format(count=len(selected_rows)))

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
            hide = True
            for c in range(self.history_table.columnCount()):
                it = self.history_table.item(r, c)
                if it and txt in it.text().lower():
                    hide = False
                    break
            self.history_table.setRowHidden(r, hide)

    def set_max_concurrent_downloads(self, idx):
        val = self.concurrent_combo.currentText()
        self.max_concurrent_downloads = int(val)
        self.append_log(self._("Max concurrent downloads set to {val}").format(val=val))

    def change_theme_clicked(self):
        new_theme = self.theme_combo.currentText()
        self.user_profile.set_theme(new_theme)
        apply_theme(QApplication.instance(), new_theme)
        self.append_log(self._("Theme changed to '{theme}'.".format(theme=new_theme)))

    def apply_resolution(self):
        sr = self.res_combo.currentText()
        self.user_profile.set_default_resolution(sr)
        prx = self.proxy_edit.text().strip()
        self.user_profile.set_proxy(prx)
        self.append_log(self._("Resolution set: {res}, Proxy: {prx}".format(res=sr, prx=prx)))
        QMessageBox.information(self, self._("Settings"), self._("Resolution: {res}\nProxy: {prx}".format(res=sr, prx=prx)))

    def select_download_path(self):
        folder = QFileDialog.getExistingDirectory(self, self._("Select Download Folder"))
        if folder:
            self.user_profile.set_profile(
                self.user_profile.data["name"],
                self.user_profile.data["profile_picture"],
                folder
            )
            self.download_path_edit.setText(folder)
            self.append_log(self._("Download path changed to {folder}".format(folder=folder)))

    def pause_active(self):
        for worker in self.active_workers.values():
            worker.pause_download()

    def resume_active(self):
        for worker in self.active_workers.values():
            worker.resume_download()

    def cancel_active(self):
        for worker in list(self.active_workers.values()):
            worker.cancel_download()

    def reset_profile(self):
        if os.path.exists(self.user_profile.profile_path):
            os.remove(self.user_profile.profile_path)
        QMessageBox.information(self, self._("Reset Profile"), self._("Profile data removed. Please restart."))
        self.append_log(self._("Profile has been reset."))

    def restart_application(self):
        self.append_log(self._("Restarting application..."))
        QMessageBox.information(self, self._("Restart"), self._("The application will now restart."))
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def apply_rate_limit(self):
        rate = self.rate_edit.text().strip()
        if rate:
            if not any(rate.endswith(x) for x in ["K", "M", "G"]):
                QMessageBox.warning(self, self._("Invalid Format"), self._("Please enter rate like '500K', '2M', etc."))
                return
            self.user_profile.set_rate_limit(rate)
            self.append_log(self._("Download speed limit set to {rate}".format(rate=rate)))
            QMessageBox.information(self, self._("Rate Limit"), self._("Download speed limited to {rate}".format(rate=rate)))
        else:
            self.user_profile.set_rate_limit(None)
            self.append_log(self._("Download speed limit removed."))
            QMessageBox.information(self, self._("Rate Limit"), self._("Download speed limit removed."))

    def change_language(self):
        selected_lang = self.lang_combo.currentText()
        lang_code = 'tr' if selected_lang == 'Türkçe' else 'en'
        self.user_profile.set_language(lang_code)
        self.append_log(self._("Language set to {lang}".format(lang=selected_lang)))
        QMessageBox.information(self, self._("Language Changed"), self._("Language will change after restart."))
        self.restart_application()

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
