from meridian_lab.core import read_yaml

"""Render the initial infrastructure report from immutable experiment records.

This is reporting only: it changes no netlist, specification, result or archive.
Run from the lab: MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python research/render_initial_report.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
BASE = "20261005T121311Z_f11a711a"
PROPOSAL = "20261005T121440Z_8f1bc311"
OPTIMIZATION = "20261005T114342Z_optimization_c7e7091b"


def read_run(identifier):
    return read_yaml(ROOT / "results/runs" / identifier / "results.json")


def metrics(record, check):
    return record["checks"][check]["metrics"]


def _text(name):
    return Path(__file__).with_name("render-initial-report-text").joinpath(name).read_text()[:-1]


import json as json
import hashlib as hashlib
