import numpy as np
import pandas as pd

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QTextEdit,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
    QStackedWidget,
)

from data import TEMPS, available_conductors
from engine import solve_one_temperature
from output import build_one_temperature_dataframe, format_dataframe_for_export


GREEK_HEADERS = {
    "temperature_C": "Θερμοκρασία",
    "span_m": "Άνοιγμα",
    "height_m": "Υψομετρική",
    "T_ref_kg": "Τάνυση με κατακόρυφους μονωτήρες",
    "H_solution_kg": "Τάνυση με αγωγούς στις τροχαλίες",
    "sag_eq_m": "Βέλος με κατακόρυφους μονωτήρες",
    "sag_alt_m": "Βέλος με αγωγούς στις τροχαλίες",
    "diorthosi_geometric_m": "Γεωμετρική Διόρθωση",
    "diorthosi_elastic_m": "Ελαστική Διόρθωση",
    "diorthosi_combined_m": "Συνολική Διόρθωση",
}


def parse_series(raw_text):
    """
    Parse pasted numeric text into a NumPy array.

    Accepted separators:
    - new lines
    - spaces
    - tabs
    - commas
    - semicolons
    """
    if not raw_text.strip():
        return np.array([], dtype=float)

    txt = (
        raw_text.replace("\r", "\n")
                .replace("\t", "\n")
                .replace(",", "\n")
                .replace(";", "\n")
    )

    values = []
    for line in txt.split("\n"):
        t = line.strip()
        if not t:
            continue
        for part in t.split():
            values.append(float(part))

    return np.asarray(values, dtype=float)


def translate_headers(df):
    """
    Return a copy of the DataFrame with Greek column headers.
    """
    return df.rename(columns=GREEK_HEADERS)


def blank_row_df(columns):
    """
    Build a one-row DataFrame of empty strings, used as a spacer between
    temperature groups in the all-temperatures view.
    """
    return pd.DataFrame([{col: "" for col in columns}])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tabu GUI")
        self.resize(1350, 800)

        self.current_display_df = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = self.build_home_page()
        self.alignment_page = self.build_alignment_page()
        self.terminal_page = self.build_terminal_page()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.alignment_page)
        self.stack.addWidget(self.terminal_page)

        self.stack.setCurrentWidget(self.home_page)

    ############### Page builders ################

    def build_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Επιλογή Ενότητας")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        btn_alignment = QPushButton("Βέλη Ευθυγραμμίας")
        btn_alignment.setMinimumHeight(60)
        btn_alignment.clicked.connect(self.open_alignment_page)

        btn_terminal = QPushButton("Τερματικά Βέλη")
        btn_terminal.setMinimumHeight(60)
        btn_terminal.clicked.connect(self.open_terminal_page)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(btn_alignment)
        layout.addWidget(btn_terminal)
        layout.addStretch()

        return page

    def build_terminal_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        home_button = QPushButton("HOME")
        home_button.clicked.connect(self.go_home)

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

        return page

    def build_alignment_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)

        top_bar = QHBoxLayout()
        self.home_button = QPushButton("HOME")
        self.home_button.clicked.connect(self.go_home)

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
        self.solve_one_button.clicked.connect(self.solve_one_temperature_clicked)

        self.solve_all_button = QPushButton("Επίλυση όλων των θερμοκρασιών")
        self.solve_all_button.clicked.connect(self.solve_all_temperatures_clicked)

        self.export_button = QPushButton("Εξαγωγή αποτελεσμάτων σε XLSX")
        self.export_button.clicked.connect(self.export_current_results)
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

        return page

    ############### Navigation ################

    def go_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def open_alignment_page(self):
        self.stack.setCurrentWidget(self.alignment_page)

    def open_terminal_page(self):
        self.stack.setCurrentWidget(self.terminal_page)

    ############### Core GUI actions ################

    def read_inputs(self):
        spans = parse_series(self.spans_edit.toPlainText())
        heights = parse_series(self.heights_edit.toPlainText())

        if len(spans) != len(heights):
            raise ValueError("Τα ανοίγματα και οι υψομετρικές πρέπει να έχουν το ίδιο πλήθος τιμών.")
        if len(spans) == 0:
            raise ValueError("Χρειάζεται τουλάχιστον μία τιμή για ανοίγματα και υψομετρικές.")

        conductor = self.conductor_combo.currentText()
        temperature_C = float(self.temp_combo.currentText())

        return spans, heights, conductor, temperature_C

    def solve_one_temperature_clicked(self):
        try:
            spans, heights, conductor, temperature_C = self.read_inputs()

            result = solve_one_temperature(
                spans=spans,
                heights=heights,
                conductor_name=conductor,
                temperature_C=temperature_C,
            )

            df = build_one_temperature_dataframe(result)
            df_fmt = format_dataframe_for_export(df)
            df_fmt = translate_headers(df_fmt)

            self.current_display_df = df_fmt.copy()
            self.populate_table(df_fmt)
            self.export_button.setEnabled(True)

            ba_short = result["ba_label"].replace("BA ", "")
            self.summary_label.setText(
                f"BA: {ba_short} ({result['ruling_span_m']:.2f} m)"
            )

        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def solve_all_temperatures_clicked(self):
        try:
            spans, heights, conductor, _ = self.read_inputs()

            formatted_groups = []
            first_result = None

            for i, temp in enumerate(TEMPS):
                result = solve_one_temperature(
                    spans=spans,
                    heights=heights,
                    conductor_name=conductor,
                    temperature_C=float(temp),
                )

                if first_result is None:
                    first_result = result

                df = build_one_temperature_dataframe(result)
                df_fmt = format_dataframe_for_export(df)
                df_fmt = translate_headers(df_fmt)

                formatted_groups.append(df_fmt)

                if i < len(TEMPS) - 1:
                    formatted_groups.append(blank_row_df(df_fmt.columns))

            all_df_fmt = pd.concat(formatted_groups, ignore_index=True)

            self.current_display_df = all_df_fmt.copy()
            self.populate_table(all_df_fmt)
            self.export_button.setEnabled(True)

            ba_short = first_result["ba_label"].replace("BA ", "")
            self.summary_label.setText(
                f"BA: {ba_short} ({first_result['ruling_span_m']:.2f} m)"
            )

        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def export_current_results(self):
        try:
            if self.current_display_df is None or len(self.current_display_df) == 0:
                raise ValueError("Δεν υπάρχουν αποτελέσματα προς εξαγωγή.")

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save XLSX",
                "results.xlsx",
                "Excel Files (*.xlsx)",
            )

            if not file_path:
                return

            if not file_path.lower().endswith(".xlsx"):
                file_path += ".xlsx"

            self.current_display_df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Export", "Η εξαγωγή ολοκληρώθηκε επιτυχώς.")

        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    ############### Table handling ################

    def populate_table(self, df):
        self.table.clear()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in df.columns])

        for r in range(len(df)):
            for c in range(len(df.columns)):
                value = df.iat[r, c]
                self.table.setItem(r, c, QTableWidgetItem(str(value)))

        self.table.resizeColumnsToContents()