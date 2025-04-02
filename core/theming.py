def apply_theme(application,theme_mode):
    if theme_mode=="Dark":
        style_sheet="""
        QMainWindow, QDialog, QDockWidget { background-color: #181818; border-radius: 25px; }
        QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QTableWidget, QComboBox, QCheckBox {
            color: #ffffff; background-color: #202020; border: none; border-radius: 25px;
        }
        QLineEdit { border: 1px solid #333; padding: 6px; }
        QPushButton { background-color: #cc0000; padding: 8px 12px; border-radius: 25px; }
        QPushButton:hover { background-color: #b30000; }
        QListWidget::item { padding: 10px; border-radius: 25px; }
        QListWidget::item:selected { background-color: #333333; border-left: 3px solid #cc0000; border-radius: 25px; }
        QProgressBar { background-color: #333333; text-align: center; color: #ffffff; font-weight: bold; border-radius: 25px; }
        QProgressBar::chunk { background-color: #cc0000; border-radius: 25px; }
        QMenuBar, QMenu { background-color: #181818; color: #ffffff; border-radius: 25px; }
        QHeaderView::section { background-color: #333333; color: white; padding: 4px; border: 1px solid #444444; border-radius: 25px; }
        """
    else:
        style_sheet="""
        QMainWindow, QDialog, QDockWidget { background-color: #f2f2f2; border-radius: 25px; }
        QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QTableWidget, QComboBox, QCheckBox {
            color: #000000; background-color: #ffffff; border: 1px solid #ccc; border-radius: 25px;
        }
        QLineEdit { padding: 6px; }
        QPushButton { background-color: #e0e0e0; padding: 8px 12px; border-radius: 25px; }
        QPushButton:hover { background-color: #cccccc; }
        QListWidget::item { padding: 10px; border-radius: 25px; }
        QListWidget::item:selected { background-color: #ddd; border-left: 3px solid #888; border-radius: 25px; }
        QProgressBar { text-align: center; font-weight: bold; border-radius: 25px; }
        QHeaderView::section { background-color: #f0f0f0; color: black; padding: 4px; border: 1px solid #ccc; border-radius: 25px; }
        """
    application.setStyleSheet(style_sheet)
