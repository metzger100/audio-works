"""Numerical measurements with explicit units and deterministic estimators."""
import numpy as np


def a_weighting(f):
    f = np.asarray(f, dtype=float)
    f2 = f * f
    ra = (12194.0**2 * f2**2) / ((f2 + 20.6**2) * np.sqrt((f2 + 107.7**2) * (f2 + 737.9**2)) * (f2 + 12194.0**2))
    return ra * 10**(2.0 / 20)


def integrate_asd(f, asd, weighted=False):
    f, asd = np.asarray(f).real, np.asarray(asd).real
    if len(f) < 2 or not np.all(np.diff(f) > 0) or np.any(asd < 0) or not np.isfinite(asd).all():
        raise ValueError('Invalid noise spectrum')
    weight = a_weighting(f) if weighted else np.ones_like(f)
    return float(np.sqrt(np.trapezoid((asd * weight)**2, f)))


def db(value):
    return float(20 * np.log10(max(abs(value), 1e-300)))


def at_frequency(f, values, frequency):
    f = np.asarray(f).real
    values = np.asarray(values)
    if not f[0] <= frequency <= f[-1]:
        raise ValueError('Interpolation outside analyzed frequencies')
    logf = np.log(f)
    if np.iscomplexobj(values):
        return np.interp(np.log(frequency), logf, values.real) + 1j * np.interp(np.log(frequency), logf, values.imag)
    return np.interp(np.log(frequency), logf, values)


def harmonic_spectrum(time, voltage, frequency, cycles=16, samples_per_cycle=256, harmonics=10):
    """Coherent uniform resampling plus least-squares harmonic fit; adaptive SPICE grids are not FFT grids."""
    time, voltage = np.asarray(time).real, np.asarray(voltage).real
    end = time[-1]
    duration = cycles / frequency
    if time[0] > end - duration or harmonics >= samples_per_cycle / 2:
        raise ValueError('Insufficient settled waveform or harmonic Nyquist coverage')
    t = end - duration + np.arange(cycles * samples_per_cycle) / frequency / samples_per_cycle
    if not np.all(np.diff(time)>0) or not np.isfinite(voltage).all():
        raise ValueError('Nonmonotonic or nonfinite transient samples')
    from scipy.interpolate import CubicSpline
    # Linear interpolation on a nonuniform grid can create spurious odd harmonics.
    # Cubic interpolation is still subject to timestep refinement, especially at clipping.
    y = CubicSpline(time, voltage, extrapolate=False)(t)
    basis = [np.ones_like(t)]
    for h in range(1, harmonics + 1):
        basis += [np.sin(2*np.pi*h*frequency*t), np.cos(2*np.pi*h*frequency*t)]
    matrix = np.column_stack(basis)
    coefficients, *_ = np.linalg.lstsq(matrix, y, rcond=None)
    peak = np.hypot(coefficients[1::2], coefficients[2::2])
    if peak[0] < 1e-12:
        raise ValueError('No measurable fundamental; not a distortion pass')
    residual = float(np.sqrt(np.mean((y - matrix @ coefficients)**2)))
    return {'frequency_hz': frequency, 'harmonics_v_rms': (peak / np.sqrt(2)).tolist(),
            'harmonics_dbc': [db(x / peak[0]) for x in peak], 'h2_percent': float(100 * peak[1] / peak[0]),
            'h3_percent': float(100 * peak[2] / peak[0]), 'thd_percent': float(100*np.linalg.norm(peak[1:])/peak[0]),
            'residual_v_rms': residual, 'output_peak_v': float(np.max(np.abs(y-np.mean(y)))),
            'method': 'Settled coherent cubic-spline resampling; least-squares H1-H10; residual reported separately from THD'}


def device_noise_totals(raw):
    """Per-device roots once, excluding every listed sub-contribution.

    SPICE lists BJT/MOS current/resistance/flicker children as well as a total.
    A power-closure test in qualification rejects ambiguous/missing classifications.
    """
    candidates={k:v.real for k,v in raw.vectors.items() if k.startswith('onoise_') and k!='onoise_spectrum'}
    return {k:v for k,v in candidates.items() if not any(k.startswith(parent+'_') for parent in candidates if parent!=k)}


def population_summary(records, metric):
    values = [r[metric] for r in records if r.get('status') == 'pass' and metric in r]
    # Failure count is always included in the denominator; no conditioning yield on convergence.
    passes = sum(r.get('status') == 'pass' for r in records)
    n = len(records)
    # Exact binomial Clopper-Pearson two-sided interval, not an assertion of real manufacturing yield.
    from scipy.stats import beta
    interval = [float(beta.ppf(0.025, passes, n-passes+1)) if passes else 0.0,
                float(beta.ppf(0.975, passes+1, n-passes)) if passes < n else 1.0] if n else [0, 1]
    out = {'samples': n, 'passing': passes, 'observed_pass_fraction': passes/n if n else None,
           'binomial_95_interval': interval, 'failures': n-passes,
           'yield_claim': False, 'reason': 'Assumed scenario distributions and screening coverage; real production statistics unknown.'}
    if values:
        out.update(median=float(np.median(values)), p95=float(np.percentile(values, 95)), p99=float(np.percentile(values, 99)), worst_observed=float(np.max(values)), metric=metric, statistics_conditioned_on_successful_simulation=True)
    return out
