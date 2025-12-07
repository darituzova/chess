import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QMessageBox)
from PyQt5.QtCore import QSettings, QTimer
from PyQt5.uic import loadUi

from chess_board_widget import ChessBoardWidget
from final_window import FinalWindow
from history_moves import HistoryMovesWindow
from settings_window import SettingsWindow

class MainWindow(QMainWindow):
    def __init__(self, white_name="", black_name="", parent=None):
        super().__init__(parent)
        loadUi("main_window.ui", self)
        
        self.settings = QSettings("MyChessApp", "ChessSettings")
        piece_style = self.settings.value("piece_style", "classic")
        
        self.white_name = white_name or "Белые"
        self.black_name = black_name or "Чёрные"
        self.parent_menu = parent
        
        # Инициализация таймера игры
        self.game_start_time = None
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game_timer)
        self.total_game_time = "00:00:00"
        
        # Обновление меток игроков и времени
        if hasattr(self, 'whitePlayerLabel'):
            self.whitePlayerLabel.setText(f"Белые: {self.white_name}")
        if hasattr(self, 'playerInfoLabel'):
            self.playerInfoLabel.setText("Ход: Белые")
        if hasattr(self, 'timerLabel'):
            self.timerLabel.setText("Время: 00:00:00")
        
        # Настройка контейнера для игровой доски
        layout = QVBoxLayout(self.chessBoardFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.chess_board = ChessBoardWidget(self.chessBoardFrame, piece_style=piece_style)
        layout.addWidget(self.chess_board)
        self.chess_board.set_players(self.white_name, self.black_name)
        
        # Передача UI элементов в шахматную доску
        self.chess_board.set_ui_elements(
            getattr(self, 'currentMoveEdit', None),
            getattr(self, 'playerInfoLabel', None),
            getattr(self, 'timerLabel', None),
        )
        
        self.connect_buttons()
        self.chess_board.game_over_callback = self.show_final_window
        
        print("DEBUG: MainWindow инициализирован с таймером")
    
    def connect_buttons(self):
        """Подключение всех кнопок управления игрой"""
        buttons = {
            'makeMoveButton': self.make_move_from_text_wrapper,
            'historyButton': self.show_history_direct,
            'surrenderButton': self.surrender_game,
            'drawButton': self.propose_draw,
            'menuButton': self.confirm_go_to_menu,
            'settingsButton': self.open_settings
        }
        for btn_name, handler in buttons.items():
            if hasattr(self, btn_name):
                getattr(self, btn_name).clicked.connect(handler)
                print(f"DEBUG: Кнопка '{btn_name}' подключена")
    
    def start_game_timer(self):
        """Запуск таймера игры"""
        print("DEBUG: Таймер игры запущен")
        self.game_start_time = time.time()
        self.game_timer.start(1000)
    
    def stop_game_timer(self):
        """Остановка таймера игры"""
        print("DEBUG: Таймер игры остановлен")
        self.game_timer.stop()
    
    def update_game_timer(self):
        """Обновление отображения времени игры"""
        if self.game_start_time:
            elapsed = int(time.time() - self.game_start_time)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.total_game_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            if hasattr(self, 'timerLabel') and self.timerLabel:
                self.timerLabel.setText(f"Время: {self.total_game_time}")
    
    def make_move_from_text_wrapper(self):
        """Обертка для make_move_from_text с запуском таймера"""
        if not self.game_start_time:
            self.start_game_timer()
        self.chess_board.make_move_from_text()
    
    def confirm_go_to_menu(self):
        """Подтверждение перед переходом в меню"""
        print("DEBUG: Запрос подтверждения перехода в меню")
        
        reply = QMessageBox.question(
            self,
            "Переход в меню",
            "Вы уверены, что хотите перейти в меню?\nИгра будет прервана.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.stop_game_timer()
            self.go_to_menu()
    
    def go_to_menu(self):
        """Переход в главное меню"""
        print("DEBUG: Подтвержден переход в меню")
        
        try:
            from main_menu import MainMenu
            menu_window = MainMenu()
            menu_window.show()
            self.parent_menu = menu_window
        except ImportError:
            print("DEBUG: Файл main_menu.py не найден")
        
        self.close()
    
    def open_settings(self):
        """Открытие окна настроек"""
        print("DEBUG: Кнопка 'Настройки' нажата")
        try:
            settings_window = SettingsWindow(parent=self)
            settings_window.show()
        except ImportError:
            QMessageBox.warning(self, "Ошибка", "Окно настроек недоступно")
    
    def show_history_direct(self):
        """Отображение истории ходов"""
        print("DEBUG: Кнопка 'История ходов' нажата")
        
        moves_history = getattr(self.chess_board.game, "moves_history", [])
        print(f"DEBUG: Найдено ходов: {len(moves_history)}")
        
        if not moves_history:
            QMessageBox.information(self, "История ходов", "Ходы отсутствуют. Партия еще не началась.")
            return
        
        try:
            history_window = HistoryMovesWindow(moves_history, parent=self)
            history_window.show()
            print("DEBUG: Окно истории открыто")
        except Exception as e:
            print(f"DEBUG: Ошибка открытия истории: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть историю: {str(e)}")
    
    def surrender_game(self):
        """Обработка сдачи игры"""
        print("DEBUG: Кнопка 'Сдаться' нажата")
        
        current_player = getattr(self.chess_board.game, 'current_player', 'white')
        player_name = self.white_name if current_player == "white" else self.black_name
        
        reply = QMessageBox.question(
            self, 
            "Сдаться", 
            f"{player_name} хочет сдаться.\nПодтвердить сдачу?", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.stop_game_timer()
            winner_name = self.black_name if current_player == "white" else self.white_name
            result_text = f"{winner_name} победил! {player_name} сдался"
            self.show_final_window(result_text)
    
    def propose_draw(self):
        """Обработка предложения ничьей"""
        print("DEBUG: Кнопка 'Ничья' нажата")
        
        current_player = getattr(self.chess_board.game, 'current_player', 'white')
        proposer_name = self.white_name if current_player == "white" else self.black_name
        opponent_name = self.black_name if current_player == "white" else self.white_name
        
        reply = QMessageBox.question(
            self,
            "Предложение ничьей",
            f"{proposer_name} предлагает ничью.\n{opponent_name}, согласны?", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.stop_game_timer()
            self.show_final_window("Ничья по обоюдному согласию")
        else:
            QMessageBox.information(self, "Ничья отклонена", 
                                  f"{opponent_name} отклонил предложение ничьей")
    
    def show_final_window(self, result_text):
        """Отображение финального окна с точным временем партии"""
        self.stop_game_timer()
        
        white_stats = f"{self.white_name}: 0 побед, 0 поражений, 0 ничьих"
        black_stats = f"{self.black_name}: 0 побед, 0 поражений, 0 ничьих"
        
        # Точное время партии передается в финальное окно
        final_game_time = self.total_game_time
        
        moves_history = getattr(self.chess_board.game, "moves_history", [])
        
        final = FinalWindow(
            result_text=result_text,
            white_stats=white_stats,
            black_stats=black_stats,
            game_time=final_game_time,
            parent=self,
            moves_history=moves_history
        )
        
        parent_menu = self.parent_menu or self.parent()
        
        def back_to_menu():
            print("DEBUG: Кнопка 'Меню' в финальном окне нажата")
            if parent_menu:
                parent_menu.show()
            final.close()
        
        def play_again():
            print("DEBUG: Кнопка 'Играть снова' в финальном окне нажата")
            new_game = MainWindow(self.white_name, self.black_name, parent=parent_menu)
            new_game.show()
            final.close()
        
        final.menu_callback = back_to_menu
        final.play_again_callback = play_again
        
        final.show()
        self.close()
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.stop_game_timer()
        print("DEBUG: MainWindow закрывается")
        if self.parent_menu or self.parent():
            (self.parent_menu or self.parent()).show()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow(white_name="Иван", black_name="Петр")
    w.show()
    sys.exit(app.exec_())
