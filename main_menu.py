# main_menu.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi

from main_window import MainWindow


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("main_menu.ui", self)

        self.game_window = None

        self.startGameButton.clicked.connect(self.start_game)
        self.settingsButton.clicked.connect(self.open_settings)
        self.statsButton.clicked.connect(self.open_stats)
        self.exitButton.clicked.connect(self.close)

    def start_game(self):
        white_name = self.whitePlayerEdit.text().strip()
        black_name = self.blackPlayerEdit.text().strip()

        if white_name and black_name and white_name == black_name:
            QMessageBox.warning(
                self,
                "Ошибка имён",
                "Имена игроков не должны совпадать.\nВведите разные имена.",
            )
            return

        self.game_window = MainWindow(white_name, black_name, parent=self)
        self.game_window.show()
        self.hide()

    def open_settings(self):
        pass

    def open_stats(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainMenu()
    w.show()
    sys.exit(app.exec_())
