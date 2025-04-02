from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from ui.widgets import DragAndDropLineEdit

def create_mp4_page(main_window):
    page=QWidget()
    layout=QVBoxLayout(page)
    label=QLabel(main_window._("Download MP4"))
    layout.addWidget(label)
    mp4_url_line_edit=DragAndDropLineEdit(main_window._("Paste or drag a link here..."))
    layout.addWidget(mp4_url_line_edit)
    button_layout=QHBoxLayout()
    download_single=QPushButton(main_window._("Download Single MP4"))
    download_single.clicked.connect(lambda:main_window.start_download(mp4_url_line_edit,False,False))
    download_playlist=QPushButton(main_window._("Download Playlist MP4"))
    download_playlist.clicked.connect(lambda:main_window.start_download(mp4_url_line_edit,False,True))
    pause_all=QPushButton(main_window._("Pause All"))
    pause_all.clicked.connect(main_window.pause_all_downloads)
    cancel_all=QPushButton(main_window._("Cancel All"))
    cancel_all.clicked.connect(main_window.cancel_all_downloads)
    for btn in [download_single,download_playlist,pause_all,cancel_all]:
        button_layout.addWidget(btn)
    layout.addLayout(button_layout)
    layout.addStretch()
    return page
