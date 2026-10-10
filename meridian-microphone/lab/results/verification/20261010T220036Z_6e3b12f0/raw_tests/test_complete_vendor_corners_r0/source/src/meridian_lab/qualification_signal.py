# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from itertools import product
import numpy as np

from .core import SimulationError
from .metrics import at_frequency, db, device_noise_totals, harmonic_spectrum, integrate_asd


def noise(sim, ctx):
    raw = sim.noise()
    f = raw["frequency"].real
    ac = ctx["nominal"]["ac.raw"]
    gain = np.array([abs(at_frequency(ac["frequency"], ac.voltage("pp", "pn"), x)) for x in f])
    if np.any(gain < 1e-12):
        raise SimulationError("Cannot refer noise through zero capsule transfer")
    # ngspice noise vectors contain both per-element totals and sub-contributions.
    # Include each element total once; never add thermal/flicker children again.
    totals = device_noise_totals(raw)
    groups = {}
    matched = set()
    for group, prefixes in sim.meta.get("noise_groups", {}).items():
        keys = [k for k in totals if any(k.startswith(prefix) for prefix in prefixes)]
        if matched.intersection(keys):
            raise ValueError("Overlapping noise groups would double count noise")
        matched.update(keys)
        density = np.sqrt(sum((totals[k] ** 2 for k in keys), np.zeros_like(f)))
        groups[group] = {
            "output_v_rms": integrate_asd(f, density),
            "pa_rms": integrate_asd(f, density / gain),
            "vectors": keys,
        }
    # Classification is explicit: DUT = electronics, capsule leakage = electrical surrogate,
    # environment = feed/cable/preamp load Johnson noise, excluded from microphone electronics.
    internal = np.sqrt(sum((v**2 for k, v in totals.items() if ".xdut." in k), np.zeros_like(f)))
    external = np.sqrt(sum((v**2 for k, v in totals.items() if ".xenv." in k), np.zeros_like(f)))
    sum_density = np.sqrt(sum((v**2 for v in totals.values()), np.zeros_like(f)))
    total = raw["onoise_spectrum"].real
    closure = float(np.max(np.abs(sum_density - total) / np.maximum(total, 1e-30)))
    if closure > 1e-5:
        raise SimulationError(f"Noise contribution power does not close: relative error {closure}")
    if not any(".xdut." in k for k in totals):
        raise SimulationError(
            "No DUT noise sources were extracted; cannot claim zero electronics noise"
        )
    pa = integrate_asd(f, internal / gain)
    paw = integrate_asd(f, internal / gain, True)
    s = sim.params["SREF"] * ctx["polarization_dc_v"] / sim.params["VREF"]
    ein = pa * s
    dba = db(paw / 20e-6)
    m = {
        "band_hz": [float(f[0]), float(f[-1])],
        "electronics_noise_pa_rms": pa,
        "electronics_noise_a_pa_rms": paw,
        "electronics_noise_dba_conditional": dba,
        "electronics_ein_v_rms_conditional": ein,
        "electronics_output_v_rms": integrate_asd(f, internal),
        "environment_output_v_rms": integrate_asd(f, external),
        "full_fixture_output_v_rms": integrate_asd(f, total),
        "noise_power_closure_relative_error": closure,
        "groups": groups,
        "unclassified_vectors": sorted(set(totals) - matched),
        "frequency_hz": f.tolist(),
        "electronics_output_asd_v_per_sqrt_hz": internal.tolist(),
        "full_fixture_asd_v_per_sqrt_hz": total.tolist(),
        "mechanical_capsule_noise_included": False,
        "semiconductor_noise_validated": False,
    }
    ok = (
        ein <= thresholds()["electronics_ein_unweighted_v_rms"]["value"]
        and dba <= thresholds()["electronics_noise_dba"]["value"]
    )
    return result(
        "pass" if ok else "fail",
        m,
        coverage="Resistive fixture noise; conditional capsule sensitivity. Semiconductor and capsule mechanical noise unresolved.",
    )


def distortion(sim, ctx):
    rows = []
    for f, level in product([100, 1000, 10000], [1.0, 20e-6 * 10 ** (135 / 20)]):
        wave = sim.transient(
            f,
            level * np.sqrt(2),
            settling=0.5,
            overrides={"LIN": 1, "POLDC": ctx["polarization_dc_v"]},
        )
        m = harmonic_spectrum(wave["time"], wave.voltage("pp", "pn"), f)
        # Compare final two coherent windows to detect incomplete settling.
        cut = wave["time"].real[-1] - 16 / f
        earlier = wave["time"].real <= cut
        prior = harmonic_spectrum(
            wave["time"].real[earlier], wave.voltage("pp", "pn").real[earlier], f
        )
        change = abs(prior["harmonics_v_rms"][0] / m["harmonics_v_rms"][0] - 1)
        m.update(
            pressure_pa_rms=level,
            pressure_spl_db=db(level / 20e-6),
            settling_amplitude_fraction=float(change),
            capsule_mode="linearized_at_actual_DC_bias",
        )
        if change > 1e-3:
            raise SimulationError(
                "Unsettled distortion waveform; extend simulation instead of accepting THD"
            )
        limit = thresholds()["thd_at_1pa_percent" if level == 1 else "thd_at_135db_percent"][
            "value"
        ]
        m["status"] = "pass" if m["thd_percent"] <= limit else "fail"
        rows.append(m)
    return result(
        "pass" if all(x["status"] == "pass" for x in rows) else "fail",
        {"cases": rows, "thd_percent": max(x["thd_percent"] for x in rows)},
        coverage="Electronics under linearized imposed capsule motion; nominal only. Device/environment distortion corners remain pending.",
    )


def headroom(sim, ctx):
    rows = ctx["checks"]["distortion"]["metrics"].get("cases", [])
    rows = [r for r in rows if r["frequency_hz"] == 1000]
    if not rows:
        return result("incomplete", reason="No valid distortion bracket")
    limit = thresholds()["thd_at_135db_percent"]["value"]
    passes = [r for r in rows if r["thd_percent"] <= limit]
    failures = [r for r in rows if r["thd_percent"] > limit]
    lower = max((r["pressure_pa_rms"] for r in passes), default=0)
    upper = min(
        (r["pressure_pa_rms"] for r in failures if r["pressure_pa_rms"] > lower), default=None
    )
    if upper is not None:
        for _ in range(8):
            level = np.sqrt(lower * upper) if lower else upper / 2
            wave = sim.transient(
                1000,
                level * np.sqrt(2),
                settling=0.5,
                overrides={"LIN": 1, "POLDC": ctx["polarization_dc_v"]},
            )
            h = harmonic_spectrum(wave["time"], wave.voltage("pp", "pn"), 1000)
            if h["thd_percent"] <= limit:
                lower = level
            else:
                upper = level
    return result(
        "pass" if lower >= 20e-6 * 10 ** (135 / 20) else "fail",
        {
            "headroom_lower_bound_pa_rms": float(lower),
            "first_failure_upper_bound_pa_rms": upper,
            "right_censored": upper is None,
            "headroom_pa_rms": None if upper is None else float(lower),
            "threshold_percent": limit,
            "frequency_hz": 1000,
            "system_max_spl_verified": False,
        },
        coverage="Bracketed electronics distortion boundary if a failure exists; otherwise lower bound only. Mechanical overload and device power pending.",
    )


from .qualification import result, thresholds
