"""Compare value-independent graph and functional niche descriptors."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from meridian_lab.core import ROOT, read_yaml
from meridian_lab.archive import novelty, graph_features

def features(candidate):
    folder=ROOT/'candidates'/candidate
    return {'niche':read_yaml(folder/'topology.yaml')['niche'],'graph':graph_features(folder/'circuit.cir')}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('a'); p.add_argument('b'); args=p.parse_args()
    print(json.dumps({'architectural_distance':novelty(features(args.a),features(args.b)), 'performance_credit':0}))
