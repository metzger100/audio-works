# SPDX-License-Identifier: GPL-3.0-or-later
"""Three declared extraction/dependency repeats, preserving the first cohort."""

from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(Path(__file__).resolve().parent)]
from meridian_lab.core import read_yaml, write_json, digest
from diverse_prerequisites import parent_diagnostics
from simulation_prerequisites import Suite
from meridian_lab.architectures import coherent_amplitudes, periodic_frequencies


def main():
    parent = ROOT / "results/mechanism_controls/20261016T130909Z_diverse_00c8217a"
    original = read_yaml(parent / "plan.json")
    # Explicit finite successor: no design, model, tolerance, timestep or timeout change.
    plan = dict(original["plan"], maximum_jobs=1)
    folder = (
        ROOT
        / "results/mechanism_controls"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_diverse_followup_"
            + uuid.uuid4().hex[:8]
        )
    )
    folder.mkdir(parents=True, exist_ok=False)
    manifest = {}
    for p in (parent / "source").rglob("*"):
        if p.is_file():
            dest = folder / "source" / p.relative_to(parent / "source")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())
            manifest[str(dest.relative_to(folder / "source"))] = digest(dest)
    for p in [
        *(ROOT / "models/environment").glob("*.cir"),
        Path(__file__),
        Path(__file__).with_name("diverse_prerequisites.py"),
    ]:
        dest = folder / "source" / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(p.read_bytes())
        manifest[str(p.relative_to(ROOT))] = digest(p)
    frozen = read_yaml(folder / "source" / "research/architectures/diverse-plan-001.yaml")
    write_json(
        folder / "plan.json",
        dict(
            parent_experiment=parent.name,
            source_manifest=manifest,
            change="Freeze missing p48 environment; two exact-parent DC/AC repeats. One island carrier-off repeat with original20-30ms saved window; prior complete startup retained. No numerical tolerance/timestep/budget change.",
            maximum_jobs=3,
            timeout_s_per_job=15,
        ),
    )
    rows = parent_diagnostics(folder)
    exp = Suite(folder, plan)
    deck = (parent / "carrier_island/1_0_32/job.cir").read_text()
    # Circuit body only, exact same integration; change output storage window.
    circuit = deck.split(".options " + frozen["options"] + "\n", 1)[1].split("\n.control", 1)[0]
    circuit = circuit.replace(str(parent / "source"), str(folder / "source"))
    raw = exp.execute(
        dict(id="carrier_off"),
        "saved_window",
        circuit,
        "tran 3.125e-7 .03 .02 3.125e-7\nwrite tran.raw time v(ff) v(rr) v(recovered)",
        ["tran.raw"],
    )
    island = dict(status="unsupported")
    if raw:
        d = raw["tran.raw"]
        island = dict(
            status="executed",
            demod_peak_v=coherent_amplitudes(
                d["time"], d["v(recovered)"], periodic_frequencies(100000, 1000)
            ),
        )
    unchanged = all(digest(folder / "source" / n) == h for n, h in manifest.items())
    # Distinguish unchanged frozen bytes from expected live script evolution.
    write_json(
        folder / "results.json",
        dict(
            parents=rows,
            carrier_off=island,
            jobs=exp.jobs,
            source_manifest=manifest,
            frozen_source_unchanged=unchanged,
            parent_experiment=parent.name,
            eligible=False,
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
                parents=[x["status"] for x in rows],
                carrier_off=island["status"],
            )
        )
    )


if __name__ == "__main__":
    main()
