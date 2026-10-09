# SPDX-License-Identifier: GPL-3.0-or-later
"""Budgeted, single-axis optimization of explicitly scoped SPICE scenarios.

No probabilistic interpretation is assigned to guaranteed bounds. A scenario
optimum is neither an all-corner bound nor a qualified implementation.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import uuid

import numpy as np
from scipy.optimize import differential_evolution

from .core import (
    ROOT,
    environment_versions,
    read_yaml,
    source_manifest,
    spec_digest,
    verify_spec_lock,
    write_json,
)
from .cli import implementation_manifest
from .metrics import population_summary


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


class BudgetExhausted(RuntimeError):
    pass


def optimize(
    candidate,
    definition,
    budget=12,
    seed=34047,
    axis="response",
    mode="worst",
    scenarios=None,
    percentile=95,
):
    verify_spec_lock()
    if budget < 6:
        raise ValueError("Budget must include nominal plus at least five initial points")
    meta = read_yaml(ROOT / "candidates" / candidate / "topology.yaml")
    prerequisite = audit(meta, axis)
    experiment = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_robust_" + uuid.uuid4().hex[:8]
    )
    directory = ROOT / "results/runs" / experiment
    directory.mkdir(parents=True, exist_ok=False)
    manifest, implementation = freeze(directory, candidate)
    parent_file = ROOT / "candidates" / candidate / "results.json"
    parent = read_yaml(parent_file)["latest_experiment"] if parent_file.exists() else None
    scenarios = scenarios or [
        {"id": "nominal", "parameters": {}, "kind": "nominal"},
        {
            "id": "training_supply_low",
            "parameters": {"VS": 44, "FT": 0.20},
            "kind": "supply bounded stress",
        },
        {
            "id": "training_supply_high",
            "parameters": {"VS": 52, "FT": -0.20},
            "kind": "supply bounded stress",
        },
    ]
    if mode == "nominal":
        scenarios = scenarios[:1]
    for group in definition.values():
        lo, hi = group["range"]
        if not (0 < lo < hi) or not group.get("rationale"):
            raise ValueError("Positive physically justified bounds required")
        for target in group["targets"]:
            if target not in meta["parameters"]:
                raise ValueError("Undeclared topology parameter: " + target)
    base = {
        "schema_version": 2,
        "experiment_id": experiment,
        "candidate_id": candidate,
        "parent_experiments": [parent] if parent else [],
        "axis": axis,
        "aggregation": mode,
        "percentile": percentile if mode == "scenario_percentile" else None,
        "prerequisite_audit": prerequisite,
        "budget_declared_before_run": budget,
        "seed": seed,
        "design_parameters": definition,
        "hard_constraints": [
            "DC energy closure/current/positive rail/positive polarization",
            "response <= frozen 1dB for each tested scenario",
        ],
        "training_scenarios": scenarios,
        "source_manifest": manifest,
        "implementation_manifest": implementation,
        "suite_sha256": hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
        "spec_sha256": spec_digest(),
        "versions": environment_versions(),
        "eligible": False,
        "global_optimality": False,
        "manufacturing_yield": None,
        "patent_state": meta.get("patent_state", "unscreened"),
        "procurement_state": meta.get("procurement_state", "unknown"),
    }
    write_json(directory / "plan.json", base)
    started = time.monotonic()
    trials, cache = [], {}
    keys = list(definition)
    bounds = [tuple(np.log(definition[k]["range"])) for k in keys]
    metric = AXES[axis][1]
    direction = AXES[axis][2]

    def evaluate(x):
        key = tuple(float(v) for v in x)
        if key in cache:
            return cache[key]
        if len(trials) >= budget:
            raise BudgetExhausted()
        values = {k: float(np.clip(np.exp(v), *definition[k]["range"])) for k, v in zip(keys, x)}
        overrides = {t: values[k] for k in keys for t in definition[k]["targets"]}
        folder = directory / f"trial_{len(trials):05d}"
        folder.mkdir()
        rows = measure(candidate, folder, directory, overrides, scenarios, axis)
        summary = aggregate(rows, metric, mode, percentile, direction)
        item = {
            "trial": len(trials),
            "design_values": values,
            "parameters": overrides,
            "cases": rows,
            "objective": summary,
            "screen_feasible": all(r["status"] == "pass" for r in rows),
        }
        write_json(folder / "trial.json", item)
        trials.append(item)
        value = summary["value"]
        # No weighted penalty: response itself guides search from the infeasible
        # region; acceptance constraints are applied separately to every scenario.
        score = (
            float(value) * (1 if direction == "minimize" else -1) if value is not None else np.inf
        )
        cache[key] = score
        return score

    termination = "prerequisite_hold"
    answer = None
    if prerequisite["allowed"]:
        nominal = [np.log(meta["parameters"][definition[k]["targets"][0]]["default"]) for k in keys]
        evaluate(nominal)
        rng = np.random.default_rng(seed)
        # Deterministic endpoints and interior points seed a bounded DE run.
        init = np.array(
            [
                [lo for lo, hi in bounds],
                [hi for lo, hi in bounds],
                [(lo + hi) / 2 for lo, hi in bounds],
                *[[rng.uniform(lo, hi) for lo, hi in bounds] for _ in range(3)],
            ]
        )
        if all(r["status"] == "error" for r in trials[0]["cases"]):
            termination = "nominal_integration_failure_hold; remaining budget unused"
        else:
            try:
                answer = differential_evolution(
                    evaluate,
                    bounds,
                    init=init,
                    maxiter=budget,
                    rng=rng,
                    polish=False,
                    tol=1e-7,
                    atol=0,
                )
                termination = "scipy_convergence" if answer.success else "scipy_iteration_limit"
            except BudgetExhausted:
                termination = "evaluation_budget_exhausted"
    feasible = [t for t in trials if t["screen_feasible"] and t["objective"]["complete"]]
    best = (
        (min if direction == "minimize" else max)(feasible, key=lambda t: t["objective"]["value"])
        if feasible
        else None
    )
    finite = [t for t in trials if t["objective"]["value"] is not None]
    diagnostic = (
        (min if direction == "minimize" else max)(finite, key=lambda t: t["objective"]["value"])
        if finite
        else None
    )
    unchanged = (
        source_manifest() == manifest
        and implementation_manifest(ROOT / "candidates" / candidate) == implementation
    )
    record = {
        **base,
        "status": "proposal_requires_full_suite"
        if best and unchanged
        else "no_feasible_tested_proposal"
        if unchanged and prerequisite["allowed"]
        else "prerequisite_hold"
        if unchanged
        else "source_integrity_error",
        "termination": termination,
        "scipy_success": bool(answer.success) if answer else False,
        "scipy_message": str(answer.message) if answer else None,
        "evaluations": len(trials),
        "trial_failures": sum(not t["screen_feasible"] for t in trials),
        "scenario_attempts": sum(len(t["cases"]) for t in trials),
        "analysis_errors": sum(r["status"] == "error" for t in trials for r in t["cases"]),
        "runtime_s": time.monotonic() - started,
        "best": best,
        "diagnostic_best_infeasible": diagnostic if best is None else None,
        "source_unchanged": unchanged,
        "full_suite_experiment": None,
        "note": "No feasible tested point is not a proof that the full value region is infeasible.",
    }
    write_json(directory / "optimization.json", record)
    write_json(directory / "trials.json", trials)
    if best:
        write_json(directory / "proposed_parameters.json", best["parameters"])
    return record


def validate(candidate, overrides, directory, seed, samples=16, design=None):
    directory = Path(directory)
    directory.mkdir(exist_ok=False)
    manifest, implementation = freeze(directory, candidate)
    meta = read_yaml(directory / "candidate/topology.yaml")
    # Center tolerances on the continuous design instead of the original BOM.
    for key, value in overrides.items():
        if key in meta["parameters"]:
            meta["parameters"][key]["default"] = value
    corners = corner_scenarios(meta, design) + thermal_passive_scenarios(
        meta, read_yaml(directory / "candidate/bom.yaml")
    )
    random = random_scenarios(meta, seed, samples, design)
    rows = measure(candidate, directory / "corners", directory, overrides, corners)
    random_rows = measure(candidate, directory / "independent_random", directory, overrides, random)
    summary = population_summary(random_rows, "response_deviation_db")
    values = [
        r["response_deviation_db"]
        for r in random_rows
        if r["status"] in {"pass", "fail"} and "response_deviation_db" in r
    ]
    summary.update(
        percentile_95_interval=percentile_interval(values)
        if len(values) == samples
        else [None, None],
        percentile_interval_incomplete_reason=None
        if len(values) == samples
        else "Missing/failed analyses prevent unconditional metric interval; finite conditional descriptive percentiles retained",
        confidence_scope="IID artificial scenario sampler only; no production/yield interpretation; missing analyses unresolved",
    )
    record = {
        "candidate_id": candidate,
        "parameters": overrides,
        "seed": seed,
        "corner_summary": aggregate(rows, "response_deviation_db"),
        "corners": rows,
        "random_summary": summary,
        "random_cases": random_rows,
        "source_manifest": manifest,
        "implementation_manifest": implementation,
        "spec_sha256": spec_digest(),
        "source_unchanged": source_manifest() == manifest
        and implementation_manifest(ROOT / "candidates" / candidate) == implementation,
        "coverage": "DC/AC only; library vendor-corner disagreements preserved; not all-requirement robustness",
        "manufacturing_evidence": False,
        "eligible": False,
    }
    write_json(directory / "validation.json", record)
    return record


from .robust_scenarios import (
    audit as audit,
    aggregate as aggregate,
    percentile_interval as percentile_interval,
    uncertainty_ranges as uncertainty_ranges,
    random_scenarios as random_scenarios,
    corner_scenarios as corner_scenarios,
    thermal_passive_scenarios as thermal_passive_scenarios,
)
from .robust_measure import measure as measure, freeze as freeze
