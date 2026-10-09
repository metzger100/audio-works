#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolated device characterization against primary evidence; errors survive in records."""

from pathlib import Path
import argparse
from datetime import datetime, timezone
import json
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.core import source_manifest, write_json, environment_versions, verify_spec_lock
from meridian_lab.device_models import resolve, index


from characterize_base import (
    Experiment as Experiment,
    interpolate as interpolate,
    compare as compare,
    fet_circuit as fet_circuit,
    bjt_circuit as bjt_circuit,
    refinement as refinement,
)
from characterize_jfet import jfet as jfet
from characterize_bipolar import bipolar as bipolar
from characterize_opa import opa as opa
from characterize_mos import mosfet as mosfet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+")
    parser.add_argument("--parent-experiment", action="append", default=[])
    args = parser.parse_args()
    for parent in args.parent_experiment:
        p = ROOT / "results/device_models" / parent
        if Path(parent).name != parent or not any(
            (p / n).is_file() for n in ["results.json", "failure.json"]
        ):
            raise ValueError("Parent experiment must resolve to a preserved device-model record")
    verify_spec_lock()
    manifest = source_manifest()
    folder = (
        ROOT
        / "results/device_models"
        / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8])
    )
    folder.mkdir(parents=True, exist_ok=False)
    for relative in manifest:
        p = folder / "source" / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ROOT / relative).read_bytes())
    available = index(folder / "source/models")
    ids = args.models or list(available)
    exp = Experiment(folder, available)
    results = {}
    for id_ in ids:
        try:
            if id_ not in available:
                raise ValueError("Unknown model ID")
            m = available[id_]
            resolve(exp.root, [id_])
            characterizers = {
                "jfe150": jfet,
                "opa197": opa,
                "bc846b": bipolar,
                "bc856b": bipolar,
                "vishay_2n7002k": mosfet,
            }
            if m["device_id"] not in characterizers:
                raise ValueError(
                    "No characterized fixture for this device; unknown behavior is unqualified"
                )
            results[id_] = characterizers[m["device_id"]](exp, m)
            results[id_]["status"] = (
                "disagreement"
                if any(r["status"] == "fail" for r in results[id_]["comparisons"])
                else "scoped_agreement"
            )
        except (ValueError, RuntimeError, OSError) as exc:
            results[id_] = {**exp.partial.get(id_, {}), "status": "error", "reason": str(exc)}
        errors = [j for j in exp.jobs if j["model_id"] == id_ and j["status"] == "error"]
        if errors:
            results[id_]["status"] = "error"
            results[id_]["failed_jobs"] = len(errors)
        write_json(
            folder / "checkpoint.json",
            {"results": results, "jobs": exp.jobs, "source_manifest": manifest, "complete": False},
        )
        print(id_, results[id_]["status"], flush=True)
    unchanged = source_manifest() == manifest
    record = dict(
        schema_version=1,
        experiment_id=folder.name,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        rng_seed=None,
        sampling="deterministic grids; no manufacturing probabilities",
        parent_experiments=args.parent_experiment,
        source_manifest=manifest,
        source_unchanged=unchanged,
        versions=environment_versions(),
        results=results,
        jobs=exp.jobs,
        eligible_for_production=False,
        status="recorded_unqualified" if unchanged else "source_integrity_error",
        unresolved="Behavior-specific scope; failures preserved; no model receives a blanket low-noise/production qualification",
    )
    write_json(folder / "results.json", record)
    print(
        json.dumps(
            {
                "record": str(folder / "results.json"),
                "jobs": len(exp.jobs),
                "errors": sum(j["status"] == "error" for j in exp.jobs),
                "source_unchanged": unchanged,
            },
            indent=2,
        )
    )
    return (
        2
        if not unchanged or any(r["status"] in {"error", "disagreement"} for r in results.values())
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
