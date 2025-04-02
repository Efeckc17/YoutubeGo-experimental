from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont

def create_home_page(main_window):
    page=QWidget()
    layout=QVBoxLayout(page)
    label=QLabel(main_window._("Home Page - Welcome to YoutubeGO Experimental\nThis version is experimental and may be unstable."))
    label.setFont(QFont("Arial",16))
    layout.addWidget(label)
    layout.addStretch()
    return page
