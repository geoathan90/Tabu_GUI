import numpy as np
import pandas as pd 
import os

spans=np.array([254.08, 385, 255, 485, 275, 420, 280, 485, 215, 460, 410, 285, 352, 590, 225,638.02])   #np.array([333.4, 523.25, 350.1, 410.4])
heights = np.array([-57.13, -21.81, -5.28, 33.25, -25.6, 38.64, 10.76, -68.07, -41.67, -84.99, -38.77, 12.91, -29.32, 23.71, 0.51, 5.41]) #np.array([75.4, 60.8, -85.2, -70])

# Temperatures (°C) — same index positions used in all T-arrays below
TEMPS = np.array([0, 10, 20, 30, 40], dtype=float)

# All conductors in one dict
CONDUCTORS = {
    "Linnet": {
        "w": 0.7024,
        "A_cm2": 1.998,
        "E_kg_per_m2": 6.184e9,
        "T350": np.array([1527, 1457, 1386, 1327, 1269], dtype=float),
        "T500": np.array([1244, 1219, 1185, 1172, 1149], dtype=float),
    },
    "Grosbeak": {
        "w": 1.303,
        "A_cm2": 3.71,
        "E_kg_per_m2": 6.184e9,
        "T350": np.array([2183, 2102, 2028, 1960, 1893], dtype=float),
        "T500": np.array([2026, 1989, 1953, 1919, 1885], dtype=float),
    },
    "Cardinal": {
        "w": 1.823,
        "A_cm2": 5.46,
        "E_kg_per_m2": 5.132e9,
        "T350": np.array([3480, 3332, 3185, 3065, 2945], dtype=float),
        "T500": np.array([3105, 3045, 2980, 2925, 2870], dtype=float),
    },
    "SW150_0_460": {
        "w": 0.46,
        "A_cm2": 0.55,
        "E_kg_per_m2": 19.334e9,
        "T350": np.array([1118, 1074, 1031, 994, 957], dtype=float),
        "T500": np.array([892, 876, 860, 846, 832], dtype=float),
    },
    "SW150_0_396": {
        "w": 0.396,
        "A_cm2": 0.62,
        "E_kg_per_m2": 14.56e9,
        "T350": np.array([962, 925, 888, 856, 824], dtype=float),
        "T500": np.array([768, 754, 740, 728, 716], dtype=float),
    },
    "SW400": {
        "w": 0.769,
        "A_cm2": 0.96,
        "E_kg_per_m2": 14.56e9, #19.334e9,
        "T350": np.array([1810, 1740, 1670, 1610, 1550], dtype=float),
        "T500": np.array([1520, 1495, 1470, 1445, 1420], dtype=float),
    },
}

w = np.nan
A_cm2 = None
E_kg_per_m2 = None

def select_conductor(name: str, ruling: int = 350):
    """
    Returns a dict with:
      - w (kg/m)
      - A_cm2 (cm²), if known
      - E_kg_per_m2 (kgf/m² or kp/m² compatible), if known
      - Tvec: the tensions vs temperature for the chosen ruling span
    """
    data = CONDUCTORS[name]
    if ruling == 350:
        Tvec = data["T350"]
    elif ruling == 500:
        Tvec = data["T500"]
    else:
        raise ValueError("ruling must be 350 or 500")

    return {
        "w": data["w"],
        "A_cm2": data.get("A_cm2"),
        "E_kg_per_m2": data.get("E_kg_per_m2"),
        "Tvec": Tvec,
    }

def lengths(tension_list: np.ndarray) -> np.ndarray:
    
    s = np.asarray(spans, dtype=float)
    h = np.asarray(heights, dtype=float)
    t = np.asarray(tension_list, dtype=float)
    
    return np.sqrt(s*s + h*h + (s**4) * (w*w) / (12.0 * t*t))

def sags(tension_list: np.ndarray) -> np.ndarray:
    """
    Returns a list of sags for each span in the dataframe
    """
    t = np.asarray(tension_list, dtype=float)
    s = np.asarray(spans, dtype=float)
    
    return (s**2) * w / (8.0 * t) + (s**4) * (w**3) / (384 * t**3)

def sags_gritzapis(tension_list: np.ndarray) -> np.ndarray:
    """
    δοκιμαστικοί υπολογισμοί Γκριτζάπη
    """

    t = np.asarray(tension_list, dtype=float)
    s = np.asarray(spans, dtype = float)

    return (s**2) * w / (8.00 * t) + (s**3) * (w**2) / (384 * t**3)

def sags_legacy(tension_list: np.ndarray) -> np.ndarray:
    """
    just a trial to see if it changes the convergence
    """

    t = np.asarray(tension_list, dtype=float)
    s = np.asarray(spans, dtype = float)

    return (s**2) * w / (8.00 * t) 

def sags_analytic(tension_list:np.ndarray) -> np.ndarray:
    """
    using the hyperbolic cosine function at mid-span for an idealized same-height span
    """ 
    t = np.asarray(tension_list, dtype=float)
    s = np.asarray(spans, dtype = float)

    return (t/w) * (np.cosh(-s/2/(t/w)) - np.cosh(0))

def increase(tension_list: np.ndarray) -> np.ndarray:

    h = np.asarray(heights, dtype=float)
    #t = np.asarray(tension_list, dtype=float)
    #l = lengths(t)
    s = np.asarray(spans, dtype=float)

    return (np.sqrt(s*s+h*h))/s #l/s

    # return l/ (s * (1 + s * w / t )**2 / 24)

def span_groups(spans_array: np.ndarray | None = None, min_positive: float = 0.1) -> list[np.ndarray]:
    """
    Split an array of spans into contiguous positive-span groups.
    Useful when a line file contains multiple independent sections separated by zeros.
    """
    s = np.asarray(spans if spans_array is None else spans_array, dtype=float)
    groups: list[np.ndarray] = []
    start = None

    for i, value in enumerate(s):
        if value > min_positive:
            if start is None:
                start = i
        else:
            if start is not None:
                groups.append(np.arange(start, i, dtype=int))
                start = None

    if start is not None:
        groups.append(np.arange(start, len(s), dtype=int))

    return groups


def ruling_span_value(spans_array: np.ndarray) -> float:
    """
    Standard ruling span:
        sqrt(sum(span^3) / sum(span))
    """
    s = np.asarray(spans_array, dtype=float)
    if s.size == 0:
        raise ValueError("ruling span requires at least one span")
    denom = float(np.sum(s))
    if denom <= 0.0:
        raise ValueError("sum(spans) must be positive")
    return float(np.sqrt(np.sum(s**3) / denom))


def classify_ruling_span(ruling_span_m: float) -> str:
    return "BA 350" if ruling_span_m < 425.0 else "BA 500"


def analyze_ruling_span_groups(
    spans_array: np.ndarray | None = None,
    min_positive: float = 0.1,
) -> list[dict]:
    """
    For each contiguous analyzed span group, compute the ruling span and the BA class.
    Returns a list of dicts with group indices, ruling span, and BA label.
    """
    s = np.asarray(spans if spans_array is None else spans_array, dtype=float)
    results: list[dict] = []
    for idxs in span_groups(s, min_positive=min_positive):
        group_spans = s[idxs]
        rs = ruling_span_value(group_spans)
        results.append({
            "start_index": int(idxs[0]),
            "end_index": int(idxs[-1]),
            "spans": group_spans.astype(float).tolist(),
            "ruling_span_m": rs,
            "ba_label": classify_ruling_span(rs),
        })
    return results


def tension_correction_terms(
    T_ref: float,
    H_solution: np.ndarray,
    area_cm2: float | None = None,
    E_kg_per_m2_value: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Legacy-C-style correction terms for the final column.

    Returns:
      elastic_term_m    per-span elastic contribution
      geometric_term_m  per-span geometric contribution, L(H_solution)-L(T_ref)
      da_m              per-span net correction = elastic - geometric
      dda_m             cumulative correction

    If area or modulus is missing, the function falls back to the geometric-only
    behavior that existed previously:
      da = L(T_ref) - L(H_solution)
    """
    s = np.asarray(spans, dtype=float)
    h = np.asarray(heights, dtype=float)
    tor = np.asarray(H_solution, dtype=float)
    T0 = np.full_like(s, float(T_ref), dtype=float)

    geometric_term = lengths(tor) - lengths(T0)

    if area_cm2 is None or E_kg_per_m2_value is None:
        da = -geometric_term
        dda = np.cumsum(da)
        zeros = np.zeros_like(da)
        return zeros, geometric_term, da, dda

    area_m2 = float(area_cm2) / 10000.0
    if area_m2 <= 0.0:
        raise ValueError("area_cm2 must be positive")
    if E_kg_per_m2_value <= 0.0:
        raise ValueError("E_kg_per_m2 must be positive")

    b = np.sqrt(s * s + h * h)
    elastic_term = (b**3) * (tor - float(T_ref)) / (area_m2 * float(E_kg_per_m2_value) * s * s)
    da = elastic_term - geometric_term
    dda = np.cumsum(da)
    return elastic_term, geometric_term, da, dda


def correction_breakdown(
    T_ref: float,
    H_solution: np.ndarray,
    area_cm2: float | None = None,
    E_kg_per_m2_value: float | None = None,
) -> dict[str, np.ndarray]:
    """
    Split the legacy final correction into three cumulative components:
      - geometric: cumulative geometric-only correction (old simple diorthosi sign)
      - elastic  : cumulative elastic contribution
      - combined : cumulative sum of both = legacy final column

    Also returns the per-span step terms for debugging.
    """
    elastic_raw, geometric_raw, combined_step, combined_cum = tension_correction_terms(
        T_ref=T_ref,
        H_solution=H_solution,
        area_cm2=area_cm2,
        E_kg_per_m2_value=E_kg_per_m2_value,
    )

    geometric_step = -geometric_raw
    elastic_step = elastic_raw

    return {
        "elastic_step_m": elastic_step,
        "geometric_step_m": geometric_step,
        "combined_step_m": combined_step,
        "elastic_cum_m": np.cumsum(elastic_step),
        "geometric_cum_m": np.cumsum(geometric_step),
        "combined_cum_m": combined_cum,
    }



def build_result_dataframe(
    temperature_C: float,
    T_ref: float,
    H_solution: np.ndarray,
    area_cm2: float | None = None,
    E_kg_per_m2_value: float | None = None,
) -> pd.DataFrame:
    """
    Build the per-temperature output table used by both tabu.py exports and app.py.
    The three correction columns are cumulative, because the original final column
    was cumulative as well.
    """
    N = len(spans)
    T_ref_arr = np.full(N, float(T_ref), dtype=float)
    inc = increase(T_ref_arr)
    corr = correction_breakdown(
        T_ref=T_ref,
        H_solution=H_solution,
        area_cm2=A_cm2 if area_cm2 is None else area_cm2,
        E_kg_per_m2_value=E_kg_per_m2 if E_kg_per_m2_value is None else E_kg_per_m2_value,
    )

    return pd.DataFrame({
        "temperature_C": np.full_like(spans, float(temperature_C), dtype=float),
        "span_m": np.asarray(spans, dtype=float),
        "height_m": np.asarray(heights, dtype=float),
        "T_ref_kg": T_ref_arr,
        "H_solution_kg": np.asarray(H_solution, dtype=float),
        "sag_eq_m": inc * sags(T_ref_arr),
        "sag_alt_m": inc * sags(H_solution),
        "diorthosi_geometric_m": corr["geometric_cum_m"],
        "diorthosi_elastic_m": corr["elastic_cum_m"],
        "diorthosi_combined_m": corr["combined_cum_m"],
    })


def _forward_from_H0(H0: float):
    """
    One forward sweep given the initial horizontal tension H0.
    Uses:
      if height[i] > 0 : axial[i+1] = H[i] + w*eq_sag[i]
      else (<= 0)      : axial[i+1] = H[i] + w*(eq_sag[i] + height[i])
    """
    s = np.asarray(spans, dtype=float)
    h = np.asarray(heights, dtype=float)
    N = s.size

    H = np.empty(N, dtype=float)
    H[0] = float(H0)

    for i in range(0, N - 1):
        # Ισοϋψές άνοιγμα και βέλος ισοϋψούς ανοίγματος 
        eq_span = s[i] + (2.0 * H[i] * abs(h[i])) / (s[i] * w)
        eq_sag  = (eq_span ** 2) * w / (8.0 * H[i])

        # Αξονική τάνυση στο επόμενο άνοιγμα
        if h[i] > 0.0:
            axial_next = H[i] + w * eq_sag
        else:
            axial_next = H[i] + w * (eq_sag + h[i])  

        # Οριζόντια συνιστώσα στο επόμενο άνοιγμα
        denom = 2.0 + (h[i + 1] * h[i + 1]) / (s[i + 1] * s[i + 1])
        disc  = (axial_next ** 2
                 + axial_next * w * h[i + 1]
                 - 0.5 * (s[i + 1] * s[i + 1]) * (w * w))

        if disc < 0.0:
            print(f"Αρνητική διακρίνουσα {i+1} , τη θεωρώ 0, ΕΛΕΓΧΟΣ.")
            disc = 0.0

        H[i + 1] = (axial_next + 0.5 * w * h[i + 1] + np.sqrt(disc)) / denom

    return H, []


def _total_length_error(H0: float, target_total_length: float):
    """
    Compute error = total_length(H0) - target_total_length.
    Returns error, H
    """
    H, _ = _forward_from_H0(H0)
    total_len = float(np.sum(lengths(H)))
    return total_len - target_total_length, H

def solve_horizontal_tensions_bruteforce(
    T_ref: float,
    atol_m: float = 0.001,
    H_min: float = 1e-6,
    H_max: float = 4000.0,
    step: float = 1.0,
    max_iters: int = 50000,
):
    """
    Outer solve on H0 (horizontal_tension[0]) using a simple unit-step search.
    - Start at T350
    - If total length is too long (F>0), increase H0 by 1
      If too short (F<0), decrease H0 by 1
    - On first sign change between consecutive integers, pick the better of the two.

    Returns:
      H    : np.ndarray of horizontal tensions per span (length N)
      info : dict with fields (target, total, error, iterations, H0)
    """
    N = len(spans)

    # 1) Target: all spans at T350
    target = float(np.sum(lengths(np.full(N, T_ref, dtype=float))))

    # 2) Start from T350, clamp to (0, 4000)
    H0 = float(np.clip(T_ref, 1e-6, 4000.0))

    # Evaluate at the start
    F, H = _total_length_error(H0, target)
    if abs(F) <= atol_m:
        total = float(np.sum(lengths(H)))
        return H, {"target": target, "total": total, "error": F, "iterations": 0, "H0": H0}

    # Decide initial direction
    # F > 0 → total too long → increase H0 (shortens length)
    # F < 0 → total too short → decrease H0 (lengthens)
    direction = 1.0 if F > 0 else -1.0

    prev_H0, prev_F, prev_H = H0, F, H

    for it in range(1, max_iters + 1):
        # Propose next H0 and clamp to physical bounds
        H0_new = prev_H0 + direction * step
        H0_new = float(np.clip(H0_new, 1e-6, 4000.0))

        # If we can't move further (stuck at bound), return best-so-far
        if H0_new == prev_H0:
            total = float(np.sum(lengths(prev_H)))
            return prev_H, {
                "target": target, "total": total,
                "error": prev_F, "iterations": it, "H0": prev_H0
            }

        F_new, H_new = _total_length_error(H0_new, target)

        # Check tolerance
        if abs(F_new) <= atol_m:
            total = float(np.sum(lengths(H_new)))
            return H_new, {"target": target, "total": total, "error": F_new, "iterations": it, "H0": H0_new}

        # Check for sign change between consecutive integers
        if prev_F * F_new < 0.0:
            # Pick the better of the two neighbors
            if abs(prev_F) <= abs(F_new):
                best_H0, best_F, best_H = prev_H0, prev_F, prev_H
            else:
                best_H0, best_F, best_H = H0_new, F_new, H_new

            total = float(np.sum(lengths(best_H)))
            return best_H, {
                "target": target, "total": total,
                "error": best_F, "iterations": it, "H0": best_H0
            }

        # No sign change: keep walking in the same direction
        prev_H0, prev_F, prev_H = H0_new, F_new, H_new

    # Max iterations reached: return best-so-far
    total = float(np.sum(lengths(prev_H)))
    return prev_H, {
        "target": target, "total": total,
        "error": prev_F, "iterations": max_iters, "H0": prev_H0,
        "method": "bruteforce"
    }

def solve_horizontal_tensions(
    T_ref: float,
    atol_m: float = 0.001,
    H_min: float = 1e-6,
    H_max: float = 4000.0,
    step: float = 1.0,
    max_iters: int = 50000,
):
    """
    Outer solve on H0 (horizontal_tension[0]) using a simple unit-step search.
    - Start at T350
    - If total length is too long (F>0), increase H0 by 1
      If too short (F<0), decrease H0 by 1
    - On first sign change between consecutive integers, pick the better of the two.

    Returns:
      H    : np.ndarray of horizontal tensions per span (length N)
      info : dict with fields (target, total, error, iterations, H0)
    """
    N = len(spans)

    # 1) Target: all spans at T350
    target = float(np.sum(lengths(np.full(N, T_ref, dtype=float))))

    # 2) Start from T350, clamp to (0, 4000)
    H0 = float(np.clip(T_ref, 1e-6, 4000.0))

    # Evaluate at the start
    F, H = _total_length_error(H0, target)
    if abs(F) <= atol_m:
        total = float(np.sum(lengths(H)))
        return H, {"target": target, "total": total, "error": F, "iterations": 0, "H0": H0}

    # Decide initial direction
    # F > 0 → total too long → increase H0 (shortens length)
    # F < 0 → total too short → decrease H0 (lengthens)
    direction = 1.0 if F > 0 else -1.0

    prev_H0, prev_F, prev_H = H0, F, H

    for it in range(1, max_iters + 1):
        # Propose next H0 and clamp to physical bounds
        H0_new = prev_H0 + direction * step
        H0_new = float(np.clip(H0_new, 1e-6, 4000.0))

        # If we can't move further (stuck at bound), return best-so-far
        if H0_new == prev_H0:
            total = float(np.sum(lengths(prev_H)))
            return prev_H, {
                "target": target, "total": total,
                "error": prev_F, "iterations": it, "H0": prev_H0
            }

        F_new, H_new = _total_length_error(H0_new, target)

        # Check tolerance
        if abs(F_new) <= atol_m:
            total = float(np.sum(lengths(H_new)))
            return H_new, {"target": target, "total": total, "error": F_new, "iterations": it, "H0": H0_new}

        # Check for sign change between consecutive integers
        if prev_F * F_new < 0.0:
            # Pick the better of the two neighbors
            if abs(prev_F) <= abs(F_new):
                best_H0, best_F, best_H = prev_H0, prev_F, prev_H
            else:
                best_H0, best_F, best_H = H0_new, F_new, H_new

            total = float(np.sum(lengths(best_H)))
            return best_H, {
                "target": target, "total": total,
                "error": best_F, "iterations": it, "H0": best_H0
            }

        # No sign change: keep walking in the same direction
        prev_H0, prev_F, prev_H = H0_new, F_new, H_new

    # Max iterations reached: return best-so-far
    total = float(np.sum(lengths(prev_H)))
    return prev_H, {
        "target": target, "total": total,
        "error": prev_F, "iterations": max_iters, "H0": prev_H0,
        "method": "bruteforce"
    }
################## additional solvers #######################

def _bracket_root_for_H0(T_ref: float,
                         H_min: float = 1e-6,
                         H_max: float = 4000.0,
                         expand_factor: float = 2.0,
                         max_expands: int = 40):
    N = len(spans)
    target = float(np.sum(lengths(np.full(N, float(T_ref), dtype=float))))

    lo = float(np.clip(T_ref / 2.0, H_min, H_max))
    hi = float(np.clip(T_ref * 2.0, H_min, H_max))

    Flo, _ = _total_length_error(lo, target)
    Fhi, _ = _total_length_error(hi, target)
    if Flo * Fhi < 0.0:
        return lo, Flo, hi, Fhi

    for _ in range(max_expands):
        new_lo = float(max(H_min, lo / expand_factor))
        Flo, _ = _total_length_error(new_lo, target)
        lo = new_lo
        if Flo * Fhi < 0.0:
            return lo, Flo, hi, Fhi 

        new_hi = float(min(H_max, hi * expand_factor))
        Fhi, _ = _total_length_error(new_hi, target)
        hi = new_hi
        if Flo * Fhi < 0.0:
            return lo, Flo, hi, Fhi

        if lo <= H_min and hi >= H_max:
            break

    raise ValueError("Could not bracket a root within physical bounds for H0.")


def solve_horizontal_tensions_bisect(
    T_ref: float,
    atol_m: float = 0.001,
    H_min: float = 1e-6,
    H_max: float = 4000.0,
    max_iters: int = 50000
):
    N = len(spans)
    target = float(np.sum(lengths(np.full(N, float(T_ref), dtype=float))))
    lo, Flo, hi, Fhi = _bracket_root_for_H0(T_ref, H_min, H_max)

    it = 0
    mid = None
    Fmid = None
    while it < max_iters:
        mid = 0.5 * (lo + hi)
        Fmid, H_mid = _total_length_error(mid, target)

        if abs(Fmid) <= atol_m:
            total = float(np.sum(lengths(H_mid)))
            return H_mid, {
                "target": target, "total": total, "error": Fmid,
                "iterations": it, "H0": mid, "method": "bisection"
            }

        if Flo * Fmid > 0.0:
            lo, Flo = mid, Fmid
        else:
            hi, Fhi = mid, Fmid

        it += 1

    H_mid, _ = _forward_from_H0(mid)
    total = float(np.sum(lengths(H_mid)))
    return H_mid, {
        "target": target, "total": total, "error": Fmid,
        "iterations": it, "H0": mid, "method": "bisection"
    }


def solve_horizontal_tensions_newton(
    T_ref: float,
    atol_m: float = 0.001,
    H0: float | None = None,
    H_min: float = 1e-6,
    H_max: float = 4000.0,
    max_iters: int = 50000,
    safeguarding: bool = True,
):
    N = len(spans)
    target = float(np.sum(lengths(np.full(N, float(T_ref), dtype=float))))
    if H0 is None:
        H0 = float(np.clip(T_ref, H_min, H_max))
    else:
        H0 = float(np.clip(H0, H_min, H_max))

    lo, Flo, hi, Fhi = _bracket_root_for_H0(T_ref, H_min, H_max)

    newton_steps = 0
    bisect_steps = 0

    for it in range(max_iters):
        F, H_curr = _total_length_error(H0, target)
        if abs(F) <= atol_m:
            total = float(np.sum(lengths(H_curr)))
            return H_curr, {
                "target": target, "total": total, "error": F,
                "iterations": it, "H0": H0, "method": "newton", 
                "newton_steps": newton_steps, "bisect_steps": bisect_steps
            }

        if Flo * F <= 0.0:
            hi, Fhi = H0, F
        else:
            lo, Flo = H0, F

        dh = max(1e-3, 1e-3 * max(1.0, abs(H0)))
        Hp = float(min(H_max, H0 + dh))
        Hm = float(max(H_min, H0 - dh))
        Fp, _ = _total_length_error(Hp, target)
        Fm, _ = _total_length_error(Hm, target)
        dF = (Fp - Fm) / (Hp - Hm) if Hp != Hm else np.nan

        if np.isfinite(dF) and dF != 0.0:
            Hn = H0 - F / dF
        else:
            Hn = np.nan

        accept_newton = (
            np.isfinite(Hn)
            and H_min <= Hn <= H_max
            and (not safeguarding or (lo <= Hn <= hi))
        )

        if accept_newton:
            H0 = float(Hn)
            newton_steps += 1
            continue

        H0 = 0.5 * (lo + hi)
        bisect_steps += 1

    H_curr, _ = _forward_from_H0(H0)
    total = float(np.sum(lengths(H_curr)))
    err, _ = _total_length_error(H0, target)
    return H_curr, {
        "target": target, "total": total, "error": err,
        "iterations": max_iters, "H0": H0, "method": "newton",
        "newton_steps": newton_steps, "bisect_steps": bisect_steps
    }

def configure_case(
    spans_arr=None,
    heights_arr=None,
    conductor_name="Grosbeak",
    ruling=350,
    area_cm2=None,
    E_kg_per_m2_value=None,
):
    """
    Set the active spans/heights and conductor properties used by the formulas.
    Returns the selected conductor dict.
    """
    global spans, heights, w, A_cm2, E_kg_per_m2

    if spans_arr is not None:
        spans = np.asarray(spans_arr, dtype=float)
    if heights_arr is not None:
        heights = np.asarray(heights_arr, dtype=float)

    sel = select_conductor(conductor_name, ruling=ruling)
    w = sel["w"]
    A_cm2 = sel.get("A_cm2") if area_cm2 is None else area_cm2
    E_kg_per_m2 = sel.get("E_kg_per_m2") if E_kg_per_m2_value is None else E_kg_per_m2_value
    return sel


def solve_case(
    T_ref,
    solver_method="Bisection",
    atol_m=0.001,
    max_iters=50000,
    step_val=0.1,
):
    """
    Shared solver dispatcher used by both tabu.py and app.py.
    """
    method = str(solver_method).strip().lower()

    if method == "brute force":
        H_solution, info = solve_horizontal_tensions_bruteforce(
            T_ref=float(T_ref),
            atol_m=float(atol_m),
            step=float(step_val),
            max_iters=int(max_iters),
        )
    elif method == "bisection":
        H_solution, info = solve_horizontal_tensions_bisect(
            T_ref=float(T_ref),
            atol_m=float(atol_m),
            max_iters=int(max_iters),
        )
    elif method in ["newton", "newton-raphson", "newton raphson"]:
        H_solution, info = solve_horizontal_tensions_newton(
            T_ref=float(T_ref),
            atol_m=float(atol_m),
            max_iters=int(max_iters),
        )
    else:
        raise ValueError("Unknown solver_method")

    if "method" not in info:
        if method == "brute force":
            info["method"] = "bruteforce"
        elif method == "bisection":
            info["method"] = "bisection"
        else:
            info["method"] = "newton"

    return H_solution, info


def run_one_temperature(
    spans_arr,
    heights_arr,
    conductor_name="Grosbeak",
    ruling=350,
    temperature_C=0,
    solver_method="Bisection",
    atol_m=0.001,
    max_iters=50000,
    step_val=0.1,
    area_cm2=None,
    E_kg_per_m2_value=None,
):
    """
    Configure one case, solve one temperature, and return the dataframe plus solver info.
    """
    sel = configure_case(
        spans_arr=spans_arr,
        heights_arr=heights_arr,
        conductor_name=conductor_name,
        ruling=ruling,
        area_cm2=area_cm2,
        E_kg_per_m2_value=E_kg_per_m2_value,
    )

    idx = list(TEMPS).index(float(temperature_C))
    T_ref = float(sel["Tvec"][idx])
    temperature = float(TEMPS[idx])

    H_solution, info = solve_case(
        T_ref=T_ref,
        solver_method=solver_method,
        atol_m=atol_m,
        max_iters=max_iters,
        step_val=step_val,
    )

    df = build_result_dataframe(
        temperature_C=temperature,
        T_ref=T_ref,
        H_solution=H_solution,
        area_cm2=A_cm2,
        E_kg_per_m2_value=E_kg_per_m2,
    )
    return df, info


def run_all_temperatures(
    spans_arr,
    heights_arr,
    conductor_name="Grosbeak",
    ruling=350,
    solver_method="Bisection",
    atol_m=0.001,
    max_iters=50000,
    step_val=0.1,
    area_cm2=None,
    E_kg_per_m2_value=None,
):
    """
    Run the full 0/10/20/30/40 C set using one shared path.
    Returns a list of dicts with temperature, dataframe, and solver info.
    """
    sel = configure_case(
        spans_arr=spans_arr,
        heights_arr=heights_arr,
        conductor_name=conductor_name,
        ruling=ruling,
        area_cm2=area_cm2,
        E_kg_per_m2_value=E_kg_per_m2_value,
    )

    results = []
    for idx, temperature in enumerate(TEMPS):
        T_ref = float(sel["Tvec"][idx])
        H_solution, info = solve_case(
            T_ref=T_ref,
            solver_method=solver_method,
            atol_m=atol_m,
            max_iters=max_iters,
            step_val=step_val,
        )
        df = build_result_dataframe(
            temperature_C=float(temperature),
            T_ref=T_ref,
            H_solution=H_solution,
            area_cm2=A_cm2,
            E_kg_per_m2_value=E_kg_per_m2,
        )
        results.append({
            "temperature_C": float(temperature),
            "T_ref": T_ref,
            "df": df,
            "info": info,
        })

    return results


################## output ##############

def _format_for_export(df: pd.DataFrame) -> pd.DataFrame:
    """Return a formatted copy for CSV export."""
    df_exp = df.copy()

    # Integer-style columns
    for col in ["T_ref_kg", "temperature_C"]:
        if col in df_exp:
            df_exp[col] = np.rint(df_exp[col]).astype(int)

    # Two-decimal engineering outputs
    for col in ["sag_eq_m", "sag_alt_m", "H_solution_kg"]:
        if col in df_exp:
            df_exp[col] = df_exp[col].round(2)

    # Three-decimal correction outputs
    for col in [
        "diorthosi_geometric_m",
        "diorthosi_elastic_m",
        "diorthosi_combined_m",
    ]:
        if col in df_exp:
            df_exp[col] = df_exp[col].round(3)

    return df_exp


def build_and_export_tables(
    conductor_name="Grosbeak",
    ruling=350,
    atol_m=0.001,
    out_dir="outputs",
    area_cm2=None,
    E_kg_per_m2_value=None,
    solver_method="Bisection",
    max_iters=50000,
    step_val=0.1,
    spans_arr=None,
    heights_arr=None,
):
    """
    Run all temperatures through one shared solve path and export CSV files.
    Returns: dict { temperature(float): DataFrame }
    """
    os.makedirs(out_dir, exist_ok=True)

    if spans_arr is None:
        spans_arr = np.asarray(spans, dtype=float)
    if heights_arr is None:
        heights_arr = np.asarray(heights, dtype=float)

    configure_case(
        spans_arr=spans_arr,
        heights_arr=heights_arr,
        conductor_name=conductor_name,
        ruling=ruling,
        area_cm2=area_cm2,
        E_kg_per_m2_value=E_kg_per_m2_value,
    )

    ruling_groups = analyze_ruling_span_groups(spans_arr)
    if len(ruling_groups) == 1:
        inferred_ruling_span_m = ruling_groups[0]["ruling_span_m"]
        inferred_ba_label = ruling_groups[0]["ba_label"]
    else:
        inferred_ruling_span_m = np.nan
        inferred_ba_label = ", ".join(group["ba_label"] for group in ruling_groups)

    runs = run_all_temperatures(
        spans_arr=spans_arr,
        heights_arr=heights_arr,
        conductor_name=conductor_name,
        ruling=ruling,
        solver_method=solver_method,
        atol_m=atol_m,
        max_iters=max_iters,
        step_val=step_val,
        area_cm2=area_cm2,
        E_kg_per_m2_value=E_kg_per_m2_value,
    )

    results = {}

    for run in runs:
        temperature = run["temperature_C"]
        T_ref = run["T_ref"]
        df_out = run["df"]
        H_solution = np.asarray(df_out["H_solution_kg"], dtype=float)
        corr = correction_breakdown(
            T_ref=T_ref,
            H_solution=H_solution,
            area_cm2=A_cm2,
            E_kg_per_m2_value=E_kg_per_m2,
        )

        df_out.attrs["title"] = f"{conductor_name} @ {temperature}°C (ruling {ruling} m)"
        df_out.attrs["ruling_span_groups"] = ruling_groups
        df_out.attrs["inferred_ruling_span_m"] = inferred_ruling_span_m
        df_out.attrs["inferred_ba_label"] = inferred_ba_label
        df_out.attrs["A_cm2"] = A_cm2
        df_out.attrs["E_kg_per_m2"] = E_kg_per_m2
        df_out.attrs["elastic_step_m"] = corr["elastic_step_m"].tolist()
        df_out.attrs["geometric_step_m"] = corr["geometric_step_m"].tolist()
        df_out.attrs["combined_step_m"] = corr["combined_step_m"].tolist()
        df_out.attrs["elastic_cum_m"] = corr["elastic_cum_m"].tolist()
        df_out.attrs["geometric_cum_m"] = corr["geometric_cum_m"].tolist()
        df_out.attrs["combined_cum_m"] = corr["combined_cum_m"].tolist()
        df_out.attrs["solver_info"] = run["info"]

        fname = f"{conductor_name}_r{ruling}_{int(temperature)}C.csv"
        df_export = _format_for_export(df_out)
        df_export.to_csv(os.path.join(out_dir, fname), index=False)
        results[temperature] = df_out

    return results

# Example use:
# tables = build_and_export_tables("Grosbeak", ruling=350, atol_m=0.001, out_dir="outputs")
# tables[0.0].head()  # DataFrame for 0°C



################# usage   -  comment out when importing ####################

# sel = select_conductor("Grosbeak", ruling=350)
# w = sel["w"]
# Tvec = sel["Tvec"]


# for T_ref in Tvec:
#     H_solution, info = solve_horizontal_tensions(T_ref=T_ref, atol_m=0.001)
#     print("Solved H per span:", H_solution)

# print("Target total length (m):", info["target"])
# print("New total length (m):   ", info["total"])
# print("Error (m):              ", info["error"])
# print("Iterations:             ", info["iterations"])
# print("H0 used (kg):           ", info["H0"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the default tabu example and export CSV tables.")
    parser.add_argument("--conductor", default="Grosbeak")
    parser.add_argument("--ruling", type=int, default=350)
    parser.add_argument("--atol", type=float, default=0.001)
    parser.add_argument("--out-dir", default="outputs")
    parser.add_argument("--solver", default="Bisection")
    parser.add_argument("--max-iters", type=int, default=50000)
    parser.add_argument("--step", type=float, default=0.1)
    args = parser.parse_args()

    tables = build_and_export_tables(
        conductor_name=args.conductor,
        ruling=args.ruling,
        atol_m=args.atol,
        out_dir=args.out_dir,
        solver_method=args.solver,
        max_iters=args.max_iters,
        step_val=args.step,
    )
    print(f"Wrote {len(tables)} table(s) to {args.out_dir}")
    for temperature, df in tables.items():
        print(f"  {temperature:.0f} C -> {len(df)} row(s)")
