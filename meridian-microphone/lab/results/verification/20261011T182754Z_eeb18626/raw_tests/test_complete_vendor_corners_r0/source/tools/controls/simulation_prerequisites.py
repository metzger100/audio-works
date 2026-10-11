# SPDX-License-Identifier: GPL-3.0-or-later
"""Frozen finite isolated suite; failed parents and complete waves remain evidence."""

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import signal
import subprocess
import sys
import uuid

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(Path(__file__).resolve().parent)]
from meridian_lab.core import (
    digest,
    read_yaml,
    parse_raw,
    write_json,
    verify_spec_lock,
    environment_versions,
)
from meridian_lab.device_models import resolve
from meridian_lab.bounded import owned_parts
from meridian_lab.nonlinear import settled_spectrum
from prerequisite_math import rc_response, synthetic_rms
from prerequisite_fixtures import jfet, bipolar, opa

PLAN = "research/devices/simulation-prerequisites-plan-001.yaml"


def supporting_sources():
    """Freeze transitive documentary pages and the loaded local code-model runtime."""
    paths = []
    for name in [
        "research/devices/simulation-prerequisites-sources-001.json",
        "research/sources.yaml",
        "research/sources/devices.yaml",
        "research/sources/simulator.yaml",
    ]:
        path = ROOT / name
        paths.extend([path, *owned_parts(path)])
    paths.extend((ROOT / "tools/ngspice/usr/lib/ngspice").glob("*.cm"))
    return sorted(set(paths))


class Suite:
    def __init__(self, folder, plan):
        self.folder, self.plan, self.jobs = folder, plan, []

    def execute(self, model, label, circuit, commands, outputs, temp=25):
        if len(self.jobs) >= self.plan["maximum_jobs"]:
            raise ValueError("Frozen job budget exhausted")
        folder = self.folder / model["id"] / label
        folder.mkdir(parents=True, exist_ok=False)
        path = self.folder / "source" / model["file"] if model.get("file") else None
        if path and digest(path) != model["sha256"]:
            raise ValueError("Frozen model hash changed")
        include = f'.include "{path}"\n' if path else ""
        body = (
            f"Meridian prerequisite {model['id']} {label}\n* SPDX-License-Identifier: CERN-OHL-S-2.0\n"
            f"{include}.temp {temp}\n.options {self.plan['options']}\n{circuit}\n.control\n"
            f"set filetype=ascii\nset numdgt=16\n{commands}\nquit\n.endc\n.end\n"
        )
        (folder / "job.cir").write_text(body)
        job = dict(
            model=model,
            label=label,
            temperature_c=temp,
            directory=str(folder.relative_to(self.folder)),
            netlist_sha256=digest(folder / "job.cir"),
            options=self.plan["options"],
            timeout_s=self.plan["timeout_s_per_job"],
        )
        self.jobs.append(job)
        env = os.environ.copy()
        env["LC_ALL"] = "C"
        if model.get("ngspice_behavior"):
            env["MERIDIAN_NGSPICE_BEHAVIOR"] = model["ngspice_behavior"]
        else:
            env.pop("MERIDIAN_NGSPICE_BEHAVIOR", None)
        try:
            process = subprocess.Popen(
                [str(ROOT / "tools/ngspice-run"), "-n", "-b", "job.cir"],
                cwd=folder,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            try:
                stdout, stderr = process.communicate(timeout=job["timeout_s"])
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
                (folder / "simulator.log").write_text(stdout + "\n" + stderr)
                raise ValueError(
                    f"{job['timeout_s']}s process-group timeout; partial log/waveform retained"
                ) from None
            log = stdout + "\n" + stderr
            (folder / "simulator.log").write_text(log)
            bad = re.search(
                r"(?im)^\s*(error\b|fatal\b|warning\b|.*timestep too small|.*singular matrix|.*convergence failed|.*analysis.*aborted)",
                log,
            )
            if process.returncode or bad:
                raise ValueError(
                    f"exit {process.returncode}: {bad.group(0) if bad else log[-300:]}"
                )
            data = {name: parse_raw(folder / name) for name in outputs}
            job["status"] = "ok"
            for name, raw in data.items():
                chosen = [
                    k
                    for k in raw.vectors
                    if k
                    in [
                        "time",
                        "frequency",
                        "v(g)",
                        "v(s)",
                        "v(c)",
                        "v(out)",
                        "i(vd)",
                        "i(vb)",
                        "i(vg)",
                        "i(vrail)",
                        "onoise_spectrum",
                        "inoise_spectrum",
                    ]
                ]
                if chosen:
                    np.savetxt(
                        folder / (name + ".csv"),
                        np.column_stack([raw[k].real for k in chosen]),
                        delimiter=",",
                        header=",".join(chosen),
                        comments="",
                        fmt="%.16g",
                    )
            return data
        except (ValueError, OSError, RuntimeError) as exc:
            job.update(status="error", reason=str(exc))
            return None
        finally:
            job["retained_hashes"] = {p.name: digest(p) for p in folder.iterdir() if p.is_file()}
            write_json(folder / "job.json", job)


def oracles(exp):
    model = dict(id="analytic_oracles")
    rows = {}
    for step in [2e-6, 1e-6]:
        c = "Vin in 0 PWL(0 0 .001 0 .001000001 1 .012 1)\nR1 in out 1k\nC1 out 0 1u"
        raw = exp.execute(
            model, f"rc_{step}", c, f"tran {step} .012 0 {step}\nwrite tran.raw all", ["tran.raw"]
        )
        if raw:
            d = raw["tran.raw"]
            error = float(np.max(abs(d["v(out)"] - rc_response(d["time"]))))
            rows[f"rc_{step}"] = dict(max_absolute_error_v=error, pass_oracle=error < 0.01)
    terms = "+".join(f".001/{h}*sin({h}*(2*pi*1000*time+.37)+.13*{h})" for h in range(4, 11))
    c = (
        "Blin linear 0 V='sin(2*pi*1000*time+.37)'\n"
        f"Bnon out 0 V='v(linear)+.1*v(linear)^2+.04*v(linear)^3+{terms}'"
    )
    raw = exp.execute(model, "synthetic", c, "tran 1u .064 0 1u\nwrite tran.raw all", ["tran.raw"])
    if raw:
        d = raw["tran.raw"]
        h = settled_spectrum(d["time"], d["v(out)"], 1000, 0.032)
        error = float(np.max(abs(np.array(h["harmonics_v_rms"]) / synthetic_rms() - 1)))
        linear = settled_spectrum(d["time"], d["v(linear)"], 1000, 0.032)
        rows["synthetic"] = dict(
            harmonics=h,
            maximum_relative_error=error,
            pass_oracle=error < 0.01,
            linear_thd_percent=linear["thd_percent"],
            linear_output_rms_v=linear["harmonics_v_rms"][0],
        )
    return rows


def main():
    verify_spec_lock()
    plan = read_yaml(ROOT / PLAN)
    models = []
    for mid in plan["models"]:
        if mid == "jfe150_tina_isolated":
            name = plan["source_receipts"] + "/slpm350b/member_001"
            m = dict(
                id=mid,
                device_id="jfe150",
                subcircuit="JFE150",
                file=name,
                sha256=digest(ROOT / name),
                version="TI Final1.2 26SEP2024 SLPM350B literal member",
                ngspice_behavior="ps",
                duplicate_of="jfe150_generic",
                isolated_only=True,
            )
        else:
            m = resolve(ROOT / "models", [mid])[0]
            m["file"] = "models/" + m["path"]
            m.pop("resolved_path")
        models.append(m)
    paths = [
        ROOT / PLAN,
        ROOT / "tools/ngspice-run",
        *supporting_sources(),
    ]
    for directory in ["src", "spec", "models/semiconductor"]:
        paths += [
            p for p in (ROOT / directory).rglob("*") if p.is_file() and p.suffix in {".py", ".yaml"}
        ]
    paths += [
        Path(__file__),
        Path(__file__).with_name("prerequisite_math.py"),
        Path(__file__).with_name("prerequisite_fixtures.py"),
    ]
    paths += [ROOT / m["file"] for m in models]
    paths += [ROOT / "tools/ngspice/usr/bin/ngspice"]
    manifest = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    folder = (
        ROOT
        / "results/device_models"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_prerequisites_"
            + uuid.uuid4().hex[:8]
        )
    )
    folder.mkdir(parents=True, exist_ok=False)
    for name, sha in manifest.items():
        dest = folder / "source" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / name).read_bytes())
        if digest(dest) != sha:
            raise ValueError("Source changed during freezing")
    write_json(
        folder / "plan.json",
        dict(plan=plan, models=models, source_manifest=manifest, versions=environment_versions()),
    )
    exp = Suite(folder, plan)
    rows = {"oracles": oracles(exp)}
    for m in models:
        function = (
            jfet
            if m["device_id"] == "jfe150"
            else opa
            if m["device_id"].startswith("opa")
            else bipolar
        )
        try:
            rows[m["id"]] = function(exp, m)
        except (ValueError, RuntimeError, OSError) as exc:
            rows[m["id"]] = dict(status="error", reason=str(exc))
        write_json(folder / "checkpoint.json", dict(results=rows, jobs=exp.jobs, complete=False))
        print(m["id"], "recorded", flush=True)
    unchanged = all(digest(ROOT / name) == sha for name, sha in manifest.items())
    write_json(
        folder / "results.json",
        dict(
            experiment_id=folder.name,
            results=rows,
            jobs=exp.jobs,
            source_manifest=manifest,
            source_unchanged=unchanged,
            plan=plan,
            models=models,
            eligible=False,
            complete=True,
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
    return 2 if any(j["status"] == "error" for j in exp.jobs) or not unchanged else 0


if __name__ == "__main__":
    raise SystemExit(main())
