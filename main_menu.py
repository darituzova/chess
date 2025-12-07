import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox)
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSettings

from settings_window import SettingsWindow  # Импорт настроек

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("main_menu.ui", self)
        self.game_window = None
        self.settings = QSettings("MyChessApp", "ChessSettings")
        self.connect_buttons()
    
    def connect_buttons(self):
        """Подключение кнопок главного меню"""
        self.startGameButton.clicked.connect(self.start_game)
        self.settingsButton.clicked.connect(self.open_settings)
        self.statsButton.clicked.connect(self.open_stats)
        self.exitButton.clicked.connect(self.close)
        print("DEBUG: Кнопки главного меню подключены")
    
    def start_game(self):
        """Запуск новой игры"""
        print("DEBUG: Кнопка 'Начать игру' нажата")
        
        white_name = self.whitePlayerEdit.text().strip() or "Белые"
        black_name = self.blackPlayerEdit.text().strip() or "Чёрные"
        
        if not white_name or not black_name or white_name == black_name:
            QMessageBox.warning(self, "Ошибка", "Введите корректные имена игроков")
            return
        
        try:
            from main_window import MainWindow
            game_window = MainWindow(white_name=white_name, black_name=black_name, parent=self)
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
        
        white_stats = f"{white_name}: 0 побед, 0 поражений, 0 ничьих"
        black_stats = f"{black_name}: 0 побед, 0 поражений, 0 ничьих"
        
        QMessageBox.information(self, "Статистика игроков", f"{white_stats}\n\n{black_stats}")
    
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
