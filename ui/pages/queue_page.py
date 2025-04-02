from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView

def create_queue_page(main_window):
    page=QWidget()
    layout=QVBoxLayout(page)
    label=QLabel(main_window._("Download Queue"))
    layout.addWidget(label)
    main_window.queue_table=QTableWidget()
    main_window.queue_table.setColumnCount(5)
    main_window.queue_table.setHorizontalHeaderLabels([main_window._("Title"),main_window._("Channel"),main_window._("URL"),main_window._("Type"),main_window._("Progress")])
    header=main_window.queue_table.horizontalHeader()
    header.setSectionResizeMode(0,QHeaderView.Stretch)
    header.setSectionResizeMode(1,QHeaderView.ResizeToContents)
    header.setSectionResizeMode(2,QHeaderView.Stretch)
    header.setSectionResizeMode(3,QHeaderView.ResizeToContents)
    header.setSectionResizeMode(4,QHeaderView.Stretch)
    layout.addWidget(main_window.queue_table)
    button_layout=QHBoxLayout()
    add_queue_button=QPushButton(main_window._("Add to Queue"))
    add_queue_button.clicked.connect(main_window.add_to_queue_dialog)
    start_queue_button=QPushButton(main_window._("Start Queue"))
    start_queue_button.clicked.connect(main_window.start_queue)
    pause_all_button=QPushButton(main_window._("Pause All"))
    pause_all_button.clicked.connect(main_window.pause_all_downloads)
    resume_all_button=QPushButton(main_window._("Resume All"))
    resume_all_button.clicked.connect(main_window.resume_all_downloads)
    cancel_all_button=QPushButton(main_window._("Cancel All"))
    cancel_all_button.clicked.connect(main_window.cancel_all_downloads)
    for btn in [add_queue_button,start_queue_button,pause_all_button,resume_all_button,cancel_all_button]:
        button_layout.addWidget(btn)
    layout.addLayout(button_layout)
    layout.addStretch()
    return page
