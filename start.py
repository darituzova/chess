import sys

from PyQt5.QtWidgets import QApplication

from main_menu import MainMenu


def main():
    """Точка входа в приложение. Сначала открывается главное меню."""
    app = QApplication(sys.argv)

    # Создаём и показываем главное меню
    menu = MainMenu()
    menu.show()

    # Запуск основного цикла приложения
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
