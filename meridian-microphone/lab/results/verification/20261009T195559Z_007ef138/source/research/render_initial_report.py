"""Render the initial infrastructure report from immutable experiment records.

This is reporting only: it changes no netlist, specification, result or archive.
Run from the lab: MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python research/render_initial_report.py
"""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
BASE = "20261005T121311Z_f11a711a"
PROPOSAL = "20261005T121440Z_8f1bc311"
OPTIMIZATION = "20261005T114342Z_optimization_c7e7091b"


from render_initial_report_support import read_run as read_run, metrics as metrics
from render_initial_report_stage_1 import stage as stage_1
from render_initial_report_stage_2 import stage as stage_2
from render_initial_report_stage_3 import stage as stage_3


def main():
    context = locals().copy()
    context = stage_1(context)
    context = stage_2(context)
    context = stage_3(context)
    return context


if __name__ == "__main__":
    main()
