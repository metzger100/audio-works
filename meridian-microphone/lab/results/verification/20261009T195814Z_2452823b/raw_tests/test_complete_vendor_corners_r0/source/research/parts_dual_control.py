#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite gap-closing controls; no generic model fitting or microphone selection."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "models/semiconductor"), str(ROOT / "research")]
from meridian_lab.metrics import at_frequency
from characterize import interpolate, compare
from parts_controls_001 import capacitance

EXTRA = [
    "research/parts_controls_002.py",
    "research/parts_controls_001.py",
    "research/devices/parts-control-plan-003.yaml",
    "tools/ngspice-run",
]


def dual(exp, m, ref):
    rows = []
    values = {}

    def circuit(vg=0, vd=10):
        return f"Vd d 0 {vd}\nVg g 0 DC {vg} AC 1\nJq d g 0 {m['subcircuit']}\nHout out 0 Vd 1"

    bias = None
    for t in [-10, 25, 50]:
        out = exp.execute(
            m, f"transfer_{t}", circuit(), "dc Vg -2 0 .001\nwrite dc.raw v(g) i(vd)", ["dc.raw"], t
        )
        if out:
            d = out["dc.raw"]
            values[f"idss_{t}_a"] = -float(d["i(vd)"][-1])
            if t == 25:
                rows.append(
                    compare(
                        "idss_25c",
                        values[f"idss_{t}_a"],
                        *ref["idss_a"],
                        condition=ref["source"] + " VDS10 VGS0",
                    )
                )
                bias = interpolate(d, -d["i(vd)"], 0.002, "v(g)")
    ns = []
    if bias is not None:
        for n in [64, 128]:
            out = exp.execute(
                m,
                f"noise_{n}",
                circuit(bias),
                f"op\nwrite op.raw i(vd)\nnoise v(out) Vg dec {n} 1 100k 1\nsetplot noise1\nwrite noise.raw all",
                ["op.raw", "noise.raw"],
                refine=n == 128,
            )
            if out:
                d = out["noise.raw"]
                ns.append(
                    [
                        float(at_frequency(d["frequency"], d["inoise_spectrum"], f))
                        for f in [10, 1000]
                    ]
                )
                values["noise_2ma_v_sqrt_hz"] = dict(zip([10, 1000], ns[-1]))
        if ns:
            for i, f in enumerate([10, 1000]):
                rows.append(
                    compare(
                        f"en_{f}",
                        ns[-1][i],
                        typ=ref["en_2ma"][f],
                        condition=ref["source"]
                        + " IC2mA VDS10 25C NBW1Hz; note3 typical disclaimer",
                    )
                )
        if len(ns) == 2:
            for i, f in enumerate([10, 1000]):
                rows.append(
                    compare(
                        f"noise_refinement_{f}",
                        abs(ns[1][i] / ns[0][i] - 1),
                        hi=0.01,
                        evidence="numerical_refinement",
                    )
                )
    out = exp.execute(m, "ciss", circuit(), "ac lin 1 1Meg 1Meg\nwrite ac.raw i(vg)", ["ac.raw"])
    if out:
        rows.append(
            compare(
                "ciss",
                capacitance(-out["ac.raw"]["i(vg)"][0], 1e6),
                typ=ref["ciss_typ_f"],
                condition="VDS10 VGS0 1MHz25C",
            )
        )
    out = exp.execute(m, "gate_leak", circuit(-25, 0), "op\nwrite op.raw i(vg)", ["op.raw"])
    if out:
        rows.append(
            compare(
                "gate_leak",
                abs(float(out["op.raw"]["i(vg)"][0])),
                hi=ref["leak_max_a"],
                condition="VGS-25 VDS0 25C",
            )
        )
    values["scope"] = (
        "One nominal half; ordinary matching limits documentary only, no substrate/dual covariance/mismatch validation."
    )
    return rows, values
