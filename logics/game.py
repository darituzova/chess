from .board import Board
from PyQt5.QtWidgets import QInputDialog


# Класс - игра
class Game:
    # Инициализация игры
    def __init__(self):
        # Доска, кто сейчас ходит, закончилась ли игра, какое кол-во ходов уже сделано, а также история ходов
        self.board = Board()
        self.current_player = 'white'
        self.game_over = False
        self.moves_count = 0
        self.moves_history = []

    # Запускаем игру (консольный режим, сейчас не используется GUI)
    def start_game(self):
        print('''
Правила игры в шахматы:
Поле: Доска 8x8. Клетки могут содержать фигуры или быть пустыми.
Фигуры: У каждого игрока (белые, черные) 16 фигур (Король, Ферзь, Ладья, Слон, Конь, Пешка). Начальное расположение определяется по умолчанию.
Ход: Игроки ходят по очереди, начиная с белых. За ход можно передвинуть только одну фигуру.
Корректность хода: Фигура должна принадлежать игроку, ход должен быть допустимым для этой фигуры, после хода король не должен быть под шахом.
Перемещение: Фигура перемещается на новую клетку, старая клетка освобождается. Обновляются флаги для рокировки и взятия на проходе.
Правила фигур:
Король: На одну клетку в любом направлении. Рокировка (если возможно).
Ферзь: Как ладья и слон вместе (по горизонтали, вертикали и диагонали).
Ладья: По горизонтали и вертикали на любое число клеток.
Слон: По диагонали на любое число клеток.
Конь: “Буквой Г”. Перепрыгивает через фигуры.
Пешка: Вперед на одну клетку (или на две при первом ходе). Бьет по диагонали. Взятие на проходе. Превращение при достижении конца доски.
Шах, мат:
Шах: Король под атакой.
Мат: Король под шахом и нет защиты. Игра проиграна.
Цель игры: Поставить мат королю противника.
При вводе координат пользуйтесь шаблоном: начальная клетка пробел конечная клетка, например: b2 b4.
Для рокировки: "рокировка k" или "рокировка q".
''')

        # Основной игровой цикл
        while not self.game_over:
            print(self.board)
            print(f'Ход № {self.moves_count + 1}\nХод игрока: {self.current_player}')
            start_row, start_col, end_row, end_col = self.get_player_move()

            flag = self.try_move(start_row, start_col, end_row, end_col)
            if flag is False:
                continue

            # Проверка мата
            if self.board.is_checkmate('black' if self.current_player == 'white' else 'white'):
                print(self.board)
                self.print_moves_history()
                print(f'Мат! Победил игрок: {self.current_player}')
                self.game_over = True
            # Проверка шаха
            elif self.board.is_check('black' if self.current_player == 'white' else 'white'):
                print(f'Шах игроку {'black' if self.current_player == 'white' else 'white'}!')
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                self.moves_count += 1
                self.print_moves_history()
            # Обычный ход
            else:
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                self.moves_count += 1
                self.print_moves_history()

    # Получаем ход игрока в виде координат (консольный режим)
    def get_player_move(self):
        # Цикл ввода хода до получения корректных координат
        while True:
            try:
                move = input(
                    f'Игрок {self.current_player} введите ход (например, b2 b3, рокировка k, рокировка q): '
                ).lower()
                if move == 'рокировка k':
                    return self.handle_castling('kingside')
                elif move == 'рокировка q':
                    return self.handle_castling('queenside')

                start, end = move.split()

                if len(start) != 2 or len(end) != 2:
                    print('Ошибка: Неверный формат ввода. Введите две клетки (например, b2 b3).')
                    continue

                start_row, start_col = self.move_player_to_board_coords(start.lower())
                end_row, end_col = self.move_player_to_board_coords(end.lower())

                return start_row, start_col, end_row, end_col

            except ValueError:
                print('Ошибка: Некорректные координаты. Попробуйте еще раз.')
            except Exception:
                print('Ошибка: Неверный формат хода. Попробуйте еще раз.')

    # Обрабатываем рокировку
    def handle_castling(self, side):
        # Определение строки короля и конечной колонки для рокировки
        king_row = 7 if self.current_player == 'white' else 0
        if side == 'kingside':
            end_col = 6
        else:
            end_col = 2
        return king_row, 4, king_row, end_col

    # Преобразуем ход игрока в координаты
    def move_player_to_board_coords(self, ceil_move):
        # Конвертация алгебраической нотации (e2) в координаты доски (row, col)
        try:
            row = 7 - (int(ceil_move[1]) - 1)
            col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(ceil_move[0])
            if not (0 <= row < 8 and 0 <= col < 8):
                raise ValueError('Координаты выходят за пределы доски.')
            return row, col
        except ValueError as e:
            raise e
        except Exception:
            raise ValueError('Неверный формат координат.')

    # Попытка выполнить ход (с рокировкой, превращением и взятием на проходе)
    def try_move(self, start_row, start_col, end_row, end_col):
        # Проверка наличия фигуры на начальной клетке
        try:
            start_figure = self.board.get_figure(start_row, start_col)
            if start_figure is None:
                print('Ошибка: На начальной клетке нет фигуры.')
                return False

            # Проверка принадлежности фигуры текущему игроку
            if start_figure.color != self.current_player:
                print(f'Ошибка: Сейчас не ваш ход. Ход игрока {self.current_player}')
                return False

            # Проверка корректности хода
            if self.board.is_correct_move(start_row, start_col, end_row, end_col, self.current_player):
                start_figure = self.board.get_figure(start_row, start_col)
                end_ceil = self.board.get_figure(end_row, end_col)

                # Рокировка
                if start_figure.figure_type == 'king' and abs(end_col - start_col) == 2:
                    side = 'kingside' if end_col > start_col else 'queenside'
                    if self.board.is_check(self.current_player):
                        print('Ошибка: Нельзя рокироваться под шахом!')
                        return False
                    if self.board.can_castle(self.current_player, side):
                        king_row = start_row
                        if side == 'kingside':
                            rook_start_col = 7
                            rook_end_col = 5
                        else:
                            rook_start_col = 0
                            rook_end_col = 3

                        # Отключение флагов рокировки
                        if start_figure.color == 'white':
                            self.board.can_white_kingside_castle = False
                            self.board.can_white_queenside_castle = False
                        else:
                            self.board.can_black_kingside_castle = False
                            self.board.can_black_queenside_castle = False

                        # Выполнение рокировки
                        self.board.move_figure(king_row, 4, king_row, end_col)
                        self.board.move_figure(king_row, rook_start_col, king_row, rook_end_col)
                        move_notation = 'O-O' if side == 'kingside' else 'O-O-O'
                    else:
                        print('Ошибка: Рокировка невозможна.')
                        return False
                else:
                    # Превращение пешки
                    promotion_choice = None
                    if start_figure.figure_type == 'pawn' and (end_row == 0 or end_row == 7):
                        promotion_choice = self.get_promotion_choice()
                        self.board.promote_pawn(start_row, start_col, end_row, end_col, promotion_choice)
                        move_notation = self.generate_promotion_notation(
                            start_figure, end_row, end_col, promotion_choice, end_ceil
                        )
                    # Взятие на проходе
                    if start_figure.figure_type == 'pawn' and (end_row, end_col) == self.board.en_passant_target:
                        move_notation = self.generate_en_passant_notation(
                            start_figure, start_row, start_col, end_row, end_col
                        )
                        self.board.move_figure(start_row, start_col, end_row, end_col)
                    # Обычный ход
                    elif promotion_choice is None:
                        self.board.move_figure(start_row, start_col, end_row, end_col)
                        move_notation = self.generate_moves_notation(
                            start_figure, start_row, start_col, end_row, end_col, end_ceil
                        )

                # Добавление символов шаха/мата в нотацию
                if self.board.is_checkmate('black' if self.current_player == 'white' else 'white'):
                    move_notation += '#'
                elif self.board.is_check('black' if self.current_player == 'white' else 'white'):
                    move_notation += '+'

                # Сохранение хода в историю
                self.moves_history.append(move_notation)
                return True
            else:
                print('Ошибка: Недопустимый ход!')
                return False

        except ValueError as e:
            print(f'Ошибка при обработке хода: {e}')
            return False

    # Нотация для обычного хода
    def generate_moves_notation(self, start_figure, start_row, start_col, end_row, end_col, end_ceil):
        # Конвертация конечных координат в нотацию
        end_ceil_notataion = self.move_player_to_notation_coords(end_row, end_col)
        figure_symbol = start_figure.symbol.upper() if start_figure.figure_type != 'pawn' else ''
        eat_symbol = 'x' if end_ceil and start_figure.figure_type == 'pawn' else ''
        # Специальная нотация для взятия пешкой
        if start_figure.figure_type == 'pawn' and eat_symbol:
            start_ceil_notataion = self.move_player_to_notation_coords(start_row, start_col)
            notation = f'{start_ceil_notataion[0]}{eat_symbol}{end_ceil_notataion}'
        elif start_figure.figure_type == 'pawn':
            notation = f'{end_ceil_notataion}'
        else:
            notation = f'{figure_symbol}{eat_symbol}{end_ceil_notataion}'
        return notation

    # Нотация для превращения пешки
    def generate_promotion_notation(self, start_figure, end_row, end_col, promotion_choice, end_ceil):
        end_ceil_notataion = self.move_player_to_notation_coords(end_row, end_col)
        eat_symbol = 'x' if end_ceil else ''
        promotion_symbol = promotion_choice
        notation = f'{end_ceil_notataion}{eat_symbol}={promotion_symbol}'
        return notation

    # Преобразуем координаты в нотацию
    def move_player_to_notation_coords(self, row, col):
        # Конвертация координат доски в алгебраическую нотацию (e4)
        col_letter = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'][col]
        row_number = 8 - row
        return f'{col_letter}{row_number}'

    # Выбор фигуры для превращения
    def get_promotion_choice(self):
        # Диалог выбора фигуры для превращения пешки
        items = ['Ферзь (Q)', 'Ладья (R)', 'Слон (B)', 'Конь (N)']
        item, ok = QInputDialog.getItem(
            None,
            'Превращение пешки',
            'Выберите фигуру:',
            items,
            0,
            False,
        )
        if not ok or item is None:
            return 'Q'
        if item.startswith('Ферзь'):
            return 'Q'
        if item.startswith('Ладья'):
            return 'R'
        if item.startswith('Слон'):
            return 'B'
        if item.startswith('Конь'):
            return 'N'
        return 'Q'

    # История ходов
    def print_moves_history(self):
        print('История ходов:')
        for i, move in enumerate(self.moves_history):
            if i % 2 == 0:
                print(f'{i // 2 + 1}. {move}', end=' ')
            else:
                print(move)
        print()

    # Нотация для взятия на проходе
    def generate_en_passant_notation(self, start_figure, start_row, start_col, end_row, end_col):
        start_ceil_notation = self.move_player_to_notation_coords(start_row, start_col)
        end_ceil_notation = self.move_player_to_notation_coords(end_row, end_col)
        notation = f'{start_ceil_notation[0]}x{end_ceil_notation}'
        return notation