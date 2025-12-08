from figures import Figure, Pawn, Knight, Bishop, Rook, Queen, King

# Класс - доска
class Board:

    # Cоздание пустой доски и расстановка фигур.
    def __init__(self):

        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.initial_place_figures()

        # Флаги для отслеживания возможности рокировки
        self.can_white_kingside_castle = True
        self.can_white_queenside_castle = True
        self.can_black_kingside_castle = True
        self.can_black_queenside_castle = True

        # Добавляем цель для взятия на проходе
        self.en_passant_target = None

    # Формирование строкового представление доски для печати в консоль.
    def __str__(self):
        board_str_print = '    a   b   c   d   e   f   g   h\n'
        board_str_print += '  ---------------------------------\n'
        for i, row in enumerate(self.board):
            board_str_print += f'{8 - i} |' + ''.join(
                ['   |' if figure is None else f' {figure.symbol} |' for figure in row]) + f' {8 - i}\n'
            board_str_print += '  ---------------------------------\n'
        board_str_print += '    a   b   c   d   e   f   g   h\n'
        return board_str_print

    # Расставляение фигуры в начальной позиции на доске.
    def initial_place_figures(self):

        for i in range(8):
            self.board[6][i] = Pawn('white', (6, i))
        self.board[7][0] = Rook('white', (7, 0))
        self.board[7][1] = Knight('white', (7, 1))
        self.board[7][2] = Bishop('white', (7, 2))
        self.board[7][3] = Queen('white', (7, 3))
        self.board[7][4] = King('white', (7, 4))
        self.board[7][5] = Bishop('white', (7, 5))
        self.board[7][6] = Knight('white', (7, 6))
        self.board[7][7] = Rook('white', (7, 7))

        for i in range(8):
            self.board[1][i] = Pawn('black', (1, i))
        self.board[0][0] = Rook('black', (0, 0))
        self.board[0][1] = Knight('black', (0, 1))
        self.board[0][2] = Bishop('black', (0, 2))
        self.board[0][3] = Queen('black', (0, 3))
        self.board[0][4] = King('black', (0, 4))
        self.board[0][5] = Bishop('black', (0, 5))
        self.board[0][6] = Knight('black', (0, 6))
        self.board[0][7] = Rook('black', (0, 7))

    # Получение фигуры в соответствии с координатами
    def get_figure(self, row, col):

        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        else:
            raise ValueError(f'Некорректные координаты: {row}, {col}')

    # Проверка на корректный ход
    def is_correct_move(self, start_row, start_col, end_row, end_col, player_color):
        # Проверка на координаты начала, и заодно возьмем фигуру из этой клетки
        try:
            figure = self.get_figure(start_row, start_col)
        except ValueError:
            return False

        # Дальше думаем, что может пойти не так

        # В начальной клетке нет фигуры
        if figure is None:
            return False

            # Цвет фигуры, который пользователь хочет походить не соответсвует цвету текущего игрока
        if figure.color != player_color:
            return False

        # Смотрим, куда может походить фигура
        correct_moves = figure.get_correct_moves(self)

        # Фигура не может походить на конечную клетку
        if (end_row, end_col) not in correct_moves:
            return False

        # Cимулируем ход
        if self.simulate_move(start_row, start_col, end_row, end_col, lambda b: b.is_check(player_color)):
            return False

        # Ход хороший
        return True

    # Перемещение фигуры с одной клетки на другую.
    def move_figure(self, start_row, start_col, end_row, end_col):

        # Берем фигуру
        figure = self.board[start_row][start_col]

        # Убираем ее с места
        self.board[start_row][start_col] = None

        # Обработка взятия на проходе
        if figure.figure_type == 'pawn' and (end_row, end_col) == self.en_passant_target:
            # Удаляем пешку, которую взяли на проходе
            self.board[start_row][end_col] = None

        # На новое место
        self.board[end_row][end_col] = figure

        # Обновляем позицию фигуры
        figure.position = (end_row, end_col)

        # Помечаем как двинувшуюся
        figure.has_moved = True

        # Обновляем флаги рокировки, если король или ладья походили
        if figure.figure_type == 'king':
            if figure.color == 'white':
                self.can_white_kingside_castle = False
                self.can_white_queenside_castle = False
            else:
                self.can_black_kingside_castle = False
                self.can_black_queenside_castle = False
        elif figure.figure_type == 'rook':
            if figure.color == 'white':
                if start_col == 0:
                    self.can_white_queenside_castle = False
                elif start_col == 7:
                    self.can_white_kingside_castle = False
            else:
                if start_col == 0:
                    self.can_black_queenside_castle = False
                elif start_col == 7:
                    self.can_black_kingside_castle = False

        # Проверяем, был ли это ход пешки на два поля
        if figure.figure_type == 'pawn' and abs(start_row - end_row) == 2:
            # Устанавливаем цель для взятия на проходе
            self.en_passant_target = (start_row + (end_row - start_row) // 2, start_col)
        else:
            # Убираем цель для взятия на проходе
            self.en_passant_target = None

    # Проверка - находится ли король игрока под шахом
    def is_check(self, player_color):

        # Находим координаты короля игрока
        king_row, king_col = self.find_king(player_color)

        # Проверяем, находится ли король под атакой какой-либо фигуры противника
        for row in range(8):
            for col in range(8):

                # Берем фигуру из клетки
                figure = self.get_figure(row, col)
                # Проверяем, что она другого цвета
                if figure is not None and figure.color != player_color:
                    # Смотрим ее правильные ходы
                    correct_moves = figure.get_correct_moves(self)
                    # Король под шахом
                    if (king_row, king_col) in correct_moves:
                        return True

        # Король не под шахом
        return False

    # Нахождение координат короля заданного цвета
    def find_king(self, player_color):

        # Перебираем все клетки
        for row in range(8):
            for col in range(8):

                # Берем фигуру из клетки
                figure = self.get_figure(row, col)
                # Проверяем фигуру на короля нужного цвета
                if figure is not None and figure.figure_type == 'king' and figure.color == player_color:
                    return row, col

        # Если король не найден (что не должно произойти)
        return None

    # Проверка на мат
    def is_checkmate(self, player_color):
        # Проверяем, есть ли у игрока хоть один допустимый ход, перебирая все клетки
        for row in range(8):
            for col in range(8):
                # Берем фигуру из клетки
                figure = self.get_figure(row, col)

                # Проверяем, что она нужного цвета цвета
                if figure is not None and figure.color == player_color:
                    # Смотрим ее правильные ходы
                    correct_moves = figure.get_correct_moves(self)
                    for move in correct_moves:
                        # Симулируем ход и проверяем, выводит ли он короля из-под шаха
                        if not self.simulate_move(row, col, move[0], move[1], lambda b: b.is_check(player_color)):
                            # Есть ход, который выводит из-под шаха
                            return False
                            # Если нет шаха, то нет мата
        if not self.is_check(player_color):
            return False
        # Мат есть
        return True

    # Симуляция хода для проверки мата
    def simulate_move(self, start_row, start_col, end_row, end_col, callback):

        # Находим начальную и конечные клетки, и что на них
        figure_to_move = self.get_figure(start_row, start_col)
        end_figure = self.get_figure(end_row, end_col)

        if end_figure is not None and end_figure.color == figure_to_move.color:
            return True

        # Сохраняем информацию о начальном состоянии
        start = figure_to_move
        end = end_figure

        # Выполняем ход
        self.board[start_row][start_col] = None
        self.board[end_row][end_col] = figure_to_move
        figure_to_move.position = (end_row, end_col)

        # Вызываем callback-функцию (проверка, будет ли пат)
        check_result = callback(self)

        # Возвращаем доску в исходное состояние
        self.board[start_row][start_col] = start
        self.board[end_row][end_col] = end
        if start:
            figure_to_move.position = (start_row, start_col)

        return check_result

    # Проверка - возможна ли рокировка для данного цвета и стороны
    def can_castle(self, color, side):

        king_row = 7 if color == 'white' else 0
        king = self.board[king_row][4]
        if side == 'kingside':
            if color == 'white':
                if not self.can_white_kingside_castle:
                    return False
            else:
                if not self.can_black_kingside_castle:
                    return False
            rook = self.board[king_row][7]
            empty_cols = [5, 6]
        elif side == 'queenside':
            if color == 'white':
                if not self.can_white_queenside_castle:
                    return False
            else:
                if not self.can_black_queenside_castle:
                    return False
            rook = self.board[king_row][0]
            empty_cols = [1, 2, 3]
        else:
            return False

        if king is None or king.figure_type != 'king' or king.has_moved:
            return False
        if rook is None or rook.figure_type != 'rook' or rook.has_moved:
            return False

        for col in empty_cols:
            if self.board[king_row][col] is not None:
                return False

        if self.is_check(color):
            return False

        # Проверяем, что король не проходит через битое поле
        king_col = 4
        if side == 'kingside':
            # До 7, а не включая 7, чтобы не проверять клетку, где будет ладья
            for col in range(king_col + 1, 7):
                if self.is_under_attack(color, king_row, col):
                    return False
        else:
            # От 1 до 4, не включая 4
            for col in range(1, king_col):
                if self.is_under_attack(color, king_row, col):
                    return False

        return True

    # Проверка - находится ли клетка под атакой фигур противника
    def is_under_attack(self, color, row, col):

        opponent_color = 'black' if color == 'white' else 'white'
        for i in range(8):
            for j in range(8):
                figure = self.get_figure(i, j)
                if figure is not None and figure.color == opponent_color:
                    possible_moves = figure.get_correct_moves(self)
                    if figure.figure_type == 'king':
                        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                        king_row, king_col = figure.position
                        for direction_row, direction_col in king_moves:
                            new_row, new_col = king_row + direction_row, king_col + direction_col
                            if new_row == row and new_col == col:
                                return True
                    elif (row, col) in possible_moves:
                        return True
        return False

    # Превращение пешки в другую фигуру при достижении края доски
    def promote_pawn(self, start_row, start_col, row, col, promotion_choice):

        # Определяем цвет пешки
        color = 'white' if row == 0 else 'black'

        # Проверяем корректность выбора фигуры
        if promotion_choice in ['Q', 'R', 'B', 'N']:
            if promotion_choice == 'Q':
                self.board[row][col] = Queen(color, (row, col))
                self.board[start_row][start_col] = None
            elif promotion_choice == 'R':
                self.board[row][col] = Rook(color, (row, col))
                self.board[start_row][start_col] = None
            elif promotion_choice == 'B':
                self.board[row][col] = Bishop(color, (row, col))
                self.board[start_row][start_col] = None
            elif promotion_choice == 'N':
                self.board[row][col] = Knight(color, (row, col))
                self.board[start_row][start_col] = None
        else:
            print('Неверный выбор фигуры. Превращение не выполнено.')