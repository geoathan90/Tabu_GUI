import numpy as np

from data import TEMPS, select_conductor_data
from formulas import ruling_span_info
from solvers import solve_horizontal_tensions_legacy


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
):
    """
    Solve one full case for one temperature.

    This is a small wrapper around the lower-level modules. Its job is to:

    1. convert the input spans and heights to NumPy arrays
    2. calculate the ruling span from the entered spans
    3. classify the ruling span as "BA 350" or "BA 500"
    4. select the conductor data for that BA class
    5. pick the correct reference tension T_ref for the requested temperature
    6. run the legacy horizontal-tension solver
    7. return all important results in one dictionary

    Parameters
    ----------
    spans : array-like of float
        Horizontal span lengths in meters.

    heights : array-like of float
        Height differences in meters.
        One height value is expected per span.

    conductor_name : str
        Conductor name as stored in data.CONDUCTORS.

    temperature_C : float or int
        Temperature to solve, in degrees Celsius.
        Must match one of the values in TEMPS.

    atol_m : float, default 0.001
        Absolute convergence tolerance on the total-length error, in meters.

    H_min : float, default 1e-6
        Minimum allowed first-span horizontal tension.

    H_max : float, default 4000.0
        Maximum allowed first-span horizontal tension.

    max_iters : int, default 50000
        Maximum number of outer legacy iterations.

    dt0 : float, default 99.0
        Initial legacy step size.

    Returns
    -------
    dict
        Dictionary containing the main results for one run.

        Returned keys:
        - "spans"
        - "heights"
        - "ruling_span_m"
        - "ba_label"
        - "temperature_C"
        - "conductor"
        - "T_ref"
        - "H_solution"
        - "info"

    Notes
    -----
    This function does not build tables or dataframes.
    It only assembles the inputs needed for one numerical solve and returns
    the numerical result plus useful metadata.

    Example
    -------
    >>> result = solve_one_temperature(
    ...     spans=[254.08, 385.0, 255.0, 485.0],
    ...     heights=[-57.13, -21.81, -5.28, 33.25],
    ...     conductor_name="Grosbeak",
    ...     temperature_C=20,
    ... )
    >>> result["ba_label"]
    'BA 500'
    >>> result["T_ref"]
    1953.0
    >>> result["H_solution"]
    array([...])

    Common usage
    ------------
    >>> result = solve_one_temperature(spans, heights, "Cardinal", 0)
    >>> H_solution = result["H_solution"]
    >>> info = result["info"]
    """
    spans_arr = np.asarray(spans, dtype=float)
    heights_arr = np.asarray(heights, dtype=float)

    if len(spans_arr) != len(heights_arr):
        raise ValueError("spans and heights must have the same length")
    
    if len(spans_arr) == 0:
        raise ValueError("spans and heights must contain at least one value")

    ruling_span_m, ba_label = ruling_span_info(spans_arr)
    conductor = select_conductor_data(conductor_name, ba_label)

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