import numpy as np

from tabu_scripts.data import CONDUCTORS

def conductor_state_data(conductor_name):
    """
        Return conductor properties needed for state-equation calculations.

        Parameters
        ----------
        conductor_name : str
            Name of the conductor as stored in tabu_scripts.data.CONDUCTORS.

        Returns
        -------
        dict
            Dictionary with:
            - "name"
            - "w"            conductor weight per unit length [kg/m]
            - "A_cm2"        conductor area [cm^2]
            - "A_m2"         conductor area [m^2]
            - "E_kg_per_m2"  elasticity modulus in the same legacy-compatible
                            unit system used elsewhere in the project
            - "alpha"        thermal expansion coefficient [1/°C]

        Notes
        -----
        This function assumes each conductor entry in data.py contains:
        - w
        - A_cm2
        - E_kg_per_m2
        - alpha

        Example
        -------
        >>> info = conductor_state_data("Cardinal")
        >>> info["w"]
        1.823
        >>> info["A_m2"]
        0.000546
    """
    if conductor_name not in CONDUCTORS:
        raise ValueError(f"Unknown conductor: {conductor_name}")

    data = CONDUCTORS[conductor_name]

    required_fields = ["w", "A_cm2", "E_kg_per_m2", "alpha"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(
            f"Conductor '{conductor_name}' is missing required fields: {', '.join(missing)}"
        )

    A_cm2 = float(data["A_cm2"])

    return {
        "name": conductor_name,
        "w": float(data["w"]),
        "A_cm2": A_cm2,
        "A_m2": A_cm2 / 10000.0,
        "E_kg_per_m2": float(data["E_kg_per_m2"]),
        "alpha": float(data["alpha"]),
    }


def solve_for_H2(
    S,
    H1,
    T1,
    T2,
    A_m2,
    E_kg_per_m2,
    alpha,
    w1,
    w2=None,
    imag_tol=1e-9,
):
    """
        Solve the legacy cubic state equation for the new horizontal tension H2.

        Parameters
        ----------
        S : float
            Span length in meters.

        H1 : float
            Initial horizontal tension.

        T1 : float
            Initial temperature in °C.

        T2 : float
            Final temperature in °C.

        A_m2 : float
            Conductor area in m^2.

        E_kg_per_m2 : float
            Elasticity modulus in the same unit system used by the rest of the
            legacy formulas.

        alpha : float
            Thermal expansion coefficient [1/°C].

        w1 : float
            Initial unit weight [kg/m].

        w2 : float or None, default None
            Final unit weight [kg/m].
            If omitted, the same value as w1 is used.

        imag_tol : float, default 1e-9
            Maximum allowed imaginary part magnitude when filtering the roots of
            the cubic.

        Returns
        -------
        float
            Selected positive real root for H2.

        Physics / model note
        --------------------
        The equation solved here is the same cubic form already used in the older
        script:

            H2^3 + c1*H2^2 + c2*H2 + c3 = 0

        The old version used SymPy to solve the cubic symbolically. This version
        uses NumPy roots numerically, then keeps the positive real candidates and
        selects the largest one.

        The choice of the largest positive real root follows the existing legacy
        script logic.

        Example
        -------
        >>> props = conductor_state_data("Cardinal")
        >>> H2 = solve_for_H2(
        ...     S=50.0,
        ...     H1=2585.0,
        ...     T1=0.0,
        ...     T2=40.0,
        ...     A_m2=props["A_m2"],
        ...     E_kg_per_m2=props["E_kg_per_m2"],
        ...     alpha=props["alpha"],
        ...     w1=props["w"],
        ... )
    """
    S = float(S)
    H1 = float(H1)
    T1 = float(T1)
    T2 = float(T2)
    A_m2 = float(A_m2)
    E_kg_per_m2 = float(E_kg_per_m2)
    alpha = float(alpha)
    w1 = float(w1)
    w2 = float(w1 if w2 is None else w2)

    c1 = (
        alpha * A_m2 * E_kg_per_m2 * (T2 - T1)
        - H1
        + (w1**2 * A_m2 * E_kg_per_m2 * S**2) / (24.0 * H1**2)
    )

    c2 = S**2 * w2**2 / 24.0

    c3 = (
        alpha * A_m2 * E_kg_per_m2 * (T2 - T1) * (S**2 * w2**2) / 24.0
        - H1 * (S**2 * w2**2) / 24.0
        - (w2**2 * A_m2 * E_kg_per_m2 * S**2) / 24.0
    )

    roots = np.roots([1.0, c1, c2, c3])

    candidates = []
    for r in roots:
        if abs(r.imag) < imag_tol and r.real > 0.0 and np.isfinite(r.real):
            candidates.append(float(r.real))

    if not candidates:
        raise RuntimeError("Δεν βρέθηκε θετική πραγματική ρίζα για το H2.")

    return max(candidates)


def solve_for_H2_with_conductor(
    conductor_name,
    S,
    H1,
    T1,
    T2,
    w1=None,
    w2=None,
):
    """
        Convenience wrapper around solve_for_H2() using conductor data from data.py.

        Parameters
        ----------
        conductor_name : str
            Conductor name from tabu_scripts.data.CONDUCTORS.

        S, H1, T1, T2 : float
            Same meaning as in solve_for_H2().

        w1 : float or None, default None
            Initial unit weight [kg/m].
            If omitted, the conductor's nominal built-in weight is used.

        w2 : float or None, default None
            Final unit weight [kg/m].
            If omitted, w1 is used.

        Returns
        -------
        float
            Solved H2.
    """
    props = conductor_state_data(conductor_name)

    if w1 is None:
        w1 = props["w"]
    if w2 is None:
        w2 = w1

    return solve_for_H2(
        S=S,
        H1=H1,
        T1=T1,
        T2=T2,
        A_m2=props["A_m2"],
        E_kg_per_m2=props["E_kg_per_m2"],
        alpha=props["alpha"],
        w1=w1,
        w2=w2,
    )


def sag_old(S, H, w):
    """
        Parabolic sag approximation.

        Parameters
        ----------
        S : float or array-like
            Span length in meters.

        H : float or array-like
            Horizontal tension.

        w : float or array-like
            Unit weight [kg/m].

        Returns
        -------
        numpy.ndarray or float
            Parabolic sag:
                sag = w*S^2 / (8*H)
    """
    S = np.asarray(S, dtype=float)
    H = np.asarray(H, dtype=float)
    w = np.asarray(w, dtype=float)
    return w * S**2 / (8.0 * H)


def Th_from_sag_old(sag, S, w):
    """
        Inverse of the parabolic sag approximation.

        Returns
        -------
        numpy.ndarray or float
            Horizontal tension:
                H = w*S^2 / (8*sag)
    """
    sag = np.asarray(sag, dtype=float)
    S = np.asarray(S, dtype=float)
    w = np.asarray(w, dtype=float)
    return w * S**2 / (8.0 * sag)


def sag(S, H, w):
    """
        Exact catenary sag for an equal-height span.

        Parameters
        ----------
        S : float or array-like
            Span length in meters.

        H : float or array-like
            Horizontal tension.

        w : float or array-like
            Unit weight [kg/m].

        Returns
        -------
        numpy.ndarray or float
            Catenary sag for an equal-height span:
                sag = 2*a*sinh(S/(4*a))^2
            where a = H / w
    """
    S = np.asarray(S, dtype=float)
    H = np.asarray(H, dtype=float)
    w = np.asarray(w, dtype=float)

    a = H / w
    return 2.0 * a * np.sinh(S / (4.0 * a)) ** 2


def Th_from_sag(target_sag, S, w, tol=1e-10, max_iter=100):
    """
        Solve for horizontal tension from a known equal-height catenary sag.

        Parameters
        ----------
        target_sag : float
            Target sag in meters.

        S : float
            Span length in meters.

        w : float
            Unit weight [kg/m].

        tol : float, default 1e-10
            Absolute tolerance on sag error.

        max_iter : int, default 100
            Maximum number of bisection iterations.

        Returns
        -------
        float
            Horizontal tension H.
    """
    target_sag = float(target_sag)
    S = float(S)
    w = float(w)

    if target_sag <= 0.0:
        raise ValueError("target_sag must be positive.")

    def f(H):
        return float(sag_catenary_same_height(S, H, w) - target_sag)

    H_low = 1e-12
    H_high = w * S**2 / (8.0 * target_sag)

    while f(H_high) > 0.0:
        H_high *= 2.0

    for _ in range(max_iter):
        H_mid = 0.5 * (H_low + H_high)
        err = f(H_mid)

        if abs(err) < tol:
            return H_mid

        if err > 0.0:
            H_low = H_mid
        else:
            H_high = H_mid

    return H_mid


def distance_lowest_point_r(S, dh, H, w):
    """
        Horizontal distance from the right support to the lowest point logic's
        companion quantity used in the legacy formulas.

        Parameters
        ----------
        S : float or array-like
            Horizontal span length [m].

        dh : float or array-like
            Elevation difference h_R - h_L [m].

        H : float or array-like
            Horizontal tension.

        w : float or array-like
            Unit weight [kg/m].

        Returns
        -------
        numpy.ndarray or float
    """
    S = np.asarray(S, dtype=float)
    dh = np.asarray(dh, dtype=float)
    H = np.asarray(H, dtype=float)
    w = np.asarray(w, dtype=float)

    a = H / w
    return -a * np.arcsinh(dh / (2.0 * a * np.sinh(S / (2.0 * a)))) + S / 2.0


def distance_lowest_point_l(S, dh, H, w):
    """
    Horizontal distance from the left support to the lowest point logic's
    companion quantity used in the legacy formulas.
    """
    S = np.asarray(S, dtype=float)
    dh = -np.asarray(dh, dtype=float)
    H = np.asarray(H, dtype=float)
    w = np.asarray(w, dtype=float)

    a = H / w
    return -a * np.arcsinh(dh / (2.0 * a * np.sinh(S / (2.0 * a)))) + S / 2.0


def height_at_x(x, S, H, w, dh, y0):
    """
        Height of the catenary at horizontal coordinate x.

        Parameters
        ----------
        x : float or array-like
            Horizontal coordinate(s) measured from the left support.

        S : float or array-like
            Horizontal span length [m].

        H : float or array-like
            Horizontal tension.

        w : float or array-like
            Unit weight [kg/m].

        dh : float or array-like
            Elevation difference h_R - h_L [m].

        y0 : float or array-like
            Height at the left support reference level.

        Returns
        -------
        numpy.ndarray or float
    """
    x = np.asarray(x, dtype=float)
    S = np.asarray(S, dtype=float)
    H = np.asarray(H, dtype=float)
    w = np.asarray(w, dtype=float)
    dh = np.asarray(dh, dtype=float)
    y0 = np.asarray(y0, dtype=float)

    a = H / w
    xr = -a * np.arcsinh(dh / (2.0 * a * np.sinh(S / (2.0 * a)))) + S / 2.0
    return y0 + a * (np.cosh((x - xr) / a) - np.cosh(xr / a))


def monopleyro_right(S, dh, H, w, invalid="nan"):
    """
    Right-side unilateral load length helper from the legacy script.

    Parameters
    ----------
    invalid : {"nan", "zero"}, default "nan"
        How to represent non-existent unilateral lengths.
    """
    S = np.asarray(S, dtype=float)
    dh = np.asarray(dh, dtype=float)
    H = np.asarray(H, dtype=float)
    w = np.asarray(w, dtype=float)

    a = H / w
    val = -a * np.arcsinh(dh / (2.0 * a * np.sinh(S / (2.0 * a)))) - S / 2.0

    if invalid == "zero":
        return np.where(val > 0.0, val, 0.0)
    return np.where(val > 0.0, val, np.nan)


def monopleyro_left(S, dh, H, w, invalid="nan"):
    """
    Left-side unilateral load length helper from the legacy script.

    Parameters
    ----------
    invalid : {"nan", "zero"}, default "nan"
        How to represent non-existent unilateral lengths.
    """
    S = np.asarray(S, dtype=float)
    dh = -np.asarray(dh, dtype=float)
    H = np.asarray(H, dtype=float)
    w = np.asarray(w, dtype=float)

    a = H / w
    val = -a * np.arcsinh(dh / (2.0 * a * np.sinh(S / (2.0 * a)))) - S / 2.0

    if invalid == "zero":
        return np.where(val > 0.0, val, 0.0)
    return np.where(val > 0.0, val, np.nan)


def synoliko_katakoryfo(S_l, dh_l, H_l, w_l, S_r, dh_r, H_r, w_r):
    """
        Sum of the left and right lowest-point distance quantities from the
        legacy script.

        Parameters
        ----------
        S_l, dh_l, H_l, w_l
            Left-span values.

        S_r, dh_r, H_r, w_r
            Right-span values.

        Returns
        -------
        numpy.ndarray or float
    """
    return (
        distance_lowest_point_r(S_r, dh_r, H_r, w_r)
        + distance_lowest_point_l(S_l, dh_l, H_l, w_l)
    )



def main():
    """
    Small standalone demo for manual CLI testing.

    Run with:
        python -m tabu_scripts.state_equation
    """
    props = conductor_state_data("Cardinal")

    H2 = solve_for_H2(
        S=350.0,
        H1=2585.0,
        T1=50.0,
        T2=0.0,
        A_m2=props["A_m2"],
        E_kg_per_m2=props["E_kg_per_m2"],
        alpha=props["alpha"],
        w1=props["w"],
    )

    print("Conductor:", props["name"])
    print("Solved H2:", H2)


if __name__ == "__main__":
    main()