#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite Prompt06 controls; no model fitting and no candidate qualification."""

from pathlib import Path
import sys, json, uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "models/semiconductor")]
from meridian_lab.core import (
    source_manifest,
    verify_spec_lock,
    write_json,
    environment_versions,
    read_yaml,
)
from meridian_lab.device_models import index, resolve
from meridian_lab.metrics import at_frequency
from characterize import Experiment, interpolate, compare


from parts_control_math import nf_db as nf_db, capacitance as capacitance


def jfet(exp, m, refs):
    rows = []
    values = {}
    sub = m["subcircuit"]
    dual = m["device_id"] == "jfe2140"

    def circuit(vg=0, vd=10):
        dev = f"Xq d g 0 h l {sub}\nVh h 0 25\nVl l 0 -5" if dual else f"Jq d g 0 {sub}"
        return f"Vd d 0 {vd}\nVg g 0 DC {vg} AC 1\n{dev}\nHout out 0 Vd 1\nHgate ig 0 Vg 1"

    for t in [-10, 25, 50]:
        out = exp.execute(
            m,
            f"transfer_{t}",
            circuit(),
            "dc Vg -2 0 .001\nwrite dc.raw v(g) i(vd) i(vg)",
            ["dc.raw"],
            t,
        )
        if not out:
            continue
        dc = out["dc.raw"]
        cur = -dc["i(vd)"]
        values[f"idss_{t}_a"] = float(cur[-1])
        if t != 25:
            continue
        rows.append(
            compare(
                "idss_25c", cur[-1], *refs["idss_a"], condition=refs["source"] + " VDS10V VGS0 25C"
            )
        )
        for id_ in [0.0001, 0.002]:
            vg = interpolate(dc, cur, id_, "v(g)")
            ns = []
            values[f"bias_{id_}"] = {"vgs_v": vg, "id_a": id_}
            for density in [64, 128]:
                out = exp.execute(
                    m,
                    f"bias_{id_}_{density}",
                    circuit(vg),
                    f"op\nwrite op.raw i(vd) i(vg)\nac dec {density} 10 10Meg\nwrite ac.raw i(vd) i(vg)\nnoise v(out) Vg dec {density} 1 100k 1\nsetplot noise1\nwrite noise.raw all",
                    ["op.raw", "ac.raw", "noise.raw"],
                    refine=density == 128,
                )
                if not out:
                    continue
                n = out["noise.raw"]
                ns.append(
                    [
                        float(at_frequency(n["frequency"], n["inoise_spectrum"], f))
                        for f in [10, 1000]
                    ]
                )
                if density == 64:
                    values[f"bias_{id_}"].update(
                        actual_id_a=-float(out["op.raw"]["i(vd)"][0]),
                        gate_current_a=float(out["op.raw"]["i(vg)"][0]),
                        en_10hz=ns[-1][0],
                        en_1khz=ns[-1][1],
                    )
                    for f, typ in refs.get("en", {}).get(id_, {}).items():
                        rows.append(
                            compare(
                                f"en_{id_}_{f}",
                                float(at_frequency(n["frequency"], n["inoise_spectrum"], f)),
                                typ=typ,
                                condition="VDS10V 25C at explicitly interpolated ID; "
                                + refs["source"],
                            )
                        )
            if len(ns) == 2:
                for i, f in enumerate([10, 1000]):
                    rows.append(
                        compare(
                            f"noise_refinement_{id_}_{f}",
                            abs(ns[1][i] / ns[0][i] - 1),
                            hi=0.01,
                            evidence="numerical_refinement",
                        )
                    )
    # Independent capacitance reference fixes bias. JFE table leaves gate bias ambiguous.
    vd = 5 if dual else 15
    target = 0.002 if dual else 0.0001
    out = exp.execute(
        m, "cap_bias", circuit(vd=vd), "dc Vg -2 0 .001\nwrite dc.raw v(g) i(vd)", ["dc.raw"]
    )
    if out:
        vg = interpolate(out["dc.raw"], -out["dc.raw"]["i(vd)"], target, "v(g)")
        out = exp.execute(
            m,
            "cap_and_gate_noise",
            circuit(vg, vd),
            "op\nwrite op.raw i(vg) i(vd)\nac lin 1 1Meg 1Meg\nwrite ac.raw i(vg)\nnoise v(ig) Vg dec 128 10 100k 1\nsetplot noise1\nwrite noise.raw all",
            ["op.raw", "ac.raw", "noise.raw"],
        )
        if out:
            cap = capacitance(-out["ac.raw"]["i(vg)"][0], 1e6)
            values["conditioned_ciss_f"] = cap
            values["gate_noise_1khz_a_sqrt_hz"] = float(
                at_frequency(
                    out["noise.raw"]["frequency"], out["noise.raw"]["onoise_spectrum"], 1000
                )
            )
            if not dual:
                rows.append(
                    compare("ciss", cap, typ=20e-12, condition="LSK170 table2 VDS15V ID100uA f1MHz")
                )
            else:
                values["ciss_scope"] = (
                    "13pF typical, VDS5V; missing explicit table frequency/gate bias prevents validation"
                )
            if dual:
                rows.append(
                    compare(
                        "current_noise_1khz",
                        values["gate_noise_1khz_a_sqrt_hz"],
                        typ=1.6e-15,
                        condition="JFE2140 table6.5 VDS5V ID2mA 25C",
                    )
                )
    out = exp.execute(
        m,
        "reverse_gate_leak",
        circuit(-30 if dual else -10, 0).replace("Vl l 0 -5", "Vl l 0 -35")
        if dual
        else circuit(-10, 0),
        "op\nwrite op.raw i(vg)",
        ["op.raw"],
    )
    if out:
        val = abs(float(out["op.raw"]["i(vg)"][0]))
        values["reverse_gate_leak_a"] = val
        rows.append(
            compare(
                "reverse_gate_leak",
                val,
                hi=60e-12 if dual else 1e-9,
                condition="25C VDS0 VGS-30V TI or -10V Linear; bound includes fixture GMIN",
            )
        )
    return rows, values


def opa(exp, m, refs):
    rows = []
    values = {}
    for vs, cm in [(5, 2), (16, 8), (36, 18)]:
        for t in [-10, 25, 50]:
            c = f"Vp p 0 {vs}\nVn n 0 0\nVin in 0 DC {cm} AC 1\nXq in out p n out guard1 guard2 {m['subcircuit']}\nRl out mid 10k\nVm mid 0 {cm}\n.options gmin=1e-16"
            out = exp.execute(
                m,
                f"follower_{vs}_{t}",
                c,
                "op\nwrite op.raw v(out) v(guard1) v(guard2) i(vin) i(vp)\nac dec 64 10 100Meg\nwrite ac.raw v(out)\nnoise v(out) Vin dec 128 10 100k 1\nsetplot noise1\nwrite noise.raw all",
                ["op.raw", "ac.raw", "noise.raw"],
                t,
            )
            if not out:
                continue
            op = out["op.raw"]
            n = out["noise.raw"]
            values[f"{vs}V_{t}C"] = {
                "out_v": float(op["v(out)"][0]),
                "guard_v": float(op["v(guard1)"][0]),
                "ib_a": float(op["i(vin)"][0]),
                "iq_a": -float(op["i(vp)"][0]),
                "en_1khz": float(at_frequency(n["frequency"], n["inoise_spectrum"], 1000)),
            }
            if t == 25:
                v = values[f"{vs}V_{t}C"]
                rows.append(
                    compare(
                        f"en_{vs}",
                        v["en_1khz"],
                        typ=15e-9,
                        condition="datasheet conditioned common mode, RL10k 25C",
                    )
                )
                rows.append(
                    compare(
                        f"ib_{vs}",
                        abs(v["ib_a"]),
                        hi=20e-15 if vs <= 16 else 75e-15,
                        condition="RH<50percent; nominal grounded simulation does not model humidity",
                    )
                )
                rows.append(
                    compare(
                        f"iq_{vs}",
                        v["iq_a"],
                        hi=400e-6,
                        condition="no-load output; model Iq fixed275u; no variation proof",
                    )
                )
    values["scope"] = (
        "Grounded only; no floating, high-Z charge feedback, humidity/board leakage, guard capacitive load or overload validation"
    )
    return rows, values


def diode(exp, m, refs):
    rows = []
    values = {}
    c = f"Vr k 0 DC 75 AC 1\nDq 0 k {m['subcircuit']}"
    for t in [25, 50]:
        out = exp.execute(m, f"reverse_{t}", c, "op\nwrite op.raw i(vr)", ["op.raw"], t)
        if out:
            i = abs(float(out["op.raw"]["i(vr)"][0]))
            values[f"leak_{t}_a"] = i
            if t == 25:
                rows.append(
                    compare("reverse_leak", i, hi=5e-9, condition="BAV199 VR75V 25C one diode")
                )
    out = exp.execute(
        m,
        "cap_0v",
        c.replace("DC 75", "DC 0"),
        "ac lin 1 1Meg 1Meg\nwrite ac.raw i(vr)",
        ["ac.raw"],
    )
    if out:
        v = capacitance(-out["ac.raw"]["i(vr)"][0], 1e6)
        values["cap_0v_f"] = v
        rows.append(compare("cap", v, hi=2e-12, condition="BAV199 VR0 f1MHz table"))
    return rows, values


def main():
    verify_spec_lock()
    plan = read_yaml(ROOT / "research/devices/parts-control-plan-002.yaml")
    manifest = source_manifest()
    folder = (
        ROOT
        / "results/device_models"
        / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_parts_" + uuid.uuid4().hex[:8])
    )
    folder.mkdir(parents=True, exist_ok=False)
    for rel in manifest:
        p = folder / "source" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ROOT / rel).read_bytes())
    available = index(folder / "source/models")
    exp = Experiment(folder, available)
    results = {}
    funcs = {
        "jfe2140": jfet,
        "lsk170a": jfet,
        "pmbt5551": bipolar,
        "bc850c": bipolar,
        "opa928": opa,
        "bav199": diode,
    }
    for id_ in plan["models"]:
        try:
            m = available[id_]
            resolve(exp.root, [id_])
            rows, values = funcs[m["device_id"]](
                exp, m, exp.refs["parts_expansion_001"][m["device_id"]]
            )
            results[id_] = {
                "comparisons": rows,
                "measurements": values,
                "status": "disagreement"
                if any(x["status"] == "fail" for x in rows)
                else "scoped_agreement",
                "behavior_validated": "only explicitly passing referenced rows; no blanket qualification",
            }
        except (ValueError, RuntimeError, OSError) as e:
            results[id_] = {"status": "error", "reason": str(e)}
        errors = [j for j in exp.jobs if j["model_id"] == id_ and j["status"] == "error"]
        if errors:
            results[id_]["status"] = "error"
            results[id_]["failed_jobs"] = len(errors)
        if len(exp.jobs) > plan["maximum_jobs"]:
            raise RuntimeError("Declared finite budget exceeded")
        write_json(
            folder / "checkpoint.json",
            {"results": results, "jobs": exp.jobs, "source_manifest": manifest, "complete": False},
        )
        print(id_, results[id_]["status"], flush=True)
    unchanged = source_manifest() == manifest
    write_json(
        folder / "results.json",
        {
            "schema_version": 1,
            "experiment_id": folder.name,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "plan": plan,
            "source_manifest": manifest,
            "source_unchanged": unchanged,
            "versions": environment_versions(),
            "results": results,
            "jobs": exp.jobs,
            "eligible_for_production": False,
            "candidate_evaluations": 0,
            "parent_experiments": plan.get("parent_experiments", []),
            "status": "recorded_unqualified" if unchanged else "source_integrity_error",
        },
    )
    print(
        json.dumps(
            {
                "record": str(folder / "results.json"),
                "jobs": len(exp.jobs),
                "errors": sum(j["status"] == "error" for j in exp.jobs),
                "source_unchanged": unchanged,
            }
        )
    )
    return (
        2
        if not unchanged or any(x["status"] in ["error", "disagreement"] for x in results.values())
        else 0
    )


from parts_bipolar_control import bipolar as bipolar

if __name__ == "__main__":
    raise SystemExit(main())
