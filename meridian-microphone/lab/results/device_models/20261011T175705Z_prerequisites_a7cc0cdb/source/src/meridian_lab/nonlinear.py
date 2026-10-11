# SPDX-License-Identifier: GPL-3.0-or-later
"""Settled H1-H10 extraction with retained startup and two complete windows."""
import numpy as np
from .metrics import harmonic_spectrum


def settled_spectrum(time, voltage, frequency, settling, cycles=16, samples_per_cycle=256):
    t, y = np.asarray(time).real, np.asarray(voltage).real
    if len(t) < 2 or frequency <= 0 or settling < 0:
        raise ValueError("Invalid transient interval")
    if t[0] > 1e-12 / frequency:
        raise ValueError("Startup waveform was not retained")
    if t[-1] < settling + 2 * cycles / frequency - 1e-9 / frequency:
        raise ValueError("Two complete post-settling windows required")
    last = harmonic_spectrum(t, y, frequency, cycles, samples_per_cycle)
    cut = t[-1] - cycles / frequency
    # Interpolate the exact coherent boundary; adaptive solver times need not hit it.
    from scipy.interpolate import CubicSpline
    select = t < cut
    prior_t = np.append(t[select], cut)
    prior_y = np.append(y[select], CubicSpline(t, y)(cut))
    prior = harmonic_spectrum(prior_t, prior_y, frequency, cycles, samples_per_cycle)
    a, b = np.array(last["harmonics_v_rms"]), np.array(prior["harmonics_v_rms"])
    # Normalize every harmonic difference to H1; relative errors at a numerical zero
    # are meaningless. Preserve the existing 1e-3 settling acceptance budget.
    change = float(np.max(abs(a - b)) / a[0])
    dc_change = float(abs(np.mean(y[t >= cut]) - np.mean(prior_y[prior_t >= cut - cycles / frequency])))
    # Means on adaptive samples are diagnostic only, not an amplitude acceptance test.
    if change > 1e-3:
        raise ValueError("Unsettled harmonic waveform")
    last.update(settling_amplitude_fraction=float(abs(a[0] - b[0]) / a[0]),
                settling_harmonic_fraction=change,
                adaptive_mean_change_v_diagnostic=dc_change,
                startup_retained=True, settling_s=settling,
                fitted_interval_s=[float(cut), float(t[-1])],
                prior_interval_s=[float(cut - cycles / frequency), float(cut)],
                window_cycles=cycles, samples_per_cycle=samples_per_cycle)
    return last
