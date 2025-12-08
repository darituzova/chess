import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

# Импортируем и создаем окно истории
from .history_moves import HistoryMovesWindow

# Класс - отображения финального окна
class FinalWindow(QMainWindow):
    def __init__(
            self,
            result_text='Партия завершена',
            white_stats='Белые: 0 побед, 0 поражений, 0 ничьих',
            black_stats='Чёрные: 0 побед, 0 поражений, 0 ничьих',
            game_time='00:00',
            parent=None,
            menu_callback=None,
            play_again_callback=None,
            history_callback=None,
            moves_history=None
    ):
        super().__init__(parent)
        
        # Получаем путь к текущему файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Переходим на уровень выше (из windows в корень проекта)
        project_root = os.path.dirname(current_dir)
        
        # Формируем путь к файлу ui
        ui_path = os.path.join(project_root, 'ui', 'final_window.ui')
        
        # Загружаем UI файл
        loadUi(ui_path, self)

        # Устанавливаем данные из параметров
        self.resultLabel.setText(result_text)
        self.whiteStatsLabel.setText(white_stats)
        self.blackStatsLabel.setText(black_stats)
        self.timeLabel.setText(f'Время партии: {game_time}')

        # Сохраняем колбэки и историю ходов
        self.menu_callback = menu_callback
        self.play_again_callback = play_again_callback
        self.history_callback = history_callback
        self.moves_history = moves_history or []

        # Подключаем обработчики кнопок
        self.exitButton.clicked.connect(self.close)
        self.menuButton.clicked.connect(self.go_to_menu)
        self.playAgainButton.clicked.connect(self.play_again)
        self.historyButton.clicked.connect(self.show_history)

    # Переход в главное меню
    def go_to_menu(self):
        if self.menu_callback:
            self.menu_callback()
        self.close()

    # Запуск новой игры
    def play_again(self):
        if self.play_again_callback:
            self.play_again_callback()
        self.close()

    # Отображение окна с историей ходов
    def show_history(self):

        # Проверяем наличие истории ходов
        if not self.moves_history:

            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, 'История ходов', 'Ходы отсутствуют')
            return

        # Создание и отображение окна истории ходов
        try:
            history_window = HistoryMovesWindow(self.moves_history, parent=self)
            history_window.show()
        except ImportError:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Ошибка', 'Файл history_moves.py не найден')
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Ошибка', f'Не удалось открыть историю: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Для проверки
    w = FinalWindow(
        result_text='Победили Белые по мату',
        white_stats='Белые: 10 побед, 4 поражения, 3 ничьих',
        black_stats='Чёрные: 4 победы, 10 поражений, 3 ничьих',
        game_time='00:35:47',
        moves_history=['e4', 'e5', 'Nf3', 'Nc6']
    )
    w.show()
    sys.exit(app.exec_())