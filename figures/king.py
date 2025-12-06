from .figure import Figure

# Класс - король, от Figure
class King(Figure):
    
    # Инициализирует коня
    def __init__(self, color, position):

        # Вызываем __init__ из родительского класса, и передаем в него эти элементы
        super().__init__(color, position, 'king')

        # Символ, чтобы на доске отображать (маленькая - черная, большая - белая)
        self.symbol = 'K' if color == 'white' else 'k'
        
    # Возвращает список возможных ходов для короля на доске
    def get_correct_moves(self, board):

        # С чем работать будем: список с ходами, позиция, от которой считаем, и направление, куда король может походить, у него их 9
        moves = []
        row, col = self.position
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        # Проверяем каждое направление
        for direction_row, direction_col in king_moves:
            # Находим координаты клетки, на которую может наступить конь
            new_row, new_col = row + direction_row, col + direction_col

            # Если не выходим на рамки
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                # Смотрим есть ли что-то на этой клетке
                end_ceil = board.get_figure(new_row, new_col)
                # Проверям, что либо эта клетка пуста, или на ней фигура другого цвета
                if end_ceil is None or end_ceil.color != self.color:
                    moves.append((new_row, new_col))
        # Добавляем возможность рокировки
        if not self.has_moved:
            if self.color == 'white':
                moves.append((row, col - 2))
            else:
                moves.append((row, col + 2))
        return moves
