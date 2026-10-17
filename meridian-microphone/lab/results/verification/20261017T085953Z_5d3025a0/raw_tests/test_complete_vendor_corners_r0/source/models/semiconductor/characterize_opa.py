# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolated device characterization against primary evidence; errors survive in records."""

from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.metrics import at_frequency
from characterize_base import compare, refinement


class OpaCharacterization:
    def __init__(self, exp, model):
        self.exp = exp
        self.model = model
        self.comparisons = []
        self.measurements = {}
        self.exp.partial[self.model["id"]] = dict(
            comparisons=self.comparisons, measurements=self.measurements
        )

    def circuit(self, v=0, rs=0, load=10000, gain=1):
        feedback = "out" if gain == 1 else "fb"
        return (
            f"Vp p 0 18\nVn n 0 -18\nVin src 0 DC {v} AC 1 SIN(0 {20 / gain} 1000)\n"
            + (f"Rsource src inp {rs}\n" if rs else "Vlink src inp 0\n")
            + f"Xu inp {feedback} p n out {self.model['subcircuit']}\nRload out 0 {load}\n"
            + ("Rf out fb 9k\nRg fb 0 1k" if gain == 10 else "")
        )

    def small_signal(self):
        for t in [-40, -10, 25, 50, 125]:
            out = self.exp.execute(
                self.model,
                f"small_{t}",
                self.circuit(),
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
            self.measurements[f"bias_{t}"] = dict(
                iq_a=-float(op["i(vp)"][0]),
                ib_a=float(op["i(vin)"][0]),
                offset_v=float(op["v(out)"][0]),
                follower_bandwidth_hz=bandwidth,
                ciss_f=cap,
                en_1k=float(at_frequency(noise["frequency"], noise["inoise_spectrum"], 1000)),
            )
            if t == 25:
                self.comparisons.extend(
                    [
                        compare(
                            "iq_max",
                            -op["i(vp)"][0],
                            hi=0.0013,
                            condition="table6.7,VS36V,VCM0,RL10k",
                        ),
                        compare(
                            "ib_max",
                            abs(op["i(vin)"][0]),
                            hi=2e-11,
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
                for hz, typ in self.exp.refs["opa197"]["voltage_noise_v_sqrt_hz"].items():
                    self.comparisons.append(
                        compare(
                            f"en_{hz}",
                            at_frequency(noise["frequency"], noise["inoise_spectrum"], hz),
                            typ=typ,
                            condition="table6.7,VS36V,VCM0",
                        )
                    )

    def current_noise(self):
        c = self.circuit() + "\nHinput inoise 0 Vin 1"
        out = self.exp.execute(
            self.model,
            "current_noise",
            c,
            "noise v(inoise) Vin dec 64 1 100k 1\nsetplot noise1\nwrite noise.raw all",
            ["noise.raw"],
        )
        if out:
            value = float(
                at_frequency(
                    out["noise.raw"]["frequency"], out["noise.raw"]["onoise_spectrum"], 1000
                )
            )
            self.measurements["in_1k_a_sqrt_hz"] = value
            self.comparisons.append(
                compare(
                    "current_noise_1k",
                    value,
                    typ=1.5e-15,
                    condition="input-current observer,clamped input,unity follower",
                )
            )

    def open_loop(self):
        openloop = f"Vp p 0 18\nVn n 0 -18\nVin inp 0 DC 0 AC 1\nXu inp inv p n out {self.model['subcircuit']}\nLbias out inv 1G\nCbreak inv 0 1\nRload out 0 10k"
        out = self.exp.execute(
            self.model,
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
                    np.exp(
                        np.interp(0, np.log(a[i - 1 : i + 1][::-1]), np.log(f[i - 1 : i + 1][::-1]))
                    )
                )
                self.measurements["open_loop_unity_gain_hz"] = gbw
                self.comparisons.append(
                    compare(
                        "gbw",
                        gbw,
                        typ=10000000.0,
                        condition="DC closed/AC open loop using1GH and1F fixture,RL10k",
                    )
                )
            else:
                self.comparisons.append(
                    dict(
                        name="gbw",
                        status="unqualified",
                        evidence="missing_unity_crossing",
                        condition="AC sweep did not bracket unity open-loop gain",
                    )
                )

    def clipping(self):
        for sign in [1, -1]:
            out = self.exp.execute(
                self.model,
                f"dc_clipping_branch_{sign}",
                self.circuit(load=2000, gain=10),
                f"dc Vin 0 {sign * 2} {sign * 0.005}\nwrite dc.raw v(out) i(vp) i(vn)",
                ["dc.raw"],
            )
            if out:
                v = out["dc.raw"]["v(out)"]
                headroom = 18 - sign * v[-1]
                self.measurements[f"clipping_{sign}"] = dict(
                    headroom_v=float(headroom), output_v=float(v[-1])
                )
                self.comparisons.append(
                    compare(
                        f"output_headroom_{sign}",
                        headroom,
                        hi=0.5,
                        condition="RL2k plus10k feedback load,VS36V; branch from converged0V input,CM within range",
                    )
                )

    def loaded_supply(self):
        out = self.exp.execute(
            self.model,
            "loaded_supply_ramp",
            self.circuit(load=2000),
            "dc Vin 0 5 .025\nwrite dc.raw v(out) i(vp) i(vn)",
            ["dc.raw"],
        )
        if out:
            current = -out["dc.raw"]["i(vp)"][-1]
            self.measurements["loaded_supply_a"] = float(current)
            self.comparisons.append(
                compare(
                    "output_supply_current",
                    current,
                    typ=0.0035,
                    condition="5V/2k +1mA Iq; circuit KCL consistency, not datasheet maximum",
                )
            )

    def refine_noise(self):
        fine = self.exp.execute(
            self.model,
            "noise_refined",
            self.circuit(),
            "noise v(out) Vin dec 128 1 100k 1\nsetplot noise1\nwrite noise.raw all",
            ["noise.raw"],
            refine=True,
        )
        if fine and "bias_25" in self.measurements:
            value = float(
                at_frequency(
                    fine["noise.raw"]["frequency"], fine["noise.raw"]["inoise_spectrum"], 1000
                )
            )
            self.comparisons.append(
                compare(
                    "noise_refinement",
                    abs(value / self.measurements["bias_25"]["en_1k"] - 1),
                    hi=0.01,
                    evidence="numerical_refinement",
                )
            )

    def slew(self):
        trans = []
        for step in [1e-06, 5e-07]:
            out = self.exp.execute(
                self.model,
                f"clipping_tran_{step}",
                self.circuit(load=2000, gain=10),
                f"tran {step} .02 .01 {step}\nwrite tran.raw v(out) i(vp)",
                ["tran.raw"],
                refine=step == 5e-07,
            )
            if out:
                trans.append(out["tran.raw"])
        if len(trans) == 2:
            self.comparisons.append(
                refinement(trans[0], trans[1], "time", "v(out)", "clipping_refinement")
            )

    def run(self):
        self.small_signal()
        self.current_noise()
        self.open_loop()
        self.clipping()
        self.loaded_supply()
        self.refine_noise()
        self.slew()
        return dict(
            comparisons=self.comparisons,
            measurements=self.measurements,
            scope="tested nominal CMOS macro DC/AC/noise/clipping and supply; no THD/process/thermal/crossover qualification",
        )


def opa(exp, m):
    return OpaCharacterization(exp, m).run()
