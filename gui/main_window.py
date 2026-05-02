import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QTextEdit, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QMessageBox
)

from data import TEMPS, available_conductors
from engine import solve_one_temperature
from output import build_one_temperature_dataframe, format_dataframe_for_export


def parse_series(raw_text):
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tabu GUI Experiment")
        self.resize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        left_panel = QWidget()
        left_layout = QGridLayout(left_panel)

        self.spans_edit = QTextEdit()
        self.heights_edit = QTextEdit()

        self.conductor_combo = QComboBox()
        self.conductor_combo.addItems(available_conductors())

        self.temp_combo = QComboBox()
        for t in TEMPS:
            self.temp_combo.addItem(str(int(t)))

        self.solve_button = QPushButton("Solve one temperature")
        self.solve_button.clicked.connect(self.solve_case)

        self.status_label = QLabel("Ready.")

        left_layout.addWidget(QLabel("Spans (m)"), 0, 0)
        left_layout.addWidget(self.spans_edit, 1, 0)

        left_layout.addWidget(QLabel("Height differences (m)"), 2, 0)
        left_layout.addWidget(self.heights_edit, 3, 0)

        left_layout.addWidget(QLabel("Conductor"), 4, 0)
        left_layout.addWidget(self.conductor_combo, 5, 0)

        left_layout.addWidget(QLabel("Temperature (°C)"), 6, 0)
        left_layout.addWidget(self.temp_combo, 7, 0)

        left_layout.addWidget(self.solve_button, 8, 0)
        left_layout.addWidget(self.status_label, 9, 0)

        self.table = QTableWidget()

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(self.table, 2)

    def solve_case(self):
        try:
            spans = parse_series(self.spans_edit.toPlainText())
            heights = parse_series(self.heights_edit.toPlainText())

            if len(spans) != len(heights):
                raise ValueError("spans and heights must have the same length")
            if len(spans) == 0:
                raise ValueError("Please enter at least one span and one height value")

            conductor = self.conductor_combo.currentText()
            temperature_C = float(self.temp_combo.currentText())

            result = solve_one_temperature(
                spans=spans,
                heights=heights,
                conductor_name=conductor,
                temperature_C=temperature_C,
            )

            df = build_one_temperature_dataframe(result)
            df = format_dataframe_for_export(df)

            self.populate_table(df)

            info = result["info"]
            self.status_label.setText(
                f"BA: {result['ba_label']} | "
                f"T_ref: {result['T_ref']:.2f} | "
                f"iters: {info.get('iterations', '?')} | "
                f"error: {info.get('error', float('nan')):.6f} m"
            )

        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

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