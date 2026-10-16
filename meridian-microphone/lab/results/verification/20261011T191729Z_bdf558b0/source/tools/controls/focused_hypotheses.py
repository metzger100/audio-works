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
    metas = [read_yaml(ROOT / "candidates" / c / "topology.yaml") for c in candidates]
    # Draw common variables once by sorted union key; adding a component cannot
    # reshuffle another candidate's external/specimen population.
    ranges = {}
    for meta in metas:
        for key, bounds in uncertainty_ranges(meta).items():
            if key in ranges and ranges[key] != bounds:
                raise ValueError("Incompatible common passive uncertainty " + key)
            ranges[key] = bounds
    rng = np.random.default_rng(plan["independent_seed"])
    cases = []
    logs = {"LEAK"} | {
        k for m in metas for k, d in m["population"].items() if d["distribution"] == "log_uniform"
    }
    for i in range(16):
        values = {
            k: float(np.exp(rng.uniform(np.log(a), np.log(b))))
            if k in logs
            else float(rng.uniform(a, b))
            for k, (a, b) in sorted(ranges.items())
        }
        cases.append(
            dict(
                id=f"holdout_{i:02d}",
                parameters=values,
                kind="paired artificial stress; not production",
            )
        )
    return cases


def scenario_set(candidate, out, scenario, validation=False):
    directory = out / candidate / scenario["id"]
    meta = read_yaml(out / "implementations" / candidate / "topology.yaml")
    allowed = set(meta["parameters"]) | set(q.scenario_ranges()) | {"CROSS"}
    s = deepcopy(scenario)
    s["parameters"] = {k: v for k, v in s.get("parameters", {}).items() if k in allowed}
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


def interaction(candidate, out):
    sim = frozen_sim(candidate, out / "interaction" / candidate, out, dict(parameters={}))
    row = dict(candidate=candidate, jobs=sim.jobs, status="incomplete")
    try:
        raw = sim.execute(
            "recovery",
            "alter @v.xenv.vphantom[pwl] [ 0 48 1 48 1.001 44 2 44 2.001 48 5 48 ]\ntran 1m 5 0 1m\nwrite recovery.raw all",
            ["recovery.raw"],
            {"PRESSURE_AC": 0},
        )["recovery.raw"]
        row["recovery_final_nodes_v"] = {
            k: float(raw.voltage("xdut." + k, "mic_g")[-1]) for k in ["source", "raw"]
        }
        row["recovery_final_polarization_v"] = float(raw.voltage("b", "f")[-1])
        row["recovery_scope"] = "Finite5s cold/dip recovery; no extension or harmonics claim"
    except Exception as exc:
        row["recovery_error"] = str(exc)
    # Record a conditional voltage-return diagnostic at the 300kohm sense path.
    # It keeps DC and bilateral device networks. Multi-loop pole/current-injection
    # evidence is still required, so no stability pass is manufactured.
    if "RSERVOOUT_VALUE" in sim.params:
        child = out / "interaction" / candidate / "sense_injection"
        child.mkdir()
        circuit = (
            (sim.candidate / "circuit.cir")
            .read_text()
            .replace(
                "Rservosense0 source sense_div0",
                "Vloop loop source DC 0 AC 1\nRservosense0 loop sense_div0",
            )
        )
        (child / "circuit.cir").write_text(circuit)
        sim.candidate = child
        try:
            a = sim.execute(
                "voltage_return",
                "ac dec 128 .001 10Meg\nwrite loop.raw all",
                ["loop.raw"],
                {"PRESSURE_AC": 0},
            )["loop.raw"]
            ratio = -a["v(xdut.source)"] / a["v(xdut.loop)"]
            f = a["frequency"].real
            crossing = np.flatnonzero((abs(ratio[:-1]) - 1) * (abs(ratio[1:]) - 1) < 0)
            row["voltage_return_diagnostic"] = dict(
                frequency_hz=f.tolist(),
                real=ratio.real.tolist(),
                imag=ratio.imag.tolist(),
                crossing_brackets_hz=[[float(f[i]), float(f[i + 1])] for i in crossing],
                gain_at_point01hz=float(abs(at_frequency(f, ratio, 0.01))),
                minimum_distance_minus1=float(min(abs(1 + ratio))),
                stability_proof=False,
                reason="Bilateral/multiple paths, open-loop RHP poles and current injection unverified",
            )
        except Exception as exc:
            row["return_ratio_error"] = str(exc)
    write_json(out / "interaction" / candidate / "result.json", row)
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
        for p in [path, *owned_parts(path)]:
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
    interactions = [interaction(c, out) for c in candidates]
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
