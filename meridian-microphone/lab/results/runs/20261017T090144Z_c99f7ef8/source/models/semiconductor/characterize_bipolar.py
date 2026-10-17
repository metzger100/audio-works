#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolated device characterization against primary evidence; errors survive in records."""

from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.metrics import at_frequency


from characterize_base import interpolate, compare, bjt_circuit


def bipolar(exp, m):
    pol = "npn" if m["device_id"] == "bc846b" else "pnp"
    s = 1 if pol == "npn" else -1
    rows = []
    measurements = {}
    curves = {}
    bias = None
    sub = m["subcircuit"]
    exp.partial[m["id"]] = dict(comparisons=rows, measurements=measurements)
    for t in [-55, -10, 25, 50, 150]:
        out = exp.execute(
            m,
            f"transfer_{t}",
            bjt_circuit(sub, pol, 0.65),
            f"dc Vb {s * 0.3} {s * 0.9} {s * 0.001}\nwrite transfer.raw v(b) i(vc) i(vb)",
            ["transfer.raw"],
            t,
        )
        if not out:
            continue
        raw = out["transfer.raw"]
        cur = -s * raw["i(vc)"]
        curves[t] = raw
        vb = abs(interpolate(raw, cur, 0.002, "v(b)"))
        ib = abs(interpolate(raw, cur, 0.002, "i(vb)"))
        measurements[f"bias_{t}"] = {"vbe_v": vb, "base_current_a": ib, "hfe": 0.002 / ib}
        if t == 25:
            bias = vb
            ref = exp.refs["bipolar"][m["device_id"]]
            rows.append(
                compare("hfe", 0.002 / ib, *ref["hfe_limits"], condition="table8,VCE5V,IC2mA,25C")
            )
            rows.append(
                compare("vbe", vb, *ref["vbe_limits_v"], condition="table8,VCE5V,IC2mA,25C")
            )
    if bias is None:
        return dict(
            comparisons=rows,
            measurements=measurements,
            scope="failed DC prevents further meaningful characterization",
        )
    out = exp.execute(
        m,
        "output",
        bjt_circuit(sub, pol, bias),
        f"dc Vc {s * 0.01} {s * 20} {s * 0.05}\nwrite output.raw v(c) i(vc) i(vb)",
        ["output.raw"],
    )
    fine = exp.execute(
        m,
        "transfer_refined",
        bjt_circuit(sub, pol, bias),
        f"dc Vb {s * 0.3} {s * 0.9} {s * 0.0005}\nwrite transfer.raw v(b) i(vc) i(vb)",
        ["transfer.raw"],
        refine=True,
    )
    if fine and 25 in curves:
        value = (
            abs(
                abs(
                    interpolate(
                        fine["transfer.raw"], -s * fine["transfer.raw"]["i(vc)"], 0.002, "v(b)"
                    )
                )
                - bias
            )
            / bias
        )
        rows.append(compare("bias_refinement", value, hi=0.01, evidence="numerical_refinement"))
    vb10 = abs(interpolate(curves[25], -s * curves[25]["i(vc)"], 0.01, "v(b)"))
    out = exp.execute(
        m,
        "bandwidth",
        bjt_circuit(sub, pol, vb10),
        "op\nwrite op.raw i(vc) i(vb)\nac dec 64 100k 10G\nwrite ac.raw i(vc) i(vb)",
        ["op.raw", "ac.raw"],
    )
    if out:
        raw = out["ac.raw"]
        h = abs(raw["i(vc)"] / raw["i(vb)"])
        f = raw["frequency"].real
        ft = float(np.interp(1, h[::-1], f[::-1])) if h[0] > 1 and h[-1] < 1 else None
        h100 = float(at_frequency(f, h, 1e8))
        measurements["bandwidth"] = {
            "unity_current_gain_hz": ft,
            "hfe_at100MHz": h100,
            "bias_ic_a": float(abs(out["op.raw"]["i(vc)"][0])),
        }
        rows.append(
            compare(
                "ft_100MHz_test",
                h100 * 1e8,
                lo=1e8,
                condition="manufacturer fT test at100MHz,VCE5V,IC10mA",
            )
        )
    # Reverse collector-base admittance with ideal zero emitter current, matching datasheet.
    circuit = f"Vc c 0 DC {s * 10} AC 1\nVb b 0 0\nRreturn e b 1T\nXq c b e {sub}"
    out = exp.execute(
        m,
        "collector_capacitance",
        circuit,
        "op\nwrite op.raw i(vc)\nac lin 1 1Meg 1Meg\nwrite ac.raw i(vc)",
        ["op.raw", "ac.raw"],
    )
    if out:
        cap = float((-out["ac.raw"]["i(vc)"][0] / (2j * np.pi * 1e6)).real)
        measurements["cc_f"] = cap
        ref = exp.refs["bipolar"][m["device_id"]]
        rows.append(
            compare(
                "cc_typical",
                cap,
                typ=ref["cc_typical_f"],
                condition=exp.refs["bipolar"]["cc_condition"],
            )
        )
        if ref["cc_max_f"]:
            rows.append(compare("cc_guaranteed_max", cap, hi=ref["cc_max_f"]))
        refined = exp.execute(
            m,
            "collector_cap_return_refinement",
            circuit.replace("1T", "1G"),
            "ac lin 1 1Meg 1Meg\nwrite ac.raw i(vc)",
            ["ac.raw"],
            refine=True,
        )
        if refined:
            other = float((-refined["ac.raw"]["i(vc)"][0] / (2j * np.pi * 1e6)).real)
            rows.append(
                compare(
                    "collector_cap_return_refinement",
                    abs(other / cap - 1),
                    hi=0.01,
                    evidence="numerical_refinement",
                    condition="1T versus1G explicit emitter return; approximate open emitter",
                )
            )
    saturation = f"Ic 0 c {s * 0.01}\nIb 0 b {s * 0.0005}\nXq c b 0 {sub}"
    out = exp.execute(m, "saturation", saturation, "op\nwrite op.raw v(c) v(b)", ["op.raw"])
    if out:
        rows.append(
            compare(
                "vcesat",
                abs(out["op.raw"]["v(c)"][0]),
                hi=exp.refs["bipolar"][m["device_id"]]["vcesat_max_v"],
                condition=exp.refs["bipolar"]["saturation_condition"],
            )
        )
    ib200 = abs(interpolate(curves[25], -s * curves[25]["i(vc)"], 0.0002, "i(vb)"))
    vb200 = abs(interpolate(curves[25], -s * curves[25]["i(vc)"], 0.0002, "v(b)")) + ib200 * 2000
    out = exp.execute(
        m,
        "noise_figure",
        bjt_circuit(sub, pol, vb200, 2000),
        "op\nwrite op.raw i(vc) i(vb)\nnoise v(out) Vb dec 48 1 100k 1\nsetplot noise1\nwrite noise.raw all",
        ["op.raw", "noise.raw"],
    )
    if out:
        noise = out["noise.raw"]
        en = float(at_frequency(noise["frequency"], noise["inoise_spectrum"], 1000))
        nf = 10 * np.log10(en**2 / (4 * 1.380649e-23 * 298.15 * 2000))
        measurements["noise"] = {
            "nf_1khz_db": float(nf),
            "en_total_source_referred_1khz": en,
            "actual_ic_a": float(abs(out["op.raw"]["i(vc)"][0])),
            "flicker_present": False,
        }
        rows.append(
            compare("noise_figure_max", nf, hi=10, condition=exp.refs["bipolar"]["noise_figure"])
        )
        rows.append(
            compare(
                "noise_figure_typical",
                nf,
                1.6,
                2.4,
                evidence="typical_accuracy_screen",
                condition="2 dB typical; +/-0.4dB research screen",
            )
        )
    return dict(
        comparisons=rows,
        measurements=measurements,
        scope="nominal DC/AC/NF only; KF omitted; no qualified low-noise input/population/SOA",
    )
