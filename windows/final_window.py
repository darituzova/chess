import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

# Импортируем и создаем окно истории
from .history_moves import HistoryMovesWindow


class FinalWindow(QMainWindow):
    def __init__(
            self,
            result_text="Партия завершена",
            white_stats="Белые: 0 побед, 0 поражений, 0 ничьих",
            black_stats="Чёрные: 0 побед, 0 поражений, 0 ничьих",
            game_time="00:00",
            parent=None,
            menu_callback=None,
            play_again_callback=None,
            history_callback=None,
            moves_history=None  # Новый параметр для хранения истории ходов
    ):
        super().__init__(parent)
        
        # Получаем путь к текущему файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Переходим на уровень выше (из windows в корень проекта)
        project_root = os.path.dirname(current_dir)
        
        # Формируем путь к файлу ui
        ui_path = os.path.join(project_root, "ui", "final_window.ui")
        
        # Загружаем UI файл
        loadUi(ui_path, self)

        # Устанавливаем данные из параметров
        self.resultLabel.setText(result_text)
        self.whiteStatsLabel.setText(white_stats)
        self.blackStatsLabel.setText(black_stats)
        self.timeLabel.setText(f"Время партии: {game_time}")

        # Сохраняем колбэки и историю ходов
        self.menu_callback = menu_callback
        self.play_again_callback = play_again_callback
        self.history_callback = history_callback
        self.moves_history = moves_history or []  # Сохраняем историю ходов

        # Подключаем обработчики кнопок
        self.exitButton.clicked.connect(self.close)
        self.menuButton.clicked.connect(self.go_to_menu)
        self.playAgainButton.clicked.connect(self.play_again)
        self.historyButton.clicked.connect(self.show_history)

    def go_to_menu(self):
        """Переход в главное меню"""
        if self.menu_callback:
            self.menu_callback()
        self.close()

    def play_again(self):
        """Запуск новой игры"""
        if self.play_again_callback:
            self.play_again_callback()
        self.close()

    def show_history(self):
        """Отображение окна с историей ходов"""
        print("DEBUG: Кнопка 'История ходов' нажата")

        # Проверяем наличие истории ходов
        if not self.moves_history:
            print("DEBUG: История ходов пуста")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "История ходов", "Ходы отсутствуют")
            return

        print(f"DEBUG: Найдено ходов: {len(self.moves_history)}")

        try:
            history_window = HistoryMovesWindow(self.moves_history, parent=self)
            history_window.show()
            print("DEBUG: Окно истории открыто успешно")
        except ImportError:
            print("DEBUG: Ошибка - файл history_moves.py не найден")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Файл history_moves.py не найден")
        except Exception as e:
            print(f"DEBUG: Ошибка открытия истории: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть историю: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = FinalWindow(
        result_text="Победили Белые по мату",
        white_stats="Белые: 10 побед, 4 поражения, 3 ничьих",
        black_stats="Чёрные: 4 победы, 10 поражений, 3 ничьих",
        game_time="00:35:47",
        moves_history=["e4", "e5", "Nf3", "Nc6"]  # Тестовые данные
    )
    w.show()
    sys.exit(app.exec_())