import pandas as pd

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
    QMessageBox,
    QFileDialog,
)

from tabu_scripts.data import TEMPS
from tabu_scripts.engine import solve_one_temperature
from tabu_scripts.output import (
    build_one_temperature_dataframe,
    format_dataframe_for_export,
)

from gui.utils.parsing import parse_series
from gui.utils.table_helpers import (
    populate_table_widget,
    translate_headers,
    blank_row_df,
)
from gui.utils.conductor_catalog import (
    conductor_names,
    get_raw_conductor_entry,
    add_conductor_to_catalog,
)
from gui.utils.conductor_loader import load_conductor_file


class SuspensionPage(QWidget):
    def __init__(self, home_callback, app_state):
        super().__init__()

        self.app_state = app_state
        self.current_display_df = None

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

        self.load_conductor_button = QPushButton("Φόρτωση Νέου Αγωγού")
        self.load_conductor_button.clicked.connect(self.load_new_conductor_data)

        conductor_row = QWidget()
        conductor_row_layout = QHBoxLayout(conductor_row)
        conductor_row_layout.setContentsMargins(0, 0, 0, 0)
        conductor_row_layout.addWidget(self.conductor_combo, 1)
        conductor_row_layout.addWidget(self.load_conductor_button)

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
        left_layout.addWidget(conductor_row, 6, 0)

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

        self.refresh_conductor_dropdown()

    def refresh_conductor_dropdown(self, select_name=None):
        current_name = select_name
        if current_name is None:
            current_name = self.conductor_combo.currentText()

        names = conductor_names(self.app_state["conductors"])

        self.conductor_combo.clear()
        self.conductor_combo.addItems(names)

        if current_name in names:
            self.conductor_combo.setCurrentText(current_name)

    def get_inputs(self):
        spans = parse_series(self.spans_edit.toPlainText())
        heights = parse_series(self.heights_edit.toPlainText())

        if len(spans) != len(heights):
            raise ValueError("Τα ανοίγματα και οι υψομετρικές πρέπει να έχουν το ίδιο πλήθος τιμών.")
        if len(spans) == 0 or len(spans) == 1:
            raise ValueError("Χρειάζονται τουλάχιστον δύο τιμές για ανοίγματα και υψομετρικές.")

        conductor = self.conductor_combo.currentText()
        temperature_C = float(self.temp_combo.currentText())

        return spans, heights, conductor, temperature_C

    def set_summary_text(self, text):
        self.summary_label.setText(text)

    def set_export_enabled(self, enabled):
        self.export_button.setEnabled(enabled)

    def show_dataframe(self, df):
        populate_table_widget(self.table, df)

    def load_new_conductor_data(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Conductor Data",
                "",
                "Text Files (*.txt);;All Files (*)",
            )

            if not file_path:
                return

            conductor_name, conductor_entry = load_conductor_file(file_path)

            add_conductor_to_catalog(
                self.app_state["conductors"],
                conductor_name,
                conductor_entry,
                overwrite=False,
            )

            self.refresh_conductor_dropdown(select_name=conductor_name)

            QMessageBox.information(
                self,
                "Success",
                f"Ο αγωγός '{conductor_name}' φορτώθηκε επιτυχώς.",
            )

        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def solve_one_temperature_clicked(self):
        try:
            spans, heights, conductor_name, temperature_C = self.get_inputs()

            raw_entry = get_raw_conductor_entry(
                self.app_state["conductors"],
                conductor_name,
            )

            result = solve_one_temperature(
                spans=spans,
                heights=heights,
                conductor_name=conductor_name,
                temperature_C=temperature_C,
                external_conductor_entry=raw_entry,
            )

            df = build_one_temperature_dataframe(result)
            df_fmt = format_dataframe_for_export(df)
            df_fmt = translate_headers(df_fmt)

            self.current_display_df = df_fmt.copy()
            self.show_dataframe(df_fmt)
            self.set_export_enabled(True)

            ba_short = result["ba_label"].replace("BA ", "")
            self.set_summary_text(
                f"BA: {ba_short} ({result['ruling_span_m']:.2f} m)"
            )

        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def solve_all_temperatures_clicked(self):
        try:
            spans, heights, conductor_name, _ = self.get_inputs()

            raw_entry = get_raw_conductor_entry(
                self.app_state["conductors"],
                conductor_name,
            )

            formatted_groups = []
            first_result = None

            for i, temp in enumerate(TEMPS):
                result = solve_one_temperature(
                    spans=spans,
                    heights=heights,
                    conductor_name=conductor_name,
                    temperature_C=float(temp),
                    external_conductor_entry=raw_entry,
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
            self.show_dataframe(all_df_fmt)
            self.set_export_enabled(True)

            ba_short = first_result["ba_label"].replace("BA ", "")
            self.set_summary_text(
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