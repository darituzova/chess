# main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PyQt5.uic import loadUi

from chess_board_widget import ChessBoardWidget


class MainWindow(QMainWindow):
    def __init__(self, white_name="", black_name="", parent=None):
        super().__init__(parent)
        loadUi("main_window.ui", self)

        layout = QVBoxLayout(self.chessBoardFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.chess_board = ChessBoardWidget(self.chessBoardFrame, piece_style="basics")
        layout.addWidget(self.chess_board)

        # если имя пустое – используем по умолчанию
        if not white_name:
            white_name = "Белые"
        if not black_name:
            black_name = "Чёрные"

        # передаем имена в виджет доски
        self.chess_board.set_players(white_name, black_name)

        # подключаем кнопку "Сделать ход"
        self.makeMoveButton.clicked.connect(self.chess_board.make_move_from_text)

        # связываем UI элементы
        self.chess_board.set_ui_elements(
            self.currentMoveEdit,
            self.playerInfoLabel,
            self.timerLabel,
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
