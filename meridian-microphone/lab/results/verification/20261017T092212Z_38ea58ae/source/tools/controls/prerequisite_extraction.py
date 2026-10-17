# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite extraction replay with frozen plan, input inventory identities and source."""

from datetime import datetime, timezone
from pathlib import Path
import contextlib
import io
import runpy
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.core import digest, read_yaml, write_json, verify_spec_lock, environment_versions
from meridian_lab.bounded import owned_parts

PLAN = "research/devices/simulation-prerequisites-plan-005.yaml"


def main():
    verify_spec_lock()
    plan = read_yaml(ROOT / PLAN)
    folder = (
        ROOT
        / "results/device_models"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_extraction_"
            + uuid.uuid4().hex[:8]
        )
    )
    folder.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), ROOT / PLAN, ROOT / "tools/reporting/prerequisite_report.py"]
    for prefix in ["src", "spec"]:
        paths += [p for p in (ROOT / prefix).rglob("*") if p.suffix in {".py", ".yaml"}]
    inputs = []
    cohorts = runpy.run_path(str(ROOT / "tools/reporting/prerequisite_report.py"))["COHORTS"]
    for cohort in cohorts:
        batch = ROOT / "results/device_models" / cohort
        inputs += [batch / "batch.sha256", batch / "results.json", batch / "plan.json"]
    comparison = (
        ROOT / "results/reports/architecture-comparison-001/architecture-comparison-001.json"
    )
    inputs += [comparison, *owned_parts(comparison)]
    for parent in read_yaml(comparison)["nominal_metrics"]:
        inputs.append(ROOT / "results/runs" / parent["experiment"] / "results.json")
    source = {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(paths))}
    input_hashes = {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(inputs))}
    for name, sha in source.items():
        path = folder / "source" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / name).read_bytes())
        if digest(path) != sha:
            raise ValueError("Source changed during freeze")
    write_json(
        folder / "plan.json",
        dict(
            plan=plan,
            source_manifest=source,
            input_inventory_hashes=input_hashes,
            versions=environment_versions(),
        ),
    )
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        runpy.run_path(str(ROOT / "tools/reporting/prerequisite_report.py"), run_name="__main__")
    (folder / "extraction.log").write_text(stream.getvalue())
    behavior = read_yaml(ROOT / "research/devices/simulation-prerequisites-behavior-001.json")
    fits = sum(row["fits"] for row in behavior["nonlinear"])
    stable = all(digest(ROOT / name) == sha for name, sha in {**source, **input_hashes}.items())
    accepted = (
        fits == plan["maximum_fits"]
        and stable
        and all(
            row["H2_refinement_pass"] and row["H3_refinement_pass"] for row in behavior["nonlinear"]
        )
    )
    write_json(
        folder / "results.json",
        dict(
            plan=plan,
            source_manifest=source,
            input_inventory_hashes=input_hashes,
            source_unchanged=stable,
            fits=fits,
            nonlinear=behavior["nonlinear"],
            status="pass" if accepted else "fail",
            scope="Numerical follower H2/H3 only; H4-H10 near floor and microphone/headroom unsupported",
            eligible=False,
            simulator_jobs=0,
        ),
    )
    (folder / "batch.sha256").write_text(
        "".join(
            f"{digest(p)}  {p.relative_to(ROOT)}\n"
            for p in sorted(folder.rglob("*"))
            if p.is_file()
        )
    )
    print(folder.relative_to(ROOT), accepted)
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
