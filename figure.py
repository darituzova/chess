# Класс фигуры (общее у фигур)
class Figure:

    # Инициализируем фигуру 
    def __init__(self, color, position, figure_type):
        
        # Цвет, позиция, тип фигуры, и двигалась ли она (для пешки и рокировки)
        self.color = color
        self.position = position
        self.figure_type = figure_type.lower()
        self.has_moved = False

    # Возможные ходы (в дочерних классах)
    def get_correct_moves(self, board):
        pass
    
    # Проверка возможности хода в указанную позицию
    def can_move(self, to_position, board):
        # Используем get_correct_moves из дочернего класса
        possible_moves = self.get_correct_moves(board)
        return to_position in possible_moves
    
    # Обновление позиции фигуры и отметка о движении
    def move(self, to_position):
        self.position = to_position
        self.has_moved = True
    
    # Возвращение типа фигуры
    def get_type(self):
        return self.figure_type