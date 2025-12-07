import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QMessageBox)
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSettings

# Импорты компонентов игры
from chess_board_widget import ChessBoardWidget
from final_window import FinalWindow
from history_moves import HistoryMovesWindow

class MainWindow(QMainWindow):
    def __init__(self, white_name="", black_name="", parent=None):
        super().__init__(parent)
        loadUi("main_window.ui", self)
        
        # Читаем текущий стиль фигур из настроек
        self.settings = QSettings("MyChessApp", "ChessSettings")
        piece_style = self.settings.value("piece_style", "classic")
        
        # Имена игроков по умолчанию
        self.white_name = white_name or "Белые"
        self.black_name = black_name or "Чёрные"
        
        # Настройка контейнера для игровой доски
        layout = QVBoxLayout(self.chessBoardFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создание шахматной доски
        self.chess_board = ChessBoardWidget(
            self.chessBoardFrame,
            piece_style=piece_style,
        )
        layout.addWidget(self.chess_board)
        
        # Установка имен игроков
        self.chess_board.set_players(self.white_name, self.black_name)
        
        # Подключение кнопки "Сделать ход"
        if hasattr(self, 'makeMoveButton'):
            self.makeMoveButton.clicked.connect(self.chess_board.make_move_from_text)
        
        # Передача UI элементов в шахматную доску
        self.chess_board.set_ui_elements(
            getattr(self, 'currentMoveEdit', None),
            getattr(self, 'playerInfoLabel', None),
            getattr(self, 'timerLabel', None),
        )
        
        # Подключение кнопки "История ходов"
        if hasattr(self, 'historyButton'):
            self.historyButton.clicked.connect(self.show_history_direct)
            print("DEBUG: Кнопка 'История ходов' подключена успешно")
        else:
            print("DEBUG: Кнопка 'historyButton' не найдена в UI")
        
        # Колбэк окончания игры
        self.chess_board.game_over_callback = self.show_final_window
        
        print("DEBUG: MainWindow инициализирован")
    
    def show_history_direct(self):
        """Обработчик кнопки 'История ходов' в главном окне"""
        print("DEBUG: Кнопка 'История ходов' в MainWindow нажата")
        
        # Получение истории ходов из объекта игры
        moves_history = getattr(self.chess_board.game, "moves_history", [])
        print(f"DEBUG: Найдено ходов: {len(moves_history)}")
        print(f"DEBUG: Первые 3 хода: {moves_history[:3]}")
        
        if not moves_history:
            QMessageBox.information(self, "История ходов", "Ходы отсутствуют. Партия еще не началась.")
            return
        
        # Отображение окна истории
        try:
            history_window = HistoryMovesWindow(moves_history, parent=self)
            history_window.show()
            print("DEBUG: Окно истории открыто успешно из MainWindow")
        except ImportError as e:
            print(f"DEBUG: ImportError: {e}")
            QMessageBox.warning(self, "Ошибка импорта", "Файл history_moves.py не найден")
        except Exception as e:
            print(f"DEBUG: Ошибка открытия истории: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть историю: {str(e)}")
    
    def show_final_window(self, result_text, winner_color, loser_color):
        """Отображение финального окна результатов игры"""
        print("DEBUG: show_final_window вызван")
        
        white_stats = f"{self.white_name}: 0 побед, 0 поражений, 0 ничьих"
        black_stats = f"{self.black_name}: 0 побед, 0 поражений, 0 ничьих"
        game_time = getattr(self.timerLabel, 'text', lambda: "00:00")() if hasattr(self, 'timerLabel') else "00:00"
        
        # Получение и передача истории ходов
        moves_history = getattr(self.chess_board.game, "moves_history", [])
        print(f"DEBUG: Передано {len(moves_history)} ходов в FinalWindow")
        
        final = FinalWindow(
            result_text=result_text,
            white_stats=white_stats,
            black_stats=black_stats,
            game_time=game_time,
            parent=self,
            moves_history=moves_history
        )
        
        parent_menu = self.parent()
        
        def back_to_menu():
            """Обработчик кнопки 'Меню'"""
            print("DEBUG: Кнопка 'Меню' нажата")
            if parent_menu:
                parent_menu.show()
            final.close()
        
        def play_again():
            """Обработчик кнопки 'Играть снова'"""
            print("DEBUG: Кнопка 'Играть снова' нажата")
            if parent_menu:
                new_game = MainWindow(self.white_name, self.black_name, parent=parent_menu)
                new_game.show()
            final.close()
        
        # Установка колбэков
        final.menu_callback = back_to_menu
        final.play_again_callback = play_again
        
        final.show()
        self.close()
    
    def closeEvent(self, event):
        """Обработка события закрытия окна"""
        print("DEBUG: MainWindow закрывается")
        if self.parent():
            self.parent().show()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow(white_name="Иван", black_name="Петр")
    w.show()
    sys.exit(app.exec_())
