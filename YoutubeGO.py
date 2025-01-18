import sys
import os
import json
import platform
import subprocess
import shutil
import yt_dlp
from PyQt5.QtCore import Qt, pyqtSignal, QThreadPool, QRunnable, QTimer, QDateTime
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QListWidget, QAbstractItemView, QDockWidget, QTextEdit, QProgressBar, QStatusBar,
    QMenuBar, QAction, QLabel, QLineEdit, QFileDialog, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QCheckBox, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QDateTimeEdit, QComboBox, QListWidgetItem
)

########################################
#                DragDropLineEdit
########################################
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

########################################
#                UserProfile
########################################
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
            "social_media_links": {"instagram": "", "twitter": "", "youtube": ""}
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
        if os.path.exists(self.data["profile_picture"]):
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

########################################
#                THEME
########################################
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

########################################
#                DOWNLOAD
########################################
class DownloadTask:
    def __init__(self, url, resolution, folder, audio_only=False, playlist=False, subtitles=False, output_format="mp4", from_queue=False):
        self.url = url
        self.resolution = resolution
        self.folder = folder
        self.audio_only = audio_only
        self.playlist = playlist
        self.subtitles = subtitles
        self.output_format = output_format
        self.from_queue = from_queue

class DownloadQueueWorker(QRunnable):
    def __init__(self, task, row, progress_signal, status_signal, log_signal):
        super().__init__()
        self.task = task
        self.row = row
        self.progress_signal = progress_signal
        self.status_signal = status_signal
        self.log_signal = log_signal
        self.pause = False
        self.cancel = False
        self.partial_files = []
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
            self.status_signal.emit(self.row, "Download Error")
            self.log_signal.emit(f"Failed to fetch video info for {self.task.url}\n{str(e)}")
            return
        ydl_opts_download = {
            "outtmpl": os.path.join(self.task.folder, "%(title)s.%(ext)s"),
            "progress_hooks": [self.progress_hook],
            "noplaylist": not self.task.playlist,
            "cookiefile": "youtube_cookies.txt"
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
            self.status_signal.emit(self.row, "Download Completed")
            self.log_signal.emit(f"Download Completed: {title} by {channel}")
        except yt_dlp.utils.DownloadError as e:
            if self.cancel:
                self.status_signal.emit(self.row, "Download Cancelled")
                self.log_signal.emit(f"Download Cancelled: {title} by {channel}")
            else:
                self.status_signal.emit(self.row, "Download Error")
                self.log_signal.emit(f"Download Error for {title} by {channel}:\n{str(e)}")
        except Exception as e:
            self.status_signal.emit(self.row, "Download Error")
            self.log_signal.emit(f"Unexpected Error for {title} by {channel}:\n{str(e)}")
    def progress_hook(self, d):
        if self.cancel:
            raise yt_dlp.utils.DownloadError("Cancelled")
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            est_total = d.get("total_bytes_estimate", 0)
            exact_total = d.get("total_bytes", 0)
            total = 0
            if exact_total > 0:
                total = exact_total
            elif est_total > 0:
                total = est_total
            if total <= 0:
                percent = 0
            else:
                if downloaded > total:
                    downloaded = total
                percent = (downloaded / total) * 100
            if percent > 100:
                percent = 100
            self.progress_signal.emit(self.row, percent)
        while self.pause:
            QTimer.singleShot(200, lambda: None)
    def pause_download(self):
        self.pause = True
        self.status_signal.emit(self.row, "Download Paused")
        self.log_signal.emit("Download Paused")
    def resume_download(self):
        self.pause = False
        self.status_signal.emit(self.row, "Download Resumed")
        self.log_signal.emit("Download Resumed")
    def cancel_download(self):
        self.cancel = True
        for f in set(self.partial_files):
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        self.status_signal.emit(self.row, "Download Cancelled")
        self.log_signal.emit("Download Cancelled")

########################################
#                MAINWINDOW
########################################
class MainWindow(QMainWindow):
    progress_signal = pyqtSignal(int, float)
    status_signal = pyqtSignal(int, str)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YoutubeGO 4.2")
        self.setGeometry(100, 100, 1280, 720)
        self.ffmpeg_found = False
        self.ffmpeg_path = ""
        self.ffmpeg_label = QLabel()
        self.show_logs_btn = QPushButton("Logs")
        self.log_dock_visible = True
        self.check_ffmpeg()
        self.user_profile = UserProfile()
        self.thread_pool = QThreadPool()
        self.active_workers = []
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
        }
        self.progress_signal.connect(self.update_progress)
        self.status_signal.connect(self.update_status)
        self.log_signal.connect(self.append_log)
        self.init_ui()
        apply_theme(QApplication.instance(), self.user_profile.get_theme())
        if not self.user_profile.is_profile_complete():
            self.prompt_user_profile()

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
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        reset_profile_action = QAction("Reset Profile", self)
        reset_profile_action.triggered.connect(self.reset_profile)
        restart_action = QAction("Restart Application", self)
        restart_action.triggered.connect(self.restart_application)
        file_menu.addAction(exit_action)
        file_menu.addAction(reset_profile_action)
        file_menu.addAction(restart_action)
        help_menu = menu_bar.addMenu("Help")
        insta_action = QAction("Instagram: toxi.dev", self)
        insta_action.triggered.connect(lambda: QMessageBox.information(self, "Instagram", "Follow on Instagram: toxi.dev"))
        help_menu.addAction(insta_action)
        mail_action = QAction("Github: https://github.com/Efeckc17", self)
        mail_action.triggered.connect(lambda: QMessageBox.information(self, "GitHub", "https://github.com/Efeckc17"))
        help_menu.addAction(mail_action)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("0%")
        self.progress_bar.setStyleSheet("font-weight: bold;")
        self.status_label = QLabel("Ready")
        if self.ffmpeg_found:
            self.ffmpeg_label.setText("FFmpeg Found")
            self.ffmpeg_label.setStyleSheet("color: green; font-weight: bold;")
            self.ffmpeg_label.setToolTip(self.ffmpeg_path)
        else:
            self.ffmpeg_label.setText("FFmpeg Missing")
            self.ffmpeg_label.setStyleSheet("color: red; font-weight: bold;")
        self.show_logs_btn.setFixedWidth(60)
        self.show_logs_btn.clicked.connect(self.toggle_logs)
        self.status_bar.addWidget(self.show_logs_btn)
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.ffmpeg_label)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.log_dock = QDockWidget("Logs", self)
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
        self.logo_label = QLabel("YoutubeGO 4.2")
        self.logo_label.setFont(QFont("Arial", 14, QFont.Bold))
        tb_layout.addWidget(self.logo_label, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        search_container = QWidget()
        sc_layout = QHBoxLayout(search_container)
        sc_layout.setSpacing(5)
        sc_layout.setContentsMargins(0, 0, 0, 0)
        self.top_search_edit = QLineEdit()
        self.top_search_edit.setPlaceholderText("Search something...")
        self.top_search_edit.setFixedHeight(30)
        self.search_btn = QPushButton("Search")
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
        self.main_stack.addWidget(self.page_home)
        self.main_stack.addWidget(self.page_mp4)
        self.main_stack.addWidget(self.page_mp3)
        self.main_stack.addWidget(self.page_history)
        self.main_stack.addWidget(self.page_settings)
        self.main_stack.addWidget(self.page_profile)
        self.main_stack.addWidget(self.page_queue)
        self.main_stack.addWidget(self.page_scheduler)
        self.side_menu = QListWidget()
        self.side_menu.setFixedWidth(130)
        self.side_menu.setSelectionMode(QAbstractItemView.SingleSelection)
        self.side_menu.setFlow(QListWidget.TopToBottom)
        self.side_menu.setSpacing(2)
        menu_items = ["Home", "MP4", "MP3", "History", "Settings", "Profile", "Queue", "Scheduler"]
        for item_name in menu_items:
            self.side_menu.addItem(item_name)
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
            "Home Page - Welcome to YoutubeGO 4.2\n\n"
            "New Features:\n"
            "- Automatic cookie usage\n"
            "- Modern rounded UI\n"
            "- Large download fix\n\n"
            "Github: https://github.com/Efeckc17\n"
            "Instagram: toxi.dev\n"
            "Developed by toxi360 under MIT License"
        )
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(lbl)
        layout.addStretch()
        return w

    def create_page_mp4(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel("Download MP4")
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.mp4_url = DragDropLineEdit("Paste or drag a link here...")
        layout.addWidget(self.mp4_url)
        hl = QHBoxLayout()
        single_btn = QPushButton("Download Single MP4")
        single_btn.clicked.connect(lambda: self.start_download_simple(self.mp4_url, audio=False, playlist=False))
        playlist_btn = QPushButton("Download Playlist MP4")
        playlist_btn.clicked.connect(lambda: self.start_download_simple(self.mp4_url, audio=False, playlist=True))
        pause_btn = QPushButton("Pause All")
        pause_btn.clicked.connect(self.pause_active)
        cancel_btn = QPushButton("Cancel All")
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
        lbl = QLabel("Download MP3")
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.mp3_url = DragDropLineEdit("Paste or drag a link here...")
        layout.addWidget(self.mp3_url)
        hl = QHBoxLayout()
        single_btn = QPushButton("Download Single MP3")
        single_btn.clicked.connect(lambda: self.start_download_simple(self.mp3_url, audio=True, playlist=False))
        playlist_btn = QPushButton("Download Playlist MP3")
        playlist_btn.clicked.connect(lambda: self.start_download_simple(self.mp3_url, audio=True, playlist=True))
        pause_btn = QPushButton("Pause All")
        pause_btn.clicked.connect(self.pause_active)
        cancel_btn = QPushButton("Cancel All")
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
        lbl = QLabel("Download History")
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Title", "Channel", "URL", "Status"])
        hh = self.history_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.history_table)
        hl = QHBoxLayout()
        del_sel_btn = QPushButton("Delete Selected")
        del_sel_btn.clicked.connect(self.delete_selected_history)
        del_all_btn = QPushButton("Delete All")
        del_all_btn.clicked.connect(self.delete_all_history)
        hist_ck = QCheckBox("Enable History Logging")
        hist_ck.setChecked(self.user_profile.is_history_enabled())
        hist_ck.stateChanged.connect(self.toggle_history_logging)
        hl.addWidget(del_sel_btn)
        hl.addWidget(del_all_btn)
        hl.addWidget(hist_ck)
        layout.addLayout(hl)
        s_hl = QHBoxLayout()
        self.search_hist_edit = QLineEdit()
        self.search_hist_edit.setPlaceholderText("Search in history...")
        s_btn = QPushButton("Search")
        s_btn.clicked.connect(self.search_history)
        s_hl.addWidget(self.search_hist_edit)
        s_hl.addWidget(s_btn)
        layout.addLayout(s_hl)
        layout.addStretch()
        return w

    def create_page_settings(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel("Settings")
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        g_con = QGroupBox("Max Concurrent Downloads")
        g_layout = QHBoxLayout(g_con)
        self.concurrent_combo = QComboBox()
        self.concurrent_combo.addItems(["1","2","3","4","5","10"])
        self.concurrent_combo.setCurrentText(str(self.max_concurrent_downloads))
        self.concurrent_combo.currentIndexChanged.connect(self.set_max_concurrent_downloads)
        g_layout.addWidget(QLabel("Concurrent:"))
        g_layout.addWidget(self.concurrent_combo)
        layout.addWidget(g_con)
        g_tech = QGroupBox("Technical / Appearance")
        fl = QFormLayout(g_tech)
        self.proxy_edit = QLineEdit()
        self.proxy_edit.setText(self.user_profile.get_proxy())
        self.proxy_edit.setPlaceholderText("Proxy or bandwidth limit...")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark","Light"])
        self.theme_combo.setCurrentText(self.user_profile.get_theme())
        fl.addRow("Proxy/BW:", self.proxy_edit)
        fl.addRow("Theme:", self.theme_combo)
        theme_btn = QPushButton("Apply Theme")
        theme_btn.clicked.connect(self.change_theme_clicked)
        fl.addWidget(theme_btn)
        layout.addWidget(g_tech)
        g_res = QGroupBox("Default Resolution")
        r_hl = QHBoxLayout(g_res)
        self.res_combo = QComboBox()
        self.res_combo.addItems(["144p","240p","360p","480p","720p","1080p","1440p","2160p","4320p"])
        self.res_combo.setCurrentText(self.user_profile.get_default_resolution())
        r_hl.addWidget(QLabel("Resolution:"))
        r_hl.addWidget(self.res_combo)
        a_btn = QPushButton("Apply")
        a_btn.clicked.connect(self.apply_resolution)
        r_hl.addWidget(a_btn)
        layout.addWidget(g_res)
        g_path = QGroupBox("Download Path")
        p_hl = QHBoxLayout(g_path)
        self.download_path_edit = QLineEdit()
        self.download_path_edit.setReadOnly(True)
        self.download_path_edit.setText(self.user_profile.get_download_path())
        b_br = QPushButton("Browse")
        b_br.clicked.connect(self.select_download_path)
        p_hl.addWidget(QLabel("Folder:"))
        p_hl.addWidget(self.download_path_edit)
        p_hl.addWidget(b_br)
        layout.addWidget(g_path)
        layout.addStretch()
        return w

    def create_page_profile(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel("Profile Page - Customize your details")
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        form_layout = QFormLayout()
        self.profile_name_edit = QLineEdit()
        self.profile_name_edit.setText(self.user_profile.data["name"])
        form_layout.addRow("Name:", self.profile_name_edit)
        pic_label = QLabel(
            os.path.basename(self.user_profile.data["profile_picture"]) if self.user_profile.data["profile_picture"] else "No file selected."
        )
        pic_btn = QPushButton("Change Picture")
        remove_pic_btn = QPushButton("Remove Picture")
        remove_pic_btn.setVisible(bool(self.user_profile.data["profile_picture"]))
        def pick_pic():
            path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg)")
            if path:
                pic_btn.setProperty("selected_path", path)
                pic_label.setText(os.path.basename(path))
        def remove_pic():
            self.user_profile.remove_profile_picture()
            pic_label.setText("No file selected.")
            pic_btn.setProperty("selected_path", "")
            remove_pic_btn.setVisible(False)
        pic_btn.clicked.connect(pick_pic)
        remove_pic_btn.clicked.connect(remove_pic)
        form_layout.addRow("Picture:", pic_btn)
        form_layout.addRow(pic_label)
        form_layout.addRow(remove_pic_btn)
        self.insta_edit = QLineEdit()
        self.insta_edit.setText(self.user_profile.data["social_media_links"].get("instagram", ""))
        form_layout.addRow("Instagram:", self.insta_edit)
        self.tw_edit = QLineEdit()
        self.tw_edit.setText(self.user_profile.data["social_media_links"].get("twitter", ""))
        form_layout.addRow("Twitter:", self.tw_edit)
        self.yt_edit = QLineEdit()
        self.yt_edit.setText(self.user_profile.data["social_media_links"].get("youtube", ""))
        form_layout.addRow("YouTube:", self.yt_edit)
        layout.addLayout(form_layout)
        save_btn = QPushButton("Save Profile")
        def save_profile():
            name = self.profile_name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Name cannot be empty.")
                return
            pic_path = pic_btn.property("selected_path") if pic_btn.property("selected_path") else ""
            if pic_path:
                dest = os.path.join(os.getcwd(), "profile_pic" + os.path.splitext(pic_path)[1])
                try:
                    with open(pic_path, "rb") as s, open(dest, "wb") as d:
                        d.write(s.read())
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
                    return
                self.user_profile.set_profile(name, dest, self.user_profile.get_download_path())
            else:
                self.user_profile.set_profile(name, self.user_profile.data["profile_picture"], self.user_profile.get_download_path())
            self.user_profile.set_social_media_links(
                self.insta_edit.text().strip(),
                self.tw_edit.text().strip(),
                self.yt_edit.text().strip()
            )
            QMessageBox.information(self, "Saved", "Profile settings saved.")
        save_btn.clicked.connect(save_profile)
        layout.addWidget(save_btn)
        layout.addStretch()
        return w

    def create_page_queue(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel("Download Queue")
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(5)
        self.queue_table.setHorizontalHeaderLabels(["Title","Channel","URL","Type","Progress"])
        hh = self.queue_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self.queue_table)
        hl = QHBoxLayout()
        b_add = QPushButton("Add to Queue")
        b_add.clicked.connect(self.add_queue_item_dialog)
        b_start = QPushButton("Start Queue")
        b_start.clicked.connect(self.start_queue)
        b_pause = QPushButton("Pause All")
        b_pause.clicked.connect(self.pause_active)
        b_resume = QPushButton("Resume All")
        b_resume.clicked.connect(self.resume_active)
        b_cancel = QPushButton("Cancel All")
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
        lbl = QLabel("Scheduler (Planned Downloads)")
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.scheduler_table = QTableWidget()
        self.scheduler_table.setColumnCount(5)
        self.scheduler_table.setHorizontalHeaderLabels(["Datetime","URL","Type","Subtitles","Status"])
        hh = self.scheduler_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout.addWidget(self.scheduler_table)
        hl = QHBoxLayout()
        b_add = QPushButton("Add Scheduled Download")
        b_add.clicked.connect(self.add_scheduled_dialog)
        b_remove = QPushButton("Remove Selected")
        b_remove.clicked.connect(self.remove_scheduled_item)
        hl.addWidget(b_add)
        hl.addWidget(b_remove)
        layout.addLayout(hl)
        layout.addStretch()
        self.scheduler_timer = QTimer()
        self.scheduler_timer.timeout.connect(self.check_scheduled_downloads)
        self.scheduler_timer.start(10000)
        return w

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
                item = QListWidgetItem(f"{k}: {v[1]}")
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
        dialog.setWindowTitle("Create User Profile")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        frm = QFormLayout()
        name_edit = QLineEdit()
        pic_btn = QPushButton("Select Picture (Optional)")
        pic_label = QLabel("No file selected.")
        def pick_pic():
            path, _ = QFileDialog.getOpenFileName(self, "Profile Picture", "", "Images (*.png *.jpg *.jpeg)")
            if path:
                pic_btn.setText(os.path.basename(path))
                pic_btn.setProperty("selected_path", path)
                pic_label.setText(os.path.basename(path))
        pic_btn.clicked.connect(pick_pic)
        frm.addRow("Name:", name_edit)
        frm.addRow("Picture:", pic_btn)
        frm.addRow(pic_label)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addLayout(frm)
        layout.addWidget(bb)
        def on_ok():
            nm = name_edit.text().strip()
            pp = pic_btn.property("selected_path")
            if not nm:
                QMessageBox.warning(dialog, "Error", "Please provide a name.")
                return
            dest_pic = ""
            if pp:
                dest_pic = os.path.join(os.getcwd(), "profile_pic" + os.path.splitext(pp)[1])
                try:
                    with open(pp, "rb") as src, open(dest_pic, "wb") as dst:
                        dst.write(src.read())
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", str(e))
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
        d.setWindowTitle("Add to Queue")
        d.setModal(True)
        ly = QVBoxLayout(d)
        frm = QFormLayout()
        url_edit = DragDropLineEdit("Enter or drag a link here")
        c_audio = QCheckBox("Audio Only")
        c_pl = QCheckBox("Playlist")
        c_subs = QCheckBox("Download Subtitles")
        fmt_combo = QComboBox()
        fmt_combo.addItems(["mp4","mkv","webm","flv","avi"])
        frm.addRow("URL:", url_edit)
        frm.addRow(c_audio)
        frm.addRow(c_pl)
        frm.addRow("Format:", fmt_combo)
        frm.addRow(c_subs)
        ly.addLayout(frm)
        b_ok = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ly.addWidget(b_ok)
        def on_ok():
            u = url_edit.text().strip()
            if not u:
                QMessageBox.warning(d, "Error", "No URL.")
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
                from_queue=True
            )
            row = self.queue_table.rowCount()
            self.queue_table.insertRow(row)
            self.queue_table.setItem(row, 0, QTableWidgetItem("Fetching..."))
            self.queue_table.setItem(row, 1, QTableWidgetItem("Fetching..."))
            self.queue_table.setItem(row, 2, QTableWidgetItem(u))
            dtp = "Audio" if ao else "Video"
            if pl:
                dtp += " - Playlist"
            self.queue_table.setItem(row, 3, QTableWidgetItem(dtp))
            self.queue_table.setItem(row, 4, QTableWidgetItem("0%"))
            self.add_history_entry("Fetching...", "Fetching...", u, "Queued")
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
            if st_item and ("Queued" in st_item.text() or "0%" in st_item.text()):
                if count_started < self.max_concurrent_downloads:
                    url = self.queue_table.item(r, 2).text()
                    typ = self.queue_table.item(r, 3).text().lower()
                    audio = ("audio" in typ)
                    playlist = ("playlist" in typ)
                    current_format = "mp4"
                    if "video" in typ and "playlist" in typ:
                        current_format = "mp4"
                    row_idx = r
                    tsk = DownloadTask(
                        url,
                        self.user_profile.get_default_resolution(),
                        self.user_profile.get_download_path(),
                        audio_only=audio,
                        playlist=playlist,
                        output_format=current_format,
                        from_queue=True
                    )
                    self.run_task(tsk, row_idx)
                    self.queue_table.setItem(r, 4, QTableWidgetItem("Started"))
                    count_started += 1
        self.append_log("Queue started.")

    def remove_scheduled_item(self):
        sel = set()
        for it in self.scheduler_table.selectedItems():
            sel.add(it.row())
        for r in sorted(sel, reverse=True):
            self.scheduler_table.removeRow(r)

    def add_scheduled_dialog(self):
        d = QDialog(self)
        d.setWindowTitle("Add Scheduled Download")
        d.setModal(True)
        ly = QVBoxLayout(d)
        frm = QFormLayout()
        dt_edit = QDateTimeEdit()
        dt_edit.setCalendarPopup(True)
        dt_edit.setDateTime(QDateTime.currentDateTime())
        url_edit = DragDropLineEdit("Enter link")
        c_a = QCheckBox("Audio Only")
        c_s = QCheckBox("Download Subtitles?")
        frm.addRow("Datetime:", dt_edit)
        frm.addRow("URL:", url_edit)
        frm.addRow(c_a)
        frm.addRow(c_s)
        ly.addLayout(frm)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ly.addWidget(bb)
        def on_ok():
            dt_val = dt_edit.dateTime()
            u = url_edit.text().strip()
            if not u:
                QMessageBox.warning(d, "Error", "No URL.")
                return
            row = self.scheduler_table.rowCount()
            self.scheduler_table.insertRow(row)
            self.scheduler_table.setItem(row, 0, QTableWidgetItem(dt_val.toString("yyyy-MM-dd HH:mm:ss")))
            self.scheduler_table.setItem(row, 1, QTableWidgetItem(u))
            typ = "Audio" if c_a.isChecked() else "Video"
            self.scheduler_table.setItem(row, 2, QTableWidgetItem(typ))
            subs_txt = "Yes" if c_s.isChecked() else "No"
            self.scheduler_table.setItem(row, 3, QTableWidgetItem(subs_txt))
            self.scheduler_table.setItem(row, 4, QTableWidgetItem("Scheduled"))
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
            if st_item and scheduled_dt <= now and st_item.text() == "Scheduled":
                u = self.scheduler_table.item(r, 1).text()
                t = self.scheduler_table.item(r, 2).text().lower()
                s = (self.scheduler_table.item(r, 3).text() == "Yes")
                audio = ("audio" in t)
                task = DownloadTask(
                    u,
                    self.user_profile.get_default_resolution(),
                    self.user_profile.get_download_path(),
                    audio_only=audio,
                    playlist=False,
                    subtitles=s,
                    from_queue=True
                )
                self.run_task(task, r)
                self.scheduler_table.setItem(r, 4, QTableWidgetItem("Started"))

    def start_download_simple(self, url_edit, audio=False, playlist=False):
        link = url_edit.text().strip()
        if not link:
            QMessageBox.warning(self, "Error", "No URL given.")
            return
        if not (link.startswith("http://") or link.startswith("https://")):
            QMessageBox.warning(self, "Input Error", "Invalid URL format.")
            return
        task = DownloadTask(
            link,
            self.user_profile.get_default_resolution(),
            self.user_profile.get_download_path(),
            audio_only=audio,
            playlist=playlist,
            from_queue=False
        )
        self.add_history_entry("Fetching...", "Fetching...", link, "Queued")
        self.run_task(task, None)

    def run_task(self, task, row):
        worker = DownloadQueueWorker(task, row, self.progress_signal, self.status_signal, self.log_signal)
        self.thread_pool.start(worker)
        self.active_workers.append(worker)

    def update_progress(self, row, percent):
        if row is not None and row < self.queue_table.rowCount():
            self.queue_table.setItem(row, 4, QTableWidgetItem(f"{int(percent)}%"))
        self.progress_bar.setValue(int(percent))
        self.progress_bar.setFormat(f"{int(percent)}%")
        self.status_label.setText(f"Downloading... {percent:.2f}%")

    def update_status(self, row, st):
        if row is not None and row < self.queue_table.rowCount():
            self.queue_table.setItem(row, 4, QTableWidgetItem(st))
        self.status_label.setText(st)
        if "Error" in st:
            QMessageBox.critical(self, "Error", st)
        elif "Completed" in st:
            user_choice = QMessageBox.question(
                self, "Download Completed", "Open Download Folder?", QMessageBox.Yes | QMessageBox.No
            )
            if user_choice == QMessageBox.Yes:
                self.open_download_folder()

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
        self.append_log(f"Deleted {len(selected_rows)} history entries.")

    def delete_all_history(self):
        ans = QMessageBox.question(self, "Delete All", "Are you sure?", QMessageBox.Yes | QMessageBox.No)
        if ans == QMessageBox.Yes:
            self.history_table.setRowCount(0)
            self.append_log("All history deleted.")

    def toggle_history_logging(self, state):
        en = (state == Qt.Checked)
        self.user_profile.set_history_enabled(en)
        self.append_log(f"History logging {'enabled' if en else 'disabled'}.")

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
        self.append_log(f"Max concurrent downloads set to {val}")

    def change_theme_clicked(self):
        new_theme = self.theme_combo.currentText()
        self.user_profile.set_theme(new_theme)
        apply_theme(QApplication.instance(), new_theme)
        self.append_log(f"Theme changed to '{new_theme}'.")

    def apply_resolution(self):
        sr = self.res_combo.currentText()
        self.user_profile.set_default_resolution(sr)
        prx = self.proxy_edit.text().strip()
        self.user_profile.set_proxy(prx)
        self.append_log(f"Resolution set: {sr}, Proxy: {prx}")
        QMessageBox.information(self, "Settings", f"Resolution: {sr}\nProxy: {prx}")

    def select_download_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.user_profile.set_profile(
                self.user_profile.data["name"],
                self.user_profile.data["profile_picture"],
                folder
            )
            self.download_path_edit.setText(folder)
            self.append_log(f"Download path changed to {folder}")

    def pause_active(self):
        for w in self.active_workers:
            w.pause_download()

    def resume_active(self):
        for w in self.active_workers:
            w.resume_download()

    def cancel_active(self):
        for w in self.active_workers:
            w.cancel_download()

    def reset_profile(self):
        if os.path.exists(self.user_profile.profile_path):
            os.remove(self.user_profile.profile_path)
        QMessageBox.information(self, "Reset Profile", "Profile data removed. Please restart.")
        self.append_log("Profile has been reset.")

    def restart_application(self):
        self.append_log("Restarting application...")
        QMessageBox.information(self, "Restart", "The application will now restart.")
        self.close()
        python = sys.executable
        os.execl(python, python, *sys.argv)

########################################
#                MAIN
########################################
def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
