import os
import sys

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main():
    if "CODESPACES" in os.environ and "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
