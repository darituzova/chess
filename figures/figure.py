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
    
    # Возвращение типа фигуры
    def get_type(self):
        return self.figure_type
