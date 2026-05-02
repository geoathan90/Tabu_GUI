from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QTextEdit,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTableWidget,
)

from tabu_scripts.data import TEMPS, available_conductors
from gui.utils.parsing import parse_series
from gui.utils.table_helpers import populate_table_widget


class SuspensionPage(QWidget):
    def __init__(
        self,
        home_callback,
        solve_one_callback,
        solve_all_callback,
        export_callback,
    ):
        super().__init__()

        main_layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()

        self.home_button = QPushButton("HOME")
        self.home_button.clicked.connect(home_callback)

        page_title = QLabel("Βέλη Ευθυγραμμίας")
        page_title.setStyleSheet("font-size: 22px; font-weight: bold;")

        top_bar.addWidget(self.home_button)
        top_bar.addSpacing(15)
        top_bar.addWidget(page_title)
        top_bar.addStretch()

        content_layout = QHBoxLayout()

        left_panel = QWidget()
        left_layout = QGridLayout(left_panel)

        self.spans_edit = QTextEdit()
        self.heights_edit = QTextEdit()

        self.conductor_combo = QComboBox()
        self.conductor_combo.addItems(available_conductors())

        self.temp_combo = QComboBox()
        for t in TEMPS:
            self.temp_combo.addItem(str(int(t)))

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.solve_one_button = QPushButton("Επίλυση μίας θερμοκρασίας")
        self.solve_one_button.clicked.connect(solve_one_callback)

        self.solve_all_button = QPushButton("Επίλυση όλων των θερμοκρασιών")
        self.solve_all_button.clicked.connect(solve_all_callback)

        self.export_button = QPushButton("Εξαγωγή αποτελεσμάτων σε XLSX")
        self.export_button.clicked.connect(export_callback)
        self.export_button.setEnabled(False)

        left_layout.addWidget(QLabel("Ανοίγματα (m)"), 0, 0)
        left_layout.addWidget(self.spans_edit, 1, 0)
        left_layout.addWidget(self.summary_label, 2, 0)

        left_layout.addWidget(QLabel("Υψομετρικές Διαφορές (m)"), 3, 0)
        left_layout.addWidget(self.heights_edit, 4, 0)

        left_layout.addWidget(QLabel("Τύπος Αγωγού"), 5, 0)
        left_layout.addWidget(self.conductor_combo, 6, 0)

        left_layout.addWidget(QLabel("Θερμοκρασία (°C)"), 7, 0)
        left_layout.addWidget(self.temp_combo, 8, 0)

        left_layout.addWidget(self.solve_one_button, 9, 0)
        left_layout.addWidget(self.solve_all_button, 10, 0)
        left_layout.addWidget(self.export_button, 11, 0)

        self.table = QTableWidget()

        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(self.table, 2)

        main_layout.addLayout(top_bar)
        main_layout.addSpacing(10)
        main_layout.addLayout(content_layout)

    def get_inputs(self):
        spans = parse_series(self.spans_edit.toPlainText())
        heights = parse_series(self.heights_edit.toPlainText())

        if len(spans) != len(heights):
            raise ValueError("Τα ανοίγματα και οι υψομετρικές πρέπει να έχουν το ίδιο πλήθος τιμών.")
        if len(spans) == 0:
            raise ValueError("Χρειάζεται τουλάχιστον μία τιμή για ανοίγματα και υψομετρικές.")

        conductor = self.conductor_combo.currentText()
        temperature_C = float(self.temp_combo.currentText())

        return spans, heights, conductor, temperature_C

    def set_summary_text(self, text):
        self.summary_label.setText(text)

    def set_export_enabled(self, enabled):
        self.export_button.setEnabled(enabled)

    def show_dataframe(self, df):
        populate_table_widget(self.table, df)