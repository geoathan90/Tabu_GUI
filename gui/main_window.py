
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from gui.pages.home_page import HomePage
from gui.pages.suspension_page import SuspensionPage
from gui.pages.terminal_page import TerminalPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tabu GUI")
        self.resize(1350, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = HomePage(
            open_suspension_callback=self.open_suspension_page,
            open_terminal_callback=self.open_terminal_page,
        )

        self.suspension_page = SuspensionPage(
            home_callback=self.go_home,
        )

        self.terminal_page = TerminalPage(
            home_callback=self.go_home,
        )

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.suspension_page)
        self.stack.addWidget(self.terminal_page)

        self.stack.setCurrentWidget(self.home_page)

    def go_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def open_suspension_page(self):
        self.stack.setCurrentWidget(self.suspension_page)

    def open_terminal_page(self):
        self.stack.setCurrentWidget(self.terminal_page)