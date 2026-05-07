from pathlib import Path
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


def resource_path(*parts):
    """
    Return an absolute path for a resource.

    Works both:
    - when running from source
    - when running from a PyInstaller-built executable
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parents[2]

    return base.joinpath(*parts)


class HomePage(QWidget):
    def __init__(self, open_suspension_callback, open_tensions_callback, open_terminal_callback):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # ---------------- Logo ----------------
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)

        logo_path = resource_path("gui", "Logo.png")

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

        btn_tensions = QPushButton("Επίλυση Τριτοβάθμιας")
        btn_tensions.setMinimumHeight(60)
        btn_tensions.setFixedWidth(260)
        btn_tensions.clicked.connect(open_tensions_callback)

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
        docs_label.setStyleSheet("font-size: 16px;")

        divider_label = QLabel("|")
        divider_label.setAlignment(Qt.AlignCenter)
        divider_label.setStyleSheet("font-size: 16px;")

        support_label = QLabel(
            '<a href="mailto:PLACEHOLDER@EMAIL.COM">Επικοινωνία</a>'
        )
        support_label.setAlignment(Qt.AlignCenter)
        support_label.setOpenExternalLinks(True)
        support_label.setTextFormat(Qt.RichText)
        support_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        support_label.setStyleSheet("font-size: 16px;")

        footer_widget = QWidget()
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(8)
        footer_layout.addStretch()
        footer_layout.addWidget(docs_label)
        footer_layout.addWidget(divider_label)
        footer_layout.addWidget(support_label)
        footer_layout.addStretch()

        # ---------------- Layout ----------------
        layout.addStretch()
        layout.addWidget(self.logo_label, alignment=Qt.AlignHCenter)
        layout.addSpacing(8)
        layout.addWidget(title, alignment=Qt.AlignHCenter)
        layout.addSpacing(20)
        layout.addWidget(btn_suspension, alignment=Qt.AlignHCenter)
        layout.addWidget(btn_tensions, alignment=Qt.AlignHCenter)
        layout.addWidget(btn_terminal, alignment=Qt.AlignHCenter)
        layout.addStretch()
        layout.addWidget(footer_widget)
        layout.addSpacing(10)