# final_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi


class FinalWindow(QMainWindow):
    def __init__(
        self,
        result_text="Партия завершена",
        white_stats="Белые: 0 побед, 0 поражений, 0 ничьих",
        black_stats="Чёрные: 0 побед, 0 поражений, 0 ничьих",
        game_time="00:00",
        parent=None,
    ):
        super().__init__(parent)
        loadUi("final_window.ui", self)

        # текстовые данные
        self.resultLabel.setText(result_text)
        self.whiteStatsLabel.setText(white_stats)
        self.blackStatsLabel.setText(black_stats)
        self.timeLabel.setText(f"Время партии: {game_time}")

        # колбэки, которые задаёт основное окно
        self.menu_callback = None
        self.play_again_callback = None
        self.history_callback = None

        # кнопки
        self.exitButton.clicked.connect(self.close)
        self.menuButton.clicked.connect(self.go_to_menu)
        self.playAgainButton.clicked.connect(self.play_again)
        self.historyButton.clicked.connect(self.show_history)

    def go_to_menu(self):
        if self.menu_callback:
            self.menu_callback()
        self.close()

    def play_again(self):
        if self.play_again_callback:
            self.play_again_callback()
        self.close()

    def show_history(self):
        if self.history_callback:
            self.history_callback()


# отдельный запуск для проверки
if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = FinalWindow(
        result_text="Победили Белые по мату",
        white_stats="Белые: 10 побед, 4 поражения, 3 ничьих",
        black_stats="Чёрные: 4 победы, 10 поражений, 3 ничьих",
        game_time="00:35:47",
    )
    w.show()

    sys.exit(app.exec_())
