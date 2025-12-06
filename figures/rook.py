from .figure import Figure

# Класс - ладья, от Figure
class Rook(Figure):
    
    # Инициализирует ладью
    def __init__(self, color, position):

        # Вызываем __init__ из родительского класса, и передаем в него эти элементы
        super().__init__(color, position, 'rook')

        # Символ, чтобы на доске отображать (маленькая - черная, большая - белая)
        self.symbol = 'R' if color == 'white' else 'r'

    # Возвращает список возможных ходов для ладьи на доске
    def get_correct_moves(self, board):

        # С чем работать будем: список с ходами, позиция, от которой считаем, и направление, куда ладья может походить, у него их 4
        moves = []
        row, col = self.position
        rook_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        # Проверяем каждое направление
        for direction_row, direction_col in rook_moves:
            # Максимум 7 клеток в каждом направлении
            for i in range(1, 8):
                # Находим координаты клетки, на которую может наступить конь
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
