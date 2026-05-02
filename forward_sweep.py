import numpy as np

def forward_sweep_from_H0(spans, heights, H0, w):
    """
    Propagate horizontal tensions span by span, starting from an assumed first-span
    horizontal tension ``H0``.

    Parameters
    ----------
    spans : array-like of float
        Horizontal span lengths in meters.

    heights : array-like of float
        Height differences in meters, one value per span.
        The sign convention is the same as in the existing solver:
        positive values mean the right support of that span is higher,
        negative values mean the right support is lower.

    H0 : float
        Assumed horizontal tension in the first span.

    w : float
        Conductor weight per unit length in kg/m.

    Returns
    -------
    dict
        Dictionary with:
        - "H": horizontal tension array, one value per span
        - "eq_span": equivalent same-height span used at each propagation step
        - "eq_sag": sag of the equivalent same-height span
        - "axial_next": axial-tension-like intermediate quantity used before
          converting to the next horizontal component
        --- commented out, but left for posterity
        --- "disc": discriminant values used in the next-step conversion

    Purpose
    -------
    This function performs one forward propagation through the line section.

    The outer solvers (bisection, N-R, etc) do not solve every span tension at once.
    Instead, they guess a first horizontal tension ``H0``, run this forward sweep,
    compute the total conductor length that results, and then compare that total
    length against the target reference length. The outer iteration then adjusts
    ``H0`` and repeats.

    In that sense, this function is the mechanical core of the whole algorithm.

    Basic step logic
    ----------------
    For each span ``i``, the function does the following:

    1. Υπολογίζει το (μεγάλο) ισοδύναμο ισοϋψές του κάθε ανοίγματος
           eq_span = s[i] + 2 * H[i] * abs(h[i]) / (s[i] * w)

    2. Εκτιμά το βέλος σε αυτό το ισοϋψές
           eq_sag = eq_span^2 * w / (8 * H[i])

    3. Βρίσκει την αξονική τάνυση στον δεξιά πύργο και την θεωρεί ίση με την αξονική 
       τάνυση του αριστερά πύργου του επόμενου ανοίγματος - δηλαδή του ίδιου ακριβώς 
       πύργου, απλά από την άλλη πλευρά.
       
    Μαθηματική απόδειξη του τύπου Ta = Th + w*sag
    ------------------------------------------------------------
    
        Ta = sqrt(Thorizontal^2 + Tvertical^2) = sqrt(Th^2 + Tv^2)
    
        Ta = Th * sqrt(1+ (Tv/Th)^2)
    
    όμως, από διωνυμικό θεώρημα
    
        (1+x)^α = 1 + α*x+ α*(α−1)​*x^2/2! + α*(α−1)*(α−2)*​x^3/3! + ⋯
    
    για x = (Tv/Th)^2, α = 1/2, και αγνοώντας τους όρους μεγαλύτερης τάξης
    
        Τa = Th * (1 + Tv^2/Th^2/2)
    
    όμως
    
        Τv = span * w / 2 (για ισοϋψές άνοιγμα)
    
    και
    
        Τh = span^2 * w / 8 / sag
    
    Με απλοποιήσεις των τριών τελευταίων τύπων, προκύπτει
    
                               Τa = Th + w * sag   

    Τρόπος υπολογισμού αξονικής τάνυσης δεξιά πύργου/ πρόσημα
    ------------------------------------------------------------
    The current propagation rule is intentionally asymmetric:

    - If ``heights[i] > 0``:
          axial_next = H[i] + w * eq_sag

    - If ``heights[i] <= 0``:
          axial_next = H[i] + w * (eq_sag + heights[i])
                        OR
          axial_next = H[i] + w * (eq_sag - abs(heights[i]))
                        
    Στην ουσία, αν υπάρχει αρνητική υψομετρική, ο δεξιά πύργος είναι χαμηλότερα.
    Άρα σε αυτόν υπάρχει μικρότερο Τv και, κατ΄ επέκταση, μικρότερο Τa.
    
    Συνεπώς, για να υπολογίσουμε το Τa σε αυτόν, πρέπει να πάρουμε το βέλος του
    μικρού ισοϋψούς. Η διαφορά μεταξύ του βέλους του μεγάλου και του βέλους του
    μικρού είναι ακριβώς όσο και η υψομετρική διαφορά του ανοίγματος.
    
    Τρόπος υπολογισμού οριζόντιας τάνυσης επόμενου ανοίγματος
    ------------------------------------------------------------
    Γνωρίζουμε την αξονική τάνυση στον αριστερά πύργο, άνοιγμα και υψομετρική.
    
    Εφαρμόζουμε ξανά την προσέγγιση του ισοδύναμου ισοϋψούς γι' αυτό το άνοιγμα.
    Αν h>0, τότε βάζουμε το μικρό. Αν h<0, τότε το μεγάλο.
    
    Βαριέμαι να τα γράψω τώρα όλα, βλέπε σημειώσεις Μάγειρα, σελ 89.
    
    Εν πάσει περιπτώσει, καταλήγουν και τα δύο σενάρια στον ίδιο τύπο:
    
        Τh = (Ta + w*h/2 + sqrt(Ta^2 + Ta*w*h - span^2*w^2/2)) / (2 + h^2/span^2)
              
    Όλα είναι γνωστά, άρα γνωρίζουμε το Τh του επόμενου ανοίγματος, καληνύχτα.
     
    Improvement avenues
    -------------------
    1. Replace the sag estimate with a higher-order or analytic catenary
       expression.

    2. Replace the equivalent same-height span shortcut with a true
       unequal-support catenary model.

    3. Replace the current next-span conversion with a catenary-consistent
       force-and-geometry relation.

    4. Re-derive the treatment of positive and negative support level differences
       from a single consistent formulation, instead of preserving the current
       branch rule as-is.
       
    5. Introduce the elastic influence of E, A into the final total length 
       convergence check. 

    Example usage
    -------
    >>> spans = [254.08, 385.0, 255.0, 485.0]
    >>> heights = [-57.13, -21.81, -5.28, 33.25]
    >>> out = forward_sweep_from_H0(spans, heights, H0=2026.0, w=1.303)
    >>> out["H"]
    array([...])

    Common usage
    ------------
    >>> out = forward_sweep_from_H0(spans, heights, H0_guess, w)
    >>> H_solution = out["H"]
    >>> total = total_length(spans, heights, H_solution, w)
    """

    s = np.asarray(spans, dtype=float)
    h = np.asarray(heights, dtype=float)

    n = len(s)
    
    H = np.empty(n)         # will end up becomeing H_solution
    H[0] = float(H0)

    eq_span = np.empty(n - 1)
    eq_sag = np.empty(n - 1)
    axial_next = np.empty(n - 1)
    #disc_arr = np.empty(n - 1)

    for i in range(n - 1):
        eq_span[i] = s[i] + (2.0 * H[i] * abs(h[i])) / (s[i] * w)
        eq_sag[i] = (eq_span[i] ** 2) * w / (8.0 * H[i])

        if h[i] > 0.0:
            axial_next[i] = H[i] + w * eq_sag[i]
        else:
            axial_next[i] = H[i] + w * (eq_sag[i] + h[i])

        denom = 2.0 + (h[i + 1] ** 2) / (s[i + 1] ** 2)

        disc = (
            axial_next[i] ** 2
            + axial_next[i] * w * h[i + 1]
            - 0.5 * (s[i + 1] ** 2) * (w ** 2)
        )

        if disc < 0.0:
            disc = 0.0

        #disc_arr[i] = disc   # optional for debugging

        H[i + 1] = (
            axial_next[i]
            + 0.5 * w * h[i + 1]
            + np.sqrt(disc)
        ) / denom

    return {
        "H": H,
        "eq_span": eq_span,
        "eq_sag": eq_sag,
        "axial_next": axial_next,
        #"disc": disc_arr,
    }