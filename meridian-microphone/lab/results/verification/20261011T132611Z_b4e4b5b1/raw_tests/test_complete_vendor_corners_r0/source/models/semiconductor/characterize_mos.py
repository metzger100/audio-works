# SPDX-License-Identifier: GPL-3.0-or-later
"""Run unchanged MOS controls as explicit, individually readable steps."""

from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.metrics import at_frequency
from characterize_base import interpolate, compare, refinement
from characterize_mos_base import MosControls


class MosCharacterization(MosControls):
    def transconductance(self):
        raw = self.curves[25]
        bias200 = interpolate(raw, -raw["i(vd)"], 0.2, "v(g)")
        out = self.exp.execute(
            self.model,
            "transconductance",
            self.circuit(vg=bias200),
            "op\nwrite op.raw i(vd)\nac lin 1 1000 1000\nwrite ac.raw i(vd)",
            ["op.raw", "ac.raw"],
        )
        if out:
            gm = float(abs(out["ac.raw"]["i(vd)"][0]))
            actual = -float(out["op.raw"]["i(vd)"][0])
            self.measurements["gfs"] = {"id_a": actual, "gm_s": gm, "vgs_v": bias200}
            self.comparisons.append(
                compare(
                    "gfs_200ma",
                    gm,
                    lo=self.reference["gfs"]["minimum_s"],
                    condition="VDS10V,ID200mA,25C; interpolated bias",
                )
            )

    def noise(self):
        noise_bias = self.exp.execute(
            self.model,
            "transfer_noise_bias_5v",
            self.circuit(vd=5),
            "dc Vg 0 6 .001\nwrite transfer.raw v(g) i(vd)",
            ["transfer.raw"],
        )
        if not noise_bias:
            raise ValueError("Missing5V bias sweep; no noise bias substitution permitted")
        bias_raw = noise_bias["transfer.raw"]
        for current in [0.0001, 0.002]:
            vg = interpolate(bias_raw, -bias_raw["i(vd)"], current, "v(g)")
            noise = []
            for density in [64, 128]:
                out = self.exp.execute(
                    self.model,
                    f"low_current_noise_{current}_{density}",
                    self.circuit(vg=vg, vd=5),
                    f"op\nwrite op.raw i(vd) i(vg)\nac dec {density} 1 100Meg\nwrite ac.raw i(vd) i(vg)\nnoise v(out) Vg dec {density} 1 100k 1\nsetplot noise1\nwrite noise.raw all\nnoise v(ig) Vg dec {density} 1 100k 1\nsetplot noise3\nwrite gate_noise.raw all",
                    ["op.raw", "ac.raw", "noise.raw", "gate_noise.raw"],
                    refine=density == 128,
                )
                if out:
                    n = out["noise.raw"]
                    ac = out["ac.raw"]
                    en = float(at_frequency(n["frequency"], n["inoise_spectrum"], 1000))
                    noise.append(en)
                    if density == 64:
                        self.measurements[f"low_current_{current}"] = {
                            "id_a": -float(out["op.raw"]["i(vd)"][0]),
                            "vgs_v": vg,
                            "en_10hz_v_sqrt_hz": float(
                                at_frequency(n["frequency"], n["inoise_spectrum"], 10)
                            ),
                            "en_1khz_v_sqrt_hz": en,
                            "gm_s": float(abs(at_frequency(ac["frequency"], ac["i(vd)"], 1000))),
                            "gate_current_noise_1k_a_sqrt_hz": float(
                                at_frequency(
                                    out["gate_noise.raw"]["frequency"],
                                    out["gate_noise.raw"]["onoise_spectrum"],
                                    1000,
                                )
                            ),
                            "status": "simulation_only_no_primary_noise_reference_KF_absent",
                            "bandwidth_status": "native AC recorded; no independent low-current bandwidth reference",
                        }
            if len(noise) == 2:
                self.comparisons.append(
                    compare(
                        f"noise_refinement_{current}",
                        abs(noise[1] / noise[0] - 1),
                        hi=0.01,
                        evidence="numerical_refinement",
                    )
                )

    def clipping(self):
        raw = self.curves[25]
        vg = interpolate(raw, -raw["i(vd)"], 0.002, "v(g)")
        trans = []
        c = f"Vs rail 0 12\nRd rail d 2k\nVg g 0 SIN({vg} .8 1000)\nXq d g 0 {self.sub}"
        for step in [2e-06, 1e-06]:
            out = self.exp.execute(
                self.model,
                f"clipping_{step}",
                c,
                f"tran {step} .02 .01 {step}\nwrite tran.raw v(d) i(vs)",
                ["tran.raw"],
                refine=step == 1e-06,
            )
            if out:
                trans.append(out["tran.raw"])
        if len(trans) == 2:
            self.comparisons.append(
                refinement(trans[0], trans[1], "time", "v(d)", "clipping_numerical_refinement")
            )
            self.measurements["clipping_simulation"] = {
                "drain_range_v": [float(np.min(trans[1]["v(d)"])), float(np.max(trans[1]["v(d)"]))],
                "status": "numerical_only_no_physical_overload_reference",
                "supply_current_mean_a": float(np.mean(-trans[1]["i(vs)"])),
            }

    def run(self):
        self.transfer()
        self.threshold()
        self.output()
        self.resistance()
        self.capacitance()
        self.leakage()
        if 25 in self.curves:
            self.transconductance()
            self.noise()
            self.clipping()
        return dict(
            comparisons=self.comparisons,
            measurements=self.measurements,
            scope="Unmodified nominal macro; isothermal pulse DC/C/native AC recorded; no noise/process/SOA/P48 qualification",
            unqualified_behaviors=[
                "noise",
                "gate_leakage",
                "process_corners",
                "low_current_temperature",
                "self_heating_SOA",
                "physical_clipping",
                "P48_supply_output",
            ],
        )


def mosfet(exp, model):
    return MosCharacterization(exp, model).run()
