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
from meridian_lab.core import ROOT, Simulator, read_yaml, verify_spec_lock, write_json, source_manifest, spec_digest
from meridian_lab.qualification import operating_point, frequency_response, noise, thresholds
from meridian_lab.cli import run


def optimize(candidate, keys, iterations=3, seed=34047):
    verify_spec_lock()
    meta=read_yaml(ROOT/'candidates'/candidate/'topology.yaml')
    definitions=[meta['parameters'][k] for k in keys]
    bounds=[tuple(np.log(d['range'])) if d.get('scale')=='log' else tuple(d['range']) for d in definitions]
    id_=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_optimization_'+uuid.uuid4().hex[:8]
    directory=ROOT/'results/runs'/id_; directory.mkdir(exist_ok=False)
    cache={}; trials=[]
    def measure(x):
        key=tuple(float(v) for v in x)
        if key in cache:
            return cache[key]
        params={k:float(np.exp(v) if d.get('scale')=='log' else v) for k,d,v in zip(keys,definitions,x)}
        sim=Simulator(candidate,directory/f'trial_{len(trials):05d}',params)
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
    answer=differential_evolution(lambda x:safe(x)['noise_pa_rms'],bounds,constraints=(constraints,),maxiter=iterations,popsize=5,rng=np.random.default_rng(seed),polish=False)
    best=safe(answer.x)
    if 'parameters' not in best or best['current_a']>thresholds()['current_max_a']['value'] or best['response_deviation_db']>thresholds()['electronics_response_db']['value']:
        write_json(directory/'optimization.json',{'status':'no_feasible_proposal','trials':len(trials),'errors':errors,'seed':seed,'source_manifest':source_manifest()})
        raise RuntimeError('Numerical search found no feasible proposal; no candidate/spec changes made')
    summary={'status':'proposal_requires_full_suite','algorithm':'scipy differential_evolution with NonlinearConstraint',
             'objective':'electronics_noise_pa_rms','constraints':'current and response thresholds from frozen spec',
             'seed':seed,'continuous_parameters':keys,'bounds':{k:d['range'] for k,d in zip(keys,definitions)},
             'trials':len(trials),'scipy_success':bool(answer.success),'message':str(answer.message),
             'best':best,'errors':errors,'source_manifest':source_manifest(),'spec_sha256':spec_digest()}
    write_json(directory/'optimization.json',summary)
    write_json(directory/'proposed_parameters.json',best['parameters'])
    final=run(candidate,seed,samples=16,overrides=best['parameters'],numerical_optimization={k:v for k,v in summary.items() if k not in {'best','source_manifest','errors'}},hypothesis='Numerically improve fixture values while frozen current and response constraints apply; full suite decides acceptance.')
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
