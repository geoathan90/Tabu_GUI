from copy import deepcopy
import numpy as np

from tabu_scripts.data import CONDUCTORS


def create_session_catalog():
    """
    Create a session-local conductor catalog.

    The returned dictionary starts as a deep copy of the built-in conductors
    and can be extended during runtime without modifying tabu_scripts.data.
    """
    return deepcopy(CONDUCTORS)


def conductor_names(catalog):
    """
    Return sorted conductor names from the given session catalog.
    """
    return sorted(catalog.keys())


def get_raw_conductor_entry(catalog, conductor_name):
    """
    Return one raw conductor entry from the session catalog.

    The returned entry is expected to have:
    - w
    - A_cm2
    - E_kg_per_m2
    - T350
    - T500
    """
    if conductor_name not in catalog:
        raise ValueError(f"Ο αγωγός '{conductor_name}' δεν βρέθηκε στον τρέχοντα κατάλογο.")

    return catalog[conductor_name]


def normalize_conductor_entry(entry):
    """
    Normalize one conductor entry to the same shape as the built-in catalog.
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
        Session-local conductor catalog.

    conductor_name : str
        Name of the conductor.

    conductor_entry : dict
        Raw conductor entry with keys:
        - w
        - A_cm2
        - E_kg_per_m2
        - T350
        - T500

    overwrite : bool, default False
        If False, an error is raised when the conductor name already exists.
    """
    if conductor_name in catalog and not overwrite:
        raise ValueError(f"Ο αγωγός '{conductor_name}' έχει φορτωθεί ήδη.")

    clean_entry = normalize_conductor_entry(conductor_entry)
    catalog[conductor_name] = clean_entry
    return clean_entry