import numpy as np


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