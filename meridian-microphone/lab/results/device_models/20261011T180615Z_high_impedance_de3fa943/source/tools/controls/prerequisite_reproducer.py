# SPDX-License-Identifier: GPL-3.0-or-later
"""Minimal complete-model high-impedance controls at an observed DUT bias."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import uuid

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"src"),str(Path(__file__).resolve().parent)]
from meridian_lab.core import digest, read_yaml, write_json, verify_spec_lock, environment_versions
from meridian_lab.device_models import resolve
from simulation_prerequisites import Suite

PLAN="research/devices/simulation-prerequisites-plan-003.yaml"


def main():
    verify_spec_lock(); plan=read_yaml(ROOT/PLAN)
    model=resolve(ROOT/"models",[plan["model"]])[0]
    folder=ROOT/"results/device_models"/(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_high_impedance_"+uuid.uuid4().hex[:8])
    folder.mkdir(parents=True,exist_ok=False)
    names=[PLAN,"tools/ngspice-run","tools/ngspice/usr/bin/ngspice","models/"+model["path"]]
    for prefix in ["src","spec","tools/controls","models/semiconductor"]:
        names += [str(p.relative_to(ROOT)) for p in (ROOT/prefix).rglob("*") if p.is_file() and p.suffix in {".py",".yaml"}]
    manifest={name:digest(ROOT/name) for name in sorted(set(names))}
    for name,sha in manifest.items():
        p=folder/"source"/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
        if digest(p)!=sha:raise ValueError("Changing freeze input")
    m={**model,"file":"models/"+model["path"]};m.pop("resolved_path")
    jobs=[]
    for resistance in plan["source_resistance_ohm"]:
        for mode in plan["excitations"]:
            wave="SIN(3.3889452055659 .01 1000)" if mode=="voltage" else ""
            link="Vlink bias g 0" if resistance==0 else f"Rbias bias g {resistance}"
            phase=90 if mode.endswith("90") else 0
            c=(f"Vrail rail 0 13.5557796144973\nVbias bias 0 DC 3.3889452055659 {wave}\n{link}\n"
               "Vback back 0 29.5293276326911\nRleak back g 1T\nCgate g back 70p\nRsource s 0 3300\nXq rail g s rail 0 JFE150\n")
            if mode!="voltage":c+=f"Ip 0 g SIN(0 8.29380490383245n 1000 0 0 {phase})"
            jobs.append(dict(label=f"source_{resistance}_{mode}",circuit=c))
    write_json(folder/"plan.json",dict(plan=plan,model=m,jobs=jobs,source_manifest=manifest,versions=environment_versions()))
    exp=Suite(folder,plan)
    for j in jobs:
        exp.execute(m,j["label"],j["circuit"],"op\nwrite op.raw all\ntran 2u .004 0 2u\nwrite tran.raw all",["op.raw","tran.raw"])
        print(j["label"],exp.jobs[-1]["status"],flush=True)
    unchanged=all(digest(ROOT/name)==sha for name,sha in manifest.items())
    write_json(folder/"results.json",dict(plan=plan,jobs=exp.jobs,source_manifest=manifest,source_unchanged=unchanged,
                                         nonlinear_credit=False,complete=True,eligible=False))
    (folder/"batch.sha256").write_text("".join(f"{digest(p)}  {p.relative_to(ROOT)}\n" for p in sorted(folder.rglob("*")) if p.is_file()))
    print(folder.relative_to(ROOT))
    return 2 if any(j["status"]=="error" for j in exp.jobs) or not unchanged else 0


if __name__=="__main__":raise SystemExit(main())
