import pandas as pd
from PySide6.QtWidgets import QTableWidgetItem


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


def populate_table_widget(table, df):
    """
    Fill a QTableWidget from a pandas DataFrame.
    """
    table.clear()
    table.setRowCount(len(df))
    table.setColumnCount(len(df.columns))
    table.setHorizontalHeaderLabels([str(c) for c in df.columns])

    for r in range(len(df)):
        for c in range(len(df.columns)):
            value = df.iat[r, c]
            table.setItem(r, c, QTableWidgetItem(str(value)))

    table.resizeColumnsToContents()