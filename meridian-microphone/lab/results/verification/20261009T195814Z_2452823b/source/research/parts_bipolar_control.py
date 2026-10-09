#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite Prompt06 controls; no model fitting and no candidate qualification."""

from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "models/semiconductor")]
from meridian_lab.metrics import at_frequency
from characterize import interpolate, compare


def bipolar(exp, m, refs):
    rows = []
    values = {}
    sub = m["subcircuit"]

    def circuit(v=0.6, rs=0, vc=5):
        return f"Vc c 0 {vc}\nVin in 0 DC {v} AC 1\nRsrc in b {rs if rs else 1e-6}\nXq c b 0 {sub}\nHout out 0 Vc 1"

    biases = {}
    for t in [-10, 25, 50]:
        out = exp.execute(
            m,
            f"transfer_{t}",
            circuit(),
            "dc Vin .3 1 .0005\nwrite dc.raw v(in) i(vc) i(vin)",
            ["dc.raw"],
            t,
        )
        if not out:
            continue
        d = out["dc.raw"]
        cur = -d["i(vc)"]
        values[f"grid_{t}"] = []
        for i in [0.0001, 0.001, 0.002, 0.01]:
            vb = interpolate(d, cur, i, "v(in)")
            ib = float(np.interp(vb, d["v(in)"], -d["i(vin)"]))
            values[f"grid_{t}"].append({"ic_a": i, "vbe_v": vb, "ib_a": ib, "hfe": i / ib})
            if t == 25:
                biases[i] = vb
                if i in refs["hfe_min"]:
                    rows.append(
                        compare(
                            f"hfe_{i}",
                            i / ib,
                            lo=refs["hfe_min"][i],
                            hi=refs.get("hfe_max"),
                            condition=refs["source"] + " VCE5V 25C",
                        )
                    )
    out = exp.execute(
        m,
        "noise_bias_rs2k",
        circuit(rs=2000),
        "dc Vin .3 1.5 .0005\nwrite dc.raw v(in) i(vc)",
        ["dc.raw"],
    )
    if out:
        v = interpolate(out["dc.raw"], -out["dc.raw"]["i(vc)"], 0.0002, "v(in)")
        ns = []
        for density in [64, 128]:
            out = exp.execute(
                m,
                f"noise_nf_{density}",
                circuit(v, 2000),
                f"op\nwrite op.raw i(vc)\nnoise v(out) Vin dec {density} 10 15.7k 1\nsetplot noise1\nwrite noise.raw all",
                ["op.raw", "noise.raw"],
                refine=density == 128,
            )
            if out:
                n = out["noise.raw"]
                ns.append(nf_db(n["frequency"], n["inoise_spectrum"], 2000, 298.15))
                values["nf_db"] = ns[-1]
                values["nf_actual_ic_a"] = -float(out["op.raw"]["i(vc)"][0])
        if ns:
            values["nf_scope"] = (
                "Broadband integrated metric only; source specifies frequency sweep, BC850C B200Hz. No broadband NF validation inferred."
            )
            point = float(at_frequency(n["frequency"], n["inoise_spectrum"], 1000))
            point_nf = 10 * np.log10(point**2 / (4 * 1.380649e-23 * 298.15 * 2000))
            values["nf_1khz_local_density_db"] = float(point_nf)
            rows.append(
                compare(
                    "nf_1khz_density_screen",
                    point_nf,
                    hi=refs["nf_max_db"],
                    evidence="conditional_frequency_screen",
                    condition="Rs2kohm IC200uA VCE5V25C; local density approximation to narrowband NF; exact measurement filter unmodeled",
                )
            )
        if len(ns) == 2:
            rows.append(
                compare(
                    "nf_refinement_ratio",
                    abs(10 ** ((ns[1] - ns[0]) / 10) - 1),
                    hi=0.01,
                    evidence="numerical_refinement",
                )
            )
    # Floating emitter is regularized by 1Pohm, whose leakage remains explicit.
    c = f"Vc c 0 DC 10 AC 1\nVb b 0 0\nRe e 0 1e15\nXq c b e {sub}"
    out = exp.execute(m, "collector_cap", c, "ac lin 1 1Meg 1Meg\nwrite ac.raw i(vc)", ["ac.raw"])
    if out:
        cap = capacitance(-out["ac.raw"]["i(vc)"][0], 1e6)
        values["collector_cap_f"] = cap
        rows.append(
            compare(
                "collector_cap",
                cap,
                hi=refs.get("ccb_max_f"),
                typ=refs.get("ccb_typ_f"),
                condition="VCB10V 1MHz emitter open approximated1Pohm; fixture leakage explicit",
            )
        )
    if m["device_id"] == "pmbt5551":
        for t in [25, 100]:
            out = exp.execute(
                m,
                f"icbo_{t}",
                c.replace("DC 10 AC 1", "DC 120 AC 1"),
                "op\nwrite op.raw i(vc)",
                ["op.raw"],
                t,
            )
            if out:
                val = abs(float(out["op.raw"]["i(vc)"][0]))
                values[f"icbo_{t}_a"] = val
                rows.append(
                    compare(
                        f"icbo_{t}",
                        val,
                        hi=50e-9 if t == 25 else 50e-6,
                        condition="VCB120V open emitter1Pohm; PMBT5551 table",
                    )
                )
        if 0.002 in biases:
            out = exp.execute(
                m,
                "p48_coupled_isothermal",
                circuit(biases[0.002], vc=52),
                "op\nwrite op.raw i(vc) i(vin)",
                ["op.raw"],
                102,
            )
            if out:
                values["p48_isothermal_current_a"] = -float(out["op.raw"]["i(vc)"][0])
            values["p48_scope"] = (
                "52V*2mA*500K/W+50C=102C; fixed25C base voltage at102C, no electrothermal feedback/SOA validation"
            )
    values["noise_scope"] = (
        "KF absent; NF agreement cannot establish separate en/in, flicker law or another bias/source impedance"
    )
    return rows, values


from parts_control_math import nf_db, capacitance
