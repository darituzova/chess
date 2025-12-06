from figure import Figure

# Класс - пешка, от Figure
class Pawn(Figure):

    # Инициализирует пешку
    def __init__(self, color, position):

        # Вызываем __init__ из родительского класса, и передаем в него эти элементы
        super().__init__(color, position, 'pawn')

        # Символ, чтобы на доске отображать (маленькая - черная, большая - белая)
        self.symbol = 'P' if color == 'white' else 'p'

    # Возвращает список возможных ходов для пешки на доске
    def get_correct_moves(self, board):

        # С чем работать будем: список с ходами, позиция, от которой считаем, и направление, так как фигуры друг на друга идут и назад не могут
        moves = []
        row, col = self.position
        # Направление не меняется
        direction = -1 if self.color == 'white' else 1

        # Движение на одну клетку вперед
        new_row = row + direction
        # Если не выходим на рамки и на этой клетке нет фигуры, то ок, так как пешка есть только по диагонали
        if 0 <= new_row < 8 and board.get_figure(new_row, col) is None:
            moves.append((new_row, col))

            # Движение на две клетки вперед (только при первом ходе)
            # Если первый ход, доска не заканчивается, и на 2 клетки вперед нет фигуры
            # То, что на клетке впереди нет фигуры проверили до
            if not self.has_moved and 0 <= row + 2 * direction < 8 and board.get_figure(
                    row + 2 * direction, col) is None:
                moves.append((row + 2 * direction, col))

        # Едим по диагонали
        for vars_diag in [(row + direction, col - 1), (row + direction, col + 1)]:
            # Если не вылезаем за границы
            if 0 <= vars_diag[0] < 8 and 0 <= vars_diag[1] < 8:
                # Смотрим, что на жтой клетке, если нет фигиру другого цвета, то неподходит
                figure_to_eat = board.get_figure(vars_diag[0], vars_diag[1])
                if figure_to_eat is not None and figure_to_eat.color != self.color:
                    moves.append((vars_diag[0], vars_diag[1]))

        # Взятие на проходе
        if board.en_passant_target is not None:
            en_passant_row, en_passant_col = board.en_passant_target
            if row + direction == en_passant_row and abs(col - en_passant_col) == 1:
                moves.append((en_passant_row, en_passant_col))
        return moves

#помогите