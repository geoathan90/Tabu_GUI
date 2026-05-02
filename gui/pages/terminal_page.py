from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout


class TerminalPage(QWidget):
    def __init__(self, home_callback):
        super().__init__()

        layout = QVBoxLayout(self)

        home_button = QPushButton("HOME")
        home_button.clicked.connect(home_callback)

        title = QLabel("Τερματικά Βέλη")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        message = QLabel("Δεν έχει ολοκληρωθεί ακόμη.")
        message.setStyleSheet("font-size: 16px;")

        layout.addWidget(home_button)
        layout.addSpacing(10)
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(message)
        layout.addStretch()