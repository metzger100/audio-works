# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolated device characterization against primary evidence; errors survive in records."""

from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.metrics import at_frequency
from characterize_base import interpolate, compare, fet_circuit, refinement


class JfetCharacterization:
    def __init__(self, exp, model):
        self.exp = exp
        self.model = model
        self.comparisons = []
        self.measurements = {}
        self.sub = self.model["subcircuit"]
        self.biases = {}
        self.exp.partial[self.model["id"]] = dict(
            comparisons=self.comparisons, measurements=self.measurements
        )

    def transfer(self):
        for t in [-40, -10, 25, 50, 125]:
            out = self.exp.execute(
                self.model,
                f"transfer_{t}",
                fet_circuit(self.sub, -1),
                "dc Vg -1.8 0 .002\nwrite transfer.raw v(g) i(vd) i(vg)",
                ["transfer.raw"],
                t,
            )
            if not out:
                continue
            raw = out["transfer.raw"]
            cur = -raw["i(vd)"]
            self.measurements[f"transfer_{t}"] = {"idss_at_5v_a": float(cur[-1])}
            if t == 25:
                for id_ in [0.0001, 0.002, 0.005]:
                    self.biases[id_] = interpolate(raw, cur, id_, "v(g)")
                for p in self.exp.refs["jfe150"]["curve_observations"]["transfer_figure_6_1"][
                    "points"
                ]:
                    value = float(np.interp(p["vgs_v"], raw["v(g)"], cur))
                    self.comparisons.append(
                        compare(
                            f"typical_transfer_vgs_{p['vgs_v']}",
                            value,
                            *p["current_interval_a"],
                            evidence="typical_curve_reading_interval",
                            condition="Fig6-1,VDS5V,25C",
                        )
                    )

    def idss_gfs(self):
        for t in [-40, 25, 125]:
            out = self.exp.execute(
                self.model,
                f"idss_gfs_{t}",
                fet_circuit(self.sub, 0, 10),
                "op\nwrite op.raw v(g) i(vd)\nac lin 1 1000 1000\nwrite ac.raw i(vd)",
                ["op.raw", "ac.raw"],
                t,
            )
            if out:
                idss = -float(out["op.raw"]["i(vd)"][0])
                gm = abs(out["ac.raw"]["i(vd)"][0])
                self.measurements[f"idss_gfs_{t}"] = {"idss_a": idss, "gfs_s": float(gm)}
                self.comparisons.append(
                    compare(
                        f"idss_{t}",
                        idss,
                        0.024 if t == 25 else 0.022,
                        0.046 if t == 25 else 0.057,
                        condition="table6.5,VDS10V,VGS0",
                    )
                )
                if t == 25:
                    self.comparisons.append(
                        compare("gfs_25", gm, 0.055, 0.08, condition="table6.5,VDS10V,VGS0")
                    )

    def noise(self):
        for id_, vg in self.biases.items():
            out = self.exp.execute(
                self.model,
                f"small_noise_{id_}",
                fet_circuit(self.sub, vg),
                "op\nwrite op.raw i(vd) i(vg)\nac dec 48 1 100Meg\nwrite ac.raw i(vd) i(vg)\nnoise v(out) Vg dec 48 .1 100k 1\nsetplot noise1\nwrite noise.raw all\nnoise v(ig) Vg dec 48 .1 100k 1\nsetplot noise3\nwrite gate_noise.raw all",
                ["op.raw", "ac.raw", "noise.raw", "gate_noise.raw"],
            )
            if not out:
                continue
            op = out["op.raw"]
            ac = out["ac.raw"]
            noise = out["noise.raw"]
            inoise = out["gate_noise.raw"]
            cap = float(
                (-at_frequency(ac["frequency"], ac["i(vg)"], 1000) / (2j * np.pi * 1000)).real
            )
            gm = abs(at_frequency(ac["frequency"], ac["i(vd)"], 1000))
            self.measurements[f"bias_{id_}"] = dict(
                vgs_v=vg,
                id_a=-float(op["i(vd)"][0]),
                gm_s=float(gm),
                ciss_f=cap,
                gate_current_a=float(op["i(vg)"][0]),
                gate_current_noise_1k_a_sqrt_hz=float(
                    at_frequency(inoise["frequency"], inoise["onoise_spectrum"], 1000)
                ),
                voltage_noise_10hz=float(
                    at_frequency(noise["frequency"], noise["inoise_spectrum"], 10)
                ),
                voltage_noise_1khz=float(
                    at_frequency(noise["frequency"], noise["inoise_spectrum"], 1000)
                ),
            )
            for ref in self.exp.refs["jfe150"]["noise_v_sqrt_hz"]:
                if ref["id_a"] == id_:
                    self.comparisons.append(
                        compare(
                            f"en_{id_}_{ref['f_hz']}",
                            at_frequency(noise["frequency"], noise["inoise_spectrum"], ref["f_hz"]),
                            typ=ref["typical"],
                            condition="table6.5,VDS5V,25C",
                        )
                    )
            if id_ == 0.002:
                self.comparisons.append(
                    compare(
                        "ciss_2ma",
                        cap,
                        typ=2.4e-11,
                        condition="table6.5,VDS5V; unspecified capacitance bias follows table default",
                    )
                )
                self.comparisons.append(
                    compare(
                        "in_2ma_1k",
                        self.measurements[f"bias_{id_}"]["gate_current_noise_1k_a_sqrt_hz"],
                        typ=1.8e-15,
                        condition="table6.5; Hgate1ohm noiseless observer",
                    )
                )

    def voltage_limits(self):
        out = self.exp.execute(
            self.model,
            "vgs_limits_10v",
            fet_circuit(self.sub, -1, 10),
            "dc Vg -1.8 0 .001\nwrite transfer.raw v(g) i(vd)",
            ["transfer.raw"],
        )
        if out:
            raw = out["transfer.raw"]
            cur = -raw["i(vd)"]
            for i, limits in [(1e-07, [-1.5, -0.9]), (0.0001, [-1.3, -0.7]), (0.002, [-1.1, -0.5])]:
                self.comparisons.append(
                    compare(
                        f"vgs_at_{i}",
                        interpolate(raw, cur, i, "v(g)"),
                        *limits,
                        condition="table6.5,VDS10V,25C",
                    )
                )

    def output_curve(self):
        out = self.exp.execute(
            self.model,
            "output_curve_minus_0p7",
            fet_circuit(self.sub, -0.7),
            "dc Vd .01 20 .05\nwrite output.raw v(d) i(vd) i(vg)",
            ["output.raw"],
        )
        if out:
            for p in self.exp.refs["jfe150"]["curve_observations"]["output_figure_6_3"]["points"]:
                value = np.interp(
                    p["vds_v"], out["output.raw"]["v(d)"], -out["output.raw"]["i(vd)"]
                )
                self.comparisons.append(
                    compare(
                        f"output_vds_{p['vds_v']}",
                        value,
                        *p["current_interval_a"],
                        evidence="typical_curve_reading_interval",
                        condition="Fig6-3,VGS=-.7,25C",
                    )
                )

    def leakage(self):
        out = self.exp.execute(
            self.model,
            "leakage",
            fet_circuit(self.sub, -0.7, 2, high=5),
            "op\nwrite op.raw i(vg)",
            ["op.raw"],
        )
        if out:
            self.comparisons.append(
                compare(
                    "gate_leakage",
                    abs(out["op.raw"]["i(vg)"][0]),
                    hi=1e-11,
                    condition="table6.5,VDS2V,VGS-.7V,VCH5V,VCL-5V",
                )
            )

    def capacitance(self):
        for vd in [0, 5]:
            out = self.exp.execute(
                self.model,
                f"off_bias_cap_{vd}",
                fet_circuit(self.sub, 0, vd),
                "ac lin 1 1Meg 1Meg\nwrite ac.raw i(vg) i(vd)",
                ["ac.raw"],
            )
            if out:
                self.measurements[f"off_bias_cap_{vd}"] = {
                    "ciss_f": float((-out["ac.raw"]["i(vg)"][0] / (2j * np.pi * 1000000.0)).real),
                    "vgs_v": 0,
                    "vds_v": vd,
                    "condition_status": "explicit_exploratory_off_bias; manufacturer capacitance gate-bias clarification required",
                }

    def refine_noise(self):
        if 0.002 in self.biases:
            out = self.exp.execute(
                self.model,
                "noise_ac_refined",
                fet_circuit(self.sub, self.biases[0.002]),
                "ac dec 96 1 100Meg\nwrite ac.raw i(vd) i(vg)\nnoise v(out) Vg dec 96 .1 100k 1\nsetplot noise1\nwrite noise.raw all",
                ["ac.raw", "noise.raw"],
                refine=True,
            )
            if out and "bias_0.002" in self.measurements:
                actual = float(
                    at_frequency(
                        out["noise.raw"]["frequency"], out["noise.raw"]["inoise_spectrum"], 1000
                    )
                )
                self.comparisons.append(
                    compare(
                        "noise_refinement",
                        abs(actual / self.measurements["bias_0.002"]["voltage_noise_1khz"] - 1),
                        hi=0.01,
                        evidence="numerical_refinement",
                    )
                )

    def clipping(self):
        if 0.002 in self.biases:
            self.circuit = f"Vs rail 0 12\nRd rail d 2k\nVg g 0 DC {self.biases[0.002]} SIN({self.biases[0.002]} .5 1000)\nVh h 0 12\nVl l 0 -5\nXq d g 0 h l {self.sub}"
            tran = []
            for step in [2e-06, 1e-06]:
                out = self.exp.execute(
                    self.model,
                    f"large_signal_{step}",
                    self.circuit,
                    f"tran {step} .02 .01 {step}\nwrite tran.raw v(d) v(g) i(vs)",
                    ["tran.raw"],
                    refine=step == 1e-06,
                )
                if out:
                    tran.append(out["tran.raw"])
            if len(tran) == 2:
                self.comparisons.append(
                    refinement(tran[0], tran[1], "time", "v(d)", "large_signal_refinement")
                )

    def annotate_evidence(self):
        for row in self.comparisons:
            if self.model["id"] in {"jfe150_weak", "jfe150_strong"} and row["evidence"].startswith(
                "typical"
            ):
                row["status"] = "reference_only"
                row["note"] = (
                    "Typical curves/noise are not guaranteed corner limits; disagreement remains quantified."
                )
            if row["name"] == "ciss_2ma":
                row["status"] = "condition_unresolved"
                row["note"] = (
                    "Table capacitance gate bias unspecified; off/operating bias both retained. No confirmed device failure from this comparison."
                )

    def run(self):
        self.transfer()
        self.idss_gfs()
        self.noise()
        self.voltage_limits()
        self.output_curve()
        self.leakage()
        self.capacitance()
        self.refine_noise()
        self.clipping()
        self.annotate_evidence()
        return dict(
            comparisons=self.comparisons,
            measurements=self.measurements,
            scope="DC/caps/terminal noise/large-signal screen; no production noise/yield/SOA qualification",
        )


def jfet(exp, m):
    return JfetCharacterization(exp, m).run()
