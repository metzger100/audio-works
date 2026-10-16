# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolated MOS DC, terminal capacitance and leakage controls."""

import numpy as np
from characterize_base import interpolate, compare, refinement


class MosControls:
    def __init__(self, exp, model):
        self.exp = exp
        self.model = model
        self.sub = model["subcircuit"]
        self.reference = exp.refs["vishay_2n7002k"]
        self.comparisons = []
        self.measurements = {}
        exp.partial[model["id"]] = dict(
            comparisons=self.comparisons, measurements=self.measurements
        )

    def circuit(self, vg=0, vd=10, gate_ac=1, drain_ac=0):
        return f"Vd d 0 DC {vd} AC {drain_ac}\nVg g 0 DC {vg} AC {gate_ac}\nXq d g 0 {self.sub}\nHout out 0 Vd 1\nHgate ig 0 Vg 1"

    def transfer(self):
        self.curves = {}
        for t in [-55, -10, 25, 50, 125]:
            out = self.exp.execute(
                self.model,
                f"transfer_{t}",
                self.circuit(),
                "dc Vg 0 6 .002\nwrite transfer.raw v(g) i(vd) i(vg)",
                ["transfer.raw"],
                t,
            )
            if out:
                self.curves[t] = out["transfer.raw"]
                raw = self.curves[t]
                self.measurements[f"transfer_{t}"] = {
                    "id_at_vgs4_a": float(np.interp(4, raw["v(g)"], -raw["i(vd)"])),
                    "vgs_at_2ma_v": interpolate(raw, -raw["i(vd)"], 0.002, "v(g)"),
                    "reference_condition": "VDS10V; source transfer plot drain bias unspecified",
                }

    def threshold(self):
        out = self.exp.execute(
            self.model,
            "threshold_diode_connected",
            f"Vg g 0 0\nVlink d g 0\nXq d g 0 {self.sub}",
            "dc Vg 0 4 .0005\nwrite threshold.raw v(g) i(vlink)",
            ["threshold.raw"],
        )
        if out:
            raw = out["threshold.raw"]
            value = interpolate(raw, -raw["i(vlink)"], 0.00025, "v(g)")
            self.measurements["threshold_v"] = value
            self.comparisons.append(
                compare(
                    "threshold_250ua",
                    value,
                    *self.reference["threshold"]["limits_v"],
                    condition="VDS=VGS,ID250uA,25C",
                )
            )
            fine = self.exp.execute(
                self.model,
                "threshold_refined",
                f"Vg g 0 0\nVlink d g 0\nXq d g 0 {self.sub}",
                "dc Vg 0 4 .00025\nwrite threshold.raw v(g) i(vlink)",
                ["threshold.raw"],
                refine=True,
            )
            if fine:
                f = fine["threshold.raw"]
                refined = interpolate(f, -f["i(vlink)"], 0.00025, "v(g)")
                self.comparisons.append(
                    compare(
                        "threshold_refinement",
                        abs(refined / value - 1),
                        hi=0.01,
                        evidence="numerical_refinement",
                    )
                )

    def output(self):
        for vg in [3, 4, 5, 10]:
            out = self.exp.execute(
                self.model,
                f"output_vgs_{vg}",
                self.circuit(vg=vg, vd=0),
                "dc Vd 0 5 .005\nwrite output.raw v(d) i(vd)",
                ["output.raw"],
            )
            if out:
                raw = out["output.raw"]
                for p in self.reference["output_curve_observations"]["points"]:
                    if p["vgs_v"] == vg:
                        value = float(np.interp(p["vds_v"], raw["v(d)"], -raw["i(vd)"]))
                        self.comparisons.append(
                            compare(
                                f"output_vgs{vg}_vds{p['vds_v']}",
                                value,
                                *p["current_interval_a"],
                                evidence="typical_curve_reading_interval",
                                condition="page3 Output Characteristics,25C; isothermal pulse approximation",
                            )
                        )
                fine = self.exp.execute(
                    self.model,
                    f"output_refined_vgs_{vg}",
                    self.circuit(vg=vg, vd=0),
                    "dc Vd 0 5 .0025\nwrite output.raw v(d) i(vd)",
                    ["output.raw"],
                    refine=True,
                )
                if fine:
                    self.comparisons.append(
                        refinement(
                            raw, fine["output.raw"], "v(d)", "i(vd)", f"output_refinement_vgs{vg}"
                        )
                    )

    def resistance(self):
        rds = {}
        for t in [-55, 25, 125]:
            for p in self.reference["rds_on"]:
                vg = p["vgs_v"]
                current = p["id_a"]
                out = self.exp.execute(
                    self.model,
                    f"rds_vgs{vg}_{t}",
                    self.circuit(vg=vg, vd=0),
                    "dc Vd 0 2 .001\nwrite output.raw v(d) i(vd)",
                    ["output.raw"],
                    t,
                )
                if out:
                    raw = out["output.raw"]
                    vd = interpolate(raw, -raw["i(vd)"], current, "v(d)")
                    rds[vg, t] = vd / current
                    self.measurements[f"rds_vgs{vg}_{t}_ohm"] = vd / current
                    if t == 25:
                        self.comparisons.append(
                            compare(
                                f"rds_on_vgs{vg}",
                                vd / current,
                                hi=p["maximum_ohm"],
                                condition=f"page2 pulse condition,VGS{vg}V,ID{current}A,25C; no self-heating",
                            )
                        )
                        fine = self.exp.execute(
                            self.model,
                            f"rds_refined_vgs{vg}",
                            self.circuit(vg=vg, vd=0),
                            "dc Vd 0 2 .0005\nwrite output.raw v(d) i(vd)",
                            ["output.raw"],
                            refine=True,
                        )
                        if fine:
                            f = fine["output.raw"]
                            r = interpolate(f, -f["i(vd)"], current, "v(d)") / current
                            self.comparisons.append(
                                compare(
                                    f"rds_refinement_vgs{vg}",
                                    abs(r / (vd / current) - 1),
                                    hi=0.01,
                                    evidence="numerical_refinement",
                                )
                            )
        for p in self.reference["rds_on"]:
            vg = p["vgs_v"]
            if (vg, 125) in rds and (vg, 25) in rds:
                self.comparisons.append(
                    compare(
                        f"rds_temperature_ratio_vgs{vg}",
                        rds[vg, 125] / rds[vg, 25],
                        *self.reference["rds_temperature"]["normalized_interval"],
                        evidence="typical_curve_reading_interval",
                        condition="page3 normalized RDS125C/25C",
                    )
                )

    def capacitance(self):
        cap = {}
        for drive in ["gate", "drain"]:
            out = self.exp.execute(
                self.model,
                f"capacitance_{drive}",
                self.circuit(
                    vg=0, vd=25, gate_ac=int(drive == "gate"), drain_ac=int(drive == "drain")
                ),
                "ac lin 1 1Meg 1Meg\nwrite ac.raw i(vg) i(vd)",
                ["ac.raw"],
            )
            if out:
                raw = out["ac.raw"]
                omega = 2 * np.pi * 1000000.0
                if drive == "gate":
                    cap["ciss"] = float(-raw["i(vg)"][0].imag / omega)
                else:
                    cap["coss"] = float(-raw["i(vd)"][0].imag / omega)
                    cap["crss"] = float(raw["i(vg)"][0].imag / omega)
                fine = self.exp.execute(
                    self.model,
                    f"capacitance_refined_{drive}",
                    self.circuit(
                        vg=0, vd=25, gate_ac=int(drive == "gate"), drain_ac=int(drive == "drain")
                    ),
                    "ac lin 1 1Meg 1Meg\nwrite ac.raw i(vg) i(vd)",
                    ["ac.raw"],
                    refine=True,
                )
                if fine:
                    vec = "i(vg)" if drive == "gate" else "i(vd)"
                    error = abs(fine["ac.raw"][vec][0] / raw[vec][0] - 1)
                    self.comparisons.append(
                        compare(
                            f"capacitance_refinement_{drive}",
                            error,
                            hi=0.01,
                            evidence="numerical_refinement",
                        )
                    )
        self.measurements["capacitance_f"] = cap
        for name, value in cap.items():
            self.comparisons.append(
                compare(
                    name + "_table",
                    value,
                    typ=self.reference["capacitance"]["table_typical_f"][name],
                    condition=self.reference["capacitance"]["conditions"],
                )
            )
            self.comparisons.append(
                compare(
                    name + "_graph",
                    value,
                    *self.reference["capacitance"]["graph_intervals_f"][name],
                    evidence="typical_curve_reading_interval",
                    condition="page3 capacitance graph,VDS25V,VGS0V",
                )
            )

    def leakage(self):
        out = self.exp.execute(
            self.model,
            "gate_leakage_omission",
            self.circuit(vg=5, vd=0),
            "dc Vg -5 5 .1\nwrite leakage.raw v(g) i(vg)",
            ["leakage.raw"],
        )
        if out:
            self.measurements["gate_leakage"] = {
                "maximum_simulated_magnitude_a": float(np.max(abs(out["leakage.raw"]["i(vg)"]))),
                "status": "unqualified_model_omits_gate_leakage_ESD",
                "datasheet_maximum_a": self.reference["gate_leakage"]["maximum_a"],
            }
        for t, limit in [(25, 1e-06), (125, 0.0005)]:
            out = self.exp.execute(
                self.model,
                f"drain_leakage_{t}",
                self.circuit(vg=0, vd=60),
                "op\nwrite op.raw i(vd) i(vg)",
                ["op.raw"],
                t,
            )
            if out:
                self.measurements[f"drain_leakage_{t}"] = {
                    "id_a": -float(out["op.raw"]["i(vd)"][0]),
                    "datasheet_maximum_a": limit,
                    "condition": "VDS60V,VGS0V",
                    "status": "unqualified_high_field_temperature_leakage; diode_IS_is_not_production_coverage",
                }
