from board import Board

# Класс - игра
class Game:

    # Инициализация игры
    def __init__(self):

        # Доска, кто сейчас ходит, закончилась ли игра, какое кол-во ходов уже сделано, а также история ходов (может потом в доп заданиях понадобиться)
        self.board = Board()
        self.current_player = 'white'
        self.game_over = False
        self.moves_count = 0
        self.moves_history = []

        # Начинаем игру, взаимодействуем с игроками

    # Запускаем игру
    def start_game(self):

        print('''
Правила игры в шахматы: 

Поле: Доска 8x8. Клетки могут содержать фигуры или быть пустыми.
Фигуры: У каждого игрока (белые, черные) 16 фигур (Король, Ферзь, Ладья, Слон, Конь, Пешка). Начальное расположение определяется по умолчанию.
Ход: Игроки ходят по очереди, начиная с белых. За ход можно передвинуть только одну фигуру.
Корректность хода: Фигура должна принадлежать игроку, ход должен быть допустимым для этой фигуры, после хода король не должен быть под шахом.
Перемещение: Фигура перемещается на новую клетку, старая клетка освобождается. Обновляются флаги для рокировки и взятия на проходе.
Правила фигур: (Король, Королева, Ладья, Слон, Конь, Пешка). Каждая фигура ходит по-своему:

Король: На одну клетку в любом направлении. Рокировка (если возможно).
Ферзь: Как ладья и слон вместе (по горизонтали, вертикали и диагонали).
Ладья: По горизонтали и вертикали на любое число клеток.
Слон: По диагонали на любое число клеток.
Конь: “Буквой Г” (две клетки в одном направлении, одна в перпендикулярном). Перепрыгивает через фигуры.
Пешка: Вперед на одну клетку (или на две при первом ходе). Бьет по диагонали. Взятие на проходе. Превращение при достижении конца доски.

Шах, мат:
Шах: Король под атакой.
Мат: Король под шахом и нет защиты. Игра проиграна.

Цель игры: Поставить мат королю противника.

При вводе координат пользуйтесь шаблон: начальная клетка пробел конечная клетка, например: b2 b4.
Для того, чтобы сделать рокировку, надо написать: рокировка и k/q, где k - короткая рокировка, q - длинная рокировка.''')

        # Пока флаг self.game_over == False, то есть игра не окончена, мы играем
        while not self.game_over:
            # Выводим доску с помощью print, так как в классе Board реализован метод __str__
            print(self.board)

            # Запрашиваем у игрока ход, используя метод  self.get_player_move(), чтобы буквы преобразовать в цифры
            print(f'Ход № {self.moves_count + 1}\nХод игрока: {self.current_player}')
            start_row, start_col, end_row, end_col = self.get_player_move()

            # Обрабатываем ход
            flag = self.try_move(start_row, start_col, end_row, end_col)

            if flag == False:
                continue

            # Проверяем на мат
            if self.board.is_checkmate('black' if self.current_player == 'white' else 'white'):
                # Выводим доску с помощью print, так как в классе Board реализован метод __str__
                print(self.board)
                self.print_moves_history()
                print(f'Мат! Победил игрок: {self.current_player}')
                self.game_over = True

            # Проверяем на шах
            elif self.board.is_check('black' if self.current_player == 'white' else 'white'):
                print(f'Шах игроку {'black' if self.current_player == 'white' else 'white'}!')
                # Смена игрока
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                # Увеличиваем счетчик ходов
                self.moves_count += 1
                # Выводим историю ходов
                self.print_moves_history()
            else:
                # Смена игрока
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                # Увеличиваем счетчик ходов
                self.moves_count += 1
                # Выводим историю ходов
                self.print_moves_history()

                # Запрашиваем ход у игрока

    # Получает ход игрока в виде координат
    def get_player_move(self):

        # Пока ход не будет введен в нужном формате
        while True:
            # Пробуем
            try:
                # Запрашиваем
                move = input(
                    f'Игрок {self.current_player} введите ход (например, b2 b3, рокировка k, рокировка q): ').lower()

                if move == 'рокировка k':
                    return self.handle_castling('kingside')
                elif move == 'рокировка q':
                    return self.handle_castling('queenside')

                # Разделяем на начальную и финальную клетку
                start, end = move.split()

                # Проверка на правильное количество введенных клеток
                if len(start) != 2 or len(end) != 2:
                    print('Ошибка: Неверный формат ввода. Введите две клетки (например, b2 b3).')
                    continue  # Начинаем цикл заново

                # Преобразовываем буквы в числа
                start_row, start_col = self.move_player_to_board_coords(start.lower())
                end_row, end_col = self.move_player_to_board_coords(end.lower())

                # Возвращаем координаты начальной и финальной клетки
                return start_row, start_col, end_row, end_col

            # Если ошибка, то выводим соответствующее сообщение
            except ValueError as e:
                # Ловим исключение, если move_player_to_board_coords выдает исключение
                print('Ошибка: Некорректные координаты. Попробуйте еще раз.')
            except:
                # Ловим любые другие исключения (например, если введено не два значения)
                print('Ошибка: Неверный формат хода. Попробуйте еще раз.')

    # Обрабатывает рокировку
    def handle_castling(self, side):

        king_row = 7 if self.current_player == 'white' else 0
        if side == 'kingside':
            end_col = 6
        else:  # queenside
            end_col = 2
        return king_row, 4, king_row, end_col

    # Преобразуем ход игрока в координаты, которые можно использовать для доски в классе Board
    def move_player_to_board_coords(self, ceil_move):

        try:
            # Строку просто инвертируем
            row = 7 - (int(ceil_move[1]) - 1)

            # Колонку находим с помощью индексов в списке соотвествующего элемента
            col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(ceil_move[0])

            # Проверка на выход за границы
            if not (0 <= row < 8 and 0 <= col < 8):
                raise ValueError('Координаты выходят за пределы доски.')
            return row, col

        # Ошибки
        except ValueError as e:
            # Пробрасываем исключение выше, чтобы его обработал get_player_move
            raise e
        except:
            # Пробрасываем исключение с общим сообщением
            raise ValueError('Неверный формат координат.')

            # Пробуем сделать ход с проверкой всех возможных ошибок

    # Преобразуем ход игрока в координаты, которые можно использовать для доски в классе Board
    def move_player_to_board_coords(self, ceil_move):

        try:
            # Строку просто инвертируем
            row = 7 - (int(ceil_move[1]) - 1)

            # Колонку находим с помощью индексов в списке соотвествующего элемента
            col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(ceil_move[0])

            # Проверка на выход за границы
            if not (0 <= row < 8 and 0 <= col < 8):
                raise ValueError('Координаты выходят за пределы доски.')
            return row, col

        # Ошибки
        except ValueError as e:
            # Пробрасываем исключение выше, чтобы его обработал get_player_move
            raise e
        except:
            # Пробрасываем исключение с общим сообщением
            raise ValueError('Неверный формат координат.')

    # Пытается выполнить ход, проверяя его корректность и обрабатывая особые случаи (рокировка, превращение пешки, взятие на проходе)
    def try_move(self, start_row, start_col, end_row, end_col):

        try:
            start_figure = self.board.get_figure(start_row, start_col)

            if start_figure is None:
                print('Ошибка: На начальной клетке нет фигуры.')
                return False

            if start_figure.color != self.current_player:
                print(f'Ошибка: Сейчас не ваш ход. Ход игрока {self.current_player}')
                return False

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
                        # Выполняем рокировку
                        king_row = start_row
                        if side == 'kingside':
                            rook_start_col = 7
                            rook_end_col = 5

                        else:  # queenside
                            rook_start_col = 0
                            rook_end_col = 3
                        # Обновление рокировки, если рокировка произошла
                        if start_figure.color == 'white':
                            self.board.can_white_kingside_castle = False
                            self.board.can_white_queenside_castle = False
                        else:
                            self.board.can_black_kingside_castle = False
                            self.board.can_black_queenside_castle = False

                        self.board.move_figure(king_row, 4, king_row, end_col)  # Move King
                        self.board.move_figure(king_row, rook_start_col, king_row, rook_end_col)  # Move Rook

                        # Генерируем нотацию для рокировки
                        move_notation = 'O-O' if side == 'kingside' else 'O-O-O'

                    else:
                        print('Ошибка: Рокировка невозможна.')
                        return False

                else:
                    # Превращение пешки, выносим до перемещения фигуры
                    promotion_choice = None
                    if start_figure.figure_type == 'pawn' and (end_row == 0 or end_row == 7):
                        promotion_choice = self.get_promotion_choice()
                        self.board.promote_pawn(start_row, start_col, end_row, end_col, promotion_choice)
                        move_notation = self.generate_promotion_notation(start_figure, end_row, end_col,
                                                                         promotion_choice, end_ceil)

                    # Взятие на проходе
                    if start_figure.figure_type == 'pawn' and (end_row, end_col) == self.board.en_passant_target:
                        move_notation = self.generate_en_passant_notation(start_figure, start_row, start_col, end_row,
                                                                          end_col)
                        self.board.move_figure(start_row, start_col, end_row, end_col)


                    # Обычный ход
                    elif promotion_choice is None:
                        self.board.move_figure(start_row, start_col, end_row, end_col)
                        move_notation = self.generate_moves_notation(start_figure, start_row, start_col, end_row,
                                                                     end_col, end_ceil)

                # Добавляем + или # в конце хода
                if self.board.is_checkmate('black' if self.current_player == 'white' else 'white'):
                    move_notation += '#'  # Мат
                elif self.board.is_check('black' if self.current_player == 'white' else 'white'):
                    move_notation += '+'  # Шах

                self.moves_history.append(move_notation)
                return True

            else:
                print('Ошибка: Недопустимый ход!')
                return False

        except ValueError as e:
            print(f'Ошибка при обработке хода: {e}')
            return False

    # Генерирует шахматную нотацию для обычного хода
    def generate_moves_notation(self, start_figure, start_row, start_col, end_row, end_col, end_ceil):

        # Переводим координаты в нотационный вид
        end_ceil_notataion = self.move_player_to_notation_coords(end_row, end_col)

        # Для пешки символ не пишем
        figure_symbol = start_figure.symbol.upper() if start_figure.figure_type != 'pawn' else ''

        # Символ взятия
        eat_symbol = 'x' if end_ceil and start_figure.figure_type == 'pawn' else ''  # Символ взятия

        if start_figure.figure_type == 'pawn' and eat_symbol:
            start_ceil_notataion = self.move_player_to_notation_coords(start_row, start_col)
            notation = f'{start_ceil_notataion[0]}{eat_symbol}{end_ceil_notataion}'
        elif start_figure.figure_type == 'pawn':
            notation = f'{end_ceil_notataion}'
        else:
            notation = f'{figure_symbol}{eat_symbol}{end_ceil_notataion}'
        return notation

        # Символ взятия
        eat_symbol = 'x' if end_ceil else ''  # Символ взятия

        notation = f'{notation}{eat_symbol}{end_ceil_notataion}'
        return notation

    # Нотация для превращения пешки
    def generate_promotion_notation(self, start_figure, end_row, end_col, promotion_choice, end_ceil):

        # Переводим координаты в нотационный вид
        end_ceil_notataion = self.move_player_to_notation_coords(end_row, end_col)

        # Символ взятия
        eat_symbol = 'x' if end_ceil else ''  # Символ взятия

        # Фигура, в которую превращаем пешку
        promotion_symbol = promotion_choice
        notation = f'{end_ceil_notataion}{eat_symbol}={promotion_symbol}'
        return notation

    # Преобразуем ход игрока в нотацию
    def move_player_to_notation_coords(self, row, col):

        # Строку просто инвертируем, а колонку через списки
        col_letter = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'][col]
        row_number = 8 - row
        return f'{col_letter}{row_number}'

        # Печать истории ходов

    # Даем пользователю выбрать во что превратить пешку
    def get_promotion_choice(self):

        while True:
            try:
                promotion_choice = input(f'Во что превратить пешку? (Q/R/B/N): ').upper()
                if promotion_choice in ['Q', 'R', 'B', 'N']:
                    return promotion_choice
                else:
                    print('Неверный выбор. Пожалуйста, выберите Q, R, B или N.')
            except ValueError:
                print('Неверный ввод. Попробуйте еще раз.')

    # Выводит историю ходов в формате шахматной нотации
    def print_moves_history(self):

        print('История ходов:')

        # С помощью enumerate пишем ходы
        for i, move in enumerate(self.moves_history):
            # Белые и оставляем место для черных
            if i % 2 == 0:  # Белые
                print(f'{i // 2 + 1}. {move}', end=' ')
            # Черные
            else:
                print(move)
        print()

    def generate_en_passant_notation(self, start_figure, start_row, start_col, end_row, end_col):
        # Получаем координаты в нотационном виде
        start_ceil_notation = self.move_player_to_notation_coords(start_row, start_col)
        end_ceil_notation = self.move_player_to_notation_coords(end_row, end_col)

        # Нотация для взятия на проходе всегда включает столбец начальной клетки пешки
        notation = f'{start_ceil_notation[0]}x{end_ceil_notation}'
        return notation


if __name__ == '__main__':
    game = Game()
    game.start_game()

# Правила написать