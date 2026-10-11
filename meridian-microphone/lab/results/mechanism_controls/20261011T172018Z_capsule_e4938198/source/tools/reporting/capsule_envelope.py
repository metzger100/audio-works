# SPDX-License-Identifier: GPL-3.0-or-later
"""Run a new finite, frozen capsule cohort. Never edit candidates or originals.

From lab: .venv/bin/python tools/reporting/capsule_envelope.py
Every invocation creates a new batch. Original private source bytes are required.
"""
from datetime import datetime, timezone
import csv
import json
from pathlib import Path
import shutil
import sys
import uuid

import numpy as np

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(LAB/'src'))
from meridian_lab.core import (Simulator, digest, environment_versions, read_yaml,
                               source_manifest, spec_digest, verify_spec_lock)
from meridian_lab.cli import implementation_manifest
from meridian_lab import qualification as q
from meridian_lab.metrics import at_frequency, device_noise_totals, integrate_asd
from capsule_envelope_math import calculate, plots


def dump(path, value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def originals():
    records=[]
    for index in [1,2]:
        rows=json.loads((LAB/f'research/capsules/retrieval-001-part-{index}.json').read_text())
        for row in rows:
            if row.get('private_file'):
                p=LAB.parents[1]/row['private_root']/row['private_file']
                if not p.exists() or digest(p)!=row['sha256']:
                    raise ValueError('Missing/changed original source '+row['id'])
            records.append({'id':row['id'],'status':row['status'],'sha256':row.get('sha256')})
    return records


def run():
    verify_spec_lock()
    plan=read_yaml(LAB/'research/capsules/scenarios-001.yaml')
    evidence=originals()
    batch=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_capsule_'+uuid.uuid4().hex[:8]
    out=LAB/'results/mechanism_controls'/batch
    out.mkdir(parents=True,exist_ok=False)
    sources=source_manifest()
    # Freeze JSON ledgers/query provenance too, outside the shared manifest extension list.
    for p in (LAB/'research/capsules').glob('*.json'):
        sources[str(p.relative_to(LAB))]=digest(p)
    candidates={c:implementation_manifest(LAB/'candidates'/c) for c in plan['candidates']}
    for relative in sources:
        target=out/'source'/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(LAB/relative,target)
    for candidate,manifest in candidates.items():
        for relative in manifest:
            target=out/'implementations'/candidate/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(LAB/'candidates'/candidate/relative,target)
    dump(out/'plan.json',plan)
    dump(out/'manifest.json',{'sources':sources,'candidates':candidates,'original_sources':evidence,
                             'spec_sha256':spec_digest(),'versions':environment_versions()})
    calculate(out)  # Independent unit/derivative/quadrature controls first.
    rows=[]
    for candidate in plan['candidates']:
        for scenario in plan['scenarios']:
            directory=out/candidate/scenario['id']
            sim=Simulator(candidate,directory,scenario['parameters'])
            sim.candidate=out/'implementations'/candidate
            sim.meta=read_yaml(sim.candidate/'topology.yaml')
            sim.model_root=out/'source/models'
            row={'candidate':candidate,'scenario':scenario['id'],'state':scenario['state'],
                 'status':'error','qualification':'unqualified','parameters':sim.params,'jobs':sim.jobs}
            try:
                raw=sim.op_ac('capsule_scenario')
                ctx={'nominal':raw,'checks':{}}
                op=q.operating_point(sim,ctx)
                fr=q.frequency_response(sim,ctx)
                row.update(current_A=op['metrics']['current_a'],
                           polarization_V=op['metrics']['polarization_dc_v'],
                           dc_status=op['status'],response_status=fr['status'],
                           response_deviation_db=fr['metrics']['response_deviation_db'],
                           sensitivity_V_per_Pa=fr['metrics']['sensitivity_v_per_pa_at_1khz'],
                           lf_db=fr['metrics']['lf_db'],hf_db=fr['metrics']['hf_db'])
                row['status']='pass' if op['status']==fr['status']=='pass' else 'fail'
                if candidate!='candidate_0012':
                    n=q.noise(sim,ctx)
                    row.update(noise_screen_status=n['status'],noise_qualification='incomplete spectra/mechanics',
                               noise_pa_rms_conditional=n['metrics']['electronics_noise_pa_rms'],
                               noise_output_V_rms=n['metrics']['electronics_output_v_rms'],
                               noise_power_closure=n['metrics']['noise_power_closure_relative_error'])
            except Exception as exc:
                row.update(status='error',error=f'{type(exc).__name__}: {exc}')
            dump(directory/'result.json',row)
            rows.append(row)
            print(candidate,scenario['id'],row['status'],row.get('response_deviation_db'),flush=True)
    assert len(rows)==plan['budget']['scenario_sets']
    # Numerical refinement is a distinct nominal subset, not added uncertainty coverage.
    refinements=[]
    for candidate in plan['candidates'][:3]:
        sim=Simulator(candidate,out/'refinement'/candidate)
        sim.candidate=out/'implementations'/candidate;sim.model_root=out/'source/models'
        base=next(r for r in rows if r['candidate']==candidate and r['scenario']=='baseline')
        record={'candidate':candidate,'status':'error','jobs':sim.jobs}
        try:
            ac=sim.execute('refined_ac','op\nwrite op.raw all\nac dec 64 1 10Meg\nwrite ac.raw all',['op.raw','ac.raw'])
            fr=q.response(ac['ac.raw'])
            noise=sim.execute('refined_noise','noise v(pp,pn) VP dec 128 20 20k 1\nsetplot noise1\nwrite noise.raw all',['noise.raw'])['noise.raw']
            f=noise['frequency'].real
            terms=device_noise_totals(noise)
            internal=np.sqrt(sum((v*v for k,v in terms.items() if '.xdut.' in k),np.zeros_like(f)))
            gain=np.array([abs(at_frequency(ac['ac.raw']['frequency'],ac['ac.raw'].voltage('pp','pn'),x)) for x in f])
            value=integrate_asd(f,internal/gain)
            record.update(response_delta_db=fr['response_deviation_db']-base['response_deviation_db'],
                          noise_relative_delta=value/base['noise_pa_rms_conditional']-1,
                          status='pass' if abs(fr['response_deviation_db']-base['response_deviation_db'])<.01 and abs(value/base['noise_pa_rms_conditional']-1)<.001 else 'fail')
        except Exception as exc:record['error']=str(exc)
        refinements.append(record)
    dump(out/'refinement.json',refinements)
    fields=['candidate','scenario','state','status','dc_status','response_status','current_A','polarization_V',
            'sensitivity_V_per_Pa','response_deviation_db','lf_db','hf_db','noise_screen_status',
            'noise_pa_rms_conditional','noise_output_V_rms','noise_power_closure','error']
    with (out/'scenarios.csv').open('w') as stream:
        w=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    plots(out,rows)
    unchanged=all(digest(LAB/path)==sha for path,sha in sources.items()) and all(
        implementation_manifest(LAB/'candidates'/c)==m for c,m in candidates.items())
    frozen=all(digest(out/'source'/path)==sha for path,sha in sources.items())
    dump(out/'integrity.json',{'source_unchanged':unchanged,'frozen_source_matches':frozen,
                             'original_sources_reverified':originals()==evidence,'rows':len(rows),
                             'errors':sum(r['status']=='error' for r in rows),'eligible':False})
    # Separate inventory retains all raw/job/failure/source bytes, paths lab-relative.
    files=sorted(p for p in out.rglob('*') if p.is_file())
    (out/'batch.sha256').write_text(''.join(f'{digest(p)}  {p.relative_to(LAB)}\n' for p in files))
    print(json.dumps({'batch':str(out.relative_to(LAB)),'source_unchanged':unchanged,'eligible':False}))
    if not unchanged or not frozen:raise RuntimeError('Changed sources; preserve failed batch')


if __name__=='__main__':run()
