"""
    data.py
    =======

    Small data module for conductor properties and temperature-dependent reference
    tensions.

    Example
    -------
    >>> from data import select_conductor_data
    >>> info = select_conductor_data("Grosbeak", "BA 500")
    >>> info["w"]
    1.303
    >>> info["Tvec"]
    array([2026., 1989., 1953., 1919., 1885.])

    Another example, printing the available conductor names:

    >>> from data import available_conductors
    >>> available_conductors()
    ['Cardinal', 'Grosbeak', 'Linnet', 'SW150_0_396', 'SW150_0_460', 'SW400']
"""

import numpy as np

# list of temperatures for building tables
TEMPS = np.array([0.0, 10.0, 20.0, 30.0, 40.0])


# Central catalog of conductors.
#
# Stored values:
#   w            conductor weight per unit length [kg/m]
#   A_cm2        nominal cross sectional area [cm^2]
#   E_kg_per_m2  modulus of elasticity in the unit system already used by the
#                legacy-style formulas [kgf/m^2 or kp/m^2 compatible]
#   T350         reference tensions for BA 350 at the temperatures in TEMPS
#   T500         reference tensions for BA 500 at the temperatures in TEMPS

CONDUCTORS = {
    "Linnet": {
        "w": 0.7024,
        "A_cm2": 2.0,               # 1.998
        "E_kg_per_m2": 6.18e9,      # 6.184e9
        "alpha": 1.899e-5,
        "T350": np.array([1527.0, 1457.0, 1386.0, 1327.0, 1269.0]),
        "T500": np.array([1244.0, 1219.0, 1185.0, 1172.0, 1149.0]),
    },
    "Grosbeak": {
        "w": 1.303,
        "A_cm2": 3.71,
        "E_kg_per_m2": 6.18e9,      # 6.184e9
        "alpha": 1.899e-5,
        "T350": np.array([2183.0, 2102.0, 2028.0, 1960.0, 1893.0]),
        "T500": np.array([2026.0, 1989.0, 1953.0, 1919.0, 1885.0]),
    },
    "Cardinal": {
        "w": 1.823,
        "A_cm2": 5.46,
        "E_kg_per_m2": 5.132e9,
        "alpha": 1.935e-5,
        "T350": np.array([3480.0, 3332.0, 3185.0, 3065.0, 2945.0]),
        "T500": np.array([3105.0, 3045.0, 2980.0, 2925.0, 2870.0]),
    },
    "SW150_0_460": {
        "w": 0.46,
        "A_cm2": 0.55,
        "E_kg_per_m2": 19.334e9,
        "alpha": 1.152e-5,
        "T350": np.array([1118.0, 1074.0, 1031.0, 994.0, 957.0]),
        "T500": np.array([892.0, 876.0, 860.0, 846.0, 832.0]),
    },
    "SW150_0_396": {
        "w": 0.396,
        "A_cm2": 0.62,                  # uncertain
        "E_kg_per_m2": 14.56e9,         # uncertain
        "alpha": 1.152e-5,
        "T350": np.array([962.0, 925.0, 888.0, 856.0, 824.0]),
        "T500": np.array([768.0, 754.0, 740.0, 728.0, 716.0]),
    },
    "SW400": {
        "w": 0.769,
        "A_cm2": 0.965,
        "E_kg_per_m2": 14.56e10,
        "alpha": 1.152e-5,
        "T350": np.array([1810.0, 1740.0, 1670.0, 1610.0, 1550.0]),
        "T500": np.array([1520.0, 1495.0, 1470.0, 1445.0, 1420.0]),
    },
}

def select_conductor_data(conductor_name, ba_label):
    """
        Returns a single dictionary with the constants needed for one run.

        Example
        -------
        >>> info = select_conductor_data("SW400", "BA 350")
        >>> info["w"]
        0.769
        >>> info["Tvec"]
        array([1810., 1740., 1670., 1610., 1550.])

        Common pattern in a larger script
        ---------------------------------
        >>> # 1) ruling_span_m = ruling_span_value(spans)
        >>> # 2) ba_label = classify_ruling_span(ruling_span_m)
        >>> # 3) conductor = select_conductor_data("Grosbeak", ba_label)
    """
    
    data = CONDUCTORS[conductor_name]

    if ba_label == "BA 350":
        Tvec = np.array(data["T350"])
    elif ba_label == "BA 500":
        Tvec = np.array(data["T500"])
    else:
        raise ValueError("ba_label must be 'BA 350' or 'BA 500'")

    return {
        "name": conductor_name,
        "ba_label": ba_label,
        "w": float(data["w"]),
        "A_cm2": float(data["A_cm2"]),
        "E_kg_per_m2": float(data["E_kg_per_m2"]),
        "alpha": float(data["alpha"]),
        "Tvec": Tvec,
    }
    
    
def available_conductors():
    """
        Returns the conductor names stored in :data:`CONDUCTORS`.

        Purpose
        ------------------------
        A GUI or command-line tool often needs to show the conductor names in a
        dropdown or menu. Returning the names through one small function is simpler
        than repeating ``sorted(CONDUCTORS.keys())`` in several places.

        Example
        -------
        >>> available_conductors()
        ['Cardinal', 'Grosbeak', 'Linnet', 'SW150_0_396', 'SW150_0_460', 'SW400']
    """
    return sorted(CONDUCTORS.keys())

