import sys
import os
import shutil
import platform
import subprocess
import gettext
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.profile import UserProfile

def main():
    app = QApplication(sys.argv)
    user_profile = UserProfile()
    locale_path = os.path.join(os.getcwd(), "assets", "locales")
    language = user_profile.get_language()
    try:
        translator = gettext.translation("base", localedir=locale_path, languages=[language])
        translator.install()
        _ = translator.gettext
    except FileNotFoundError:
        gettext.install("base")
        _ = gettext.gettext
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
