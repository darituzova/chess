import os
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt
from board import Board


class PieceSprite(QGraphicsPixmapItem):

    def __init__(self, figure, square_size, piece_style="classic"):
        super().__init__()
        self.figure = figure
        self.square_size = square_size
        self.piece_style = piece_style
        self._init_pixmap()

    def _init_pixmap(self):
        # Поддержка двух стилей: "classic" и "basics"
        PIECES_DIR = os.path.join("pieces", self.piece_style)
        
        PIECE_MAP = {
            "P": "wp.png", "p": "bp.png",
            "R": "wr.png", "r": "br.png",
            "N": "wn.png", "n": "bn.png",
            "B": "wb.png", "b": "bb.png",
            "Q": "wq.png", "q": "bq.png",
            "K": "wk.png", "k": "bk.png",
        }
        
        filename = PIECE_MAP.get(self.figure.symbol)
        path = os.path.join(PIECES_DIR, filename) if filename else ""

        if filename and os.path.exists(path):
            pix = QPixmap(path)
            w = int(self.square_size * 0.9)
            h = int(self.square_size * 0.9)
            pix = pix.scaled(
                w,
                h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.setPixmap(pix)
        else:
            # fallback на букву
            text = QGraphicsTextItem(self.figure.symbol.upper())
            font = QFont("Arial", 32, QFont.Bold)
            text.setFont(font)
            text.setDefaultTextColor(Qt.black if self.figure.color == "white" else Qt.darkGray)
            br = text.boundingRect()
            pix = QPixmap(int(br.width()) + 4, int(br.height()) + 4)
            pix.fill(Qt.transparent)
            painter = QPainter(pix)
            text.paint(painter, None, None)
            painter.end()
            self.setPixmap(pix)


class ChessBoardWidget(QGraphicsView):

    def __init__(self, parent=None, piece_style="classic"):
        super().__init__(parent)
        
        self.board = Board()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Стиль фигур (передается из main_window.py)
        self.piece_style = piece_style

        # большая доска, но с аккуратными отступами
        self.board_size = 700          # квадрат 600x600
        self.margin_x = 35             # слева
        self.margin_y = 10             # сверху
        self.bottom_space = 30         # под буквами a–h
        self.square_size = self.board_size // 8

        self.board_item = None
        self.piece_items = []
        self.cell_coords = {}          # (row, col) -> (x, y) в пикселях

        self._init_view()
        self._draw_board()
        self._draw_coordinates()
        self._draw_pieces()

    def set_piece_style(self, style):
        """Изменить стиль фигур динамически."""
        if style in ["classic", "basics"]:
            self.piece_style = style
            self._draw_pieces()

    def _init_view(self):
        self.setFixedSize(
            self.board_size + self.margin_x + 35,
            self.board_size + self.margin_y + self.bottom_space + 10,
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("QGraphicsView { border: none; background: #fefefe; }")

    def _draw_board(self):
        pix = QPixmap(self.board_size, self.board_size)
        pix.fill(Qt.transparent)

        painter = QPainter(pix)
        light = QColor(240, 217, 181)
        dark = QColor(181, 136, 99)

        self.cell_coords.clear()

        for row in range(8):
            for col in range(8):
                x = col * self.square_size
                y = row * self.square_size

                self.cell_coords[(row, col)] = (x, y)

                color = light if (row + col) % 2 == 0 else dark
                painter.fillRect(x, y, self.square_size, self.square_size, color)
                painter.setPen(QPen(QColor(200, 180, 150), 1))
                painter.drawRect(x, y, self.square_size, self.square_size)

        painter.end()

        self.board_item = QGraphicsPixmapItem(pix)
        self.board_item.setPos(self.margin_x, self.margin_y)
        self.scene.addItem(self.board_item)

    def _draw_coordinates(self):
        font = QFont("Arial", 11, QFont.Bold)

        # буквы под доской, в полосе bottom_space — гарантированно видны
        for col, letter in enumerate("abcdefgh"):
            text = self.scene.addText(letter, font)
            text.setDefaultTextColor(QColor(80, 80, 80))
            x_center = self.margin_x + col * self.square_size + self.square_size / 2
            y = self.margin_y + self.board_size + 6
            br = text.boundingRect()
            text.setPos(x_center - br.width() / 2, y)

        # цифры слева, центр по ряду; 1 внизу, 8 наверху
        for rank in range(1, 9):
            text = self.scene.addText(str(rank), font)
            text.setDefaultTextColor(QColor(80, 80, 80))
            row = 8 - rank
            y_center = self.margin_y + row * self.square_size + self.square_size / 2
            x = self.margin_x - 6
            br = text.boundingRect()
            text.setPos(x - br.width(), y_center - br.height() / 2)

    def _draw_pieces(self):
        for item in self.piece_items:
            self.scene.removeItem(item)
        self.piece_items.clear()

        for row in range(8):
            for col in range(8):
                fig = self.board.get_figure(row, col)
                if not fig:
                    continue

                sprite = PieceSprite(fig, self.square_size, self.piece_style)

                bx, by = self.cell_coords[(row, col)]
                center_x = self.margin_x + bx + self.square_size / 2
                center_y = self.margin_y + by + self.square_size / 2

                br = sprite.boundingRect()
                sprite.setPos(center_x - br.width() / 2, center_y - br.height() / 2)

                self.scene.addItem(sprite)
                self.piece_items.append(sprite)
