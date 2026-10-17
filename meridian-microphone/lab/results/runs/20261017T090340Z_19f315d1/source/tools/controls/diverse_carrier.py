# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit seeded LPTV bridge oracle; no native periodic transistor-noise claim."""

import numpy as np
from scipy.signal import lfilter, welch
from scipy.stats import t as student_t

from meridian_lab.architectures import coherent_amplitudes, periodic_frequencies
from meridian_lab.core import write_json


def covariance_power(a, r, variance, omega):
    """Time-averaged m=2cos covariance summed as an infinite geometric series."""
    z = a * r
    return 2 * variance * (1 - a) / (1 + a) * (1 - z * z) / (1 - 2 * z * np.cos(omega) + z * z)


def shifted_psd(f, fs, a, r, variance, fc=100000):
    """Two-sided stationary AR spectrum, translated twice, then RC recursion."""

    def source(x):
        return variance * (1 - r * r) / fs / (1 + r * r - 2 * r * np.cos(2 * np.pi * x / fs))

    h2 = (1 - a) ** 2 / (1 + a * a - 2 * a * np.cos(2 * np.pi * f / fs))
    return (source(f - fc) + source(f + fc)) * h2


def seeded_control(folder, plan):
    rows, aggregates = [], []
    tau, fc, s0, rho = 1e-4, 100000, 1e-16, 0.6
    rawdir = folder / "seeded"
    rawdir.mkdir()
    for fs in plan["tracks"]["carrier"]["sample_rates_hz"]:
        a = np.exp(-1 / (fs * tau))
        omega = 2 * np.pi * fc / fs
        for n in plan["tracks"]["carrier"]["numerical_sizes"]:
            for color in ["white", "colored_10khz"]:
                r = 0 if color == "white" else np.exp(-2 * np.pi * 10000 / fs)
                # Each arm has one-sided low-frequency PSD S0; shared source makes rho.
                variance = s0 * fs / 2 * (1 - r) / (1 + r)
                diff_variance = 2 * (1 - rho) * variance
                expected = covariance_power(a, r, diff_variance, omega)
                values = []
                for seed in plan["tracks"]["carrier"]["seeds"]:
                    rng = np.random.default_rng(seed)
                    # Burn-in >20 RC time constants for output and AR source, retained.
                    burn = int(20 * tau * fs)
                    size = n + burn
                    z1, z2 = rng.standard_normal((2, size))
                    noise1 = lfilter([np.sqrt(variance * (1 - r * r))], [1, -r], z1)
                    noise2 = lfilter(
                        [np.sqrt(variance * (1 - r * r))],
                        [1, -r],
                        rho * z1 + np.sqrt(1 - rho * rho) * z2,
                    )
                    bridge = noise1 - noise2
                    tt = np.arange(size) / fs
                    mixer = 2 * np.cos(2 * np.pi * fc * tt)
                    output = lfilter([1 - a], [1, -a], bridge * mixer)
                    off = lfilter([1 - a], [1, -a], bridge)
                    y = output[burn:]
                    power = float(np.mean(y * y))
                    values.append(power / expected)
                    freq, pxx = welch(
                        y,
                        fs=fs,
                        window="hann",
                        nperseg=16384,
                        noverlap=0,
                        detrend=False,
                        scaling="density",
                    )
                    _, box = welch(
                        y,
                        fs=fs,
                        window="boxcar",
                        nperseg=16384,
                        noverlap=0,
                        detrend=False,
                        scaling="density",
                    )
                    # DFT/Parseval independent of recursion power estimator.
                    parseval = float(
                        np.sum(abs(np.fft.rfft(y)) ** 2 * np.r_[1, np.full(len(y) // 2 - 1, 2), 1])
                        / len(y) ** 2
                    )
                    grid = np.arange(131072) * fs / 131072
                    spectral_power = float(np.mean(shifted_psd(grid, fs, a, r, diff_variance)) * fs)
                    theory_one = 2 * shifted_psd(freq, fs, a, r, diff_variance)
                    mask = (freq >= 20) & (freq <= 20000)
                    expected_off = diff_variance * (1 - a) / (1 + a) * (1 + a * r) / (1 - a * r)
                    row = dict(
                        fs_hz=fs,
                        samples=n,
                        seed=seed,
                        color=color,
                        rho=rho,
                        source_low_frequency_psd_v2_hz=s0,
                        source_variance_v2=variance,
                        source_measured_variance_ratio=float(np.var(noise1[burn:]) / variance),
                        correlation_measured=float(np.corrcoef(noise1[burn:], noise2[burn:])[0, 1]),
                        mean_square_v2=power,
                        expected_v2=float(expected),
                        ratio=power / expected,
                        spectral_oracle_relative_error=float(abs(spectral_power / expected - 1)),
                        parseval_relative_error=float(abs(parseval / power - 1)),
                        carrier_off_ratio=float(np.mean(off[burn:] ** 2) / expected_off),
                        welch_band_power_v2=float(np.trapezoid(pxx[mask], freq[mask])),
                        expected_band_power_v2=float(np.trapezoid(theory_one[mask], freq[mask])),
                        boxcar_band_power_v2=float(np.trapezoid(box[mask], freq[mask])),
                        burn_samples=burn,
                        burn_s=burn / fs,
                        window_enbw_hz=1.5 * fs / 16384,
                        nonoverlapping_segments=n // 16384,
                        confidence="Per-bin approximate DOF=2K for stationary Gaussian surrogate only; LPTV bins correlated; use independent-seed t interval for total power",
                    )
                    name = f"{fs}_{n}_{color}_{seed}"
                    np.savez_compressed(
                        rawdir / (name + ".npz"),
                        time=tt,
                        arm1=noise1,
                        arm2=noise2,
                        mixer=mixer,
                        output=output,
                        carrier_off=off,
                        psd_frequency=freq,
                        hann_psd=pxx,
                        boxcar_psd=box,
                    )
                    write_json(rawdir / (name + ".json"), row)
                    rows.append(row)
                mean = float(np.mean(values))
                half = float(
                    student_t.ppf(0.975, len(values) - 1)
                    * np.std(values, ddof=1)
                    / np.sqrt(len(values))
                )
                aggregates.append(
                    dict(
                        fs_hz=fs,
                        samples=n,
                        color=color,
                        mean_ratio=mean,
                        independent_seed_95percent_interval=[mean - half, mean + half],
                        finite_screen_pass=abs(mean - 1) < 0.1,
                    )
                )
    # Exact common-mode cancellation shares the identical source bytes, not two new draws.
    zero = float(np.max(abs((noise1 - noise1) * mixer)))
    return dict(
        rows=rows,
        aggregate=aggregates,
        zero_shared_source_output=zero,
        continuous_white_limit_v2=float(2 * (1 - rho) * s0 / (2 * tau)),
        scope="Ideal seeded discrete LPTV oracle only; no native periodic device noise, P48 current, oscillator/mixer hardware or capsule rating",
    )


def islands(exp):
    rows = []
    include = exp.folder / "source/models/capsule/flat-k47.cir"
    for pressure, carrier, density in [(0, 0.2, 32), (1, 0, 32), (1, 0.2, 32), (1, 0.2, 64)]:
        circuit = f""".include "{include}"
Vrf bb 0 DC 40 SIN(40 {carrier} 100k)
Vanti aa 0 DC 40 SIN(40 {-carrier} 100k)
Vpressure pf 0 SIN(0 {pressure} 1k)
Vrearpressure pr 0 0
Xisland ff bb rr pf pr 0 FLAT_K47 CF=70p CR=70p PAR=1f CROSS=1f LEAK=1e14
Ccomparef ff aa 100p
Ccomparer rr aa 100p
Rreturnf ff 0 1e12
Rreturnr rr 0 1e12
Bproduct dd 0 V=2*(v(ff)-v(rr))*sin(2*pi*100k*time)
Rlp dd recovered 1k
Clp recovered 0 100n"""
        step = 1 / (100000 * density)
        raw = exp.execute(
            dict(id="carrier_island"),
            f"{pressure}_{carrier}_{density}",
            circuit,
            f"tran {step} .03 0 {step}\nwrite tran.raw time v(ff) v(rr) v(recovered)",
            ["tran.raw"],
        )
        row = dict(
            pressure_peak_pa=pressure,
            carrier_peak_v=carrier,
            density=density,
            status="unsupported" if raw is None else "executed",
        )
        if raw:
            d = raw["tran.raw"]
            t = d["time"].real
            mask = t >= 0.02
            frequencies = periodic_frequencies(100000, 1000)
            amp = coherent_amplitudes(t[mask], d["v(recovered)"][mask], frequencies)
            side = coherent_amplitudes(t[mask], d.voltage("ff", "rr")[mask], frequencies)
            expected_side = 0.2 * 70e-12 * 100e-12 / (170e-12) ** 2 * (0.02 / 60)
            expected_out = 2 * expected_side / np.sqrt(1 + (2 * np.pi * 1000 * 1e-4) ** 2)
            row.update(
                sidebands_peak_v=side,
                demod_peak_v=amp,
                expected_demod_peak_v=float(expected_out),
                recovered_ratio=amp["1000"] / expected_out,
            )
        rows.append(row)
    return rows
