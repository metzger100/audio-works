#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exact DMMT5401 package control, separate from discrete MMBT5401."""
from pathlib import Path
from datetime import datetime,timezone
import sys,uuid,hashlib,json
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'research')]
import parts_controls_002 as controls
from meridian_lab.core import read_yaml,verify_spec_lock,write_json,environment_versions
from meridian_lab.device_models import index

class PackageExperiment(controls.Experiment):
    def execute(self,model,label,circuit,commands,outputs,temp=25,refine=False):
        for nodes in ['c b 0','c b e']:
            circuit=circuit.replace(f'Xq {nodes} DMMT5401',f'Xq c b 0 0 0 {nodes.split()[-1]} DMMT5401')
        return super().execute(model,label,circuit,commands,outputs,temp,refine)

def manifest():
    m=controls.manifest()
    for r in ['research/parts_dual_pnp_control.py','research/parts_control_plan_005.yaml']:
        m[r]=hashlib.sha256((ROOT/r).read_bytes()).hexdigest()
    return m
def main():
    verify_spec_lock();plan=read_yaml(ROOT/'research/parts_control_plan_005.yaml');before=manifest()
    folder=ROOT/'results/device_models'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_dual_pnp_'+uuid.uuid4().hex[:8]);folder.mkdir(parents=True,exist_ok=False)
    for rel in before:
        p=folder/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/rel).read_bytes())
    available=index(folder/'source/models');exp=PackageExperiment(folder,available);m=available['dmmt5401_vendor']
    ref={**exp.refs['parts_expansion_002']['diodes_mmbt5401'],'source':'DS30437 Rev9-2 March2024 page2'}
    rows,values=controls.bipolar(exp,m,ref)
    c='Vc1 c1 0 -5\nVc2 c2 0 -5\nVb1 b1 0 -.67456\nVb2 b2 0 -.67456\nXq c1 b1 b2 c2 0 0 DMMT5401'
    out=exp.execute(m,'nominal_two_half_symmetry',c,'op\nwrite op.raw i(vc1) i(vc2) i(vb1) i(vb2)',['op.raw'])
    if out:
        d=out['op.raw'];values['two_half_nominal_currents_a']=[abs(float(d[k][0])) for k in ['i(vc1)','i(vc2)']]
        values['matching_scope']='Equal nominal halves are numerical symmetry only; no production mismatch, package thermal correlation or2percent validation.'
    unchanged=manifest()==before;errors=sum(j['status']=='error' for j in exp.jobs)
    results={m['id']:dict(comparisons=rows,measurements=values,failed_jobs=errors,status='error' if errors else 'disagreement' if any(r['status']=='fail' for r in rows) else 'scoped_record')}
    write_json(folder/'results.json',dict(schema_version=1,experiment_id=folder.name,timestamp_utc=datetime.now(timezone.utc).isoformat(),plan=plan,source_manifest=before,source_unchanged=unchanged,versions=environment_versions(),results=results,jobs=exp.jobs,eligible_for_production=False,candidate_evaluations=0,status='recorded_unqualified' if unchanged else 'source_integrity_error'))
    print(json.dumps(dict(record=str(folder/'results.json'),jobs=len(exp.jobs),errors=errors,source_unchanged=unchanged)))
    return 2 if errors or not unchanged or any(r['status']=='fail' for r in rows) else 0
if __name__=='__main__':raise SystemExit(main())
