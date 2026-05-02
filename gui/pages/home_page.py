from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout


class HomePage(QWidget):
    def __init__(self, open_suspension_callback, open_terminal_callback):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Επιλογή Ενότητας")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        btn_alignment = QPushButton("Βέλη Ευθυγραμμίας")
        btn_alignment.setMinimumHeight(60)
        btn_alignment.clicked.connect(open_suspension_callback)

        btn_terminal = QPushButton("Τερματικά Βέλη")
        btn_terminal.setMinimumHeight(60)
        btn_terminal.clicked.connect(open_terminal_callback)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(btn_alignment)
        layout.addWidget(btn_terminal)
        layout.addStretch()