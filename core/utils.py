import platform
import subprocess
import os

def format_time(milliseconds):
    seconds=milliseconds//1000
    minutes,sec=divmod(seconds,60)
    hours,minutes=divmod(minutes,60)
    if hours>0:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    else:
        return f"{minutes:02d}:{sec:02d}"

def open_download_path(folder):
    if platform.system()=="Windows":
        os.startfile(folder)
    elif platform.system()=="Darwin":
        subprocess.run(["open",folder])
    else:
        subprocess.run(["xdg-open",folder])
