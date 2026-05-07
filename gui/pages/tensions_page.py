from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QMessageBox,
)

from gui.utils.conductor_catalog import conductor_names
from tabu_scripts.tensions import solve_for_H2_with_conductor


class TensionsPage(QWidget):
    def __init__(self, home_callback, app_state):
        super().__init__()

        self.app_state = app_state

        main_layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()

        self.home_button = QPushButton("HOME")
        self.home_button.clicked.connect(home_callback)

        page_title = QLabel("Επίλυση Τριτοβάθμιας")
        page_title.setStyleSheet("font-size: 22px; font-weight: bold;")

        top_bar.addWidget(self.home_button)
        top_bar.addSpacing(15)
        top_bar.addWidget(page_title)
        top_bar.addStretch()

        form_panel = QWidget()
        form_layout = QGridLayout(form_panel)

        self.conductor_combo = QComboBox()

        self.span_edit = QLineEdit()
        self.h1_edit = QLineEdit()
        self.t1_edit = QLineEdit()
        self.t2_edit = QLineEdit()

        self.solve_button = QPushButton("Επίλυση")
        self.solve_button.clicked.connect(self.solve_clicked)

        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-size: 15px; font-weight: bold;")

        form_layout.addWidget(QLabel("Τύπος Αγωγού"), 0, 0)
        form_layout.addWidget(self.conductor_combo, 0, 1)

        form_layout.addWidget(QLabel("Άνοιγμα S (m)"), 1, 0)
        form_layout.addWidget(self.span_edit, 1, 1)

        form_layout.addWidget(QLabel("Αρχική Οριζόντια Τάνυση H1"), 2, 0)
        form_layout.addWidget(self.h1_edit, 2, 1)

        form_layout.addWidget(QLabel("Αρχική Θερμοκρασία T1 (°C)"), 3, 0)
        form_layout.addWidget(self.t1_edit, 3, 1)

        form_layout.addWidget(QLabel("Τελική Θερμοκρασία T2 (°C)"), 4, 0)
        form_layout.addWidget(self.t2_edit, 4, 1)

        form_layout.addWidget(self.solve_button, 5, 0, 1, 2)
        form_layout.addWidget(self.result_label, 6, 0, 1, 2)

        main_layout.addLayout(top_bar)
        main_layout.addSpacing(15)
        main_layout.addWidget(form_panel)
        main_layout.addStretch()

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

    def solve_clicked(self):
        try:
            conductor_name = self.conductor_combo.currentText()
            S = float(self.span_edit.text().strip())
            H1 = float(self.h1_edit.text().strip())
            T1 = float(self.t1_edit.text().strip())
            T2 = float(self.t2_edit.text().strip())

            H2 = solve_for_H2_with_conductor(
                conductor_name=conductor_name,
                S=S,
                H1=H1,
                T1=T1,
                T2=T2,
            )

            self.result_label.setText(f"H2 = {H2:.3f}")

        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))