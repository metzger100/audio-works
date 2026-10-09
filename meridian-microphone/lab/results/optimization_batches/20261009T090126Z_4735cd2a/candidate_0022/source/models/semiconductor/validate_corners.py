#!/usr/bin/env python3
"""Freeze and test analytic coupled DC controls, including the failed parent."""
from pathlib import Path
import sys, json, subprocess, os, uuid, argparse
from datetime import datetime, timezone
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from meridian_lab.core import source_manifest, read_yaml, digest, parse_raw, write_json, environment_versions, verify_spec_lock

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--parent-experiment',action='append',default=[]);args=parser.parse_args()
    for parent in args.parent_experiment:
        p=ROOT/'results/device_models'/parent
        if Path(parent).name!=parent or not any((p/n).is_file() for n in ['results.json','failure.json']):
            raise ValueError('Parent experiment must resolve to a preserved device-model record')
    verify_spec_lock(); manifest=source_manifest()
    folder=ROOT/'results/device_models'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_corners_'+uuid.uuid4().hex[:8])
    folder.mkdir(parents=True)
    for name in manifest:
        p=folder/'source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
    library=folder/'source/models/semiconductor'; jobs=[]
    for label,metadata,model in [('r1','proposals/corners_r1.yaml','proposals/dc_bound_controls_r1.cir'),('r2','corners.yaml','dc_bound_controls.cir')]:
        controls=read_yaml(library/metadata)['coupled_dc_controls']
        directory=folder/label;directory.mkdir()
        body=f'* Independent native DC checks, {label}; no device qualification\n.include "{library/model}"\n.temp 25\n.options tnom=25 reltol=1e-8 abstol=1e-16 gmin=1e-15\n'
        for i,c in enumerate(controls):
            for tag,vg in [('zero',0),('2ma',c['vgs_at_2ma_v']),('100ua',c['vgs_at_100ua_v']),('100na',c['vto_v']*(1-np.sqrt(1e-7/c['idss_a'])))]:
                key=f'{i}_{tag}'
                body+=f'Vd{key} d{key} 0 10\nVg{key} g{key} 0 DC {vg:.16g} AC 1\nJq{key} d{key} g{key} 0 DC_BOUND_{i}\n'
        body+='\n.control\nset filetype=ascii\nset numdgt=16\nop\nwrite op.raw all\nac lin 1 1000 1000\nwrite ac.raw all\nquit\n.endc\n.end\n'
        (directory/'job.cir').write_text(body)
        env=os.environ.copy();env.pop('MERIDIAN_NGSPICE_BEHAVIOR',None)
        run=subprocess.run([str(ROOT/'tools/ngspice-run'),'-n','-b','job.cir'],cwd=directory,env=env,capture_output=True,text=True,timeout=15)
        (directory/'simulator.log').write_text(run.stdout+'\n'+run.stderr)
        if run.returncode:raise RuntimeError(run.stderr)
        op=parse_raw(directory/'op.raw');ac=parse_raw(directory/'ac.raw'); rows=[]
        for i,c in enumerate(controls):
            for tag,target in [('zero',c['idss_a']),('2ma',.002),('100ua',.0001),('100na',1e-7)]:
                actual=-float(op[f'i(vd{i}_{tag})'][0]);rows.append(dict(control_id=c['id'],metric=f'id_{tag}',value_a=actual,target_a=target,relative_error=actual/target-1,pass_physics=abs(actual/target-1)<1e-5))
            gm=float(abs(ac[f'i(vd{i}_zero)'][0]));cutoff=float(c['vto_v']*(1-np.sqrt(1e-7/c['idss_a'])))
            rows.append(dict(control_id=c['id'],metric='gfs',value_s=gm,target_s=c['gfs_s'],pass_physics=abs(gm/c['gfs_s']-1)<1e-5))
            rows.append(dict(control_id=c['id'],metric='vgs_at_100na',value_v=cutoff,guaranteed_range_v=[-1.5,-.9],pass_manufacturer_limit=-1.5<=cutoff<=-.9))
        job=dict(proposal=label,parent_proposal=None if label=='r1' else 'r1',netlist_sha256=digest(directory/'job.cir'),metadata_sha256=digest(library/metadata),model_sha256=digest(library/model),rows=rows,raw_hashes={n:digest(directory/n) for n in ['op.raw','ac.raw']},physics_agreement=all(r.get('pass_physics',True) for r in rows),guaranteed_subset_agreement=all(r.get('pass_manufacturer_limit',True) for r in rows),production_corner_qualified=False)
        write_json(directory/'results.json',job);jobs.append(job)
        np.savetxt(directory/'dc_currents.csv',np.array([[i,c['idss_a'],-float(op[f'i(vd{i}_zero)'][0]),abs(ac[f'i(vd{i}_zero)'][0])] for i,c in enumerate(controls)]),delimiter=',',header='control_index,expected_idss_a,simulated_idss_a,simulated_gfs_s',comments='')
    unchanged=source_manifest()==manifest
    write_json(folder/'results.json',dict(experiment_id=folder.name,timestamp_utc=datetime.now(timezone.utc).isoformat(),rng_seed=None,parent_experiments=args.parent_experiment,source_manifest=manifest,source_unchanged=unchanged,versions=environment_versions(),jobs=jobs,status='failed_parent_and_scoped_subset_preserved',eligible_for_production=False))
    print(json.dumps({'record':str(folder/'results.json'),'source_unchanged':unchanged,'r1_limit_agreement':jobs[0]['guaranteed_subset_agreement'],'r2_physics_agreement':jobs[1]['physics_agreement'],'r2_limit_agreement':jobs[1]['guaranteed_subset_agreement']},indent=2))
    return 0 if unchanged and all(j['physics_agreement'] for j in jobs) and not jobs[0]['guaranteed_subset_agreement'] and jobs[1]['guaranteed_subset_agreement'] else 2
if __name__=='__main__':raise SystemExit(main())
