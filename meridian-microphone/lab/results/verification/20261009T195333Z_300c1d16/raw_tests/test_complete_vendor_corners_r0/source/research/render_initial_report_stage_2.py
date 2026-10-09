# SPDX-License-Identifier: GPL-3.0-or-later
"""Render the initial infrastructure report from immutable experiment records.

This is reporting only: it changes no netlist, specification, result or archive.
Run from the lab: MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python research/render_initial_report.py
"""

from render_initial_report_support import BASE, OPTIMIZATION, PROPOSAL, ROOT


def _literal(name):
    return (ROOT / "research/render-initial-report-text" / name).read_text()[:-1]


def stage(context):
    b = context["b"]
    checks = context["checks"]
    table = context["table"]
    tests = context["tests"]
    verification_relative = context["verification_relative"]
    report = (
        _literal("initial-template-000.txt")
        + f"{tests}"
        + _literal("initial-template-002.txt")
        + f"{b['spec_sha256']}"
        + _literal("initial-template-004.txt")
        + f"{BASE}"
        + _literal("initial-template-006.txt")
        + f"{PROPOSAL}"
        + _literal("initial-template-008.txt")
        + f"{len(b['jobs'])}"
        + _literal("initial-template-010.txt")
        + f"{table}"
        + _literal("initial-template-012.txt")
        + f"{OPTIMIZATION}"
        + _literal("initial-template-014.txt")
        + f"{checks}"
        + _literal("initial-template-016.txt")
        + f"{verification_relative}"
        + _literal("initial-template-018.txt")
        + f"{tests}"
        + _literal("initial-template-020.txt")
    )
    return {**context, "report": report}
