import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSettings

from .settings_window import SettingsWindow
from .main_window import MainWindow

# ---------- путь к файлу статистики ----------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # .../windows
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)                   # .../ (корень проекта)
STATS_FILE = os.path.join(PROJECT_ROOT, "data", "stats.json")


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        # путь к ui
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        ui_path = os.path.join(project_root, "ui", "main_menu.ui")

        loadUi(ui_path, self)

        self.game_window = None
        self.settings = QSettings("MyChessApp", "ChessSettings")

        self.connect_buttons()

    # ---------- кнопки ----------
    def connect_buttons(self):
        """Подключение кнопок главного меню"""
        self.startGameButton.clicked.connect(self.start_game)
        self.settingsButton.clicked.connect(self.open_settings)
        self.statsButton.clicked.connect(self.open_stats)
        self.exitButton.clicked.connect(self.close)
        print("DEBUG: Кнопки главного меню подключены")

    # ---------- статистика ----------
    def load_stats(self) -> dict:
        """Загрузить статистику игроков из файла."""
        if not os.path.exists(STATS_FILE):
            return {}
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                import json
                return json.load(f)
        except Exception:
            return {}

    def get_player_stats_text(self, player_name: str) -> str:
        """Вернуть строку 'Имя: X побед, Y поражений, Z ничьих'."""
        stats = self.load_stats()
        player_stats = stats.get(player_name, {"wins": 0, "losses": 0, "draws": 0})
        wins = player_stats.get("wins", 0)
        losses = player_stats.get("losses", 0)
        draws = player_stats.get("draws", 0)
        return f"{player_name}: {wins} побед, {losses} поражений, {draws} ничьих"

    # ---------- обработчики ----------
    def start_game(self):
        """Запуск новой игры"""
        print("DEBUG: Кнопка 'Начать игру' нажата")

        white_name = self.whitePlayerEdit.text().strip() or "Белые"
        black_name = self.blackPlayerEdit.text().strip() or "Чёрные"

        if not white_name or not black_name or white_name == black_name:
            QMessageBox.warning(self, "Ошибка", "Введите корректные имена игроков")
            return

        try:
            game_window = MainWindow(
                white_name=white_name,
                black_name=black_name,
                parent=self,
            )
            self.game_window = game_window
            self.game_window.show()
            self.hide()
            print("DEBUG: Новая игра запущена")
        except ImportError:
            QMessageBox.warning(self, "Ошибка", "Файл main_window.py не найден")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка запуска игры: {str(e)}")

    def open_settings(self):
        """Открытие окна настроек из главного меню"""
        print("DEBUG: Кнопка 'Настройки' нажата в MainMenu")
        try:
            settings_window = SettingsWindow(parent=self)
            settings_window.show()
            print("DEBUG: Окно настроек открыто")
        except ImportError:
            print("DEBUG: Файл settings_window.py не найден")
            QMessageBox.warning(self, "Ошибка", "Окно настроек недоступно")
        except Exception as e:
            print(f"DEBUG: Ошибка открытия настроек: {e}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка настроек: {str(e)}")

    def open_stats(self):
        """Отображение статистики игроков"""
        print("DEBUG: Кнопка 'Статистика' нажата")

        white_name = self.whitePlayerEdit.text().strip() or "Белые"
        black_name = self.blackPlayerEdit.text().strip() or "Чёрные"

        white_stats = self.get_player_stats_text(white_name)
        black_stats = self.get_player_stats_text(black_name)

        QMessageBox.information(
            self,
            "Статистика игроков",
            f"{white_stats}\n\n{black_stats}",
        )

    def closeEvent(self, event):
        """Обработка закрытия главного меню"""
        print("DEBUG: Главное меню закрывается")
        if self.game_window:
            self.game_window.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainMenu()
    w.show()
    sys.exit(app.exec_())
