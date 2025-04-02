from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt

class DragAndDropLineEdit(QLineEdit):
    def __init__(self,placeholder="Enter or drag a link here..."):
        super().__init__()
        self.setAcceptDrops(True)
        self.setPlaceholderText(placeholder)
    def dragEnterEvent(self,event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    def dropEvent(self,event):
        text=event.mimeData().text().strip()
        if text.startswith("http"):
            self.setText(text)
        else:
            self.setText(text.replace("file://",""))
