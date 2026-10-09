"""Quality-diversity retention; eligibility and novelty remain independent."""
from collections import Counter
import hashlib
import math
from pathlib import Path
import re

from .core import ROOT, read_yaml, write_json


def graph_features(netlist):
    """Value-independent labelled bipartite graph with 3 WL refinement rounds.

    An approximate graph signature, not an isomorphism proof. Controlled-source
    expression dependencies and hierarchical functional intent come from niche metadata.
    """
    nodes={}; neighbors={}; histogram=Counter()
    for line in Path(netlist).read_text().splitlines():
        words=line.split()
        if not words or words[0][0] in '*.+':
            continue
        kind=words[0][0].upper()
        count={'R':2,'C':2,'L':2,'V':2,'I':2,'B':2,'E':2,'G':2,'J':3,'M':4,'Q':3,'D':2}.get(kind)
        if count is None or len(words)<=count:
            continue
        device='d:'+words[0].lower(); nodes[device]='device:'+kind; neighbors[device]=[]; histogram[kind]+=1
        for pin,net in enumerate(words[1:1+count]):
            node='n:'+net.lower(); nodes.setdefault(node,'net'); neighbors.setdefault(node,[])
            neighbors[device].append((node,str(pin))); neighbors[node].append((device,str(pin)))
    labels=dict(nodes)
    for _ in range(3):
        labels={n:hashlib.sha256((labels[n]+'|'+'|'.join(sorted(pin+':'+labels[v] for v,pin in neighbors[n]))).encode()).hexdigest() for n in nodes}
    signature=hashlib.sha256('|'.join(sorted(labels.values())).encode()).hexdigest()
    return {'graph_signature':signature,'device_histogram':dict(histogram),'graph_nodes':len(nodes)}


def novelty(a,b):
    keys=set(a['niche'])|set(b['niche'])
    block=sum(a['niche'].get(k)!=b['niche'].get(k) for k in keys)/max(1,len(keys))
    ga,gb=a['graph'],b['graph']
    kinds=set(ga['device_histogram'])|set(gb['device_histogram'])
    histogram=sum(abs(ga['device_histogram'].get(k,0)-gb['device_histogram'].get(k,0)) for k in kinds)/max(1,sum(ga['device_histogram'].values())+sum(gb['device_histogram'].values()))
    return .5*block+.25*histogram+.25*(ga['graph_signature']!=gb['graph_signature'])


def dominates(a,b,objectives):
    if a['spec_sha256']!=b['spec_sha256'] or a['suite_sha256']!=b['suite_sha256'] or a['backend']!=b['backend']:
        return False
    if not all(k in a['metrics'] and k in b['metrics'] and a['metrics'][k] is not None and b['metrics'][k] is not None for k in objectives):
        return False
    if not all(math.isfinite(a['metrics'][k]) and math.isfinite(b['metrics'][k]) for k in objectives):
        return False
    if a.get('analysis_domain','stationary_audio') != b.get('analysis_domain','stationary_audio'):
        return False
    if any(not e.get('objective_validity',{}).get(k,True) for e in [a,b] for k in objectives):
        return False
    signs={k:1 if direction=='minimize' else -1 for k,direction in objectives.items()}
    return all(signs[k]*a['metrics'][k]<=signs[k]*b['metrics'][k] for k in objectives) and any(signs[k]*a['metrics'][k]<signs[k]*b['metrics'][k] for k in objectives)


def update(record):
    import fcntl
    with (ROOT/'results/archive.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return _update(record)


def _update(record):
    import json
    import pandas as pd
    path=ROOT/'results/archive.json'
    archive=json.loads(path.read_text()) if path.exists() else {'schema_version':1,'experiments':[],'niches':{},'family_counts':{},'champions':{}}
    meta=record['topology']
    metrics={}
    for check in record['checks'].values():
        for k,v in check['metrics'].items():
            if isinstance(v,(float,int)) and not isinstance(v,bool):
                metrics[k]=v
    entry={'experiment_id':record['experiment_id'],'candidate_id':meta['id'],'kind':meta['kind'],
           'eligible':record['eligible'],'status':record['status'],'spec_sha256':record['spec_sha256'],
           'suite_sha256':record['suite_sha256'],'backend':record['backend'],'niche':meta['niche'],
           'graph':graph_features((ROOT/record['result_file']).with_name('circuit.cir')), 'metrics':metrics,
           'result_file':record['result_file'],'failure_reasons':record['failure_reasons']}
    entry.update(family=meta['family'], analysis_domain=meta.get('analysis_domain','stationary_audio'),
                 patent_state=meta.get('patent_state','unknown_unscreened'),
                 implementation_gates={k:meta.get(k,'hold') for k in ['prototype_gate','manufacture_gate','build_publication_gate']},
                 procurement_state=meta.get('procurement_state','unknown'),
                 objective_validity={k:False for k in ['electronics_noise_pa_rms','thd_percent','headroom_pa_rms','observed_pass_fraction','sensitivity_to_devices','pcb_sensitivity','cost_eur']})
    evidence=set(meta.get('qualification_evidence',[]))
    entry['objective_validity'].update(electronics_noise_pa_rms='validated_noise_models' in evidence,
                                       thd_percent='validated_nonlinear_models' in evidence,
                                       headroom_pa_rms='validated_nonlinear_models' in evidence)
    bom=(ROOT/record['result_file']).with_name('bom.yaml')
    if bom.exists():
        parts=read_yaml(bom)
        entry['procurement_cost']=parts.get('electronics_cost',{})
        entry['metrics']['component_count']=sum(p['quantity'] for p in parts.get('physical_parts',[]))
        delivered=entry['procurement_cost'].get('confirmed_delivered_eur')
        if delivered is not None:
            entry['metrics']['cost_eur']=delivered
            entry['objective_validity']['cost_eur']=True
    entry['novelty_nearest']=min((novelty(entry,e) for e in archive['experiments']),default=1.0)
    if any(e['experiment_id']==entry['experiment_id'] for e in archive['experiments']):
        raise ValueError('Duplicate immutable experiment ID')
    archive['experiments'].append(entry)
    niche=json.dumps(meta['niche'],sort_keys=True)
    archive['niches'].setdefault(niche,[]).append(entry['experiment_id'])
    archive['family_counts'][meta['family']]=archive['family_counts'].get(meta['family'],0)+1
    objectives=read_yaml(ROOT/'spec/scoring.yaml')['objectives']
    eligible=[e for e in archive['experiments'] if e['eligible']]
    # Complete demonstrated axes, rather than absent objectives surviving dominance.
    # Objective completeness is shown separately; no incomplete vector masquerades as a champion.
    complete=[e for e in eligible if all(k in e['metrics'] and e['metrics'][k] is not None and math.isfinite(e['metrics'][k]) and e.get('objective_validity',{}).get(k,True) for k in objectives)]
    front=[e for e in complete if not any(dominates(other,e,objectives) for other in complete if other!=e)]
    cohorts={}
    for e in archive['experiments']:
        cohort='|'.join([e['spec_sha256'],e['suite_sha256'],e['backend'],e.get('analysis_domain','stationary_audio')])
        cohorts.setdefault(cohort,[]).append(e)
    archive['champions_by_cohort']={cohort:{k:(min(valid,key=lambda e:e['metrics'][k]) if direction=='minimize' else max(valid,key=lambda e:e['metrics'][k]))['experiment_id'] for k,direction in objectives.items()}
                                   for cohort,entries in cohorts.items() if (valid:=[e for e in entries if e in complete])}
    archive['champions']=next(iter(archive['champions_by_cohort'].values())) if len(archive['champions_by_cohort'])==1 else {}
    representatives={}
    for cohort,entries in cohorts.items():
        for e in entries:
            key=cohort+'|'+json.dumps(e['niche'],sort_keys=True)
            slot=representatives.setdefault(key,{'scope':'model-conditional niche evidence only; no global winner','axes':{}})
            for metric in ['response_deviation_db','current_a']:
                value=e['metrics'].get(metric)
                if value is None or not math.isfinite(value) or e.get('analysis_domain','stationary_audio')!='stationary_audio': continue
                old=slot['axes'].get(metric)
                if old is None or value<old['value']:
                    slot['axes'][metric]={'experiment_id':e['experiment_id'],'value':value,'qualified':e['eligible']}
    archive['niche_representatives_by_cohort']=representatives
    write_json(path,archive)
    write_json(ROOT/'results/pareto_front.json',{'schema_version':2,'eligible_front':front,'unqualified_count':len(archive['experiments'])-len(eligible), 'incomplete_objective_count':len(eligible)-len(complete),'cohorts':list(cohorts), 'note':'Complete qualified objectives and physical evidence required; scenario screens, unknown delivered cost and model predictions cannot populate the production front.'})
    pd.DataFrame([{'experiment_id':e['experiment_id'],'candidate_id':e['candidate_id'],'status':e['status'],'eligible':e['eligible'],'novelty_nearest':e['novelty_nearest'],**e['metrics']} for e in archive['experiments']]).to_csv(ROOT/'results/leaderboard.csv',index=False)
    return entry
