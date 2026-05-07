from PySide6.QtWidgets import QMainWindow, QStackedWidget

from gui.pages.home_page import HomePage
from gui.pages.suspension_page import SuspensionPage
from gui.pages.terminal_page import TerminalPage
from gui.pages.tensions_page import TensionsPage
from gui.utils.conductor_catalog import create_session_catalog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tabu GUI")
        self.resize(1350, 800)

        self.app_state = {
            "conductors": create_session_catalog()
        }

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = HomePage(
            open_suspension_callback=self.open_suspension_page,
            open_tensions_callback=self.open_tensions_page,
            open_terminal_callback=self.open_terminal_page,
        )

        self.suspension_page = SuspensionPage(
            home_callback=self.go_home,
            app_state=self.app_state,
        )

        self.tensions_page = TensionsPage(
            home_callback=self.go_home,
            app_state=self.app_state,
        )

        self.terminal_page = TerminalPage(
            home_callback=self.go_home,
        )

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.suspension_page)
        self.stack.addWidget(self.tensions_page)
        self.stack.addWidget(self.terminal_page)

        self.stack.setCurrentWidget(self.home_page)

    def go_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def open_suspension_page(self):
        self.suspension_page.refresh_conductor_dropdown()
        self.stack.setCurrentWidget(self.suspension_page)

    def open_tensions_page(self):
        self.tensions_page.refresh_conductor_dropdown()
        self.stack.setCurrentWidget(self.tensions_page)

    def open_terminal_page(self):
        self.stack.setCurrentWidget(self.terminal_page)