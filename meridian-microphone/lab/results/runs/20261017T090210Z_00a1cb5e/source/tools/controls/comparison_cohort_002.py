# SPDX-License-Identifier: GPL-3.0-or-later
"""Execute the predeclared common cohort once; no optimization or source repairs."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import uuid

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tools/controls"), str(ROOT / "tools/reporting")]
from meridian_lab.core import read_yaml, write_json, digest, source_manifest, environment_versions
from meridian_lab.core import verify_spec_lock
from meridian_lab.cli import run, implementation_manifest
from meridian_lab.bounded import owned_parts
from meridian_lab import qualification as q
from meridian_lab.metrics import at_frequency, device_noise_totals, integrate_asd
from meridian_lab.robust_scenarios import thermal_passive_scenarios
from focused_hypotheses import frozen_sim, paired_scenarios
from comparison_common import verify_partition, require_common

PLAN = "research/architectures/architecture-comparison-002.yaml"


def cell(candidate, out, scenario, holdout=False, density=64):
    s = deepcopy(scenario)
    s["parameters"] = s.pop("parameters_by_candidate", {}).get(candidate, s.get("parameters", {}))
    directory = out / "matched" / candidate / s["id"]
    sim = frozen_sim(candidate, directory, out, s)
    row = dict(candidate=candidate, scenario=s["id"], holdout=holdout,
               declared=s, status="error", jobs=sim.jobs, density=density)
    try:
        raw = sim.execute("matched", f"op\nwrite op.raw all\nac dec {density} 1 10Meg\nwrite ac.raw all",
                          ["op.raw", "ac.raw"])
        ctx = {"nominal": raw, "checks": {}}
        op, fr = q.operating_point(sim, ctx), q.frequency_response(sim, ctx)
        row.update(status="pass" if op["status"] == fr["status"] == "pass" else "fail",
                   dc=op, ac=fr, current_a=op["metrics"]["current_a"],
                   response_deviation_db=fr["metrics"]["response_deviation_db"])
        n = sim.execute("noise", f"noise v(pp,pn) VP dec {2*density} 20 20k 1\nsetplot noise1\nwrite noise.raw all",
                        ["noise.raw"])["noise.raw"]
        f = n["frequency"].real
        gain = np.array([abs(at_frequency(raw["ac.raw"]["frequency"], raw["ac.raw"].voltage("pp", "pn"), x)) for x in f])
        roots = device_noise_totals(n)
        groups, spectra, closure = verify_partition(f, roots, n["onoise_spectrum"].real)
        electronics = np.sqrt(sum((v*v for k,v in spectra.items() if not k.endswith("(excluded)")), np.zeros_like(f)))
        row.update(noise_pa_rms=integrate_asd(f, electronics/gain),
                   noise_a_pa_rms=integrate_asd(f, electronics/gain, True),
                   noise_partition_closure=closure,
                   contributions={k:dict(roots=groups[k], output_v_rms=integrate_asd(f,v),
                       pressure_pa_rms=integrate_asd(f,v/gain), pressure_a_pa_rms=integrate_asd(f,v/gain,True))
                       for k,v in spectra.items()},
                   noise_scope="conditional stationary modeled sources; incomplete physical spectra")
        # Terminal current from the actual zero-volt gate observer; input admittance
        # is conditional on this driven capsule boundary, not an independent two-port.
        if any(x.startswith("jfe150") for x in sim.meta["semiconductor_models"]):
            ac = raw["ac.raw"]
            i = ac["i(v.xdut.vjinput_1)"]
            v = ac.voltage("f", "mic_g")
            reference = ac.voltage("xdut.gatebias", "mic_g")
            y = i/v + (v-reference)/v*(1/sim.params["RBIAS_VALUE"] + 2j*np.pi*ac["frequency"].real*sim.params["CBIASSTRAY_VALUE"])
            yy = at_frequency(ac["frequency"], y, 1000)
            row["input_diagnostic_1khz"] = dict(real_s=float(yy.real), imag_s=float(yy.imag),
                equivalent_capacitance_f=float(yy.imag/(2*np.pi*1000)),
                boundary="observed semiconductor plus actual moving Rbias/Cbiasstray return; driven capsule boundary; not independent port")
    except Exception as exc:
        row.update(status="error", reason=f"{type(exc).__name__}: {exc}")
    write_json(directory / "result.json", row)
    print(candidate, s["id"], row["status"], flush=True)
    return row


def main():
    verify_spec_lock()
    plan = read_yaml(ROOT / PLAN)
    if (ROOT / "results/reports/architecture_comparison_002/cohort.json").exists():
        raise ValueError("Cohort already registered; reproduce report without reevaluation")
    candidates = list(plan["representatives"])
    out = ROOT / "results/mechanism_controls" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_comparison002_" + uuid.uuid4().hex[:8])
    out.mkdir(parents=True, exist_ok=False)
    manifest = source_manifest()
    # Include transitive structured records and shared binary/modules missing from
    # older source_manifest versions, without mutating the laboratory evaluator.
    extras = [ROOT / p for p in plan["documentary_inputs"]]
    extras += [ROOT / PLAN, ROOT / "tools/ngspice/usr/bin/ngspice"]
    extras += sorted((ROOT / "tools/ngspice/usr/lib/ngspice").glob("*.cm"))
    for path in extras:
        paths = [path, *(owned_parts(path) if path.suffix in {".yaml", ".json"} else [])]
        for p in paths:
            manifest[str(p.relative_to(ROOT))] = digest(p)
    for name, sha in manifest.items():
        p = out / "source" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ROOT / name).read_bytes())
        if digest(p) != sha:
            raise ValueError("Source changed during freeze")
    implementations = {c:implementation_manifest(ROOT / "candidates" / c) for c in candidates}
    for c, m in implementations.items():
        for name in m:
            p = out / "implementations" / c / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes((ROOT / "candidates" / c / name).read_bytes())
    holdouts = paired_scenarios(plan, candidates)
    write_json(out / "plan.json", dict(plan=plan, matched_holdouts=holdouts, versions=environment_versions()))
    write_json(out / "manifest.json", dict(sources=manifest, implementations=implementations))
    report = ROOT / "results/reports/architecture_comparison_002"
    write_json(report / "cohort.json", dict(batch=str(out.relative_to(ROOT)), complete=False))
    full = {}
    # Complete ordinary suite attempted also for held CMOS and periodic controls;
    # prerequisite failures retain every required check as error/incomplete.
    for c in candidates:
        r = run(c, seed=plan["seed"], samples=plan["full_suite_samples"],
                hypothesis="Prompt13 frozen common cohort; exact existing BOM; no design selection",
                parent_experiments=plan["representatives"][c]["parent_experiments"])
        full[c] = r["experiment_id"]
        write_json(out / "full-suite-index.json", full)
    records = [read_yaml(ROOT / "results/runs" / e / "results.json") for e in full.values()]
    require_common(records)
    rows = []
    for c in plan["matched_realized"]:
        for s in plan["scenarios"]:
            rows.append(cell(c, out, s))
        for s in holdouts:
            rows.append(cell(c, out, s, True))
        meta = read_yaml(out / "implementations" / c / "topology.yaml")
        bom = read_yaml(out / "implementations" / c / "bom.yaml")
        for s in thermal_passive_scenarios(meta, bom):
            # Opposed actual output cap endpoints; new film actual endpoints.
            sign = 0 if s["id"].endswith("-1") else 1
            for k,d in meta["population"].items():
                if k.startswith("COUT"):
                    s["parameters"][k] = d["range"][sign if k.startswith("COUTP") else 1-sign]
                if k in {"CBACKFILTER_VALUE", "RCBACKFILTERLOSS_VALUE", "RCBACKFILTERINSULATION_VALUE", "LBACKFILTER_VALUE"}:
                    s["parameters"][k] = d["range"][sign]
            rows.append(cell(c, out, s))
        if any(m.startswith("jfe150") for m in meta["semiconductor_models"]):
            for model in ["jfe150_weak", "jfe150_strong"]:
                rows.append(cell(c,out,dict(id=model,model_replacement=model,parameters={},
                    kind="complete coupled vendor stress; known validation failures; not production")))
        rows.append(cell(c,out,dict(id="nominal_refinement",parameters={}),density=128))
    unchanged = all(digest(ROOT / n)==sha for n,sha in manifest.items()) and all(
        implementation_manifest(ROOT / "candidates" / c)==m for c,m in implementations.items())
    result = dict(batch=str(out.relative_to(ROOT)), full_suite=full, rows=rows,
                  source_unchanged=unchanged, complete=True, eligible=False,
                  production_front=[], physical_front=[], optimizer_evaluations=0)
    write_json(out / "results.json", result)
    write_json(report / "cohort.json", dict(batch=str(out.relative_to(ROOT)), complete=True,
        results_sha256=digest(out/"results.json"), source_unchanged=unchanged))
    print(json.dumps(dict(batch=str(out.relative_to(ROOT)), cells=len(rows), unchanged=unchanged)))


if __name__ == "__main__":
    main()
