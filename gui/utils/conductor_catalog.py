from copy import deepcopy
import numpy as np

from tabu_scripts.data import CONDUCTORS


def create_session_catalog():
    """
    Create a session-local conductor catalog.

    The returned dictionary starts as a deep copy of the built-in conductors
    from tabu_scripts.data.CONDUCTORS and can then be extended during runtime
    without modifying the built-in source data.
    """
    return deepcopy(CONDUCTORS)


def conductor_names(catalog):
    """
    Return sorted conductor names from the given session catalog.
    """
    return sorted(catalog.keys())


def normalize_conductor_entry(entry):
    """
    Normalize one conductor entry to the same basic structure used by the
    built-in catalog.

    Expected keys:
    - w
    - A_cm2
    - E_kg_per_m2
    - T350
    - T500
    """
    return {
        "w": float(entry["w"]),
        "A_cm2": float(entry["A_cm2"]),
        "E_kg_per_m2": float(entry["E_kg_per_m2"]),
        "T350": np.asarray(entry["T350"], dtype=float),
        "T500": np.asarray(entry["T500"], dtype=float),
    }


def add_conductor_to_catalog(catalog, conductor_name, conductor_entry, overwrite=False):
    """
    Insert one conductor into the session catalog.

    Parameters
    ----------
    catalog : dict
        The session-local conductor catalog.

    conductor_name : str
        Name of the conductor.

    conductor_entry : dict
        Dictionary with the conductor fields:
        w, A_cm2, E_kg_per_m2, T350, T500

    overwrite : bool, default False
        If False, an error is raised when the name already exists.

    Returns
    -------
    dict
        The normalized conductor entry that was inserted.
    """
    if conductor_name in catalog and not overwrite:
        raise ValueError(f"Ο αγωγός '{conductor_name}' υπάρχει ήδη στην τρέχουσα συνεδρία.")

    clean_entry = normalize_conductor_entry(conductor_entry)
    catalog[conductor_name] = clean_entry
    return clean_entry


def resolve_conductor_data(catalog, conductor_name, ba_label):
    """
    Resolve one conductor from the session catalog and return the same kind of
    dictionary that the solver currently expects.

    Returned keys:
    - name
    - ba_label
    - w
    - A_cm2
    - E_kg_per_m2
    - Tvec
    """
    if conductor_name not in catalog:
        raise ValueError(f"Ο αγωγός '{conductor_name}' δεν βρέθηκε στον τρέχοντα κατάλογο.")

    data = catalog[conductor_name]

    if ba_label == "BA 350":
        Tvec = np.asarray(data["T350"], dtype=float)
    elif ba_label == "BA 500":
        Tvec = np.asarray(data["T500"], dtype=float)
    else:
        raise ValueError("ba_label must be 'BA 350' or 'BA 500'")

    return {
        "name": conductor_name,
        "ba_label": ba_label,
        "w": float(data["w"]),
        "A_cm2": float(data["A_cm2"]),
        "E_kg_per_m2": float(data["E_kg_per_m2"]),
        "Tvec": Tvec,
    }