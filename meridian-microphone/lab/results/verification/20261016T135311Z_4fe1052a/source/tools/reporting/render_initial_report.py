"""Render the initial infrastructure report from immutable experiment records.

This is reporting only: it changes no netlist, specification, result or archive.
Run from the lab: MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python tools/reporting/render_initial_report.py
"""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "src"))
BASE = "20261005T121311Z_f11a711a"
PROPOSAL = "20261005T121440Z_8f1bc311"
OPTIMIZATION = "20261005T114342Z_optimization_c7e7091b"


from initial_common import read_run as read_run, metrics as metrics
from initial_plots import stage as stage_1
from initial_summary import stage as stage_2
from initial_receipt import stage as stage_3


def main():
    context = locals().copy()
    context = stage_1(context)
    context = stage_2(context)
    context = stage_3(context)
    return context


if __name__ == "__main__":
    main()
