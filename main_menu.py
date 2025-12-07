# main_menu.py
import sys
import json
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi

from main_window import MainWindow
from settings_window import SettingsWindow


STATS_PATH = os.path.join("data", "stats.json")


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("main_menu.ui", self)

        self.game_window = None
        self.settings_window = None

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
        if self.settings_window is None:
            self.settings_window = SettingsWindow(parent=self)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def _load_stats(self):
        if not os.path.exists(STATS_PATH):
            return {}
        try:
            with open(STATS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

    def _format_player_stats(self, name, stats_dict):
        s = stats_dict.get(name, {"wins": 0, "losses": 0, "draws": 0})
        wins = s.get("wins", 0)
        losses = s.get("losses", 0)
        draws = s.get("draws", 0)
        # многострочная строка для одного игрока
        return (
            f"{name}:\n"
            f"  победы: {wins}\n"
            f"  поражения: {losses}\n"
            f"  ничьи: {draws}"
        )

    def open_stats(self):
        white_name = self.whitePlayerEdit.text().strip() or "Белые"
        black_name = self.blackPlayerEdit.text().strip() or "Чёрные"

        stats = self._load_stats()

        white_block = self._format_player_stats(white_name, stats)
        black_block = self._format_player_stats(black_name, stats)

        msg = (
            "Статистика игроков:\n\n"
            f"{white_block}\n\n"
            f"{black_block}"
        )

        QMessageBox.information(self, "Статистика", msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainMenu()
    w.show()
    sys.exit(app.exec_())
