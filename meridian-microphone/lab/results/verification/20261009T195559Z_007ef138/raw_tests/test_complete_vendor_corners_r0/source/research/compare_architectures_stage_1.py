# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce comparison 001 from immutable records and original local waveforms.

No simulator, candidate, specification, archive or original result is modified.
Run from lab: .venv/bin/python research/compare_architectures.py
"""

from compare_architectures_support import OUT, ROOT, require_common, sha

from meridian_lab.core import read_yaml


from pathlib import Path


def stage(context):
    OUT.mkdir(parents=True, exist_ok=True)
    cfg_path = ROOT / "research/architectures/architecture-comparison-001.yaml"
    cfg = read_yaml(cfg_path)
    inputs = {}
    checked = {}

    def evidence(path):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        inputs[str(path.relative_to(ROOT))] = sha(path)
        return path

    def load(path):
        return read_yaml(evidence(path))

    def declared(path, expected):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        key = str(path.relative_to(ROOT))
        if key in checked and checked[key] != expected:
            raise ValueError("Conflicting declared hashes: " + key)
        checked[key] = expected
        if not path.is_file() or sha(path) != expected:
            raise ValueError("Missing or changed original evidence: " + key)

    def audit_jobs(value):
        if isinstance(value, dict):
            if "folder" in value and ("netlist_sha256" in value or "files" in value):
                folder = Path(value["folder"])
                if value.get("netlist_sha256"):
                    declared(folder / "job.cir", value["netlist_sha256"])
                for name, h in value.get("files", {}).items():
                    declared(folder / name, h)
            for child in value.values():
                audit_jobs(child)
        elif isinstance(value, list):
            for child in value:
                audit_jobs(child)

    batch = Path(cfg["batch"])
    index = load(batch / "evaluation.json")
    experiment_ids = list(index["baseline_experiments"].values())
    experiment_ids += [e["experiment"] for e in index["continuous"].values()]
    experiment_ids += [e["experiment"] for e in index["children"].values()]
    records = {id_: load(Path("results/runs") / id_ / "results.json") for id_ in experiment_ids}
    require_common(list(records.values()))
    assert index["source_unchanged"]
    for id_, r in records.items():
        folder = ROOT / "results/runs" / id_
        for name, h in r["source_manifest"].items():
            declared(folder / "source" / name, h)
        for name, h in r["implementation_manifest"].items():
            declared(folder / name, h)
        audit_jobs(r["jobs"])
        assert not r["eligible"]
    search = load(batch / "search.json")["experiments"]
    optimizers = {}
    for family, id_ in search.items():
        directory = ROOT / "results/runs" / id_
        r = load(directory / "optimization.json")
        trials = load(directory / "trials.json")
        for name, h in r["source_manifest"].items():
            declared(directory / "source" / name, h)
        for name, h in r.get("implementation_manifest", {}).items():
            declared(directory / "candidate" / name, h)
        audit_jobs(trials)
        optimizers[family] = {
            k: r.get(k)
            for k in [
                "experiment_id",
                "candidate_id",
                "evaluations",
                "budget_declared_before_run",
                "scenario_attempts",
                "analysis_errors",
                "termination",
                "best",
                "diagnostic_best_infeasible",
                "rng_seed",
                "suite_sha256",
                "spec_sha256",
            ]
        }
    validation = {}
    for candidate, entry in index["children"].items():
        v = load(entry["validation"])
        audit_jobs(v)
        assert v["source_unchanged"]
        assert v["source_manifest"] == next(iter(records.values()))["source_manifest"]
        validation[candidate] = v
    first = ROOT / "results/runs" / experiment_ids[0]
    part_register = read_yaml(
        evidence(first / "source/research/procurement/architecture_parts_2026-10-09.yaml")
    )
    robust_register = read_yaml(
        evidence(first / "source/research/procurement/robust_parts_2026-10-09.yaml")
    )
    refresh = read_yaml(
        evidence(ROOT / "research/comparison_procurement_observations_2026-10-09.yaml")
    )
    flags = read_yaml(evidence(ROOT / "research/patents/first_architecture_batch_2026-10-09.yaml"))
    robust_flags = read_yaml(
        evidence(ROOT / "research/patents/robust_optimization_2026-10-09.yaml")
    )
    comparison_flags = read_yaml(
        evidence(ROOT / "research/patents/architecture_comparison_001_2026-10-09.yaml")
    )
    patent_index = {r["candidate_id"]: r for r in flags["records"]}
    patent_index.update({r["candidate"]: r for r in robust_flags["candidates"]})
    nominal_rows, statuses, boms, details, contributions, spectra, harmonics = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    representative_records = {}
    return {
        **context,
        "boms": boms,
        "candidate": candidate,
        "cfg": cfg,
        "cfg_path": cfg_path,
        "checked": checked,
        "comparison_flags": comparison_flags,
        "contributions": contributions,
        "details": details,
        "evidence": evidence,
        "family": family,
        "folder": folder,
        "harmonics": harmonics,
        "index": index,
        "inputs": inputs,
        "name": name,
        "nominal_rows": nominal_rows,
        "optimizers": optimizers,
        "part_register": part_register,
        "patent_index": patent_index,
        "r": r,
        "records": records,
        "refresh": refresh,
        "representative_records": representative_records,
        "robust_register": robust_register,
        "spectra": spectra,
        "statuses": statuses,
        "v": v,
        "validation": validation,
    }
