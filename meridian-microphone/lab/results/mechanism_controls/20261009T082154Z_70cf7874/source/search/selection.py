"""Exploration allocation and persistent family coverage, independent of novelty credit."""
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from meridian_lab.core import ROOT, read_yaml

def next_allocation(counts):
    fractions=read_yaml(ROOT/'spec/scoring.yaml')['exploration_allocation']
    total=sum(counts.values())+1
    return max(fractions,key=lambda k:fractions[k]*total-counts.get(k,0))

def underexplored_family(implemented_counts):
    families=read_yaml(ROOT/'search/families.yaml')['families']
    return min(families,key=lambda f:implemented_counts.get(f['id'],0))['id']

if __name__=='__main__':
    print(json.dumps({'target_allocation':read_yaml(ROOT/'spec/scoring.yaml')['exploration_allocation'],
                      'next_underexplored_family':underexplored_family({}), 'note':'No family is removed by another family winning.'},indent=2))
