from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import uuid

from . import archive
from .core import ROOT, Simulator, digest, environment_versions, read_yaml, source_manifest, spec_digest, verify_spec_lock, write_json
from .qualification import evaluate
from .device_models import resolve


def implementation_manifest(folder):
    """Freeze the physical BOM and rationale with the DUT, excluding mutable results."""
    return {p.name: digest(p) for p in sorted(folder.iterdir())
            if p.is_file() and p.name != 'results.json'}


def run(candidate, seed=34047, samples=16, selected=None, overrides=None, hypothesis=None, parent_experiments=None, numerical_optimization=None):
    verify_spec_lock()
    meta=read_yaml(ROOT/'candidates'/candidate/'topology.yaml')
    now=datetime.now(timezone.utc)
    experiment_id=now.strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8]
    folder=ROOT/'results/runs'/experiment_id
    folder.mkdir(exist_ok=False)
    manifest=source_manifest()
    for relative in manifest:
        target=folder/'source'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/relative).read_bytes())
    suite_sha=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    sim=Simulator(candidate,folder,overrides)
    # Preserve candidate source and metadata before execution, including failing proposals.
    candidate_folder=ROOT/'candidates'/candidate
    implementation=implementation_manifest(candidate_folder)
    for name in implementation:
        (folder/name).write_bytes((candidate_folder/name).read_bytes())
    sim.model_root=folder/'source/models'
    sim.candidate=folder
    model_versions=resolve(sim.model_root,meta.get('semiconductor_models',[]))
    for path in (ROOT/'spec').glob('*.yaml'):
        (folder/path.name).write_bytes(path.read_bytes())
    checks=evaluate(sim,seed,samples,selected)
    required=read_yaml(ROOT/'spec/microphone_spec.yaml')['qualification']['required_tests']
    allpass=all(n in checks and checks[n]['status']=='pass' for n in required)
    evidence=set(read_yaml(ROOT/'spec/microphone_spec.yaml')['qualification']['evidence_required'])
    missing_evidence=sorted(evidence-set(meta.get('qualification_evidence',[])))
    eligible=allpass and not meta.get('ideal_devices',False) and meta.get('kind')=='research_candidate' and not missing_evidence
    status='qualified' if eligible else 'failed' if any(c['status'] in {'fail','error'} for c in checks.values()) else 'incomplete'
    failures={n:c['reason'] or 'Numerical acceptance requirement failed' for n,c in checks.items() if c['status']!='pass'}
    record={'schema_version':1,'experiment_id':experiment_id,'timestamp_utc':now.isoformat(),'backend':'ngspice',
            'candidate_id':candidate,'parent_candidates':meta.get('parents',[]),'parent_experiments':parent_experiments or [],
            'hypothesis':hypothesis or meta['hypothesis'],'structural_changes':meta.get('structural_changes'),
            'numerical_optimization':numerical_optimization or {'performed':False},'simulation_configuration':sim.params,
            'rng_seed':seed,'scenario_samples':samples,'spec_sha256':spec_digest(),'suite_sha256':suite_sha,
            'source_manifest':manifest,'versions':environment_versions(),'topology':meta,'checks':checks,
            'status':status,'eligible':eligible,'missing_qualification_evidence':missing_evidence,
            'failure_reasons':failures,'jobs':sim.jobs,'comparison_with_parent':None,
            'useful_discovery':None,'next_potential_experiment':'Resolve failed checks and missing evidence without changing acceptance thresholds.',
            'result_file':str((folder/'results.json').relative_to(ROOT))}
    record['solver_configuration']={'method':'gear','maxord':2,'reltol':1e-6,'abstol_a':1e-15,'vntol_v':1e-9,'gmin_s':1e-15,'rshunt':None,
                                    'note':'Timestep-refinement regressions required; integration method is not a stability proof.'}
    if source_manifest()!=manifest or implementation_manifest(candidate_folder)!=implementation:
        record['status']='error'; record['eligible']=False
        record['failure_reasons']['source_integrity']='Research or implementation sources changed during evaluation. Rerun from a stable source snapshot.'
        status='error'; eligible=False
    record['provenance']={'timestamp':now.isoformat(),'instrument_or_simulator':record['versions']['ngspice'],
                          'configuration':sim.params,'raw_data_hashes':{job['folder']:job.get('files',{}) for job in sim.jobs},
                          'candidate_circuit_sha256':digest(folder/'circuit.cir'),'source_snapshot':'source/',
                          'semiconductor_models':model_versions}
    record['implementation_manifest']=implementation
    if parent_experiments:
        parents=[]
        for id_ in parent_experiments:
            parent=json.loads((ROOT/'results/runs'/id_/'results.json').read_text())
            delta={}
            for check in checks:
                pm=parent['checks'].get(check,{}).get('metrics',{})
                delta[check]={k:v-pm[k] for k,v in checks[check]['metrics'].items() if isinstance(v,(float,int)) and not isinstance(v,bool) and isinstance(pm.get(k),(float,int)) and not isinstance(pm[k],bool)}
            parents.append({'experiment_id':id_,'metric_deltas':delta,'same_spec':parent['spec_sha256']==record['spec_sha256'],
                            'same_suite':parent['suite_sha256']==record['suite_sha256'],
                            'note':'Interpret deltas as a controlled value comparison only when specification and suite match.'})
        record['comparison_with_parent']=parents
    write_json(folder/'results.json',record)
    write_json(ROOT/'candidates'/candidate/'results.json',{'latest_experiment':experiment_id,'result_file':record['result_file'],'eligible':eligible,'status':status})
    archive.update(record)
    with (ROOT/'research/experiment_log.md').open('a') as log:
        log.write(f'\n## {experiment_id} — {candidate}\n\nHypothesis: {record["hypothesis"]}\n\nResult: **{status}**, qualified: {eligible}. Seed: {seed}. [Full record](../{record["result_file"]}). Parent experiments: {parent_experiments or []}. Optimization: {record["numerical_optimization"]}.\n\nFailures/incomplete: {json.dumps(failures)}\n\nNext: {record["next_potential_experiment"]}\n')
    print(json.dumps({'experiment_id':experiment_id,'status':status,'eligible':eligible,'checks':{n:c['status'] for n,c in checks.items()},'result_file':record['result_file']},indent=2))
    return record


def main():
    parser=argparse.ArgumentParser(description='M100 Meridian evidence-first research')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor')
    sub.add_parser('verify')
    test=sub.add_parser('evaluate')
    test.add_argument('candidate'); test.add_argument('--samples',type=int,default=16); test.add_argument('--seed',type=int,default=34047)
    test.add_argument('--checks',nargs='+'); test.add_argument('--parameters',type=Path)
    test.add_argument('--parent-experiment',action='append')
    args=parser.parse_args()
    if args.command=='doctor':
        verify_spec_lock()
        print(json.dumps({'root':str(ROOT),'spec_sha256':spec_digest(),'versions':environment_versions()},indent=2))
    elif args.command=='verify':
        import pytest
        now=datetime.now(timezone.utc)
        folder=ROOT/'results/verification'/(now.strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8])
        folder.mkdir(parents=True,exist_ok=False)
        manifest=source_manifest()
        for relative in manifest:
            target=folder/'source'/relative; target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/relative).read_bytes())
        code=pytest.main([str(ROOT/'tests'),'-q','--basetemp',str(folder/'raw_tests'),'--junitxml',str(folder/'junit.xml')])
        write_json(folder/'verification.json',{'schema_version':1,'timestamp_utc':now.isoformat(),'exit_code':code,
                   'status':'pass' if code==0 else 'fail','source_manifest':manifest,'source_unchanged':source_manifest()==manifest,
                   'spec_sha256':spec_digest(),'versions':environment_versions(),'raw_data_hashes':{str(p.relative_to(folder)):digest(p) for p in (folder/'raw_tests').rglob('*.raw')}})
        raise SystemExit(code)
    else:
        if args.samples<1 or args.samples>100000:
            parser.error('samples must be 1..100000')
        params=json.loads(args.parameters.read_text()) if args.parameters else None
        record=run(args.candidate,args.seed,args.samples,args.checks,params,parent_experiments=args.parent_experiment)
        # An incomplete or failed engineering result is never a successful qualification.
        raise SystemExit(0 if record['eligible'] else 2)


if __name__=='__main__':
    main()
