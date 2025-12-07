import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor


class HistoryMovesWindow(QMainWindow):
    def __init__(self, moves_history=None, parent=None):
        super().__init__(parent)
        # Получаем путь к текущему файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Переходим на уровень выше (из windows в корень проекта)
        project_root = os.path.dirname(current_dir)
        
        # Формируем путь к файлу ui
        ui_path = os.path.join(project_root, "ui", "history_moves.ui")
        
        # Загружаем UI файл
        loadUi(ui_path, self)

        self.moves_history = moves_history or []
        self.parent_window = parent

        # Подключаем кнопки
        self.closeButton.clicked.connect(self.close)

        # Заполняем список ходов
        self.populate_moves()

    def populate_moves(self):
        """Форматирует и отображает историю ходов"""
        if not self.moves_history:
            self.movesTextEdit.setText("Ходы отсутствуют")
            return

        formatted_moves = []
        move_number = 1

        for i, move in enumerate(self.moves_history):
            if i % 2 == 0:  # Ход белых
                formatted_moves.append(f"{move_number}. {move}")
                move_number += 1
            else:  # Ход черных
                formatted_moves.append(f"   {move}")

        moves_text = "\n".join(formatted_moves)
        self.movesTextEdit.setText(moves_text)

        # Автопрокрутка вниз
        cursor = self.movesTextEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.movesTextEdit.setTextCursor(cursor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sample_moves = ["e4", "e5", "Nf3", "Nc6"]
    w = HistoryMovesWindow(sample_moves)
    w.show()
    sys.exit(app.exec_())