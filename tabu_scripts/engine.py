import numpy as np

from tabu_scripts.data import TEMPS, select_conductor_data
from tabu_scripts.formulas import ruling_span_info
from tabu_scripts.solvers import solve_horizontal_tensions_legacy


def _build_conductor_from_raw_entry(conductor_name, ba_label, raw_entry):
    """
    Build the solver-ready conductor dictionary from a raw conductor entry.

    raw_entry is expected to contain:
    - w
    - A_cm2
    - E_kg_per_m2
    - T350
    - T500
    """
    required_fields = ["w", "A_cm2", "E_kg_per_m2", "T350", "T500"]
    missing = [field for field in required_fields if field not in raw_entry]
    if missing:
        raise ValueError(
            f"external_conductor_entry is missing required fields: {', '.join(missing)}"
        )

    if ba_label == "BA 350":
        Tvec = np.asarray(raw_entry["T350"], dtype=float)
    elif ba_label == "BA 500":
        Tvec = np.asarray(raw_entry["T500"], dtype=float)
    else:
        raise ValueError("ba_label must be 'BA 350' or 'BA 500'")

    if len(Tvec) != len(TEMPS):
        raise ValueError("The selected tension vector must have the same length as TEMPS.")

    return {
        "name": conductor_name,
        "ba_label": ba_label,
        "w": float(raw_entry["w"]),
        "A_cm2": float(raw_entry["A_cm2"]),
        "E_kg_per_m2": float(raw_entry["E_kg_per_m2"]),
        "Tvec": Tvec,
    }


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
    external_conductor_entry=None,
):
    """
    Solve one full case for one temperature.

    Two conductor-source modes are supported:

    1. Built-in mode
       If external_conductor_entry is None, the conductor is resolved from
       tabu_scripts.data through conductor_name and the automatically inferred
       BA label.

    2. External/session mode
       If external_conductor_entry is provided, it is used directly.
       In that case the supplied dictionary is expected to contain:
       - w
       - A_cm2
       - E_kg_per_m2
       - T350
       - T500
    """
    spans_arr = np.asarray(spans, dtype=float)
    heights_arr = np.asarray(heights, dtype=float)

    if len(spans_arr) != len(heights_arr):
        raise ValueError("spans and heights must have the same length")

    if len(spans_arr) == 0:
        raise ValueError("spans and heights must contain at least one value")

    ruling_span_m, ba_label = ruling_span_info(spans_arr)

    if external_conductor_entry is None:
        conductor = select_conductor_data(conductor_name, ba_label)
    else:
        conductor = _build_conductor_from_raw_entry(
            conductor_name=conductor_name,
            ba_label=ba_label,
            raw_entry=external_conductor_entry,
        )

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