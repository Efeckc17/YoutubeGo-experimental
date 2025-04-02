from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QDialog, QDialogButtonBox, QFormLayout, QComboBox, QCheckBox
from PyQt5.QtCore import QTimer, QDateTime
from ui.widgets import DragAndDropLineEdit

def create_scheduler_page(main_window):
    page=QWidget()
    layout=QVBoxLayout(page)
    label=QLabel(main_window._("Scheduler (Planned Downloads)"))
    layout.addWidget(label)
    main_window.scheduler_table=QTableWidget()
    main_window.scheduler_table.setColumnCount(7)
    main_window.scheduler_table.setHorizontalHeaderLabels([main_window._("Datetime"),main_window._("URL"),main_window._("Type"),main_window._("Subtitles"),main_window._("Status"),main_window._("Priority"),main_window._("Recurrence")])
    header=main_window.scheduler_table.horizontalHeader()
    for i in range(7):
        header.setSectionResizeMode(i,QHeaderView.ResizeToContents)
    layout.addWidget(main_window.scheduler_table)
    button_layout=QHBoxLayout()
    add_scheduler_button=QPushButton(main_window._("Add Scheduled Download"))
    add_scheduler_button.clicked.connect(main_window.add_scheduler_dialog)
    remove_scheduler_button=QPushButton(main_window._("Remove Selected"))
    remove_scheduler_button.clicked.connect(main_window.remove_scheduler_items)
    button_layout.addWidget(add_scheduler_button)
    button_layout.addWidget(remove_scheduler_button)
    layout.addLayout(button_layout)
    main_window.scheduler_timer=QTimer()
    main_window.scheduler_timer.timeout.connect(main_window.check_scheduler_downloads)
    main_window.scheduler_timer.start(10000)
    layout.addStretch()
    return page
