from PySide6.QtCore import Qt
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

from gui.utils.conductor_catalog import conductor_names, get_raw_conductor_entry
from tabu_scripts.tensions import solve_for_H2_with_conductor, solve_for_H2_inclined_with_conductor


class TensionsPage(QWidget):
    def __init__(self, home_callback, app_state):
        super().__init__()

        self.app_state = app_state

        main_layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()

        self.home_button = QPushButton("HOME")
        self.home_button.clicked.connect(home_callback)

        page_title = QLabel("Επίλυση Καταστατικής Εξίσωσης")
        page_title.setStyleSheet("font-size: 22px; font-weight: bold;")

        top_bar.addWidget(self.home_button)
        top_bar.addSpacing(15)
        top_bar.addWidget(page_title)
        top_bar.addStretch()

        form_panel = QWidget()
        form_panel.setMaximumWidth(560)

        form_layout = QGridLayout(form_panel)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)

        self.conductor_combo = QComboBox()
        self.conductor_combo.setFixedWidth(220)
        self.conductor_combo.currentTextChanged.connect(self.update_default_weights)

        self.span_edit = QLineEdit()
        self.span_edit.setFixedWidth(180)

        self.dh_edit = QLineEdit()
        self.dh_edit.setFixedWidth(180)

        self.h1_edit = QLineEdit()
        self.h1_edit.setFixedWidth(180)

        self.t1_edit = QLineEdit()
        self.t1_edit.setFixedWidth(180)

        self.t2_edit = QLineEdit()
        self.t2_edit.setFixedWidth(180)

        self.w1_edit = QLineEdit()
        self.w1_edit.setFixedWidth(180)

        self.w2_edit = QLineEdit()
        self.w2_edit.setFixedWidth(180)

        self.solve_button = QPushButton("Επίλυση")
        self.solve_button.clicked.connect(self.solve_clicked)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-size: 15px; font-weight: bold;")

        form_layout.addWidget(QLabel("Τύπος Αγωγού"), 0, 0)
        form_layout.addWidget(self.conductor_combo, 0, 1)

        form_layout.addWidget(QLabel("Οριζόντιο Άνοιγμα S (m)"), 1, 0)
        form_layout.addWidget(self.span_edit, 1, 1)

        form_layout.addWidget(QLabel("Υψομετρική Διαφορά Δh (m)"), 2, 0)
        form_layout.addWidget(self.dh_edit, 2, 1)

        form_layout.addWidget(QLabel("Αρχική Οριζόντια Τάνυση Th1 (kg)"), 3, 0)
        form_layout.addWidget(self.h1_edit, 3, 1)

        form_layout.addWidget(QLabel("Αρχική Θερμοκρασία θ1 (°C)"), 4, 0)
        form_layout.addWidget(self.t1_edit, 4, 1)

        form_layout.addWidget(QLabel("Τελική Θερμοκρασία θ2 (°C)"), 5, 0)
        form_layout.addWidget(self.t2_edit, 5, 1)

        form_layout.addWidget(QLabel("Αρχικό Βάρος w1 (kg/m)"), 6, 0)
        form_layout.addWidget(self.w1_edit, 6, 1)

        form_layout.addWidget(QLabel("Αρχικό Βάρος w2 (kg/m)"), 7, 0)
        form_layout.addWidget(self.w2_edit, 7, 1)

        form_layout.addWidget(self.solve_button, 8, 0, 1, 2)
        form_layout.addWidget(self.result_label, 9, 0, 1, 2)

        main_layout.addLayout(top_bar)
        main_layout.addSpacing(15)
        main_layout.addWidget(form_panel, alignment=Qt.AlignTop | Qt.AlignHCenter)
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

        self.update_default_weights()

    def update_default_weights(self):
        """
        Refill w1 and w2 from the currently selected conductor.
        """
        conductor_name = self.conductor_combo.currentText()
        if not conductor_name:
            return

        raw_entry = get_raw_conductor_entry(
            self.app_state["conductors"],
            conductor_name,
        )

        w_default = float(raw_entry["w"])

        self.w1_edit.setText(f"{w_default}")
        self.w2_edit.setText(f"{w_default}")

    def solve_clicked(self):
        try:
            conductor_name = self.conductor_combo.currentText()
    
            S = float(self.span_edit.text().strip())
            dh = float(self.dh_edit.text().strip())
            H1 = float(self.h1_edit.text().strip())
            T1 = float(self.t1_edit.text().strip())
            T2 = float(self.t2_edit.text().strip())
            w1 = float(self.w1_edit.text().strip())
            w2 = float(self.w2_edit.text().strip())
    
            if abs(dh) < 0.01:
                H2 = solve_for_H2_with_conductor(
                    conductor_name=conductor_name,
                    S=S,
                    H1=H1,
                    T1=T1,
                    T2=T2,
                    w1=w1,
                    w2=w2,
                )
            else:
                H2 = solve_for_H2_inclined_with_conductor(
                    conductor_name=conductor_name,
                    S=S,
                    dh=dh,
                    H1=H1,
                    T1=T1,
                    T2=T2,
                    w1=w1,
                    w2=w2,
                )
    
            self.result_label.setText(f"Th2 = {H2:.3f} kg")
    
        except Exception as ex:
            QMessageBox.critical(self, "Error", str(ex))
