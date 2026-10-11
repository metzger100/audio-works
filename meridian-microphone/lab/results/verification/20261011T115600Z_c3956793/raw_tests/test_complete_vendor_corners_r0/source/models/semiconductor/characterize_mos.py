# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolated device characterization against primary evidence; errors survive in records."""

from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.metrics import at_frequency


from characterize_base import interpolate, compare, refinement


def mosfet(exp, m):
    """Unmodified MOS macro: pulsed/isothermal DC, two-port C, low-current noise gaps."""
    sub = m["subcircuit"]
    ref = exp.refs["vishay_2n7002k"]
    rows = []
    measurements = {}
    exp.partial[m["id"]] = dict(comparisons=rows, measurements=measurements)

    def circuit(vg=0, vd=10, gate_ac=1, drain_ac=0):
        return (
            f"Vd d 0 DC {vd} AC {drain_ac}\nVg g 0 DC {vg} AC {gate_ac}\n"
            f"Xq d g 0 {sub}\nHout out 0 Vd 1\nHgate ig 0 Vg 1"
        )

    curves = {}
    for t in [-55, -10, 25, 50, 125]:
        out = exp.execute(
            m,
            f"transfer_{t}",
            circuit(),
            "dc Vg 0 6 .002\nwrite transfer.raw v(g) i(vd) i(vg)",
            ["transfer.raw"],
            t,
        )
        if out:
            curves[t] = out["transfer.raw"]
            raw = curves[t]
            measurements[f"transfer_{t}"] = {
                "id_at_vgs4_a": float(np.interp(4, raw["v(g)"], -raw["i(vd)"])),
                "vgs_at_2ma_v": interpolate(raw, -raw["i(vd)"], 0.002, "v(g)"),
                "reference_condition": "VDS10V; source transfer plot drain bias unspecified",
            }
    out = exp.execute(
        m,
        "threshold_diode_connected",
        f"Vg g 0 0\nVlink d g 0\nXq d g 0 {sub}",
        "dc Vg 0 4 .0005\nwrite threshold.raw v(g) i(vlink)",
        ["threshold.raw"],
    )
    if out:
        raw = out["threshold.raw"]
        value = interpolate(raw, -raw["i(vlink)"], 0.00025, "v(g)")
        measurements["threshold_v"] = value
        rows.append(
            compare(
                "threshold_250ua",
                value,
                *ref["threshold"]["limits_v"],
                condition="VDS=VGS,ID250uA,25C",
            )
        )
        fine = exp.execute(
            m,
            "threshold_refined",
            f"Vg g 0 0\nVlink d g 0\nXq d g 0 {sub}",
            "dc Vg 0 4 .00025\nwrite threshold.raw v(g) i(vlink)",
            ["threshold.raw"],
            refine=True,
        )
        if fine:
            f = fine["threshold.raw"]
            refined = interpolate(f, -f["i(vlink)"], 0.00025, "v(g)")
            rows.append(
                compare(
                    "threshold_refinement",
                    abs(refined / value - 1),
                    hi=0.01,
                    evidence="numerical_refinement",
                )
            )
    for vg in [3, 4, 5, 10]:
        out = exp.execute(
            m,
            f"output_vgs_{vg}",
            circuit(vg=vg, vd=0),
            "dc Vd 0 5 .005\nwrite output.raw v(d) i(vd)",
            ["output.raw"],
        )
        if out:
            raw = out["output.raw"]
            for p in ref["output_curve_observations"]["points"]:
                if p["vgs_v"] == vg:
                    value = float(np.interp(p["vds_v"], raw["v(d)"], -raw["i(vd)"]))
                    rows.append(
                        compare(
                            f"output_vgs{vg}_vds{p['vds_v']}",
                            value,
                            *p["current_interval_a"],
                            evidence="typical_curve_reading_interval",
                            condition="page3 Output Characteristics,25C; isothermal pulse approximation",
                        )
                    )
            fine = exp.execute(
                m,
                f"output_refined_vgs_{vg}",
                circuit(vg=vg, vd=0),
                "dc Vd 0 5 .0025\nwrite output.raw v(d) i(vd)",
                ["output.raw"],
                refine=True,
            )
            if fine:
                rows.append(
                    refinement(
                        raw, fine["output.raw"], "v(d)", "i(vd)", f"output_refinement_vgs{vg}"
                    )
                )
    rds = {}
    for t in [-55, 25, 125]:
        for p in ref["rds_on"]:
            vg = p["vgs_v"]
            current = p["id_a"]
            out = exp.execute(
                m,
                f"rds_vgs{vg}_{t}",
                circuit(vg=vg, vd=0),
                "dc Vd 0 2 .001\nwrite output.raw v(d) i(vd)",
                ["output.raw"],
                t,
            )
            if out:
                raw = out["output.raw"]
                vd = interpolate(raw, -raw["i(vd)"], current, "v(d)")
                rds[(vg, t)] = vd / current
                measurements[f"rds_vgs{vg}_{t}_ohm"] = vd / current
                if t == 25:
                    rows.append(
                        compare(
                            f"rds_on_vgs{vg}",
                            vd / current,
                            hi=p["maximum_ohm"],
                            condition=f"page2 pulse condition,VGS{vg}V,ID{current}A,25C; no self-heating",
                        )
                    )
                    fine = exp.execute(
                        m,
                        f"rds_refined_vgs{vg}",
                        circuit(vg=vg, vd=0),
                        "dc Vd 0 2 .0005\nwrite output.raw v(d) i(vd)",
                        ["output.raw"],
                        refine=True,
                    )
                    if fine:
                        f = fine["output.raw"]
                        r = interpolate(f, -f["i(vd)"], current, "v(d)") / current
                        rows.append(
                            compare(
                                f"rds_refinement_vgs{vg}",
                                abs(r / (vd / current) - 1),
                                hi=0.01,
                                evidence="numerical_refinement",
                            )
                        )
    for p in ref["rds_on"]:
        vg = p["vgs_v"]
        if (vg, 125) in rds and (vg, 25) in rds:
            rows.append(
                compare(
                    f"rds_temperature_ratio_vgs{vg}",
                    rds[(vg, 125)] / rds[(vg, 25)],
                    *ref["rds_temperature"]["normalized_interval"],
                    evidence="typical_curve_reading_interval",
                    condition="page3 normalized RDS125C/25C",
                )
            )
    cap = {}
    for drive in ["gate", "drain"]:
        out = exp.execute(
            m,
            f"capacitance_{drive}",
            circuit(vg=0, vd=25, gate_ac=int(drive == "gate"), drain_ac=int(drive == "drain")),
            "ac lin 1 1Meg 1Meg\nwrite ac.raw i(vg) i(vd)",
            ["ac.raw"],
        )
        if out:
            raw = out["ac.raw"]
            omega = 2 * np.pi * 1e6
            if drive == "gate":
                cap["ciss"] = float(-raw["i(vg)"][0].imag / omega)
            else:
                cap["coss"] = float(-raw["i(vd)"][0].imag / omega)
                cap["crss"] = float(raw["i(vg)"][0].imag / omega)
            fine = exp.execute(
                m,
                f"capacitance_refined_{drive}",
                circuit(vg=0, vd=25, gate_ac=int(drive == "gate"), drain_ac=int(drive == "drain")),
                "ac lin 1 1Meg 1Meg\nwrite ac.raw i(vg) i(vd)",
                ["ac.raw"],
                refine=True,
            )
            if fine:
                vec = "i(vg)" if drive == "gate" else "i(vd)"
                error = abs(fine["ac.raw"][vec][0] / raw[vec][0] - 1)
                rows.append(
                    compare(
                        f"capacitance_refinement_{drive}",
                        error,
                        hi=0.01,
                        evidence="numerical_refinement",
                    )
                )
    measurements["capacitance_f"] = cap
    for name, value in cap.items():
        rows.append(
            compare(
                name + "_table",
                value,
                typ=ref["capacitance"]["table_typical_f"][name],
                condition=ref["capacitance"]["conditions"],
            )
        )
        rows.append(
            compare(
                name + "_graph",
                value,
                *ref["capacitance"]["graph_intervals_f"][name],
                evidence="typical_curve_reading_interval",
                condition="page3 capacitance graph,VDS25V,VGS0V",
            )
        )
    out = exp.execute(
        m,
        "gate_leakage_omission",
        circuit(vg=5, vd=0),
        "dc Vg -5 5 .1\nwrite leakage.raw v(g) i(vg)",
        ["leakage.raw"],
    )
    if out:
        measurements["gate_leakage"] = {
            "maximum_simulated_magnitude_a": float(np.max(abs(out["leakage.raw"]["i(vg)"]))),
            "status": "unqualified_model_omits_gate_leakage_ESD",
            "datasheet_maximum_a": ref["gate_leakage"]["maximum_a"],
        }
    for t, limit in [(25, 1e-6), (125, 500e-6)]:
        out = exp.execute(
            m,
            f"drain_leakage_{t}",
            circuit(vg=0, vd=60),
            "op\nwrite op.raw i(vd) i(vg)",
            ["op.raw"],
            t,
        )
        if out:
            measurements[f"drain_leakage_{t}"] = {
                "id_a": -float(out["op.raw"]["i(vd)"][0]),
                "datasheet_maximum_a": limit,
                "condition": "VDS60V,VGS0V",
                "status": "unqualified_high_field_temperature_leakage; diode_IS_is_not_production_coverage",
            }
    if 25 in curves:
        raw = curves[25]
        bias200 = interpolate(raw, -raw["i(vd)"], 0.2, "v(g)")
        out = exp.execute(
            m,
            "transconductance",
            circuit(vg=bias200),
            "op\nwrite op.raw i(vd)\nac lin 1 1000 1000\nwrite ac.raw i(vd)",
            ["op.raw", "ac.raw"],
        )
        if out:
            gm = float(abs(out["ac.raw"]["i(vd)"][0]))
            actual = -float(out["op.raw"]["i(vd)"][0])
            measurements["gfs"] = {"id_a": actual, "gm_s": gm, "vgs_v": bias200}
            rows.append(
                compare(
                    "gfs_200ma",
                    gm,
                    lo=ref["gfs"]["minimum_s"],
                    condition="VDS10V,ID200mA,25C; interpolated bias",
                )
            )
        noise_bias = exp.execute(
            m,
            "transfer_noise_bias_5v",
            circuit(vd=5),
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
                out = exp.execute(
                    m,
                    f"low_current_noise_{current}_{density}",
                    circuit(vg=vg, vd=5),
                    f"op\nwrite op.raw i(vd) i(vg)\nac dec {density} 1 100Meg\nwrite ac.raw i(vd) i(vg)\n"
                    f"noise v(out) Vg dec {density} 1 100k 1\nsetplot noise1\nwrite noise.raw all\n"
                    f"noise v(ig) Vg dec {density} 1 100k 1\nsetplot noise3\nwrite gate_noise.raw all",
                    ["op.raw", "ac.raw", "noise.raw", "gate_noise.raw"],
                    refine=density == 128,
                )
                if out:
                    n = out["noise.raw"]
                    ac = out["ac.raw"]
                    en = float(at_frequency(n["frequency"], n["inoise_spectrum"], 1000))
                    noise.append(en)
                    if density == 64:
                        measurements[f"low_current_{current}"] = {
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
                rows.append(
                    compare(
                        f"noise_refinement_{current}",
                        abs(noise[1] / noise[0] - 1),
                        hi=0.01,
                        evidence="numerical_refinement",
                    )
                )
        vg = interpolate(raw, -raw["i(vd)"], 0.002, "v(g)")
        trans = []
        c = f"Vs rail 0 12\nRd rail d 2k\nVg g 0 SIN({vg} .8 1000)\nXq d g 0 {sub}"
        for step in [2e-6, 1e-6]:
            out = exp.execute(
                m,
                f"clipping_{step}",
                c,
                f"tran {step} .02 .01 {step}\nwrite tran.raw v(d) i(vs)",
                ["tran.raw"],
                refine=step == 1e-6,
            )
            if out:
                trans.append(out["tran.raw"])
        if len(trans) == 2:
            rows.append(
                refinement(trans[0], trans[1], "time", "v(d)", "clipping_numerical_refinement")
            )
            measurements["clipping_simulation"] = {
                "drain_range_v": [float(np.min(trans[1]["v(d)"])), float(np.max(trans[1]["v(d)"]))],
                "status": "numerical_only_no_physical_overload_reference",
                "supply_current_mean_a": float(np.mean(-trans[1]["i(vs)"])),
            }
    return dict(
        comparisons=rows,
        measurements=measurements,
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
