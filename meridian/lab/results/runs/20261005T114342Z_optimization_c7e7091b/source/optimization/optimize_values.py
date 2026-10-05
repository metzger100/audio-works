"""Constrained numerical optimization; proposal values never edit a candidate or spec."""
import argparse
from datetime import datetime, timezone
import json
import sys
from pathlib import Path
import uuid

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from scipy.optimize import differential_evolution, NonlinearConstraint
import numpy as np
from meridian_lab.core import ROOT, Simulator, read_yaml, verify_spec_lock, write_json, source_manifest, spec_digest, environment_versions
from meridian_lab.qualification import operating_point, frequency_response, noise, thresholds
from meridian_lab.cli import run


def optimize(candidate, keys, iterations=3, seed=34047):
    verify_spec_lock()
    meta=read_yaml(ROOT/'candidates'/candidate/'topology.yaml')
    definitions=[meta['parameters'][k] for k in keys]
    bounds=[tuple(np.log(d['range'])) if d.get('scale')=='log' else tuple(d['range']) for d in definitions]
    id_=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_optimization_'+uuid.uuid4().hex[:8]
    directory=ROOT/'results/runs'/id_; directory.mkdir(exist_ok=False)
    manifest=source_manifest()
    for relative in manifest:
        target=directory/'source'/relative; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/relative).read_bytes())
    candidate_snapshot=directory/'candidate'; candidate_snapshot.mkdir()
    for name in ['circuit.cir','topology.yaml','hypothesis.md']:
        (candidate_snapshot/name).write_bytes((ROOT/'candidates'/candidate/name).read_bytes())
    previous=ROOT/'candidates'/candidate/'results.json'
    parent=json.loads(previous.read_text()).get('latest_experiment') if previous.exists() else None
    from itertools import count
    cache={}; trials=[]; attempt=count()
    def measure(x):
        key=tuple(float(v) for v in x)
        if key in cache:
            return cache[key]
        params={k:float(np.clip(np.exp(v) if d.get('scale')=='log' else v,*d['range'])) for k,d,v in zip(keys,definitions,x)}
        sim=Simulator(candidate,directory/f'trial_{next(attempt):05d}',params)
        sim.model_root=directory/'source/models'; sim.candidate=candidate_snapshot
        ctx={'nominal':sim.op_ac(),'checks':{}}
        op=operating_point(sim,ctx); fr=frequency_response(sim,ctx); ns=noise(sim,ctx)
        output={'parameters':params,'noise_pa_rms':ns['metrics']['electronics_noise_pa_rms'],
                'current_a':op['metrics']['current_a'],'response_deviation_db':fr['metrics']['response_deviation_db'],
                'spec_sha256':spec_digest(),'checks':{n:r['status'] for n,r in [('operating_point',op),('frequency_response',fr),('noise',ns)]},'jobs':sim.jobs}
        trials.append(output); write_json(directory/'trials.json',trials); cache[key]=output
        return output
    errors=[]
    def safe(x):
        try:
            return measure(x)
        except Exception as exc:
            item={'x':list(map(float,x)),'status':'error','reason':str(exc)}
            errors.append(item); write_json(directory/'errors.json',errors)
            return {'noise_pa_rms':1e30,'current_a':1e30,'response_deviation_db':1e30}
    constraints=NonlinearConstraint(lambda x: [safe(x)['current_a'],safe(x)['response_deviation_db']],
                                    [0,0],[thresholds()['current_max_a']['value'],thresholds()['electronics_response_db']['value']])
    from itertools import product
    # An explicit corner preflight finds thin feasible regions without extending any range.
    corners=[(np.array(x),safe(np.array(x))) for x in product(*[(lo,hi) for lo,hi in bounds])]
    feasible=[(x,m) for x,m in corners if m['current_a']<=thresholds()['current_max_a']['value'] and m['response_deviation_db']<=thresholds()['electronics_response_db']['value']]
    # SciPy normalizes x0 internally; exact log endpoints can exceed [0,1] by an ULP.
    # Inset only the initial seed numerically; search bounds and preflight corners remain unchanged.
    options={}
    if feasible:
        x0=min(feasible,key=lambda xm:xm[1]['noise_pa_rms'])[0]
        blo=np.array([b[0] for b in bounds]); bhi=np.array([b[1] for b in bounds])
        options['x0']=np.clip(x0,blo+1e-10*(bhi-blo),bhi-1e-10*(bhi-blo))
    try:
        answer=differential_evolution(lambda x:safe(x)['noise_pa_rms'],bounds,constraints=(constraints,),maxiter=iterations,popsize=5,rng=np.random.default_rng(seed),polish=False,**options)
    except Exception as exc:
        write_json(directory/'optimization.json',{'schema_version':1,'experiment_id':id_,'candidate_id':candidate,'parent_experiments':[parent] if parent else [],
                   'hypothesis':'Constrained numerical value optimization','structural_changes':None,'status':'error','failure_reason':str(exc),
                   'algorithm':'scipy differential_evolution with NonlinearConstraint','seed':seed,'bounds':{k:d['range'] for k,d in zip(keys,definitions)},
                   'trials':len(trials),'errors':errors,'source_manifest':manifest,'spec_sha256':spec_digest(),'versions':environment_versions(),
                   'comparison_with_parent':None,'useful_discovery':None,'next_potential_experiment':'Repair numerical orchestration and rerun within unchanged bounds.'})
        with (ROOT/'research/experiment_log.md').open('a') as log:
            log.write(f'\n## {id_} — optimizer error\n\n{exc}. All trial decks/data retained. [Record](../results/runs/{id_}/optimization.json).\n')
        raise
    best=safe(answer.x)
    base={'schema_version':1,'experiment_id':id_,'candidate_id':candidate,'parent_candidates':meta.get('parents',[]),
          'parent_experiments':[parent] if parent else [],'hypothesis':'Numerical value optimization within declared bounds; full suite still decides acceptance.',
          'structural_changes':None,'algorithm':'scipy differential_evolution with NonlinearConstraint',
          'objective':'electronics_noise_pa_rms','constraints':'current and response thresholds from frozen spec',
          'seed':seed,'continuous_parameters':keys,'bounds':{k:d['range'] for k,d in zip(keys,definitions)},
          'trials':len(trials),'errors':errors,'source_manifest':manifest,'spec_sha256':spec_digest(),'versions':environment_versions(),
          'next_potential_experiment':'Inspect the limiting constraint and investigate a structural change or additional declared parameters; keep thresholds fixed.'}
    if 'parameters' not in best or best['current_a']>thresholds()['current_max_a']['value'] or best['response_deviation_db']>thresholds()['electronics_response_db']['value']:
        write_json(directory/'optimization.json',{**base,'status':'no_feasible_proposal','failure_reason':'No point met frozen current and frequency-response constraints.','comparison_with_parent':None,'useful_discovery':'The selected parameter subset could not repair the fixture within its declared bounds.'})
        with (ROOT/'research/experiment_log.md').open('a') as log:
            log.write(f'\n## {id_} — failed optimization of {candidate}\n\n{len(trials)} saved trials; no feasible proposal. [Record](../results/runs/{id_}/optimization.json). Constraints and ranges retained.\n')
        raise RuntimeError('Numerical search found no feasible proposal; no candidate/spec changes made')
    summary={**base,'status':'proposal_requires_full_suite','algorithm':'scipy differential_evolution with NonlinearConstraint',
             'objective':'electronics_noise_pa_rms','constraints':'current and response thresholds from frozen spec',
             'seed':seed,'continuous_parameters':keys,'bounds':{k:d['range'] for k,d in zip(keys,definitions)},
             'trials':len(trials),'scipy_success':bool(answer.success),'message':str(answer.message),
             'best':best,'errors':errors,'source_manifest':manifest,'spec_sha256':spec_digest()}
    write_json(directory/'optimization.json',summary)
    write_json(directory/'proposed_parameters.json',best['parameters'])
    if source_manifest()!=manifest:
        raise RuntimeError('Research code changed during optimization; proposal remains unqualified. Rerun with stable sources.')
    final=run(candidate,seed,samples=16,overrides=best['parameters'],parent_experiments=[parent] if parent else [],numerical_optimization={k:v for k,v in summary.items() if k not in {'best','source_manifest','errors'}},hypothesis='Numerically improve fixture values while frozen current and response constraints apply; full suite decides acceptance.')
    summary['full_suite_experiment']=final['experiment_id']; summary['full_suite_status']=final['status']; summary['eligible']=final['eligible']
    write_json(directory/'optimization.json',summary)
    with (ROOT/'research/experiment_log.md').open('a') as log:
        log.write(f'\n## {id_} — numerical optimization of {candidate}\n\nConstrained objective: electronics noise; parameters: {keys}. Seed: {seed}. Trials: {len(trials)}. [Record](../results/runs/{id_}/optimization.json). Final full-suite experiment: {final["experiment_id"]}; qualified: {final["eligible"]}. Values are a proposal; canonical netlist and specification were not edited.\n')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('candidate'); parser.add_argument('--parameters',nargs='+',required=True); parser.add_argument('--iterations',type=int,default=3); parser.add_argument('--seed',type=int,default=34047)
    args=parser.parse_args()
    print(json.dumps(optimize(args.candidate,args.parameters,args.iterations,args.seed),indent=2))
