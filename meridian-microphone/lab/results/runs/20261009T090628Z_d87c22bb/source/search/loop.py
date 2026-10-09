"""Bounded autonomous evaluation of implemented Engineer candidates; no background service."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from meridian_lab.core import ROOT, read_yaml
from meridian_lab.cli import run
from selection import next_allocation

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--evaluations',type=int,default=1); p.add_argument('--samples',type=int,default=16); p.add_argument('--seed',type=int,default=34047); a=p.parse_args()
    if a.evaluations<1 or a.samples<1:
        p.error('Use positive explicit budgets')
    ready=[read_yaml(f) for f in (ROOT/'candidates').glob('*/topology.yaml')]
    ready=[m for m in ready if m.get('kind')=='research_candidate' and m.get('state')=='engineering_ready']
    if not ready:
        print(json.dumps({'status':'awaiting_engineer_netlists','concepts':len(read_yaml(ROOT/'search/concepts.yaml')['concepts']), 'evaluations_run':0})); raise SystemExit(2)
    counts={}; family_counts={}
    records=[]
    for i in range(a.evaluations):
        category=next_allocation(counts)
        # A family with fewer evaluated representatives survives regardless of global performance.
        chosen=min(ready,key=lambda m:family_counts.get(m['family'],0))
        record=run(chosen['id'],a.seed+i,a.samples,hypothesis=chosen['hypothesis']+f' [allocation: {category}]')
        records.append({'candidate':chosen['id'],'experiment':record['experiment_id'],'status':record['status']})
        counts[category]=counts.get(category,0)+1
        family_counts[chosen['family']]=family_counts.get(chosen['family'],0)+1
    print(json.dumps(records,indent=2))
