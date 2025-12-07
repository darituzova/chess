# settings_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSettings


class SettingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("settings_window.ui", self)

        self.settings = QSettings("MyChessApp", "ChessSettings")

        # загрузить сохранённый стиль (по умолчанию classic)
        piece_style = self.settings.value("piece_style", "classic")
        index = self.pieceStyleComboBox.findText(piece_style)
        if index != -1:
            self.pieceStyleComboBox.setCurrentIndex(index)

        self.saveButton.clicked.connect(self.save_settings)
        self.backButton.clicked.connect(self.close)

    def save_settings(self):
        style = self.pieceStyleComboBox.currentText()
        self.settings.setValue("piece_style", style)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SettingsWindow()
    w.show()
    sys.exit(app.exec_())
