from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout


class HomePage(QWidget):
    def __init__(self, open_suspension_callback, open_terminal_callback):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Επιλογή Ενότητας")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        btn_suspension = QPushButton("Βέλη Ευθυγραμμίας")
        btn_suspension.setMinimumHeight(60)
        btn_suspension.setFixedWidth(260)
        btn_suspension.clicked.connect(open_suspension_callback)

        btn_terminal = QPushButton("Τερματικά Βέλη")
        btn_terminal.setMinimumHeight(60)
        btn_terminal.setFixedWidth(260)
        btn_terminal.clicked.connect(open_terminal_callback)

        layout.addStretch()
        layout.addWidget(title, alignment=Qt.AlignHCenter)
        layout.addSpacing(20)
        layout.addWidget(btn_suspension, alignment=Qt.AlignHCenter)
        layout.addWidget(btn_terminal, alignment=Qt.AlignHCenter)
        layout.addStretch()