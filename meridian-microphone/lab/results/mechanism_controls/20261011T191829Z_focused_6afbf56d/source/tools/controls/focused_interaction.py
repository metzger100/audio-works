# SPDX-License-Identifier: GPL-3.0-or-later
"""Preserved recovery and conditional voltage-return diagnostic children."""

from meridian_lab.core import write_json
from meridian_lab.metrics import at_frequency
import numpy as np


def interaction(candidate, out, make_sim):
    sim = make_sim(candidate, out / "interaction" / candidate, out, dict(parameters={}))
    row = dict(candidate=candidate, jobs=sim.jobs, status="incomplete")
    try:
        raw = sim.execute(
            "recovery",
            "alter @v.xenv.vphantom[pwl] [ 0 48 1 48 1.001 44 2 44 2.001 48 5 48 ]\ntran 1m 5 0 1m\nwrite recovery.raw all",
            ["recovery.raw"],
            {"PRESSURE_AC": 0},
        )["recovery.raw"]
        row["recovery_final_nodes_v"] = {
            k: float(raw.voltage("xdut." + k, "mic_g")[-1]) for k in ["source", "raw"]
        }
        row["recovery_final_polarization_v"] = float(raw.voltage("b", "f")[-1])
        row["recovery_scope"] = "Finite5s cold/dip recovery; no extension or harmonics claim"
    except Exception as exc:
        row["recovery_error"] = str(exc)
    # Record a conditional voltage-return diagnostic at the 300kohm sense path.
    # It keeps DC and bilateral device networks. Multi-loop pole/current-injection
    # evidence is still required, so no stability pass is manufactured.
    if "RSERVOOUT_VALUE" in sim.params:
        child = out / "interaction" / candidate / "sense_injection"
        child.mkdir()
        circuit = (
            (sim.candidate / "circuit.cir")
            .read_text()
            .replace(
                "Rservosense0 source sense_div0",
                "Vloop loop source DC 0 AC 1\nRservosense0 loop sense_div0",
            )
        )
        (child / "circuit.cir").write_text(circuit)
        sim.candidate = child
        try:
            a = sim.execute(
                "voltage_return",
                "ac dec 128 .001 10Meg\nwrite loop.raw all",
                ["loop.raw"],
                {"PRESSURE_AC": 0},
            )["loop.raw"]
            ratio = -a["v(xdut.source)"] / a["v(xdut.loop)"]
            f = a["frequency"].real
            crossing = np.flatnonzero((abs(ratio[:-1]) - 1) * (abs(ratio[1:]) - 1) < 0)
            row["voltage_return_diagnostic"] = dict(
                frequency_hz=f.tolist(),
                real=ratio.real.tolist(),
                imag=ratio.imag.tolist(),
                crossing_brackets_hz=[[float(f[i]), float(f[i + 1])] for i in crossing],
                gain_at_point01hz=float(abs(at_frequency(f, ratio, 0.01))),
                minimum_distance_minus1=float(min(abs(1 + ratio))),
                stability_proof=False,
                reason="Bilateral/multiple paths, open-loop RHP poles and current injection unverified",
            )
        except Exception as exc:
            row["return_ratio_error"] = str(exc)
    write_json(out / "interaction" / candidate / "result.json", row)
    return row
