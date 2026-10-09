# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit phases keep source cohorts idle/stable between evaluations.

search -> realize -> evaluate; each phase writes a new record, refuses overwrite.
"""

from datetime import datetime, timezone
import argparse
from pathlib import Path
import sys
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "search"))
from meridian_lab.core import ROOT, digest, read_yaml, source_manifest, write_json
from meridian_lab.robust import optimize, validate, freeze, measure, aggregate
from meridian_lab.cli import run


def search():
    plan = read_yaml(ROOT / "optimization/robust-plan.yaml")
    batch = (
        ROOT
        / "results/optimization_batches"
        / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8])
    )
    batch.mkdir(parents=True, exist_ok=False)
    write_json(batch / "plan.json", plan)
    records = {}
    for family, definition in plan["families"].items():
        r = optimize(
            definition["candidate"],
            definition["design"],
            plan["initial_evaluation_budget_per_family"],
            plan["training_seed"],
            plan["axis"],
            plan["aggregation"],
        )
        records[family] = r["experiment_id"]
        print(
            f"{family}: {r['status']}; {r['evaluations']}/{r['budget_declared_before_run']}; {r['termination']}",
            flush=True,
        )
    write_json(
        batch / "search.json", {"experiments": records, "plan_sha256": digest(batch / "plan.json")}
    )
    print(str(batch.relative_to(ROOT)), flush=True)


def evaluate_batch(batch):
    if (batch / "evaluation.json").exists():
        raise ValueError("Never overwrite a completed batch; create a new batch")
    plan = read_yaml(batch / "plan.json")
    searches = read_yaml(batch / "search.json")["experiments"]
    children = read_yaml(batch / "realization.json")["children"]
    manifest = source_manifest()
    started = time.monotonic()
    baselines = {}
    continuous = {}
    evaluations = {}
    discrete = {}
    for family, definition in plan["families"].items():
        candidate = definition["candidate"]
        previous = read_yaml(ROOT / "candidates" / candidate / "results.json")["latest_experiment"]
        base = run(
            candidate,
            plan["validation_seeds"][0],
            plan["full_suite_samples"],
            parent_experiments=[previous],
            hypothesis="Current frozen-cohort baseline; preserve prior source cohorts and all checks",
        )
        baselines[family] = base["experiment_id"]
        proposal = read_yaml(ROOT / "results/runs" / searches[family] / "optimization.json")
        if proposal["best"]:
            overrides = proposal["best"]["parameters"]
            tolerance = {
                t: [
                    overrides[t] * (1 - g["tolerance_fraction"]),
                    overrides[t] * (1 + g["tolerance_fraction"]),
                ]
                for g in definition["design"].values()
                for t in g["targets"]
            }
            record = run(
                candidate,
                plan["validation_seeds"][0],
                plan["full_suite_samples"],
                overrides=overrides,
                population_overrides=tolerance,
                parent_experiments=[base["experiment_id"]],
                numerical_optimization={
                    "performed": True,
                    "proposal_experiment": proposal["experiment_id"],
                    "training_budget": proposal["evaluations"],
                    "termination": proposal["termination"],
                },
                hypothesis="Full suite of continuous response proposal; physical BOM still parent nominal, design tolerances explicitly recentered, not a realized hardware claim",
            )
            validate(
                candidate,
                overrides,
                batch / ("continuous_" + family),
                plan["validation_seeds"][0],
                plan["validation_samples_per_seed"],
                definition["design"],
            )
            continuous[family] = {
                "experiment": record["experiment_id"],
                "validation": str(
                    (batch / ("continuous_" + family) / "validation.json").relative_to(ROOT)
                ),
            }
    for child in children:
        candidate = child["candidate"]
        family = child["family"]
        parent = continuous.get(family, {}).get("experiment", baselines[family])
        record = run(
            candidate,
            plan["validation_seeds"][1],
            plan["full_suite_samples"],
            parent_experiments=[parent, baselines[family]]
            if parent != baselines[family]
            else [parent],
            hypothesis="Full suite of distinct sourced BOM combination/structural child; never inherit continuous/nominal qualification",
        )
        validate(
            candidate,
            {},
            batch / candidate,
            plan["validation_seeds"][1],
            plan["validation_samples_per_seed"],
        )
        evaluations[candidate] = {
            "experiment": record["experiment_id"],
            "validation": str((batch / candidate / "validation.json").relative_to(ROOT)),
        }
        # Two loss/leakage assumption-breaking endpoint cases per combination.
        if "count_per_leg" in child:
            meta = read_yaml(ROOT / "candidates" / candidate / "topology.yaml")
            cases = []
            for side in [0, 1]:
                params = {
                    k: d["range"][side]
                    for k, d in meta["parameters"].items()
                    if "loss" in k.lower() or "leak" in k.lower()
                }
                cases.append(
                    {
                        "id": "passive_loss_leakage_" + str(side),
                        "kind": "constant-law source-anchored stress; not a population bound",
                        "parameters": params,
                    }
                )
            snap = batch / ("discrete_" + candidate)
            snap.mkdir()
            freeze(snap, candidate)
            rows = measure(candidate, snap / "screens", snap, {}, cases)
            discrete[candidate] = {
                "cases": rows,
                "summary": aggregate(rows, "response_deviation_db"),
            }
            write_json(snap / "discrete.json", discrete[candidate])
    record = {
        "baseline_experiments": baselines,
        "continuous": continuous,
        "children": evaluations,
        "discrete_combinations": discrete,
        "runtime_s": time.monotonic() - started,
        "source_manifest": manifest,
        "source_unchanged": source_manifest() == manifest,
        "manufacturing_yield": None,
        "physical_qualified": False,
        "production_winner": None,
    }
    write_json(batch / "evaluation.json", record)
    print(str(batch / "evaluation.json"), flush=True)


from robust_realization import output_child as output_child, realize as realize

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=["search", "realize", "evaluate"])
    p.add_argument("--batch", type=Path)
    args = p.parse_args()
    if args.phase == "search":
        search()
    elif args.phase == "realize":
        realize(args.batch.resolve())
    else:
        evaluate_batch(args.batch.resolve())
