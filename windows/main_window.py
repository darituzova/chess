import sys
import time
import json
import os

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QMessageBox
)
from PyQt5.QtCore import QSettings, QTimer
    # QSettings – хранение настроек, QTimer – таймер для времени партии
from PyQt5.uic import loadUi

from logics.chess_board_widget import ChessBoardWidget
from .final_window import FinalWindow
from .history_moves import HistoryMovesWindow
from .settings_window import SettingsWindow

# Файл для хранения статистики игроков
STATS_FILE = 'data/stats.json'

# Главное игровое окно с шахматной доской, таймером, статистикой и управлением партией
class MainWindow(QMainWindow):
    def __init__(self, white_name: str = '', black_name: str = '', parent=None):
        super().__init__(parent)

        # Получаем путь к текущему файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Переходим на уровень выше (из windows в корень проекта)
        project_root = os.path.dirname(current_dir)
        
        # Формируем путь к файлу ui
        ui_path = os.path.join(project_root, 'ui', 'main_window.ui')
        
        # Загружаем UI файл
        loadUi(ui_path, self)
        
        # Гарантируем существование папки под данные
        os.makedirs('data', exist_ok=True)

        # Загружаем настройки приложения
        self.settings = QSettings('MyChessApp', 'ChessSettings')
        piece_style = self.settings.value('piece_style', 'classic')

        # Имена игроков
        self.white_name = white_name or 'Белые'
        self.black_name = black_name or 'Чёрные'
        self.parent_menu = parent

        # Таймер партии
        self.game_start_time = None
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.update_game_timer)
        self.total_game_time = '00:00:00'

        # Инициализация подписей, если они есть в .ui
        if hasattr(self, 'whitePlayerLabel'):
            self.whitePlayerLabel.setText(f'Белые: {self.white_name}')
        if hasattr(self, 'playerInfoLabel'):
            self.playerInfoLabel.setText('Ход: Белые')
        if hasattr(self, 'timerLabel'):
            self.timerLabel.setText('Время: 00:00:00')

        # Размещаем шахматную доску в отведённом фрейме
        layout = QVBoxLayout(self.chessBoardFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Создание виджета шахматной доски
        self.chess_board = ChessBoardWidget(
            self.chessBoardFrame,
            piece_style=piece_style
        )
        layout.addWidget(self.chess_board)

        # Передаём доске имена игроков и нужные элементы интерфейса
        self.chess_board.set_players(self.white_name, self.black_name)
        self.chess_board.set_ui_elements(
            getattr(self, 'currentMoveEdit', None),
            getattr(self, 'playerInfoLabel', None),
            getattr(self, 'timerLabel', None),
        )

        # Подключаем кнопки
        self.connect_buttons()

        # Колбэк, который доска вызывает при окончании игры
        self.chess_board.game_over_callback = self.show_final_window

    #  Подключение кнопок
    def connect_buttons(self) -> None:
        buttons = {
            'makeMoveButton': self.make_move_from_text_wrapper,
            'historyButton': self.show_history_direct,
            'surrenderButton': self.surrender_game,
            'drawButton': self.propose_draw,
            'menuButton': self.confirm_go_to_menu,
            'settingsButton': self.open_settings,
        }

        for btn_name, handler in buttons.items():
            if hasattr(self, btn_name):
                getattr(self, btn_name).clicked.connect(handler)

    # Работа со статистикой
    def load_stats(self) -> dict:
        # Загрузка статистики игроков из файла
        if not os.path.exists(STATS_FILE):
            return {}
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    # Сохранение обновлённой статистики в файл
    def save_stats(self, stats: dict) -> None:
        try:
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'Ошибка сохранения статистики: {e}')

    # Обновление статистики игроков в зависимости от результата партии
    def update_player_stats(
        self,
        white_winner: bool = False,
        black_winner: bool = False,
        draw: bool = False,
    ) -> None:

        stats = self.load_stats()

        # Победа белых
        if white_winner:
            stats.setdefault(self.white_name, {'wins': 0, 'losses': 0, 'draws': 0})
            stats[self.white_name]['wins'] += 1

            stats.setdefault(self.black_name, {'wins': 0, 'losses': 0, 'draws': 0})
            stats[self.black_name]['losses'] += 1

        # Победа чёрных
        elif black_winner:
            stats.setdefault(self.black_name, {'wins': 0, 'losses': 0, 'draws': 0})
            stats[self.black_name]['wins'] += 1

            stats.setdefault(self.white_name, {'wins': 0, 'losses': 0, 'draws': 0})
            stats[self.white_name]['losses'] += 1

        # Ничья
        elif draw:
            stats.setdefault(self.white_name, {'wins': 0, 'losses': 0, 'draws': 0})
            stats[self.white_name]['draws'] += 1

            stats.setdefault(self.black_name, {'wins': 0, 'losses': 0, 'draws': 0})
            stats[self.black_name]['draws'] += 1

        self.save_stats(stats)

    # Формирование текстовой строки статистики конкретного игрока
    def get_player_stats_text(self, player_name: str) -> str:
        stats = self.load_stats()
        player_stats = stats.get(player_name, {'wins': 0, 'losses': 0, 'draws': 0})

        wins = player_stats.get('wins', 0)
        losses = player_stats.get('losses', 0)
        draws = player_stats.get('draws', 0)

        return f'{player_name}: {wins} побед, {losses} поражений, {draws} ничьих'

    # Запустить таймер партии
    def start_game_timer(self) -> None:
        self.game_start_time = time.time()
        self.game_timer.start(1000)  # обновление каждую секунду

    # Остановить таймер партии
    def stop_game_timer(self) -> None:
        self.game_timer.stop()

    # Раз в секунду обновлять надпись с временем
    def update_game_timer(self) -> None:
        if self.game_start_time:
            elapsed = int(time.time() - self.game_start_time)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.total_game_time = f'{hours:02d}:{minutes:02d}:{seconds:02d}'

            if hasattr(self, 'timerLabel'):
                self.timerLabel.setText(f'Время: {self.total_game_time}')

    # Логика управления
    # Обёртка над методом доски: при первом ходе запускает таймер
    def make_move_from_text_wrapper(self) -> None:
        if not self.game_start_time:
            self.start_game_timer()
        self.chess_board.make_move_from_text()

    # Запрос подтверждения перед переходом в меню
    def confirm_go_to_menu(self) -> None:
        reply = QMessageBox.question(
            self,
            'Меню',
            'Перейти в меню? Игра будет прервана.',
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.stop_game_timer()
            self.go_to_menu()

    # Открыть главное меню
    def go_to_menu(self) -> None:
        try:
            from .main_menu import MainMenu

            menu_window = MainMenu()
            menu_window.show()
            self.parent_menu = menu_window
        except ImportError:
            print('Файл main_menu.py не найден')
        self.close()

    # Открыть окно настроек
    def open_settings(self) -> None:
        try:
            settings_window = SettingsWindow(parent=self)
            settings_window.show()
        except ImportError:
            QMessageBox.warning(self, 'Ошибка', 'Настройки недоступны')

    # Показать окно истории ходов прямо из главного окна
    def show_history_direct(self) -> None:
        moves_history = getattr(self.chess_board.game, 'moves_history', [])
        if not moves_history:
            QMessageBox.information(self, 'История', 'Ходов нет')
            return

        try:
            HistoryMovesWindow(moves_history, parent=self).show()
        except Exception:
            QMessageBox.warning(self, 'Ошибка', 'history_moves.py не найден')

    # Отображение итогового окна с результатами партии, статистикой и временем
    # Вызывается доской при мате или методами сдачи/ничьей
    def show_final_window(self, result_text: str = 'Партия завершена') -> None:
        # Останавливаем таймер и берём итоговое время
        self.stop_game_timer()
        game_time = self.total_game_time

        # Готовим текст статистики
        white_stats_text = self.get_player_stats_text(self.white_name)
        black_stats_text = self.get_player_stats_text(self.black_name)

        # Берём историю ходов из объекта игры (если реализована)
        moves_history = getattr(self.chess_board.game, 'moves_history', [])

        # Колбэк для кнопки 'Меню' во финальном окне
        def menu_callback():
            self.go_to_menu()

        # Создаём новое окно игры с теми же игроками.
        def play_again_callback():
            # Сохраняем ссылку на родительское меню, если оно нужно
            parent = self.parent() if hasattr(self, 'parent') else None
            
            # Сохраняем имена игроков
            white_name = getattr(self, 'white_name', 'Белые')
            black_name = getattr(self, 'black_name', 'Черные')
            
            # Закрываем текущее окно
            self.close()
            
            # Проверяем, не уничтожен ли уже родитель
            if parent and parent.isWidgetType() and not parent.isHidden():
                parent_menu = parent
            else:
                parent_menu = None
            
            # Создаем новое окно
            new_window = MainWindow(
                white_name,
                black_name,
                parent=parent_menu,
            )
            new_window.show()

        # Создаём и настраиваем финальное окно
        self.final_window = FinalWindow(
            result_text=result_text,
            white_stats=white_stats_text,
            black_stats=black_stats_text,
            game_time=game_time,
            parent=self,
            menu_callback=menu_callback,
            play_again_callback=play_again_callback,
            moves_history=moves_history,
        )

        # Скрываем окно с доской и показываем окно результата
        self.hide()
        self.final_window.show()

    # Сдача и ничья 
    # Текущий игрок сдаётся, объявляем победителя и показываем итоговое окно
    def surrender_game(self) -> None:
        current_player = getattr(self.chess_board.game, 'current_player', 'white')
        player_name = self.white_name if current_player == 'white' else self.black_name

        reply = QMessageBox.question(
            self,
            'Сдаться',
            f'{player_name} сдаётся?',
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.stop_game_timer()

            winner_name = (
                self.black_name if current_player == 'white' else self.white_name
            )

            # Обновляем статистику
            self.update_player_stats(
                black_winner=(current_player == 'white'),
                white_winner=(current_player == 'black'),
            )

            # Показываем итоговое окно
            self.show_final_window(f'{winner_name} победил! {player_name} сдался')

    # Предложение ничьи, при согласии фиксируем ничью и итоговое окно
    def propose_draw(self) -> None:
        current_player = getattr(self.chess_board.game, 'current_player', 'white')
        proposer_name = self.white_name if current_player == 'white' else self.black_name

        reply = QMessageBox.question(
            self,
            'Ничья',
            f'{proposer_name} предлагает ничью. Согласиться?',
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Обновляем статистику как ничью
            self.update_player_stats(draw=True)
            # Показываем итоговое окно
            self.show_final_window('Партия завершилась ничьёй')
        else:
            # Уведомление об отказе от ничьей
            QMessageBox.information(
                self,
                'Ничья отклонена',
                f'{proposer_name} получил отказ в ничьей.')


# Возможность запускать окно напрямую из этого файла
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())