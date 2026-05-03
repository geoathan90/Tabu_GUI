import numpy as np

from tabu_scripts.data import TEMPS, select_conductor_data
from tabu_scripts.formulas import ruling_span_info
from tabu_scripts.solvers import solve_horizontal_tensions_legacy


def solve_one_temperature(
    spans,
    heights,
    conductor_name,
    temperature_C,
    atol_m=0.001,
    H_min=1e-6,
    H_max=4000.0,
    max_iters=50000,
    dt0=99.0,
    conductor_data=None,
):
    """
    Solve one full case for one temperature.

    Two conductor-source modes are supported:

    1. Built-in mode
       If conductor_data is None, the conductor is resolved from
       tabu_scripts.data through conductor_name and the automatically inferred
       BA label.

    2. External/session mode
       If conductor_data is provided, it is used directly.
       In that case the supplied dictionary is expected to already contain the
       correct Tvec for the currently inferred BA label.

    Parameters
    ----------
    spans : array-like of float
        Horizontal span lengths in meters.

    heights : array-like of float
        Height differences in meters.

    conductor_name : str
        Conductor name. Still useful for metadata even when conductor_data is
        supplied.

    temperature_C : float or int
        Temperature to solve, in degrees Celsius.
        Must match one of the values in TEMPS.

    conductor_data : dict or None, default None
        Optional pre-resolved conductor dictionary with keys:
        - w
        - A_cm2
        - E_kg_per_m2
        - Tvec

        This path is intended for session-loaded external conductors.

    Returns
    -------
    dict
        Dictionary containing the main results for one run.
    """
    spans_arr = np.asarray(spans, dtype=float)
    heights_arr = np.asarray(heights, dtype=float)

    if len(spans_arr) != len(heights_arr):
        raise ValueError("spans and heights must have the same length")

    if len(spans_arr) == 0:
        raise ValueError("spans and heights must contain at least one value")

    ruling_span_m, ba_label = ruling_span_info(spans_arr)

    if conductor_data is None:
        conductor = select_conductor_data(conductor_name, ba_label)
    else:
        if not isinstance(conductor_data, dict):
            raise ValueError("conductor_data must be a dictionary when provided.")

        required_fields = ["w", "A_cm2", "E_kg_per_m2", "Tvec"]
        missing = [field for field in required_fields if field not in conductor_data]
        if missing:
            raise ValueError(
                f"conductor_data is missing required fields: {', '.join(missing)}"
            )

        Tvec = np.asarray(conductor_data["Tvec"], dtype=float)
        if len(Tvec) != len(TEMPS):
            raise ValueError("conductor_data['Tvec'] must have the same length as TEMPS.")

        conductor = {
            "name": conductor_name,
            "ba_label": ba_label,
            "w": float(conductor_data["w"]),
            "A_cm2": float(conductor_data["A_cm2"]),
            "E_kg_per_m2": float(conductor_data["E_kg_per_m2"]),
            "Tvec": Tvec,
        }

    temp_matches = np.where(TEMPS == float(temperature_C))[0]
    if len(temp_matches) == 0:
        raise ValueError(f"temperature_C must be one of {TEMPS.tolist()}")

    temp_index = int(temp_matches[0])
    T_ref = float(conductor["Tvec"][temp_index])

    H_solution, info = solve_horizontal_tensions_legacy(
        spans=spans_arr,
        heights=heights_arr,
        T_ref=T_ref,
        w=conductor["w"],
        atol_m=atol_m,
        H_min=H_min,
        H_max=H_max,
        max_iters=max_iters,
        dt0=dt0,
    )

    return {
        "spans": spans_arr,
        "heights": heights_arr,
        "ruling_span_m": float(ruling_span_m),
        "ba_label": ba_label,
        "temperature_C": float(TEMPS[temp_index]),
        "conductor": conductor,
        "T_ref": T_ref,
        "H_solution": H_solution,
        "info": info,
    }