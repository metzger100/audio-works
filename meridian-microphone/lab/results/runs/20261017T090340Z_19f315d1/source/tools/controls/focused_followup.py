# SPDX-License-Identifier: GPL-3.0-or-later
"""Append-only board-control repair and independent final-network checks."""

from datetime import datetime, timezone
from pathlib import Path
import sys
import uuid

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(Path(__file__).resolve().parent)]
from meridian_lab.core import digest, read_yaml, write_json, parse_raw
from meridian_lab.cli import implementation_manifest
from meridian_lab.robust_scenarios import thermal_passive_scenarios
from focused_hypotheses import scenario_set, frozen_sim
from simulation_prerequisites import Suite

PARENT = "results/mechanism_controls/20261011T192308Z_focused_1992e85a"


def local_filter(suite, filtered, adverse=False):
    r, cp, c, ir, esr, esl = 1e6, 1e-7, 1e-7, 1e11, 0.7957747154594768, 3e-8
    if adverse:
        c, esl = 0.9e-7, 5e-8
    circuit = (
        "Vraw raw 0 DC 24 AC 1\nRp raw pol 10Meg\nCp pol 0 100n\nRb pol b 1Meg\nIback pol b AC 0"
    )
    if filtered:
        circuit += f"\nLfilm b l {esl}\nRfilm l x {esr}\nCfilm x 0 {c}\nRir b 0 {ir}"
    else:
        # A local backplate parasitic provides a finite physically interpretable
        # load; the complete capsule/JFE circuit is tested separately.
        c = 1e-10
        circuit += "\nCback b 0 100p"
    label = "filtered_adverse" if adverse else "filtered" if filtered else "unfiltered"
    raw = suite.execute(
        dict(id="final_network_oracle"),
        label,
        circuit,
        "ac dec 128 .001 10Meg\nwrite raw.raw all\nalter Vraw ac=0\nalter Iback ac=1\nac dec 128 .001 10Meg\nwrite back.raw all",
        ["raw.raw", "back.raw"],
    )
    if not raw:
        return dict(label=label, status="error")
    f = raw["raw.raw"]["frequency"].real
    s = 2j * np.pi * f
    gp, gb = 1e-7, 1 / r
    yb = 1 / ir + 1 / (esr + s * esl + 1 / (s * c)) if filtered else s * c
    a = gp + gb + s * cp
    determinant = a * (gb + yb) - gb * gb
    expected = {"raw.raw": gp * gb / determinant, "back.raw": (gp + s * cp) / determinant}
    errors = {k: float(max(abs(raw[k]["v(b)"] / value - 1))) for k, value in expected.items()}
    return dict(
        label=label,
        status="pass" if max(errors.values()) < 1e-7 else "fail",
        maximum_relative_errors=errors,
        scope="Actual local polarization R/C/IR/ESR/ESL two-node network; no capsule/nonlinear transfer substitution",
    )


def reverse_return(candidate, out):
    sim = frozen_sim(candidate, out / "reverse_return" / candidate, out, dict(parameters={}))
    child = sim.directory / "implementation"
    child.mkdir()
    original = (sim.candidate / "circuit.cir").read_text()
    circuit = original.replace(
        "Rservosense0 source sense_div0",
        "Vloop source loop DC 0 AC 1\nRservosense0 loop sense_div0",
    )
    (child / "circuit.cir").write_text(circuit)
    sim.candidate = child
    row = dict(candidate=candidate, status="incomplete", jobs=sim.jobs, stability_proof=False)
    try:
        raw = sim.execute(
            "reverse_voltage_return",
            "op\nwrite op.raw all\nac dec 128 .001 10Meg\nwrite loop.raw all",
            ["op.raw", "loop.raw"],
            {"PRESSURE_AC": 0},
        )
        old = parse_raw(ROOT / PARENT / "interaction" / candidate / "0002_voltage_return/loop.raw")
        ratio = -raw["loop.raw"]["v(xdut.source)"] / raw["loop.raw"]["v(xdut.loop)"]
        previous = -old["v(xdut.source)"] / old["v(xdut.loop)"]
        row.update(
            sign_reversal_relative_error=float(max(abs(ratio - previous)) / max(abs(previous))),
            source_dc_v=float(raw["op.raw"].voltage("xdut.source", "mic_g")[0]),
            reason="Voltage-source orientation invariance checked; bilateral current injection and RHP pole count remain unsupported",
        )
    except Exception as exc:
        row["reason"] = str(exc)
    return row


def main():
    parent = ROOT / PARENT
    m = read_yaml(parent / "manifest.json")
    # This is a declared repair/equation control, not a new value search. No
    # completed parent cell or frozen source is rewritten or silently pooled.
    plan = dict(
        parent_batch=PARENT,
        maximum_jobs=25,
        timeout_s_per_job=15,
        options="reltol=1e-6 abstol=1e-16 vntol=1e-10 gmin=1e-15 method=gear maxord=2",
        scope="Three board-control numeric-type repairs, six remaining +50C TCR endpoints, three final-network oracles, two voltage orientation checks",
        budget="No optimizer/design vectors, no invariant or uncertainty changes; C design reservation unchanged",
        stopping_rule="One execution per declared cell; retain errors and no further design search",
    )
    for n, sha in m["sources"].items():
        if n.startswith(("spec/", "models/", "src/", "tools/ngspice")) and digest(ROOT / n) != sha:
            raise ValueError("Parent common input changed: " + n)
    for c, manifest in m["implementations"].items():
        if implementation_manifest(ROOT / "candidates" / c) != manifest:
            raise ValueError("Parent candidate changed: " + c)
    out = (
        ROOT
        / "results/mechanism_controls"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_focused_followup_"
            + uuid.uuid4().hex[:8]
        )
    )
    out.mkdir(exist_ok=False)
    for directory in ["source", "implementations"]:
        for p in (parent / directory).rglob("*"):
            if p.is_file():
                q = out / directory / p.relative_to(parent / directory)
                q.parent.mkdir(parents=True, exist_ok=True)
                q.write_bytes(p.read_bytes())
    controls = {
        "tools/controls/" + n: digest(ROOT / "tools/controls" / n)
        for n in ["focused_followup.py", "focused_hypotheses.py", "focused_driver.py"]
    }
    for n in controls:
        (out / "source" / n).write_bytes((ROOT / n).read_bytes())
    write_json(out / "plan.json", plan)
    write_json(out / "manifest.json", dict(parent=m, repaired_controls=controls))
    rows = []
    for c in m["implementations"]:
        rows.append(
            scenario_set(
                c,
                out,
                dict(
                    id="board_leakage_repaired", board_leakage_ohm=1e11, parameters=dict(LEAK=1e9)
                ),
            )
        )
        meta = read_yaml(out / "implementations" / c / "topology.yaml")
        bom = read_yaml(out / "implementations" / c / "bom.yaml")
        for i, s in enumerate(thermal_passive_scenarios(meta, bom)[2:]):
            s["id"] = f"tolerance_TCR_50_{i}"
            for k, d in meta["population"].items():
                if k.startswith("COUT"):
                    s["parameters"][k] = d["range"][i if k.startswith("COUTP") else 1 - i]
                if k in [
                    "CBACKFILTER_VALUE",
                    "RCBACKFILTERINSULATION_VALUE",
                    "RCBACKFILTERLOSS_VALUE",
                    "LBACKFILTER_VALUE",
                ]:
                    s["parameters"][k] = d["range"][i]
            rows.append(scenario_set(c, out, s))
    suite = Suite(out / "oracles", plan)
    oracles = [
        local_filter(suite, False),
        local_filter(suite, True),
        local_filter(suite, True, True),
    ]
    reverse = [reverse_return(c, out) for c in m["implementations"] if c != "candidate_0019"]
    unchanged = all(digest(ROOT / n) == h for n, h in controls.items())
    write_json(
        out / "results.json",
        dict(
            rows=rows,
            oracles=oracles,
            jobs=suite.jobs,
            reverse_return=reverse,
            parent_batch=PARENT,
            complete=True,
            eligible=False,
            source_unchanged=unchanged,
            C_boundary_correction="13.5557796V rail and29.5293276V raw are observed0019 fixed-parent boundary, not0023 servo; equations/results unchanged",
        ),
    )
    (out / "batch.sha256").write_text(
        "".join(
            f"{digest(p)}  {p.relative_to(ROOT)}\n" for p in sorted(out.rglob("*")) if p.is_file()
        )
    )
    print(out.relative_to(ROOT), unchanged, flush=True)


if __name__ == "__main__":
    main()
