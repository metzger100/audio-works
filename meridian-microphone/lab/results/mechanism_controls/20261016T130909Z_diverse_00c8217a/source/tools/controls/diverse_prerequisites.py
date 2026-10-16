# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite Prompt10 suite; immutable cohorts and strict failure retention."""

from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import uuid

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(Path(__file__).resolve().parent)]
from meridian_lab.core import (
    Simulator,
    digest,
    read_yaml,
    write_json,
    verify_spec_lock,
    environment_versions,
)
from meridian_lab.device_models import resolve
from meridian_lab.bounded import owned_parts
from meridian_lab.metrics import at_frequency
from simulation_prerequisites import Suite
from diverse_fixtures import bjt_oracles, cmos_controls, complex_record
from diverse_carrier import islands, seeded_control

PLAN = "research/architectures/diverse-plan-001.yaml"


def evidence_audit():
    rows = []
    for cid in ["0012", "0024", "0010", "0014", "0013", "0019", "0023", "0025"]:
        path = ROOT / "candidates" / ("candidate_" + cid)
        pointer = read_yaml(path / "results.json")
        result = read_yaml(ROOT / pointer["result_file"])
        checks = result["checks"]
        rows.append(
            dict(
                candidate=cid,
                circuit_sha256=digest(path / "circuit.cir"),
                prior_experiment=pointer["latest_experiment"],
                original_result_sha256=digest(ROOT / pointer["result_file"]),
                checks={
                    k: dict(status=v["status"], reason=v.get("reason")) for k, v in checks.items()
                },
                response_metrics=checks["frequency_response"]["metrics"],
                noise_metrics=checks["noise"]["metrics"],
                eligible=result.get("eligible", False),
            )
        )
    return rows


def parent_diagnostics(folder):
    rows = []
    for cid in ["candidate_0012", "candidate_0024"]:
        sim = Simulator(cid, folder / cid)
        sim.model_root = folder / "source/models"
        sim.candidate = folder / "source/candidates" / cid
        sim.meta = read_yaml(sim.candidate / "topology.yaml")
        row = dict(
            candidate=cid, scope="unchanged nominal full-DUT DC/AC diagnostic only", jobs=sim.jobs
        )
        try:
            raw = sim.execute(
                "nominal",
                "op\nwrite op.raw all\nac dec 64 1 10Meg\nwrite ac.raw all",
                ["op.raw", "ac.raw"],
            )
            op, ac = raw["op.raw"], raw["ac.raw"]
            row.update(
                status="executed",
                dc_nodes={
                    k: float(op[k][0])
                    for k in ["v(f)", "v(b)", "v(xdut.outa)", "v(xdut.ref)", "v(rail)"]
                },
                base_current_a=float(op["i(v.xdut.vqinput_1)"][0]),
                base_ac_current_1khz=complex_record(
                    at_frequency(ac["frequency"], ac["i(v.xdut.vqinput_1)"], 1000)
                ),
                ac_nodes={
                    str(f): {
                        k: complex_record(at_frequency(ac["frequency"], ac[k], f))
                        for k in ["v(f)", "v(b)", "v(xdut.outa)", "v(pp)", "v(pn)"]
                    }
                    for f in [20, 1000, 20000]
                },
            )
            # Direct capsule-current KCL checks the complete original topology,
            # not the simplified finite-gain stage's unknown device parameters.
            f = ac["frequency"].real
            vf, vo = ac["v(f)"], ac["v(xdut.outa)"]
            cf = 1e-7
            yf = np.full(len(f), 2e-6, dtype=complex)
            if cid.endswith("0024"):
                yseries = 1 / 1e10 + 1 / (1.5915494309 + 1 / (2j * np.pi * f * 1e-10))
                yf += 1 / (1 / (2j * np.pi * f * cf) + 1 / yseries)
            else:
                yf += 2j * np.pi * f * cf
            ib = ac["i(v.xdut.vqinput_1)"]
            row["reset_current_dc_a"] = float((op["v(xdut.outa)"][0] - op["v(f)"][0]) * 2e-6)
            row["feedback_current_1khz_a_per_pa"] = complex_record(
                at_frequency(f, (vo - vf) * yf, 1000)
            )
            # Save full branch terms for independent diagnostic replay.
            row["base_to_feedback_1khz_magnitude_ratio"] = float(
                abs(at_frequency(f, ib / ((vo - vf) * yf), 1000))
            )
        except Exception as exc:
            row.update(status="error", reason=f"{type(exc).__name__}: {exc}")
        write_json(folder / cid / "diagnostic.json", row)
        rows.append(row)
    return rows


def main():
    verify_spec_lock()
    plan = read_yaml(ROOT / PLAN)
    models = resolve(ROOT / "models", plan["models"])
    for m in models:
        m["file"] = "models/" + m["path"]
        m.pop("resolved_path")
    paths = [ROOT / PLAN, Path(__file__), ROOT / "tools/ngspice-run", ROOT / "requirements.txt"]
    for directory in ["src", "spec", "models/capsule", "models/semiconductor"]:
        paths += [
            p
            for p in (ROOT / directory).rglob("*")
            if p.is_file() and p.suffix in {".py", ".cir", ".yaml"}
        ]
    paths += [ROOT / m["file"] for m in models]
    paths += [ROOT / "models/semiconductor/vendor/bc846b.lib"]
    for private_batch in (ROOT / "research/architecture_sources/local").glob("*_diverse_*"):
        paths += [p for p in private_batch.rglob("*") if p.is_file()]
    for name in ["diverse_fixtures.py", "diverse_carrier.py", "simulation_prerequisites.py"]:
        paths.append(Path(__file__).with_name(name))
    for path in (ROOT / "tools/ngspice/usr").rglob("*"):
        if path.is_file() and (path.name == "ngspice" or path.suffix in {".cm", ".so"}):
            paths.append(path)
    for cid in plan["parents"] + ["candidate_0019", "candidate_0023", "candidate_0025"]:
        paths += [
            p
            for p in (ROOT / "candidates" / cid).rglob("*")
            if p.is_file() and p.name != "INDEX.md"
        ]
    for name in [
        "research/sources.yaml",
        "research/sources/mechanisms.yaml",
        "research/sources/simulator.yaml",
        "research/sources/devices.yaml",
        "search/families.yaml",
        "search/concepts.yaml",
        "research/architectures/diverse-source-notes-001.md",
        "research/architectures/diverse-sources-001.json",
    ]:
        p = ROOT / name
        paths.append(p)
        if p.suffix in {".yaml", ".yml", ".json"}:
            paths += owned_parts(p)
    manifest = {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(paths))}
    folder = (
        ROOT
        / "results/mechanism_controls"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_diverse_"
            + uuid.uuid4().hex[:8]
        )
    )
    folder.mkdir(parents=True, exist_ok=False)
    for name, sha in manifest.items():
        dest = folder / "source" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / name).read_bytes())
        if digest(dest) != sha:
            raise ValueError("Source changed during freeze")
    write_json(
        folder / "plan.json",
        dict(plan=plan, models=models, source_manifest=manifest, versions=environment_versions()),
    )
    exp = Suite(folder, plan)
    rows = dict(prior=evidence_audit())
    write_json(folder / "prior.json", rows["prior"])
    for name, callback in [
        ("bjt", lambda: bjt_oracles(exp)),
        ("parents", lambda: parent_diagnostics(folder)),
        ("cmos", lambda: cmos_controls(exp, models[1:])),
        ("island", lambda: islands(exp)),
        ("seeded", lambda: seeded_control(folder, plan)),
    ]:
        try:
            rows[name] = callback()
        except Exception as exc:
            rows[name] = dict(status="error", reason=f"{type(exc).__name__}: {exc}")
        write_json(folder / (name + ".json"), rows[name])
        print(name, "recorded", flush=True)
    unchanged = all(digest(ROOT / name) == sha for name, sha in manifest.items())
    write_json(
        folder / "results.json",
        dict(
            experiment_id=folder.name,
            results=rows,
            jobs=exp.jobs,
            source_manifest=manifest,
            source_unchanged=unchanged,
            eligible=False,
            complete=True,
            plan=plan,
        ),
    )
    files = sorted(p for p in folder.rglob("*") if p.is_file())
    (folder / "batch.sha256").write_text(
        "".join(f"{digest(p)}  {p.relative_to(ROOT)}\n" for p in files)
    )
    print(
        json.dumps(
            dict(
                folder=str(folder.relative_to(ROOT)),
                jobs=len(exp.jobs),
                errors=sum(j["status"] == "error" for j in exp.jobs),
                source_unchanged=unchanged,
            )
        )
    )


if __name__ == "__main__":
    main()
