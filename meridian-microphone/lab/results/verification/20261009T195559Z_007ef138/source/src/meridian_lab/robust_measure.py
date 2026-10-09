# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: GPL-3.0-or-later
"""Budgeted, single-axis optimization of explicitly scoped SPICE scenarios.

No probabilistic interpretation is assigned to guaranteed bounds. A scenario
optimum is neither an all-corner bound nor a qualified implementation.
"""

from copy import deepcopy
import re
import time


from .core import ROOT, Simulator, read_yaml, source_manifest, write_json
from .cli import implementation_manifest
from . import qualification as q


AXES = {
    "response": ("frequency_response", "response_deviation_db", "minimize", None),
    "current": ("operating_point", "current_a", "minimize", None),
    "noise": ("noise", "electronics_noise_pa_rms", "minimize", "validated_noise_models"),
    "distortion": ("distortion", "thd_percent", "minimize", "validated_nonlinear_models"),
    "headroom": ("headroom", "headroom_pa_rms", "maximize", "validated_nonlinear_models"),
    "loading": ("loading", "loading_loss_db", "minimize", "validated_loading_models"),
    "balance": ("balance", "impedance_mismatch_fraction", "minimize", "validated_port_models"),
    "drive": ("output_impedance", "output_impedance_ohm", "minimize", "validated_port_models"),
    "complexity": (None, "component_count", "minimize", "realized_component_count"),
}


def measure(candidate, directory, snapshot, overrides, scenarios, axis="response"):
    rows = []
    for i, scenario in enumerate(scenarios):
        started = time.monotonic()
        sim = Simulator(
            candidate,
            directory / f"scenario_{i:04d}",
            {**overrides, **scenario.get("parameters", {})},
        )
        sim.candidate = snapshot / "candidate"
        sim.model_root = snapshot / "source/models"
        sim.meta = deepcopy(sim.meta)
        if scenario.get("model_replacement"):
            sim.meta["semiconductor_models"] = [
                scenario["model_replacement"] if m.startswith("jfe150") else m
                for m in sim.meta["semiconductor_models"]
            ]
            # Separate immutable scenario implementation; never mutate the parent
            # snapshot or splice independent BETA/VTO parameters into a device.
            corner_candidate = sim.directory / "candidate"
            corner_candidate.mkdir()
            circuit = (sim.candidate / "circuit.cir").read_text()
            symbol = scenario["model_replacement"].upper()
            (corner_candidate / "circuit.cir").write_text(
                re.sub(r"(?im)\bJFE150\s*$", symbol, circuit)
            )
            sim.candidate = corner_candidate
        row = {"scenario": scenario, "status": "error", "jobs": sim.jobs}
        try:
            ctx = {
                "nominal": sim.execute("dc_feasibility", "op\nwrite op.raw all", ["op.raw"]),
                "checks": {},
            }
            op = q.operating_point(sim, ctx)
            ctx["checks"]["operating_point"] = op
            row.update(
                current_a=op["metrics"]["current_a"],
                polarization_dc_v=op["metrics"]["polarization_dc_v"],
            )
            if op["status"] != "pass":
                row.update(status="fail", stage="DC infeasible; expensive analyses skipped")
            else:
                ctx["nominal"].update(sim.op_ac("ac_feasibility"))
                fr = q.frequency_response(sim, ctx)
                ctx["checks"]["frequency_response"] = fr
                row.update(
                    response_deviation_db=fr["metrics"]["response_deviation_db"],
                    sensitivity_v_per_pa=fr["metrics"]["sensitivity_v_per_pa_at_1khz"],
                    status=fr["status"],
                    stage="DC/AC screen",
                )
                check, metric, _, _ = AXES[axis]
                if axis == "complexity":
                    bom = read_yaml(snapshot / "candidate/bom.yaml")
                    row[metric] = sum(p["quantity"] for p in bom["physical_parts"])
                elif check not in {"operating_point", "frequency_response"}:
                    # Prerequisite audited by caller; preserve dependencies/errors.
                    for name in {
                        "noise": ["noise"],
                        "distortion": ["distortion"],
                        "headroom": ["distortion", "headroom"],
                        "loading": ["loading"],
                        "balance": ["output_impedance", "balance"],
                        "drive": ["output_impedance"],
                    }[axis]:
                        ctx["checks"][name] = q.CHECKS[name](sim, ctx)
                    value = ctx["checks"][check]["metrics"].get(metric)
                    if value is None:
                        raise ValueError("Objective has absent or censored metric")
                    row[metric] = value
        except Exception as exc:
            row.update(status="error", reason=f"{type(exc).__name__}: {exc}")
        row["runtime_s"] = time.monotonic() - started
        rows.append(row)
    return rows


def freeze(directory, candidate):
    manifest = source_manifest()
    implementation = implementation_manifest(ROOT / "candidates" / candidate)
    for relative in manifest:
        p = directory / "source" / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ROOT / relative).read_bytes())
    (directory / "candidate").mkdir()
    for relative in implementation:
        target = directory / "candidate" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / "candidates" / candidate / relative).read_bytes())
    write_json(
        directory / "frozen_manifest.json", {"sources": manifest, "implementation": implementation}
    )
    return manifest, implementation
