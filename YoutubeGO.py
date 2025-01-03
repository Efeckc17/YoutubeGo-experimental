#                                                                             TOXİ360                                                                                                   # 


import sys
import os
import json
import yt_dlp
import requests
import socket
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThreadPool, QRunnable, QTimer
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, 
    QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, 
    QProgressBar, QDockWidget, QTextEdit, QStatusBar, QMenuBar, 
    QAction, QComboBox, QFileDialog, QMessageBox, QListWidget, QListWidgetItem, 
    QAbstractItemView, QTableWidget, QTableWidgetItem, 
    QHeaderView, QGroupBox, QFormLayout, QCheckBox, QDialog, 
    QDialogButtonBox
)

class UserProfile:
    def __init__(self, profile_path="user_profile.json"):
        self.profile_path = profile_path
        self.data = {
            "name": "",
            "profile_picture": "",
            "default_resolution": "720p",
            "download_path": os.getcwd(),
            "history_enabled": True
        }
        self.load_profile()

    def load_profile(self):
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                try:
                    self.data = json.load(f)
                except json.JSONDecodeError:
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

    def set_default_resolution(self, resolution):
        self.data["default_resolution"] = resolution
        self.save_profile()

    def set_download_path(self, path):
        self.data["download_path"] = path
        self.save_profile()

    def set_history_enabled(self, enabled):
        self.data["history_enabled"] = enabled
        self.save_profile()

    def get_default_resolution(self):
        return self.data.get("default_resolution", "720p")

    def get_download_path(self):
        return self.data.get("download_path", os.getcwd())

    def is_history_enabled(self):
        return self.data.get("history_enabled", True)

    def is_profile_complete(self):
        return bool(self.data["name"] and self.data["profile_picture"])

def apply_theme(app, theme):
    if theme == "Dark":
        stylesheet = """
        QMainWindow {
            background-color: #1e1e1e;
        }
        QLabel, QPushButton, QLineEdit, QListWidget, QTableWidget, QComboBox, QCheckBox {
            color: #ffffff;
            background-color: #2d2d2d;
            border: 1px solid #444444;
            border-radius: 10px;
            padding: 5px;
        }
        QPushButton {
            border-radius: 15px;
            background-color: #e74c3c;
            color: white;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 10px;
            text-align: center;
            color: black;
            height: 20px;
        }
        QProgressBar::chunk {
            background-color: #e74c3c;
            width: 1px;
            border-radius: 5px;
        }
        QMenuBar {
            background-color: #1e1e1e;
            color: white;
        }
        QMenuBar::item:selected {
            background-color: #444444;
        }
        QMenu {
            background-color: #2d2d2d;
            color: white;
        }
        QMenu::item:selected {
            background-color: #444444;
        }
        QTableWidget {
            gridline-color: #555555;
            border-radius: 10px;
        }
        QHeaderView::section {
            background-color: #3c3f41;
            color: white;
            padding: 4px;
            border: 1px solid #555555;
            border-radius: 5px;
        }
        QGroupBox {
            border: 1px solid #555555;
            margin-top: 10px;
            padding-top: 5px;
            border-radius: 10px;
        }
        QLineEdit:read-only {
            background-color: #1e1e1e;
        }
        QListWidget::item {
            padding: 10px;
        }
        """
    else:
        stylesheet = ""
    app.setStyleSheet(stylesheet)

class DragDropLineEdit(QLineEdit):
    def __init__(self, placeholder="Drag and drop URL or enter manually"):
        super().__init__()
        self.setAcceptDrops(True)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("background-color: rgba(45, 45, 45, 200); color: white;")

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.acceptProposedAction()

    def dropEvent(self, e):
        txt = e.mimeData().text().strip()
        if txt.startswith("http"):
            self.setText(txt)
        else:
            self.setText(txt.replace("file://", ""))

class DownloadTask:
    def __init__(self, url, resolution, folder, audio_only, playlist, bandwidth):
        self.url = url
        self.resolution = resolution
        self.folder = folder
        self.audio_only = audio_only
        self.playlist = playlist
        self.bandwidth = bandwidth

class DownloadQueueWorker(QRunnable):
    def __init__(self, task, progress_signal, status_signal, log_signal):
        super().__init__()
        self.task = task
        self.progress_signal = progress_signal
        self.status_signal = status_signal
        self.log_signal = log_signal
        self.pause = False
        self.cancel = False
        self.partial_files = []

    def run(self):
       
        ydl_opts_info = {
            'quiet': True,
            'skip_download': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(self.task.url, download=False)
                title = info.get('title', 'No Title')
                channel = info.get('uploader', 'Unknown Channel')
        except Exception as e:
            self.status_signal.emit("Download Error")
            self.log_signal.emit(f"Failed to fetch video info for URL: {self.task.url} - Error: {str(e)}")
            return

      
        ydl_opts_download = {
            "outtmpl": os.path.join(self.task.folder, '%(title)s.%(ext)s'),
            "progress_hooks": [self.progress_hook],
            "noplaylist": not self.task.playlist
        }
        rate = self.convert_bandwidth(self.task.bandwidth)
        if rate is not None:
            ydl_opts_download["ratelimit"] = rate
      
        if self.task.audio_only:
            ydl_opts_download.update({
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }
                ]
            })
        else:
            ydl_opts_download["format"] = "bestvideo+bestaudio/best" 
            ydl_opts_download["merge_output_format"] = "mp4"
        try:
            with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                ydl.download([self.task.url])
                self.status_signal.emit("Download Completed")
                self.log_signal.emit(f"Download Completed: {title} by {channel}")
        except yt_dlp.utils.DownloadError as e:
            if self.cancel:
                self.status_signal.emit("Download Cancelled")
                self.log_signal.emit(f"Download Cancelled: {title} by {channel}")
            else:
                self.status_signal.emit("Download Error")
                self.log_signal.emit(f"Download Error for {title} by {channel}: {str(e)}")
        except Exception as e:
            self.status_signal.emit("Download Error")
            self.log_signal.emit(f"Unexpected Error for {title} by {channel}: {str(e)}")

    def progress_hook(self, d):
        if self.cancel:
            raise yt_dlp.utils.DownloadError("Cancelled")
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes", 1)
            percent = (downloaded / total) * 100 if total > 0 else 0
            speed = d.get("speed", 0) or 0
            speed_mb = speed / 1024 / 1024
            filename = os.path.basename(d.get("filename", "File"))
            self.partial_files.append(d.get("filename"))
           
            server_ip = self.get_server_ip(d.get("url"))
            request_type = "HTTPS" if d.get("protocol") == "https" else "HTTP"
            self.progress_signal.emit(percent, speed_mb, filename, server_ip, request_type)
        while self.pause:
            QTimer.singleShot(100, lambda: None)

    def get_server_ip(self, url):
        try:
            hostname = url.split("//")[1].split("/")[0]
            ip = socket.gethostbyname(hostname)
            return ip
        except:
            return "Unknown"

    def pause_download(self):
        self.pause = True
        self.status_signal.emit("Download Paused")
        self.log_signal.emit("Download Paused")

    def resume_download(self):
        self.pause = False
        self.status_signal.emit("Download Resumed")
        self.log_signal.emit("Download Resumed")

    def cancel_download(self):
        self.cancel = True
        for f in set(self.partial_files):
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        self.status_signal.emit("Download Cancelled")
        self.log_signal.emit("Download Cancelled")

    def convert_bandwidth(self, b):
        if not b or b.lower() == "high performance":
            return None
        elif b.lower() == "balanced":
            return 5_000_000  
        else:
            return 1_000_000  

class MainWindow(QMainWindow):
    progress_signal = pyqtSignal(float, float, str, str, str)
    status_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.active_workers = []
        self.max_concurrent_downloads = 3
        self.bandwidth = "High Performance"
        self.download_history = []
        self.setWindowTitle("YoutubeGO4.0")
        self.setGeometry(100, 100, 1280, 800)
        self.progress_signal.connect(self.update_progress)
        self.status_signal.connect(self.update_status)
        self.log_signal.connect(self.append_log)
        self.current_theme = "Dark"
        self.user_profile = UserProfile()
        self.setup_ui()

    def setup_ui(self):
        self.setup_theme()
        self.setup_menubar()
        self.setup_statusbar()
        self.create_dock_log()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(10)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)

        self.profile_widget = QWidget()
        profile_layout = QVBoxLayout(self.profile_widget)
        profile_layout.setAlignment(Qt.AlignCenter)
        profile_layout.setContentsMargins(0, 0, 0, 0)

        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(100, 100)
        self.profile_pic_label.setScaledContents(True)
        if self.user_profile.data["profile_picture"] and os.path.exists(self.user_profile.data["profile_picture"]):
            pixmap = QPixmap(self.user_profile.data["profile_picture"])
        else:
            pixmap = QPixmap(100, 100)
            pixmap.fill(QColor("#555555"))
        self.profile_pic_label.setPixmap(pixmap)
        profile_layout.addWidget(self.profile_pic_label)

        self.profile_name_label = QLabel(self.user_profile.data["name"] if self.user_profile.data["name"] else "User Name")
        self.profile_name_label.setAlignment(Qt.AlignCenter)
        self.profile_name_label.setFont(QFont("Arial", 12, QFont.Bold))
        profile_layout.addWidget(self.profile_name_label)

        self.profile_widget.setCursor(Qt.PointingHandCursor)
        self.profile_widget.mousePressEvent = self.edit_user_profile
        sidebar_layout.addWidget(self.profile_widget)

       
        separator = QLabel()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #444444;")
        sidebar_layout.addWidget(separator)

        self.sidebar = QListWidget()
        self.sidebar.setSelectionMode(QAbstractItemView.SingleSelection)
        self.sidebar.setFixedWidth(180)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                color: white;
                border: none;
            }
            QListWidget::item:selected {
                background-color: rgba(68, 68, 68, 150);
                border-radius: 10px;
            }
        """)


        nav_items = ["Download MP4", "Download MP3", "History", "Settings", "Queue"]
        for item_name in nav_items:
            item = QListWidgetItem(item_name)
            self.sidebar.addItem(item)

        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self.sidebar_changed)
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addStretch()

        main_layout.addLayout(sidebar_layout)

        self.central_content = QStackedWidget()
        main_layout.addWidget(self.central_content)

        self.page_mp4 = self.create_mp4_page()
        self.page_mp3 = self.create_mp3_page()
        self.page_history = self.create_history_page()
        self.page_settings = self.create_settings_page()
        self.page_queue = self.create_queue_page()

        self.central_content.addWidget(self.page_mp4)
        self.central_content.addWidget(self.page_mp3)
        self.central_content.addWidget(self.page_history)
        self.central_content.addWidget(self.page_settings)
        self.central_content.addWidget(self.page_queue)

        if not self.user_profile.is_profile_complete():
            self.prompt_user_profile()

    def setup_theme(self):
        apply_theme(QApplication.instance(), self.current_theme)

    def setup_menubar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

     
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Quit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)


        help_menu = menu_bar.addMenu("Help")
        insta_action = QAction("Instagram: fntxii", self)
        insta_action.triggered.connect(lambda: QMessageBox.information(self, "Instagram", "Follow us on Instagram: fntxii"))
        help_menu.addAction(insta_action)

        mail_action = QAction("E-Mail: toxi360@workmail.com", self)
        mail_action.triggered.connect(lambda: QMessageBox.information(self, "E-Mail", "Contact us at: toxi360@workmail.com"))
        help_menu.addAction(mail_action)

    def setup_statusbar(self):
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(250)
        self.progress_bar.setValue(0)
        status_bar.addPermanentWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)

    def create_dock_log(self):
        self.log_dock = QDockWidget("Log", self)
        self.log_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setStyleSheet("background-color: #2d2d2d; color: white;")

        self.log_dock.setWidget(self.log_text_edit)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)

    def sidebar_changed(self, index):
        self.central_content.setCurrentIndex(index)

    def create_mp4_page(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(20)
        lay.setContentsMargins(20, 20, 20, 20)

        form_box = QGroupBox("Download MP4")
        form_lay = QFormLayout(form_box)
        form_lay.setSpacing(15)

        self.mp4_url_label = QLabel("URL:")
        self.mp4_url = DragDropLineEdit()
        form_lay.addRow(self.mp4_url_label, self.mp4_url)

        form_box.setLayout(form_lay)
        lay.addWidget(form_box)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(20)

        b_single = QPushButton("Download Single MP4")
        b_single.setToolTip("Download a single MP4 video")
        b_single.clicked.connect(lambda: self.start_download_simple(self.mp4_url, False, False))
        btn_box.addWidget(b_single)

        b_playlist = QPushButton("Download Playlist MP4")
        b_playlist.setToolTip("Download an entire MP4 playlist")
        b_playlist.clicked.connect(lambda: self.start_download_simple(self.mp4_url, False, True))
        btn_box.addWidget(b_playlist)

    
        b_pause = QPushButton("Pause")
        b_pause.setToolTip("Pause active downloads")
        b_pause.clicked.connect(self.pause_active)
        btn_box.addWidget(b_pause)

        b_cancel = QPushButton("Cancel")
        b_cancel.setToolTip("Cancel active downloads")
        b_cancel.clicked.connect(self.cancel_active)
        btn_box.addWidget(b_cancel)

        lay.addLayout(btn_box)
        lay.addStretch()
        return w

    def create_mp3_page(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(20)
        lay.setContentsMargins(20, 20, 20, 20)

        form_box = QGroupBox("Download MP3")
        form_lay = QFormLayout(form_box)
        form_lay.setSpacing(15)

        self.mp3_url_label = QLabel("URL:")
        self.mp3_url = DragDropLineEdit()
        form_lay.addRow(self.mp3_url_label, self.mp3_url)

        form_box.setLayout(form_lay)
        lay.addWidget(form_box)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(20)

        b_single = QPushButton("Download Single MP3")
        b_single.setToolTip("Download a single MP3 audio")
        b_single.clicked.connect(lambda: self.start_download_simple(self.mp3_url, True, False))
        btn_box.addWidget(b_single)

        b_playlist = QPushButton("Download Playlist MP3")
        b_playlist.setToolTip("Download an entire MP3 playlist")
        b_playlist.clicked.connect(lambda: self.start_download_simple(self.mp3_url, True, True))
        btn_box.addWidget(b_playlist)

      
        b_pause = QPushButton("Pause")
        b_pause.setToolTip("Pause active downloads")
        b_pause.clicked.connect(self.pause_active)
        btn_box.addWidget(b_pause)

        b_cancel = QPushButton("Cancel")
        b_cancel.setToolTip("Cancel active downloads")
        b_cancel.clicked.connect(self.cancel_active)
        btn_box.addWidget(b_cancel)

        lay.addLayout(btn_box)
        lay.addStretch()
        return w

    def create_history_page(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(15)
        lay.setContentsMargins(20, 20, 20, 20)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)  
        self.history_table.setHorizontalHeaderLabels([
            "Title",
            "Channel",
            "URL",
            "Status"
        ])
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #3c3f41;
                color: white;
                border-radius: 10px;
            }
            QTableWidget::item {
                border: none;
            }
        """)
        hh = self.history_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch) 
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents) 
        hh.setSectionResizeMode(2, QHeaderView.Stretch) 
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents) 
        lay.addWidget(self.history_table)

       
        history_btn_layout = QHBoxLayout()
        b_delete_selected = QPushButton("Delete Selected")
        b_delete_selected.setToolTip("Delete selected history entries")
        b_delete_selected.clicked.connect(self.delete_selected_history)
        history_btn_layout.addWidget(b_delete_selected)

        b_delete_all = QPushButton("Delete All")
        b_delete_all.setToolTip("Delete all history entries")
        b_delete_all.clicked.connect(self.delete_all_history)
        history_btn_layout.addWidget(b_delete_all)

        c_history_enabled = QCheckBox("Enable History Logging")
        c_history_enabled.setChecked(self.user_profile.is_history_enabled())
        c_history_enabled.setToolTip("Enable or disable history logging")
        c_history_enabled.stateChanged.connect(self.toggle_history_logging)
        history_btn_layout.addWidget(c_history_enabled)

        lay.addLayout(history_btn_layout)

  
        srch_box = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter search term...")
        b_srch = QPushButton("Search")
        b_srch.setToolTip("Search History")
        b_srch.clicked.connect(self.search_history)
        srch_box.addWidget(self.search_box)
        srch_box.addWidget(b_srch)
        lay.addLayout(srch_box)
        lay.addStretch()
        return w

    def create_settings_page(self):
        w = QWidget()
        main_lay = QVBoxLayout(w)
        main_lay.setSpacing(20)
        main_lay.setContentsMargins(20, 20, 20, 20)

       
        concurrent_grp = QGroupBox("Max Concurrent Downloads")
        concurrent_layout = QHBoxLayout(concurrent_grp)
        concurrent_layout.setSpacing(15)

        self.concurrent_combo = QComboBox()
        self.concurrent_combo.addItems(['1', '2', '3', '4', '5'])
        self.concurrent_combo.setCurrentText(str(self.max_concurrent_downloads))
        self.concurrent_combo.setToolTip("Set Maximum Concurrent Downloads")
        self.concurrent_combo.currentIndexChanged.connect(self.set_max_concurrent_downloads)
        concurrent_layout.addWidget(QLabel("Set Maximum Concurrent Downloads:"))
        concurrent_layout.addWidget(self.concurrent_combo)
        concurrent_grp.setLayout(concurrent_layout)
        main_lay.addWidget(concurrent_grp)
        technical_grp = QGroupBox("Technical Settings")
        technical_layout = QFormLayout(technical_grp)
        technical_layout.setSpacing(15)
        self.speed_limit_edit = QLineEdit()
        self.speed_limit_edit.setPlaceholderText("e.g., 5MB/s")
        self.speed_limit_edit.setToolTip("Set download speed limit (e.g., 5MB/s)")
        technical_layout.addRow("Download Speed Limit:", self.speed_limit_edit)
        technical_grp.setLayout(technical_layout)
        main_lay.addWidget(technical_grp)
        resolution_grp = QGroupBox("Resolution Selection")
        resolution_layout = QHBoxLayout(resolution_grp)
        resolution_layout.setSpacing(15)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "144p",
            "240p",
            "360p",
            "480p",
            "720p",
            "1080p",
            "1440p",
            "2160p",
            "4320p"
        ])
        self.resolution_combo.setToolTip("Select Default Download Resolution")
        self.resolution_combo.setCurrentText(self.user_profile.get_default_resolution())
        resolution_layout.addWidget(QLabel("Default Resolution:"))
        resolution_layout.addWidget(self.resolution_combo)

        self.apply_resolution_btn = QPushButton("Apply")
        self.apply_resolution_btn.setToolTip("Apply Resolution Settings")
        self.apply_resolution_btn.clicked.connect(self.apply_resolution_settings)
        resolution_layout.addWidget(self.apply_resolution_btn)
        resolution_grp.setLayout(resolution_layout)
        main_lay.addWidget(resolution_grp)
        download_path_grp = QGroupBox("Download Path")
        download_path_layout = QHBoxLayout(download_path_grp)
        download_path_layout.setSpacing(15)

        self.download_path_edit = QLineEdit()
        self.download_path_edit.setText(self.user_profile.get_download_path())
        self.download_path_edit.setToolTip("Current Download Path")
        self.download_path_edit.setReadOnly(True)

        b_browse_download = QPushButton("Browse")
        b_browse_download.setToolTip("Select Download Folder")
        b_browse_download.clicked.connect(self.select_download_path)

        download_path_layout.addWidget(QLabel("Download Path:"))
        download_path_layout.addWidget(self.download_path_edit)
        download_path_layout.addWidget(b_browse_download)

        download_path_grp.setLayout(download_path_layout)
        main_lay.addWidget(download_path_grp)

        main_lay.addStretch()
        return w

    def create_queue_page(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(15)
        lay.setContentsMargins(20, 20, 20, 20)

        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(5)  
        self.queue_table.setHorizontalHeaderLabels([
            "Title",
            "Channel",
            "URL",
            "Type",
            "Progress"
        ])
        self.queue_table.setStyleSheet("""
            QTableWidget {
                background-color: #3c3f41;
                color: white;
                border-radius: 10px;
            }
            QTableWidget::item {
                border: none;
            }
        """)
        hh = self.queue_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)  
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)  
        hh.setSectionResizeMode(2, QHeaderView.Stretch)  
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents) 
        hh.setSectionResizeMode(4, QHeaderView.Stretch)  
        lay.addWidget(self.queue_table)

        btn_line = QHBoxLayout()
        btn_line.setSpacing(20)

        b_add = QPushButton("Add to Queue")
        b_add.setToolTip("Add download to queue")
        b_add.clicked.connect(self.add_queue_item_dialog)
        btn_line.addWidget(b_add)

        b_start = QPushButton("Start Queue")
        b_start.setToolTip("Start queued downloads")
        b_start.clicked.connect(self.start_queue)
        btn_line.addWidget(b_start)

       
        b_pause = QPushButton("Pause All")
        b_pause.setToolTip("Pause all active downloads")
        b_pause.clicked.connect(self.pause_active)
        btn_line.addWidget(b_pause)

        b_resume = QPushButton("Resume All")
        b_resume.setToolTip("Resume all paused downloads")
        b_resume.clicked.connect(self.resume_active)
        btn_line.addWidget(b_resume)

        b_cancel = QPushButton("Cancel All")
        b_cancel.setToolTip("Cancel all active downloads")
        b_cancel.clicked.connect(self.cancel_active)
        btn_line.addWidget(b_cancel)

        lay.addLayout(btn_line)
        lay.addStretch()
        return w

    def prompt_user_profile(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create User Profile")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)

        form = QFormLayout()
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter your name")
        form.addRow("Name:", name_edit)

        pic_button = QPushButton("Select Profile Picture")
        pic_button.setToolTip("Choose a profile picture")
        pic_path_label = QLabel("No file selected.")
        pic_path_label.setWordWrap(True)
        pic_button.clicked.connect(lambda: self.select_profile_picture(pic_path_label))

        pic_layout = QHBoxLayout()
        pic_layout.addWidget(pic_button)
        pic_layout.addWidget(pic_path_label)
        form.addRow("Profile Picture:", pic_layout)


        download_path_button = QPushButton("Select Download Path")
        download_path_button.setToolTip("Choose the default download folder")
        download_path_label = QLabel(os.getcwd())
        download_path_label.setWordWrap(True)
        download_path_button.clicked.connect(lambda: self.select_download_path_initial(download_path_label))

        download_path_layout = QHBoxLayout()
        download_path_layout.addWidget(download_path_button)
        download_path_layout.addWidget(download_path_label)
        form.addRow("Download Path:", download_path_layout)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(lambda: self.save_user_profile(dialog, name_edit, pic_path_label, download_path_label))
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)

        dialog.exec_()

    def select_profile_picture(self, label):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_path:
            label.setText(os.path.basename(file_path))
            label.setProperty("selected_path", file_path)

    def select_download_path_initial(self, label):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            label.setText(folder)
            label.setProperty("selected_path", folder)

    def select_download_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.download_path_edit.setText(folder)
            self.user_profile.set_download_path(folder)
            self.append_log(f"Download path set to: {folder}")

    def save_user_profile(self, dialog, name_edit, pic_label, download_path_label):
        name = name_edit.text().strip()
        pic_path = pic_label.property("selected_path")
        download_path = download_path_label.property("selected_path") or os.getcwd()
        if not name:
            QMessageBox.warning(dialog, "Input Error", "Please enter your name.")
            return
        if not pic_path or not os.path.exists(pic_path):
            QMessageBox.warning(dialog, "Input Error", "Please select a valid profile picture.")
            return
        dest_pic = os.path.join(os.getcwd(), "profile_pic" + os.path.splitext(pic_path)[1])
        try:
            with open(pic_path, 'rb') as f_src, open(dest_pic, 'wb') as f_dst:
                f_dst.write(f_src.read())
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Failed to copy profile picture: {str(e)}")
            return
        self.user_profile.set_profile(name, dest_pic, download_path)
        self.update_profile_ui()
        dialog.accept()

    def update_profile_ui(self):
        if self.user_profile.data["profile_picture"] and os.path.exists(self.user_profile.data["profile_picture"]):
            pixmap = QPixmap(self.user_profile.data["profile_picture"])
        else:
            pixmap = QPixmap(100, 100)
            pixmap.fill(QColor("#555555"))
        self.profile_pic_label.setPixmap(pixmap)
        self.profile_name_label.setText(self.user_profile.data["name"])
        self.download_path_edit.setText(self.user_profile.get_download_path())

    def edit_user_profile(self, event):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit User Profile")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)

        form = QFormLayout()
        name_edit = QLineEdit()
        name_edit.setText(self.user_profile.data["name"])
        form.addRow("Name:", name_edit)

        pic_button = QPushButton("Change Profile Picture")
        pic_button.setToolTip("Choose a new profile picture")
        pic_path_label = QLabel(os.path.basename(self.user_profile.data["profile_picture"]) if self.user_profile.data["profile_picture"] else "No file selected.")
        pic_path_label.setWordWrap(True)
        pic_button.clicked.connect(lambda: self.select_profile_picture(pic_path_label))

        pic_layout = QHBoxLayout()
        pic_layout.addWidget(pic_button)
        pic_layout.addWidget(pic_path_label)
        form.addRow("Profile Picture:", pic_layout)

       
        download_path_button = QPushButton("Change Download Path")
        download_path_button.setToolTip("Choose a new download folder")
        download_path_label = QLabel(self.user_profile.get_download_path())
        download_path_label.setWordWrap(True)
        download_path_button.clicked.connect(lambda: self.select_download_path_edit(download_path_label))

        download_path_layout = QHBoxLayout()
        download_path_layout.addWidget(download_path_button)
        download_path_layout.addWidget(download_path_label)
        form.addRow("Download Path:", download_path_layout)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(lambda: self.update_user_profile(dialog, name_edit, pic_path_label, download_path_label))
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)

        dialog.exec_()

    def select_download_path_edit(self, label):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            label.setText(folder)
            label.setProperty("selected_path", folder)

    def update_user_profile(self, dialog, name_edit, pic_label, download_path_label):
        name = name_edit.text().strip()
        pic_path = pic_label.property("selected_path")
        download_path = download_path_label.property("selected_path") or self.user_profile.get_download_path()
        if not name:
            QMessageBox.warning(dialog, "Input Error", "Please enter your name.")
            return
        if pic_path and not os.path.exists(pic_path):
            QMessageBox.warning(dialog, "Input Error", "Please select a valid profile picture.")
            return
        if pic_path:
            dest_pic = os.path.join(os.getcwd(), "profile_pic" + os.path.splitext(pic_path)[1])
            try:
                with open(pic_path, 'rb') as f_src, open(dest_pic, 'wb') as f_dst:
                    f_dst.write(f_src.read())
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to copy profile picture: {str(e)}")
                return
        else:
            dest_pic = self.user_profile.data["profile_picture"]
        self.user_profile.set_profile(name, dest_pic, download_path)
        self.update_profile_ui()
        dialog.accept()

    def add_history_entry(self, title, channel, url, stat):
        if not self.user_profile.is_history_enabled():
            return  

        row = self.history_table.rowCount()
        self.history_table.insertRow(row)

   
        self.history_table.setItem(row, 0, QTableWidgetItem(title))

        
        self.history_table.setItem(row, 1, QTableWidgetItem(channel))

    
        self.history_table.setItem(row, 2, QTableWidgetItem(url))

        self.history_table.setItem(row, 3, QTableWidgetItem(stat))

    def add_queue_item_dialog(self):
        d = QDialog(self)
        d.setWindowTitle("Add Download")
        d.setModal(True)
        ly = QVBoxLayout(d)

        form = QFormLayout()
        dd_url = DragDropLineEdit()
        dd_url.setPlaceholderText("Enter download URL or drag it here")
        dd_url.setObjectName("queue_url")

        c_audio = QCheckBox("Audio Only")
        c_audio.setToolTip("Download audio file only (MP3)")
        c_audio.setObjectName("queue_audio_only")

        c_pl = QCheckBox("Playlist")
        c_pl.setToolTip("Download all items in a playlist")
        c_pl.setObjectName("queue_playlist")

        form.addRow(QLabel("URL:"), dd_url)
        form.addRow(c_audio)
        form.addRow(c_pl)
        ly.addLayout(form)

        b_ok = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        def on_ok():
            uu = dd_url.text().strip()
            ao = c_audio.isChecked()
            pl = c_pl.isChecked()

            if not uu:
                QMessageBox.warning(d, "Input Error", "No URL specified.")
                return
            if not (uu.startswith("http://") or uu.startswith("https://")):
                QMessageBox.warning(d, "Input Error", "Invalid URL format. Please enter a valid HTTP or HTTPS URL.")
                return

    
            task = DownloadTask(uu, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(), ao, pl, self.bandwidth)
            self.queue_table.insertRow(self.queue_table.rowCount())
            row = self.queue_table.rowCount() - 1

            
            self.queue_table.setItem(row, 0, QTableWidgetItem("Fetching..."))

            self.queue_table.setItem(row, 1, QTableWidgetItem("Fetching..."))

            self.queue_table.setItem(row, 2, QTableWidgetItem(uu))

            dtp = "Audio" if ao else "Video"
            if pl:
                dtp += " - Playlist"
            self.queue_table.setItem(row, 3, QTableWidgetItem(dtp))


            progress_bar = QProgressBar()
            progress_bar.setValue(0)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #e74c3c;
                    border-radius: 5px;
                }
            """)
            self.queue_table.setCellWidget(row, 4, progress_bar)

            self.add_history_entry("Fetching...", "Fetching...", uu, "Queued")
            self.run_task(task, row)
            d.accept()

        def on_cancel():
            d.reject()

        b_ok.accepted.connect(on_ok)
        b_ok.rejected.connect(on_cancel)
        ly.addWidget(b_ok)
        d.exec_()

    def start_queue(self):
        for r in range(self.queue_table.rowCount()):
            st = self.queue_table.item(r, 3)
            if st and st.text() == "Queued" and len(self.active_workers) < self.max_concurrent_downloads:
                title = self.queue_table.item(r, 0).text().strip()
                channel = self.queue_table.item(r, 1).text().strip()
                url = self.queue_table.item(r, 2).text().strip()
                dtp = self.queue_table.item(r, 3).text().lower()
                audio = "audio" in dtp
                playlist = "playlist" in dtp

      
                task = DownloadTask(url, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(), audio, playlist, self.bandwidth)
                self.run_task(task, r)
                self.queue_table.setItem(r, 3, QTableWidgetItem("Started"))

    def set_max_concurrent_downloads(self, index):
        value = self.concurrent_combo.currentText()
        self.max_concurrent_downloads = int(value)
        self.append_log(f"Max concurrent downloads set to {value}")

    def set_default_resolution(self, resolution):
        self.append_log(f"Default resolution set to {resolution}")

    def apply_resolution_settings(self):
        selected_resolution = self.resolution_combo.currentText()
        self.user_profile.set_default_resolution(selected_resolution)
        self.append_log(f"Resolution settings applied: {selected_resolution}")
        QMessageBox.information(self, "Settings Applied", f"Resolution has been set to {selected_resolution}.")

    def append_log(self, text):
        if any(word in text for word in ["Error", "Hata", "Fehler"]):
            color = "red"
        elif any(word in text for word in ["Warning", "Uyarı"]):
            color = "yellow"
        elif any(word in text for word in ["Started", "Completed", "Applied", "Queued", "Fetching"]):
            color = "green"
        elif any(word in text for word in ["Cancelled"]):
            color = "orange"
        else:
            color = "white"
        self.log_text_edit.setTextColor(QColor(color))
        self.log_text_edit.append(text)
        self.log_text_edit.setTextColor(QColor("white"))

    def delete_selected_history(self):
        selected_rows = set()
        for item in self.history_table.selectedItems():
            selected_rows.add(item.row())
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one entry to delete.")
            return
        for row in sorted(selected_rows, reverse=True):
            self.history_table.removeRow(row)
        self.append_log(f"Deleted {len(selected_rows)} selected history entries.")

    def delete_all_history(self):
        reply = QMessageBox.question(self, "Delete All", "Are you sure you want to delete all history entries?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history_table.setRowCount(0)
            self.append_log("All history entries have been deleted.")

    def toggle_history_logging(self, state):
        enabled = state == Qt.Checked
        self.user_profile.set_history_enabled(enabled)
        status = "enabled" if enabled else "disabled"
        self.append_log(f"History logging has been {status}.")

    def search_history(self):
        txt = self.search_box.text().strip().lower()
        for r in range(self.history_table.rowCount()):
            title = self.history_table.item(r, 0)
            channel = self.history_table.item(r, 1)
            url = self.history_table.item(r, 2)
            status = self.history_table.item(r, 3)
            hide = True
            if title and channel and url and status:
                if (txt in title.text().lower()) or (txt in channel.text().lower()) or (txt in url.text().lower()) or (txt in status.text().lower()):
                    hide = False
            self.history_table.setRowHidden(r, hide)

    def change_theme(self, theme):
        self.current_theme = theme
        apply_theme(QApplication.instance(), theme)
        self.append_log(f"Theme changed to '{theme}'.")
        sidebar_style = """
            QListWidget {
                background-color: transparent;
                color: white;
                border: none;
            }
            QListWidget::item:selected {
                background-color: rgba(68, 68, 68, 150);
                border-radius: 10px;
            }
        """
        self.sidebar.setStyleSheet(sidebar_style)

    def closeEvent(self, event):
        event.accept()

    def start_download_simple(self, url_edit, audio, playlist):
        u = url_edit.text().strip()
        if not u:
            QMessageBox.warning(self, "Warning", "No URL specified.")
            return
        if not (u.startswith("http://") or u.startswith("https://")):
            QMessageBox.warning(self, "Input Error", "Invalid URL format. Please enter a valid HTTP or HTTPS URL.")
            return

    
        task = DownloadTask(u, self.user_profile.get_default_resolution(), self.user_profile.get_download_path(), audio, playlist, self.bandwidth)
        self.queue_table.insertRow(self.queue_table.rowCount())
        row = self.queue_table.rowCount() - 1

      
        self.queue_table.setItem(row, 0, QTableWidgetItem("Fetching..."))

  
        self.queue_table.setItem(row, 1, QTableWidgetItem("Fetching..."))

  
        self.queue_table.setItem(row, 2, QTableWidgetItem(u))

        dtp = "Audio" if audio else "Video"
        if playlist:
            dtp += " - Playlist"
        self.queue_table.setItem(row, 3, QTableWidgetItem(dtp))

       
        progress_bar = QProgressBar()
        progress_bar.setValue(0)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #e74c3c;
                border-radius: 5px;
            }
        """)
        self.queue_table.setCellWidget(row, 4, progress_bar)

        self.add_history_entry("Fetching...", "Fetching...", u, "Queued")
        self.run_task(task, row)

    def run_task(self, task, row):
        worker = DownloadQueueWorker(task, self.progress_signal, self.status_signal, self.log_signal)
        self.threadpool.start(worker)
        if row is not None:
            self.active_workers.append(worker)

    def update_progress(self, percent, speed, title, server_ip, request_type):
        self.progress_bar.setValue(int(min(percent, 100)))
        self.status_label.setText(f"{title} - {percent:.2f}% @ {speed:.2f} MB/s")
        self.append_log(f"Downloading {title} - Server IP: {server_ip} - Request Type: {request_type}")

    def update_status(self, st):
        self.status_label.setText(f"{st}")
        if "Error" in st:
            QMessageBox.critical(self, "Error", st)
        elif "Completed" in st:
            QMessageBox.information(self, "Completed", "Download Completed Successfully!")

    def pause_active(self):
        for worker in self.active_workers:
            worker.pause_download()

    def resume_active(self):
        for worker in self.active_workers:
            worker.resume_download()

    def cancel_active(self):
        for worker in self.active_workers:
            worker.cancel_download()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
#                                                                             TOXİ360                                                                                                   # 
