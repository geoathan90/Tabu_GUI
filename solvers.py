"""
solvers.py
==========

Small solver helper module.

At the moment this file contains only one function:

- ``total_length_error``

Purpose
-------
The outer solving methods do not solve every span tension directly.
Instead, they:

1. assume a first-span horizontal tension ``H0``
2. run the forward sweep to propagate tensions through all spans
3. calculate the total conductor length that results
4. compare that total length against a target total length

The difference between those two totals is the quantity that the outer solver
tries to drive to zero.

Typical usage
-------------
>>> import numpy as np
>>> from solvers import total_length_error
>>>
>>> spans = np.array([254.08, 385.0, 255.0, 485.0])
>>> heights = np.array([-57.13, -21.81, -5.28, 33.25])
>>> H0 = 2026.0
>>> w = 1.303
>>> target_total_length = 1387.5
>>>
>>> error_m, H_solution = total_length_error(
...     spans=spans,
...     heights=heights,
...     H0=H0,
...     w=w,
...     target_total_length=target_total_length,
... )
>>> H_solution
array([...])
"""

import numpy as np

from formulas import total_length
from forward_sweep import forward_sweep_from_H0

def total_length_error(spans, heights, H0, w, target_total_length):
    """
    Run one forward sweep and compare the resulting total conductor length
    against a target total length.

    Parameters
    ----------
    spans : array-like of float
        Horizontal span lengths in meters.

    heights : array-like of float
        Height differences in meters.

    H0 : float
        Assumed horizontal tension in the first span.

    w : float
        Conductor weight per unit length in kg/m.

    target_total_length : float
        Target total conductor length for the whole section, in meters.
        In the larger solver workflow, this target is the total length
        produced by one constant reference tension ``T_ref`` applied to all spans.

    Returns
    -------
    tuple
        Two values are returned:

        error_m : float
            Difference between the calculated total length and the target total
            length:

                error = total_length(H_solution) - target_total_length

        H_solution : numpy.ndarray
            Horizontal tensions obtained from the forward sweep, one value per
            span.

    Notes
    -----
    This function is the bridge between the forward sweep and the outer solver.

    The forward sweep itself does not know whether the guessed ``H0`` is good or
    bad. It simply propagates tensions span by span and returns the resulting
    tension state.

    This function takes that propagated tension state, calculates the total
    conductor length that it implies, and compares that total against the target.
    That comparison is what the outer solver uses to decide whether the next
    guess for ``H0`` should be larger or smaller.

    Formula used
    ------------
    The returned error is:

        error = total_length(spans, heights, H_solution, w) - target_total_length

    So the sign convention is the same one used in the earlier codebase:

    - if the current total length is greater than the target, error is positive
        -> the outer solver then increases tension, which reduces total length
    - if the current total length is smaller than the target, error is negative
        -> the outer solver then reduces tension, which increases total length

    Example
    -------
    >>> import numpy as np
    >>> spans = np.array([230.0, 250.0, 410.0, 220.0])
    >>> heights = np.array([5.0, -3.0, 8.0, 0.0])
    >>> error_m, H_solution = total_length_error(
    ...     spans=spans,
    ...     heights=heights,
    ...     H0=2026.0,
    ...     w=1.303,
    ...     target_total_length=1115.0,
    ... )
    >>> error_m
    ...
    >>> H_solution
    array([...])

    Common usage in an outer solver
    -------------------------------
    >>> # 1) choose a trial H0
    >>> # 2) run the error function
    >>> error_m, H_solution = total_length_error(
    ...     spans, heights, H0_guess, w, target_total_length
    ... )
    >>> # 3) if error_m > 0, the current solution is too long
    >>> # 4) if error_m < 0, the current solution is too short
    """
    
    out = forward_sweep_from_H0(spans, heights, H0, w)
    H_solution = out["H"]

    total_len = total_length(spans, heights, H_solution, w)
    error_m = total_len - target_total_length

    return error_m, H_solution



def solve_horizontal_tensions_legacy(
    spans,
    heights,
    T_ref,
    w,
    atol_m=0.001,
    H_min=1e-6,
    H_max=4000.0,
    max_iters=50000,
    dt0=99.0,
):
    """
    Legacy-style outer solve on the first horizontal tension H0.

    Philosophy
    ----------
    This solver does not use bracketing, bisection, or derivatives.

    Instead, it follows the older step-halving approach:

    1. Start from H0 = T_ref
    2. Compute the total-length error
    3. If the solved section is too short, decrease H0
    4. If the solved section is too long, increase H0
    5. Whenever the direction flips, halve the step size dt
    6. Stop when abs(error) <= atol_m

    This is intended to reproduce the convergence path of the older legacy code
    as closely as possible.

    Parameters
    ----------
    spans : array-like of float
        Horizontal span lengths in meters.

    heights : array-like of float
        Height differences in meters.

    T_ref : float
        Reference tension used to define the target total conductor length.

    w : float
        Conductor weight per unit length in kg/m.

    atol_m : float, default 0.001
        Absolute tolerance on the total-length error, in meters.

    H_min : float, default 1e-6
        Lower bound for H0.

    H_max : float, default 4000.0
        Upper bound for H0.

    max_iters : int, default 50000
        Maximum number of outer iterations.

    dt0 : float, default 99.0
        Initial legacy step size.

    Returns
    -------
    tuple
        H_solution : numpy.ndarray
            Solved horizontal tensions, one per span.

        info : dict
            Dictionary with summary fields:
            - "target"
            - "total"
            - "error"
            - "iterations"
            - "H0"
            - "method"
            - "dt_final"

    Notes
    -----
    The target total conductor length is defined as the length obtained when all
    spans are evaluated at the single reference tension T_ref. This matches the
    current total-length-error philosophy in the rebuilt solver structure. 
    """
    n = len(spans)
    target = total_length(spans, heights, np.full(n, float(T_ref)), w)

    H0 = float(np.clip(T_ref, H_min, H_max))
    dt = float(dt0)

    iso = None
    best_H = None
    best_F = None
    best_H0 = H0

    for it in range(max_iters):
        F, H = total_length_error(
            spans=spans,
            heights=heights,
            H0=H0,
            w=w,
            target_total_length=target,
        )

        if best_F is None or abs(F) < abs(best_F):
            best_F = F
            best_H = H.copy()
            best_H0 = float(H0)

        if abs(F) <= atol_m:
            total = total_length(spans, heights, H, w)
            return H, {
                "target": target,
                "total": total,
                "error": F,
                "iterations": it,
                "H0": float(H0),
                "method": "legacy",
                "dt_final": dt,
            }

        if F <= 0.0:
            isn = -1
            if iso is not None and isn != iso:
                dt /= 2.0
            H0 -= dt
        else:
            isn = 1
            if iso is not None and isn != iso:
                dt /= 2.0
            H0 += dt

        iso = isn
        H0 = float(np.clip(H0, H_min, H_max))

    total = total_length(spans, heights, best_H, w)
    return best_H, {
        "target": target,
        "total": total,
        "error": best_F,
        "iterations": max_iters,
        "H0": float(best_H0),
        "method": "legacy",
        "dt_final": dt,
    }