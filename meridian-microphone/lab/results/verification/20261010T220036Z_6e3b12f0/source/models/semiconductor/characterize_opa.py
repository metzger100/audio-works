#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolated device characterization against primary evidence; errors survive in records."""

from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.metrics import at_frequency


from characterize_base import compare, refinement


def opa(exp, m):
    rows = []
    measurements = {}
    exp.partial[m["id"]] = dict(comparisons=rows, measurements=measurements)

    def circuit(v=0, rs=0, load=10000, gain=1):
        feedback = "out" if gain == 1 else "fb"
        return (
            f"Vp p 0 18\nVn n 0 -18\nVin src 0 DC {v} AC 1 SIN(0 {20 / gain} 1000)\n"
            + (f"Rsource src inp {rs}\n" if rs else "Vlink src inp 0\n")
            + f"Xu inp {feedback} p n out {m['subcircuit']}\nRload out 0 {load}\n"
            + ("Rf out fb 9k\nRg fb 0 1k" if gain == 10 else "")
        )

    for t in [-40, -10, 25, 50, 125]:
        out = exp.execute(
            m,
            f"small_{t}",
            circuit(),
            "op\nwrite op.raw v(out) i(vp) i(vn) i(vin)\nac dec 64 1 100Meg\nwrite ac.raw v(out) i(vin)\nnoise v(out) Vin dec 64 1 100k 1\nsetplot noise1\nwrite noise.raw all",
            ["op.raw", "ac.raw", "noise.raw"],
            t,
        )
        if not out:
            continue
        op = out["op.raw"]
        ac = out["ac.raw"]
        noise = out["noise.raw"]
        f = ac["frequency"].real
        gain = abs(ac["v(out)"])
        bandwidth = float(np.interp(1 / np.sqrt(2), gain[::-1], f[::-1]))
        cap = float((-at_frequency(f, ac["i(vin)"], 1000) / (2j * np.pi * 1000)).real)
        measurements[f"bias_{t}"] = dict(
            iq_a=-float(op["i(vp)"][0]),
            ib_a=float(op["i(vin)"][0]),
            offset_v=float(op["v(out)"][0]),
            follower_bandwidth_hz=bandwidth,
            ciss_f=cap,
            en_1k=float(at_frequency(noise["frequency"], noise["inoise_spectrum"], 1000)),
        )
        if t == 25:
            rows.extend(
                [
                    compare(
                        "iq_max", -op["i(vp)"][0], hi=0.0013, condition="table6.7,VS36V,VCM0,RL10k"
                    ),
                    compare(
                        "ib_max",
                        abs(op["i(vin)"][0]),
                        hi=20e-12,
                        condition="table6.7,25C,mid-supply",
                    ),
                    compare(
                        "ciss",
                        cap,
                        typ=6.4e-12,
                        condition="common-mode Cin; follower bootstraps differential Cin",
                    ),
                ]
            )
            for hz, typ in exp.refs["opa197"]["voltage_noise_v_sqrt_hz"].items():
                rows.append(
                    compare(
                        f"en_{hz}",
                        at_frequency(noise["frequency"], noise["inoise_spectrum"], hz),
                        typ=typ,
                        condition="table6.7,VS36V,VCM0",
                    )
                )
    # Current noise: separate input-current observer with input clamped (1 ohm noiseless CCVS).
    c = circuit() + "\nHinput inoise 0 Vin 1"
    out = exp.execute(
        m,
        "current_noise",
        c,
        "noise v(inoise) Vin dec 64 1 100k 1\nsetplot noise1\nwrite noise.raw all",
        ["noise.raw"],
    )
    if out:
        value = float(
            at_frequency(out["noise.raw"]["frequency"], out["noise.raw"]["onoise_spectrum"], 1000)
        )
        measurements["in_1k_a_sqrt_hz"] = value
        rows.append(
            compare(
                "current_noise_1k",
                value,
                typ=1.5e-15,
                condition="input-current observer,clamped input,unity follower",
            )
        )
    # DC feedback is closed through Lbias; AC loop is open through Cbreak.
    # A follower's peaking/closed-loop -3dB frequency is not GBW.
    openloop = f"Vp p 0 18\nVn n 0 -18\nVin inp 0 DC 0 AC 1\nXu inp inv p n out {m['subcircuit']}\nLbias out inv 1G\nCbreak inv 0 1\nRload out 0 10k"
    out = exp.execute(
        m,
        "open_loop_bandwidth",
        openloop,
        "op\nwrite op.raw v(out)\nac dec 96 1 100Meg\nwrite ac.raw v(out) v(inv)",
        ["op.raw", "ac.raw"],
    )
    if out:
        f = out["ac.raw"]["frequency"].real
        a = abs(out["ac.raw"]["v(out)"])
        cross = np.where(a < 1)[0]
        if len(cross) and cross[0] > 0:
            i = cross[0]
            gbw = float(
                np.exp(np.interp(0, np.log(a[i - 1 : i + 1][::-1]), np.log(f[i - 1 : i + 1][::-1])))
            )
            measurements["open_loop_unity_gain_hz"] = gbw
            rows.append(
                compare(
                    "gbw",
                    gbw,
                    typ=1e7,
                    condition="DC closed/AC open loop using1GH and1F fixture,RL10k",
                )
            )
        else:
            rows.append(
                dict(
                    name="gbw",
                    status="unqualified",
                    evidence="missing_unity_crossing",
                    condition="AC sweep did not bracket unity open-loop gain",
                )
            )
    for sign in [1, -1]:
        out = exp.execute(
            m,
            f"dc_clipping_branch_{sign}",
            circuit(load=2000, gain=10),
            f"dc Vin 0 {sign * 2} {sign * 0.005}\nwrite dc.raw v(out) i(vp) i(vn)",
            ["dc.raw"],
        )
        if out:
            v = out["dc.raw"]["v(out)"]
            headroom = 18 - sign * v[-1]
            measurements[f"clipping_{sign}"] = dict(
                headroom_v=float(headroom), output_v=float(v[-1])
            )
            rows.append(
                compare(
                    f"output_headroom_{sign}",
                    headroom,
                    hi=0.5,
                    condition="RL2k plus10k feedback load,VS36V; branch from converged0V input,CM within range",
                )
            )
    out = exp.execute(
        m,
        "loaded_supply_ramp",
        circuit(load=2000),
        "dc Vin 0 5 .025\nwrite dc.raw v(out) i(vp) i(vn)",
        ["dc.raw"],
    )
    if out:
        current = -out["dc.raw"]["i(vp)"][-1]
        measurements["loaded_supply_a"] = float(current)
        rows.append(
            compare(
                "output_supply_current",
                current,
                typ=0.0035,
                condition="5V/2k +1mA Iq; circuit KCL consistency, not datasheet maximum",
            )
        )
    fine = exp.execute(
        m,
        "noise_refined",
        circuit(),
        "noise v(out) Vin dec 128 1 100k 1\nsetplot noise1\nwrite noise.raw all",
        ["noise.raw"],
        refine=True,
    )
    if fine and "bias_25" in measurements:
        value = float(
            at_frequency(fine["noise.raw"]["frequency"], fine["noise.raw"]["inoise_spectrum"], 1000)
        )
        rows.append(
            compare(
                "noise_refinement",
                abs(value / measurements["bias_25"]["en_1k"] - 1),
                hi=0.01,
                evidence="numerical_refinement",
            )
        )
    trans = []
    for step in [1e-6, 0.5e-6]:
        out = exp.execute(
            m,
            f"clipping_tran_{step}",
            circuit(load=2000, gain=10),
            f"tran {step} .02 .01 {step}\nwrite tran.raw v(out) i(vp)",
            ["tran.raw"],
            refine=step == 0.5e-6,
        )
        if out:
            trans.append(out["tran.raw"])
    if len(trans) == 2:
        rows.append(refinement(trans[0], trans[1], "time", "v(out)", "clipping_refinement"))
    return dict(
        comparisons=rows,
        measurements=measurements,
        scope="tested nominal CMOS macro DC/AC/noise/clipping and supply; no THD/process/thermal/crossover qualification",
    )
