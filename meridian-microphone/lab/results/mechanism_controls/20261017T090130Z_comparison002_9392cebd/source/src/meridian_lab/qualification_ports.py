# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from itertools import product
import numpy as np

from .core import ROOT, SimulationError, read_yaml
from .metrics import at_frequency, db


def port_matrix(sim, ports, label, environment_only=False):
    columns = []
    f = None
    for j, port in enumerate(ports):
        raw = sim.execute(
            label,
            "ac dec 8 20 20k\nwrite port.raw all",
            ["port.raw"],
            {"PRESSURE_AC": 0},
            extra=f"Iprobe mic_g {port} DC 0 AC 1",
            environment_only=environment_only,
        )["port.raw"]
        f = raw["frequency"].real
        columns.append(np.column_stack([raw.voltage(p, "mic_g") for p in ports]))
    return f, np.stack(columns, axis=-1)


def output_impedance(sim, ctx):
    f, zloaded = port_matrix(sim, ["p", "n"], "output_loaded")
    fe, zenv = port_matrix(sim, ["p", "n"], "output_environment", True)
    if not np.array_equal(f, fe):
        raise SimulationError("Cannot deembed different frequency grids")
    # Full 2-port deembedding handles mismatch; scalar subtraction would be wrong.
    ydut = np.linalg.inv(zloaded) - np.linalg.inv(zenv)
    zdut = np.linalg.inv(ydut)
    differential = np.einsum("i,nij,j->n", np.array([1, -1]), zdut, np.array([1, -1]))
    mismatch = np.abs(zdut[:, 0, 0] - zdut[:, 1, 1]) / np.maximum(
        (np.abs(zdut[:, 0, 0]) + np.abs(zdut[:, 1, 1])) / 2, 1e-20
    )
    m = {
        "frequency_hz": f.tolist(),
        "differential_ohm": np.abs(differential).tolist(),
        "differential_phase_deg": np.angle(differential, deg=True).tolist(),
        "output_impedance_ohm": float(np.max(np.abs(differential))),
        "leg_diagonal_ohm": np.abs(np.diagonal(zdut, axis1=1, axis2=2)).tolist(),
        "impedance_mismatch_fraction": float(np.max(mismatch)),
        "method": "Full 2-port Y subtraction of feed/cable/preamp, preserving DUT DC operating point",
        "raw_dut_z_real": zdut.real.tolist(),
        "raw_dut_z_imag": zdut.imag.tolist(),
    }
    ctx["output"] = m
    return result(
        "pass"
        if m["output_impedance_ohm"] <= thresholds()["differential_output_impedance_ohm"]["value"]
        else "fail",
        m,
    )


def balance(sim, ctx):
    if "output" not in ctx:
        return result("incomplete", reason="Output impedance deembedding failed")
    raw = sim.op_ac("common_mode", {"PRESSURE_AC": 0, "CMAC": 1})["ac.raw"]
    f = raw["frequency"].real
    diff = raw.voltage("pp", "pn")
    m = {
        "impedance_mismatch_fraction": ctx["output"]["impedance_mismatch_fraction"],
        "common_mode_to_differential_v_per_v_at_1khz": float(abs(at_frequency(f, diff, 1000))),
        "common_mode_drive": "Preamp input midpoint relative to supply earth; fixture susceptibility, not microphone intrinsic CMRR",
    }
    return result(
        "pass"
        if m["impedance_mismatch_fraction"] <= thresholds()["impedance_balance_fraction"]["value"]
        else "fail",
        m,
    )


def screen(sim, label, overrides):
    try:
        raw = sim.op_ac(label, overrides)
        m = response(raw["ac.raw"])
        i = current(raw["op.raw"])
        pol = float(raw["op.raw"].voltage("b", "f")[0])
        ok = (
            0 < i <= thresholds()["current_max_a"]["value"]
            and pol > 0
            and m["response_deviation_db"] <= thresholds()["electronics_response_db"]["value"]
        )
        return {
            "parameters": overrides,
            "status": "pass" if ok else "fail",
            "current_a": i,
            "polarization_dc_v": pol,
            "response_deviation_db": m["response_deviation_db"],
            "sensitivity_v_per_pa": m["sensitivity_v_per_pa_at_1khz"],
        }
    except (SimulationError, ValueError, np.linalg.LinAlgError) as exc:
        return {"parameters": overrides, "status": "error", "reason": str(exc)}


def loading(sim, ctx):
    f, z = port_matrix(sim, ["f", "b", "rear"], "input_admittance")
    y = np.linalg.inv(z)
    p = sim.params
    s = 2j * np.pi * f
    a = s * p["CF"] + 1 / p["LEAK"]
    b = s * p["CR"] + 1 / p["LEAK"]
    par = s * p["PAR"]
    cross = s * p["CROSS"]
    ycap = np.zeros_like(y)
    ycap[:, 0, 0] = a + par + cross
    ycap[:, 1, 1] = a + b
    ycap[:, 2, 2] = b + par + cross
    ycap[:, 0, 1] = ycap[:, 1, 0] = -a
    ycap[:, 1, 2] = ycap[:, 2, 1] = -b
    ycap[:, 0, 2] = ycap[:, 2, 0] = -cross
    ydut = y - ycap
    cin = ydut[:, 0, 0].imag / (2 * np.pi * f)
    ac = ctx["nominal"]["ac.raw"]
    actual = abs(at_frequency(ac["frequency"], ac.voltage("f", "mic_g"), 1000))
    unloaded = p["SREF"] * ctx["polarization_dc_v"] / p["VREF"]
    loss = -db(actual / unloaded)
    ranges = scenario_ranges()
    rows = [
        screen(sim, "capsule_corner", dict(CF=c, CR=cr, LEAK=l, PAR=cp))
        for c, cr, l, cp in product(ranges["CF"], ranges["CR"], ranges["LEAK"], ranges["PAR"])
    ]
    m = {
        "frequency_hz": f.tolist(),
        "clamped_electrode_input_capacitance_f": cin.tolist(),
        "clamped_electrode_input_conductance_s": ydut[:, 0, 0].real.tolist(),
        "loading_loss_db": float(loss) if sim.meta["niche"]["sensing"] == "voltage" else None,
        "front_voltage_transfer_ratio_at_1khz": float(actual / unloaded),
        "capsule_corner_cases": rows,
        "definition": "3-port Y subtraction of the capsule; input C/G with other electrodes AC-clamped. Dynamic floating/bootstrap behavior is retained in raw Y matrix.",
        "dut_y_real": ydut.real.tolist(),
        "dut_y_imag": ydut.imag.tolist(),
    }
    return result(
        "pass" if all(r["status"] == "pass" for r in rows) else "fail",
        m,
        coverage="Electrical loading and 16 assumed capsule corners; not an acoustic polar or mechanical model",
    )


def startup(sim, ctx):
    raw = sim.execute(
        "startup",
        "tran 1m 5 0 1m\nwrite startup.raw all",
        ["startup.raw"],
        {"START": 1, "PRESSURE_AC": 0},
    )["startup.raw"]
    t = raw["time"].real
    rail = raw.voltage("rail", "mic_g").real
    target = float(ctx["nominal"]["op.raw"].voltage("rail", "mic_g")[0])
    bad = np.flatnonzero(abs(rail - target) > 0.01 * max(abs(target), 1e-12))
    settled = float(t[min(int(bad[-1]) + 1, len(t) - 1)]) if len(bad) else float(t[0])
    peak = float(np.max(abs(raw.voltage("pp", "pn"))))
    ok = (
        abs(rail[-1] - target) <= 0.01 * abs(target)
        and settled < thresholds()["startup_settling_s"]["value"]
    )
    return result(
        "pass" if ok else "fail",
        {
            "settling_to_1percent_s": settled,
            "rail_target_v": target,
            "rail_final_v": float(rail[-1]),
            "differential_output_peak_v": peak,
        },
        coverage="Symmetric cold turn-on PWL. Hot-plug, asymmetric pin connection, disconnect, RF/ESD pending.",
    )


def stability(sim, ctx):
    raw = ctx["nominal"]["ac.raw"]
    f = raw["frequency"].real
    gain = abs(raw.voltage("pp", "pn"))
    ref = abs(at_frequency(f, raw.voltage("pp", "pn"), 1000))
    peaking = db(np.max(gain[f >= 20000]) / ref)
    ranges = scenario_ranges()
    env = read_yaml(ROOT / "spec/design-constraints.yaml")["environment"]
    rows = [
        screen(sim, "cable_load_corner", dict(LEN=l, ZIN=z, ZM=m))
        for l, z, m in product(
            ranges["LEN"],
            [env["preamp_differential_load_ohm"]["stress_min"], ranges["ZIN"][1]],
            ranges["ZM"],
        )
    ]
    m = {
        "hf_peaking_db": peaking,
        "analyzed_max_hz": float(f[-1]),
        "cable_load_cases": rows,
        "loop_phase_margin_deg": None,
        "oscillation_ruled_out": False,
        "reason": "Closed-loop AC peaking cannot prove loop stability; declared injection ports/Nyquist or return-ratio tests required.",
    }
    if peaking > thresholds()["hf_peaking_db"]["value"] or any(x["status"] != "pass" for x in rows):
        return result("fail", m, coverage="HF and cable/load screening")
    return result(
        "incomplete",
        m,
        reason="Loop stability and multi-loop/servo interaction analysis not implemented yet; cannot qualify from peaking alone",
    )


from .qualification import result, thresholds, current, response, scenario_ranges
