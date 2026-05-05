"""
    formulas.py
    ===========

    Main groups of functions
    ------------------------
    1. Ruling span
    2. Span length and sag formulas
    3. Correction-term formulas used in the final output tables

    Typical usage pattern
    ---------------------
    >>> import numpy as np
    >>> from data import select_conductor_data
    >>> from formulas import ruling_span_info, lengths, sags
    >>>
    >>> spans = np.array([230.0, 250.0, 410.0, 220.0])
    >>> heights = np.array([5.0, -3.0, 8.0, 0.0])
    >>> ruling_span_m, ba_label = ruling_span_info(spans)
    >>> conductor = select_conductor_data("Grosbeak", ba_label)
    >>> T_ref = conductor["Tvec"][0]
    >>> L = lengths(spans, heights, np.full(len(spans), T_ref), conductor["w"])
    >>> f = sags(spans, np.full(len(spans), T_ref), conductor["w"])
"""

import numpy as np


################### Ruling span formulas #########################################

BA_350_LIMIT = 425.0


def ruling_span_info(spans):
    """
    Calculates the ruling span from a span list and classify the result.
    
    Notes
    -----
    The ruling span is calculated from:

        ruling span = sqrt(sum(span^3) / sum(span))

    This is the same expression already used in the previous codebase.

    Examples
    --------
    >>> spans = [230.0, 250.0, 410.0, 220.0]
    >>> ruling_span_m, ba_label = ruling_span_info(spans)
    >>> ba_label
    'BA 350'

    Common usage
    ------------
    >>> spans_arr = np.array([254.08, 385.0, 255.0, 485.0])
    >>> ruling_span_m, ba_label = ruling_span_info(spans_arr)
    >>> # The ba_label can then be passed to data.select_conductor_data().
    """
    s = np.asarray(spans, dtype=float)

    ruling_span_m = np.sqrt(np.sum(s**3) / np.sum(s))

    if ruling_span_m < BA_350_LIMIT:
        ba_label = "BA 350"
    else:
        ba_label = "BA 500"

    return ruling_span_m, ba_label


#################### Sag & Tension formulas ######################################

def lengths(spans, heights, tensions, w):
    """
    Calculates conductor lengths for each span - or for a single span, if a scalar is passed.

    Parameters
    ----------
    spans : array-like of float
        Horizontal spans in meters.

    heights : array-like of float
        Height differences in meters.

    tensions : array-like of float
        Tension values used in the length expression.
        One value is expected per span.

    w : float
        Conductor weight per unit length in kg/m.

    Returns
    -------
    numpy.ndarray
        One calculated length per span, in meters.

    Notes
    -----
    The expression used is:

        L = sqrt(s^2 + h^2 + s^4 * w^2 / (12 * T^2))

    This is the same formula already used in the previous solver files.
    
    NOTE:   This could be further improved by an analytic solution using
            the catenary equation.
            Perhaps also by introducing the additional complexity of E, A.

    Examples
    --------
    >>> spans = [230.0, 250.0]
    >>> heights = [5.0, -3.0]
    >>> tensions = [1800.0, 1800.0]
    >>> lengths(spans, heights, tensions, w=1.303)
    array([...])

    A very common pattern is to use one constant reference tension for all spans:

    >>> spans = np.array([230.0, 250.0, 410.0])
    >>> heights = np.array([5.0, -3.0, 8.0])
    >>> T_ref = 2026.0
    >>> L = lengths(spans, heights, np.full(len(spans), T_ref), w=1.303)
    """
    s = np.asarray(spans, dtype=float)
    h = np.asarray(heights, dtype=float)
    t = np.asarray(tensions, dtype=float)

    return np.sqrt(s**2 + h**2 + (s**4) * (w**2) / (12.0 * t**2))


def total_length(spans, heights, tensions, w):
    """
    Calculate the total conductor length over all spans.

    Returns
    -------
    float/scalar
        Sum of all span lengths, in meters.

    Example
    -------
    >>> spans = [230.0, 250.0, 410.0]
    >>> heights = [5.0, -3.0, 8.0]
    >>> tensions = [1800.0, 1800.0, 1800.0]
    >>> total = total_length(spans, heights, tensions, 1.303)
    """
    return np.sum(lengths(spans, heights, tensions, w))


def sags(spans, tensions, w):
    """
    Calculate sag values with the polynomial expression currently used in the solver.

    Parameters
    ----------
    spans : array-like of float
        Horizontal spans in meters.

    tensions : array-like of float
        Tension values, one per span.

    w : float
        Conductor weight per unit length in kg/m.

    Returns
    -------
    numpy.ndarray
        Sag values in meters.

    Notes
    -----
    The expression used is:

        f = s^2 * w / (8 * T) + s^4 * w^3 / (384 * T^3)

    Examples
    --------
    >>> spans = [230.0, 250.0]
    >>> tensions = [1800.0, 1800.0]
    >>> sags(spans, tensions, w=1.303)
    array([...])
    """
    s = np.asarray(spans, dtype=float)
    t = np.asarray(tensions, dtype=float)

    return (s**2) * w / (8.0 * t) + (s**4) * (w**3) / (384.0 * t**3)


def sags_legacy(spans, tensions, w):
    """
    Calculate sag values using only the first-order term.

    Notes
    -----
    The expression used is:

        f = s^2 * w / (8 * T)
    """
    s = np.asarray(spans, dtype=float)
    t = np.asarray(tensions, dtype=float)

    return (s**2) * w / (8.0 * t)


def sags_gritzapis(spans, tensions, w):
    """
    Λανθασμένος τύπος του Γκριτζάπη και του Μακρυκώστα. Έχουν λάθος στον όρο μεγαλύτερης τάξης.
    
    Notes
    -----
    The expression used is:

        f = s^2 * w / (8 * T) + s^3 * w^2 / (384 * T^3)
    """
    s = np.asarray(spans, dtype=float)
    t = np.asarray(tensions, dtype=float)

    return (s**2) * w / (8.0 * t) + (s**3) * (w ** 2) / (384.0 * t**3)


def sags_analytic(spans, tensions, w):
    """
    Calculate sag values using the analytic catenary expression at mid-span (for an equal-height span).

    Notes
    -----
    This function uses the equal-level catenary expression:

        f = (T / w) * (cosh(w * s / (2 * T)) - 1)

    This is an analytic same-support-height expression. It is useful for
    comparison work, but it does not by itself handle unequal support heights.
    """
    s = np.asarray(spans, dtype=float)
    t = np.asarray(tensions, dtype=float)

    a = t / float(w)
    
    return a * (np.cosh(s/2/a) - 1.0)     


def increase(spans, heights):
    """
    Calculate the geometric span-increase factor.

    Notes
    -----
    The expression used is:

        increase = sqrt(s^2 + h^2) / s

    In the existing code, this factor is multiplied by the sag values to account
    for the fact that the actual span direction is longer than the horizontal
    projection when the supports are at different levels.

    Example
    -------
    >>> spans = [230.0, 250.0]
    >>> heights = [5.0, -3.0]
    >>> increase(spans, heights)
    array([...])
    """
    s = np.asarray(spans, dtype=float)
    h = np.asarray(heights, dtype=float)

    return np.sqrt(s**2 + h**2) / s


###################### Correction Geometric - Elastic ############################################

def tension_correction_terms(spans, heights, T_ref, H_solution, w, area_cm2, E_kg_per_m2):
    """
    Calculate the legacy-style correction terms used for the final correction column.
    
    Parameters
    ----------
        spans : array-like of float
            Horizontal span lengths in meters.

        heights : array-like of float
            Height differences in meters.

        T_ref : float
            Reference horizontal tension used to define the target total conductor
            length for the section.

        H_solution : array-like of float
            Solved horizontal tensions, one value per span.

        w : float
            Conductor weight per unit length in kg/m.

        area_cm2 : float
            Metallic area in cm^2.

        E_kg_per_m2 : float
            Modulus of elasticity in the same unit system used in the rest of the
            solver.

    Returns
    -------
    dict
        Dictionary with both per-span step terms and cumulative terms:

        ``elastic_term_m``
            Per-span elastic contribution.

        ``geometric_term_m``
            Per-span geometric correction written in the same sign convention used
            by the older "simple correction" style. This is ``-geometric_raw``.

        ``combined_term_m``
            Per-span total correction.

        ``elastic_cum_m``
            Cumulative elastic contribution.

        ``geometric_cum_m``
            Cumulative geometric contribution.

        ``combined_cum_m``
            Cumulative total correction.


    Physical meaning
    ----------------
    This function tries to answer the following question:

    When the final solved tensions differ from the single reference tension
    ``T_ref``, how much of the conductor-length difference in each span comes
    from:

    1. elastic stretching or shrinking of the conductor material, and
    2. the purely geometric fact that a deeper curve is longer than a flatter one?

    The function keeps those two mechanisms separate.

    1) Elastic term
    ----------------
    If tension increases, the conductor stretches.
    If tension decreases, the conductor contracts.

    In the legacy expression used here, the elastic contribution is written as:

        elastic_term = b^3 * (H_solution - T_ref) / (A * E * s^2)

    where:

    - ``b = sqrt(s^2 + h^2)`` is the straight support-to-support chord
    - ``A`` is the metallic area converted from cm^2 to m^2
    - ``E`` is the modulus of elasticity
    - ``s`` is the horizontal span
    - ``H_solution`` is the solved tension of the current span

    No idea how legit this expression is; something to research in the future.

    2) Geometric term
    -----------------
    Even if the material itself did not stretch, changing the tension changes the
    conductor shape. A lower-tension span sags more and therefore requires more
    conductor length. A higher-tension span sags less and therefore requires less
    conductor length.

    This is measured by comparing the span length formula at the solved tension
    against the span length formula at the reference tension:

        geometric_term = L(H_solution) - L(T_ref)

    Interpretation:

    - positive geometric term:
      the solved shape is longer than the reference shape
    - negative geometric term:
      the solved shape is shorter than the reference shape

    Why the correction propagates span to span
    ------------------------------------------
    The conductor is continuous through a section of suspension spans.
    Because of that continuity, an excess or deficit of available conductor in
    one span does not remain isolated to that span. It must be absorbed by the
    neighboring spans and by the overall final state of the section.

    That is why the function returns not only the per-span correction ``da`` but
    also the cumulative correction ``dda``:

        dda[0] = da[0]
        dda[1] = da[0] + da[1]
        dda[2] = da[0] + da[1] + da[2]
        ...

    The cumulative array is a running balance of length surplus or deficit as the
    spans are traversed in order.

    In simple words:

    - one span may end up effectively "giving" conductor length to the chain
    - another span may end up "taking" conductor length from the chain
    - the cumulative sum shows how that balance evolves from span to span

    This is the practical reason the correction is not treated as a completely
    independent value for each span.

    Example
    -------
    >>> info = tension_correction_terms(
    ...     spans=spans,
    ...     heights=heights,
    ...     T_ref=1800.0,
    ...     H_solution=H_solution,
    ...     w=1.303,
    ...     area_cm2=3.71,
    ...     E_kg_per_m2=6.184e9,
    ... )
    >>> info["combined_cum_m"]
    array([...])

    """
    
    s = np.asarray(spans, dtype=float)
    h = np.asarray(heights, dtype=float)
    H_solution = np.asarray(H_solution, dtype=float)
    T_ref = float(T_ref)                # scalar --- I later do H_solution - T_ref, which is fine.
                                        # it's perfectly okay to subtract scalars from numpy arrays.   

    geometric_term = lengths(s, h, H_solution, w) - lengths(s, h, T_ref, w)

    area_m2 = area_cm2/10000.0          # unit conversion
    b = np.sqrt(s**2 + h**2)
    
    elastic_term = (b**3) * (H_solution - T_ref) / (area_m2 * E_kg_per_m2 * s**2)

    da = elastic_term - geometric_term  # αφαίρεση, διότι η τάνυση έχει άντιστροφη επίδραση σε αυτά τα μεγέθη
                                        # μεγάλη τάνυση => αύξηση ελαστικού όρου με ταυτόχρονη μείωση γεωμετρικού   
                                        # και το αντίστροφο
    
    dda = np.cumsum(da)                 # cummulative sum for correction propagation.       
                                        
    return {
        "elastic_term_m": elastic_term,
        "geometric_term_m": -geometric_term,
        "combined_term_m": da,
        "elastic_cum_m": np.cumsum(elastic_term),
        "geometric_cum_m": np.cumsum(-geometric_term),
        "combined_cum_m": dda,
    }
