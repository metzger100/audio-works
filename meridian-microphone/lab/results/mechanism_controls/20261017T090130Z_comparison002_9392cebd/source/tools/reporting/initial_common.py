# SPDX-License-Identifier: GPL-3.0-or-later
"""Render the initial infrastructure report from immutable experiment records.

This is reporting only: it changes no netlist, specification, result or archive.
Run from the lab: MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python tools/reporting/render_initial_report.py
"""

from pathlib import Path

from meridian_lab.core import read_yaml

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[2]
BASE = "20261005T121311Z_f11a711a"
PROPOSAL = "20261005T121440Z_8f1bc311"
OPTIMIZATION = "20261005T114342Z_optimization_c7e7091b"


def read_run(identifier):
    return read_yaml(ROOT / "results/runs" / identifier / "results.json")


def metrics(record, check):
    return record["checks"][check]["metrics"]
