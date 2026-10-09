# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: GPL-3.0-or-later
"""Budgeted, single-axis optimization of explicitly scoped SPICE scenarios.

No probabilistic interpretation is assigned to guaranteed bounds. A scenario
optimum is neither an all-corner bound nor a qualified implementation.
"""

import numpy as np
from scipy.stats import binom

from .core import ROOT, read_yaml
from . import qualification as q


AXES = {
    "response": ("frequency_response", "response_deviation_db", "minimize", None),
    "current": ("operating_point", "current_a", "minimize", None),
    "noise": ("noise", "electronics_noise_pa_rms", "minimize", "validated_noise_models"),
    "distortion": ("distortion", "thd_percent", "minimize", "validated_nonlinear_models"),
    "headroom": ("headroom", "headroom_pa_rms", "maximize", "validated_nonlinear_models"),
    "loading": ("loading", "loading_loss_db", "minimize", "validated_loading_models"),
    "balance": ("balance", "impedance_mismatch_fraction", "minimize", "validated_port_models"),
    "drive": ("output_impedance", "output_impedance_ohm", "minimize", "validated_port_models"),
    "complexity": (None, "component_count", "minimize", "realized_component_count"),
}


def audit(meta, axis):
    """Fail closed for missing behaviors and incompatible analysis protocols."""
    if axis not in AXES:
        raise ValueError("Unknown separate objective axis")
    if meta.get("analysis_domain") == "periodic_mechanism_control":
        return {
            "allowed": False,
            "reason": "Periodic conversion needs a validated periodic objective protocol.",
        }
    required = AXES[axis][3]
    if required and required not in meta.get("qualification_evidence", []):
        return {"allowed": False, "reason": "Missing prerequisite: " + required}
    return {
        "allowed": True,
        "scope": "restricted model-conditional DC/AC research; no production ranking",
        "noise_ranking_allowed": "validated_noise_models" in meta.get("qualification_evidence", []),
        "manufacturing_evidence": False,
    }


def aggregate(rows, metric, mode="worst", percentile=95, direction="minimize"):
    """Adverse finite specimens stay; any absent/error sample invalidates objective."""
    values = [
        float(r[metric])
        for r in rows
        if isinstance(r.get(metric), (int, float)) and np.isfinite(r[metric])
    ]
    complete = len(values) == len(rows) and bool(rows) and all(r["status"] != "error" for r in rows)
    worst = (max(values) if direction == "minimize" else min(values)) if values else None
    if mode not in {"nominal", "worst", "scenario_percentile"}:
        raise ValueError("Use nominal, worst, or explicitly empirical scenario_percentile")
    value = None
    if complete:
        if mode == "nominal":
            value = values[0]
        elif mode == "worst":
            value = worst
        else:
            if not 50 <= percentile < 100:
                raise ValueError("Scenario percentile must be >=50 and <100")
            value = float(
                np.percentile(values, percentile if direction == "minimize" else 100 - percentile)
            )
    return {
        "value": value,
        "complete": complete,
        "samples": len(rows),
        "finite_samples": len(values),
        "missing_or_error_samples": len(rows)
        - sum(
            isinstance(r.get(metric), (int, float))
            and np.isfinite(r[metric])
            and r["status"] != "error"
            for r in rows
        ),
        "worst_observed": worst,
        "p95_scenario": float(np.percentile(values, 95)) if values else None,
        "interpretation": "finite tested scenarios only; no full-envelope bound or population percentile",
    }


def percentile_interval(values, percentile=95):
    """Distribution-free order-statistic CI under the declared IID scenario sampler.

    Null endpoints denote unbounded tails, not omitted adverse specimens.
    """
    values = sorted(float(v) for v in values if np.isfinite(v))
    n = len(values)
    if not n:
        return [None, None]
    low, high = binom.ppf([0.025, 0.975], n, percentile / 100).astype(int)
    return [values[low - 1] if low > 0 else None, values[high] if high < n else None]


def uncertainty_ranges(meta, design=None):
    ranges = q.scenario_ranges()
    # The original general screen omitted cross capacitance; preserve it here.
    ranges["CROSS"] = read_yaml(ROOT / "spec/capsule-model.yaml")["parameters"][
        "front_rear_stray_f"
    ]["range"]
    for key, definition in meta.get("population", {}).items():
        ranges[key] = list(definition["range"])
    for group in (design or {}).values():
        for target in group["targets"]:
            tolerance = group.get("tolerance_fraction")
            if tolerance is not None:
                center = meta["parameters"][target]["default"]
                ranges[target] = [center * (1 - tolerance), center * (1 + tolerance)]
    return ranges


def random_scenarios(meta, seed, count, design=None):
    rng = np.random.default_rng(seed)
    ranges = uncertainty_ranges(meta, design)
    log_keys = {"LEAK"} | {
        k for k, d in meta.get("population", {}).items() if d.get("distribution") == "log_uniform"
    }
    return [
        {
            "id": f"holdout_seed_{seed}_{i}",
            "kind": "IID artificial scenario design; not production",
            "parameters": {
                k: float(np.exp(rng.uniform(np.log(lo), np.log(hi))))
                if k in log_keys
                else float(rng.uniform(lo, hi))
                for k, (lo, hi) in ranges.items()
            },
        }
        for i in range(count)
    ]


def corner_scenarios(meta, design=None):
    ranges = uncertainty_ranges(meta, design)
    # One-at-a-time extremes plus combined opposite endpoints; no exhaustive claim.
    cases = [
        {"id": f"{k}_{side}", "kind": "bounded endpoint scenario", "parameters": {k: ends[i]}}
        for k, ends in ranges.items()
        if k not in meta.get("population", {})
        for i, side in enumerate(["low", "high"])
    ]
    cases += [
        {
            "id": "combined_" + side,
            "kind": "combined bounded stress",
            "parameters": {k: v[i] for k, v in ranges.items()},
        }
        for i, side in enumerate(["low", "high"])
    ]
    # Complete temperature-dependent files are used; semiconductor parameters are
    # never independently randomized. Vendor coupled JFE proposals remain stresses
    # with known limit failures, not certified process coverage.
    if any(m.startswith("jfe150") for m in meta.get("semiconductor_models", [])):
        for model in ["jfe150_weak", "jfe150_strong"]:
            cases.append(
                {
                    "id": model,
                    "kind": "complete coupled vendor proposal; fails library bounds; not production corner",
                    "model_replacement": model,
                    "parameters": {},
                }
            )
    return cases


def thermal_passive_scenarios(meta, bom):
    """Documented resistor TCR maxima as coupled endpoint stresses, never samples."""
    cases = []
    for temperature in q.scenario_ranges()["TEMP"]:
        for sign in [-1, 1]:
            parameters = {"TEMP": temperature}
            for part in bom.get("physical_parts", []):
                tcr = part.get("ratings", {}).get("tcr_ppm_per_C")
                key = part["reference"].upper() + "_VALUE"
                if tcr is None or key not in meta["parameters"]:
                    continue
                nominal = meta["parameters"][key]["default"]
                tolerance = part["tolerance_fraction"]
                parameters[key] = (
                    nominal
                    * (1 + sign * tolerance)
                    * (1 + sign * abs(temperature - 25) * tcr * 1e-6)
                )
            cases.append(
                {
                    "id": f"TCR_{temperature}_{sign}",
                    "kind": "coupled tolerance/TCR endpoint stress; cap temperature/noise laws unknown",
                    "parameters": parameters,
                }
            )
    return cases
