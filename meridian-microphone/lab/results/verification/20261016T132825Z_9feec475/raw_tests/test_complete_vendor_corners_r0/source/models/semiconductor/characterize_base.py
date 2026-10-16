#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolated device characterization against primary evidence; errors survive in records."""

from pathlib import Path
import json
import os
import re
import signal
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.core import digest, read_yaml, parse_raw, write_json
from meridian_lab.device_models import resolve


class Experiment:
    def __init__(self, folder, models, refinement=False):
        self.folder = folder
        self.models = models
        self.jobs = []
        self.refinement = refinement
        self.root = folder / "source/models"
        self.refs = read_yaml(self.root / "semiconductor/references.yaml")
        self.partial = {}

    def execute(self, model, label, circuit, commands, outputs, temp=25, refine=False):
        directory = self.folder / model["id"] / label
        directory.mkdir(parents=True, exist_ok=False)
        m = resolve(self.root, [model["id"]])[0]
        reltol = 1e-7 if refine else 1e-6
        body = f'''Meridian isolated {model["id"]} {label}
* SPDX-License-Identifier: CERN-OHL-S-2.0
.include "{m["resolved_path"]}"
.temp {temp}
.options reltol={reltol} abstol=1e-16 vntol=1e-10 gmin=1e-15 method=gear maxord=2
{circuit}
.control
set filetype=ascii
set numdgt=16
{commands}
quit
.endc
.end
'''
        (directory / "job.cir").write_text(body)
        job = dict(
            model_id=m["id"],
            label=label,
            temperature_c=temp,
            refinement=refine,
            netlist_sha256=digest(directory / "job.cir"),
            model_sha256=m["sha256"],
            model_version=m["version"],
            parent_model_id=m.get("parent_model_id"),
            model_lineage=m.get("model_lineage", []),
            source_url=m.get("source_url"),
            compatibility=m.get("ngspice_behavior"),
            directory=str(directory.relative_to(self.folder)),
        )
        self.jobs.append(job)
        env = os.environ.copy()
        env["LC_ALL"] = "C"
        if m.get("ngspice_behavior"):
            env["MERIDIAN_NGSPICE_BEHAVIOR"] = m["ngspice_behavior"]
        else:
            env.pop("MERIDIAN_NGSPICE_BEHAVIOR", None)
        try:
            process = subprocess.Popen(
                [
                    os.environ.get("MERIDIAN_NGSPICE", str(ROOT / "tools/ngspice-run")),
                    "-n",
                    "-b",
                    "job.cir",
                ],
                cwd=directory,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            try:
                stdout, stderr = process.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
                (directory / "simulator.log").write_text(stdout + "\n" + stderr)
                raise ValueError(
                    "Simulator process-group timeout after15s; partial diagnostic output preserved"
                ) from None
            log = stdout + "\n" + stderr
            (directory / "simulator.log").write_text(log)
            bad = re.search(
                r"(?im)^\s*(error\b|fatal\b|warning\b|.*timestep too small|.*singular matrix|.*convergence failed|.*analysis.*aborted)",
                log,
            )
            if process.returncode or bad:
                raise ValueError(
                    f"exit {process.returncode}: {bad.group(0) if bad else log[-300:]}"
                )
            raw = {n: parse_raw(directory / n) for n in outputs}
            job.update(status="ok", raw_data_hashes={n: digest(directory / n) for n in outputs})
            # Compact portable numeric evidence; full ASCII raw vectors remain local.
            for name, data in raw.items():
                chosen = [k for k in data.vectors if "." not in k and not k.startswith("v(x")]
                columns = []
                names = []
                for k in chosen:
                    v = data[k]
                    columns.append(v.real)
                    names.append(k + "_real" if np.iscomplexobj(v) else k)
                    if np.iscomplexobj(v):
                        columns.append(v.imag)
                        names.append(k + "_imag")
                target = directory / (name + ".csv")
                np.savetxt(
                    target,
                    np.array(columns).T,
                    delimiter=",",
                    header=",".join(names),
                    comments="",
                    fmt="%.12g",
                )
                job.setdefault("csv_hashes", {})[target.name] = digest(target)
            write_json(directory / "job.json", job)
            return raw
        except (ValueError, OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
            job.update(status="error", reason=str(exc))
            (directory / "failure.json").write_text(json.dumps(job, indent=2) + "\n")
            return None


def interpolate(raw, current, target, vector):
    x = np.asarray(current).real
    valid = (x > 0) & np.isfinite(x)
    x = x[valid]
    y = np.asarray(raw[vector]).real[valid]
    order = np.argsort(x)
    x = x[order]
    y = y[order]
    if len(x) < 2 or not x[0] <= target <= x[-1]:
        raise ValueError("Target current outside simulated transfer curve")
    return float(np.interp(target, x, y))


def compare(
    name,
    value,
    lo=None,
    hi=None,
    typ=None,
    relative=0.20,
    evidence="guaranteed_limit",
    condition="",
):
    if typ is not None:
        lo = typ * (1 - relative)
        hi = typ * (1 + relative)
        evidence = "typical_accuracy_screen"
    ok = (lo is None or value >= lo) and (hi is None or value <= hi)
    return dict(
        name=name,
        value=float(value),
        status="pass" if ok else "fail",
        lower=lo,
        upper=hi,
        typical=typ,
        relative_disagreement=None if typ is None else float((value - typ) / typ),
        evidence=evidence,
        condition=condition,
    )


def fet_circuit(sub, gate, drain=5, high=25):
    return f"Vd d 0 {drain}\nVg g 0 DC {gate} AC 1\nVh h 0 {high}\nVl l 0 -5\nXq d g 0 h l {sub}\nHout out 0 Vd 1\nHgate ig 0 Vg 1"


def bjt_circuit(sub, pol, vb, rs=0, vc=5):
    s = 1 if pol == "npn" else -1
    return (
        f"Vc c 0 {s * vc}\nVb inp 0 DC {s * vb} AC 1\n"
        + (f"Rsource inp b {rs}\n" if rs else "Vlink inp b 0\n")
        + f"Xq c b 0 {sub}\nHout out 0 Vc 1"
    )


def refinement(a, b, x, y, name):
    ya = a[y].real
    yb = np.interp(a[x].real, b[x].real, b[y].real)
    value = float(np.max(abs(ya - yb)) / max(float(np.ptp(ya)), 1e-12))
    return compare(
        name,
        value,
        hi=0.01,
        evidence="numerical_refinement",
        condition="range-normalized maximum difference on common grid",
    )
