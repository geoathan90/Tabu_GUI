"""
output.py
=========

Small output module for turning raw solver results into pandas DataFrames.

Purpose
-------
The numerical modules return plain dictionaries and NumPy arrays.
This file is responsible only for presentation/output work.

At the moment, the main function here is:

- build_one_temperature_dataframe(result)

It expects the dictionary returned by engine.solve_one_temperature(...).

Typical usage
-------------
>>> from engine import solve_one_temperature
>>> from output import build_one_temperature_dataframe
>>>
>>> result = solve_one_temperature(
...     spans=[254.08, 385.0, 255.0, 485.0],
...     heights=[-57.13, -21.81, -5.28, 33.25],
...     conductor_name="Grosbeak",
...     temperature_C=20,
... )
>>> df = build_one_temperature_dataframe(result)
>>> df.head()
"""

import numpy as np
import pandas as pd

from formulas import increase, sags, tension_correction_terms


def build_one_temperature_dataframe(result):
    """
    Build a pandas DataFrame for one solved temperature case.

    Parameters
    ----------
    result : dict
        Dictionary returned by engine.solve_one_temperature(...).

        Expected keys:
        - "spans"
        - "heights"
        - "temperature_C"
        - "T_ref"
        - "H_solution"
        - "conductor"

        The "conductor" entry is expected to contain:
        - "w"
        - "A_cm2"
        - "E_kg_per_m2"

    Returns
    -------
    pandas.DataFrame
        Table with one row per span.

        Columns:
        - "temperature_C"
        - "span_m"
        - "height_m"
        - "T_ref_kg"
        - "H_solution_kg"
        - "sag_eq_m"
        - "sag_alt_m"
        - "diorthosi_geometric_m"
        - "diorthosi_elastic_m"
        - "diorthosi_combined_m"

    Notes
    -----
    The correction columns are cumulative, matching the legacy-style output
    philosophy already used in the previous codebase.

    Example
    -------
    >>> df = build_one_temperature_dataframe(result)
    >>> df.columns.tolist()
    ['temperature_C', 'span_m', 'height_m', 'T_ref_kg', 'H_solution_kg',
     'sag_eq_m', 'sag_alt_m', 'diorthosi_geometric_m',
     'diorthosi_elastic_m', 'diorthosi_combined_m']
    """
    spans = np.asarray(result["spans"], dtype=float)
    heights = np.asarray(result["heights"], dtype=float)
    temperature_C = float(result["temperature_C"])
    T_ref = float(result["T_ref"])
    H_solution = np.asarray(result["H_solution"], dtype=float)

    conductor = result["conductor"]
    w = float(conductor["w"])
    area_cm2 = float(conductor["A_cm2"])
    E_kg_per_m2 = float(conductor["E_kg_per_m2"])

    n = len(spans)
    T_ref_arr = np.full(n, T_ref, dtype=float)

    inc = increase(spans, heights)

    corr = tension_correction_terms(
        spans=spans,
        heights=heights,
        T_ref=T_ref,
        H_solution=H_solution,
        w=w,
        area_cm2=area_cm2,
        E_kg_per_m2=E_kg_per_m2,
    )

    df = pd.DataFrame({
        "temperature_C": np.full(n, temperature_C, dtype=float),
        "span_m": spans,
        "height_m": heights,
        "T_ref_kg": T_ref_arr,
        "H_solution_kg": H_solution,
        "sag_eq_m": inc * sags(spans, T_ref_arr, w),
        "sag_alt_m": inc * sags(spans, H_solution, w),
        "diorthosi_geometric_m": corr["geometric_cum_m"],
        "diorthosi_elastic_m": corr["elastic_cum_m"],
        "diorthosi_combined_m": corr["combined_cum_m"],
    })

    return df


def format_dataframe_for_export(df):
    """
    Return a formatted copy of the results DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw DataFrame produced by build_one_temperature_dataframe().

    Returns
    -------
    pandas.DataFrame
        Copy with simple rounding/formatting applied.

    Notes
    -----
    This function is optional.
    It is useful for CSV/XLSX export or GUI display, but the raw numerical
    DataFrame can also be used directly.
    """
    df_out = df.copy()

    if "temperature_C" in df_out:
        df_out["temperature_C"] = np.rint(df_out["temperature_C"]).astype(int)

    if "T_ref_kg" in df_out:
        df_out["T_ref_kg"] = np.rint(df_out["T_ref_kg"]).astype(int)

    for col in ["H_solution_kg", "sag_eq_m", "sag_alt_m"]:
        if col in df_out:
            df_out[col] = df_out[col].round(2)

    for col in [
        "diorthosi_geometric_m",
        "diorthosi_elastic_m",
        "diorthosi_combined_m",
    ]:
        if col in df_out:
            df_out[col] = df_out[col].round(3)

    return df_out