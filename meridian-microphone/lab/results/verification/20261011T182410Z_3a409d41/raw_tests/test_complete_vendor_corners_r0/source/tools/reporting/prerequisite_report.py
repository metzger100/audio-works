# SPDX-License-Identifier: GPL-3.0-or-later
"""Rebuild scoped behavior/uncertainty tables without changing frozen evidence."""

import csv
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.core import read_yaml, write_json, digest, parse_raw
from meridian_lab.nonlinear import settled_spectrum

COHORTS = [
    "20261011T175705Z_prerequisites_a7cc0cdb",
    "20261011T180313Z_observer_diagnosis_0f2c5116",
    "20261011T180615Z_high_impedance_de3fa943",
]


def main():
    out = ROOT / "research/devices"
    records = []
    checked = 0
    behaviors = []
    nonlinear = []
    for cohort in COHORTS:
        folder = ROOT / "results/device_models" / cohort
        record = read_yaml(folder / "results.json")
        for name, sha in record["source_manifest"].items():
            if digest(folder / "source" / name) != sha:
                raise ValueError("Frozen source damaged")
            checked += 1
        for job in record["jobs"]:
            directory = folder / job["directory"]
            for name, sha in job["retained_hashes"].items():
                if digest(directory / name) != sha:
                    raise ValueError("Retained job evidence damaged")
                checked += 1
            behaviors.append(
                dict(
                    cohort=cohort,
                    model=job["model"]["id"],
                    test=job["label"],
                    status=job["status"],
                    reason=job.get("reason", ""),
                    temperature_c=job["temperature_c"],
                    model_sha256=job["model"].get("sha256", "multiple/includes in frozen plan"),
                    deck_sha256=job["netlist_sha256"],
                    directory=job["directory"],
                )
            )
        records.append(
            dict(
                cohort=cohort,
                jobs=len(record["jobs"]),
                errors=sum(j["status"] == "error" for j in record["jobs"]),
                stable_at_execution=record["source_unchanged"],
                record_sha256=digest(folder / "results.json"),
                plan_sha256=digest(folder / "plan.json"),
            )
        )
    r = read_yaml(ROOT / "results/device_models" / COHORTS[0] / "results.json")
    for model in [
        "jfe150_generic",
        "jfe150_weak",
        "jfe150_strong",
        "jfe150_pspice",
        "jfe150_tina_isolated",
    ]:
        folder = ROOT / "results/device_models" / COHORTS[0] / model
        fits = []
        for name in ["follower_direct", "follower_refined"]:
            wave = parse_raw(folder / name / "tran.raw")
            for cycles in [8, 16]:
                for samples in [128, 256, 512]:
                    fits.append(
                        settled_spectrum(wave["time"], wave["v(s)"], 1000, 0.032, cycles, samples)
                    )
        values = np.array([h["harmonics_v_rms"] for h in fits])
        nominal = values[3]
        spread = np.ptp(values, axis=0)
        nonlinear.append(
            dict(
                model=model,
                source_peak_v=0.01,
                source_impedance_ohm=0,
                load_ohm=1000,
                load_f=70e-12,
                frequency_hz=1000,
                fits=len(fits),
                H1_H10_rms_v=nominal.tolist(),
                deterministic_spread_v=spread.tolist(),
                relative_spread_to_each_harmonic=(spread / np.maximum(nominal, 1e-30)).tolist(),
                H2_percent=100 * nominal[1] / nominal[0],
                H3_percent=100 * nominal[2] / nominal[0],
                THD_percent=100 * np.linalg.norm(nominal[1:]) / nominal[0],
                H2_refinement_pass=bool(spread[1] / nominal[1] < 0.01),
                H3_refinement_pass=bool(spread[2] / nominal[2] < 0.01),
                support="Frozen isothermal voltage-driven follower only; no independent measured nonlinear reference",
                guaranteed_limits=r["results"][model]["guaranteed_25c_10v"],
            )
        )
    comparison = read_yaml(
        ROOT / "results/reports/architecture-comparison-001/architecture-comparison-001.json"
    )
    parents = []
    for rep in comparison["nominal_metrics"]:
        folder = ROOT / "results/runs" / rep["experiment"]
        record = read_yaml(folder / "results.json")
        parents.append(
            dict(
                candidate=rep["candidate"],
                experiment=rep["experiment"],
                record_sha256=digest(folder / "results.json"),
                checks={
                    k: v
                    for k, v in record.get("checks", {}).items()
                    if k in ["operating_point", "distortion", "headroom", "carrier"]
                },
            )
        )
    write_json(
        out / "simulation-prerequisites-behavior-001.json",
        dict(
            date="2026-10-11",
            cohorts=records,
            checked_frozen_and_job_files=checked,
            behaviors=behaviors,
            nonlinear=nonlinear,
            original_comparison_parents=parents,
            full_microphone_nonlinear_supported=False,
            headroom_supported=False,
            physical_measurements=[],
            eligible=False,
            uncertainty="Deterministic timestep/window/sampling spread, not stochastic confidence or model-error bound",
        ),
    )
    groups = {"jfet": [], "bipolar": [], "opa": [], "integration": []}
    for row in behaviors:
        kind = (
            "jfet"
            if row["model"].startswith("jfe")
            else "opa"
            if row["model"].startswith("opa")
            else "bipolar"
            if row["model"].startswith(("bc", "pmbt", "diotec", "diodes"))
            else "integration"
        )
        groups[kind].append({k: row[k] for k in ["model", "test", "status", "reason"]})
    for kind, rows in groups.items():
        with (out / f"simulation-prerequisites-{kind}-001.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(records)
    print("checked", checked)
    print(
        [
            (
                x["model"],
                x["H2_percent"],
                x["H3_percent"],
                x["H2_refinement_pass"],
                x["H3_refinement_pass"],
            )
            for x in nonlinear
        ]
    )


if __name__ == "__main__":
    main()
