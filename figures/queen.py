from figure import Figure

class Queen(Figure):

    # Инициализирует ферзя
    def __init__(self, color, position):

        # Вызываем __init__ из родительского класса, и передаем в него эти элементы
        super().__init__(color, position, 'queen')

        # Символ, чтобы на доске отображать (маленькая - черная, большая - белая)
        self.symbol = 'Q' if color == 'white' else 'q'

    # Возвращает список возможных ходов для ферзя на доске
    def get_correct_moves(self, board):

        # С чем работать будем: список с ходами, позиция, от которой считаем, и направление, куда ферзь может походить, у него их 8
        moves = []
        row, col = self.position
        queen_moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        # Проверяем каждое направление
        for direction_row, direction_col in queen_moves:
            # Максимум 7 клеток в каждом направлении
            for i in range(1, 8):
                # Находим координаты клетки, на которую может наступить на эту клетку
                new_row, new_col = row + direction_row * i, col + direction_col * i

                # Если не выходим на рамки
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    # Смотрим есть ли что-то на этой клетке
                    end_ceil = board.get_figure(new_row, new_col)
                    # Если клетка пуста
                    if end_ceil is None:
                        moves.append((new_row, new_col))
                    # Останавливаем движение после взятия фигуры
                    elif end_ceil.color != self.color:
                        moves.append((new_row, new_col))
                        break
                    # Блокировка своей фигурой
                    else:
                        break

                # Выход за пределы доски
                else:
                    break

        return moves
