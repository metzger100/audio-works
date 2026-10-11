# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce comparison 001 from immutable records and original local waveforms.

No simulator, candidate, specification, archive or original result is modified.
Run from lab: .venv/bin/python tools/reporting/compare_architectures.py
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results/reports/architecture-comparison-001"


from comparison_common import (
    sha as sha,
    dump as dump,
    table as table,
    noise_group as noise_group,
    verify_partition as verify_partition,
    cohort_key as cohort_key,
    require_common as require_common,
    pareto as pareto,
    parse_elements as parse_elements,
    diagram as diagram,
)
from comparison_records import stage as stage_1
from comparison_metrics import stage as stage_2
from comparison_tables import stage as stage_3
from comparison_outputs import stage as stage_4


def run():
    context = locals().copy()
    context = stage_1(context)
    context = stage_2(context)
    context = stage_3(context)
    context = stage_4(context)
    return context


if __name__ == "__main__":
    run()
