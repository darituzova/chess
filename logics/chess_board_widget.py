# chess_board_widget.py
import os

from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsTextItem,
    QMessageBox,
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt

from .game import Game


class PieceSprite(QGraphicsPixmapItem):
    def __init__(self, figure, square_size, piece_style='classic'):
        super().__init__()
        self.figure = figure
        self.square_size = square_size
        self.piece_style = piece_style
        self._init_pixmap()

    def _init_pixmap(self):
        PIECES_DIR = os.path.join('pieces', self.piece_style)
        PIECE_MAP = {
            'P': 'wp.png', 'p': 'bp.png',
            'R': 'wr.png', 'r': 'br.png',
            'N': 'wn.png', 'n': 'bn.png',
            'B': 'wb.png', 'b': 'bb.png',
            'Q': 'wq.png', 'q': 'bq.png',
            'K': 'wk.png', 'k': 'bk.png',
        }

        filename = PIECE_MAP.get(self.figure.symbol)
        path = os.path.join(PIECES_DIR, filename) if filename else ''

        if filename and os.path.exists(path):
            pix = QPixmap(path)
            w = int(self.square_size * 0.9)
            h = int(self.square_size * 0.9)
            pix = pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(pix)
        else:
            text = QGraphicsTextItem(self.figure.symbol.upper())
            font = QFont('Arial', 32, QFont.Bold)
            text.setFont(font)
            text.setDefaultTextColor(
                Qt.black if self.figure.color == 'white' else Qt.darkGray
            )
            br = text.boundingRect()
            pix = QPixmap(int(br.width()) + 4, int(br.height()) + 4)
            pix.fill(Qt.transparent)
            painter = QPainter(pix)
            text.paint(painter, None, None)
            painter.end()
            self.setPixmap(pix)


class ChessBoardWidget(QGraphicsView):
    def __init__(self, parent=None, piece_style='classic'):
        super().__init__(parent)

        # Создание экземпляра игровой логики
        self.game = Game()

        # Инициализация графической сцены
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Параметры отображения доски
        self.piece_style = piece_style
        self.board_size = 700
        self.margin_x = 35
        self.margin_y = 10
        self.bottom_space = 30
        self.square_size = self.board_size // 8

        # Графические элементы доски
        self.board_item = None
        self.piece_items = []
        self.cell_coords = {}

        # Ссылки на UI элементы основного окна
        self.current_move_edit = None
        self.player_info_label = None
        self.timer_label = None

        # Состояние игры
        self.is_game_over = False
        self.parent_window = parent.window() if parent is not None else None

        # Callback для окончания игры
        self.game_over_callback = None

        # Имена игроков
        self.white_player_name = 'Белые'
        self.black_player_name = 'Чёрные'

        # Инициализация интерфейса и отрисовка
        self._init_view()
        self._draw_board()
        self._draw_coordinates()
        self._draw_pieces()

    # Связь с UI и именами
    def set_ui_elements(self, move_edit, player_label, timer_label):
        self.current_move_edit = move_edit
        self.player_info_label = player_label
        self.timer_label = timer_label
        self._update_player_info()

    # Установка имен игроков с изменяемыми значениями
    def set_players(self, white_name, black_name):
        self.white_player_name = white_name or 'Белые'
        self.black_player_name = black_name or 'Чёрные'
        self._update_player_info()

    # Палитра доски
    def _get_board_colors(self):
        if self.piece_style == 'basics':
            light = QColor(230, 242, 255)   # светло-голубой
            dark = QColor(90, 120, 160)     # синевато-серый
        else:  # classic
            light = QColor(240, 217, 181)
            dark = QColor(181, 136, 99)
        return light, dark

    # Ход из текстового поля
    def make_move_from_text(self):
        if self.is_game_over:
            return False
        if not self.current_move_edit:
            return False

        # Получение текста хода из поля ввода
        move_text = self.current_move_edit.text().strip().lower()
        if not move_text:
            QMessageBox.warning(self, 'Ошибка', 'Введите ход!')
            return False

        try:
            # Сохранение текущего игрока и состояния шаха
            current_color = self.game.current_player
            is_in_check_before = self.game.board.is_check(current_color)

            # Обработка специальных ходов рокировкой
            if move_text == 'рокировка k':
                start_row, start_col, end_row, end_col = self.game.handle_castling(
                    'kingside'
                )
            elif move_text == 'рокировка q':
                start_row, start_col, end_row, end_col = self.game.handle_castling(
                    'queenside'
                )
            else:
                # Парсинг стандартного хода в формате 'e2 e4'
                parts = move_text.split()
                if len(parts) != 2:
                    raise ValueError('Формат: "e2 e4"')
                start, end = parts
                if len(start) != 2 or len(end) != 2:
                    raise ValueError('Формат: "e2 e4"')
                start_row, start_col = self._move_player_to_board_coords(start)
                end_row, end_col = self._move_player_to_board_coords(end)

            # Выполнение хода через игровую логику
            success = self.game.try_move(start_row, start_col, end_row, end_col)

            # Обработка неудачного хода
            if not success:
                if is_in_check_before:
                    color_ru = 'белые' if current_color == 'white' else 'черные'
                    QMessageBox.warning(
                        self,
                        'Ошибка хода',
                        f'{color_ru.title()} под шахом.\nСделайте ход, который убирает шах.',
                    )
                else:
                    QMessageBox.warning(self, 'Неверный ход', 'Попробуйте другой ход.')
                return False

            # Обновление визуального состояния
            self._draw_pieces()
            self.current_move_edit.clear()

            # Проверка шаха/мата для противника
            opponent = 'black' if current_color == 'white' else 'white'
            self._handle_check_and_mate(opponent)

            # Переключение хода и обновление UI
            if not self.is_game_over:
                self.game.current_player = opponent
                self._update_player_info()

            return True

        # Обработка ошибок ввода
        except ValueError as e:
            QMessageBox.warning(self, 'Ошибка ввода', str(e))
            return False
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Неожиданная ошибка: {str(e)}')
            return False

    # Шах и мат
    def _handle_check_and_mate(self, color_under_attack):
        # Проверка мата
        if self.game.board.is_checkmate(color_under_attack):
            self.is_game_over = True
            loser_ru = 'белым' if color_under_attack == 'white' else 'черным'
            winner_ru = 'Черные' if color_under_attack == 'white' else 'Белые'

            # Вызов callback или закрытие окна
            if self.game_over_callback:
                self.game_over_callback(
                    result_text=f'Мат {loser_ru}. Победили {winner_ru}.'
                )
            else:
                QMessageBox.information(
                    self,
                    'Мат',
                    f'Мат {loser_ru}. Победили {winner_ru}.',
                )
                if self.parent_window is not None:
                    self.parent_window.close()
                else:
                    self.close()
            return

        # Уведомление о шахе
        if self.game.board.is_check(color_under_attack):
            color_ru = 'белым' if color_under_attack == 'white' else 'черным'
            QMessageBox.information(self, 'Шах', f'Шах {color_ru}!')

    # Вспомогательное
    def _move_player_to_board_coords(self, ceil_move):
        row = 7 - (int(ceil_move[1]) - 1)
        col = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].index(ceil_move[0])
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError('Координаты за пределами доски')
        return row, col

    # Обновление информации о текущем игроке
    def _update_player_info(self):
        if self.player_info_label:
            if self.game.current_player == 'white':
                text = f'Ход: {self.white_player_name}'
            else:
                text = f'Ход: {self.black_player_name}'
            self.player_info_label.setText(text)

    # Смена стиля фигур с перерисовкой
    def set_piece_style(self, style):
        if style in ['classic', 'basics']:
            self.piece_style = style
            self._draw_board()
            self._draw_pieces()

    # Рисование доски и фигур
    def _init_view(self):
        # Фиксированный размер виджета с отступами
        self.setFixedSize(
            self.board_size + self.margin_x + 35,
            self.board_size + self.margin_y + self.bottom_space + 10,
        )
        # Отключение скроллбаров
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Стилизация фона
        self.setStyleSheet('QGraphicsView { border: none; background: #fefefe; }')

    # Создание pixmap для доски
    def _draw_board(self):
        pix = QPixmap(self.board_size, self.board_size)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)

        # Получение цветов палитры
        light, dark = self._get_board_colors()

        # Очистка и заполнение координат клеток
        self.cell_coords.clear()
        for row in range(8):
            for col in range(8):
                x = col * self.square_size
                y = row * self.square_size
                self.cell_coords[(row, col)] = (x, y)
                # Чередование цветов клеток
                color = light if (row + col) % 2 == 0 else dark
                painter.fillRect(x, y, self.square_size, self.square_size, color)
                # Рисование границ клеток
                painter.setPen(QPen(QColor(200, 180, 150), 1))
                painter.drawRect(x, y, self.square_size, self.square_size)

        # Добавление доски
        painter.end()
        if self.board_item:
            self.scene.removeItem(self.board_item)
        self.board_item = QGraphicsPixmapItem(pix)
        self.board_item.setPos(self.margin_x, self.margin_y)
        self.scene.addItem(self.board_item)

    # Рисовка координат
    def _draw_coordinates(self):
        # Шрифт для координат
        font = QFont('Arial', 11, QFont.Bold)

        # Горизонтальные координаты a-h
        for col, letter in enumerate('abcdefgh'):
            text = self.scene.addText(letter, font)
            text.setDefaultTextColor(QColor(80, 80, 80))
            x_center = self.margin_x + col * self.square_size + self.square_size / 2
            y = self.margin_y + self.board_size + 6
            br = text.boundingRect()
            text.setPos(x_center - br.width() / 2, y)

        # Вертикальные координаты 1-8
        for rank in range(1, 9):
            text = self.scene.addText(str(rank), font)
            text.setDefaultTextColor(QColor(80, 80, 80))
            row = 8 - rank
            y_center = self.margin_y + row * self.square_size + self.square_size / 2
            x = self.margin_x - 6
            br = text.boundingRect()
            text.setPos(x - br.width(), y_center - br.height() / 2)

    # Рисовка фигур
    def _draw_pieces(self):
        # Удаление старых спрайтов фигур
        for item in self.piece_items:
            self.scene.removeItem(item)
        self.piece_items.clear()

        # Создание спрайтов для всех фигур на доске
        for row in range(8):
            for col in range(8):
                fig = self.game.board.get_figure(row, col)
                if not fig:
                    continue
                # Создание спрайта фигуры
                sprite = PieceSprite(fig, self.square_size, self.piece_style)
                bx, by = self.cell_coords[(row, col)]

                center_x = self.margin_x + bx + self.square_size / 2
                center_y = self.margin_y + by + self.square_size / 2
                br = sprite.boundingRect()
                sprite.setPos(
                    center_x - br.width() / 2,
                    center_y - br.height() / 2,
                )
                self.scene.addItem(sprite)
                self.piece_items.append(sprite)