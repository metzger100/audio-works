# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite terminal fixtures; complete original files, no fitted parameters."""

import numpy as np
from prerequisite_math import current_balance, noise_closure
from meridian_lab.metrics import at_frequency
from meridian_lab.nonlinear import settled_spectrum


def jfet(exp, model):
    sub = model["subcircuit"]
    rows = {}

    def fixed(vg=0, vd=5):
        return (
            f"Vd d 0 {vd}\nVg g 0 DC {vg} AC 1\nVs s 0 0\nVh h 0 25\nVl l 0 -5\n"
            f"Xq d g s h l {sub}\nHout out 0 Vd 1\nHgate ig 0 Vg 1"
        )

    bias = None
    for temp in [-10, 25, 50]:
        raw = exp.execute(
            model,
            f"transfer_{temp}",
            fixed(),
            "dc Vg -1.8 0 .001\nwrite dc.raw all",
            ["dc.raw"],
            temp,
        )
        if raw is None:
            continue
        d = raw["dc.raw"]
        cur = -d["i(vd)"].real
        rows[f"transfer_{temp}"] = dict(
            idss_5v_a=float(cur[-1]),
            terminal_kcl_fraction=current_balance(d, ["vd", "vg", "vs", "vh", "vl"]),
        )
        if temp == 25 and cur.min() < 0.002 < cur.max():
            bias = float(np.interp(0.002, cur, d["v(g)"].real))
    raw = exp.execute(
        model,
        "idss_gm",
        fixed(vd=10),
        "op\nwrite op.raw all\nac lin 1 1k 1k\nwrite ac.raw all",
        ["op.raw", "ac.raw"],
    )
    if raw:
        ids = -float(raw["op.raw"]["i(vd)"][0])
        gm = float(abs(raw["ac.raw"]["i(vd)"][0]))
        rows["guaranteed_25c_10v"] = dict(
            idss_a=ids, gm_s=gm, idss_pass=0.024 <= ids <= 0.046, gm_pass=0.055 <= gm <= 0.080
        )
    raw = exp.execute(
        model, "output", fixed(-0.7), "dc Vd .01 20 .05\nwrite dc.raw all", ["dc.raw"]
    )
    if raw:
        d = raw["dc.raw"]
        rows["output_vgs_minus_0p7"] = {
            str(v): float(np.interp(v, d["v(d)"], -d["i(vd)"])) for v in [5, 20]
        }
    raw = exp.execute(
        model,
        "leakage",
        fixed(-0.7, 2).replace("Vh h 0 25", "Vh h 0 5"),
        "op\nwrite op.raw all",
        ["op.raw"],
    )
    if raw:
        rows["leakage_a"] = float(abs(raw["op.raw"]["i(vg)"][0]))
    if bias is None:
        rows["subsequent_scope"] = "No bracketed 2mA bias; no noise/transient credit"
        return rows
    raw = exp.execute(
        model,
        "admittance_noise",
        fixed(bias),
        "op\nwrite op.raw all\nac dec 64 10 10Meg\nwrite ac.raw all\n"
        "noise v(out) Vg dec 128 .1 100k 1\nsetplot noise1\nwrite noise.raw all\n"
        "noise v(ig) Vg dec 128 .1 100k 1\nsetplot noise3\nwrite gate.raw all",
        ["op.raw", "ac.raw", "noise.raw", "gate.raw"],
    )
    if raw:
        n, a = raw["noise.raw"], raw["ac.raw"]
        rows["bias_2ma_5v"] = dict(
            vgs_v=bias,
            actual_id_a=-float(raw["op.raw"]["i(vd)"][0]),
            ciss_f=float(
                (-at_frequency(a["frequency"], a["i(vg)"], 1000) / (2j * np.pi * 1000)).real
            ),
            en_10hz=float(at_frequency(n["frequency"], n["inoise_spectrum"], 10)),
            en_1khz=float(at_frequency(n["frequency"], n["inoise_spectrum"], 1000)),
            in_1khz=float(
                at_frequency(raw["gate.raw"]["frequency"], raw["gate.raw"]["onoise_spectrum"], 1000)
            ),
            noise_closure_fraction=noise_closure(n),
        )
    # Drain/source follower and all five zero-voltage terminal observers separately.
    base = (
        "Vrail rail 0 12\nVg g 0 DC 1 AC 1 SIN(1 .01 1000)\nRsource s 0 1k\n"
        "Rin g 0 1G\nCload s 0 70p\n"
    )
    direct = base + f"Xq rail g s rail 0 {sub}"
    observed = (
        base
        + "\n".join(
            f"Vo{i} {node} t{i} 0" for i, node in enumerate(["rail", "g", "s", "rail", "0"])
        )
        + f"\nXq t0 t1 t2 t3 t4 {sub}"
    )
    for label, circuit, step in [
        ("follower_direct", direct, 2e-6),
        ("follower_observed", observed, 2e-6),
        ("follower_refined", direct, 1e-6),
    ]:
        raw = exp.execute(
            model, label, circuit, f"tran {step} .064 0 {step}\nwrite tran.raw all", ["tran.raw"]
        )
        if raw:
            d = raw["tran.raw"]
            try:
                h = settled_spectrum(d["time"], d["v(s)"], 1000, 0.032)
                h["rail_energy_j"] = float(np.trapezoid(-12 * d["i(vrail)"], d["time"]))
                h["peak_source_v"] = float(np.max(d["v(s)"]))
                rows[label] = h
            except ValueError as exc:
                rows[label] = dict(status="unsettled", reason=str(exc))
    return rows


def bipolar(exp, model):
    rows = {}
    primitive = model.get("primitive", "X")
    sign = -1 if model["device_id"] == "diodes_mmbt5401" else 1

    def fixed(v=0.65, rs=0, vc=5):
        link = f"Rb in b {rs}" if rs else "Vlink in b 0"
        return f"Vc c 0 {sign * vc}\nVb in 0 DC {sign * v} AC 1\n{link}\nVe e 0 0\n{primitive}q c b e {model['subcircuit']}\nHout out 0 Vc 1"

    bias = None
    for temp in [-10, 25, 50]:
        raw = exp.execute(
            model,
            f"transfer_{temp}",
            fixed(),
            f"dc Vb {sign * 0.3} {sign * 0.95} {sign * 0.0005}\nwrite dc.raw all",
            ["dc.raw"],
            temp,
        )
        if raw is None:
            continue
        d = raw["dc.raw"]
        current = -sign * d["i(vc)"].real
        grid = []
        for target in [0.0001, 0.001, 0.002, 0.01]:
            if not current.min() < target < current.max():
                continue
            vb = float(np.interp(target, current, sign * d["v(in)"].real))
            ib = float(abs(np.interp(target, current, d["i(vb)"].real)))
            grid.append(dict(ic_a=target, vbe_v=vb, ib_a=ib, beta=target / ib))
            if temp == 25 and target == 0.002:
                bias = vb
        rows[f"grid_{temp}"] = grid
    if bias is None:
        rows["scope"] = "Strict parent DC failure; no capacitance/bandwidth/noise/recovery credit"
        return rows
    raw = exp.execute(
        model,
        "ac_noise",
        fixed(bias, 2000),
        "op\nwrite op.raw all\nac dec 64 10 1G\nwrite ac.raw all\n"
        "noise v(out) Vb dec 128 10 100k 1\nsetplot noise1\nwrite noise.raw all",
        ["op.raw", "ac.raw", "noise.raw"],
    )
    if raw:
        n, a = raw["noise.raw"], raw["ac.raw"]
        rows["loaded_base_2kohm"] = dict(
            actual_ic_a=-sign * float(raw["op.raw"]["i(vc)"][0]),
            base_current_a=abs(float(raw["op.raw"]["i(vb)"][0])),
            current_gain_100mhz=float(
                abs(at_frequency(a["frequency"], a["i(vc)"] / a["i(vb)"], 1e8))
            ),
            en_1khz=float(at_frequency(n["frequency"], n["inoise_spectrum"], 1000)),
            noise_closure_fraction=noise_closure(n),
            flicker_qualified=False,
        )
    # Exact open-emitter constraint: zero-current source, no invented leakage resistor.
    cap = f"Vc c 0 DC {sign * 10} AC 1\nVb b 0 0\nIopen e 0 0\n{primitive}q c b e {model['subcircuit']}"
    raw = exp.execute(
        model, "open_emitter_cap", cap, "ac lin 1 1Meg 1Meg\nwrite ac.raw all", ["ac.raw"]
    )
    if raw:
        rows["ccb_f"] = float((-raw["ac.raw"]["i(vc)"][0] / (2j * np.pi * 1e6)).real)
    c = (
        f"Vrail rail 0 {sign * 5}\nRc rail c 500\nIb 0 b PULSE(0 {sign * 0.0005} .002 1u 1u .002 .008)\n"
        f"Ve e 0 0\n{primitive}q c b e {model['subcircuit']}"
    )
    raw = exp.execute(
        model, "saturation_recovery", c, "tran 1u .012 0 1u\nwrite tran.raw all", ["tran.raw"]
    )
    if raw:
        d = raw["tran.raw"]
        t = d["time"].real
        v = sign * d["v(c)"].real
        off = t > 0.004001
        above = off & (v > 4.5)
        rows["recovery"] = dict(
            vcesat_v=float(np.interp(0.003, t, v)),
            recovery_to_90percent_s=float(t[above][0] - 0.004001) if np.any(above) else None,
            rail_energy_j=float(np.trapezoid(-sign * 5 * d["i(vrail)"], t)),
            scope="5V,500ohm collector,500uA base pulse; diagnostic, no matched datasheet recovery bound",
        )
    return rows


def opa(exp, model):
    rows = {}
    for translation in [0, 20]:
        extra = "guard1 guard2 " if model["device_id"] == "opa928" else ""
        c = (
            f"Vg g 0 {translation}\nVp p g 16\nVn n g 0\nVin in g DC 8 AC 1 SIN(8 .01 1000)\n"
            f"Vm mid g 8\nRl out mid 10k\nXq in out p n out {extra}{model['subcircuit']}"
        )
        for guess in [False, True]:
            circuit = c + (f"\n.nodeset v(out)={translation + 8}" if guess else "")
            raw = exp.execute(
                model,
                f"translation_{translation}_guess_{guess}",
                circuit,
                "op\nwrite op.raw all\nac dec 64 10 10Meg\nwrite ac.raw all",
                ["op.raw", "ac.raw"],
            )
            if raw:
                rows[f"{translation}_{guess}"] = dict(
                    output_error_v=float(raw["op.raw"]["v(out)"][0]) - translation - 8,
                    iq_a=-float(raw["op.raw"]["i(vp)"][0]),
                )
    return rows
