# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit observer children and common-cohort reduced original DUT reproductions."""
from datetime import datetime, timezone
from pathlib import Path
import difflib
import json
import re
import sys
import uuid

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"src"),str(Path(__file__).resolve().parent)]
from meridian_lab.core import Simulator, digest, read_yaml, write_json, verify_spec_lock, environment_versions
from meridian_lab.device_models import resolve
from meridian_lab.nonlinear import settled_spectrum
from meridian_lab.metrics import harmonic_spectrum
from simulation_prerequisites import Suite

PLAN="research/devices/simulation-prerequisites-plan-002.yaml"


def collapse_observers(text):
    """Merge only explicitly ideal zero-volt measurement sources in a DUT scope."""
    mapping={}; lines=[]
    for line in text.splitlines():
        tokens=line.split()
        if len(tokens)==4 and re.fullmatch(r"V[QJ]\w+_\d+",tokens[0],re.I) and tokens[3]=="0":
            mapping[tokens[2]]=tokens[1]
        else:
            lines.append(line)
    if not mapping: raise ValueError("No explicit terminal observers to collapse")
    return "\n".join(" ".join(mapping.get(token,token) for token in line.split()) if not line.lstrip().startswith("*") else line for line in lines)+"\n"


def main():
    verify_spec_lock(); plan=read_yaml(ROOT/PLAN)
    folder=ROOT/"results/device_models"/(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_observer_diagnosis_"+uuid.uuid4().hex[:8])
    folder.mkdir(parents=True,exist_ok=False)
    names=[PLAN,"tools/ngspice-run","tools/ngspice/usr/bin/ngspice"]
    for prefix in ["src","spec","models/capsule","models/environment","tools/controls","models/semiconductor"]:
        names += [str(p.relative_to(ROOT)) for p in (ROOT/prefix).rglob("*") if p.is_file() and p.suffix in {".py",".cir",".yaml"}]
    models=resolve(ROOT/"models",["jfe150_generic","jfe150_pspice","bc846b_emitter_r1","opa197_pspice"])
    names += ["models/"+m["path"] for m in models]
    for candidate in plan["candidate_ids"]:
        names += [str(p.relative_to(ROOT)) for p in (ROOT/"candidates"/candidate).rglob("*") if p.is_file() and p.suffix in {".cir",".yaml"}]
    manifest={name:digest(ROOT/name) for name in sorted(set(names))}
    for name,sha in manifest.items():
        p=folder/"source"/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
        if digest(p)!=sha: raise ValueError("Changing freeze input")
    source=folder/"source"
    parent=(source/"models/capsule/flat-k47.cir").read_text()
    child=(source/"models/capsule/flat-k47-observer-r2.cir").read_text()
    (folder/"observer.diff").write_text("".join(difflib.unified_diff(parent.splitlines(True),child.splitlines(True),fromfile="flat-k47.cir",tofile="flat-k47-observer-r2.cir")))
    jobs=[]
    for version in ["flat-k47.cir","flat-k47-observer-r2.cir"]:
        for translation in [0,20]:
            for step in [2e-6,1e-6]:
                c=(f'.include "{source / "models/capsule" / version}"\n'
                   f"Vg g 0 {translation}\nVp pressure 0 SIN(0 1 1000)\nVpr pr 0 0\nVbias b g 40\n"
                   "Rload f g 1G\nRrear rear g 1k\nXcap f b rear pressure pr g FLAT_K47 LIN=1 POLDC=40 CROSS=0")
                jobs.append(dict(model=dict(id="charge_oracle"),label=f"{version}_{translation}_{step}",circuit=c,
                                 commands=f"tran {step} .064 0 {step}\nwrite tran.raw all",outputs=["tran.raw"],kind="charge",translation=translation))
    for model in models[:2]:
        c=(f'.include "{source / "models" / model["path"]}"\n'
           "Vin in 0 PWL(0 -1 .001 -1 .005 1 .009 -1 .010 -1)\nRg in g 100k\nVd d 0 0\nVs s 0 0\nVh h 0 0\nVl l 0 0\nXq d g s h l JFE150")
        jobs.append(dict(model=dict(id=model["id"],ngspice_behavior="ps"),label="clamp_ramp",circuit=c,
                         commands="tran 1u .010 0 1u\nwrite tran.raw all",outputs=["tran.raw"],kind="clamp"))
    # Prepare complete plans before the first simulator call. Candidate topologies/BOMs
    # are preserved; each altered numerical deck is an explicit named child.
    for cid in plan["candidate_ids"]:
        sim=Simulator(cid,folder/"unused")
        circuit=(source/"candidates"/cid/"circuit.cir").read_text()
        defs="\n".join(f".param {k}={v:.16g}" for k,v in sim.params.items() if k!="TEMP")
        defs += "\n.param LIN=1\n.param POLDC=40\n.param PRESSURE_PEAK=1.414213562373095\n.param FREQ=1000"
        # Remove duplicated definitions by setting values before rendering instead.
        params={**sim.params,"LIN":1,"POLDC":40,"PRESSURE_PEAK":np.sqrt(2),"FREQ":1000}
        defs="\n".join(f".param {k}={v:.16g}" for k,v in params.items() if k!="TEMP")
        for version in plan["candidate_controls"]:
            cap="flat-k47-observer-r2.cir" if version=="charge_observer_reference_child" else "flat-k47.cir"
            dut=collapse_observers(circuit) if version=="terminal_observers_collapsed" else circuit
            (folder/(cid+"_"+version+".diff")).write_text("".join(difflib.unified_diff(circuit.splitlines(True),dut.splitlines(True),fromfile=cid+"/parent",tofile=cid+"/"+version)))
            includes="\n".join(f'.include "{source / "models" / m["path"]}"' for m in models if m["id"] in sim.meta["semiconductor_models"])
            c=(defs+"\n"+includes+f'\n.include "{source/"models/capsule"/cap}"\n.include "{source/"models/environment/p48.cir"}"\n'
               "VP pressure 0 DC 0 AC {PRESSURE_AC} SIN(0 {PRESSURE_PEAK} {FREQ})\nVPR pressure_r 0 DC 0 AC 0\n"
               "Xenv p n mic_g pp pn cm P48 VS={VS} FT={FT} FM={FM} LEN={LEN} RW={RW} RS={RS} CD={CD} CS={CS} ZIN={ZIN} ZM={ZM} CC={CC} CP={CP} START={START} CMAC={CMAC}\n"
               "Xcap f b rear pressure pressure_r mic_g FLAT_K47 CF={CF} CR={CR} SREF={SREF} VREF={VREF} LEAK={LEAK} PAR={PAR} CROSS={CROSS} LIN={LIN} POLDC={POLDC}\n"
               +dut+"\nXdut f b rear p n mic_g rail DUT")
            jobs.append(dict(model=dict(id=cid,ngspice_behavior="ps",semiconductor_ids=sim.meta["semiconductor_models"]),
                             label=version,circuit=c,commands="op\nwrite op.raw all\ntran 2u .004 0 2u\nwrite tran.raw all",
                             outputs=["op.raw","tran.raw"],kind="dut",capsule_file=cap,parameters=params))
    write_json(folder/"plan.json",dict(plan=plan,source_manifest=manifest,jobs=jobs,versions=environment_versions()))
    exp=Suite(folder,plan); rows=[]
    for job in jobs:
        old=exp.plan
        if job["kind"]=="dut":
            exp.plan={**plan,"options":plan["candidate_options"],"timeout_s_per_job":plan["candidate_timeout_s"]}
        data=exp.execute(job["model"],job["label"],job["circuit"],job["commands"],job["outputs"])
        exp.plan=old
        row=dict(model=job["model"]["id"],label=job["label"],kind=job["kind"],status="error" if data is None else "diagnostic_only")
        if data:
            d=data["tran.raw"]
            if job["kind"]=="charge":
                try:
                    h=settled_spectrum(d["time"],d.voltage("f","g"),1000,.032)
                    expected=70e-12*.02/60*40*(2*np.pi*1000)/abs(1/1e9+1/1e12+2j*np.pi*1000*72e-12)/np.sqrt(2)
                    row.update(harmonics=h,expected_rms_v=expected,relative_error=h["harmonics_v_rms"][0]/expected-1)
                except ValueError as exc: row.update(status="unsettled",reason=str(exc))
            elif job["kind"]=="clamp":
                row.update(gate_min_v=float(min(d["v(g)"])),gate_max_v=float(max(d["v(g)"])),
                           peak_source_current_a=float(max(abs(d["i(vin)"]))))
            else:
                row.update(saved_time_s=[float(d["time"][0]),float(d["time"][-1])],
                           nonlinear_credit=False,reason="4ms diagnostic cannot establish post-0.5s settling or headroom")
        rows.append(row)
        write_json(folder/"checkpoint.json",dict(rows=rows,jobs=exp.jobs,complete=False))
        print(job["model"]["id"],job["label"],row["status"],flush=True)
    unchanged=all(digest(ROOT/name)==sha for name,sha in manifest.items())
    write_json(folder/"results.json",dict(rows=rows,jobs=exp.jobs,source_manifest=manifest,source_unchanged=unchanged,
                                         plan=plan,complete=True,eligible=False))
    (folder/"batch.sha256").write_text("".join(f"{digest(p)}  {p.relative_to(ROOT)}\n" for p in sorted(folder.rglob("*")) if p.is_file()))
    print(json.dumps(dict(folder=str(folder.relative_to(ROOT)),source_unchanged=unchanged,jobs=len(exp.jobs),errors=sum(j["status"]=="error" for j in exp.jobs))))
    return 2 if any(j["status"]=="error" for j in exp.jobs) or not unchanged else 0


if __name__=="__main__":
    raise SystemExit(main())
