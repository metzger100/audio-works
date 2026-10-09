#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Supply a known mathematical constant, preserving original Diotec models."""
from pathlib import Path
from datetime import datetime,timezone
import sys,uuid,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'research')]
import parts_controls_002 as controls
from meridian_lab.core import read_yaml,verify_spec_lock,write_json,environment_versions
from meridian_lab.device_models import index

class ConstantExperiment(controls.Experiment):
    def execute(self,model,label,circuit,commands,outputs,temp=25,refine=False):
        return super().execute(model,label,'.param pi=3.141592653589793238462643383279502884\n'+circuit,commands,outputs,temp,refine)

def manifest():
    result=controls.manifest()
    for rel in ['research/parts_constant_control.py','research/parts_control_plan_004.yaml']:
        result[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    return result

def main():
    verify_spec_lock();plan=read_yaml(ROOT/'research/parts_control_plan_004.yaml');before=manifest()
    folder=ROOT/'results/device_models'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_constant_'+uuid.uuid4().hex[:8]);folder.mkdir(parents=True,exist_ok=False)
    for rel in before:
        p=folder/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/rel).read_bytes())
    models=index(folder/'source/models');exp=ConstantExperiment(folder,models);results={}
    for mid in plan['models']:
        m=models[mid];ref=exp.refs['parts_expansion_002']['diotec_2n5551']
        rows,values=controls.bipolar(exp,m,ref)
        if m['device_id']=='diotec_mmbt5551':
            for r in rows:r['condition']=r['condition'].replace('2N5551 Version2025-01-17 page2','MMBT5551 Version2025-01-17 page2; matching numeric limits independently checked')
        errors=sum(j['status']=='error' for j in exp.jobs if j['model_id']==mid)
        results[mid]=dict(comparisons=rows,measurements=values,failed_jobs=errors,status='error' if errors else 'disagreement' if any(r['status']=='fail' for r in rows) else 'scoped_record')
        write_json(folder/'checkpoint.json',dict(results=results,jobs=exp.jobs,complete=False));print(mid,results[mid]['status'],flush=True)
    if len(exp.jobs)>plan['maximum_jobs']:raise RuntimeError('Finite budget exceeded')
    unchanged=manifest()==before
    write_json(folder/'results.json',dict(schema_version=1,experiment_id=folder.name,timestamp_utc=datetime.now(timezone.utc).isoformat(),plan=plan,source_manifest=before,source_unchanged=unchanged,versions=environment_versions(),results=results,jobs=exp.jobs,eligible_for_production=False,candidate_evaluations=0,parent_experiments=plan['parent_experiments'],status='recorded_unqualified' if unchanged else 'source_integrity_error'))
    print(json.dumps(dict(record=str(folder/'results.json'),jobs=len(exp.jobs),errors=sum(j['status']=='error' for j in exp.jobs),source_unchanged=unchanged)))
    return 2 if not unchanged or any(r['status'] in ['error','disagreement'] for r in results.values()) else 0
if __name__=='__main__':raise SystemExit(main())
