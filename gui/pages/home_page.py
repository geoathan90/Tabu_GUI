from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout


class HomePage(QWidget):
    def __init__(self, open_suspension_callback, open_terminal_callback):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # ---------------- Logo ----------------
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)

        logo_path = Path(__file__).resolve().parent.parent / "Logo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    220,
                    220,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self.logo_label.setPixmap(pixmap)
            else:
                self.logo_label.hide()
        else:
            self.logo_label.hide()

        # ---------------- Title ----------------
        title = QLabel("Επιλογή Ενότητας")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        # ---------------- Main buttons ----------------
        btn_suspension = QPushButton("Βέλη Ευθυγραμμίας")
        btn_suspension.setMinimumHeight(60)
        btn_suspension.setFixedWidth(260)
        btn_suspension.clicked.connect(open_suspension_callback)

        btn_terminal = QPushButton("Τερματικά Βέλη")
        btn_terminal.setMinimumHeight(60)
        btn_terminal.setFixedWidth(260)
        btn_terminal.clicked.connect(open_terminal_callback)

        # ---------------- Footer links ----------------
        docs_label = QLabel(
            '<a href="https://PLACEHOLDER-DOCS-LINK">Οδηγός Χρήσης</a>'
        )
        docs_label.setAlignment(Qt.AlignCenter)
        docs_label.setOpenExternalLinks(True)
        docs_label.setTextFormat(Qt.RichText)
        docs_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        docs_label.setStyleSheet("font-size: 13px;")

        support_label = QLabel(
            '<a href="mailto:PLACEHOLDER@EMAIL.COM">PLACEHOLDER@EMAIL.COM</a>'
        )
        support_label.setAlignment(Qt.AlignCenter)
        support_label.setOpenExternalLinks(True)
        support_label.setTextFormat(Qt.RichText)
        support_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        support_label.setStyleSheet("font-size: 13px;")

        # ---------------- Layout ----------------
        layout.addStretch()
        layout.addWidget(self.logo_label, alignment=Qt.AlignHCenter)
        layout.addSpacing(8)
        layout.addWidget(title, alignment=Qt.AlignHCenter)
        layout.addSpacing(20)
        layout.addWidget(btn_suspension, alignment=Qt.AlignHCenter)
        layout.addWidget(btn_terminal, alignment=Qt.AlignHCenter)
        layout.addStretch()
        layout.addWidget(docs_label, alignment=Qt.AlignHCenter)
        layout.addWidget(support_label, alignment=Qt.AlignHCenter)
        layout.addSpacing(10)