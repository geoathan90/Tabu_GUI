import pandas as pd

from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QMessageBox,
    QFileDialog,
)

from tabu_scripts.engine import solve_one_temperature
from tabu_scripts.output import build_one_temperature_dataframe, format_dataframe_for_export

from gui.pages.home_page import HomePage
from gui.pages.suspension_page import SuspensionPage
from gui.pages.terminal_page import TerminalPage
from gui.utils.table_helpers import translate_headers, blank_row_df


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tabu GUI")
        self.resize(1350, 800)

        self.current_display_df = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = HomePage(
            open_suspension_callback=self.open_suspension_page,
            open_terminal_callback=self.open_terminal_page,
        )

        self.suspension_page = SuspensionPage(
            home_callback=self.go_home,
            solve_one_callback=self.solve_one_temperature_clicked,
            solve_all_callback=self.solve_all_temperatures_clicked,
            export_callback=self.export_current_results,
        )

        self.terminal_page = TerminalPage(home_callback=self.go_home)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.suspension_page)
        self.stack.addWidget(self.terminal_page)

        self.stack.setCurrentWidget(self.home_page)

    ################ Navigation ################

    def go_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def open_suspension_page(self):
        self.stack.setCurrentWidget(self.suspension_page)

    def open_terminal_page(self):
        self.stack.setCurrentWidget(self.terminal_page)

    ################ Module actions ################

    def solve_one_temperature_clicked(self):
        try:
            spans, heights, conductor, temperature_C = self.suspension_page.get_inputs()

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
            self.suspension_page.show_dataframe(df_fmt)
            self.suspension_page.set_export_enabled(True)

            ba_short = result["ba_label"].replace("BA ", "")
            self.suspension_page.set_summary_text(
                f"BA: {ba_short} ({result['ruling_span_m']:.2f} m)"
            )

        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def solve_all_temperatures_clicked(self):
        try:
            spans, heights, conductor, _ = self.suspension_page.get_inputs()

            formatted_groups = []
            first_result = None

            from data import TEMPS

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
            self.suspension_page.show_dataframe(all_df_fmt)
            self.suspension_page.set_export_enabled(True)

            ba_short = first_result["ba_label"].replace("BA ", "")
            self.suspension_page.set_summary_text(
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