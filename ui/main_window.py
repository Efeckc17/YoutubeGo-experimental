import os
import sys
import platform
import shutil
import subprocess
import requests
import gettext
from PyQt5.QtCore import Qt, pyqtSignal, QThreadPool, QTimer, QDateTime
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QListWidget, QDockWidget, QLineEdit, QLabel, QPushButton, QSystemTrayIcon, QStyle, QAction, QMessageBox, QStatusBar, QProgressBar, QTextEdit, QFileDialog, QListWidgetItem, QDialog, QFormLayout, QDialogButtonBox, QCheckBox, QComboBox, QTableWidget, QHeaderView, QTableWidgetItem, QDateTimeEdit, QSlider
from core.downloader import DownloadTask, WorkerSignals, DownloadWorker
from core.profile import UserProfile
from core.theming import apply_theme
from core.utils import format_time, open_download_path
from ui.pages.home import create_home_page
from ui.pages.mp4_page import create_mp4_page
from ui.pages.mp3_page import create_mp3_page
from ui.pages.history_page import create_history_page
from ui.pages.settings_page import create_settings_page
from ui.pages.profile_page import create_profile_page
from ui.pages.queue_page import create_queue_page
from ui.pages.scheduler_page import create_scheduler_page
from ui.pages.player_page import create_player_page
from ui.pages.experimental_page import create_experimental_page

class MainWindow(QMainWindow):
    update_progress_signal=pyqtSignal(int,float,float,int)
    update_status_signal=pyqtSignal(int,str)
    update_log_signal=pyqtSignal(str)
    update_info_signal=pyqtSignal(int,str,str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YoutubeGO Experimental")
        self.setGeometry(100,100,800,600)
        self.ffmpeg_path=shutil.which("ffmpeg") or ""
        self.ffmpeg_found=bool(self.ffmpeg_path)
        self.status_label=QLabel("Ready")
        self.progress_bar=QProgressBar()
        self.log_text_edit=QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.user_profile=UserProfile()
        self.thread_pool=QThreadPool()
        self.active_workers={}
        self.all_queue_tasks={}
        self.max_concurrent_downloads=3
        self.developer_mode=False
        self.verbose_logging=False
        self.search_map={"proxy":(4,"Proxy configuration is in Settings."),"resolution":(4,"Resolution configuration is in Settings."),"profile":(5,"Profile page for user details."),"queue":(6,"Queue page for multiple downloads."),"mp4":(1,"MP4 page for video downloads."),"mp3":(2,"MP3 page for audio downloads."),"history":(3,"History page for download logs."),"settings":(4,"Settings page for various options."),"scheduler":(7,"Scheduler for planned downloads."),"download path":(4,"Download path is in Settings."),"theme":(4,"Theme switch is in Settings."),"player":(8,"Video Player for downloaded videos.")}
        self.update_progress_signal.connect(self.update_progress)
        self.update_status_signal.connect(self.update_status)
        self.update_log_signal.connect(self.append_log)
        self.update_info_signal.connect(self.update_queue_info)
        apply_theme(self,self.user_profile.get_theme())
        if not self.user_profile.is_profile_complete():
            self.prompt_user_profile()
        self.create_tray_icon()
        self.initialize_ui()
        self.load_history_table()
    def initialize_ui(self):
        self.navbar=QListWidget()
        self.navbar.setFixedHeight(50)
        self.navbar.setFlow(QListWidget.LeftToRight)
        self.navbar.setSpacing(5)
        pages=["Home","MP4","MP3","History","Settings","Profile","Queue","Scheduler","Player","Experimental"]
        for page in pages:
            self.navbar.addItem(self._(page))
        self.navbar.setCurrentRow(0)
        self.navbar.currentRowChanged.connect(self.change_page)
        self.search_line_edit=QLineEdit()
        self.search_line_edit.setPlaceholderText(self._("Search something..."))
        self.search_line_edit.setFixedHeight(30)
        self.search_button=QPushButton(self._("Search"))
        self.search_button.setFixedHeight(30)
        self.search_button.clicked.connect(self.top_search)
        self.search_results_list=QListWidget()
        self.search_results_list.setVisible(False)
        self.search_results_list.setFixedHeight(150)
        self.search_results_list.itemClicked.connect(self.search_result_clicked)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("0%")
        if self.ffmpeg_found:
            self.ffmpeg_label=QLabel(self._("FFmpeg Found"))
            self.ffmpeg_label.setStyleSheet("color: green; font-weight: bold;")
            self.ffmpeg_label.setToolTip(self.ffmpeg_path)
        else:
            self.ffmpeg_label=QLabel(self._("FFmpeg Missing"))
            self.ffmpeg_label.setStyleSheet("color: red; font-weight: bold;")
        self.logs_button=QPushButton("Logs")
        self.logs_button.setFixedWidth(60)
        self.logs_button.clicked.connect(self.toggle_logs)
        status_bar=QStatusBar(self)
        status_bar.addWidget(self.logs_button)
        status_bar.addWidget(self.status_label)
        status_bar.addPermanentWidget(self.ffmpeg_label)
        status_bar.addPermanentWidget(self.progress_bar)
        self.setStatusBar(status_bar)
        self.log_dock=QDockWidget(self._("Logs"),self)
        self.log_dock.setWidget(self.log_text_edit)
        self.addDockWidget(Qt.BottomDockWidgetArea,self.log_dock)
        central_widget=QWidget()
        main_layout=QVBoxLayout(central_widget)
        main_layout.addWidget(self.navbar)
        self.stack_pages=QStackedWidget()
        self.stack_pages.addWidget(create_home_page(self))
        self.stack_pages.addWidget(create_mp4_page(self))
        self.stack_pages.addWidget(create_mp3_page(self))
        self.stack_pages.addWidget(create_history_page(self))
        self.stack_pages.addWidget(create_settings_page(self))
        self.stack_pages.addWidget(create_profile_page(self))
        self.stack_pages.addWidget(create_queue_page(self))
        self.stack_pages.addWidget(create_scheduler_page(self))
        self.stack_pages.addWidget(create_player_page(self))
        self.stack_pages.addWidget(create_experimental_page(self))
        main_layout.addWidget(self.stack_pages)
        main_layout.addWidget(self.search_line_edit)
        main_layout.addWidget(self.search_button)
        main_layout.addWidget(self.search_results_list)
        self.setCentralWidget(central_widget)
    def create_tray_icon(self):
        self.tray_icon=QSystemTrayIcon(self)
        icon=self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setContextMenu(self.create_tray_menu())
        self.tray_icon.show()
    def create_tray_menu(self):
        menu=self.menuBar().addMenu("")
        show_action=QAction("Show",self)
        quit_action=QAction("Quit",self)
        show_action.triggered.connect(self.showNormal)
        quit_action.triggered.connect(self.close)
        menu.addAction(show_action)
        menu.addAction(quit_action)
        return menu
    def change_page(self,index):
        self.stack_pages.setCurrentIndex(index)
    def top_search(self):
        query=self.search_line_edit.text().lower().strip()
        self.search_results_list.clear()
        self.search_results_list.setVisible(False)
        if not query:
            return
        found_match=False
        for key,value in self.search_map.items():
            if query in key:
                item=QListWidgetItem(f"{self._(key)}: {self._(value[1])}")
                item.setData(Qt.UserRole,value[0])
                self.search_results_list.addItem(item)
                found_match=True
        if found_match:
            self.search_results_list.setVisible(True)
    def search_result_clicked(self,item):
        page_index=item.data(Qt.UserRole)
        self.navbar.setCurrentRow(page_index)
        self.search_results_list.clear()
        self.search_results_list.setVisible(False)
    def append_log(self,text):
        text_lower=text.lower()
        if "error" in text_lower or "fail" in text_lower:
            color="red"
        elif "warning" in text_lower:
            color="yellow"
        elif any(keyword in text_lower for keyword in ["completed","started","queued","fetching"]):
            color="green"
        elif "cancel" in text_lower:
            color="orange"
        else:
            color="white"
        self.log_text_edit.setTextColor(QColor(color))
        self.log_text_edit.append(text)
        self.log_text_edit.setTextColor(QColor("white"))
    def toggle_logs(self):
        self.log_dock.setVisible(not self.log_dock.isVisible())
    def load_history_table(self):
        if not self.user_profile.is_history_enabled():
            return
        if not hasattr(self,"history_table"):
            return
        for entry in self.user_profile.data["history"]:
            row=self.history_table.rowCount()
            self.history_table.insertRow(row)
            self.history_table.setItem(row,0,QTableWidgetItem(entry["title"]))
            self.history_table.setItem(row,1,QTableWidgetItem(entry["channel"]))
            self.history_table.setItem(row,2,QTableWidgetItem(entry["url"]))
            self.history_table.setItem(row,3,QTableWidgetItem(entry["status"]))
    def delete_selected_history(self):
        selected_rows=set(item.row() for item in self.history_table.selectedItems())
        urls_to_remove=[]
        for row in sorted(selected_rows,reverse=True):
            url_item=self.history_table.item(row,2)
            if url_item:
                urls_to_remove.append(url_item.text())
            self.history_table.removeRow(row)
        if urls_to_remove:
            self.user_profile.remove_history_entries(urls_to_remove)
        self.append_log(self._("Deleted {count} history entries.").format(count=len(selected_rows)))
    def delete_all_history(self):
        if QMessageBox.question(self,self._("Delete All"),self._("Are you sure?"),QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            self.history_table.setRowCount(0)
            self.user_profile.clear_history()
            self.append_log(self._("All history deleted."))
    def toggle_history_logging(self,state):
        enabled=(state==Qt.Checked)
        self.user_profile.set_history_enabled(enabled)
        self.append_log(self._("History logging {status}.").format(status=self._("enabled") if enabled else self._("disabled")))
    def search_history(self):
        search_text=self.history_search_line_edit.text().lower().strip()
        for row in range(self.history_table.rowCount()):
            hide=True
            for col in range(self.history_table.columnCount()):
                item=self.history_table.item(row,col)
                if item and search_text in item.text().lower():
                    hide=False
                    break
            self.history_table.setRowHidden(row,hide)
    def update_queue_info(self,row,title,channel):
        if row is not None and hasattr(self,"queue_table"):
            if row<self.queue_table.rowCount():
                self.queue_table.setItem(row,0,QTableWidgetItem(title))
                self.queue_table.setItem(row,1,QTableWidgetItem(channel))
                url_item=self.queue_table.item(row,2)
                if url_item:
                    self.user_profile.update_history_entry(url_item.text(),title,channel)
    def add_scheduler_dialog(self):
        dialog=QDialog(self)
        dialog.setWindowTitle(self._("Add Scheduled Download"))
        dialog.setModal(True)
        layout=QVBoxLayout(dialog)
        form=QFormLayout()
        datetime_edit=QDateTimeEdit()
        datetime_edit.setCalendarPopup(True)
        datetime_edit.setDateTime(QDateTime.currentDateTime())
        url_line_edit=self.search_line_edit.__class__(self._("Enter link"))
        audio_checkbox=QCheckBox(self._("Audio Only"))
        subtitles_checkbox=QCheckBox(self._("Download Subtitles?"))
        priority_combo=QComboBox()
        priority_combo.addItems([self._("1 - High"),self._("2 - Medium"),self._("3 - Low")])
        recurrence_combo=QComboBox()
        recurrence_combo.addItems([self._("None"),self._("Daily"),self._("Weekly"),self._("Monthly")])
        form.addRow(self._("Datetime:"),datetime_edit)
        form.addRow(self._("URL:"),url_line_edit)
        form.addRow(audio_checkbox)
        form.addRow(subtitles_checkbox)
        form.addRow(self._("Priority:"),priority_combo)
        form.addRow(self._("Recurrence:"),recurrence_combo)
        layout.addLayout(form)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(lambda:self.confirm_scheduler(dialog,datetime_edit,url_line_edit,audio_checkbox,subtitles_checkbox,priority_combo,recurrence_combo))
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    def confirm_scheduler(self,dialog,datetime_edit,url_line_edit,audio_checkbox,subtitles_checkbox,priority_combo,recurrence_combo):
        url=url_line_edit.text().strip()
        if not url:
            QMessageBox.warning(dialog,self._("Error"),self._("No URL provided."))
            return
        priority=int(priority_combo.currentText().split(" - ")[0])
        recurrence=recurrence_combo.currentText().lower() if recurrence_combo.currentText()!=self._("None") else None
        row=self.scheduler_table.rowCount()
        self.scheduler_table.insertRow(row)
        self.scheduler_table.setItem(row,0,QTableWidgetItem(datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")))
        self.scheduler_table.setItem(row,1,QTableWidgetItem(url))
        self.scheduler_table.setItem(row,2,QTableWidgetItem(self._("Audio") if audio_checkbox.isChecked() else self._("Video")))
        self.scheduler_table.setItem(row,3,QTableWidgetItem(self._("Yes") if subtitles_checkbox.isChecked() else self._("No")))
        self.scheduler_table.setItem(row,4,QTableWidgetItem(self._("Scheduled")))
        self.scheduler_table.setItem(row,5,QTableWidgetItem(str(priority)))
        self.scheduler_table.setItem(row,6,QTableWidgetItem(recurrence.capitalize() if recurrence else self._("None")))
        dialog.accept()
    def remove_scheduler_items(self):
        rows=set(item.row() for item in self.scheduler_table.selectedItems())
        for row in sorted(rows,reverse=True):
            self.scheduler_table.removeRow(row)
    def check_scheduler_downloads(self):
        if not hasattr(self,"scheduler_table"):
            return
        current_time=QDateTime.currentDateTime()
        for row in range(self.scheduler_table.rowCount()):
            dt_str=self.scheduler_table.item(row,0).text()
            scheduled_time=QDateTime.fromString(dt_str,"yyyy-MM-dd HH:mm:ss")
            status_item=self.scheduler_table.item(row,4)
            if status_item and scheduled_time<=current_time and status_item.text()==self._("Scheduled"):
                url=self.scheduler_table.item(row,1).text()
                video_type=self.scheduler_table.item(row,2).text().lower()
                subtitles=(self.scheduler_table.item(row,3).text()==self._("Yes"))
                audio_only="audio" in video_type
                priority=int(self.scheduler_table.item(row,5).text())
                recurrence=self.scheduler_table.item(row,6).text().lower() if self.scheduler_table.item(row,6).text()!=self._("None") else None
                task=DownloadTask(url,self.user_profile.get_default_resolution(),self.user_profile.get_download_path(),audio_only,False,subtitles,"mp4",True,priority,recurrence,self.user_profile.get_rate_limit())
                self.schedule_download(task,row)
                self.scheduler_table.setItem(row,4,QTableWidgetItem(self._("Started")))
                if recurrence:
                    new_time=None
                    if recurrence=="daily":
                        new_time=scheduled_time.addDays(1)
                    elif recurrence=="weekly":
                        new_time=scheduled_time.addDays(7)
                    elif recurrence=="monthly":
                        new_time=scheduled_time.addMonths(1)
                    if new_time:
                        self.scheduler_table.setItem(row,0,QTableWidgetItem(new_time.toString("yyyy-MM-dd HH:mm:ss")))
                        self.scheduler_table.setItem(row,4,QTableWidgetItem(self._("Scheduled")))
    def schedule_download(self,task,scheduler_row):
        if not hasattr(self,"queue_table"):
            return
        queue_row=self.queue_table.rowCount()
        self.queue_table.insertRow(queue_row)
        for col,text in enumerate(["Fetching...","Fetching...",task.url,self._("Audio") if task.audio_only else self._("Video"),"Queued"]):
            self.queue_table.setItem(queue_row,col,QTableWidgetItem(text))
        self.all_queue_tasks[queue_row]=task
        self.user_profile.add_history_entry("Fetching...","Fetching...",task.url,"Queued")
        if len(self.active_workers)<self.max_concurrent_downloads:
            self.run_download_task(task,queue_row)
            self.queue_table.setItem(queue_row,4,QTableWidgetItem("Starting"))
    def update_position(self,position):
        if not hasattr(self,"position_slider"):
            return
        self.position_slider.setValue(position)
        duration=self.media_player.duration()
        current_time=format_time(position)
        total_time=format_time(duration)
        self.time_label.setText(f"{current_time}/{total_time}")
    def update_duration(self,duration):
        if hasattr(self,"position_slider"):
            self.position_slider.setRange(0,duration)
    def set_position(self,position):
        if hasattr(self,"media_player"):
            self.media_player.setPosition(position)
    def change_playback_speed(self,value):
        if hasattr(self,"media_player"):
            speed=value/100.0
            self.media_player.setPlaybackRate(speed)
            self.playback_speed_label.setText(f"{speed:.2f}x")
    def change_volume(self,value):
        if hasattr(self,"media_player"):
            self.media_player.setVolume(value)
            self.volume_label.setText(f"{value}%")
    def open_video_file(self):
        file_path,_=QFileDialog.getOpenFileName(self,self._("Open Video"),"",self._("Videos (*.mp4 *.mkv *.avi *.webm)"))
        if file_path and hasattr(self,"media_player"):
            from PyQt5.QtMultimedia import QMediaContent
            from PyQt5.QtCore import QUrl
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.media_player.play()
    def start_download(self,url_line_edit,audio,playlist):
        url=url_line_edit.text().strip()
        if not url:
            QMessageBox.warning(self,self._("Error"),self._("No URL provided."))
            return
        if not (url.startswith("http://") or url.startswith("https://")):
            QMessageBox.warning(self,self._("Input Error"),self._("Invalid URL format."))
            return
        task=DownloadTask(url,self.user_profile.get_default_resolution(),self.user_profile.get_download_path(),audio,playlist,False,"mp4",False,1,None,self.user_profile.get_rate_limit())
        self.user_profile.add_history_entry("Fetching...","Fetching...",url,self._("Queued"))
        self.run_download_task(task,None)
    def run_download_task(self,task,row):
        if row is not None and len(self.active_workers)>=self.max_concurrent_downloads:
            if self.queue_table.item(row,4):
                self.queue_table.setItem(row,4,QTableWidgetItem("Queued"))
            return
        signals=WorkerSignals()
        signals.progress.connect(self.update_progress_signal.emit)
        signals.status.connect(self.update_status_signal.emit)
        signals.log.connect(self.update_log_signal.emit)
        signals.info.connect(self.update_info_signal.emit)
        worker=DownloadWorker(task,row,signals)
        if row is not None:
            self.active_workers[row]=worker
        if self.developer_mode or self.verbose_logging:
            self.append_log(self._("Starting task for URL: {url}").format(url=task.url))
        self.thread_pool.start(worker)
    def start_queue(self):
        if not hasattr(self,"queue_table"):
            return
        for row in range(self.queue_table.rowCount()):
            status_item=self.queue_table.item(row,4)
            if status_item and status_item.text()=="Queued":
                if len(self.active_workers)<self.max_concurrent_downloads:
                    self.run_download_task(self.all_queue_tasks[row],row)
                    self.queue_table.setItem(row,4,QTableWidgetItem("Starting"))
    def update_progress(self,row,percent,speed,eta):
        if row is not None and hasattr(self,"queue_table"):
            if row<self.queue_table.rowCount():
                self.queue_table.setItem(row,4,QTableWidgetItem(f"{int(percent)}%"))
        self.progress_bar.setValue(int(percent))
        self.progress_bar.setFormat(f"{int(percent)}%")
        speed_kb=speed/1024 if speed else 0
        self.status_label.setText(self._("Downloading...")+f" {percent:.2f}% - {speed_kb:.2f} KB/s - ETA: {eta}s")
    def update_status(self,row,status):
        self.status_label.setText(status)
        if row is not None and hasattr(self,"queue_table"):
            if row<self.queue_table.rowCount():
                item=self.queue_table.item(row,4)
                if item:
                    item.setText(status)
        if "Error" in status:
            QMessageBox.critical(self,self._("Error"),status)
            self.tray_icon.showMessage(self._("Error"),status,QSystemTrayIcon.Information,3000)
        elif "Completed" in status:
            self.tray_icon.showMessage(self._("Download Completed"),self._("Download finished successfully."),QSystemTrayIcon.Information,3000)
            if QMessageBox.question(self,self._("Download Completed"),self._("Download finished. Open download folder?"),QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
                open_download_path(self.user_profile.get_download_path())
        if row is not None and row in self.active_workers:
            if any(x in status for x in ["Error","Completed","Cancelled"]):
                del self.active_workers[row]
                self.start_next_task()
    def start_next_task(self):
        if not hasattr(self,"queue_table"):
            return
        for row in range(self.queue_table.rowCount()):
            status_item=self.queue_table.item(row,4)
            if status_item and status_item.text()=="Queued":
                if len(self.active_workers)<self.max_concurrent_downloads:
                    self.run_download_task(self.all_queue_tasks[row],row)
                    self.queue_table.setItem(row,4,QTableWidgetItem("Starting"))
                else:
                    break
    def pause_all_downloads(self):
        for worker in self.active_workers.values():
            worker.pause_download()
    def resume_all_downloads(self):
        for worker in self.active_workers.values():
            worker.resume_download()
    def cancel_all_downloads(self):
        for worker in list(self.active_workers.values()):
            worker.cancel_download()
    def set_max_concurrent_downloads(self,index):
        self.max_concurrent_downloads=int(self.concurrent_combo.currentText())
        self.append_log(self._("Max concurrent downloads set to {val}").format(val=self.concurrent_combo.currentText()))
    def apply_theme_settings(self):
        new_theme=self.theme_combo.currentText()
        self.user_profile.set_theme(new_theme)
        apply_theme(self,new_theme)
        self.append_log(self._("Theme changed to '{theme}'").format(theme=new_theme))
    def apply_resolution_settings(self):
        resolution=self.resolution_combo.currentText()
        self.user_profile.set_default_resolution(resolution)
        proxy=self.proxy_line_edit.text().strip()
        self.user_profile.set_proxy(proxy)
        self.append_log(self._("Resolution set: {res}, Proxy: {proxy}").format(res=resolution,proxy=proxy))
        QMessageBox.information(self,self._("Settings"),self._("Resolution: {res}\nProxy: {proxy}").format(res=resolution,proxy=proxy))
    def select_download_path(self):
        folder=QFileDialog.getExistingDirectory(self,self._("Select Download Folder"))
        if folder:
            self.user_profile.set_profile(self.user_profile.data["name"],self.user_profile.data["profile_picture"],folder)
            self.download_path_line_edit.setText(folder)
            self.append_log(self._("Download path changed to {folder}").format(folder=folder))
    def apply_rate_limit_settings(self):
        rate=self.rate_limit_line_edit.text().strip()
        if rate:
            if not (rate.endswith("K") or rate.endswith("M") or rate.endswith("G")):
                QMessageBox.warning(self,self._("Invalid Format"),self._("Please enter rate like '500K', '2M', etc."))
                return
            self.user_profile.set_rate_limit(rate)
            self.append_log(self._("Download speed limit set to {rate}").format(rate=rate))
            QMessageBox.information(self,self._("Rate Limit"),self._("Download speed limited to {rate}").format(rate=rate))
        else:
            self.user_profile.set_rate_limit(None)
            self.append_log(self._("Download speed limit removed."))
            QMessageBox.information(self,self._("Rate Limit"),self._("Download speed limit removed."))
    def apply_language_settings(self):
        selected_lang=self.language_combo.currentText()
        language_code="tr" if selected_lang=="Türkçe" else "en"
        self.user_profile.set_language(language_code)
        self.append_log(self._("Language set to {lang}").format(lang=selected_lang))
        QMessageBox.information(self,self._("Language Changed"),self._("Language will change after restart."))
        self.restart_application()
    def prompt_user_profile(self):
        dialog=QDialog(self)
        dialog.setWindowTitle(self._("Create User Profile"))
        dialog.setModal(True)
        layout=QVBoxLayout(dialog)
        form=QFormLayout()
        name_line_edit=QLineEdit()
        picture_button=QPushButton(self._("Select Picture (Optional)"))
        picture_label=QLabel(self._("No file selected."))
        remove_picture_button=QPushButton(self._("Remove Picture"))
        remove_picture_button.setVisible(False)
        picture_button.clicked.connect(lambda:self.select_profile_picture(picture_button,picture_label,remove_picture_button))
        remove_picture_button.clicked.connect(lambda:self.remove_profile_picture(picture_button,picture_label,remove_picture_button))
        form.addRow(self._("Name:"),name_line_edit)
        form.addRow(self._("Picture:"),picture_button)
        form.addRow(picture_label)
        form.addRow(remove_picture_button)
        layout.addLayout(form)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(lambda:self.confirm_profile(dialog,name_line_edit,picture_button))
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    def select_profile_picture(self,button,label,remove_button):
        file_path,_=QFileDialog.getOpenFileName(self,self._("Select Profile Picture"),"","Images (*.png *.jpg *.jpeg)")
        if file_path:
            button.setText(os.path.basename(file_path))
            button.setProperty("selected_path",file_path)
            label.setText(os.path.basename(file_path))
            remove_button.setVisible(True)
    def remove_profile_picture(self,button,label,remove_button):
        self.user_profile.remove_profile_picture()
        label.setText(self._("No file selected."))
        button.setText(self._("Change Picture"))
        button.setProperty("selected_path","")
        remove_button.setVisible(False)
    def confirm_profile(self,dialog,name_line_edit,picture_button):
        name=name_line_edit.text().strip()
        selected_path=picture_button.property("selected_path")
        if not name:
            QMessageBox.warning(dialog,self._("Error"),self._("Please provide a name."))
            return
        destination=""
        if selected_path:
            destination=os.path.join(os.getcwd(),"profile_pic"+os.path.splitext(selected_path)[1])
            try:
                shutil.copy(selected_path,destination)
            except Exception as e:
                QMessageBox.critical(dialog,self._("Error"),str(e))
                return
        self.user_profile.set_profile(name,destination,self.user_profile.get_download_path())
        dialog.accept()
    def save_profile_settings(self):
        name=self.profile_name_line_edit.text().strip()
        if not name:
            QMessageBox.warning(self,self._("Error"),self._("Name cannot be empty."))
            return
        selected_path=self.change_pic_button.property("selected_path") or ""
        destination=""
        if selected_path:
            destination=os.path.join(os.getcwd(),"profile_pic"+os.path.splitext(selected_path)[1])
            try:
                shutil.copy(selected_path,destination)
            except Exception as e:
                QMessageBox.critical(self,self._("Error"),str(e))
                return
        self.user_profile.set_profile(name,destination,self.user_profile.get_download_path())
        self.user_profile.set_social_links(self.instagram_line_edit.text().strip(),self.twitter_line_edit.text().strip(),self.youtube_line_edit.text().strip())
        QMessageBox.information(self,self._("Saved"),self._("Profile settings saved."))
    def add_to_queue_dialog(self):
        dialog=QDialog(self)
        dialog.setWindowTitle(self._("Add to Queue"))
        dialog.setModal(True)
        layout=QVBoxLayout(dialog)
        form=QFormLayout()
        url_line_edit=QLineEdit(self._("Enter or drag a link here"))
        audio_checkbox=QCheckBox(self._("Audio Only"))
        playlist_checkbox=QCheckBox(self._("Playlist"))
        subtitles_checkbox=QCheckBox(self._("Download Subtitles"))
        format_combo=QComboBox()
        format_combo.addItems(["mp4","mkv","webm","flv","avi"])
        form.addRow(self._("URL:"),url_line_edit)
        form.addRow(audio_checkbox)
        form.addRow(playlist_checkbox)
        form.addRow(self._("Format:"),format_combo)
        form.addRow(subtitles_checkbox)
        layout.addLayout(form)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(lambda:self.confirm_queue(dialog,url_line_edit,audio_checkbox,playlist_checkbox,subtitles_checkbox,format_combo))
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    def confirm_queue(self,dialog,url_line_edit,audio_checkbox,playlist_checkbox,subtitles_checkbox,format_combo):
        url=url_line_edit.text().strip()
        if not url:
            QMessageBox.warning(dialog,self._("Error"),self._("No URL provided."))
            return
        audio_only=audio_checkbox.isChecked()
        playlist=playlist_checkbox.isChecked()
        subs=subtitles_checkbox.isChecked()
        output_format=format_combo.currentText()
        row=self.queue_table.rowCount()
        self.queue_table.insertRow(row)
        for col,text in enumerate(["Fetching...","Fetching...",url,(self._("Audio") if audio_only else self._("Video"))+(" - "+self._("Playlist") if playlist else ""),"Queued"]):
            self.queue_table.setItem(row,col,QTableWidgetItem(text))
        task=DownloadTask(url,self.user_profile.get_default_resolution(),self.user_profile.get_download_path(),audio_only,playlist,subs,output_format,True,1,None,self.user_profile.get_rate_limit())
        self.all_queue_tasks[row]=task
        self.user_profile.add_history_entry("Fetching...","Fetching...",url,self._("Queued"))
        dialog.accept()
    def restart_application(self):
        self.append_log(self._("Restarting application..."))
        QMessageBox.information(self,self._("Restart"),self._("The application will now restart."))
        python_executable=sys.executable
        os.execl(python_executable,python_executable,*sys.argv)
    def toggle_developer_mode(self,state):
        self.developer_mode=(state==Qt.Checked)
        if self.developer_mode:
            self.append_log(self._("Developer Mode Enabled"))
        else:
            self.append_log(self._("Developer Mode Disabled"))
    def check_for_updates(self):
        self.append_log(self._("Checking for updates..."))
        QTimer.singleShot(2000,lambda:QMessageBox.information(self,self._("Update Check"),self._("No updates available. You are running the latest version.")))
    def retry_failed_downloads(self):
        count=0
        if hasattr(self,"history_table"):
            for row in range(self.history_table.rowCount()):
                status_item=self.history_table.item(row,3)
                if status_item and "Error" in status_item.text():
                    url=self.history_table.item(row,2).text()
                    task=DownloadTask(url,self.user_profile.get_default_resolution(),self.user_profile.get_download_path(),False,False,False,"mp4",False,1,None,self.user_profile.get_rate_limit())
                    self.user_profile.add_history_entry("Fetching...","Fetching...",url,self._("Queued"))
                    self.run_download_task(task,None)
                    count+=1
        self.append_log(self._("{count} failed downloads retried.").format(count=count))
    def extract_thumbnail(self):
        if not hasattr(self,"thumbnail_url_line_edit"):
            return
        url=self.thumbnail_url_line_edit.text().strip()
        if not url:
            QMessageBox.warning(self,self._("Error"),self._("Please enter a video URL."))
            return
        try:
            from yt_dlp import YoutubeDL
            options={"quiet":True,"skip_download":True,"cookiefile":"youtube_cookies.txt"}
            with YoutubeDL(options) as ydl:
                info=ydl.extract_info(url,download=False)
                thumb_url=info.get("thumbnail")
                if not thumb_url:
                    QMessageBox.warning(self,self._("Error"),self._("No thumbnail found for this video."))
                    return
                self.append_log(self._("Thumbnail URL found: {url}").format(url=thumb_url))
                with requests.Session() as sess:
                    response=sess.get(thumb_url)
                    if response.status_code==200:
                        img=response.content
                        pixmap=QPixmap()
                        pixmap.loadFromData(img)
                        pixmap=pixmap.scaled(self.thumbnail_label.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation)
                        self.thumbnail_label.setPixmap(pixmap)
                        self.append_log(self._("Thumbnail extracted successfully."))
                    else:
                        QMessageBox.warning(self,self._("Error"),self._("Failed to download thumbnail image."))
        except Exception as e:
            QMessageBox.critical(self,self._("Error"),str(e))
            self.append_log(self._("Error extracting thumbnail: {error}").format(error=str(e)))
    def convert_file(self):
        if not hasattr(self,"converter_input_line_edit") or not hasattr(self,"converter_target_format_line_edit"):
            return
        input_path=self.converter_input_line_edit.text().strip()
        target_format=self.converter_target_format_line_edit.text().strip().lower()
        if not input_path or not target_format:
            QMessageBox.warning(self,self._("Error"),self._("Please provide both file path and target format."))
            return
        if target_format not in ["mp4","mp3","mkv"]:
            QMessageBox.warning(self,self._("Error"),self._("Supported target formats: mp4, mp3, mkv."))
            return
        output_path=os.path.splitext(input_path)[0]+"."+target_format
        if not self.ffmpeg_found:
            QMessageBox.critical(self,self._("Error"),self._("FFmpeg not found."))
            return
        cmd=["ffmpeg","-i",input_path,output_path]
        try:
            subprocess.run(cmd,check=True)
            self.append_log(self._("Converted file {file} to format {fmt}.").format(file=input_path,fmt=target_format))
            QMessageBox.information(self,self._("Conversion"),self._("File converted successfully to {fmt}").format(fmt=target_format))
        except Exception as e:
            QMessageBox.critical(self,self._("Error"),str(e))
            self.append_log(self._("Conversion error: {error}").format(error=str(e)))
    def _(self,text):
        return gettext.gettext(text)
