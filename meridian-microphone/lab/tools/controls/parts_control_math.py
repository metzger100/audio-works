# SPDX-License-Identifier: GPL-3.0-or-later
import numpy as np


def nf_db(f, density, resistance, temperature):
    """Total input-referred PSD / independently known source Johnson PSD."""
    if resistance <= 0 or temperature <= 0:
        raise ValueError("Physical reference required")
    power = np.trapezoid(np.asarray(density) ** 2, np.asarray(f))
    return float(
        10 * np.log10(power / (4 * 1.380649e-23 * temperature * resistance * (f[-1] - f[0])))
    )


def capacitance(current, frequency):
    return float(np.imag(current) / (2 * np.pi * frequency))
