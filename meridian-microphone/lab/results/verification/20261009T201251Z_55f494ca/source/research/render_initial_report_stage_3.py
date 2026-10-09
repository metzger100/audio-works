# SPDX-License-Identifier: GPL-3.0-or-later
"""Render the initial infrastructure report from immutable experiment records.

This is reporting only: it changes no netlist, specification, result or archive.
Run from the lab: MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python research/render_initial_report.py
"""

from render_initial_report_support import BASE, OPTIMIZATION, PROPOSAL, ROOT

from meridian_lab.bounded import write_markdown


import hashlib
import json


def stage(context):
    b = context["b"]
    output = context["output"]
    report = context["report"]
    tests = context["tests"]
    verification_path = context["verification_path"]
    verification_relative = context["verification_relative"]
    write_markdown((ROOT / "research/architectures/initial/phase0-report.md"), report)
    inputs = [ROOT / "results/runs" / ident / "results.json" for ident in [BASE, PROPOSAL]] + [
        verification_path
    ]
    overview = {
        "schema_version": 1,
        "scope": "phase_0_2_foundation",
        "candidate_kind": "ideal_infrastructure_fixture",
        "baseline_experiment": BASE,
        "value_proposal_experiment": PROPOSAL,
        "optimization_experiment": OPTIMIZATION,
        "numerical_trials": 202,
        "regression_tests": tests,
        "verification_record": verification_relative,
        "qualified_designs": 0,
        "architectural_concepts": 22,
        "persistent_families": 14,
        "implemented_nonideal_architectures": 0,
        "physical_measurements": 0,
        "same_specification": True,
        "same_suite": True,
        "spec_sha256": b["spec_sha256"],
        "suite_sha256": b["suite_sha256"],
        "report_inputs_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in inputs
        },
        "outputs": [
            "research/architectures/initial/phase0-report.md",
            "results/reports/initial-fixture-comparison.png",
            "results/reports/initial-fixture-comparison.svg",
        ],
    }
    (output / "initial-environment.json").write_text(json.dumps(overview, indent=2) + "\n")
    print(json.dumps(overview, indent=2))
    return {
        **context,
    }
