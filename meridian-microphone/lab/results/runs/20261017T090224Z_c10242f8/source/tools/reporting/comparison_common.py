# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce comparison 001 from immutable records and original local waveforms.

No simulator, candidate, specification, archive or original result is modified.
Run from lab: .venv/bin/python tools/reporting/compare_architectures.py
"""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results/reports/architecture-comparison-001"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


from meridian_lab.bounded import write_csv, write_data

dump = write_data


def table(path, rows, fields=None):
    write_csv(path, rows, fields or list(rows[0]))


def noise_group(vector):
    """Classify one device root, never its already-included noise children."""
    if ".xenv." in vector:
        return "environment (excluded)"
    if ".xcap." in vector:
        return "capsule Johnson surrogate (excluded)"
    if ".xdut." not in vector:
        raise ValueError("Unidentified noise scope: " + vector)
    ref = vector.split(".xdut.", 1)[1].split(".")[0]
    if ref.startswith(("xqout", "xqinvert", "rout", "rinv", "rcout")):
        return "output drive and coupling"
    if ref.startswith(("rpolar", "rback", "rcbackfilter")):
        return "polarization network"
    if ref.startswith(("xqreg", "rharvest", "rreg", "rmid")):
        return "power and midpoint"
    if ref.startswith(("xqservo", "rservo")):
        return "servo"
    if ref.startswith(("xjinput", "xqinput", "xqreference", "xuinput")):
        return "input semiconductor"
    # Explicit remaining input/reference/reset/degeneration resistors.
    if ref.startswith(
        (
            "rbias",
            "rgate",
            "rrear",
            "rsource",
            "rsignal",
            "rref",
            "remitter",
            "rtail",
            "rcollector",
            "rfeedback",
            "rcfeedback",
        )
    ):
        return "input bias, reset and degeneration"
    raise ValueError("Unclassified DUT noise root: " + vector)


def verify_partition(frequency, totals, total):
    groups = defaultdict(list)
    for name in totals:
        groups[noise_group(name)].append(name)
    asd = {
        g: np.sqrt(sum((totals[k] ** 2 for k in names), np.zeros_like(frequency)))
        for g, names in groups.items()
    }
    reconstructed = np.sqrt(sum((v**2 for v in asd.values()), np.zeros_like(frequency)))
    closure = float(np.max(np.abs(reconstructed - total) / np.maximum(total, 1e-30)))
    if closure > 1e-5:
        raise ValueError(f"Contribution power does not close: {closure}")
    return groups, asd, closure


def cohort_key(record):
    return (
        record["spec_sha256"],
        record["suite_sha256"],
        record["backend"],
        json.dumps(record["source_manifest"], sort_keys=True),
    )


def require_common(records):
    if len({cohort_key(r) for r in records}) != 1:
        raise ValueError("Different frozen comparison cohorts")


def pareto(rows, axes):
    """Scoped all-minimize projection: missing axes cannot dominate."""
    complete = [
        r for r in rows if all(type(r.get(a)) in (float, int) and np.isfinite(r[a]) for a in axes)
    ]
    return [
        r["candidate"]
        for r in complete
        if not any(
            all(other[a] <= r[a] for a in axes) and any(other[a] < r[a] for a in axes)
            for other in complete
            if other is not r
        )
    ]


def parse_elements(circuit, params):
    rows = []
    for line in circuit.splitlines():
        if not line.strip() or line.lstrip().startswith(("*", ".")):
            continue
        tokens = line.split()
        ref = tokens[0]
        kind = ref[0].upper()
        if kind == "X":
            nodes, value = tokens[1:-1], tokens[-1]
        elif kind in {"R", "C", "L", "V", "B"}:
            nodes, value = tokens[1:3], " ".join(tokens[3:])
        elif kind == "E":
            nodes = tokens[1:3] if "VOL=" in line else tokens[1:5]
            value = " ".join(tokens[3:]) if "VOL=" in line else " ".join(tokens[5:])
        else:
            raise ValueError("Unsupported element in faithful diagram: " + line)
        if re.fullmatch(r"\{\w+\}", value):
            value = str(params[value[1:-1]])
        rows.append(
            {
                "reference": ref,
                "kind": kind,
                "nodes": nodes,
                "value_or_model": value,
                "source_line": line,
            }
        )
    return rows


def diagram(candidate, elements):
    """Full bipartite connectivity diagram; only zero-V observers collapse.

    All physical and behavioral elements remain explicit. The companion CSV
    retains the uncollapsed node order and original source line.
    """
    alias = {}

    def node(n):
        while n in alias:
            n = alias[n]
        return n

    for e in elements:
        if e["kind"] == "V" and e["value_or_model"] == "0":
            alias[node(e["nodes"][1])] = node(e["nodes"][0])
    lines = [
        "graph DUT {",
        'graph [overlap=false, splines=true, bgcolor="white",',
        f'label="{candidate}: netlist connectivity; zero-V observers collapsed; research only", labelloc=t];',
        'node [fontname="DejaVu Sans", fontsize=10]; edge [fontname="DejaVu Sans", fontsize=8];',
    ]
    names = sorted({node(n) for e in elements for n in e["nodes"]})
    for n in names:
        lines.append(
            f'{json.dumps("n_" + n)} [label={json.dumps(n)}, shape=ellipse, color="#6a8295"];'
        )
    for e in elements:
        if e["kind"] == "V" and e["value_or_model"] == "0":
            continue
        name = "e_" + e["reference"]
        value = e["value_or_model"]
        if len(value) > 65:
            value = value[:62] + "..."
        label = e["reference"] + "\n" + value
        color = (
            "#a14265" if e["kind"] in {"B", "E"} else "#246957" if e["kind"] == "X" else "#555555"
        )
        lines.append(f'{json.dumps(name)} [shape=box,label={json.dumps(label)},color="{color}"];')
        for i, n in enumerate(e["nodes"], 1):
            lines.append(f'{json.dumps("n_" + node(n))} -- {json.dumps(name)} [label="{i}"];')
    lines.append("}")
    path = OUT / f"{candidate.replace(chr(95), chr(45))}-connectivity.dot"
    payload = "\n".join(lines) + "\n"
    for i, name in enumerate(names):
        payload = payload.replace(json.dumps("n_" + name), "n" + str(i))
    payload = re.sub(r"(?m)^\s+", "", payload)
    payload = re.sub(r"\s*(--|\[|\]|=|,)\s*", r"\1", payload)
    payload = payload.replace(";\n", ";").replace("DejaVu Sans", "sans")
    payload = payload.replace(
        ": netlist connectivity; zero-V observers collapsed; research only",
        " connectivity; research",
    )
    if len(payload) > 15000:
        raise ValueError("Connectivity graph exceeds text budget; restructure the diagram")
    path.write_text(payload)

    subprocess.run(
        ["dot", "-Kneato", "-Tsvg", str(path), "-o", str(path.with_suffix(".svg"))], check=True
    )


from meridian_lab.core import parse_raw as parse_raw
from meridian_lab.metrics import (
    at_frequency as at_frequency,
    device_noise_totals as device_noise_totals,
    integrate_asd as integrate_asd,
)
