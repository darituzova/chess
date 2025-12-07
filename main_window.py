# main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PyQt5.uic import loadUi
from chess_board_widget import ChessBoardWidget  # Обновленный импорт

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("main_window.ui", self)
        
        layout = QVBoxLayout(self.chessBoardFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.chess_board = ChessBoardWidget(self.chessBoardFrame, piece_style="basics")
        layout.addWidget(self.chess_board)
        
        # Подключаем кнопку "Сделать ход"
        self.makeMoveButton.clicked.connect(self.chess_board.make_move_from_text)
        
        # Связываем UI элементы
        self.chess_board.set_ui_elements(
            self.currentMoveEdit, 
            self.playerInfoLabel, 
            self.timerLabel
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
