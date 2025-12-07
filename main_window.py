# main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSettings

from chess_board_widget import ChessBoardWidget
from final_window import FinalWindow


class MainWindow(QMainWindow):
    def __init__(self, white_name="", black_name="", parent=None):
        super().__init__(parent)
        loadUi("main_window.ui", self)

        # читаем настройки
        self.settings = QSettings("MyChessApp", "ChessSettings")
        piece_style = self.settings.value("piece_style", "classic")

        layout = QVBoxLayout(self.chessBoardFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # создаём доску с выбранным стилем
        self.chess_board = ChessBoardWidget(self.chessBoardFrame, piece_style=piece_style)
        layout.addWidget(self.chess_board)

        self.white_name = white_name or "Белые"
        self.black_name = black_name or "Чёрные"
        self.chess_board.set_players(self.white_name, self.black_name)

        self.makeMoveButton.clicked.connect(self.chess_board.make_move_from_text)

        self.chess_board.set_ui_elements(
            self.currentMoveEdit,
            self.playerInfoLabel,
            self.timerLabel,
        )

        self.chess_board.game_over_callback = self.show_final_window

    def show_final_window(self, result_text, winner_color, loser_color):
        white_stats = f"{self.white_name}: 0 побед, 0 поражений, 0 ничьих"
        black_stats = f"{self.black_name}: 0 побед, 0 поражений, 0 ничьих"
        game_time = self.timerLabel.text() if self.timerLabel is not None else "00:00"

        final = FinalWindow(
            result_text=result_text,
            white_stats=white_stats,
            black_stats=black_stats,
            game_time=game_time,
            parent=None,
        )

        parent_menu = self.parent()

        def back_to_menu():
            if parent_menu is not None:
                parent_menu.show()

        def play_again():
            if parent_menu is not None:
                new_game = MainWindow(self.white_name, self.black_name, parent=parent_menu)
                new_game.show()

        def show_history():
            moves = getattr(self.chess_board.game, "moves_history", [])
            text = "\n".join(moves) if moves else "Ходов нет."
            QMessageBox.information(final, "История ходов", text)

        final.menu_callback = back_to_menu
        final.play_again_callback = play_again
        final.history_callback = show_history

        final.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
