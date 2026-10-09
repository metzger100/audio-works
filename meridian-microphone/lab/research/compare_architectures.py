# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce comparison 001 from immutable records and original local waveforms.

No simulator, candidate, specification, archive or original result is modified.
Run from lab: .venv/bin/python research/compare_architectures.py
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results/reports/architecture-comparison-001"


from compare_architectures_support import (
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
from compare_architectures_stage_1 import stage as stage_1
from compare_architectures_stage_2 import stage as stage_2
from compare_architectures_stage_3 import stage as stage_3
from compare_architectures_stage_4 import stage as stage_4


def run():
    context = locals().copy()
    context = stage_1(context)
    context = stage_2(context)
    context = stage_3(context)
    context = stage_4(context)
    return context


if __name__ == "__main__":
    run()
