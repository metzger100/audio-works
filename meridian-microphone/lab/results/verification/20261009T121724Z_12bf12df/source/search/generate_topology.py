"""Export an Inventor proposal to the Engineer queue; never invent performance."""
import argparse, json, sys
from pathlib import Path
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from meridian_lab.core import ROOT, read_yaml

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--concept'); args=p.parse_args()
    concepts=read_yaml(ROOT/'search/concepts.yaml')['concepts']
    if not args.concept:
        print(json.dumps([{'id':c['id'],'title':c['title'],'families':c['families'],'status':c['status']} for c in concepts],indent=2)); raise SystemExit()
    concept=next(c for c in concepts if c['id']==args.concept)
    folder=ROOT/'search/proposals'/args.concept; folder.mkdir(parents=True,exist_ok=False)
    (folder/'proposal.yaml').write_text(yaml.safe_dump(concept,sort_keys=False))
    (folder/'engineer_task.md').write_text('# Engineer handoff\n\nImplement this physical conversion principle in a DUT subcircuit. Preserve the principle through bias/power/output additions. Obtain device models and bounds. Numerical optimization proposes values and the full suite judges them. No ideal-device or matching assumptions may become manufacturing claims.\n\n'+concept['title']+'\n\nFastest falsification: '+concept['fastest_falsification']+'\n')
    print(folder)
