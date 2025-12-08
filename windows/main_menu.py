import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSettings

from .settings_window import SettingsWindow
from .main_window import MainWindow

# Путь к файлу статистики
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # .../windows
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)                   # .../ (корень проекта)
STATS_FILE = os.path.join(PROJECT_ROOT, 'data', 'stats.json')

# Главное меню шахматного приложения с запуском игры, настройками и статистикой
class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        # путь к ui
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        ui_path = os.path.join(project_root, 'ui', 'main_menu.ui')

        # Загрузка интерфейса из UI файла
        loadUi(ui_path, self)

        # Инициализация окна игры и настроек
        self.game_window = None
        self.settings = QSettings('MyChessApp', 'ChessSettings')

        # Подключение обработчиков кнопок
        self.connect_buttons()

    # Подключение кнопок главного меню'
    def connect_buttons(self):
        self.startGameButton.clicked.connect(self.start_game)
        self.settingsButton.clicked.connect(self.open_settings)
        self.statsButton.clicked.connect(self.open_stats)
        self.exitButton.clicked.connect(self.close)

    # Статистика
    def load_stats(self) -> dict:
        # Проверка существования файла статистики
        if not os.path.exists(STATS_FILE):
            return {}
        try:
            # Чтение и парсинг JSON файла
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                import json
                return json.load(f)
        except Exception:
            # Возврат пустой статистики при ошибке чтения
            return {}

    # Формирование текстовой строки статистики игрока
    def get_player_stats_text(self, player_name: str) -> str:
        stats = self.load_stats()
        player_stats = stats.get(player_name, {'wins': 0, 'losses': 0, 'draws': 0})
        wins = player_stats.get('wins', 0)
        losses = player_stats.get('losses', 0)
        draws = player_stats.get('draws', 0)
        return f'{player_name}: {wins} побед, {losses} поражений, {draws} ничьих'

    # Запуск новой игры
    def start_game(self):
        # Получение имен игроков из полей ввода
        white_name = self.whitePlayerEdit.text().strip() or 'Белые'
        black_name = self.blackPlayerEdit.text().strip() or 'Чёрные'

        # Валидация имен игроков
        if not white_name or not black_name or white_name == black_name:
            QMessageBox.warning(self, 'Ошибка', 'Введите корректные имена игроков')
            return

        try:
            # Создание и отображение окна игры
            game_window = MainWindow(
                white_name=white_name,
                black_name=black_name,
                parent=self,
            )
            self.game_window = game_window
            self.game_window.show()
            self.hide()
        except ImportError:
            QMessageBox.warning(self, 'Ошибка', 'Файл main_window.py не найден')
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка запуска игры: {str(e)}')

    # Открытие окна настроек из главного меню
    def open_settings(self):
        try:
            # Создание и отображение окна настроек
            settings_window = SettingsWindow(parent=self)
            settings_window.show()
        except ImportError:
            QMessageBox.warning(self, 'Ошибка', 'Окно настроек недоступно')
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка настроек: {str(e)}')

    # Отображение статистики игроков
    def open_stats(self):
        # Получение текущих имен игроков
        white_name = self.whitePlayerEdit.text().strip() or 'Белые'
        black_name = self.blackPlayerEdit.text().strip() or 'Чёрные'

        # Формирование текста статистики
        white_stats = self.get_player_stats_text(white_name)
        black_stats = self.get_player_stats_text(black_name)

        # Отображение статистики в диалоговом окне
        QMessageBox.information(
            self,
            'Статистика игроков',
            f'{white_stats}\n\n{black_stats}',
        )

    # Обработка закрытия главного меню
    def closeEvent(self, event):
        if self.game_window:
            self.game_window.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainMenu()
    w.show()
    sys.exit(app.exec_())
