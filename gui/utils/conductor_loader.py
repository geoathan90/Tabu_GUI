import ast
import re
import numpy as np


NP_ARRAY_PATTERN = re.compile(
    r"np\.array\s*\(\s*(\[[\s\S]*?\])\s*\)",
    flags=re.MULTILINE,
)


def _strip_comments(text):
    """
    Remove simple trailing # comments line by line.
    """
    cleaned_lines = []
    for line in text.splitlines():
        if "#" in line:
            line = line.split("#", 1)[0]
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def _extract_mapping_text(raw_text):
    """
    Accept either:
    - a plain dictionary text
    - or text starting with: CONDUCTORS = { ... }

    Also converts np.array([...]) into plain list syntax so that
    ast.literal_eval can parse the result safely.
    """
    text = raw_text.strip()
    text = _strip_comments(text)

    if text.startswith("CONDUCTORS"):
        eq_pos = text.find("=")
        if eq_pos == -1:
            raise ValueError("Το αρχείο περιέχει 'CONDUCTORS' αλλά δεν βρέθηκε '='.")
        text = text[eq_pos + 1:].strip()

    text = NP_ARRAY_PATTERN.sub(r"\1", text)
    return text


def _validate_numeric_scalar(value, field_name):
    try:
        return float(value)
    except Exception:
        raise ValueError(f"Το πεδίο '{field_name}' πρέπει να είναι αριθμός.")


def _validate_tension_vector(values, field_name):
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"Το πεδίο '{field_name}' πρέπει να είναι λίστα 5 αριθμών.")

    if len(values) != 5:
        raise ValueError(f"Το πεδίο '{field_name}' πρέπει να έχει ακριβώς 5 τιμές.")

    cleaned = []
    for i, value in enumerate(values):
        try:
            cleaned.append(float(value))
        except Exception:
            raise ValueError(f"Το πεδίο '{field_name}' περιέχει μη αριθμητική τιμή στη θέση {i}.")

    return np.asarray(cleaned, dtype=float)


def parse_conductor_text(raw_text):
    """
    Parse one conductor-definition text safely.

    Expected accepted shape:
        CONDUCTORS = {
            "Name": {
                "w": ...,
                "A_cm2": ...,
                "E_kg_per_m2": ...,
                "T350": np.array([...]),
                "T500": np.array([...]),
            },
        }

    Safe parsing rules:
    - no eval
    - no exec
    - np.array([...]) is rewritten to [...]
    - ast.literal_eval is used on the remaining text

    Returns
    -------
    tuple
        (conductor_name, conductor_entry_dict)
    """
    text = _extract_mapping_text(raw_text)

    try:
        obj = ast.literal_eval(text)
    except Exception as ex:
        raise ValueError(f"Αποτυχία ανάγνωσης του αρχείου αγωγού: {ex}")

    if not isinstance(obj, dict):
        raise ValueError("Το αρχείο πρέπει να περιέχει dictionary στην κορυφή.")

    if len(obj) != 1:
        raise ValueError("Το αρχείο πρέπει να περιέχει ακριβώς έναν αγωγό.")

    conductor_name, entry = next(iter(obj.items()))

    if not isinstance(conductor_name, str) or not conductor_name.strip():
        raise ValueError("Το όνομα του αγωγού πρέπει να είναι μη κενό string.")

    if not isinstance(entry, dict):
        raise ValueError("Τα δεδομένα του αγωγού πρέπει να είναι dictionary.")

    required_fields = ["w", "A_cm2", "E_kg_per_m2", "alpha", "T350", "T500"]
    missing = [field for field in required_fields if field not in entry]
    if missing:
        raise ValueError(f"Λείπουν τα εξής πεδία: {', '.join(missing)}")

    clean_entry = {
        "w": _validate_numeric_scalar(entry["w"], "w"),
        "A_cm2": _validate_numeric_scalar(entry["A_cm2"], "A_cm2"),
        "E_kg_per_m2": _validate_numeric_scalar(entry["E_kg_per_m2"], "E_kg_per_m2"),
        "alpha": _validate_numeric_scalar(entry["alpha"], "alpha"),
        "T350": _validate_tension_vector(entry["T350"], "T350"),
        "T500": _validate_tension_vector(entry["T500"], "T500"),
    }

    if clean_entry["w"] <= 0:
        raise ValueError("Το w πρέπει να είναι θετικό.")
    if clean_entry["A_cm2"] <= 0:
        raise ValueError("Το A_cm2 πρέπει να είναι θετικό.")
    if clean_entry["E_kg_per_m2"] <= 0:
        raise ValueError("Το E_kg_per_m2 πρέπει να είναι θετικό.")
    if clean_entry["alpha"] <= 0:
        raise ValueError("Το alpha πρέπει να είναι θετικό.")

    return conductor_name.strip(), clean_entry


def load_conductor_file(file_path):
    """
    Read and parse one conductor file from disk.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    return parse_conductor_text(raw_text)
