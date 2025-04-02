import time
import os
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

class DownloadTask:
    def __init__(self,url,resolution,folder,audio_only=False,playlist=False,subtitles=False,output_format="mp4",from_queue=False,priority=1,recurrence=None,max_rate=None):
        self.url=url
        self.resolution=resolution
        self.folder=folder
        self.audio_only=audio_only
        self.playlist=playlist
        self.subtitles=subtitles
        self.output_format=output_format
        self.from_queue=from_queue
        self.priority=priority
        self.recurrence=recurrence
        self.max_rate=max_rate

class WorkerSignals(QObject):
    progress=pyqtSignal(int,float,float,int)
    status=pyqtSignal(int,str)
    log=pyqtSignal(str)
    info=pyqtSignal(int,str,str)

class DownloadWorker(QRunnable):
    cookie_text="# Netscape HTTP Cookie File\nyoutube.com\tFALSE\t/\tFALSE\t0\tCONSENT\tYES+42\n"
    def __init__(self,task,row,signals):
        super().__init__()
        self.task=task
        self.row=row
        self.signals=signals
        self.is_paused=False
        self.is_cancelled=False
        self.title="Fetching..."
        self.channel="Fetching..."
    def run(self):
        if not os.path.exists("youtube_cookies.txt"):
            with open("youtube_cookies.txt","w") as cf:
                cf.write(self.cookie_text)
        info_options={"quiet":True,"skip_download":True,"cookiefile":"youtube_cookies.txt"}
        try:
            with YoutubeDL(info_options) as ydl:
                info=ydl.extract_info(self.task.url,download=False)
                self.title=info.get("title","No Title")
                self.channel=info.get("uploader","Unknown Channel")
        except Exception as e:
            self.signals.status.emit(self.row,"Download Error")
            self.signals.log.emit("Failed to fetch info: "+str(e))
            if self.row is not None:
                self.signals.status.emit(self.row,"Info Extraction Error")
            return
        self.signals.info.emit(self.row,self.title,self.channel)
        download_options={"outtmpl":os.path.join(self.task.folder,"%(title)s.%(ext)s"),"progress_hooks":[self.progress_hook],"noplaylist":not self.task.playlist,"cookiefile":"youtube_cookies.txt","ratelimit":self.task.max_rate if self.task.max_rate else None}
        if self.task.audio_only:
            download_options["format"]="bestaudio/best"
            download_options["postprocessors"]=[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"192"}]
        else:
            if self.task.output_format.lower()=="mp4":
                download_options["format"]='bestvideo[vcodec*="avc1"]+bestaudio[acodec*="mp4a"]/best'
                download_options["merge_output_format"]="mp4"
            else:
                download_options["format"]="bestvideo+bestaudio/best"
                download_options["merge_output_format"]=self.task.output_format
        if self.task.subtitles:
            download_options["writesubtitles"]=True
            download_options["allsubtitles"]=True
        try:
            with YoutubeDL(download_options) as ydl:
                ydl.download([self.task.url])
            self.signals.status.emit(self.row,"Download Completed")
            self.signals.log.emit("Completed: "+self.title+" by "+self.channel)
        except DownloadError as e:
            if self.is_cancelled:
                self.signals.status.emit(self.row,"Download Cancelled")
                self.signals.log.emit("Cancelled: "+self.title+" by "+self.channel)
            else:
                self.signals.status.emit(self.row,"Download Error")
                self.signals.log.emit("Download Error: "+str(e))
        except Exception as e:
            self.signals.status.emit(self.row,"Download Error")
            self.signals.log.emit("Unexpected Error: "+str(e))
    def progress_hook(self,progress_data):
        if self.is_cancelled:
            raise DownloadError("Cancelled")
        while self.is_paused:
            time.sleep(1)
            if self.is_cancelled:
                raise DownloadError("Cancelled")
        if progress_data["status"]=="downloading":
            downloaded=progress_data.get("downloaded_bytes",0)
            total=progress_data.get("total_bytes") or progress_data.get("total_bytes_estimate",0)
            percent=(downloaded/total*100) if total else 0
            if percent>100:
                percent=100
            speed=progress_data.get("speed",0) or 0
            eta=progress_data.get("eta",0) or 0
            self.signals.progress.emit(self.row,percent,speed,eta)
    def pause_download(self):
        self.is_paused=True
        self.signals.status.emit(self.row,"Download Paused")
        self.signals.log.emit("Paused: "+self.title)
    def resume_download(self):
        self.is_paused=False
        self.signals.status.emit(self.row,"Download Resumed")
        self.signals.log.emit("Resumed: "+self.title)
    def cancel_download(self):
        self.is_cancelled=True
        self.signals.status.emit(self.row,"Download Cancelled")
        self.signals.log.emit("Cancelled: "+self.title)
