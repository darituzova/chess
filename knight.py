from figure import Figure

# Класс - конь, от Figure
class Knight(Figure):
    
    # Инициализирует коня
    def __init__(self, color, position):

        # Вызываем __init__ из родительского класса, и передаем в него эти элементы
        super().__init__(color, position, 'knight')

        # Символ, чтобы на доске отображать (маленькая - черная, большая - белая)
        self.symbol = 'N' if color == 'white' else 'n'
        
    # Возвращает список возможных ходов для коня на данной доске 
    def get_correct_moves(self, board):

        # С чем работать будем: список с ходами, позиция, от которой считаем, и направление, куда конь может походить, у него их 8
        moves = []
        row, col = self.position
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        # Проверяем каждое направление
        for direction_row, direction_col in knight_moves:
            # Находим координаты клетки, на которую может наступить конь
            new_row, new_col = row + direction_row, col + direction_col

            # Если не выходим на рамки
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                # Смотрим есть ли что-то на этой клетке
                end_ceil = board.get_figure(new_row, new_col)
                # Проверям, что либо эта клетка пуста, или на ней фигура другого цвета
                if end_ceil is None or end_ceil.color != self.color:
                    moves.append((new_row, new_col))

        return moves