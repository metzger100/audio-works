# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite matched A/B cohort and isolated C; never overwrite previous evidence."""

from copy import deepcopy
from datetime import datetime, timezone
import csv
import json
from pathlib import Path
import re
import sys
import uuid

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(Path(__file__).resolve().parent)]
from meridian_lab.core import (
    Simulator,
    digest,
    read_yaml,
    source_manifest,
    write_json,
    verify_spec_lock,
    environment_versions,
)
from meridian_lab.bounded import owned_parts
from meridian_lab.cli import run, implementation_manifest
from meridian_lab import qualification as q
from meridian_lab.metrics import at_frequency, device_noise_totals, integrate_asd
from meridian_lab.robust_scenarios import uncertainty_ranges, thermal_passive_scenarios
from focused_math import dc_oracle, filter_calculation, passive_twoport_oracle
from focused_driver import fixtures
from focused_interaction import interaction

PLAN = "research/architectures/focused-plan-001.yaml"


def frozen_sim(candidate, directory, out, scenario):
    sim = Simulator(candidate, directory, scenario.get("parameters", {}))
    sim.candidate = out / "implementations" / candidate
    sim.meta = deepcopy(read_yaml(sim.candidate / "topology.yaml"))
    sim.model_root = out / "source/models"
    if scenario.get("model_replacement"):
        name = scenario["model_replacement"]
        sim.meta["semiconductor_models"] = [
            name if x.startswith("jfe150") else x for x in sim.meta["semiconductor_models"]
        ]
        corner = directory / "implementation"
        corner.mkdir(parents=True)
        (corner / "circuit.cir").write_text(
            re.sub(r"(?im)\bJFE150\s*$", name.upper(), (sim.candidate / "circuit.cir").read_text())
        )
        sim.candidate = corner
    return sim


def paired_scenarios(plan, candidates):
    metas = {c: read_yaml(ROOT / "candidates" / c / "topology.yaml") for c in candidates}
    ranges = {c: uncertainty_ranges(m) for c, m in metas.items()}
    keys = sorted(set().union(*(r.keys() for r in ranges.values())))
    rng = np.random.default_rng(plan["independent_seed"])
    cases = []
    for i in range(16):
        quantiles = dict(zip(keys, map(float, rng.uniform(size=len(keys))), strict=True))
        parameters = {}
        for c, meta in metas.items():
            logs = {"LEAK"} | {
                k for k, d in meta["population"].items() if d["distribution"] == "log_uniform"
            }
            parameters[c] = {
                k: float(np.exp(np.log(a) + quantiles[k] * (np.log(b) - np.log(a))))
                if k in logs
                else float(a + quantiles[k] * (b - a))
                for k, (a, b) in sorted(ranges[c].items())
            }
        cases.append(
            dict(
                id=f"holdout_{i:02d}",
                parameters={},
                parameters_by_candidate=parameters,
                common_quantiles=quantiles,
                kind="paired artificial stress; same environment and quantiles, design-specific ranges; not production",
            )
        )
    return cases


def scenario_set(candidate, out, scenario, validation=False):
    directory = out / candidate / scenario["id"]
    meta = read_yaml(out / "implementations" / candidate / "topology.yaml")
    allowed = set(meta["parameters"]) | set(q.scenario_ranges()) | {"CROSS"}
    s = deepcopy(scenario)
    values = s.pop("parameters_by_candidate", {}).get(candidate, s.get("parameters", {}))
    s["parameters"] = {k: float(v) for k, v in values.items() if k in allowed}
    sim = frozen_sim(candidate, directory, out, s)
    row = dict(
        candidate=candidate,
        scenario=scenario["id"],
        validation=validation,
        declared_scenario=s,
        status="error",
        jobs=sim.jobs,
    )
    board = scenario.get("board_leakage_ohm")
    extra = f"Rboard f mic_g {board}" if board else ""
    try:
        raw = sim.execute(
            "matched",
            "op\nwrite op.raw all\nac dec 64 1 10Meg\nwrite ac.raw all",
            ["op.raw", "ac.raw"],
            extra=extra,
        )
        ctx = {"nominal": raw, "checks": {}}
        op = q.operating_point(sim, ctx)
        fr = q.frequency_response(sim, ctx)
        row.update(
            status="pass" if op["status"] == fr["status"] == "pass" else "fail",
            current_a=op["metrics"]["current_a"],
            polarization_v=op["metrics"]["polarization_dc_v"],
            response_db=fr["metrics"]["response_deviation_db"],
            sensitivity_v_per_pa=fr["metrics"]["sensitivity_v_per_pa_at_1khz"],
            dc=dc_oracle(
                raw["op.raw"],
                sim.params,
                "RSERVOOUT_VALUE" in sim.params,
                "RCBACKFILTERINSULATION_VALUE" in sim.params,
                board,
            ),
        )
        if not validation:
            # q.noise does not accept the added board branch. Explicitly use the
            # same branch in both AC and native-noise decks and independent roots.
            n = sim.execute(
                "matched_noise",
                "noise v(pp,pn) VP dec 128 20 20k 1\nsetplot noise1\nwrite noise.raw all",
                ["noise.raw"],
                extra=extra,
            )["noise.raw"]
            roots = device_noise_totals(n)
            f = n["frequency"].real
            gain = np.array(
                [
                    abs(
                        at_frequency(
                            raw["ac.raw"]["frequency"], raw["ac.raw"].voltage("pp", "pn"), x
                        )
                    )
                    for x in f
                ]
            )
            internal = sum(
                (x * x for k, x in roots.items() if ".xdut." in k or "rboard" in k),
                np.zeros_like(f),
            )
            total = sum((x * x for x in roots.values()), np.zeros_like(f))
            row.update(
                noise_pa_rms_conditional=integrate_asd(f, np.sqrt(internal) / gain),
                noise_power_closure_relative=float(
                    np.max(
                        abs(total - n["onoise_spectrum"].real ** 2)
                        / np.maximum(n["onoise_spectrum"].real ** 2, 1e-300)
                    )
                ),
                contribution_pa_rms={k: integrate_asd(f, x / gain) for k, x in roots.items()},
                noise_state="conditional incomplete spectra; capsule/fixture excluded from electronics",
            )
    except Exception as exc:
        row.update(status="error", reason=f"{type(exc).__name__}: {exc}")
    write_json(directory / "result.json", row)
    print("AB", candidate, scenario["id"], row["status"], row.get("response_db"), flush=True)
    return row


def main():
    verify_spec_lock()
    plan = read_yaml(ROOT / PLAN)
    child = read_yaml(ROOT / "research/architectures/focused-children-001.json")["B_child"]
    candidates = ["candidate_0019", "candidate_0023", child]
    out = (
        ROOT
        / "results/mechanism_controls"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_focused_"
            + uuid.uuid4().hex[:8]
        )
    )
    out.mkdir(parents=True, exist_ok=False)
    manifest = source_manifest()
    for name in [
        "tools/ngspice/usr/bin/ngspice",
        "research/architectures/focused-children-001.json",
        "research/architectures/focused-sources-001.json",
        "research/architectures/focused-queries-001.json",
    ]:
        path = ROOT / name
        for p in [path, *(owned_parts(path) if path.suffix == ".json" else [])]:
            manifest[str(p.relative_to(ROOT))] = digest(p)
    for p in (ROOT / "tools/ngspice/usr/lib/ngspice").glob("*.cm"):
        manifest[str(p.relative_to(ROOT))] = digest(p)
    for name, sha in manifest.items():
        p = out / "source" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ROOT / name).read_bytes())
        if digest(p) != sha:
            raise ValueError("Source changed during freeze")
    implementations = {c: implementation_manifest(ROOT / "candidates" / c) for c in candidates}
    for c, m in implementations.items():
        for name in m:
            p = out / "implementations" / c / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes((ROOT / "candidates" / c / name).read_bytes())
    holdouts = paired_scenarios(plan, candidates)
    write_json(
        out / "plan.json",
        dict(
            plan=plan,
            candidates=candidates,
            matched_holdouts=holdouts,
            versions=environment_versions(),
        ),
    )
    write_json(out / "manifest.json", dict(sources=manifest, implementations=implementations))
    write_json(
        out / "independent-math.json",
        dict(filter=filter_calculation(), two_port=passive_twoport_oracle()),
    )
    rows = []
    for c in candidates:
        for scenario in plan["scenarios"]:
            rows.append(scenario_set(c, out, scenario))
        for scenario in holdouts:
            rows.append(scenario_set(c, out, scenario, True))
        meta = read_yaml(ROOT / "candidates" / c / "topology.yaml")
        bom = read_yaml(ROOT / "candidates" / c / "bom.yaml")
        for sign, base in enumerate(thermal_passive_scenarios(meta, bom)[:2]):
            base["id"] = f"tolerance_TCR_{sign}"
            # Output count preserved; opposing capacitor endpoint stresses.
            for key, d in meta["population"].items():
                if key.startswith("COUT"):
                    side = sign if key.startswith("COUTP") else 1 - sign
                    base["parameters"][key] = d["range"][side]
                if key in [
                    "CBACKFILTER_VALUE",
                    "RCBACKFILTERINSULATION_VALUE",
                    "RCBACKFILTERLOSS_VALUE",
                    "LBACKFILTER_VALUE",
                ]:
                    base["parameters"][key] = d["range"][sign]
            rows.append(scenario_set(c, out, base))
    full = {}
    for c in candidates:
        full[c] = run(
            c,
            seed=plan["seed"],
            samples=plan["full_suite_samples"],
            hypothesis="Prompt9 matched complete suite; retained unsupported nonlinear and all physical gates",
            parent_experiments=[
                read_yaml(ROOT / "candidates" / c / "results.json")["latest_experiment"]
            ]
            if (ROOT / "candidates" / c / "results.json").exists()
            else [],
        )["experiment_id"]
        print("full suite", c, full[c], flush=True)
    interactions = [interaction(c, out, frozen_sim) for c in candidates]
    driver = fixtures(out / "driver", plan)
    write_json(out / "driver-results.json", driver)
    fields = [
        "candidate",
        "scenario",
        "validation",
        "status",
        "current_a",
        "polarization_v",
        "response_db",
        "sensitivity_v_per_pa",
        "noise_pa_rms_conditional",
        "reason",
    ]
    with (out / "scenarios.csv").open("w") as f:
        w = csv.DictWriter(f, fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    unchanged = all(digest(ROOT / n) == sha for n, sha in manifest.items()) and all(
        implementation_manifest(ROOT / "candidates" / c) == m for c, m in implementations.items()
    )
    record = dict(
        experiment_id=out.name,
        plan=PLAN,
        rows=rows,
        full_suite=full,
        interactions=interactions,
        driver_result="driver-results.json",
        source_unchanged=unchanged,
        production_front=[],
        physical_front=[],
        eligible=False,
        complete=True,
    )
    write_json(out / "results.json", record)
    (out / "batch.sha256").write_text(
        "".join(
            f"{digest(p)}  {p.relative_to(ROOT)}\n" for p in sorted(out.rglob("*")) if p.is_file()
        )
    )
    print(
        json.dumps(
            dict(
                batch=str(out.relative_to(ROOT)),
                source_unchanged=unchanged,
                rows=len(rows),
                eligible=False,
            )
        )
    )
    if not unchanged:
        raise RuntimeError("Source integrity failed; preserve batch")


if __name__ == "__main__":
    main()
