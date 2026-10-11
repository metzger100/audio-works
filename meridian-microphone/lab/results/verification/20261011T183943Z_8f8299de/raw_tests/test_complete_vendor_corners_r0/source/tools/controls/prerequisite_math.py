# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent circuit/extraction oracles; no device qualification."""

import numpy as np


def synthetic(time, phase=0.0):
    angle = 2 * np.pi * 1000 * np.asarray(time) + phase
    x = np.sin(angle)
    y = x + 0.1 * x**2 + 0.04 * x**3
    for h in range(4, 11):
        y += 0.001 / h * np.sin(h * angle + 0.13 * h)
    return y


def synthetic_rms():
    return np.array([1.03, 0.05, 0.01, *(0.001 / np.arange(4, 11))]) / np.sqrt(2)


def rc_response(time, resistance=1000, capacitance=1e-6, onset=0.001):
    return 1 - np.exp(-np.maximum(np.asarray(time) - onset, 0) / (resistance * capacitance))


def noise_closure(raw):
    from meridian_lab.metrics import device_noise_totals

    roots = device_noise_totals(raw)
    if not roots:
        raise ValueError("Missing native noise contributions")
    power = sum(x**2 for x in roots.values())
    total = raw["onoise_spectrum"].real
    return float(np.max(abs(np.sqrt(power) - total) / np.maximum(total, 1e-30)))


def current_balance(raw, sources):
    currents = np.array([raw["i(" + name + ")"].real for name in sources])
    return float(np.max(abs(currents.sum(axis=0))) / max(float(np.max(abs(currents))), 1e-15))
